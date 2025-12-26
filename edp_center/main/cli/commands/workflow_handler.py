#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workflow Handler - 工作流处理模块

负责处理工作流加载和执行相关的 CLI 命令。
"""

from ...workflow_manager import WorkflowManager
from edp_center.packages.edp_common import handle_cli_error
from ..utils.param_inference import get_foundry_node


@handle_cli_error(error_message="加载工作流失败")
def handle_load_workflow(manager: WorkflowManager, args) -> int:
    """
    处理 load-workflow 命令（已废弃，保留函数用于内部调用）
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
    
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 获取 foundry 和 node（使用统一的参数获取逻辑）
    foundry, node = get_foundry_node(manager, args.project, args.foundry, args.node)
    
    graph = manager.load_workflow(foundry, node, args.project, args.flow)
    
    print("[OK] 工作流加载成功！")
    print(f"步骤数量: {len(graph.steps)}")
    print(f"步骤列表:")
    for step_name in sorted(graph.steps.keys()):
        step = graph.steps[step_name]
        print(f"  - {step_name}: {step.status}")
    
    if args.output:
        # 可以输出工作流信息到文件
        pass
    
    return 0


@handle_cli_error(error_message="工作流执行失败")
def handle_run_workflow(manager: WorkflowManager, args) -> int:
    """
    处理 run 子命令：执行完整工作流
    
    此函数用于执行完整的工作流（包括初始化、配置加载、脚本处理、工作流执行等）。
    与 handle_run_cmd 不同，此函数会实际执行工作流，而不是只生成 cmds 文件。
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    version = getattr(args, 'version', None)
    results = manager.run_full_workflow(
        work_path=args.work_path,
        project=args.project,
        version=version,
        block=args.block,
        user=args.user,
        branch=args.branch,
        flow=args.flow,
        foundry=args.foundry,
        node=args.node,
        from_branch_step=args.from_branch_step,
        prepend_default_sources=not args.no_prepend_sources
    )
    
    print("[OK] 工作流执行完成！")
    print(f"执行结果: {results}")
    
    return 0

