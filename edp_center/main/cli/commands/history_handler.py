#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
历史查询功能处理模块
处理 -history 命令，查询和显示运行历史
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

from ..utils import infer_work_path_info, infer_project_info


def load_run_history(branch_dir: Path) -> List[Dict[str, Any]]:
    """
    从 .run_info 文件加载运行历史
    
    Args:
        branch_dir: branch 目录路径
        
    Returns:
        运行历史记录列表（按时间倒序）
    """
    run_info_file = branch_dir / '.run_info'
    
    if not run_info_file.exists():
        return []
    
    try:
        with open(run_info_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            runs = data.get('runs', [])
            
            # 按时间戳正序排序（最旧的在最上面，最新的在最下面，方便滚动到底部查看最新记录）
            runs.sort(key=lambda x: x.get('timestamp', ''), reverse=False)
            
            return runs
    except Exception as e:
        print(f"[WARN] 读取 .run_info 文件失败: {e}", file=sys.stderr)
        return []


def filter_history(
    runs: List[Dict[str, Any]],
    step_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    过滤历史记录
    
    Args:
        runs: 运行历史记录列表
        step_filter: 步骤过滤器（格式: flow.step 或 step）
        status_filter: 状态过滤器（success/failed）
        from_date: 起始日期（格式: YYYY-MM-DD）
        to_date: 结束日期（格式: YYYY-MM-DD）
        limit: 限制返回的记录数量
        
    Returns:
        过滤后的运行历史记录列表
    """
    filtered = runs
    
    # 步骤过滤
    if step_filter:
        # 支持 flow.step 或 step 格式
        if '.' in step_filter:
            flow_name, step_name = step_filter.split('.', 1)
            filtered = [
                run for run in filtered
                if run.get('flow') == flow_name and run.get('step') == step_name
            ]
        else:
            # 只匹配 step 名称
            filtered = [
                run for run in filtered
                if run.get('step') == step_filter
            ]
    
    # 状态过滤
    if status_filter:
        status_filter = status_filter.lower()
        filtered = [
            run for run in filtered
            if run.get('status', '').lower() == status_filter
        ]
    
    # 日期过滤
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            filtered = [
                run for run in filtered
                if _parse_timestamp(run.get('timestamp', '')) >= from_dt
            ]
        except ValueError:
            print(f"[WARN] 无效的起始日期格式: {from_date}，忽略此过滤条件", file=sys.stderr)
    
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            # 设置为当天的 23:59:59
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            filtered = [
                run for run in filtered
                if _parse_timestamp(run.get('timestamp', '')) <= to_dt
            ]
        except ValueError:
            print(f"[WARN] 无效的结束日期格式: {to_date}，忽略此过滤条件", file=sys.stderr)
    
    # 限制数量
    if limit and limit > 0:
        filtered = filtered[:limit]
    
    return filtered


def _parse_timestamp(timestamp_str: str) -> datetime:
    """
    解析时间戳字符串
    
    Args:
        timestamp_str: 时间戳字符串（格式: YYYY-MM-DD HH:MM:SS）
        
    Returns:
        datetime 对象
    """
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        # 尝试其他格式
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%d')
        except ValueError:
            return datetime.min


def format_duration(seconds: Optional[float]) -> str:
    """
    格式化执行时长
    
    Args:
        seconds: 执行时长（秒）
        
    Returns:
        格式化后的时长字符串
    """
    if seconds is None:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_status(status: Optional[str]) -> Tuple[str, str]:
    """
    格式化状态显示
    
    Args:
        status: 状态字符串
        
    Returns:
        (状态符号, 状态文本) 元组
    """
    if status == 'success':
        return ('✅', 'success')
    elif status == 'failed':
        return ('❌', 'failed')
    elif status == 'running':
        return ('⏳', 'running')
    else:
        return ('⚪', status or 'unknown')


def format_resource_info(run: Dict[str, Any]) -> str:
    """
    格式化资源使用信息
    
    Args:
        run: 运行记录字典
        
    Returns:
        格式化后的资源信息字符串
    """
    resources = run.get('resources', {})
    parts = []
    
    # CPU 信息
    cpu_used = resources.get('cpu_used')
    if cpu_used is not None:
        parts.append(f"CPU: {cpu_used}")
    
    # 内存信息
    peak_memory = resources.get('peak_memory')
    if peak_memory is not None:
        if peak_memory >= 1024:
            parts.append(f"Mem: {peak_memory/1024:.1f}GB")
        else:
            parts.append(f"Mem: {peak_memory}MB")
    
    return " | ".join(parts) if parts else ""


def display_history(runs: List[Dict[str, Any]], step_filter: Optional[str] = None) -> None:
    """
    显示历史记录
    
    Args:
        runs: 运行历史记录列表
        step_filter: 步骤过滤器（用于标题显示）
    """
    if not runs:
        print("[INFO] 未找到匹配的历史记录", file=sys.stderr)
        return
    
    # 标题
    if step_filter:
        if '.' in step_filter:
            title = f"{step_filter} 执行历史"
        else:
            title = f"步骤 '{step_filter}' 执行历史"
    else:
        title = "运行历史"
    
    print(f"\n{'━'*80}", file=sys.stderr)
    print(f"{title} (共 {len(runs)} 条记录):", file=sys.stderr)
    print(f"{'━'*80}", file=sys.stderr)
    
    # 显示记录
    for idx, run in enumerate(runs, 1):
        timestamp = run.get('timestamp', 'N/A')
        flow = run.get('flow', 'N/A')
        step = run.get('step', 'N/A')
        status = run.get('status')
        duration = run.get('duration')
        error = run.get('error')
        resources = format_resource_info(run)
        
        # 状态符号和文本
        status_symbol, status_text = format_status(status)
        
        # 格式化时长
        duration_str = format_duration(duration)
        
        # 步骤显示
        if step_filter and '.' in step_filter:
            step_display = f"{flow}.{step}"
        else:
            step_display = f"{flow}.{step}"
        
        # 基本信息行
        info_line = f"[{idx}] {timestamp} | {step_display} | {status_symbol} {status_text} | {duration_str}"
        if resources:
            info_line += f" | {resources}"
        print(info_line, file=sys.stderr)
        
        # 错误信息（如果有）
        if error:
            print(f"     错误: {error}", file=sys.stderr)
        
        # LSF Job ID（如果有）
        lsf_job_id = run.get('lsf_job_id')
        if lsf_job_id:
            print(f"     LSF Job ID: {lsf_job_id}", file=sys.stderr)
    
    print(f"{'━'*80}\n", file=sys.stderr)
    
    # 统计信息
    if len(runs) > 1:
        _display_statistics(runs)


def _display_statistics(runs: List[Dict[str, Any]]) -> None:
    """
    显示统计信息
    
    Args:
        runs: 运行历史记录列表
    """
    total = len(runs)
    success_count = sum(1 for run in runs if run.get('status') == 'success')
    failed_count = sum(1 for run in runs if run.get('status') == 'failed')
    
    durations = [run.get('duration') for run in runs if run.get('duration') is not None]
    
    print("统计信息:", file=sys.stderr)
    print(f"  - 总执行次数: {total}", file=sys.stderr)
    if total > 0:
        success_rate = (success_count / total) * 100
        print(f"  - 成功率: {success_rate:.1f}% ({success_count}/{total})", file=sys.stderr)
    
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        print(f"  - 平均执行时间: {format_duration(avg_duration)}", file=sys.stderr)
        print(f"  - 最短执行时间: {format_duration(min_duration)}", file=sys.stderr)
        print(f"  - 最长执行时间: {format_duration(max_duration)}", file=sys.stderr)
    print("", file=sys.stderr)


def handle_history_cmd(manager, args) -> int:
    """
    处理 -history 命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
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
        
        if not runs:
            print(f"[INFO] 未找到运行历史记录（.run_info 文件不存在或为空）", file=sys.stderr)
            print(f"[INFO] 分支目录: {branch_dir}", file=sys.stderr)
            return 0
        
        # 获取过滤参数
        step_filter = args.history  # 可能是 flow.step 格式
        status_filter = getattr(args, 'status', None)  # --status 参数
        from_date = getattr(args, 'history_from', None)  # --from-date 参数
        to_date = getattr(args, 'history_to', None)  # --to-date 参数
        limit = getattr(args, 'limit', None)  # --limit 参数
        
        # 过滤历史记录
        filtered_runs = filter_history(
            runs,
            step_filter=step_filter,
            status_filter=status_filter,
            from_date=from_date,
            to_date=to_date,
            limit=limit
        )
        
        # 显示历史记录
        display_history(filtered_runs, step_filter=step_filter)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] 查询历史记录失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

