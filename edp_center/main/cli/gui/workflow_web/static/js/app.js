let graphData = null;
let svg = null;
let nodes = null;
let links = null;
let statusUpdateInterval = null;
let g = null;
let render = null;

// 日志功能
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// 更新统计信息
function updateStats() {
    if (!graphData || !graphData.nodes) return;
    
    const statusData = {};
    // 从服务器获取最新状态
    fetch('/api/workflow/status')
        .then(r => r.json())
        .then(result => {
            if (result.success) {
                Object.assign(statusData, result.data);
            }
            
            let total = graphData.nodes.length;
            let success = 0;
            let running = 0;
            let failed = 0;
            
            graphData.nodes.forEach(n => {
                const status = statusData[n.id]?.status || n.status || 'pending';
                if (status === 'success') success++;
                else if (status === 'running') running++;
                else if (status === 'failed') failed++;
            });
            
            document.getElementById('stat-total').textContent = total;
            document.getElementById('stat-success').textContent = success;
            document.getElementById('stat-running').textContent = running;
            document.getElementById('stat-failed').textContent = failed;
        });
}

// 加载工作流
async function loadWorkflow() {
    try {
        addLog('正在加载工作流...', 'info');
        const response = await fetch('/api/workflow/load');
        const result = await response.json();
        if (result.success) {
            graphData = result.data;
            drawGraph();
            updateStats();
            addLog('工作流加载成功', 'success');
        } else {
            addLog('加载失败: ' + result.error, 'error');
            alert('加载失败: ' + result.error);
        }
    } catch (error) {
        addLog('加载失败: ' + error, 'error');
        alert('加载失败: ' + error);
    }
}

// 绘制图形（使用 dagre-d3）
function drawGraph() {
    if (!graphData || !graphData.nodes) return;
    
    const container = d3.select('#graph-container');
    container.selectAll('*').remove();
    
    const width = container.node().clientWidth;
    const height = container.node().clientHeight || 800;
    
    svg = container.append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // 在 SVG 级别全局拦截所有点击和鼠标事件，防止文件打开对话框
    svg.on('mousedown', (event) => {
        // 检查是否点击的是节点
        const target = event.target;
        const nodeElement = target.closest('g.node');
        if (!nodeElement) {
            // 不是节点，阻止默认行为
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    });
    
    svg.on('click', (event) => {
        // 全局拦截，只允许我们的节点点击处理器执行
        const target = event.target;
        const nodeElement = target.closest('g.node');
        if (!nodeElement) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    });
    
    // 使用 capture 阶段拦截所有点击
    container.node().addEventListener('click', (event) => {
        const target = event.target;
        // 如果点击的不是节点，或者节点没有我们的处理器，阻止默认行为
        const nodeElement = target.closest('g.node');
        if (nodeElement) {
            // 检查是否有我们的自定义属性
            const hasCustomHandler = nodeElement.getAttribute('data-has-handler') === 'true';
            if (!hasCustomHandler) {
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();
                return false;
            }
        }
    }, true);  // 使用 capture 阶段
    
    g = svg.append('g');
    
    // 创建 dagre 图
    const graph = new dagre.graphlib.Graph()
        .setGraph({
            rankdir: 'TB',  // 从上到下布局（Top to Bottom）
            nodesep: 50,    // 节点水平间距
            ranksep: 100,   // 层级垂直间距
            marginx: 50,
            marginy: 50
        })
        .setDefaultEdgeLabel(() => ({}));
    
    // 识别独立节点（没有入边也没有出边的节点）
    const nodeIds = new Set(graphData.nodes.map(n => n.id));
    const hasIncoming = new Set();
    const hasOutgoing = new Set();
    const incomingEdges = new Map(); // nodeId -> [sourceNodeIds]
    
    (graphData.edges || []).forEach(edge => {
        hasIncoming.add(edge.to);
        hasOutgoing.add(edge.from);
        if (!incomingEdges.has(edge.to)) {
            incomingEdges.set(edge.to, []);
        }
        incomingEdges.get(edge.to).push(edge.from);
    });
    
    // 找出完全独立的节点（既没有入边也没有出边）
    const isolatedNodes = graphData.nodes.filter(node => 
        !hasIncoming.has(node.id) && !hasOutgoing.has(node.id)
    );
    
    // 判断节点是否准备好
    // 1. 首先检查步骤本身是否可用（flow 是否准备好，源脚本是否存在）
    // 2. 然后检查所有前置步骤是否都已完成
    function isNodeReady(nodeId) {
        const node = graphData.nodes.find(n => n.id === nodeId);
        if (!node) {
            return false;
        }
        
        // 第一步：检查步骤本身是否 ready（flow 是否准备好）
        const flowReady = node.flow_ready === true;
        if (!flowReady) {
            return false;  // flow 未准备好，步骤不可执行
        }
        
        // 第二步：检查所有前置步骤是否都已完成
        // 如果没有前置步骤，则准备好
        if (!hasIncoming.has(nodeId)) {
            return true;
        }
        
        // 检查所有前置步骤是否都已完成
        const prerequisites = incomingEdges.get(nodeId) || [];
        if (prerequisites.length === 0) {
            return true;
        }
        
        // 检查所有前置步骤的状态
        return prerequisites.every(prereqId => {
            const prereqNode = graphData.nodes.find(n => n.id === prereqId);
            const status = prereqNode?.status || 'pending';
            return status === 'success' || status === 'skipped';
        });
    }
    
    // 添加节点（保留原始状态）
    graphData.nodes.forEach(node => {
        const isIsolated = isolatedNodes.some(n => n.id === node.id);
        const isReady = isNodeReady(node.id);
        
        // 确保 label 不包含任何路径信息，只保留步骤名称
        let cleanLabel = node.label || node.id;
        // 移除任何可能的路径字符
        cleanLabel = cleanLabel.replace(/[\\\/]/g, '');
        // 只保留步骤名称部分（flow.step 格式）
        if (cleanLabel.includes('.')) {
            const parts = cleanLabel.split('.');
            cleanLabel = parts.slice(-2).join('.');  // 只保留最后两部分
        }
        
        graph.setNode(node.id, {
            label: cleanLabel,  // 使用清理后的标签
            width: 200,
            height: 45,
            status: node.status || 'pending',
            originalNode: node,  // 保存原始节点引用
            isIsolated: isIsolated,
            isReady: isReady
        });
    });
    
    // 添加边
    (graphData.edges || []).forEach(edge => {
        graph.setEdge(edge.from, edge.to);
    });
    
    // 如果有独立节点，创建一个虚拟的根节点来统一管理它们，使它们整齐排列
    if (isolatedNodes.length > 0) {
        const virtualRootId = '__virtual_root__';
        graph.setNode(virtualRootId, {
            label: '',
            width: 0,
            height: 0,
            style: 'visibility: hidden;'
        });
        
        // 将独立节点连接到虚拟根节点（使用隐藏的边）
        isolatedNodes.forEach(node => {
            graph.setEdge(virtualRootId, node.id, {
                style: 'stroke: none; fill: none; opacity: 0;'
            });
        });
    }
    
    // 计算布局
    dagre.layout(graph);
    
    // 创建渲染器
    render = new dagreD3.render();
    
    // 渲染图形
    render(g, graph);
    
    // 立即移除所有可能的链接属性（防止浏览器打开文件对话框）
    // 遍历所有元素，包括 SVG 元素
    const allElements = g.selectAll('*');
    allElements.each(function() {
        const elem = d3.select(this);
        // 移除所有可能的链接属性
        elem.attr('href', null)
            .attr('xlink:href', null)
            .attr('href', null)
            .attr('onclick', null);
        
        // 如果是 <a> 标签，移除它并保留内容
        if (this.tagName === 'a' || this.tagName === 'A') {
            const parent = this.parentNode;
            if (parent) {
                // 将 <a> 标签的内容移到父元素
                while (this.firstChild) {
                    parent.insertBefore(this.firstChild, this);
                }
                parent.removeChild(this);
            }
        }
    });
    
    // 也检查 SVG 根元素
    svg.selectAll('a').each(function() {
        const parent = this.parentNode;
        if (parent) {
            while (this.firstChild) {
                parent.insertBefore(this.firstChild, this);
            }
            parent.removeChild(this);
        }
    });
    
    // 使用 MutationObserver 监控 DOM 变化，自动移除任何新添加的链接属性
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) {  // Element node
                    // 移除链接属性
                    if (node.hasAttribute) {
                        node.removeAttribute('href');
                        node.removeAttribute('xlink:href');
                    }
                    // 如果是 <a> 标签，移除它
                    if (node.tagName === 'a' || node.tagName === 'A') {
                        const parent = node.parentNode;
                        if (parent) {
                            while (node.firstChild) {
                                parent.insertBefore(node.firstChild, node);
                            }
                            parent.removeChild(node);
                        }
                    }
                    // 递归检查子元素
                    const allChildren = node.querySelectorAll ? node.querySelectorAll('*') : [];
                    allChildren.forEach((child) => {
                        child.removeAttribute('href');
                        child.removeAttribute('xlink:href');
                    });
                }
            });
        });
    });
    
    // 开始观察 SVG 容器
    observer.observe(container.node(), {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['href', 'xlink:href']
    });
    
    // 获取图形边界
    const graphBounds = g.node().getBBox();
    
    // 计算缩放和平移，使图形居中
    const scale = Math.min(
        (width - 100) / graphBounds.width,
        (height - 100) / graphBounds.height,
        1.0
    );
    const translateX = (width - graphBounds.width * scale) / 2 - graphBounds.x * scale;
    const translateY = (height - graphBounds.height * scale) / 2 - graphBounds.y * scale;
    
    // 应用初始变换
    g.attr('transform', `translate(${translateX}, ${translateY}) scale(${scale})`);
    
    // 添加缩放和平移功能
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // 隐藏虚拟根节点和连接到它的边
    g.selectAll('g.node')
        .filter(d => d === '__virtual_root__')
        .style('display', 'none');
    
    g.selectAll('g.edgePath')
        .filter(function() {
            const path = d3.select(this).select('path');
            const marker = path.attr('marker-end');
            // 隐藏连接到虚拟根节点的边
            return path.attr('stroke') === 'none' || !marker;
        })
        .style('display', 'none');
    
    // 更新节点样式和交互
    nodes = g.selectAll('g.node')
        .filter(d => d !== '__virtual_root__');
    
    // 更新节点样式
    nodes.each(function(d) {
        const node = d3.select(this);
        const nodeData = graph.node(d);
        const status = nodeData.status || 
                      (nodeData.originalNode ? nodeData.originalNode.status : null) || 
                      'pending';
        const isReady = nodeData.isReady !== false; // 默认准备好
        
        // 确保节点元素及其所有子元素都没有链接属性（防止浏览器打开文件对话框）
        node.attr('href', null)
            .attr('xlink:href', null);
        
        // 移除节点内部所有子元素的链接属性
        node.selectAll('*').each(function() {
            const elem = d3.select(this);
            elem.attr('href', null)
                .attr('xlink:href', null);
        });
        
        // 更新矩形样式
        const rect = node.select('rect');
        if (rect.node()) {
            let className = `node-${status}`;
            if (status === 'pending') {
                if (isReady) {
                    className += ' node-ready';  // 准备好可以执行
                } else {
                    className += ' node-not-ready';  // 需要等待前置步骤
                }
            }
            rect.attr('class', className)
                .attr('rx', 8);
        }
        
        // 更新文本样式
        const text = node.select('text');
        if (text.node()) {
            if (!isReady && status === 'pending') {
                text.attr('opacity', 0.5);
            } else if (isReady && status === 'pending') {
                text.attr('opacity', 1)
                    .attr('font-weight', '600');  // 可执行节点文字加粗
            } else {
                text.attr('opacity', 1)
                    .attr('font-weight', '500');
            }
        }
        
        // 标记节点有自定义处理器
        node.attr('data-has-handler', 'true');
        
        // 添加点击和右键菜单事件（只有准备好的节点才能点击）
        if (isReady || status !== 'pending') {
            // 移除所有现有的事件监听器，然后重新添加
            node.on('click', null);  // 先清除
            node.on('mousedown', (event, d) => {
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();
                return false;
            });
            node.on('click', (event, d) => {
                event.preventDefault();  // 阻止默认行为（防止浏览器打开文件对话框）
                event.stopPropagation();
                event.stopImmediatePropagation();  // 阻止其他事件处理器
                // 直接执行，使用正常模式（debug_mode = 0）
                executeStep(d, 0);
                return false;  // 额外确保阻止默认行为
            })
            .style('cursor', 'pointer')
            .style('pointer-events', 'all');  // 确保可以接收点击事件
        } else {
            node.on('click', (event, d) => {
                event.preventDefault();  // 阻止默认行为
                event.stopPropagation();
                // 显示提示信息
                const prerequisites = incomingEdges.get(d) || [];
                const incompletePrereqs = prerequisites.filter(prereqId => {
                    const prereqNode = graphData.nodes.find(n => n.id === prereqId);
                    const prereqStatus = prereqNode?.status || 'pending';
                    return prereqStatus !== 'success' && prereqStatus !== 'skipped';
                });
                if (incompletePrereqs.length > 0) {
                    const prereqNames = incompletePrereqs.map(id => {
                        const n = graphData.nodes.find(n => n.id === id);
                        return n?.label || id;
                    }).join(', ');
                    addLog(`无法执行 ${nodeData.label || d}：前置步骤未完成 (${prereqNames})`, 'warning');
                }
            })
            .style('cursor', 'not-allowed');
        }
        
        node.on('contextmenu', (event, d) => {
            event.preventDefault();
            event.stopPropagation();
            showContextMenu(event, d);
        });
    });
    
    // 更新边的样式
    g.selectAll('g.edgePath path')
        .attr('stroke', '#6c757d')
        .attr('stroke-width', 2)
        .attr('fill', 'none')
        .attr('opacity', 0.6);
    
    // 更新箭头样式
    g.selectAll('marker')
        .attr('fill', '#6c757d');
}

// 显示执行模式选择对话框
function showExecuteDialog(stepName, callback) {
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        padding: 24px;
        z-index: 2000;
        min-width: 400px;
    `;
    
    dialog.innerHTML = `
        <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #212529;">执行步骤: ${stepName}</h3>
        <div style="margin-bottom: 20px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px; border-radius: 4px; transition: background 0.2s;">
                <input type="radio" name="exec_mode" value="0" checked style="cursor: pointer;">
                <span>正常模式</span>
            </label>
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 8px; border-radius: 4px; transition: background 0.2s;">
                <input type="radio" name="exec_mode" value="1" style="cursor: pointer;">
                <span>Debug 模式（交互式调试）</span>
            </label>
        </div>
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button id="cancel-btn" style="padding: 8px 16px; border: 1px solid #dee2e6; border-radius: 6px; background: white; cursor: pointer;">取消</button>
            <button id="confirm-btn" style="padding: 8px 16px; border: none; border-radius: 6px; background: #667eea; color: white; cursor: pointer; font-weight: 500;">执行</button>
        </div>
    `;
    
    // 添加背景遮罩
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 1999;
    `;
    
    document.body.appendChild(overlay);
    document.body.appendChild(dialog);
    
    // 关闭对话框
    const closeDialog = () => {
        document.body.removeChild(overlay);
        document.body.removeChild(dialog);
    };
    
    // 确认按钮
    document.getElementById('confirm-btn').onclick = () => {
        const selectedMode = document.querySelector('input[name="exec_mode"]:checked').value;
        closeDialog();
        callback(parseInt(selectedMode));
    };
    
    // 取消按钮
    document.getElementById('cancel-btn').onclick = closeDialog;
    overlay.onclick = closeDialog;
}

// 执行步骤
async function executeStep(stepName, debugMode = 0) {
    try {
        const modeText = debugMode === 1 ? ' (Debug 模式)' : '';
        addLog(`开始执行: ${stepName}${modeText}`, 'info');
        updateStatusBadge('运行中');
        
        const response = await fetch('/api/workflow/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                step_name: stepName,
                debug_mode: debugMode
            })
        });
        const result = await response.json();
        if (result.success) {
            // 立即更新状态
            await updateStatus();
            // 开始轮询（如果有步骤在运行）
            startStatusPolling();
        } else {
            addLog(`执行失败: ${result.error}`, 'error');
            alert('执行失败: ' + result.error);
        }
    } catch (error) {
        addLog(`执行失败: ${error}`, 'error');
        alert('执行失败: ' + error);
    }
}

// 执行步骤（带对话框选择模式）
function executeStepWithDialog(stepName) {
    showExecuteDialog(stepName, (debugMode) => {
        executeStep(stepName, debugMode);
    });
}

// 跳过步骤
async function skipStep(stepName) {
    try {
        addLog(`跳过步骤: ${stepName}`, 'warning');
        const response = await fetch('/api/workflow/skip', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({step_name: stepName})
        });
        const result = await response.json();
        if (result.success) {
            await updateStatus();
            updateStats();
        }
    } catch (error) {
        addLog(`操作失败: ${error}`, 'error');
    }
}

// 中断步骤
async function stopStep(stepName) {
    try {
        addLog(`中断步骤: ${stepName}`, 'warning');
        const response = await fetch('/api/workflow/stop', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({step_name: stepName})
        });
        const result = await response.json();
        if (result.success) {
            await updateStatus();
            updateStats();
        }
    } catch (error) {
        addLog(`操作失败: ${error}`, 'error');
    }
}

// 更新状态徽章
function updateStatusBadge(status) {
    const badge = document.getElementById('status-badge');
    badge.textContent = status;
    badge.className = 'status-badge';
    if (status === '运行中') {
        badge.classList.add('running');
    }
}

// 显示右键菜单
function showContextMenu(event, d) {
    // 移除现有菜单
    const existingMenu = document.querySelector('.context-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.style.left = event.pageX + 'px';
    menu.style.top = event.pageY + 'px';
    
    const nodeStatus = graphData.nodes.find(n => n.id === d)?.status || 'pending';
    const nodeData = graphData.nodes.find(n => n.id === d);
    
    // 判断节点是否准备好
    const hasIncoming = new Set();
    const incomingEdges = new Map();
    (graphData.edges || []).forEach(edge => {
        hasIncoming.add(edge.to);
        if (!incomingEdges.has(edge.to)) {
            incomingEdges.set(edge.to, []);
        }
        incomingEdges.get(edge.to).push(edge.from);
    });
    
    function isNodeReady(nodeId) {
        const node = graphData.nodes.find(n => n.id === nodeId);
        if (!node) {
            return false;
        }
        
        // 第一步：检查步骤本身是否 ready（flow 是否准备好）
        const flowReady = node.flow_ready === true;
        if (!flowReady) {
            return false;  // flow 未准备好，步骤不可执行
        }
        
        // 第二步：检查所有前置步骤是否都已完成
        if (!hasIncoming.has(nodeId)) {
            return true;
        }
        const prerequisites = incomingEdges.get(nodeId) || [];
        if (prerequisites.length === 0) {
            return true;
        }
        return prerequisites.every(prereqId => {
            const prereqNode = graphData.nodes.find(n => n.id === prereqId);
            const status = prereqNode?.status || 'pending';
            return status === 'success' || status === 'skipped';
        });
    }
    
    const isReady = isNodeReady(d);
    
    const actions = [];
    
    // 只有准备好的节点或非 pending 状态的节点才能执行
    if (isReady || nodeStatus !== 'pending') {
        actions.push({label: '▶️ 执行（正常模式）', action: () => executeStep(d, 0), icon: '▶️'});
        actions.push({label: '🐛 执行（Debug 模式）', action: () => executeStep(d, 1), icon: '🐛'});
    }
    
    actions.push({label: '⏭️ 跳过', action: () => skipStep(d), icon: '⏭️'});
    
    if (nodeStatus === 'running') {
        actions.push({label: '⏹️ 中断', action: () => stopStep(d), icon: '⏹️', danger: true});
    }
    
    if (nodeStatus === 'success' || nodeStatus === 'failed') {
        actions.push({label: '🔄 重新运行（正常模式）', action: () => executeStep(d, 0), icon: '🔄'});
        actions.push({label: '🔄 重新运行（Debug 模式）', action: () => executeStep(d, 1), icon: '🔄'});
    }
    
    actions.forEach((action, idx) => {
        if (idx > 0 && (action.danger || actions[idx-1].danger)) {
            const divider = document.createElement('div');
            divider.className = 'context-menu-divider';
            menu.appendChild(divider);
        }
        
        const item = document.createElement('div');
        item.className = 'context-menu-item' + (action.danger ? ' danger' : '');
        item.textContent = action.label;
        item.onclick = () => {
            action.action();
            menu.remove();
        };
        menu.appendChild(item);
    });
    
    document.body.appendChild(menu);
    
    // 点击其他地方关闭菜单
    setTimeout(() => {
        const removeMenu = (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', removeMenu);
            }
        };
        document.addEventListener('click', removeMenu);
    }, 0);
}

// 更新状态
async function updateStatus() {
    try {
        const response = await fetch('/api/workflow/status');
        const result = await response.json();
        if (result.success) {
            let hasRunning = false;
            
            // 更新 graphData 中的节点状态
            if (graphData && graphData.nodes) {
                graphData.nodes.forEach(node => {
                    if (result.data[node.id]) {
                        node.status = result.data[node.id].status;
                    }
                });
            }
            
            // 重新选择节点并更新样式（dagre-d3 渲染后需要重新选择）
            if (g) {
                // 重新计算依赖关系
                const hasIncoming = new Set();
                const incomingEdges = new Map();
                (graphData.edges || []).forEach(edge => {
                    hasIncoming.add(edge.to);
                    if (!incomingEdges.has(edge.to)) {
                        incomingEdges.set(edge.to, []);
                    }
                    incomingEdges.get(edge.to).push(edge.from);
                });
                
                // 判断节点是否准备好
                // 1. 首先检查步骤本身是否可用（flow 是否准备好，源脚本是否存在）
                // 2. 然后检查所有前置步骤是否都已完成
                function isNodeReady(nodeId) {
                    const node = graphData.nodes.find(n => n.id === nodeId);
                    if (!node) {
                        return false;
                    }
                    
                    // 第一步：检查步骤本身是否 ready（flow 是否准备好）
                    const flowReady = node.flow_ready !== false; // 默认为 true（向后兼容）
                    if (!flowReady) {
                        return false;  // flow 未准备好，步骤不可执行
                    }
                    
                    // 第二步：检查所有前置步骤是否都已完成
                    if (!hasIncoming.has(nodeId)) {
                        return true;
                    }
                    const prerequisites = incomingEdges.get(nodeId) || [];
                    if (prerequisites.length === 0) {
                        return true;
                    }
                    return prerequisites.every(prereqId => {
                        const prereqNode = graphData.nodes.find(n => n.id === prereqId);
                        const status = prereqNode?.status || 'pending';
                        return status === 'success' || status === 'skipped';
                    });
                }
                
                const allNodes = g.selectAll('g.node')
                    .filter(d => d !== '__virtual_root__');
                
                allNodes.each(function(d) {
                    const node = d3.select(this);
                    const nodeId = d;
                    const status = result.data[nodeId]?.status || 
                                  graphData.nodes.find(n => n.id === nodeId)?.status || 
                                  'pending';
                    const isReady = isNodeReady(nodeId);
                    
                    if (status === 'running') {
                        hasRunning = true;
                    }
                    
                    // 更新矩形样式
                    const rect = node.select('rect');
                    if (rect.node()) {
                        let className = `node-${status}`;
                        if (status === 'pending') {
                            if (isReady) {
                                className += ' node-ready';  // 准备好可以执行
                            } else {
                                className += ' node-not-ready';  // 需要等待前置步骤
                            }
                        }
                        rect.node().className.baseVal = className;
                        rect.attr('class', className);
                    }
                    
                    // 更新文本样式
                    const text = node.select('text');
                    if (text.node()) {
                        if (!isReady && status === 'pending') {
                            text.attr('opacity', 0.5)
                                .attr('font-weight', '500');
                        } else if (isReady && status === 'pending') {
                            text.attr('opacity', 1)
                                .attr('font-weight', '600');  // 可执行节点文字加粗
                        } else {
                            text.attr('opacity', 1)
                                .attr('font-weight', '500');
                        }
                    }
                    
                    // 更新光标样式
                    if (isReady || status !== 'pending') {
                        node.style('cursor', 'pointer');
                    } else {
                        node.style('cursor', 'not-allowed');
                    }
                });
            }
            
            // 更新统计信息
            updateStats();
            
            // 检查是否有状态变化的步骤，并显示日志（避免重复显示）
            if (graphData && graphData.nodes) {
                graphData.nodes.forEach(node => {
                    const statusInfo = result.data[node.id];
                    const oldStatus = node.status || 'pending';
                    const newStatus = statusInfo?.status || oldStatus;
                    
                    // 只在状态变化时显示日志（避免重复）
                    if (statusInfo && oldStatus !== newStatus) {
                        if (newStatus === 'failed') {
                            const message = statusInfo.message || statusInfo.error || '执行失败';
                            addLog(`${node.label || node.id}: ${message}`, 'error');
                            
                            // 如果有日志内容，显示关键错误信息
                            if (statusInfo.log_content) {
                                const logLines = statusInfo.log_content.split('\n');
                                // 查找错误相关的行
                                const errorLines = logLines.filter(line => 
                                    line.includes('ERROR') || 
                                    line.includes('错误') || 
                                    line.includes('失败') ||
                                    line.includes('Failed') ||
                                    line.includes('Exception')
                                );
                                // 显示最后几条错误信息
                                errorLines.slice(-3).forEach(line => {
                                    if (line.trim()) {
                                        addLog(`  ${line.trim()}`, 'error');
                                    }
                                });
                            }
                        } else if (newStatus === 'success') {
                            const message = statusInfo.message || '执行成功';
                            addLog(`${node.label || node.id}: ${message}`, 'success');
                        }
                    }
                });
            }
            
            // 如果没有正在运行的步骤，停止轮询
            if (!hasRunning && statusUpdateInterval) {
                clearInterval(statusUpdateInterval);
                statusUpdateInterval = null;
                updateStatusBadge('就绪');
            } else if (hasRunning) {
                updateStatusBadge('运行中');
            }
            
            return hasRunning;
        }
    } catch (error) {
        console.error('更新状态失败:', error);
    }
    return false;
}

// 清除状态
function clearStatus() {
    addLog('清除所有状态', 'info');
    // 停止轮询
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
        statusUpdateInterval = null;
    }
    // 重新加载工作流
    loadWorkflow();
    updateStatusBadge('就绪');
}

// 开始状态轮询（只在有步骤运行时）
function startStatusPolling() {
    if (!statusUpdateInterval) {
        statusUpdateInterval = setInterval(async () => {
            const hasRunning = await updateStatus();
            if (!hasRunning && statusUpdateInterval) {
                clearInterval(statusUpdateInterval);
                statusUpdateInterval = null;
                updateStatusBadge('就绪');
            }
        }, 1000);
    }
}

// 页面加载时自动加载工作流
window.addEventListener('load', () => {
    loadWorkflow();
    setTimeout(updateStatus, 500);
});

// 窗口大小改变时重新调整图形
window.addEventListener('resize', () => {
    if (graphData) {
        drawGraph();
    }
});
