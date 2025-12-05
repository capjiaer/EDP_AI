#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化相关命令的参数解析器
负责定义 edp_init 命令的所有参数
"""

import argparse
import sys

# 尝试导入 argcomplete（可选依赖）
try:
    import argcomplete
    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False


def create_parser() -> argparse.ArgumentParser:
    """
    创建初始化相关命令的参数解析器
    
    Returns:
        ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog='edp_init',
        description='EDP Init - 初始化相关命令（设置项目、创建项目等）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 初始化项目到 user 级别（使用命令行参数）
  edp_init -init -prj dongting -v P85 --block block1 --user zhangsan
  
  # 如果存在 config.yaml，可以直接运行
  edp_init -init
  
  # 只指定 block，会初始化该 block 的所有 user（从 config.yaml 读取）
  edp_init -init --block block1
  
  # 指定 block 和 user，只初始化指定的（覆盖 config.yaml）
  edp_init -init --block block1 --user zhangsan
  
  # 使用图形界面初始化
  edp_init -init --gui
  
  # 创建新项目
  edp_init -create-project new_prj TSMC n8
        """
    )
    
    # 全局参数
    parser.add_argument(
        '--edp-center',
        type=str,
        default=None,
        help='EDP Center 资源库路径（默认：自动检测）'
    )
    
    # ==================== -init 选项 ====================
    parser.add_argument(
        '-init',
        action='store_true',
        help='初始化项目环境到 user 级别'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='使用图形界面进行初始化配置（仅用于 -init 选项）'
    )
    
    # ==================== -create_project 选项 ====================
    parser.add_argument(
        '-create_project', '--create-project',
        nargs=3,
        metavar=('PROJECT', 'FOUNDRY', 'NODE'),
        help='创建新项目的文件夹结构（格式: -create_project PROJECT_NAME FOUNDRY NODE，例如: -create_project new_prj TSMC n8）。如果目录已存在，只会创建缺失的目录和文件，不会覆盖已有内容。'
    )
    
    # 通用参数
    parser.add_argument('--work-path', default='.', help='WORK_PATH 根目录路径（默认：当前目录）')
    parser.add_argument('--config', '-config', '-cfg', help='指定配置文件路径（默认：work_path/config.yaml）')
    
    # 导入补全辅助函数
    from .completion import (
        complete_projects, complete_foundries, complete_nodes,
        complete_blocks, complete_users, complete_versions
    )
    
    # 为参数添加补全函数
    project_arg = parser.add_argument('--project', '-prj', help='项目名称（如 dongting），如果存在 config.yaml 则从中读取')
    version_arg = parser.add_argument('--version', '-v', help='项目版本名称（如 P85），如果存在 config.yaml 则从中读取', dest='version')
    block_arg = parser.add_argument('--block', '-blk', help='块名称（如 block1），如果存在 config.yaml 则从中读取')
    user_arg = parser.add_argument('--user', '-u', help='用户名（如 zhangsan），如果存在 config.yaml 则从中读取')
    foundry_arg = parser.add_argument('--foundry', help='代工厂名称（可选）')
    node_arg = parser.add_argument('--node', help='工艺节点（可选）')
    
    # 如果 argcomplete 可用，设置补全函数
    if ARGCOMPLETE_AVAILABLE:
        # 为项目参数添加补全
        def complete_project(prefix, parsed_args, **kwargs):
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            results = complete_projects(foundry=foundry, node=node)
            return [r for r in results if r.startswith(prefix)]
        
        project_arg.completer = complete_project
        
        # 为 foundry 参数添加补全
        def complete_foundry(prefix, parsed_args, **kwargs):
            results = complete_foundries()
            return [r for r in results if r.startswith(prefix)]
        
        foundry_arg.completer = complete_foundry
        
        # 为 node 参数添加补全（需要 foundry）
        def complete_node(prefix, parsed_args, **kwargs):
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            results = complete_nodes(foundry=foundry)
            return [r for r in results if r.startswith(prefix)]
        
        node_arg.completer = complete_node
        
        # 为 version 参数添加补全
        def complete_version(prefix, parsed_args, **kwargs):
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            results = complete_versions(project=project)
            return [r for r in results if r.startswith(prefix)]
        
        version_arg.completer = complete_version
        
        # 为 block 参数添加补全
        def complete_block(prefix, parsed_args, **kwargs):
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            results = complete_blocks(project=project)
            return [r for r in results if r.startswith(prefix)]
        
        block_arg.completer = complete_block
        
        # 为 user 参数添加补全（需要 block）
        def complete_user(prefix, parsed_args, **kwargs):
            block = getattr(parsed_args, 'block', None) if parsed_args else None
            results = complete_users(block=block)
            return [r for r in results if r.startswith(prefix)]
        
        user_arg.completer = complete_user
    
    return parser

