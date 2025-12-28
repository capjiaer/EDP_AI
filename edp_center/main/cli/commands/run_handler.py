#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run 命令处理模块
处理 -run 选项：生成 cmds 文件并执行
"""

import sys
import logging

from .run_single_step import execute_single_step
from .run_range import handle_run_range
from edp_center.packages.edp_common.error_handler import handle_cli_error

# 获取 logger
logger = logging.getLogger(__name__)


@handle_cli_error(error_message="执行 run 命令失败")
def handle_run_cmd(manager, args) -> int:
    """
    处理 -run 选项：生成 cmds 文件并执行
    
    此函数用于处理 `-run` 选项（如 `edp -run pv_calibre.ipmerge`），
    它会生成 cmds 文件（包括 full.tcl），并执行工作流。
    
    支持以下模式：
    1. 单个步骤：`edp -run pv_calibre.ipmerge`
    2. 从某个步骤到另一个步骤：`edp -run --from pnr_innovus.place --to pv_calibre.drc`
    3. 从某个步骤开始：`edp -run --from pnr_innovus.place`
    4. 执行到某个步骤：`edp -run --to pv_calibre.drc`
    
    与 handle_run_workflow 不同：
    - handle_run_cmd: 支持 --from/--to 参数，可以执行多个步骤（用于 `-run` 选项）
    - handle_run_workflow: 执行完整工作流（用于 `run` 子命令）
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 检查是否使用了 --from 或 --to 参数
    run_from = getattr(args, 'run_from', None)
    run_to = getattr(args, 'run_to', None)
    single_step = getattr(args, 'run', None)
    
    # 如果使用了 --from 或 --to，需要执行多个步骤
    if run_from or run_to:
        return handle_run_range(manager, args, run_from, run_to, single_step)
    
    # 否则执行单个步骤（原有逻辑）
    if not single_step:
        print(f"[ERROR] 必须指定 --run、--from、--to 中的至少一个", file=sys.stderr)
        return 1
    
    # 执行单个步骤
    return execute_single_step(manager, args, single_step)



