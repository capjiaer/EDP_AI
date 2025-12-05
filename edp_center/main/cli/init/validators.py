#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init 验证相关函数
用于验证 init 操作是否被允许
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


def validate_allowed_work_path(work_path: Path, 
                                init_config: Optional[Dict[str, Any]] = None,
                                config_yaml: Optional[Dict[str, Any]] = None,
                                edp_center_path: Optional[Path] = None) -> Tuple[bool, Optional[str]]:
    """
    验证 work_path 是否在允许的 init 路径列表中
    
    优先级：
    1. config.yaml 中的 allowed_work_paths（如果存在）
    2. init_project.yaml 中的 allowed_work_paths（如果存在）
    3. 如果都没有配置，则必须配置（不允许空配置）
    
    Args:
        work_path: 要验证的工作路径
        init_config: init_project.yaml 配置字典
        config_yaml: config.yaml 配置字典
        edp_center_path: edp_center 路径（用于解析相对路径）
        
    Returns:
        (is_allowed, error_message) 元组
        - is_allowed: 是否允许
        - error_message: 如果不允许，返回错误信息；如果允许，返回 None
    """
    work_path = Path(work_path).resolve()
    
    # 1. 优先检查 config.yaml 中的配置
    # 所有配置都在 project 下
    allowed_paths = None
    if config_yaml:
        project_config = config_yaml.get('project', {})
        if isinstance(project_config, dict):
            # 从 project 下读取 allowed_work_paths
            allowed_paths = project_config.get('allowed_work_paths')
    
    # 2. 如果 config.yaml 中没有，检查 init_project.yaml
    if allowed_paths is None and init_config:
        project_config = init_config.get('project', {})
        if isinstance(project_config, dict):
            allowed_paths = project_config.get('allowed_work_paths')
    
    # 3. 如果都没有配置或配置为空列表，则不限制（向后兼容）
    # 空列表或 None 表示允许任何路径
    if not allowed_paths or (isinstance(allowed_paths, list) and len(allowed_paths) == 0):
        return True, None  # 不限制，允许任何路径
    
    # 4. 验证配置格式
    if not isinstance(allowed_paths, list):
        return False, "allowed_work_paths 配置格式错误，必须是列表"
    
    # 解析允许的路径列表
    allowed_paths_resolved = []
    for allowed_path in allowed_paths:
        if not isinstance(allowed_path, str):
            continue
        
        # 处理 Unix 风格的路径（如 /c/... 在 Windows 上）
        # 如果是 Unix 风格的绝对路径，需要转换为 Windows 路径
        if allowed_path.startswith('/') and not allowed_path.startswith('//'):
            # Unix 风格路径，尝试转换
            # /c/Users/... -> C:/Users/...
            if len(allowed_path) > 2 and allowed_path[1].isalpha() and allowed_path[2] == '/':
                # /c/... 格式，转换为 C:/...
                drive_letter = allowed_path[1].upper()
                windows_path = f"{drive_letter}:{allowed_path[2:]}"
                allowed_paths_resolved.append(Path(windows_path).resolve())
            else:
                # 其他 Unix 路径，尝试直接解析
                allowed_paths_resolved.append(Path(allowed_path).resolve())
        elif Path(allowed_path).is_absolute():
            # Windows 绝对路径，直接使用
            allowed_paths_resolved.append(Path(allowed_path).resolve())
        else:
            # 相对路径，相对于 edp_center_path 的父目录
            if edp_center_path:
                allowed_paths_resolved.append((edp_center_path.parent / allowed_path).resolve())
            else:
                # 如果没有 edp_center_path，尝试相对于当前工作目录
                allowed_paths_resolved.append(Path(allowed_path).resolve())
    
    # 检查 work_path 是否匹配任何允许的路径
    # 统一转换为绝对路径并规范化
    work_path_resolved = work_path.resolve()
    for allowed_path in allowed_paths_resolved:
        allowed_path_resolved = allowed_path.resolve()
        try:
            # 检查 work_path 是否在 allowed_path 下（允许子目录）
            work_path_resolved.relative_to(allowed_path_resolved)
            return True, None
        except ValueError:
            # 检查是否完全匹配（使用规范化后的路径比较）
            if work_path_resolved == allowed_path_resolved:
                return True, None
    
    # 如果不匹配任何允许的路径，返回错误
    allowed_paths_str = ', '.join([str(p) for p in allowed_paths])
    allowed_paths_resolved_str = ', '.join([str(p.resolve()) for p in allowed_paths_resolved])
    return False, (
        f"工作路径 '{work_path_resolved}' 不在允许的 init 路径列表中\n"
        f"配置的路径: {allowed_paths_str}\n"
        f"解析后的路径: {allowed_paths_resolved_str}\n"
        f"请在 init_project.yaml 或 config.yaml 中配置 allowed_work_paths"
    )


def validate_init_permission(work_path: Path,
                             project: str,
                             foundry: Optional[str] = None,
                             node: Optional[str] = None,
                             manager=None,
                             config_yaml: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
    """
    验证是否允许执行 init 操作
    
    这是一个统一的验证入口，会检查：
    1. allowed_work_paths 配置
    
    Args:
        work_path: 工作路径
        project: 项目名称
        foundry: 代工厂名称（可选）
        node: 工艺节点（可选）
        manager: WorkflowManager 实例（可选，用于加载 init_project.yaml）
        config_yaml: config.yaml 配置字典（可选）
        
    Returns:
        (is_allowed, error_message) 元组
    """
    work_path = Path(work_path).resolve()
    
    # 加载 init_project.yaml 配置
    init_config = None
    edp_center_path = None
    
    if manager:
        try:
            # 获取项目信息
            if not foundry or not node:
                from edp_center.packages.edp_dirkit import ProjectFinder
                config_path = manager.edp_center / "config"
                project_finder = ProjectFinder(config_path)
                project_info = project_finder.get_project_info(project)
                foundry = project_info['foundry']
                node = project_info['node']
            
            # 加载 init_project.yaml
            init_config = manager.work_path_initializer.config_loader.load_init_project_config(foundry, node, project)
            edp_center_path = manager.edp_center
        except Exception:
            # 如果加载失败，继续使用其他配置
            pass
    
    # 验证 allowed_work_paths
    is_allowed, error_msg = validate_allowed_work_path(
        work_path, 
        init_config=init_config,
        config_yaml=config_yaml,
        edp_center_path=edp_center_path
    )
    
    if not is_allowed:
        return False, error_msg
    
    return True, None

