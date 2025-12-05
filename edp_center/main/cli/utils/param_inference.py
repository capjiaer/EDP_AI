#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
参数推断工具模块

提供统一的参数推断逻辑，减少代码重复。
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from argparse import Namespace

from ...workflow_manager import WorkflowManager
from ..init.params import infer_params_from_version_file


def create_default_args(work_path: Optional[Path] = None) -> Namespace:
    """
    创建默认参数对象
    
    Args:
        work_path: 工作路径（默认：当前目录）
    
    Returns:
        Namespace 对象，包含所有默认参数
    """
    args = Namespace()
    args.work_path = str(work_path) if work_path else str(Path.cwd())
    args.project = None
    args.foundry = None
    args.node = None
    args.version = None
    args.block = None
    args.user = None
    return args


def infer_all_params(manager: WorkflowManager, 
                     current_dir: Optional[Path] = None,
                     args: Optional[Namespace] = None) -> Dict[str, Any]:
    """
    推断所有项目参数（project, version, block, user, foundry, node）
    
    统一的参数推断逻辑，从 .edp_version 文件和项目配置中推断所有必要参数。
    
    Args:
        manager: WorkflowManager 实例
        current_dir: 当前工作目录（默认：Path.cwd()）
        args: 可选的参数对象（如果提供，会修改它；否则创建新的）
    
    Returns:
        包含所有推断参数的字典：
        {
            'project': str,
            'version': str,
            'block': str,
            'user': str,
            'foundry': str,
            'node': str,
            'work_path': Path
        }
    
    Raises:
        ValueError: 如果无法推断必要参数（project, foundry, node）
    
    Example:
        >>> manager = WorkflowManager('/path/to/edp_center')
        >>> params = infer_all_params(manager)
        >>> print(params['project'], params['foundry'], params['node'])
    """
    if current_dir is None:
        current_dir = Path.cwd()
    
    if args is None:
        args = create_default_args(current_dir)
    
    # 推断 work_path, project, version, block, user
    success = infer_params_from_version_file(args, manager, current_dir)
    if not success:
        raise ValueError("无法推断项目参数")
    
    project = args.project
    if not project:
        raise ValueError("无法推断 project 参数")
    
    # 推断 foundry 和 node
    foundry, node = get_foundry_node(manager, project, args.foundry, args.node)
    
    return {
        'project': project,
        'version': getattr(args, 'version', None),
        'block': args.block,
        'user': args.user,
        'foundry': foundry,
        'node': node,
        'work_path': Path(args.work_path)
    }


def get_foundry_node(manager: WorkflowManager, 
                     project: Optional[str] = None,
                     foundry: Optional[str] = None,
                     node: Optional[str] = None) -> Tuple[str, str]:
    """
    获取 foundry 和 node（从参数或推断）
    
    如果 foundry 和 node 都已提供，直接返回。
    否则，从项目配置中推断。
    
    Args:
        manager: WorkflowManager 实例
        project: 项目名称（如果 foundry/node 未提供，则必需）
        foundry: 代工厂名称（可选，如果提供则直接返回）
        node: 工艺节点（可选，如果提供则直接返回）
    
    Returns:
        (foundry, node) 元组
    
    Raises:
        ValueError: 如果无法获取 foundry 或 node
    
    Example:
        >>> manager = WorkflowManager('/path/to/edp_center')
        >>> foundry, node = get_foundry_node(manager, 'dongting')
        >>> print(foundry, node)
        'SAMSUNG' 'S8'
    """
    if foundry and node:
        return foundry, node
    
    if not project:
        raise ValueError("需要提供 project 参数以推断 foundry 和 node")
    
    try:
        project_info = manager.work_path_initializer.get_project_info(
            project, foundry, node
        )
    except Exception as e:
        raise ValueError(f"无法获取项目 {project} 的信息: {e}")
    
    inferred_foundry = project_info.get('foundry')
    inferred_node = project_info.get('node')
    
    # 使用推断的值或提供的值
    foundry = foundry or inferred_foundry
    node = node or inferred_node
    
    if not foundry or not node:
        raise ValueError(f"无法获取项目 {project} 的 foundry 和 node")
    
    return foundry, node


def prepare_execution_args(manager: WorkflowManager,
                          debug_mode: int = 0,
                          current_dir: Optional[Path] = None) -> Namespace:
    """
    准备执行参数（用于步骤执行）
    
    创建并推断执行步骤所需的所有参数。
    
    Args:
        manager: WorkflowManager 实例
        debug_mode: Debug 模式（0=正常, 1=debug）
        current_dir: 当前工作目录（默认：Path.cwd()）
    
    Returns:
        Namespace 对象，包含所有执行参数
    
    Raises:
        ValueError: 如果无法推断必要参数
    """
    if current_dir is None:
        current_dir = Path.cwd()
    
    args = create_default_args(current_dir)
    args.debug = debug_mode
    
    # 推断参数
    success = infer_params_from_version_file(args, manager, current_dir)
    if success:
        if args.project and not args.foundry:
            try:
                foundry, node = get_foundry_node(manager, args.project)
                args.foundry = foundry
                args.node = node
            except Exception:
                pass
    
    return args

