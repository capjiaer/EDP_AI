#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
补全配置缓存模块
生成和读取补全配置缓存，避免每次补全时都进行复杂的运算
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


# 补全配置缓存文件路径（在 edp_center 目录下）
CACHE_FILE_NAME = '.completion_cache.json'


def get_cache_file_path(edp_center_path: Optional[Path] = None) -> Path:
    """
    获取补全配置缓存文件路径
    
    Args:
        edp_center_path: edp_center 路径，如果为 None 则自动查找
        
    Returns:
        缓存文件路径
    """
    if edp_center_path is None:
        # 简单查找 edp_center 路径（不导入复杂模块）
        current = Path.cwd()
        depth = 0
        max_depth = 10
        while current != current.parent and depth < max_depth:
            potential_edp_center = current / 'edp_center'
            if potential_edp_center.exists() and (potential_edp_center / 'config').exists():
                edp_center_path = potential_edp_center
                break
            current = current.parent
            depth += 1
    
    if edp_center_path is None:
        # 如果找不到 edp_center，使用用户主目录
        return Path.home() / CACHE_FILE_NAME
    
    return edp_center_path / CACHE_FILE_NAME


def generate_completion_cache(edp_center_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    生成补全配置缓存
    
    Args:
        edp_center_path: edp_center 路径，如果为 None 则自动查找
        
    Returns:
        补全配置字典
    """
    from .helpers import (
        complete_projects, complete_foundries, complete_nodes,
        complete_flows, complete_blocks, complete_users, complete_versions
    )
    
    if edp_center_path is None:
        from .helpers import find_edp_center_path
        edp_center_path = find_edp_center_path()
    
    if edp_center_path is None:
        return {}
    
    cache = {
        'generated_at': datetime.now().isoformat(),
        'edp_center_path': str(edp_center_path),
        'projects': {},
        'foundries': [],
        'nodes': {},
        'flows': {},
        'blocks': {},
        'users': {},
        'versions': []
    }
    
    try:
        # 1. 获取所有 foundry
        cache['foundries'] = complete_foundries()
        
        # 2. 获取所有 foundry/node 组合
        for foundry in cache['foundries']:
            nodes = complete_nodes(foundry=foundry)
            cache['nodes'][foundry] = nodes
            
            # 3. 获取每个 foundry/node 下的项目
            for node in nodes:
                projects = complete_projects(foundry=foundry, node=node)
                cache['projects'][f"{foundry}/{node}"] = projects
                
                # 4. 获取每个项目的 flow
                for project in projects:
                    flows = complete_flows(project=project, foundry=foundry, node=node)
                    cache['flows'][f"{foundry}/{node}/{project}"] = flows
        
        # 5. 从当前目录的 config.yaml 读取 blocks 和 users（如果存在）
        try:
            current_dir = Path.cwd()
            config_file = current_dir / 'config.yaml'
            if config_file.exists():
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                project_config = config.get('project', {})
                if isinstance(project_config, dict):
                    blocks_config = project_config.get('blocks', {})
                    if isinstance(blocks_config, dict):
                        cache['blocks'] = list(blocks_config.keys())
                        
                        # 获取所有 users
                        users = set()
                        for block_users in blocks_config.values():
                            if isinstance(block_users, str):
                                users.update(block_users.split())
                            elif isinstance(block_users, list):
                                users.update(str(u) for u in block_users)
                        cache['users'] = sorted(users)
        except Exception:
            pass
        
        # 6. 获取所有 version
        cache['versions'] = complete_versions()
        
    except Exception as e:
        # 如果生成缓存失败，返回空字典
        print(f"警告: 生成补全缓存失败: {e}", file=sys.stderr)
        return {}
    
    return cache


def save_completion_cache(cache: Dict[str, Any], cache_file: Optional[Path] = None) -> bool:
    """
    保存补全配置缓存到文件
    
    Args:
        cache: 补全配置字典
        cache_file: 缓存文件路径，如果为 None 则自动确定
        
    Returns:
        是否保存成功
    """
    try:
        if cache_file is None:
            cache_file = get_cache_file_path()
        
        # 确保目录存在
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存到文件
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"错误: 保存补全缓存失败: {e}", file=sys.stderr)
        return False


def load_completion_cache(cache_file: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    从文件加载补全配置缓存
    
    Args:
        cache_file: 缓存文件路径，如果为 None 则自动确定
        
    Returns:
        补全配置字典，如果加载失败则返回 None
    """
    try:
        if cache_file is None:
            cache_file = get_cache_file_path()
        
        if not cache_file.exists():
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        return cache
    except Exception:
        return None


def get_cached_completions(cache: Dict[str, Any], 
                           completion_type: str,
                           **kwargs) -> List[str]:
    """
    从缓存中获取补全列表
    
    Args:
        cache: 补全配置缓存
        completion_type: 补全类型（'projects', 'foundries', 'nodes', 'flows', 'blocks', 'users', 'versions'）
        **kwargs: 过滤参数（foundry, node, project 等）
        
    Returns:
        补全列表
    """
    if not cache:
        return []
    
    try:
        if completion_type == 'foundries':
            return cache.get('foundries', [])
        
        elif completion_type == 'nodes':
            foundry = kwargs.get('foundry')
            if foundry:
                nodes = cache.get('nodes', {}).get(foundry, [])
                return nodes
            else:
                # 返回所有 foundry 下的所有 nodes
                all_nodes = set()
                for nodes in cache.get('nodes', {}).values():
                    all_nodes.update(nodes)
                return sorted(all_nodes)
        
        elif completion_type == 'projects':
            foundry = kwargs.get('foundry')
            node = kwargs.get('node')
            if foundry and node:
                key = f"{foundry}/{node}"
                return cache.get('projects', {}).get(key, [])
            else:
                # 返回所有项目
                all_projects = set()
                for projects in cache.get('projects', {}).values():
                    all_projects.update(projects)
                return sorted(all_projects)
        
        elif completion_type == 'flows':
            foundry = kwargs.get('foundry')
            node = kwargs.get('node')
            project = kwargs.get('project')
            if foundry and node and project:
                key = f"{foundry}/{node}/{project}"
                return cache.get('flows', {}).get(key, [])
            elif foundry and node:
                # 返回该 foundry/node 下所有项目的 flows
                all_flows = set()
                for key, flows in cache.get('flows', {}).items():
                    if key.startswith(f"{foundry}/{node}/"):
                        all_flows.update(flows)
                return sorted(all_flows)
            else:
                # 返回所有 flows
                all_flows = set()
                for flows in cache.get('flows', {}).values():
                    all_flows.update(flows)
                return sorted(all_flows)
        
        elif completion_type == 'blocks':
            return cache.get('blocks', [])
        
        elif completion_type == 'users':
            block = kwargs.get('block')
            if block:
                # 从 config.yaml 读取特定 block 的 users
                # 这里简化处理，返回所有 users
                return cache.get('users', [])
            else:
                return cache.get('users', [])
        
        elif completion_type == 'versions':
            return cache.get('versions', [])
        
    except Exception:
        pass
    
    return []


def update_completion_cache(edp_center_path: Optional[Path] = None) -> bool:
    """
    更新补全配置缓存
    
    Args:
        edp_center_path: edp_center 路径，如果为 None 则自动查找
        
    Returns:
        是否更新成功
    """
    cache = generate_completion_cache(edp_center_path)
    if not cache:
        return False
    
    return save_completion_cache(cache)


if __name__ == '__main__':
    # 命令行工具：生成补全缓存
    import argparse
    
    parser = argparse.ArgumentParser(description='生成 EDP 补全配置缓存')
    parser.add_argument('--edp-center', type=str, help='edp_center 路径')
    parser.add_argument('--output', type=str, help='输出文件路径（默认：edp_center/.completion_cache.json）')
    
    args = parser.parse_args()
    
    edp_center_path = Path(args.edp_center) if args.edp_center else None
    cache = generate_completion_cache(edp_center_path)
    
    if cache:
        cache_file = Path(args.output) if args.output else get_cache_file_path(edp_center_path)
        if save_completion_cache(cache, cache_file):
            print(f"✅ 补全缓存已生成: {cache_file}")
            print(f"   生成时间: {cache.get('generated_at', 'unknown')}")
        else:
            print("❌ 保存补全缓存失败", file=sys.stderr)
            sys.exit(1)
    else:
        print("❌ 生成补全缓存失败", file=sys.stderr)
        sys.exit(1)

