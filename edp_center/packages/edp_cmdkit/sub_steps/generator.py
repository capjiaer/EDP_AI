#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sub Steps Generator - 主入口模块

协调各个子模块完成 sub_steps 的生成，提供统一的接口。
"""

from pathlib import Path
from typing import List, Optional

# 导入核心功能模块
from .source_generator import generate_sub_steps_sources
from .call_generator import generate_sub_steps_calls

# 向后兼容：导出 proc_processor 的函数（供其他模块使用）
from .proc_processor import (
    generate_step_hook_proc,
    generate_sub_step_pre_proc,
    generate_sub_step_post_proc,
    ensure_global_declarations_in_proc
)

# 重新导出核心函数（保持向后兼容）
__all__ = [
    'generate_sub_steps_sources',
    'generate_sub_steps_calls',
    'generate_step_hook_proc',
    'generate_sub_step_pre_proc',
    'generate_sub_step_post_proc',
    'ensure_global_declarations_in_proc'
]

