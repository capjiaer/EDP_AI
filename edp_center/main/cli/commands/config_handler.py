#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Config Handler - 配置处理模块

负责处理配置加载相关的 CLI 命令。
"""

import yaml
from ...workflow_manager import WorkflowManager
from edp_center.packages.edp_common import handle_cli_error
from ..utils.param_inference import get_foundry_node


@handle_cli_error(error_message="加载配置失败")
def handle_load_config(manager: WorkflowManager, args) -> int:
    """
    处理 load-config 命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
    
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 获取 foundry 和 node（使用统一的参数获取逻辑）
    foundry, node = get_foundry_node(manager, args.project, args.foundry, args.node)
    
    config = manager.load_config(foundry, node, args.project, args.flow)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print(f"[OK] 配置已保存到: {args.output}")
    else:
        print("配置内容：")
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True))
    
    return 0

