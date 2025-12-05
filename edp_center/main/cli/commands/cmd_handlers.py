#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI 命令处理函数（统一入口）
实际处理函数已拆分到独立模块
"""

from .info_handler import handle_info_cmd
from .run_handler import handle_run_cmd

__all__ = ['handle_info_cmd', 'handle_run_cmd']
