#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
依赖关系可视化工具

支持多种输出格式：
1. CLI 文本输出（ASCII 树形图）
2. Graphviz 图片输出（PNG/SVG）
3. Mermaid 图表输出（Markdown 兼容）
4. Web 交互式可视化（HTML + D3.js）
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque


class GraphVisualizer:
    """依赖关系可视化器"""
    
    def __init__(self, graph):
        """
        初始化可视化器
        
        Args:
            graph: Graph 对象（来自 edp_flowkit）
        """
        self.graph = graph
        self.steps = graph.steps
        self.dependencies = graph.dependencies
    
    def extract_graph_data(self, 
                          focus_step: Optional[str] = None,
                          depth: Optional[int] = None,
                          include_sub_steps: bool = False) -> Dict:
        """
        提取图数据用于可视化
        
        Args:
            focus_step: 聚焦的步骤名称，如果提供则只显示相关子图
            depth: 深度限制，只显示指定深度的依赖关系
            include_sub_steps: 是否包含 sub_steps 信息
            
        Returns:
            包含节点和边的字典
        """
        nodes = []
        edges = []
        node_set = set()
        
        # 确定要显示的步骤
        if focus_step:
            # 只显示与 focus_step 相关的步骤
            related_steps = self._get_related_steps(focus_step, depth)
            steps_to_show = related_steps
        else:
            # 显示所有步骤
            steps_to_show = set(self.steps.keys())
        
        # 构建节点
        for step_name in steps_to_show:
            if step_name not in self.steps:
                continue
                
            step = self.steps[step_name]
            node_info = {
                'id': step_name,
                'label': step_name,
                'flow': step_name.split('.')[0] if '.' in step_name else '',
                'step': step_name.split('.')[1] if '.' in step_name else step_name,
                'cmd': step.cmd or '',
                'inputs': step.inputs or [],
                'outputs': step.outputs or [],
            }
            
            # 添加 sub_steps 信息（如果可用）
            if include_sub_steps and hasattr(step, 'sub_steps'):
                node_info['sub_steps'] = getattr(step, 'sub_steps', {})
            
            nodes.append(node_info)
            node_set.add(step_name)
        
        # 构建边（只包含在显示范围内的）
        for step_name in steps_to_show:
            if step_name not in self.dependencies:
                continue
                
            deps = self.dependencies[step_name]
            
            # 前置步骤 -> 当前步骤
            for prev_step in deps.get('prev', []):
                if prev_step in node_set:
                    edges.append({
                        'from': prev_step,
                        'to': step_name,
                        'type': 'dependency',
                        'label': self._get_edge_label(prev_step, step_name)
                    })
            
            # 当前步骤 -> 后续步骤
            for next_step in deps.get('next', []):
                if next_step in node_set:
                    edges.append({
                        'from': step_name,
                        'to': next_step,
                        'type': 'dependency',
                        'label': self._get_edge_label(step_name, next_step)
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_steps': len(self.steps),
                'displayed_steps': len(nodes),
                'focus_step': focus_step,
                'depth': depth
            }
        }
    
    def _get_related_steps(self, step_name: str, max_depth: Optional[int] = None) -> Set[str]:
        """
        获取与指定步骤相关的所有步骤（BFS）
        
        Args:
            step_name: 起始步骤名称
            max_depth: 最大深度，None 表示无限制
            
        Returns:
            相关步骤名称集合
        """
        if step_name not in self.steps:
            return set()
        
        related = {step_name}
        queue = deque([(step_name, 0)])  # (step_name, depth)
        
        while queue:
            current, depth = queue.popleft()
            
            if max_depth is not None and depth >= max_depth:
                continue
            
            # 添加前置步骤
            if current in self.dependencies:
                for prev_step in self.dependencies[current].get('prev', []):
                    if prev_step not in related:
                        related.add(prev_step)
                        queue.append((prev_step, depth + 1))
            
            # 添加后续步骤
            if current in self.dependencies:
                for next_step in self.dependencies[current].get('next', []):
                    if next_step not in related:
                        related.add(next_step)
                        queue.append((next_step, depth + 1))
        
        return related
    
    def _get_edge_label(self, from_step: str, to_step: str) -> str:
        """
        获取边的标签（显示传递的文件）
        
        Args:
            from_step: 源步骤
            to_step: 目标步骤
            
        Returns:
            边标签文本
        """
        if from_step not in self.steps or to_step not in self.steps:
            return ''
        
        from_step_obj = self.steps[from_step]
        to_step_obj = self.steps[to_step]
        
        # 找到从 from_step 输出到 to_step 输入的文件
        common_files = set(from_step_obj.outputs) & set(to_step_obj.inputs)
        
        if common_files:
            # 只显示第一个文件，避免标签过长
            return list(common_files)[0]
        return ''
    
    # ==================== CLI 文本输出 ====================
    
    def to_text_tree(self, 
                    focus_step: Optional[str] = None,
                    depth: Optional[int] = None) -> str:
        """
        生成文本树形图（ASCII art）
        
        Args:
            focus_step: 聚焦的步骤
            depth: 深度限制
            
        Returns:
            文本树形图字符串
        """
        graph_data = self.extract_graph_data(focus_step, depth)
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        if not nodes:
            return "没有找到步骤"
        
        # 构建邻接表
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)
        
        for edge in edges:
            adj_list[edge['from']].append(edge['to'])
            in_degree[edge['to']] += 1
        
        # 找到根节点（入度为 0）
        roots = [node['id'] for node in nodes if in_degree[node['id']] == 0]
        
        if not roots:
            # 如果没有根节点，选择第一个节点
            roots = [nodes[0]['id']]
        
        lines = []
        visited = set()
        
        def build_tree(node_id: str, prefix: str = '', is_last: bool = True):
            """递归构建树形结构"""
            if node_id in visited:
                return
            
            visited.add(node_id)
            
            # 当前节点
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node_id}")
            
            # 获取子节点
            children = sorted(adj_list[node_id])
            
            for i, child in enumerate(children):
                is_child_last = (i == len(children) - 1)
                child_prefix = prefix + ("    " if is_last else "│   ")
                build_tree(child, child_prefix, is_child_last)
        
        # 从每个根节点开始构建树
        for i, root in enumerate(roots):
            is_root_last = (i == len(roots) - 1)
            build_tree(root, "", is_root_last)
        
        # 处理没有根节点的节点（可能是循环依赖的一部分）
        for node in nodes:
            if node['id'] not in visited:
                lines.append(f"    {node['id']} (孤立节点或循环依赖)")
        
        # 添加元数据
        lines.append("")
        lines.append(f"总步骤数: {graph_data['metadata']['total_steps']}")
        lines.append(f"显示步骤数: {graph_data['metadata']['displayed_steps']}")
        
        return "\n".join(lines)
    
    # ==================== Graphviz 输出 ====================
    
    def to_graphviz(self,
                   output_file: Optional[Path] = None,
                   format: str = 'png',
                   focus_step: Optional[str] = None,
                   depth: Optional[int] = None,
                   layout: str = 'dot') -> str:
        """
        生成 Graphviz DOT 格式并可选导出为图片
        
        Args:
            output_file: 输出文件路径（可选）
            format: 输出格式（png, svg, pdf, dot）
            focus_step: 聚焦的步骤
            depth: 深度限制
            layout: 布局引擎（dot, neato, fdp, sfdp, twopi, circo）
            
        Returns:
            DOT 格式字符串
        """
        graph_data = self.extract_graph_data(focus_step, depth)
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        # 按 flow 分组节点，用于颜色编码
        flow_colors = self._get_flow_colors()
        
        lines = [f"digraph G {{"]
        lines.append(f"  rankdir=LR;")
        lines.append(f"  node [shape=box, style=rounded];")
        lines.append("")
        
        # 添加节点
        for node in nodes:
            node_id = node['id'].replace('.', '_').replace('-', '_')
            label = node['label']
            flow = node['flow']
            color = flow_colors.get(flow, 'gray')
            
            # 添加工具提示（显示输入输出文件）
            tooltip = f"\\nCmd: {node['cmd']}"
            if node['inputs']:
                tooltip += f"\\nInputs: {', '.join(node['inputs'][:3])}"
            if node['outputs']:
                tooltip += f"\\nOutputs: {', '.join(node['outputs'][:3])}"
            
            lines.append(f'  "{node_id}" [label="{label}", fillcolor="{color}", style="rounded,filled", tooltip="{tooltip}"];')
        
        lines.append("")
        
        # 添加边
        for edge in edges:
            from_id = edge['from'].replace('.', '_').replace('-', '_')
            to_id = edge['to'].replace('.', '_').replace('-', '_')
            label = edge['label']
            
            if label:
                lines.append(f'  "{from_id}" -> "{to_id}" [label="{label}"];')
            else:
                lines.append(f'  "{from_id}" -> "{to_id}";')
        
        lines.append("}")
        
        dot_content = "\n".join(lines)
        
        # 如果指定了输出文件且格式不是 dot，尝试生成图片
        if output_file and format != 'dot':
            try:
                import graphviz
                dot_graph = graphviz.Source(dot_content)
                dot_graph.render(
                    str(output_file.with_suffix('')),
                    format=format,
                    engine=layout,
                    cleanup=True
                )
            except ImportError:
                raise ImportError("需要安装 graphviz 库: pip install graphviz")
            except Exception as e:
                raise RuntimeError(f"生成图片失败: {e}")
        
        return dot_content
    
    def _get_flow_colors(self) -> Dict[str, str]:
        """获取 flow 到颜色的映射"""
        flows = set()
        for step_name in self.steps.keys():
            if '.' in step_name:
                flows.add(step_name.split('.')[0])
        
        # 使用预定义的颜色
        colors = [
            'lightblue', 'lightgreen', 'lightyellow', 'lightpink',
            'lightcoral', 'lightgray', 'lightsalmon', 'lightseagreen'
        ]
        
        return {flow: colors[i % len(colors)] for i, flow in enumerate(sorted(flows))}
    
    # ==================== Mermaid 输出 ====================
    
    def to_mermaid(self,
                  focus_step: Optional[str] = None,
                  depth: Optional[int] = None) -> str:
        """
        生成 Mermaid 图表格式（Markdown 兼容）
        
        Args:
            focus_step: 聚焦的步骤
            depth: 深度限制
            
        Returns:
            Mermaid 格式字符串
        """
        graph_data = self.extract_graph_data(focus_step, depth)
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        lines = ["```mermaid", "graph LR"]
        
        # 添加节点（使用简化的 ID）
        node_id_map = {}
        for i, node in enumerate(nodes):
            node_id = f"step{i}"
            node_id_map[node['id']] = node_id
            label = node['label']
            lines.append(f"    {node_id}[\"{label}\"]")
        
        lines.append("")
        
        # 添加边
        for edge in edges:
            from_id = node_id_map[edge['from']]
            to_id = node_id_map[edge['to']]
            label = edge['label']
            
            if label:
                lines.append(f"    {from_id} -->|{label}| {to_id}")
            else:
                lines.append(f"    {from_id} --> {to_id}")
        
        lines.append("```")
        
        return "\n".join(lines)
    
    # ==================== Web 交互式可视化 ====================
    
    def to_web_html(self,
                    output_file: Path,
                    focus_step: Optional[str] = None,
                    depth: Optional[int] = None,
                    title: str = "EDP 依赖关系图") -> Path:
        """
        生成 Web 交互式可视化 HTML 文件
        
        Args:
            output_file: 输出 HTML 文件路径
            focus_step: 聚焦的步骤
            depth: 深度限制
            title: 页面标题
            
        Returns:
            输出文件路径
        """
        graph_data = self.extract_graph_data(focus_step, depth, include_sub_steps=True)
        
        # 读取 HTML 模板
        html_template = self._get_web_template()
        
        # 将数据嵌入 HTML
        html_content = html_template.replace(
            '{{GRAPH_DATA}}',
            json.dumps(graph_data, ensure_ascii=False, indent=2)
        ).replace(
            '{{TITLE}}',
            title or "EDP 依赖关系图"
        )
        
        # 写入文件
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
        
        return output_file
    
    def _get_web_template(self) -> str:
        """获取 Web 可视化 HTML 模板"""
        # 从模板文件读取
        template_path = Path(__file__).parent / 'templates' / 'graph_web_template.html'
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        else:
            # 如果模板文件不存在，返回一个简单的错误提示
            return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{TITLE}}</title>
</head>
<body>
    <h1>错误：模板文件未找到</h1>
    <p>请确保模板文件存在于: {}</p>
</body>
</html>""".format(template_path)
