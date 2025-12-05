#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl 生成器辅助模块
包含所有 full.tcl 生成相关的辅助函数
"""

from .config_file_loader import build_config_file_paths
from .tcl_type_handler import save_type_info, restore_type_info
from .tcl_expander import expand_variable_references
from .blocks_handler import handle_blocks_replacement
from .tcl_writer import write_array_variables, write_simple_variables

__all__ = [
    'build_config_file_paths',
    'save_type_info',
    'restore_type_info',
    'expand_variable_references',
    'handle_blocks_replacement',
    'write_array_variables',
    'write_simple_variables',
]

