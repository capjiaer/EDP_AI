#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dependency.yaml 解析器
负责解析 dependency.yaml 文件，提取 flow 和 step 信息
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .script_finders import find_source_script


def list_available_flows(edp_center_path: Path, foundry: str, node: str,
                        project: Optional[str]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    从 dependency.yaml 配置文件列出所有可用的 flow 和 step，并标注是否 ready
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        
    Returns:
        字典，key 为 flow_name，value 为字典 {step_name: {'ready': bool, 'cmd': str}}
    """
    flows = {}
    config_path = edp_center_path / 'config' / foundry / node
    
    # 搜索路径：项目特定和 common（按优先级从低到高）
    search_paths = []
    
    # 1. common 路径（优先级低）
    common_path = config_path / 'common'
    if common_path.exists():
        search_paths.append(common_path)
    
    # 2. 项目特定路径（优先级高，会覆盖 common）
    if project:
        project_path = config_path / project
        if project_path.exists():
            search_paths.append(project_path)
    
    # 遍历所有配置目录
    for config_dir in search_paths:
        if not config_dir.exists():
            continue
        
        # 遍历所有 flow 目录（每个 flow 目录下应该有 dependency.yaml）
        for flow_dir in config_dir.iterdir():
            if not flow_dir.is_dir() or flow_dir.name.startswith('.'):
                continue
            
            flow_name = flow_dir.name
            dependency_file = flow_dir / 'dependency.yaml'
            
            if not dependency_file.exists():
                continue
            
            # 读取 dependency.yaml 文件
            try:
                import yaml
                with open(dependency_file, 'r', encoding='utf-8') as f:
                    dependency_config = yaml.safe_load(f) or {}
                
                # 从 dependency.yaml 中提取 step 信息
                # dependency.yaml 格式：
                # {flow_name: {dependency: {FP_MODE: [{step_name: {...}}, ...]}}}
                # 只有包含 'cmd' 键的才被认为是有效的 step
                # 支持任意深度的嵌套结构
                # 同时检查源脚本文件是否存在，标注是否 ready
                steps_info = {}
                
                def extract_steps_recursive(data):
                    """递归提取所有包含 'cmd' 的 step，并检查源脚本是否存在"""
                    if isinstance(data, dict):
                        # 如果是字典，遍历每个 key-value
                        for key, value in data.items():
                            if isinstance(value, dict):
                                # 如果 value 包含 'cmd'，说明 key 是一个 step_name
                                if 'cmd' in value:
                                    cmd_filename = value['cmd']
                                    # 检查源脚本文件是否存在
                                    source_script = find_source_script(
                                        edp_center_path, foundry, node, project, flow_name, key
                                    )
                                    is_ready = source_script is not None
                                    steps_info[key] = {
                                        'ready': is_ready,
                                        'cmd': cmd_filename
                                    }
                                else:
                                    # 否则继续递归查找
                                    extract_steps_recursive(value)
                            elif isinstance(value, list):
                                # 如果 value 是列表，递归处理列表中的每个元素
                                extract_steps_recursive(value)
                            elif isinstance(value, str) and 'cmd' in data:
                                # 如果 value 是字符串，但当前字典包含 'cmd'，说明 key 是一个 step_name
                                cmd_filename = data['cmd']
                                source_script = find_source_script(
                                    edp_center_path, foundry, node, project, flow_name, key
                                )
                                is_ready = source_script is not None
                                steps_info[key] = {
                                    'ready': is_ready,
                                    'cmd': cmd_filename
                                }
                    elif isinstance(data, list):
                        # 如果是列表，递归处理每个元素
                        for item in data:
                            extract_steps_recursive(item)
                
                if flow_name in dependency_config:
                    flow_config = dependency_config[flow_name]
                    if 'dependency' in flow_config:
                        dependency = flow_config['dependency']
                        # 递归处理 dependency 结构（支持任意深度嵌套）
                        extract_steps_recursive(dependency)
                
                # 合并到 flows 字典中（项目特定的会覆盖 common）
                if steps_info:
                    # 如果 flow_name 已存在，合并 step（项目特定的会覆盖 common 的）
                    if flow_name in flows:
                        flows[flow_name].update(steps_info)
                    else:
                        flows[flow_name] = steps_info
                    
            except Exception as e:
                # 如果读取失败，跳过该文件
                continue
    
    return flows


def find_step_flow(edp_center_path: Path, foundry: str, node: str,
                   project: Optional[str], step_name: str) -> Optional[str]:
    """
    查找指定 step 属于哪个 flow
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        step_name: 步骤名称
        
    Returns:
        flow 名称，如果找不到则返回 None
    """
    config_path = edp_center_path / 'config' / foundry / node
    
    # 搜索路径：项目特定和 common（按优先级从低到高）
    search_paths = []
    
    # 1. common 路径（优先级低）
    common_path = config_path / 'common'
    if common_path.exists():
        search_paths.append(common_path)
    
    # 2. 项目特定路径（优先级高，会覆盖 common）
    if project:
        project_path = config_path / project
        if project_path.exists():
            search_paths.append(project_path)
    
    # 遍历所有配置目录
    for config_dir in search_paths:
        if not config_dir.exists():
            continue
        
        # 遍历所有 flow 目录（每个 flow 目录下应该有 dependency.yaml）
        for flow_dir in config_dir.iterdir():
            if not flow_dir.is_dir() or flow_dir.name.startswith('.'):
                continue
            
            flow_name = flow_dir.name
            dependency_file = flow_dir / 'dependency.yaml'
            
            if not dependency_file.exists():
                continue
            
            # 读取 dependency.yaml 文件
            try:
                import yaml
                with open(dependency_file, 'r', encoding='utf-8') as f:
                    dependency_config = yaml.safe_load(f) or {}
                
                if flow_name not in dependency_config:
                    continue
                
                flow_config = dependency_config[flow_name]
                if 'dependency' not in flow_config:
                    continue
                
                dependency = flow_config['dependency']
                
                # 递归查找 step_name
                def find_step_recursive(data):
                    """递归查找 step_name"""
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if key == step_name and isinstance(value, dict) and 'cmd' in value:
                                return True
                            # 继续递归查找
                            if find_step_recursive(value):
                                return True
                    elif isinstance(data, list):
                        for item in data:
                            if find_step_recursive(item):
                                return True
                    return False
                
                if find_step_recursive(dependency):
                    return flow_name
                    
            except Exception:
                continue
    
    return None


def get_cmd_filename_from_dependency(edp_center_path: Path, foundry: str, node: str,
                                     project: Optional[str], flow_name: str, step_name: str) -> Optional[str]:
    """
    从 dependency.yaml 中获取指定 step 的 cmd 文件名
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        step_name: 步骤名称
        
    Returns:
        cmd 文件名（如 calibre_dummy.tcl），如果找不到则返回 None
    """
    config_path = edp_center_path / 'config' / foundry / node
    
    # 搜索路径：项目特定和 common（按优先级从低到高）
    search_paths = []
    
    # 1. common 路径（优先级低）
    common_path = config_path / 'common' / flow_name / 'dependency.yaml'
    if common_path.exists():
        search_paths.append(common_path)
    
    # 2. 项目特定路径（优先级高）
    if project:
        project_path = config_path / project / flow_name / 'dependency.yaml'
        if project_path.exists():
            search_paths.append(project_path)
    
    # 从后往前搜索（项目特定的优先）
    for dependency_file in reversed(search_paths):
        try:
            import yaml
            with open(dependency_file, 'r', encoding='utf-8') as f:
                dependency_config = yaml.safe_load(f) or {}
            
            if flow_name not in dependency_config:
                continue
            
            flow_config = dependency_config[flow_name]
            if 'dependency' not in flow_config:
                continue
            
            dependency = flow_config['dependency']
            
            # 递归查找 step_name 对应的 cmd
            def find_cmd_recursive(data):
                """递归查找 step_name 对应的 cmd"""
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == step_name and isinstance(value, dict) and 'cmd' in value:
                            return value['cmd']
                        # 继续递归查找
                        result = find_cmd_recursive(value)
                        if result:
                            return result
                elif isinstance(data, list):
                    for item in data:
                        result = find_cmd_recursive(item)
                        if result:
                            return result
                return None
            
            cmd_filename = find_cmd_recursive(dependency)
            if cmd_filename:
                return cmd_filename
                
        except Exception:
            continue
    
    return None

