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
    
    # 处理 -history 命令（新增，待实现）
    if args.history is not None:
        # TODO: 实现历史查询功能
        print("⚠️  历史查询功能正在开发中，敬请期待", file=sys.stderr)
        print("   提示: 可以查看 .run_info 文件获取运行历史", file=sys.stderr)
        return 0
    
    # 处理 -stats 命令（新增，待实现）
    if args.stats is not None:
        # TODO: 实现性能分析功能
        print("⚠️  性能分析功能正在开发中，敬请期待", file=sys.stderr)
        return 0
    
    # 处理 -rollback 命令（新增，待实现）
    if args.rollback is not None:
        # TODO: 实现回滚功能
        print("⚠️  回滚功能正在开发中，敬请期待", file=sys.stderr)
        return 0
    
    # 处理 -validate 命令（新增，待实现）
    if args.validate is not None:
        # TODO: 实现结果验证功能
        print("⚠️  结果验证功能正在开发中，敬请期待", file=sys.stderr)
        return 0
    
    # 如果没有提供命令，显示帮助
    if not (has_info_flag or args.tutorial or 
            args.history is not None or args.stats is not None or 
            args.rollback is not None or args.validate is not None):
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

