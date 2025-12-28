#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能分析功能处理模块
处理 -stats 命令，分析和展示性能统计数据
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict

from ..utils import infer_all_info, build_branch_dir
from .history_handler import load_run_history, filter_history
from edp_center.packages.edp_common.error_handler import handle_cli_error


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


def export_stats(runs: List[Dict[str, Any]], output_path: str, step_filter: Optional[str] = None, show_trend: bool = False):
    """
    导出统计信息到文件
    
    Args:
        runs: 运行历史记录列表
        output_path: 输出文件路径（支持 .csv, .json 格式）
        step_filter: 步骤过滤器
        show_trend: 是否显示趋势
    """
    output_file = Path(output_path)
    file_ext = output_file.suffix.lower()
    
    # 计算统计数据
    overall_stats = calculate_stats(runs)
    step_stats = calculate_step_stats(runs) if not step_filter else {}
    
    # 准备导出数据
    export_data = {
        'summary': {
            'total_runs': overall_stats['total_runs'],
            'success_count': overall_stats['success_count'],
            'failed_count': overall_stats['failed_count'],
            'unknown_count': overall_stats['unknown_count'],
            'success_rate': round(overall_stats['success_rate'], 2),
            'avg_duration': overall_stats['avg_duration'],
            'min_duration': overall_stats['min_duration'],
            'max_duration': overall_stats['max_duration'],
            'total_duration': overall_stats['total_duration'],
            'avg_cpu': overall_stats['avg_cpu'],
            'avg_memory': overall_stats['avg_memory']
        },
        'step_stats': {
            step_name: {
                'total_runs': stats['total_runs'],
                'success_count': stats['success_count'],
                'failed_count': stats['failed_count'],
                'success_rate': round(stats['success_rate'], 2),
                'avg_duration': stats['avg_duration'],
                'min_duration': stats['min_duration'],
                'max_duration': stats['max_duration']
            }
            for step_name, stats in step_stats.items()
        },
        'runs': runs
    }
    
    # 根据文件扩展名选择导出格式
    if file_ext == '.json':
        export_json(export_data, output_file)
    elif file_ext == '.csv':
        export_csv(export_data, output_file)
    else:
        # 默认使用 JSON 格式
        output_file = output_file.with_suffix('.json')
        export_json(export_data, output_file)
        print(f"[WARN] 未识别的文件格式，已导出为 JSON: {output_file}", file=sys.stderr)


def export_json(data: Dict[str, Any], output_file: Path):
    """导出为 JSON 格式"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def export_csv(data: Dict[str, Any], output_file: Path):
    """导出为 CSV 格式"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # 写入汇总信息
        writer.writerow(['统计类型', '指标', '值'])
        writer.writerow(['汇总', '总执行次数', data['summary']['total_runs']])
        writer.writerow(['汇总', '成功次数', data['summary']['success_count']])
        writer.writerow(['汇总', '失败次数', data['summary']['failed_count']])
        writer.writerow(['汇总', '成功率(%)', data['summary']['success_rate']])
        writer.writerow(['汇总', '平均时长(秒)', data['summary']['avg_duration']])
        writer.writerow(['汇总', '最短时长(秒)', data['summary']['min_duration']])
        writer.writerow(['汇总', '最长时长(秒)', data['summary']['max_duration']])
        writer.writerow(['汇总', '总时长(秒)', data['summary']['total_duration']])
        if data['summary']['avg_cpu'] is not None:
            writer.writerow(['汇总', '平均CPU(核)', data['summary']['avg_cpu']])
        if data['summary']['avg_memory'] is not None:
            writer.writerow(['汇总', '平均内存(MB)', data['summary']['avg_memory']])
        
        writer.writerow([])  # 空行
        
        # 写入步骤统计
        if data['step_stats']:
            writer.writerow(['步骤统计'])
            writer.writerow(['步骤', '执行次数', '成功次数', '失败次数', '成功率(%)', '平均时长(秒)', '最短时长(秒)', '最长时长(秒)'])
            for step_name, stats in data['step_stats'].items():
                writer.writerow([
                    step_name,
                    stats['total_runs'],
                    stats['success_count'],
                    stats['failed_count'],
                    stats['success_rate'],
                    stats['avg_duration'],
                    stats['min_duration'],
                    stats['max_duration']
                ])
            
            writer.writerow([])  # 空行
        
        # 写入详细运行记录
        writer.writerow(['详细运行记录'])
        writer.writerow(['时间戳', '流程', '步骤', '状态', '时长(秒)', 'CPU(核)', '内存(MB)'])
        for run in data['runs']:
            resources = run.get('resources', {})
            writer.writerow([
                run.get('timestamp', ''),
                run.get('flow', ''),
                run.get('step', ''),
                run.get('status', ''),
                run.get('duration', ''),
                resources.get('cpu_used', ''),
                resources.get('peak_memory', '')
            ])


def handle_stats_cmd(manager, args) -> int:
    """
    处理 -stats 命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 推断所有信息（项目信息、工作路径信息、branch 目录）
    project_info, work_path_info, branch_dir = infer_all_info(manager, args)
    if not project_info or not work_path_info or not branch_dir:
        return 1
    
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
        try:
            export_stats(runs, export_file, step_filter=step_filter, show_trend=show_trend)
            print(f"[OK] 统计信息已导出到: {export_file}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] 导出失败: {e}", file=sys.stderr)
            return 1
    
    return 0

