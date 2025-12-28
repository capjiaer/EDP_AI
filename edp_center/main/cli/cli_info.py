#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Info CLI - 信息查询相关命令的 CLI

处理查看信息、历史查询、性能分析、结果验证等操作。
"""

import sys

from .arg_parser_info import create_parser
from .command_router import find_edp_center_path, create_manager

# 初始化日志系统
from edp_center.packages.edp_common.logging_config import setup_logging
_logging_initialized = False


def main():
    """信息查询相关命令的主入口"""
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
    
    # 处理 -tutorial 命令（不需要 WorkflowManager）
    if args.tutorial:
        try:
            from .commands.tutorial_handler import handle_tutorial_cmd
            return handle_tutorial_cmd(edp_center_path, args)
        except ImportError as e:
            print(f"错误: 无法导入教程处理器: {e}", file=sys.stderr)
            return 1
    
    # 处理 -info 命令
    has_info_flag = any(arg in ('-i', '-info', '--info') for arg in sys.argv)
    if has_info_flag:
        manager = create_manager(edp_center_path)
        from .commands import handle_info_cmd
        return handle_info_cmd(manager, args)
    
    # 处理 -history 命令
    # 需要检查命令行参数，因为 nargs='?' 时 None 也可能表示提供了选项
    has_history = any(arg in ('-history', '--history', '-hist') for arg in sys.argv)
    if has_history:
        manager = create_manager(edp_center_path)
        try:
            from .commands.history_handler import handle_history_cmd
            return handle_history_cmd(manager, args)
        except ImportError as e:
            print(f"错误: 无法导入历史查询处理器: {e}", file=sys.stderr)
            return 1
    
    # 处理 -stats 命令
    # 需要检查命令行参数，因为 nargs='?' 时 None 也可能表示提供了选项
    has_stats = any(arg in ('-stats', '--stats') for arg in sys.argv)
    if has_stats:
        manager = create_manager(edp_center_path)
        try:
            from .commands.stats_handler import handle_stats_cmd
            return handle_stats_cmd(manager, args)
        except ImportError as e:
            print(f"错误: 无法导入性能分析处理器: {e}", file=sys.stderr)
            return 1
    
    # 处理 -rollback 命令
    # 需要检查命令行参数，因为 nargs='?' 时 None 也可能表示提供了选项
    has_rollback = any(arg in ('-rollback', '--rollback') for arg in sys.argv)
    if has_rollback:
        manager = create_manager(edp_center_path)
        try:
            from .commands.rollback_handler import handle_rollback_cmd
            return handle_rollback_cmd(manager, args)
        except ImportError as e:
            print(f"错误: 无法导入回滚处理器: {e}", file=sys.stderr)
            return 1
    
    # 处理 -validate 命令（待实现）
    # 需要检查命令行参数，因为 nargs='?' 时 None 也可能表示提供了选项
    has_validate = any(arg in ('-validate', '--validate', '-val') for arg in sys.argv)
    if has_validate:
        # TODO: 实现结果验证功能
        print("⚠️  结果验证功能正在开发中，敬请期待", file=sys.stderr)
        return 0
    
    # 如果没有提供命令，显示帮助
    
    if not (has_info_flag or args.tutorial or has_history or has_stats or 
            has_rollback or has_validate):
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

