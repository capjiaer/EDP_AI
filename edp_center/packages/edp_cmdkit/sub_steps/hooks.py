#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sub Steps Hooks - Hooks 处理模块
"""

from pathlib import Path
from typing import Optional
import logging
from ..hooks_handler import is_hook_file_empty

logger = logging.getLogger(__name__)


def get_sub_step_pre(file_name: str, proc_name: str, hooks_dir: Optional[Path]) -> Optional[str]:
    """
    获取 sub_step.pre hook 内容
    
    sub_step.pre 用于在 sub_step 之前插入临时逻辑
    
    查找优先级（从高到低）：
    1. {file_name}.pre（如 config_design.tcl.pre）- 推荐，最直观
    2. {file_stem}.pre（如 config_design.pre）- 去掉 .tcl 扩展名
    
    Args:
        file_name: sub_step 文件名（如 config_design.tcl）
        proc_name: sub_step proc 名称（如 pnr_innovus::config_design，仅用于日志）
        hooks_dir: hooks 目录路径
    
    Returns:
        sub_step.pre 内容，如果不存在返回 None
    """
    if not hooks_dir:
        return None
    
    hooks_dir_path = Path(hooks_dir)
    if not hooks_dir_path.exists():
        return None
    
    # 优先级 1：基于完整文件名（推荐，最直观）
    pre_file = hooks_dir_path / f"{file_name}.pre"
    
    # 优先级 2：基于文件名（去掉扩展名）
    if not pre_file.exists():
        file_stem = file_name.replace('.tcl', '').replace('.TCL', '')
        pre_file = hooks_dir_path / f"{file_stem}.pre"
    
    if pre_file.exists():
        pre_content = pre_file.read_text(encoding='utf-8')
        if not is_hook_file_empty(pre_content):
            logger.info(f"找到 sub_step.pre hook: {pre_file}")
            return pre_content
    
    return None


def get_sub_step_replace(file_name: str, proc_name: str, hooks_dir: Optional[Path]) -> Optional[str]:
    """
    获取 sub_step.replace hook 内容
    
    sub_step.replace 用于完全重写 sub_step proc：包含完整的 proc 定义
    
    查找优先级（从高到低）：
    1. {file_name}.replace（如 config_design.tcl.replace）- 推荐，最直观
    2. {file_stem}.replace（如 config_design.replace）- 去掉 .tcl 扩展名
    
    Args:
        file_name: sub_step 文件名（如 config_design.tcl）
        proc_name: sub_step proc 名称（如 pnr_innovus::config_design，仅用于日志）
        hooks_dir: hooks 目录路径
    
    Returns:
        sub_step.replace 内容，如果不存在返回 None
    """
    if not hooks_dir:
        return None
    
    hooks_dir_path = Path(hooks_dir)
    if not hooks_dir_path.exists():
        return None
    
    # 优先级 1：基于完整文件名（推荐，最直观）
    replace_file = hooks_dir_path / f"{file_name}.replace"
    
    # 优先级 2：基于文件名（去掉扩展名）
    if not replace_file.exists():
        file_stem = file_name.replace('.tcl', '').replace('.TCL', '')
        replace_file = hooks_dir_path / f"{file_stem}.replace"
    
    if replace_file.exists():
        replace_content = replace_file.read_text(encoding='utf-8')
        if not is_hook_file_empty(replace_content):
            logger.info(f"找到 sub_step.replace hook: {replace_file}")
            return replace_content
    
    return None


def get_sub_step_post(file_name: str, proc_name: str, hooks_dir: Optional[Path]) -> Optional[str]:
    """
    获取 sub_step.post hook 内容
    
    sub_step.post 用于在 sub_step 之后插入临时逻辑
    
    查找优先级（从高到低）：
    1. {file_name}.post（如 config_design.tcl.post）- 推荐，最直观
    2. {file_stem}.post（如 config_design.post）- 去掉 .tcl 扩展名
    
    Args:
        file_name: sub_step 文件名（如 config_design.tcl）
        proc_name: sub_step proc 名称（如 pnr_innovus::config_design，仅用于日志）
        hooks_dir: hooks 目录路径
    
    Returns:
        sub_step.post 内容，如果不存在返回 None
    """
    if not hooks_dir:
        return None
    
    hooks_dir_path = Path(hooks_dir)
    if not hooks_dir_path.exists():
        return None
    
    # 优先级 1：基于完整文件名（推荐，最直观）
    post_file = hooks_dir_path / f"{file_name}.post"
    
    # 优先级 2：基于文件名（去掉扩展名）
    if not post_file.exists():
        file_stem = file_name.replace('.tcl', '').replace('.TCL', '')
        post_file = hooks_dir_path / f"{file_stem}.post"
    
    if post_file.exists():
        post_content = post_file.read_text(encoding='utf-8')
        if not is_hook_file_empty(post_content):
            logger.info(f"找到 sub_step.post hook: {post_file}")
            return post_content
    
    return None
