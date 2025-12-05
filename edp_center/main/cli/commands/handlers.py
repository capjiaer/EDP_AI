#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI 命令处理函数

主入口模块，导出所有命令处理函数。
"""

# 从各个子模块导入函数
from .config_handler import handle_load_config
from .script_handler import handle_process_script
from .workflow_handler import handle_load_workflow, handle_run_workflow

# 向后兼容：导出所有函数
__all__ = [
    'handle_load_config',
    'handle_process_script',
    'handle_load_workflow',
    'handle_run_workflow'
]

