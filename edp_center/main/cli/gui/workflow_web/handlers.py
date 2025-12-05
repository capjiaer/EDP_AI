#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工作流 Web 服务器业务逻辑处理

主入口模块，协调各个子模块完成工作流 Web 功能。
"""

from typing import Dict

from ....workflow_manager import WorkflowManager
from .workflow_loader import load_workflow_data
from .step_executor import execute_step

# 向后兼容：导出所有函数
__all__ = ['load_workflow_data', 'execute_step']

