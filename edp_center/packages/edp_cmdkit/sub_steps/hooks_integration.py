#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hooks Integration - Hooks 集成模块

负责收集和处理 sub_step hooks（pre/post/replace），并生成相应的 proc 定义。
"""

from pathlib import Path
from typing import Dict, Optional, List
import logging

from .hooks import get_sub_step_pre, get_sub_step_replace, get_sub_step_post
from .proc_processor import generate_sub_step_pre_proc, generate_sub_step_post_proc

logger = logging.getLogger(__name__)


def collect_sub_step_hooks(sub_steps: List[dict], hooks_dir: Optional[Path], flow_name: str) -> Dict[str, Dict[str, str]]:
    """
    收集所有 sub_step 的 hooks（pre/post/replace）
    
    Args:
        sub_steps: sub_steps 列表，格式为 [{file_name: proc_name}, ...]
        hooks_dir: hooks 目录路径
        flow_name: 流程名称
    
    Returns:
        字典，格式为 {
            'replace': {proc_name: replace_content},
            'pre': {proc_name: pre_content},
            'post': {proc_name: post_content}
        }
    """
    replace_hooks = {}
    pre_hooks = {}
    post_hooks = {}
    
    if not hooks_dir:
        return {'replace': replace_hooks, 'pre': pre_hooks, 'post': post_hooks}
    
    for sub_step in sub_steps:
        if not isinstance(sub_step, dict) or len(sub_step) != 1:
            continue
        
        file_name, proc_name = next(iter(sub_step.items()))
        # 确保文件名有 .tcl 扩展名
        if not file_name.endswith('.tcl'):
            file_name = file_name + '.tcl'
        
        # 收集 replace hook
        replace_content = get_sub_step_replace(file_name, proc_name, hooks_dir)
        if replace_content:
            replace_hooks[proc_name] = replace_content
            logger.debug(f"找到 sub_step.replace hook: {file_name} -> {proc_name}")
        
        # 收集 pre hook
        pre_content = get_sub_step_pre(file_name, proc_name, hooks_dir)
        if pre_content:
            pre_hooks[proc_name] = pre_content
            logger.debug(f"找到 sub_step.pre hook: {file_name} -> {proc_name}")
        
        # 收集 post hook
        post_content = get_sub_step_post(file_name, proc_name, hooks_dir)
        if post_content:
            post_hooks[proc_name] = post_content
            logger.debug(f"找到 sub_step.post hook: {file_name} -> {proc_name}")
    
    return {
        'replace': replace_hooks,
        'pre': pre_hooks,
        'post': post_hooks
    }


def generate_replace_hooks_code(replace_hooks: Dict[str, str]) -> List[str]:
    """
    生成 replace hooks 的代码
    
    Args:
        replace_hooks: {proc_name: replace_content}
    
    Returns:
        代码行列表
    """
    if not replace_hooks:
        return []
    
    lines = []
    lines.append("\n# ========== Sub_step replace hooks ==========\n")
    for proc_name, replace_content in replace_hooks.items():
        # 确保 replace_content 以换行符结尾
        if replace_content and not replace_content.endswith('\n'):
            replace_content += '\n'
        lines.append(f"# ========== sub_step.replace hook: {proc_name} ==========\n")
        lines.append(replace_content)
        lines.append(f"# ========== end of sub_step.replace hook: {proc_name} ==========\n")
        logger.debug(f"已添加 sub_step.replace hook: {proc_name}")
    
    return lines


def generate_pre_hooks_code(pre_hooks: Dict[str, str], flow_name: str) -> List[str]:
    """
    生成 pre hooks 的 proc 定义代码
    
    Args:
        pre_hooks: {proc_name: pre_content}
        flow_name: 流程名称
    
    Returns:
        代码行列表
    """
    if not pre_hooks:
        return []
    
    lines = []
    lines.append("\n# ========== Sub_step pre-step procs ==========\n")
    for proc_name, pre_content in pre_hooks.items():
        pre_proc_def = generate_sub_step_pre_proc(proc_name, pre_content, flow_name)
        # 确保 pre_proc_def 以换行符结尾
        if pre_proc_def and not pre_proc_def.endswith('\n'):
            pre_proc_def += '\n'
        lines.append(f"# ========== sub_step.pre hook: {proc_name} ==========\n")
        lines.append(pre_proc_def)
        lines.append(f"# ========== end of sub_step.pre hook: {proc_name} ==========\n")
        logger.debug(f"已生成 sub_step.pre proc: {proc_name}_pre")
    
    return lines


def generate_post_hooks_code(post_hooks: Dict[str, str], flow_name: str) -> List[str]:
    """
    生成 post hooks 的 proc 定义代码
    
    Args:
        post_hooks: {proc_name: post_content}
        flow_name: 流程名称
    
    Returns:
        代码行列表
    """
    if not post_hooks:
        return []
    
    lines = []
    lines.append("\n# ========== Sub_step post-step procs ==========\n")
    for proc_name, post_content in post_hooks.items():
        post_proc_def = generate_sub_step_post_proc(proc_name, post_content, flow_name)
        # 确保 post_proc_def 以换行符结尾
        if post_proc_def and not post_proc_def.endswith('\n'):
            post_proc_def += '\n'
        lines.append(f"# ========== sub_step.post hook: {proc_name} ==========\n")
        lines.append(post_proc_def)
        lines.append(f"# ========== end of sub_step.post hook: {proc_name} ==========\n")
        logger.debug(f"已生成 sub_step.post proc: {proc_name}_post")
    
    return lines


def get_pre_post_proc_names(sub_steps: List[dict], hooks_dir: Optional[Path]) -> Dict[str, Dict[str, str]]:
    """
    获取有 pre/post hooks 的 sub_steps 的 proc 名称
    
    Args:
        sub_steps: sub_steps 列表
        hooks_dir: hooks 目录路径
    
    Returns:
        字典，格式为 {
            'pre': {proc_name: pre_proc_name},
            'post': {proc_name: post_proc_name}
        }
    """
    pre_procs = {}
    post_procs = {}
    
    if not hooks_dir:
        return {'pre': pre_procs, 'post': post_procs}
    
    for sub_step in sub_steps:
        if not isinstance(sub_step, dict) or len(sub_step) != 1:
            continue
        
        file_name, proc_name = next(iter(sub_step.items()))
        # 确保文件名有 .tcl 扩展名
        if not file_name.endswith('.tcl'):
            file_name = file_name + '.tcl'
        
        pre_content = get_sub_step_pre(file_name, proc_name, hooks_dir)
        if pre_content:
            pre_procs[proc_name] = f"{proc_name}_pre"
        
        post_content = get_sub_step_post(file_name, proc_name, hooks_dir)
        if post_content:
            post_procs[proc_name] = f"{proc_name}_post"
    
    return {'pre': pre_procs, 'post': post_procs}

