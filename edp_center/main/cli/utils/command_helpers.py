#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command Helpers - 命令处理辅助函数

提取命令处理函数中的公共逻辑，减少代码重复。
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

from .unified_inference import infer_project_info, infer_work_path_info


def get_current_dir() -> Path:
    """
    获取当前工作目录（公共函数）
    
    Returns:
        当前工作目录的 Path 对象
    """
    return Path.cwd().resolve()


def infer_and_validate_project_info(manager, current_dir: Path, args) -> Optional[Dict]:
    """
    推断并验证项目信息（公共函数）
    
    如果推断失败，会打印错误信息并返回 None。
    
    Args:
        manager: WorkflowManager 实例
        current_dir: 当前工作目录
        args: 命令行参数对象
        
    Returns:
        项目信息字典，如果推断失败则返回 None
    """
    project_info = infer_project_info(manager, current_dir, args)
    if not project_info:
        print(f"[ERROR] 无法推断项目信息，请确保在正确的工作目录下运行", file=sys.stderr)
        print(f"[INFO] 或者手动指定: --edp-center, --project, --foundry, --node", file=sys.stderr)
        return None
    return project_info


def infer_and_validate_work_path_info(current_dir: Path, args, project_info: Dict) -> Optional[Dict]:
    """
    推断并验证工作路径信息（公共函数）
    
    如果推断失败，会打印错误信息并返回 None。
    
    Args:
        current_dir: 当前工作目录
        args: 命令行参数对象
        project_info: 项目信息字典
        
    Returns:
        工作路径信息字典，如果推断失败则返回 None
    """
    work_path_info = infer_work_path_info(current_dir, args, project_info)
    if not work_path_info or not work_path_info.get('work_path') or \
       not work_path_info.get('project') or not work_path_info.get('version') or \
       not work_path_info.get('block') or not work_path_info.get('user') or \
       not work_path_info.get('branch'):
        print(f"[ERROR] 无法推断工作路径信息，请确保在正确的工作目录下运行", file=sys.stderr)
        print(f"[INFO] 或者手动指定: --work-path, --project, --version, --block, --user, --branch", file=sys.stderr)
        return None
    return work_path_info


def build_branch_dir(work_path_info: Dict) -> Path:
    """
    构建 branch 目录路径（公共函数）
    
    Args:
        work_path_info: 工作路径信息字典
        
    Returns:
        branch 目录的 Path 对象
    """
    work_path = Path(work_path_info['work_path']).resolve()
    project = work_path_info['project']
    version = work_path_info['version']
    block = work_path_info['block']
    user = work_path_info['user']
    branch = work_path_info['branch']
    return work_path / project / version / block / user / branch


def infer_all_info(manager, args) -> Tuple[Optional[Dict], Optional[Dict], Optional[Path]]:
    """
    推断所有信息（项目信息、工作路径信息、branch 目录）
    
    这是一个便捷函数，一次性完成所有推断和验证。
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
    Returns:
        (project_info, work_path_info, branch_dir) 元组
        如果任何推断失败，对应的值为 None
    """
    current_dir = get_current_dir()
    
    # 推断项目信息
    project_info = infer_and_validate_project_info(manager, current_dir, args)
    if not project_info:
        return None, None, None
    
    # 推断工作路径信息
    work_path_info = infer_and_validate_work_path_info(current_dir, args, project_info)
    if not work_path_info:
        return project_info, None, None
    
    # 构建 branch 目录
    branch_dir = build_branch_dir(work_path_info)
    
    return project_info, work_path_info, branch_dir

