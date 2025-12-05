#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工作流 Web 应用
提供 Web 界面用于工作流可视化和管理
"""

from .server import WorkflowWebServer, run_workflow_web

__all__ = ['WorkflowWebServer', 'run_workflow_web']

