#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径构建模块
负责构建 full.tcl 文件的输出路径
"""

from pathlib import Path
from typing import Optional, Dict


def build_output_path(work_path_info: Optional[Dict], flow_name: str, step_name: str,
                     current_dir: Optional[Path] = None) -> Path:
    """
    构建 full.tcl 文件的输出路径
    
    Args:
        work_path_info: 工作路径信息字典（可选）
        flow_name: 流程名称
        step_name: 步骤名称
        current_dir: 当前目录（可选）
        
    Returns:
        full.tcl 文件路径
    """
    if work_path_info and work_path_info.get('work_path') and work_path_info.get('project') and \
       work_path_info.get('version') and work_path_info.get('block') and \
       work_path_info.get('user') and work_path_info.get('branch'):
        work_path = Path(work_path_info['work_path']).resolve()
        project = work_path_info['project']
        version = work_path_info.get('version')
        block = work_path_info['block']
        user = work_path_info['user']
        branch = work_path_info['branch']
        
        # 检查 work_path 是否已经包含了 project/version/block/user/branch
        work_path_parts = work_path.parts
        expected_parts = [project, version, block, user, branch]
        
        if len(work_path_parts) >= len(expected_parts):
            work_path_tail = work_path_parts[-len(expected_parts):]
            if list(work_path_tail) == expected_parts:
                # work_path 已经包含了完整路径，直接使用
                runs_dir = work_path / 'runs' / f"{flow_name}.{step_name}"
            else:
                # work_path 只是根目录，需要拼接完整路径
                runs_dir = work_path / project / version / block / user / branch / 'runs' / f"{flow_name}.{step_name}"
        else:
            # work_path 只是根目录，需要拼接完整路径
            runs_dir = work_path / project / version / block / user / branch / 'runs' / f"{flow_name}.{step_name}"
        
        runs_dir.mkdir(parents=True, exist_ok=True)
        return runs_dir / 'full.tcl'
    else:
        # 如果无法推断完整路径，使用当前目录
        if current_dir is None:
            current_dir = Path.cwd()
        runs_dir = current_dir / 'runs' / f"{flow_name}.{step_name}"
        runs_dir.mkdir(parents=True, exist_ok=True)
        return runs_dir / 'full.tcl'

