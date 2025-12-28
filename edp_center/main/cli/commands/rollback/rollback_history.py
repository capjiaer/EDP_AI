#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rollback History - 回滚历史记录模块

负责加载和查找运行历史记录。
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


def load_run_history(branch_dir: Path) -> List[Dict]:
    """
    加载运行历史记录
    
    Args:
        branch_dir: branch 目录路径
        
    Returns:
        运行历史记录列表
    """
    run_info_file = branch_dir / '.run_info'
    if not run_info_file.exists():
        return []
    
    try:
        with open(run_info_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            return data.get('runs', [])
    except Exception as e:
        print(f"[ERROR] 读取 .run_info 文件失败: {e}", file=sys.stderr)
        return []


def find_target_runs(run_history: List[Dict], args) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    根据参数找到要对比的两个运行记录
    
    Args:
        run_history: 运行历史记录列表
        args: 命令行参数
        
    Returns:
        (记录1, 记录2) - 记录1通常是较早的或作为基准的记录，记录2是较新的或要对比的记录
    """
    if not run_history:
        return None, None
    
    # 如果指定了对比两个索引
    if hasattr(args, 'compare_indices') and args.compare_indices:
        indices = args.compare_indices
        if len(indices) != 2:
            print(f"[ERROR] --compare-index 需要两个参数，例如: --compare-index 1 3", file=sys.stderr)
            return None, None
        
        index1, index2 = indices
        if index1 < 1 or index1 > len(run_history) or index2 < 1 or index2 > len(run_history):
            print(f"[ERROR] 索引超出范围（1-{len(run_history)}）", file=sys.stderr)
            return None, None
        
        if index1 == index2:
            print(f"[ERROR] 不能对比同一条记录（索引 {index1}）", file=sys.stderr)
            return None, None
        
        # 索引从1开始，列表从后往前，所以 -index 表示倒数第index个
        run1 = run_history[-index1]
        run2 = run_history[-index2]
        
        # 返回较早的记录作为第一个（基准），较新的作为第二个（对比）
        # 通过比较时间戳来确定顺序
        timestamp1 = run1.get('timestamp', '')
        timestamp2 = run2.get('timestamp', '')
        if timestamp1 and timestamp2 and timestamp1 < timestamp2:
            return run1, run2
        else:
            return run2, run1
    
    # 如果指定了单个索引
    if hasattr(args, 'index') and args.index is not None:
        index = args.index
        if index < 1 or index > len(run_history):
            print(f"[ERROR] 索引 {index} 超出范围（1-{len(run_history)}）", file=sys.stderr)
            return None, None
        target_run = run_history[-index]  # 索引从1开始，列表从后往前
        # 找到最近一次成功或失败的运行
        if target_run.get('status') == 'success':
            # 找最近一次失败的运行
            for run in reversed(run_history):
                if run.get('status') == 'failed' and run != target_run:
                    return target_run, run
        else:
            # 找最近一次成功的运行
            for run in reversed(run_history):
                if run.get('status') == 'success' and run != target_run:
                    return run, target_run
        return None, None
    
    # 如果指定了时间点
    if hasattr(args, 'rollback_to_time') and args.rollback_to_time:
        return find_runs_by_time(run_history, args.rollback_to_time)
    
    # 默认：找最近一次成功和最近一次失败的运行
    success_run = None
    failed_run = None
    
    for run in reversed(run_history):
        if run.get('status') == 'success' and success_run is None:
            success_run = run
        elif run.get('status') == 'failed' and failed_run is None:
            failed_run = run
        
        if success_run and failed_run:
            break
    
    return success_run, failed_run


def _parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    解析时间戳字符串
    
    Args:
        timestamp_str: 时间戳字符串（格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD）
        
    Returns:
        datetime 对象，如果解析失败返回 None
    """
    if not timestamp_str:
        return None
    
    # 尝试解析完整格式: YYYY-MM-DD HH:MM:SS
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    
    # 尝试解析日期格式: YYYY-MM-DD
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d')
    except ValueError:
        pass
    
    return None


def find_runs_by_time(run_history: List[Dict], target_time: str) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    按时间点查找运行记录
    
    Args:
        run_history: 运行历史记录列表
        target_time: 目标时间点（格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD）
        
    Returns:
        (目标时间点之前的最后一次成功运行, 目标时间点之后的第一次运行)
        如果找不到，返回 (None, None)
    """
    target_dt = _parse_timestamp(target_time)
    if not target_dt:
        print(f"[ERROR] 无效的时间格式: {target_time}", file=sys.stderr)
        print(f"[INFO] 支持的格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD", file=sys.stderr)
        return None, None
    
    # 如果只提供了日期，设置为当天的 23:59:59
    if len(target_time) == 10:  # YYYY-MM-DD
        target_dt = target_dt.replace(hour=23, minute=59, second=59)
    
    # 查找目标时间点之前的最后一次成功运行
    before_success = None
    # 查找目标时间点之后的第一次运行（成功或失败）
    after_run = None
    
    for run in run_history:
        run_timestamp = run.get('timestamp', '')
        run_dt = _parse_timestamp(run_timestamp)
        
        if not run_dt:
            continue
        
        # 查找目标时间点之前的最后一次成功运行
        if run_dt <= target_dt and run.get('status') == 'success':
            if before_success is None:
                before_success = run
            else:
                before_dt = _parse_timestamp(before_success.get('timestamp', ''))
                if before_dt and run_dt > before_dt:
                    before_success = run
        
        # 查找目标时间点之后的第一次运行
        if run_dt > target_dt:
            if after_run is None:
                after_run = run
            else:
                after_dt = _parse_timestamp(after_run.get('timestamp', ''))
                if after_dt and run_dt < after_dt:
                    after_run = run
    
    if not before_success:
        print(f"[WARN] 未找到时间点 {target_time} 之前的成功运行", file=sys.stderr)
        if after_run:
            print(f"[INFO] 找到时间点之后的运行: {after_run.get('timestamp')} ({after_run.get('flow')}.{after_run.get('step')})", file=sys.stderr)
        return None, after_run
    
    if not after_run:
        print(f"[INFO] 未找到时间点 {target_time} 之后的运行", file=sys.stderr)
        return before_success, None
    
    return before_success, after_run


def try_restore_from_backup(full_tcl_path: Path, run_info: Dict, context: str, all_runs: List[Dict] = None) -> Optional[Path]:
    """
    尝试从备份目录恢复 full.tcl 文件
    
    Args:
        full_tcl_path: full.tcl 文件路径
        run_info: 运行信息字典
        context: 上下文信息（用于错误提示）
        all_runs: 所有运行记录列表（可选，用于查找备份）
        
    Returns:
        备份文件路径，如果找不到返回 None
    """
    if not full_tcl_path or not full_tcl_path.exists():
        return None
    
    # 从 run_info 中获取 full_tcl_path（可能是相对路径）
    backup_path_str = run_info.get('full_tcl_path')
    if not backup_path_str:
        return None
    
    # 构建备份路径
    backup_dir = full_tcl_path.parent / 'backup'
    backup_path = backup_dir / backup_path_str
    
    if backup_path.exists():
        return backup_path
    
    # 如果直接路径不存在，尝试从时间戳查找
    run_timestamp = run_info.get('timestamp', '')
    if run_timestamp and all_runs:
        # 从时间戳中提取日期和时间部分
        try:
            dt = datetime.strptime(run_timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp_str = dt.strftime('%Y%m%d_%H%M%S')
            
            # 查找匹配的备份文件
            if backup_dir.exists():
                for backup_file in backup_dir.glob(f'*{timestamp_str}*'):
                    if backup_file.suffix == '.tcl':
                        return backup_file
        except ValueError:
            pass
    
    return None
