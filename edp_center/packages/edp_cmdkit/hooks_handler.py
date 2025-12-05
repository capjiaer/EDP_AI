#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hooks 处理模块
提供处理 hooks 的基础功能

注意：
- Step hooks 的处理现在由 content_assembler.py::assemble_content_with_hooks() 负责
- 本模块只提供基础功能：检查 hooks 文件是否为空
- 采用"先整合后处理"策略：先整合所有内容（包括 hooks），然后统一处理 #import 指令
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def is_hook_file_empty(hook_content: str) -> bool:
    """
    检查 hooks 文件是否为空（只包含注释或空白行）
    
    Args:
        hook_content: hooks 文件内容
        
    Returns:
        如果文件为空（只包含注释或空白行），返回 True；否则返回 False
    """
    if not hook_content:
        return True
    
    # 移除所有空白行和注释行
    lines = hook_content.splitlines()
    for line in lines:
        stripped = line.strip()
        # 如果行不为空且不是注释，说明文件不为空
        if stripped and not stripped.startswith('#'):
            return False
    
    # 所有行都是空白或注释，文件为空
    return True



