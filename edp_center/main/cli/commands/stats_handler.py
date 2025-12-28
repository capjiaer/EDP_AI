#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能分析功能处理模块
处理 -stats 命令，分析和展示性能统计数据
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict

from ..utils import infer_work_path_info, infer_project_info
from .history_handler import load_run_history, filter_history


def calculate_stats(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算性能统计数据
    
    Args:
        runs: 运行历史记录列表
        
    Returns:
        统计数据字典
    """
    if not runs:
        return {
            'total_runs': 0,
            'success_count': 0,
            'failed_count': 0,
            'unknown_count': 0,
            'success_rate': 0.0,
            'avg_duration': None,
            'min_duration': None,
            'max_duration': None,
            'total_duration': 0.0,
            'avg_cpu': None,
            'avg_memory': None
        }
    
    # 统计执行次数和状态
    total_runs = len(runs)
    success_count = sum(1 for r in runs if r.get('status') == 'success')
    failed_count = sum(1 for r in runs if r.get('status') == 'failed')
    unknown_count = total_runs - success_count - failed_count
    success_rate = (success_count / total_runs * 100) if total_runs > 0 else 0.0
    
    # 统计执行时长
    durations = [r.get('duration') for r in runs if r.get('duration') is not None]
    avg_duration = sum(durations) / len(durations) if durations else None
    min_duration = min(durations) if durations else None
    max_duration = max(durations) if durations else None
    total_duration = sum(durations) if durations else 0.0
    
    # 统计资源使用
    cpu_values = []
    memory_values = []
    for r in runs:
        resources = r.get('resources', {})
        if resources.get('cpu_used') is not None:
            cpu_values.append(resources['cpu_used'])
        if resources.get('peak_memory') is not None:
            memory_values.append(resources['peak_memory'])
    
    avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else None
    avg_memory = sum(memory_values) / len(memory_values) if memory_values else None
    
    return {
        'total_runs': total_runs,
        'success_count': success_count,
        'failed_count': failed_count,
        'unknown_count': unknown_count,
        'success_rate': success_rate,
        'avg_duration': avg_duration,
        'min_duration': min_duration,
        'max_duration': max_duration,
        'total_duration': total_duration,
        'avg_cpu': avg_cpu,
        'avg_memory': avg_memory
    }


def calculate_step_stats(runs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    按步骤分组计算统计数据
    
    Args:
        runs: 运行历史记录列表
        
    Returns:
        按步骤分组的统计数据字典 {step_name: stats}
    """
    step_runs = defaultdict(list)
    
    # 按步骤分组
    for run in runs:
        flow = run.get('flow', '')
        step = run.get('step', '')
        step_name = f"{flow}.{step}" if flow and step else step or flow
        step_runs[step_name].append(run)
    
    # 计算每个步骤的统计
    step_stats = {}
    for step_name, step_runs_list in step_runs.items():
        step_stats[step_name] = calculate_stats(step_runs_list)
    
    return step_stats


def format_duration(seconds: Optional[float]) -> str:
    """
    格式化时长显示
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的字符串（如 "1h 23m 45s"）
    """
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def format_memory(mb: Optional[float]) -> str:
    """
    格式化内存显示
    
    Args:
        mb: 内存大小（MB）
        
    Returns:
        格式化后的字符串（如 "12.5GB" 或 "512MB"）
    """
    if mb is None:
        return "N/A"
    
    if mb >= 1024:
        return f"{mb / 1024:.1f}GB"
    else:
        return f"{int(mb)}MB"


def display_stats_cli(runs: List[Dict[str, Any]], step_filter: Optional[str] = None, show_trend: bool = False) -> None:
    """
    在 CLI 中显示性能统计数据
    
    Args:
        runs: 运行历史记录列表
        step_filter: 步骤过滤器
        show_trend: 是否显示趋势
    """
    if not runs:
        print("[INFO] 未找到匹配的历史记录", file=sys.stderr)
        return
    
    # 计算总体统计
    overall_stats = calculate_stats(runs)
    
    # 标题
    if step_filter:
        if '.' in step_filter:
            title = f"{step_filter} 性能统计"
        else:
            title = f"步骤 '{step_filter}' 性能统计"
    else:
        title = "性能统计"
    
    print(f"\n{'━'*80}", file=sys.stderr)
    print(f"{title}", file=sys.stderr)
    print(f"{'━'*80}", file=sys.stderr)
    
    # 总体统计
    print(f"\n📊 总体统计:", file=sys.stderr)
    print(f"  - 总执行次数: {overall_stats['total_runs']}", file=sys.stderr)
    print(f"  - 成功: {overall_stats['success_count']} ({overall_stats['success_rate']:.1f}%)", file=sys.stderr)
    print(f"  - 失败: {overall_stats['failed_count']}", file=sys.stderr)
    if overall_stats['unknown_count'] > 0:
        print(f"  - 未知状态: {overall_stats['unknown_count']}", file=sys.stderr)
    
    # 执行时长统计
    if overall_stats['avg_duration'] is not None:
        print(f"\n⏱️  执行时长:", file=sys.stderr)
        print(f"  - 平均: {format_duration(overall_stats['avg_duration'])}", file=sys.stderr)
        print(f"  - 最短: {format_duration(overall_stats['min_duration'])}", file=sys.stderr)
        print(f"  - 最长: {format_duration(overall_stats['max_duration'])}", file=sys.stderr)
        print(f"  - 总计: {format_duration(overall_stats['total_duration'])}", file=sys.stderr)
    
    # 资源使用统计
    if overall_stats['avg_cpu'] is not None or overall_stats['avg_memory'] is not None:
        print(f"\n💻 资源使用:", file=sys.stderr)
        if overall_stats['avg_cpu'] is not None:
            print(f"  - 平均 CPU: {overall_stats['avg_cpu']:.1f} 核", file=sys.stderr)
        if overall_stats['avg_memory'] is not None:
            print(f"  - 平均内存: {format_memory(overall_stats['avg_memory'])}", file=sys.stderr)
    
    # 按步骤分组统计（如果未指定步骤过滤器）
    if not step_filter and len(runs) > 1:
        step_stats = calculate_step_stats(runs)
        if step_stats:
            print(f"\n📈 按步骤统计:", file=sys.stderr)
            print(f"{'步骤':<40} {'执行次数':<10} {'成功率':<10} {'平均时长':<15}", file=sys.stderr)
            print(f"{'-'*80}", file=sys.stderr)
            
            # 按执行次数排序
            sorted_steps = sorted(step_stats.items(), key=lambda x: x[1]['total_runs'], reverse=True)
            for step_name, stats in sorted_steps:
                success_rate_str = f"{stats['success_rate']:.1f}%" if stats['total_runs'] > 0 else "N/A"
                avg_duration_str = format_duration(stats['avg_duration'])
                print(f"{step_name:<40} {stats['total_runs']:<10} {success_rate_str:<10} {avg_duration_str:<15}", file=sys.stderr)
    
    # 趋势分析（如果启用）
    if show_trend and len(runs) > 1:
        print(f"\n📉 趋势分析:", file=sys.stderr)
        # 按时间排序
        sorted_runs = sorted(runs, key=lambda x: x.get('timestamp', ''))
        
        # 计算最近几次的执行情况
        recent_runs = sorted_runs[-10:] if len(sorted_runs) > 10 else sorted_runs
        recent_success = sum(1 for r in recent_runs if r.get('status') == 'success')
        recent_failed = sum(1 for r in recent_runs if r.get('status') == 'failed')
        recent_rate = (recent_success / len(recent_runs) * 100) if recent_runs else 0.0
        
        print(f"  - 最近 {len(recent_runs)} 次执行成功率: {recent_rate:.1f}%", file=sys.stderr)
        
        # 时长趋势
        recent_durations = [r.get('duration') for r in recent_runs if r.get('duration') is not None]
        if recent_durations:
            recent_avg = sum(recent_durations) / len(recent_durations)
            if overall_stats['avg_duration']:
                trend = "📈 上升" if recent_avg > overall_stats['avg_duration'] else "📉 下降"
                print(f"  - 最近平均时长: {format_duration(recent_avg)} ({trend})", file=sys.stderr)


def handle_stats_cmd(manager, args) -> int:
    """
    处理 -stats 命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    try:
        # 获取当前工作目录
        current_dir = Path.cwd().resolve()
        
        # 推断项目信息
        project_info = infer_project_info(manager, current_dir, args)
        if not project_info:
            print(f"[ERROR] 无法推断项目信息，请确保在正确的工作目录下运行", file=sys.stderr)
            print(f"[INFO] 或者手动指定: --edp-center, --project, --foundry, --node", file=sys.stderr)
            return 1
        
        # 推断工作路径信息
        work_path_info = infer_work_path_info(current_dir, args, project_info)
        if not work_path_info or not work_path_info.get('work_path') or \
           not work_path_info.get('project') or not work_path_info.get('version') or \
           not work_path_info.get('block') or not work_path_info.get('user') or \
           not work_path_info.get('branch'):
            print(f"[ERROR] 无法推断工作路径信息，请确保在正确的工作目录下运行", file=sys.stderr)
            print(f"[INFO] 或者手动指定: --work-path, --project, --version, --block, --user, --branch", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"[ERROR] 推断工作路径信息时出错: {e}", file=sys.stderr)
        return 1
    
    # 构建 branch 目录路径
    work_path = Path(work_path_info['work_path']).resolve()
    project = work_path_info['project']
    version = work_path_info['version']
    block = work_path_info['block']
    user = work_path_info['user']
    branch = work_path_info['branch']
    branch_dir = work_path / project / version / block / user / branch
    
    if not branch_dir.exists():
        print(f"[ERROR] 分支目录不存在: {branch_dir}", file=sys.stderr)
        return 1
    
    # 加载运行历史
    runs = load_run_history(branch_dir)
    
    # 检查是否有数据
    run_info_file = branch_dir / '.run_info'
    if not run_info_file.exists():
        print(f"[INFO] 未找到运行历史记录（.run_info 文件不存在）", file=sys.stderr)
        print(f"[INFO] 分支目录: {branch_dir}", file=sys.stderr)
        print(f"[INFO] 请先执行一些步骤（使用 edp -run），然后再次查看统计", file=sys.stderr)
        return 0
    
    if not runs:
        print(f"[INFO] 运行历史记录为空（.run_info 文件存在但无数据）", file=sys.stderr)
        print(f"[INFO] 分支目录: {branch_dir}", file=sys.stderr)
        return 0
    
    # 应用过滤器
    step_filter = args.stats  # 如果提供了 flow.step 参数
    if step_filter:
        original_count = len(runs)
        runs = filter_history(runs, step_filter=step_filter)
        if not runs:
            print(f"[INFO] 未找到匹配的历史记录（步骤 '{step_filter}' 没有执行记录）", file=sys.stderr)
            print(f"[INFO] 总记录数: {original_count}", file=sys.stderr)
            return 0
    
    # 显示统计
    show_trend = getattr(args, 'trend', False)
    display_stats_cli(runs, step_filter=step_filter, show_trend=show_trend)
    
    # 导出功能（如果指定）
    export_file = getattr(args, 'export', None)
    if export_file:
        # TODO: 实现导出功能
        print(f"[INFO] 导出功能正在开发中，目标文件: {export_file}", file=sys.stderr)
    
    return 0

