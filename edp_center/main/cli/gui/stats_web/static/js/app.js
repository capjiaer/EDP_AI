let durationChart = null;
let successRateChart = null;
let resourceChart = null;

// 格式化时长
function formatDuration(seconds) {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const parts = [];
    if (hours > 0) parts.push(hours + 'h');
    if (minutes > 0) parts.push(minutes + 'm');
    if (secs > 0 || parts.length === 0) parts.push(secs + 's');
    return parts.join(' ');
}

// 格式化内存
function formatMemory(mb) {
    if (!mb) return 'N/A';
    if (mb >= 1024) return (mb / 1024).toFixed(1) + 'GB';
    return Math.round(mb) + 'MB';
}

// 加载统计数据
async function loadStats() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('statsContent').style.display = 'none';
    document.getElementById('errorContent').style.display = 'none';
    
    try {
        // 加载总体统计
        const overallRes = await fetch('/api/stats/overall');
        const overallData = await overallRes.json();
        
        if (!overallData.success) {
            throw new Error(overallData.error || '加载失败');
        }
        
        // 加载步骤统计
        const stepsRes = await fetch('/api/stats/steps');
        const stepsData = await stepsRes.json();
        
        if (!stepsData.success) {
            throw new Error(stepsData.error || '加载失败');
        }
        
        // 加载历史记录
        const stepFilter = document.getElementById('stepFilter').value;
        const timeRange = document.getElementById('timeRange').value;
        let historyUrl = '/api/stats/history?';
        if (stepFilter) historyUrl += 'step=' + encodeURIComponent(stepFilter) + '&';
        if (timeRange !== 'all') {
            const limit = parseInt(timeRange) * 10;
            historyUrl += 'limit=' + limit;
        }
        
        const historyRes = await fetch(historyUrl);
        const historyData = await historyRes.json();
        
        if (!historyData.success) {
            throw new Error(historyData.error || '加载失败');
        }
        
        // 更新步骤筛选器
        updateStepFilter(Object.keys(stepsData.data));
        
        // 显示统计数据
        displayStats(overallData.data, stepsData.data, historyData.data);
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('statsContent').style.display = 'block';
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('errorContent').style.display = 'block';
        document.getElementById('errorMessage').textContent = '加载失败: ' + error.message;
    }
}

// 更新步骤筛选器
function updateStepFilter(steps) {
    const select = document.getElementById('stepFilter');
    const currentValue = select.value;
    
    select.innerHTML = '<option value="">所有步骤</option>';
    steps.forEach(step => {
        const option = document.createElement('option');
        option.value = step;
        option.textContent = step;
        select.appendChild(option);
    });
    
    if (currentValue) {
        select.value = currentValue;
    }
}

// 显示统计数据
function displayStats(overall, steps, history) {
    // 显示统计卡片
    const cardsContainer = document.getElementById('statsCards');
    const successRate = overall.success_rate || 0;
    const successClass = successRate >= 80 ? 'success' : successRate >= 50 ? 'warning' : 'danger';
    
    cardsContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-card-icon">📊</div>
            <div class="stat-card-label">总执行次数</div>
            <div class="stat-card-value">${overall.total_runs}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">✅</div>
            <div class="stat-card-label">成功率</div>
            <div class="stat-card-value ${successClass}">${successRate.toFixed(1)}%</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">⏱️</div>
            <div class="stat-card-label">平均时长</div>
            <div class="stat-card-value">${formatDuration(overall.avg_duration)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">💻</div>
            <div class="stat-card-label">平均CPU</div>
            <div class="stat-card-value">${overall.avg_cpu ? overall.avg_cpu.toFixed(1) : 'N/A'} 核</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">💾</div>
            <div class="stat-card-label">平均内存</div>
            <div class="stat-card-value">${formatMemory(overall.avg_memory)}</div>
        </div>
    `;
    
    // 绘制图表
    drawCharts(history);
    
    // 显示步骤统计表格
    displayStepStatsTable(steps);
}

// 绘制图表
function drawCharts(history) {
    const sortedHistory = history.sort((a, b) => {
        return new Date(a.timestamp) - new Date(b.timestamp);
    });
    
    const labels = sortedHistory.map(r => {
        const date = new Date(r.timestamp);
        return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    });
    
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    font: {
                        size: 12,
                        family: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
                    }
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    size: 14
                },
                bodyFont: {
                    size: 13
                }
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            y: {
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            }
        }
    };
    
    // 执行时长趋势图
    const durationData = sortedHistory.map(r => r.duration || null);
    if (durationChart) durationChart.destroy();
    durationChart = new Chart(document.getElementById('durationChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '执行时长 (秒)',
                data: durationData,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                ...chartOptions.scales,
                y: {
                    ...chartOptions.scales.y,
                    beginAtZero: true
                }
            }
        }
    });
    
    // 成功率趋势图
    const windowSize = 5;
    const successRateData = [];
    for (let i = 0; i < sortedHistory.length; i++) {
        const window = sortedHistory.slice(Math.max(0, i - windowSize + 1), i + 1);
        const successCount = window.filter(r => r.status === 'success').length;
        successRateData.push((successCount / window.length * 100).toFixed(1));
    }
    if (successRateChart) successRateChart.destroy();
    successRateChart = new Chart(document.getElementById('successRateChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '成功率 (%)',
                data: successRateData,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                ...chartOptions.scales,
                y: {
                    ...chartOptions.scales.y,
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
    
    // 资源使用趋势图
    const cpuData = sortedHistory.map(r => r.resources?.cpu_used || null);
    const memoryData = sortedHistory.map(r => r.resources?.peak_memory || null);
    if (resourceChart) resourceChart.destroy();
    resourceChart = new Chart(document.getElementById('resourceChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'CPU (核)',
                    data: cpuData,
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: '内存 (MB)',
                    data: memoryData,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            ...chartOptions,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// 显示步骤统计表格
function displayStepStatsTable(steps) {
    const tbody = document.getElementById('stepStatsBody');
    tbody.innerHTML = '';
    
    const sortedSteps = Object.entries(steps).sort((a, b) => b[1].total_runs - a[1].total_runs);
    
    sortedSteps.forEach(([stepName, stats]) => {
        const row = document.createElement('tr');
        const successRate = stats.success_rate || 0;
        const badgeClass = successRate >= 80 ? 'badge-success' : successRate >= 50 ? 'badge-warning' : 'badge-danger';
        
        row.innerHTML = `
            <td><strong>${stepName}</strong></td>
            <td>${stats.total_runs}</td>
            <td><span class="badge ${badgeClass}">${successRate.toFixed(1)}%</span></td>
            <td>${formatDuration(stats.avg_duration)}</td>
            <td>${formatDuration(stats.min_duration)}</td>
            <td>${formatDuration(stats.max_duration)}</td>
            <td>${stats.avg_cpu ? stats.avg_cpu.toFixed(1) : 'N/A'}</td>
            <td>${formatMemory(stats.avg_memory)}</td>
        `;
        tbody.appendChild(row);
    });
}

// 页面加载时自动加载数据
window.addEventListener('load', () => {
    loadStats();
});

