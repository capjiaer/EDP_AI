#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.run_info 扩展实现示例

展示如何扩展 update_run_info 函数来收集更多信息
"""

import sys
import yaml
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any


def update_run_info_extended(
    branch_dir: Path,
    flow_name: str,
    step_name: str,
    used_hooks: Dict,
    utils: List[str] = None,
    # 新增参数
    status: str = "success",  # success, failed, running, cancelled
    duration: Optional[float] = None,  # 执行时间（秒）
    lsf_job_id: Optional[str] = None,  # LSF 作业 ID
    resources: Optional[Dict[str, Any]] = None,  # 资源使用信息
    output_files: Optional[List[str]] = None,  # 输出文件列表
    error: Optional[str] = None,  # 错误信息
    validation: Optional[Dict[str, Any]] = None  # 验证结果
) -> None:
    """
    更新 .run_info 文件，记录扩展的运行信息
    
    Args:
        branch_dir: branch 目录路径
        flow_name: flow 名称
        step_name: step 名称
        used_hooks: 使用的 hooks 信息字典
        utils: 使用的 util 名称列表（可选）
        status: 执行状态
        duration: 执行时间（秒）
        lsf_job_id: LSF 作业 ID
        resources: 资源使用信息
        output_files: 输出文件列表
        error: 错误信息
        validation: 验证结果
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
            print(f"[WARN] 读取 .run_info 文件失败: {e}，将创建新文件", file=sys.stderr)
            run_history = []
    
    # 创建新的运行记录（扩展格式）
    new_run = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'flow': flow_name,
        'step': step_name,
        'utils': utils if utils is not None else [],
        'hooks': {
            'step': used_hooks.get('step', []),
            'utils': used_hooks.get('utils', {})
        },
        # 新增字段
        'status': status,
    }
    
    # 添加可选字段
    if duration is not None:
        new_run['duration'] = duration
    
    if lsf_job_id:
        new_run['lsf_job_id'] = lsf_job_id
    
    if resources:
        new_run['resources'] = resources
    
    if output_files:
        new_run['output_files'] = output_files
    
    if error:
        new_run['error'] = error
    
    if validation:
        new_run['validation'] = validation
    
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


def collect_lsf_resources(lsf_job_id: str) -> Optional[Dict[str, Any]]:
    """
    从 LSF 收集资源使用信息
    
    Args:
        lsf_job_id: LSF 作业 ID
        
    Returns:
        资源使用信息字典，如果收集失败返回 None
    """
    import subprocess
    
    try:
        # 使用 bhist 获取历史作业信息
        result = subprocess.run(
            f"bhist -l {lsf_job_id}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        # 解析输出（简化示例）
        resources = {
            'cpu_used': None,
            'peak_memory': None,
            'queue': None
        }
        
        # 这里需要解析 bhist 输出，提取资源信息
        # 实际实现会更复杂
        
        return resources
    except Exception as e:
        print(f"[WARN] 收集 LSF 资源信息失败: {e}", file=sys.stderr)
        return None


def collect_local_resources(process_pid: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    从本地进程收集资源使用信息
    
    Args:
        process_pid: 进程 PID（可选）
        
    Returns:
        资源使用信息字典，如果收集失败返回 None
    """
    try:
        import psutil
        
        if process_pid:
            process = psutil.Process(process_pid)
        else:
            # 使用当前进程
            process = psutil.Process()
        
        # 获取资源使用信息
        cpu_percent = process.cpu_percent(interval=1)
        memory_info = process.memory_info()
        
        resources = {
            'cpu_used': cpu_percent,
            'peak_memory': memory_info.rss / (1024 * 1024),  # MB
        }
        
        return resources
    except ImportError:
        print("[WARN] psutil 未安装，无法收集资源信息", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[WARN] 收集本地资源信息失败: {e}", file=sys.stderr)
        return None


def find_output_files(branch_dir: Path, flow_name: str, step_name: str) -> List[str]:
    """
    查找步骤的输出文件
    
    Args:
        branch_dir: branch 目录路径
        flow_name: flow 名称
        step_name: step 名称
        
    Returns:
        输出文件路径列表（相对于 branch_dir）
    """
    output_files = []
    
    # 查找 cmds 目录下的文件
    cmds_dir = branch_dir / 'cmds' / flow_name / step_name
    if cmds_dir.exists():
        for file in cmds_dir.rglob('*'):
            if file.is_file():
                rel_path = file.relative_to(branch_dir)
                output_files.append(str(rel_path))
    
    # 查找 logs 目录下的文件
    logs_dir = branch_dir / 'logs' / flow_name / step_name
    if logs_dir.exists():
        for file in logs_dir.rglob('*'):
            if file.is_file():
                rel_path = file.relative_to(branch_dir)
                output_files.append(str(rel_path))
    
    return output_files


# 使用示例
if __name__ == '__main__':
    # 示例：记录一次成功的执行
    branch_dir = Path('/path/to/branch')
    
    update_run_info_extended(
        branch_dir=branch_dir,
        flow_name='pv_calibre',
        step_name='ipmerge',
        used_hooks={'step': [], 'utils': {}},
        utils=['test'],
        status='success',
        duration=3600.5,
        lsf_job_id='12345',
        resources={
            'cpu_used': 16,
            'peak_memory': 32000,
            'queue': 'default'
        },
        output_files=[
            'cmds/pv_calibre/ipmerge/ipmerge.tcl',
            'logs/pv_calibre/ipmerge/ipmerge.log'
        ],
        validation={
            'passed': True,
            'files_checked': ['ipmerge.tcl', 'ipmerge.log']
        }
    )
    
    # 示例：记录一次失败的执行
    update_run_info_extended(
        branch_dir=branch_dir,
        flow_name='pnr_innovus',
        step_name='place',
        used_hooks={'step': ['step.pre'], 'utils': {}},
        utils=[],
        status='failed',
        duration=300.0,
        lsf_job_id='12346',
        resources={
            'cpu_used': 16,
            'peak_memory': 32000,
            'queue': 'default'
        },
        error='Placement failed: timing violation detected',
        validation={
            'passed': False,
            'error': 'Timing violation detected'
        }
    )

