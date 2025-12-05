#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script Handler - 脚本处理模块

负责处理脚本处理相关的 CLI 命令。
"""

from ...workflow_manager import WorkflowManager
from edp_center.packages.edp_common import handle_cli_error


@handle_cli_error(error_message="处理脚本失败")
def handle_process_script(manager: WorkflowManager, args) -> int:
    """
    处理 process-script 命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
    
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    content = manager.process_script(
        input_file=args.input,
        output_file=args.output,
        search_paths=args.search_paths,
        prepend_default_sources=not args.no_prepend_sources
    )
    
    if args.output:
        print(f"[OK] 脚本已处理并保存到: {args.output}")
    else:
        print("处理后的脚本内容：")
        print(content)
    
    return 0

