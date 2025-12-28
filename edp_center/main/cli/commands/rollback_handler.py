#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rollback Handler - 回滚功能处理器

主要功能：
1. 对比两次执行的 full.tcl 配置差异
2. 帮助用户找出配置变化，定位问题
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ..utils import infer_all_info, build_branch_dir
from edp_center.packages.edp_common.error_handler import handle_cli_error

# 导入拆分后的模块
from .rollback import (
    load_run_history,
    find_target_runs,
    parse_full_tcl,
    compare_configs,
    display_config_diff
)


@handle_cli_error(error_message="执行 rollback 命令失败")
def handle_rollback_cmd(manager, args) -> int:
    """
    处理 rollback 命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数
        
    Returns:
        退出码
    """
    # 推断所有信息（项目信息、工作路径信息、branch 目录）
    project_info, work_path_info, branch_dir = infer_all_info(manager, args)
    if not project_info or not work_path_info or not branch_dir:
        return 1
    
    # 从 work_path_info 中提取信息（用于后续的跨 branch 对比）
    work_path = Path(work_path_info['work_path']).resolve()
    project = work_path_info['project']
    version = work_path_info['version']
    block = work_path_info['block']
    user = work_path_info['user']
    branch = work_path_info['branch']
    
    # 加载运行历史
    run_history = load_run_history(branch_dir)
    if not run_history:
        print("[WARN] 未找到运行历史记录", file=sys.stderr)
        return 1
    
    # 如果是预览模式
    if hasattr(args, 'rollback_dry_run') and args.rollback_dry_run:
        print("━" * 80)
        print("回滚预览 (Dry Run)")
        print("━" * 80)
        print()
        print("将对比以下运行记录的配置差异:")
        print()
        # 显示最近几次运行记录（显示索引）
        # 索引从1开始，1表示最近一次运行
        display_count = min(10, len(run_history))
        for i in range(display_count):
            idx = len(run_history) - i  # 索引（从1开始）
            run = run_history[-(i+1)]  # 从后往前取
            status = run.get('status', 'unknown')
            status_icon = '[OK]' if status == 'success' else '[FAIL]' if status == 'failed' else '[?]'
            print(f"  [{idx}] {run.get('timestamp', 'N/A')} | "
                  f"{run.get('flow', 'N/A')}.{run.get('step', 'N/A')} | "
                  f"{status_icon} {status}")
        print()
        print("使用说明:")
        print("  - 默认对比: edp -rollback")
        print("  - 对比指定索引: edp -rollback --compare-index 1 3")
        print("  - 对比单个索引与最近的成功/失败: edp -rollback --index 2")
        return 0
    
    # 找到要对比的两个运行记录
    run1, run2 = find_target_runs(run_history, args)
    
    if not run1 or not run2:
        print("[ERROR] 未找到可对比的运行记录", file=sys.stderr)
        if hasattr(args, 'compare_indices') and args.compare_indices:
            print("提示: 请确保指定的索引有效", file=sys.stderr)
        else:
            print("提示: 需要至少一次成功和一次失败的运行记录", file=sys.stderr)
            print("提示: 或使用 --compare-index 1 2 来指定要对比的两个记录", file=sys.stderr)
        return 1
    
    # 为了保持兼容性，使用 success_run 和 failed_run 变量名
    # 但实际上 run1 和 run2 可能是任意两次运行
    success_run = run1
    failed_run = run2
    
    # 获取 full.tcl 路径
    # 支持跨 branch 对比：如果指定了 --compare-branch，使用指定的 branch
    compare_branch = getattr(args, 'compare_branch', None)
    if compare_branch:
        # 使用指定的 branch 目录
        compare_branch_dir = work_path / project / version / block / user / compare_branch
        if not compare_branch_dir.exists():
            print(f"[ERROR] 指定的对比 branch 不存在: {compare_branch_dir}", file=sys.stderr)
            return 1
        
        # 加载对比 branch 的运行历史
        compare_run_history = load_run_history(compare_branch_dir)
        if not compare_run_history:
            print(f"[ERROR] 对比 branch 中没有运行历史记录: {compare_branch}", file=sys.stderr)
            return 1
        
        # 找到对比 branch 中最近一次成功的运行
        compare_success_run = None
        for run in reversed(compare_run_history):
            if run.get('status') == 'success':
                compare_success_run = run
                break
        
        if not compare_success_run:
            print(f"[ERROR] 对比 branch 中没有找到成功的运行记录: {compare_branch}", file=sys.stderr)
            return 1
        
        # 使用对比 branch 的成功运行和当前 branch 的失败运行
        success_run = compare_success_run
        success_full_tcl_path = compare_branch_dir / success_run.get('full_tcl_path', '')
        failed_full_tcl_path = branch_dir / failed_run.get('full_tcl_path', '')
        
        print(f"[INFO] 跨 branch 对比: {compare_branch} (成功) vs {branch} (失败)", file=sys.stderr)
    else:
        # 同一 branch 内的对比
        success_full_tcl_path = branch_dir / success_run.get('full_tcl_path', '')
        failed_full_tcl_path = branch_dir / failed_run.get('full_tcl_path', '')
    
    # 辅助函数：尝试从备份目录恢复文件
    def try_restore_from_backup(full_tcl_path: Path, run_info: Dict, context: str, all_runs: List[Dict] = None) -> Optional[Path]:
        """
        尝试从备份目录恢复 full.tcl 文件
        
        Args:
            full_tcl_path: full.tcl 文件路径
            run_info: 运行记录信息
            context: 上下文描述（用于日志）
            all_runs: 所有运行记录列表（用于判断是否有多个记录指向同一路径）
        """
        # 如果 full_tcl_path 指向备份目录，直接使用
        if 'backups' in str(full_tcl_path):
            if full_tcl_path.exists():
                return full_tcl_path
        
        # 如果文件存在，检查是否与其他运行记录共享同一路径
        if full_tcl_path.exists():
            # 检查是否有其他运行记录也指向这个路径
            if all_runs:
                same_path_count = sum(1 for r in all_runs 
                                    if r.get('full_tcl_path') == str(full_tcl_path.relative_to(branch_dir)).replace('\\', '/'))
                if same_path_count > 1:
                    # 有多个记录指向同一路径，需要根据时间戳从备份目录匹配
                    print(f"[INFO] {context}: 检测到多个运行记录共享同一 full.tcl 路径，尝试从备份目录匹配", file=sys.stderr)
                else:
                    # 只有一个记录指向这个路径，可以使用当前文件
                    return full_tcl_path
            else:
                # 没有提供 all_runs，直接使用当前文件
                return full_tcl_path
        
        # 文件不存在或需要从备份恢复
        backup_dir = full_tcl_path.parent / 'backups'
        if not backup_dir.exists():
            return None
        
        # 尝试根据时间戳匹配备份文件
        run_timestamp = run_info.get('timestamp', '')
        if run_timestamp:
            # 将时间戳转换为备份文件名格式：YYYYMMDD_HHMMSS
            try:
                dt = datetime.strptime(run_timestamp, '%Y-%m-%d %H:%M:%S')
                expected_backup_name = f"full_{dt.strftime('%Y%m%d_%H%M%S')}.tcl"
                expected_backup_path = backup_dir / expected_backup_name
                if expected_backup_path.exists():
                    print(f"[INFO] {context}: 根据时间戳从备份恢复文件: {expected_backup_path}", file=sys.stderr)
                    return expected_backup_path
            except ValueError:
                pass
        
        # 如果无法匹配时间戳，尝试找到最接近的备份文件（按时间排序）
        backup_files = sorted(backup_dir.glob('full_*.tcl'), reverse=True)
        if backup_files and run_timestamp:
            # 找到时间最接近的备份文件
            try:
                run_dt = datetime.strptime(run_timestamp, '%Y-%m-%d %H:%M:%S')
                best_match = None
                min_diff = None
                for backup_file in backup_files:
                    # 从文件名提取时间戳
                    try:
                        backup_name = backup_file.stem  # full_YYYYMMDD_HHMMSS
                        backup_timestamp_str = backup_name.replace('full_', '')
                        backup_dt = datetime.strptime(backup_timestamp_str, '%Y%m%d_%H%M%S')
                        diff = abs((run_dt - backup_dt).total_seconds())
                        if min_diff is None or diff < min_diff:
                            min_diff = diff
                            best_match = backup_file
                    except ValueError:
                        continue
                
                if best_match and min_diff is not None and min_diff < 3600:  # 1小时内
                    print(f"[INFO] {context}: 使用时间最接近的备份文件: {best_match}", file=sys.stderr)
                    return best_match
            except ValueError:
                pass
        
        # 如果无法匹配，使用最新的备份文件
        if backup_files:
            print(f"[INFO] {context}: 使用最新备份文件: {backup_files[0]}", file=sys.stderr)
            return backup_files[0]
        
        return None
    
    # 检查并恢复文件（传入所有运行记录，用于检测路径冲突）
    restored_success_path = try_restore_from_backup(success_full_tcl_path, success_run, "成功执行", run_history)
    if restored_success_path:
        success_full_tcl_path = restored_success_path
    elif not success_full_tcl_path.exists():
        print(f"[ERROR] 成功执行的 full.tcl 文件不存在，且未找到备份: {success_full_tcl_path}", file=sys.stderr)
        return 1
    
    restored_failed_path = try_restore_from_backup(failed_full_tcl_path, failed_run, "失败执行", run_history)
    if restored_failed_path:
        failed_full_tcl_path = restored_failed_path
    elif not failed_full_tcl_path.exists():
        print(f"[ERROR] 失败执行的 full.tcl 文件不存在，且未找到备份: {failed_full_tcl_path}", file=sys.stderr)
        return 1
    
    # 解析两个 full.tcl 文件
    try:
        print("[INFO] 正在解析配置...", file=sys.stderr)
        config1 = parse_full_tcl(success_full_tcl_path)
        config2 = parse_full_tcl(failed_full_tcl_path)
    except Exception as e:
        print(f"[ERROR] 解析配置失败: {e}", file=sys.stderr)
        return 1
    
    # 对比配置差异
    differences = compare_configs(config1, config2)
    
    # 显示差异
    display_config_diff(differences, success_run, failed_run)
    
    return 0
