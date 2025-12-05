#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目推断模块
提供项目信息推断功能（edp_center_path, foundry, node, project）
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List

from ...init.params import find_edp_version_file


def get_edp_center_path(edp_center_path: Path, args) -> Optional[Path]:
    """
    获取 edp_center 路径
    
    优先级：
    1. 命令行参数 --edp-center
    2. 从当前目录向上查找 edp_center 目录
    3. 使用初始化时提供的 edp_center_path
    
    Args:
        edp_center_path: 初始化时提供的 edp_center 路径
        args: 命令行参数对象
        
    Returns:
        edp_center 路径，如果找不到返回 None
    """
    # 1. 如果命令行提供了 edp-center，使用它
    if getattr(args, 'edp_center', None):
        edp_center_path = Path(args.edp_center).resolve()
        if edp_center_path.exists():
            return edp_center_path
        print(f"[WARN] 指定的 edp-center 路径不存在: {edp_center_path}", file=sys.stderr)
    
    # 2. 从当前目录向上查找 edp_center 目录
    current_dir = Path.cwd().resolve()
    search_dir = current_dir
    while search_dir != search_dir.parent:
        potential_edp_center = search_dir / 'edp_center'
        if potential_edp_center.exists() and (potential_edp_center / 'config').exists():
            return potential_edp_center.resolve()
        search_dir = search_dir.parent
    
    # 3. 使用初始化时提供的 edp_center_path
    if edp_center_path.exists():
        return edp_center_path
    
    return None


def list_projects_direct(config_path: Path, foundry: Optional[str] = None, 
                        node: Optional[str] = None) -> List[Dict[str, str]]:
    """
    直接扫描目录列出项目（当 ProjectFinder 不可用时使用）
    
    Args:
        config_path: config 目录路径
        foundry: 可选，过滤指定的 foundry
        node: 可选，过滤指定的 node
        
    Returns:
        项目信息列表，每个包含 foundry, node, project
    """
    projects = []
    
    if not config_path.exists():
        return projects
    
    # 遍历 config 目录
    for foundry_dir in config_path.iterdir():
        if not foundry_dir.is_dir() or foundry_dir.name.startswith('.'):
            continue
        
        if foundry and foundry_dir.name != foundry:
            continue
        
        for node_dir in foundry_dir.iterdir():
            if not node_dir.is_dir() or node_dir.name.startswith('.'):
                continue
            
            if node and node_dir.name != node:
                continue
            
            # 跳过 common 目录（common 是配置目录，不是 node）
            if node_dir.name == 'common':
                continue
            
            # 查找项目目录（排除 common）
            # node_dir 是 node 目录（如 S8），其下的子目录是项目目录（如 dongting）
            for item in node_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name != 'common':
                    projects.append({
                        'foundry': foundry_dir.name,
                        'node': node_dir.name,
                        'project': item.name
                    })
    
    return sorted(projects, key=lambda x: (x['foundry'], x['node'], x['project']))


def infer_project_info_from_version_file(current_dir: Path, args) -> Dict[str, Optional[str]]:
    """
    从 .edp_version 文件和命令行参数读取项目信息
    
    Args:
        current_dir: 当前工作目录
        args: 命令行参数对象
        
    Returns:
        包含 foundry, node, project 的字典
    """
    foundry = getattr(args, 'foundry', None)
    node = getattr(args, 'node', None)
    project = getattr(args, 'project', None)
    
    # 从 .edp_version 文件读取
    version_file, version_info = find_edp_version_file(current_dir)
    if version_file and version_info:
        if not foundry and 'foundry' in version_info:
            foundry = version_info['foundry']
        if not node and 'node' in version_info:
            node = version_info['node']
        if not project and 'project' in version_info:
            project = version_info['project']
    
    # 从命令行参数读取（优先级更高）
    if getattr(args, 'foundry', None):
        foundry = args.foundry
    if getattr(args, 'node', None):
        node = args.node
    if getattr(args, 'project', None):
        project = args.project
    
    return {
        'foundry': foundry,
        'node': node,
        'project': project
    }


def infer_project_info_from_path(current_dir: Path) -> Dict[str, Optional[str]]:
    """
    从路径结构推断 foundry 和 node
    
    Args:
        current_dir: 当前工作目录
        
    Returns:
        包含 foundry, node 的字典
    """
    foundry = None
    node = None
    
    # 尝试从路径推断（例如：.../SAMSUNG/S8/...）
    parts = current_dir.parts
    for i, part in enumerate(parts):
        # 常见的 foundry 名称（可以从 config 目录动态获取，但这里先硬编码）
        if part in ['SAMSUNG', 'TSMC', 'GF']:
            foundry = part
            if i + 1 < len(parts):
                node = parts[i + 1]
            break
    
    return {
        'foundry': foundry,
        'node': node
    }


def infer_project_info(edp_center_path: Path, config_path: Path, 
                      project_finder, current_dir: Path, args) -> Optional[Dict]:
    """
    推断项目信息（edp_center_path, foundry, node, project）
    
    逻辑：
    1. 获取 edp_center_path（从命令行参数或自动查找）
    2. 从 .edp_version 文件读取 foundry, node, project
    3. 从命令行参数读取 foundry, node, project
    4. 从路径结构推断 foundry, node（如果路径中包含 foundry 名称）
    5. 如果知道 project，从 edp_center/config 查找其所属的 foundry 和 node
    
    Args:
        edp_center_path: 初始化时提供的 edp_center 路径
        config_path: config 目录路径
        project_finder: ProjectFinder 实例（可能为 None）
        current_dir: 当前工作目录
        args: 命令行参数对象
        
    Returns:
        包含项目信息的字典，如果无法推断则返回 None
        {
            'edp_center_path': Path,
            'foundry': str,
            'node': str,
            'project': Optional[str]  # 可能为 None（使用 common）
        }
    """
    # 1. 获取 edp_center_path
    resolved_edp_center_path = get_edp_center_path(edp_center_path, args)
    if not resolved_edp_center_path:
        return None
    
    # 2-3. 从 .edp_version 文件和命令行参数读取
    info = infer_project_info_from_version_file(current_dir, args)
    foundry = info['foundry']
    node = info['node']
    project = info['project']
    
    # 4. 如果还是缺少信息，尝试从当前目录路径推断
    if not foundry or not node:
        path_info = infer_project_info_from_path(current_dir)
        if not foundry:
            foundry = path_info['foundry']
        if not node:
            node = path_info['node']
    
    # 5. 如果知道 project 但不知道 foundry/node，从 edp_center/config 查找
    if project and (not foundry or not node):
        project_info = None
        
        # 首先尝试使用 project_finder
        if project_finder:
            try:
                project_info = project_finder.get_project_info(project, foundry, node)
            except (ValueError, AttributeError):
                pass
        
        # 如果 project_finder 不可用或找不到，尝试直接扫描
        if not project_info:
            projects = list_projects_direct(config_path, foundry, node)
            for p in projects:
                if p['project'] == project:
                    project_info = p
                    break
        
        if project_info:
            if not foundry:
                foundry = project_info['foundry']
            if not node:
                node = project_info['node']
    
    # 验证必要信息
    if not foundry or not node:
        return None
    
    return {
        'edp_center_path': resolved_edp_center_path,
        'foundry': foundry,
        'node': node,
        'project': project  # 可能为 None（使用 common）
    }

