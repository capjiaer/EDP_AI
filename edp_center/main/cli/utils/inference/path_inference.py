#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径推断模块
提供工作路径信息推断功能（work_path, project, version, block, user, branch）
"""

from pathlib import Path
from typing import Optional, Dict

from ...init.params import find_edp_version_file


def infer_work_path_info(current_dir: Path, args, 
                         project_info: Optional[Dict] = None) -> Optional[Dict]:
    """
    推断工作路径信息（work_path, project, version, block, user, branch）
    
    逻辑：
    1. 向上查找 .edp_version 文件（必须找到，否则返回 None）
    2. 找到后，.edp_version 所在的目录就是 version
    3. version 的父目录就是 project_name
    4. version 的父目录的父目录就是 work_path
    5. 从当前目录到 version 之间的路径部分就是 block/user/branch
    
    注意：此函数严格要求找到 .edp_version 文件，如果找不到，返回 None。
    
    Args:
        current_dir: 当前工作目录
        args: 命令行参数对象
        project_info: 可选，项目信息字典（包含 edp_center_path, foundry, node, project）
        
    Returns:
        包含工作路径信息的字典，如果无法推断（找不到 .edp_version）则返回 None
        {
            'work_path': Path,
            'project': str,
            'version': str,
            'block': Optional[str],
            'user': Optional[str],
            'branch': Optional[str]
        }
    """
    # 1. 向上查找 .edp_version 文件（必须找到）
    version_file, version_info = find_edp_version_file(current_dir)
    if not version_file or not version_info:
        return None
    
    # 2. .edp_version 所在的目录就是 version
    version_dir = version_file.parent
    version = version_dir.name
    
    # 3. version 的父目录就是 project_name
    project_dir = version_dir.parent
    project = project_dir.name
    
    # 4. version 的父目录的父目录就是 work_path
    work_path = project_dir.parent
    
    # 5. 从当前目录到 version 之间的路径部分就是 block/user/branch
    try:
        rel_path = current_dir.relative_to(version_dir)
        parts = rel_path.parts
        
        # 路径结构：{block}/{user}/{branch}/...
        block = None
        user = None
        branch = None
        
        if len(parts) >= 1:
            block = parts[0]
        if len(parts) >= 2:
            user = parts[1]
        if len(parts) >= 3:
            branch = parts[2]
    except ValueError:
        # 如果当前目录不在 version 目录下，无法推断 block/user/branch
        block = None
        user = None
        branch = None
    
    # 命令行参数优先级更高（如果提供了的话）
    # 但是，如果 work_path 是默认值 '.'，应该使用推断出的 work_path
    args_work_path = getattr(args, 'work_path', None)
    if args_work_path and args_work_path != '.':
        work_path = Path(args_work_path).resolve()
    if getattr(args, 'project', None):
        project = args.project
    if getattr(args, 'version', None):
        version = args.version
    if getattr(args, 'block', None):
        block = args.block
    if getattr(args, 'user', None):
        user = args.user
    if getattr(args, 'branch', None):
        branch = args.branch
    
    # 验证必要信息
    if not (work_path and project and version):
        return None
    
    return {
        'work_path': Path(work_path).resolve(),
        'project': project,
        'version': version,
        'block': block,
        'user': user,
        'branch': branch
    }

