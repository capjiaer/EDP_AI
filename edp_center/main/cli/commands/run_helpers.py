#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run 命令辅助函数模块
包含 run 命令处理过程中使用的辅助函数
"""

import sys
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


# 注意：已移除 #import util 机制，不再需要扫描 util


def get_used_hooks(hooks_dir: Path, step_name: str) -> Dict[str, List[str]]:
    """
    获取实际使用的 hooks 文件列表（非空的 hooks 文件）
    
    Args:
        hooks_dir: hooks 目录路径
        step_name: 步骤名称
        
    Returns:
        包含使用的 hooks 信息的字典
    """
    used_hooks = {
        'step': []
    }
    
    if not hooks_dir.exists():
        return used_hooks
    
    # 导入 is_hook_file_empty 函数（从 cmd_processor 模块）
    from edp_center.packages.edp_cmdkit.hooks_handler import is_hook_file_empty
    
    # 检查 step.pre 和 step.post
    step_pre_file = hooks_dir / 'step.pre'
    if step_pre_file.exists():
        step_pre_content = step_pre_file.read_text(encoding='utf-8')
        if not is_hook_file_empty(step_pre_content):
            used_hooks['step'].append('step.pre')
    
    step_post_file = hooks_dir / 'step.post'
    if step_post_file.exists():
        step_post_content = step_post_file.read_text(encoding='utf-8')
        if not is_hook_file_empty(step_post_content):
            used_hooks['step'].append('step.post')
    
    return used_hooks


def update_run_info(branch_dir: Path, flow_name: str, step_name: str, used_hooks: Dict, step=None, full_tcl_path: Optional[Path] = None) -> None:
    """
    更新 .run_info 文件，记录运行信息
    
    Args:
        branch_dir: branch 目录路径
        flow_name: flow 名称
        step_name: step 名称
        used_hooks: 使用的 hooks 信息字典
        utils: 使用的 util 名称列表（可选）
        step: 步骤对象（可选），用于获取执行信息（execution_info）
        full_tcl_path: full.tcl 文件路径（可选），用于记录配置信息
    """
    run_info_file = branch_dir / '.run_info'
    
    # 读取现有的 run_info（如果存在）
    run_history = []
    if run_info_file.exists():
        try:
            with open(run_info_file, 'r', encoding='utf-8') as f:
                existing_data = yaml.safe_load(f) or {}
                run_history = existing_data.get('runs', [])
        except Exception as e:
            # 如果读取失败，从空列表开始
            print(f"[WARN] 读取 .run_info 文件失败: {e}，将创建新文件", file=sys.stderr)
            run_history = []
    
    # 创建新的运行记录
    new_run = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'flow': flow_name,
        'step': step_name,
        'hooks': {
            'step': used_hooks.get('step', [])
        }
    }
    
    # 如果提供了 step 对象且有 execution_info，添加扩展字段
    if step and hasattr(step, 'execution_info'):
        exec_info = step.execution_info
        
        # 执行状态
        if exec_info.get('success') is not None:
            new_run['status'] = 'success' if exec_info.get('success') else 'failed'
        
        # 执行时长
        if exec_info.get('duration') is not None:
            new_run['duration'] = round(exec_info.get('duration'), 2)
        
        # LSF Job ID
        if exec_info.get('job_id'):
            new_run['lsf_job_id'] = exec_info.get('job_id')
        
        # 资源使用信息
        resources = exec_info.get('resources')
        if resources:
            resource_dict = {}
            
            # CPU 使用情况
            if resources.get('cpu_used') is not None:
                resource_dict['cpu_used'] = resources.get('cpu_used')
            
            # 每个 CPU 的使用时间
            if resources.get('cpu_time_per_cpu') is not None:
                resource_dict['cpu_time_per_cpu'] = round(resources.get('cpu_time_per_cpu'), 2)
            
            # 峰值内存
            if resources.get('peak_memory') is not None:
                resource_dict['peak_memory'] = resources.get('peak_memory')  # MB
            
            # 使用的机器列表（包含每个主机的 CPU 数量）
            if resources.get('hosts'):
                # hosts 现在是一个字典列表，格式: [{'host': 'host1', 'cpus': 4}, ...]
                resource_dict['hosts'] = resources.get('hosts')
            
            # 队列信息
            if resources.get('queue'):
                resource_dict['queue'] = resources.get('queue')
            
            # 开始和结束时间
            if resources.get('start_time'):
                resource_dict['start_time'] = resources.get('start_time')
            if resources.get('end_time'):
                resource_dict['end_time'] = resources.get('end_time')
            
            if resource_dict:
                new_run['resources'] = resource_dict
        
        # 错误信息
        if exec_info.get('error'):
            new_run['error'] = exec_info.get('error')
    
    # 记录 full.tcl 路径（相对于 branch_dir）
    if full_tcl_path:
        try:
            # 将 full_tcl_path 转换为相对于 branch_dir 的路径
            full_tcl_path_resolved = Path(full_tcl_path).resolve()
            branch_dir_resolved = branch_dir.resolve()
            try:
                relative_path = full_tcl_path_resolved.relative_to(branch_dir_resolved)
                new_run['full_tcl_path'] = str(relative_path).replace('\\', '/')  # 统一使用正斜杠
            except ValueError:
                # 如果无法转换为相对路径，使用绝对路径
                new_run['full_tcl_path'] = str(full_tcl_path_resolved)
        except Exception as e:
            # 如果路径处理失败，记录警告但继续
            print(f"[WARN] 无法处理 full.tcl 路径: {e}", file=sys.stderr)
    
    # 追加到历史记录
    run_history.append(new_run)
    
    # 构建完整的 run_info 数据结构
    run_info_data = {
        'runs': run_history
    }
    
    # 写入文件
    try:
        with open(run_info_file, 'w', encoding='utf-8') as f:
            yaml.dump(run_info_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"[INFO] 已更新运行记录: {run_info_file}", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] 写入 .run_info 文件失败: {e}", file=sys.stderr)


def create_hooks_files(hooks_dir: Path, step_name: str) -> None:
    """
    创建缺失的 hooks 文件
    
    如果 hooks 目录不存在，会创建目录；如果文件缺失，会重新创建。
    这样可以自动恢复被删除的 hooks 文件。
    
    Args:
        hooks_dir: hooks 目录路径（如 hooks/pv_calibre/ipmerge）
        step_name: 步骤名称（如 ipmerge）
    """
    # 创建 hooks 目录（如果不存在）
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # 记录是否有文件被创建（用于输出信息）
    files_created = []
    
    # 创建 step.pre 和 step.post
    step_pre_file = hooks_dir / 'step.pre'
    step_post_file = hooks_dir / 'step.post'
    
    if not step_pre_file.exists():
        step_pre_file.write_text(
            f"# Step pre hook - executed at the beginning of {step_name} step\n"
            f"# Add code here that needs to be executed before the step starts\n",
            encoding='utf-8'
        )
        files_created.append('step.pre')
    
    if not step_post_file.exists():
        step_post_file.write_text(
            f"# Step post hook - executed at the end of {step_name} step\n"
            f"# Add code here that needs to be executed after the step ends\n",
            encoding='utf-8'
        )
        files_created.append('step.post')
    
    # 如果有文件被创建，输出信息
    if files_created:
        print(f"[INFO] 已自动创建缺失的 hooks 文件: {', '.join(files_created)}", file=sys.stderr)

