#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令分发模块
负责根据命令行参数分发到相应的处理函数
"""

import sys
from pathlib import Path

from ..workflow_manager import WorkflowManager
from .commands import (
    handle_init_project,
    handle_run_cmd, handle_info_cmd,
    handle_create_project
)
from .commands.graph_handler import handle_graph_cmd


def find_edp_center_path(args) -> Path:
    """
    查找 edp_center 路径
    
    Args:
        args: 命令行参数对象
        
    Returns:
        edp_center 路径
        
    Raises:
        SystemExit: 如果找不到 edp_center 路径
    """
    edp_center_path = args.edp_center
    if edp_center_path is None:
        # 尝试从当前目录向上查找 edp_center
        current = Path.cwd()
        while current != current.parent:
            potential_edp_center = current / 'edp_center'
            if potential_edp_center.exists() and (potential_edp_center / 'config').exists():
                edp_center_path = potential_edp_center
                break
            current = current.parent
        
        if edp_center_path is None:
            print("错误: 无法自动检测 edp_center 路径，请使用 --edp-center 参数指定", file=sys.stderr)
            sys.exit(1)
    
    return Path(edp_center_path).resolve()


def create_manager(edp_center_path: Path) -> WorkflowManager:
    """
    创建 WorkflowManager 实例
    
    Args:
        edp_center_path: edp_center 路径
        
    Returns:
        WorkflowManager 实例
        
    Raises:
        SystemExit: 如果创建失败
    """
    try:
        return WorkflowManager(edp_center_path)
    except Exception as e:
        print(f"错误: 无法初始化 WorkflowManager: {e}", file=sys.stderr)
        sys.exit(1)


def route_shortcut_commands(args) -> int:
    """
    处理快捷命令（-init, -branch, -run, -info, -create_project, -tutorial）
    
    Args:
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 检查是否提供了 -info 选项（即使参数为 None）
    # 当使用 nargs='?' 时，如果用户提供了 -info 但没有参数，args.info 会是 None
    # 我们需要检查命令行中是否包含 -info 或 -i
    has_info_flag = any(arg in ('-i', '-info', '--info') for arg in sys.argv)
    
    # 检查是否提供了 -create_project 选项
    has_create_project = getattr(args, 'create_project', None) is not None
    
    # 检查是否提供了 -tutorial 选项
    has_tutorial = getattr(args, 'tutorial', False)
    
    # 检查是否提供了 -release 选项
    has_release = getattr(args, 'release', False)
    
    # 检查是否提供了 -graph 选项
    has_graph = getattr(args, 'graph', False)
    
    # 检查信息查询相关选项（需要检查命令行参数，因为 nargs='?' 时 None 也可能表示提供了选项）
    has_history = any(arg in ('-history', '--history', '-hist') for arg in sys.argv)
    has_stats = any(arg in ('-stats', '--stats') for arg in sys.argv)
    has_rollback = any(arg in ('-rollback', '--rollback') for arg in sys.argv)
    has_validate = any(arg in ('-validate', '--validate', '-val') for arg in sys.argv)
    
    # 安全地检查各种命令选项
    has_init = getattr(args, 'init', False)
    has_branch = getattr(args, 'branch', False)
    has_run = getattr(args, 'run', False)
    
    if not (has_init or has_branch or has_run or has_info_flag or has_create_project or has_tutorial or has_release or has_graph or has_history or has_stats or has_rollback or has_validate):
        return None
    
    # 自动检测 edp_center 路径
    edp_center_path = find_edp_center_path(args)
    
    # 处理 -create_project 命令（不需要 WorkflowManager）
    if has_create_project:
        return handle_create_project(edp_center_path, args)
    
    # 处理 -tutorial 命令（不需要 WorkflowManager）
    if has_tutorial:
        try:
            from .commands.tutorial_handler import handle_tutorial_cmd
            return handle_tutorial_cmd(edp_center_path, args)
        except ImportError as e:
            print(f"错误: 无法导入教程处理器: {e}", file=sys.stderr)
            return 1
    
    # 创建 WorkflowManager
    manager = create_manager(edp_center_path)
    
    if has_init:
        return handle_init_project(manager, args)
    elif has_branch:
        # 创建一个临时的 args 对象来传递参数
        class BranchArgs:
            def __init__(self, args):
                self.work_path = getattr(args, 'work_path', None)
                self.project = getattr(args, 'project', None)
                self.version = getattr(args, 'version', None)
                self.block = getattr(args, 'block', None)
                self.user = getattr(args, 'user', None)
                self.branch = getattr(args, 'branch', None)
                self.foundry = getattr(args, 'foundry', None)
                self.node = getattr(args, 'node', None)
                self.from_branch_step = getattr(args, 'from_branch_step', None)
        
        branch_args = BranchArgs(args)
        from .commands import handle_create_branch
        return handle_create_branch(manager, branch_args)
    elif has_run:
        # 处理 -run 命令
        return handle_run_cmd(manager, args)
    elif has_release:
        # 处理 -release 命令
        from .commands.release import handle_release_cmd
        return handle_release_cmd(manager, args)
    elif has_graph:
        # 处理 -graph 命令
        # 创建一个临时的 args 对象来传递参数
        class GraphArgs:
            def __init__(self, args):
                self.project = args.project
                self.foundry = args.foundry
                self.node = args.node
                self.flow = getattr(args, 'flow', None)
                self.format = getattr(args, 'graph_format', 'text')
                self.output = getattr(args, 'graph_output', None)
                self.focus_step = getattr(args, 'graph_focus_step', None)
                self.depth = getattr(args, 'graph_depth', None)
                self.layout = getattr(args, 'graph_layout', 'dot')
                self.title = getattr(args, 'graph_title', None)
                self.open_browser = getattr(args, 'open_browser', False)
                # 添加 work_path 属性（推断函数需要）
                self.work_path = getattr(args, 'work_path', '.')
                self.version = getattr(args, 'version', None)
                self.block = getattr(args, 'block', None)
                self.user = getattr(args, 'user', None)
        
        graph_args = GraphArgs(args)
        return handle_graph_cmd(manager, graph_args)
    else:
        # 处理信息查询相关命令
        has_info_flag = any(arg in ('-i', '-info', '--info') for arg in sys.argv)
        if has_info_flag:
            return handle_info_cmd(manager, args)
        elif has_history:
            from .commands.history_handler import handle_history_cmd
            return handle_history_cmd(manager, args)
        elif has_stats:
            from .commands.stats_handler import handle_stats_cmd
            return handle_stats_cmd(manager, args)
        elif has_rollback:
            from .commands.rollback_handler import handle_rollback_cmd
            return handle_rollback_cmd(manager, args)
        elif has_validate:
            # TODO: 实现结果验证功能
            print("⚠️  结果验证功能正在开发中，敬请期待", file=sys.stderr)
            return 0
    
    return None


def route_subcommands(args) -> int:
    """
    处理子命令
    
    Args:
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    if not args.command:
        return None
    
    # 如果还有子命令，在这里处理
    print(f"错误: 未知命令: {args.command}", file=sys.stderr)
    return 1

