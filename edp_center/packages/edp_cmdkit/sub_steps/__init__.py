#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sub Steps Handler Module

处理从 dependency.yaml 读取 sub_steps 并生成 source 语句
"""

from .reader import read_sub_steps_from_dependency
from .hooks import get_sub_step_pre, get_sub_step_replace, get_sub_step_post
from .generator import (
    generate_step_hook_proc,
    generate_sub_step_pre_proc,
    generate_sub_step_post_proc,
    generate_sub_steps_sources,
    generate_sub_steps_calls
)
# 向后兼容：导出 proc_processor 的函数
from .proc_processor import (
    ensure_global_declarations_in_proc
)

__all__ = [
    'generate_step_hook_proc',
    'generate_sub_step_pre_proc',
    'generate_sub_step_post_proc',
    'read_sub_steps_from_dependency',
    'get_sub_step_pre',
    'get_sub_step_replace',
    'get_sub_step_post',
    'generate_sub_steps_sources',
    'generate_sub_steps_calls',
    'ensure_global_declarations_in_proc'
]

