#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令补全辅助模块
提供动态补全功能，支持项目、flow、block 等自动补全
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# 尝试导入补全缓存模块
try:
    from .cache import (
        load_completion_cache, get_cached_completions,
        get_cache_file_path
    )
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


def find_edp_center_path(max_depth: int = 10) -> Optional[Path]:
    """
    从当前目录向上查找 edp_center 路径
    
    Args:
        max_depth: 最大查找深度（避免在深层目录中卡住）
    
    Returns:
        edp_center 路径，如果找不到则返回 None
    """
    current = Path.cwd()
    depth = 0
    while current != current.parent and depth < max_depth:
        potential_edp_center = current / 'edp_center'
        if potential_edp_center.exists() and (potential_edp_center / 'config').exists():
            return potential_edp_center
        current = current.parent
        depth += 1
    return None


def complete_projects(foundry: Optional[str] = None, 
                      node: Optional[str] = None) -> List[str]:
    """
    补全项目名称列表（仅从缓存读取）
    
    Args:
        foundry: 可选的 foundry 过滤
        node: 可选的 node 过滤
        
    Returns:
        项目名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(
                cache, 'projects',
                foundry=foundry, node=node
            )
    except Exception:
        pass
    
    return []


def complete_foundries() -> List[str]:
    """
    补全 foundry 列表（仅从缓存读取）
    
    Returns:
        foundry 名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(cache, 'foundries')
    except Exception:
        pass
    
    return []


def complete_nodes(foundry: Optional[str] = None) -> List[str]:
    """
    补全 node 列表（仅从缓存读取）
    
    Args:
        foundry: 可选的 foundry 过滤
        
    Returns:
        node 名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(
                cache, 'nodes',
                foundry=foundry
            )
    except Exception:
        pass
    
    return []


def complete_flows(project: Optional[str] = None,
                   foundry: Optional[str] = None,
                   node: Optional[str] = None) -> List[str]:
    """
    补全 flow 列表（仅从缓存读取）
    
    Args:
        project: 可选的项目名称
        foundry: 可选的 foundry
        node: 可选的 node
        
    Returns:
        flow 名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(
                cache, 'flows',
                project=project, foundry=foundry, node=node
            )
    except Exception:
        pass
    
    return []


def complete_flow_steps(flow: str,
                        project: Optional[str] = None,
                        foundry: Optional[str] = None,
                        node: Optional[str] = None) -> List[str]:
    """
    补全指定 flow 下的 step 列表（用于 -run flow.step 格式，仅从缓存读取）
    
    Args:
        flow: flow 名称
        project: 可选的项目名称
        foundry: 可选的 foundry
        node: 可选的 node
        
    Returns:
        step 名称列表（格式：flow.step）
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            # 从缓存中获取 flows
            flows = get_cached_completions(
                cache, 'flows',
                project=project, foundry=foundry, node=node
            )
            
            # 检查 flow 是否存在
            if flow not in flows:
                return []
            
            # 从缓存中获取 flow 的 steps（需要扩展缓存结构）
            # 暂时返回空列表，需要扩展缓存来支持 steps
            return []
    except Exception:
        pass
    
    return []


def complete_blocks(project: Optional[str] = None) -> List[str]:
    """
    补全 block 列表（仅从缓存读取）
    
    Args:
        project: 可选的项目名称
        
    Returns:
        block 名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(cache, 'blocks')
    except Exception:
        pass
    
    return []


def complete_users(block: Optional[str] = None) -> List[str]:
    """
    补全 user 列表（仅从缓存读取）
    
    Args:
        block: 可选的 block 名称
        
    Returns:
        user 名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(
                cache, 'users',
                block=block
            )
    except Exception:
        pass
    
    return []


def complete_branches() -> List[str]:
    """
    补全 branch 列表（从当前目录结构推断）
    
    Returns:
        branch 名称列表
    """
    try:
        current_dir = Path.cwd()
        
        # 尝试从 .edp_version 文件推断路径
        from ..init import find_edp_version_file
        version_file = find_edp_version_file(current_dir)
        
        if version_file:
            # 从 .edp_version 文件读取信息
            import yaml
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = yaml.safe_load(f) or {}
            
            # 注意：.edp_version 文件中的 'version' 键是项目版本名称（如 P85），
            # 'init_version' 键是初始化文件格式版本号（如 '1.0'）。
            # 优先从文件内容读取 version，如果没有则从目录名称推断
            work_path = version_info.get('work_path')
            project = version_info.get('project')
            version = version_info.get('version') or version_file.parent.name
            block = version_info.get('block')
            user = version_info.get('user')
            
            if all([work_path, project, version, block, user]):
                user_dir = Path(work_path) / project / version / block / user
                if user_dir.exists():
                    branches = []
                    for branch_dir in user_dir.iterdir():
                        if branch_dir.is_dir() and not branch_dir.name.startswith('.'):
                            branches.append(branch_dir.name)
                    return sorted(branches)
        
        return []
    except Exception:
        return []


def complete_versions(project: Optional[str] = None) -> List[str]:
    """
    补全 version 列表（仅从缓存读取）
    
    Args:
        project: 可选的项目名称
        
    Returns:
        version 名称列表
    """
    if not CACHE_AVAILABLE:
        return []
    
    try:
        cache = load_completion_cache()
        if cache:
            return get_cached_completions(cache, 'versions')
    except Exception:
        pass
    
    return []

