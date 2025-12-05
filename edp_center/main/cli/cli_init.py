#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Init CLI - 初始化相关命令的 CLI

处理初始化工作空间、创建项目等操作。
"""

import sys

from .arg_parser_init import create_parser
from .command_router import find_edp_center_path, create_manager

# 初始化日志系统
from edp_center.packages.edp_common.logging_config import setup_logging
_logging_initialized = False


def main():
    """初始化相关命令的主入口"""
    # 初始化日志系统
    global _logging_initialized
    if not _logging_initialized:
        setup_logging()
        _logging_initialized = True
    
    # 创建参数解析器
    parser = create_parser()
    
    # 解析参数
    args = parser.parse_args()
    
    # 自动检测 edp_center 路径
    edp_center_path = find_edp_center_path(args)
    
    # 处理 -create_project 命令（不需要 WorkflowManager）
    if args.create_project:
        from .commands import handle_create_project
        return handle_create_project(edp_center_path, args)
    
    # 处理 -init 命令
    if args.init:
        # 创建 WorkflowManager
        manager = create_manager(edp_center_path)
        from .commands import handle_init_project
        return handle_init_project(manager, args)
    
    # 如果没有提供命令，显示帮助
    if not args.init and not args.create_project:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

