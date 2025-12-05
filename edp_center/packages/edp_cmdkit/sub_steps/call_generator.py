#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Call Generator - Sub Steps 调用代码生成模块

负责从 dependency.yaml 读取 sub_steps，生成对应的 proc 调用代码。
"""

from pathlib import Path
from typing import Optional
import logging

from .reader import read_sub_steps_from_dependency
from .hooks_integration import get_pre_post_proc_names

logger = logging.getLogger(__name__)


def generate_sub_steps_calls(edp_center_path: Path, foundry: str, node: str,
                             project: Optional[str], flow_name: str, step_name: str,
                             hooks_dir: Optional[Path] = None) -> str:
    """
    从 dependency.yaml 读取 sub_steps，生成对应的 proc 调用代码
    
    生成的代码包括：
    1. sub_step proc 调用（按 dependency.yaml 中的顺序）
    2. 如果有 sub_step.pre hook，在调用前插入 pre-step 调用
    3. 如果有 sub_step.post hook，在调用后插入 post-step 调用
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        step_name: 步骤名称
        hooks_dir: hooks 目录路径（用于检查 sub_step.pre/post hooks）
    
    Returns:
        生成的 sub_steps 调用代码字符串（如果存在 sub_steps），否则返回空字符串
    """
    # 从 dependency.yaml 读取 sub_steps
    sub_steps = read_sub_steps_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
    if not sub_steps:
        return ""
    
    call_lines = []
    call_lines.append("\n# ========== Auto-generated sub_steps calls ==========\n")
    call_lines.append("# Sub_steps are automatically generated from dependency.yaml\n")
    
    # 检查哪些 sub_steps 有 pre hook 和 post hook
    hook_proc_names = get_pre_post_proc_names(sub_steps, hooks_dir)
    sub_step_pre_procs = hook_proc_names['pre']  # {proc_name: pre_proc_name}
    sub_step_post_procs = hook_proc_names['post']  # {proc_name: post_proc_name}
    
    # 生成 sub_step 调用（按顺序）
    for sub_step in sub_steps:
        if isinstance(sub_step, dict) and len(sub_step) == 1:
            _, proc_name = next(iter(sub_step.items()))
            
            # 如果有 pre hook，先调用 pre-step
            if proc_name in sub_step_pre_procs:
                pre_proc_name = sub_step_pre_procs[proc_name]
                call_lines.append(f"{pre_proc_name}\n")
            
            # 调用 sub_step proc
            call_lines.append(f"{proc_name}\n")
            
            # 如果有 post hook，在 sub_step 调用之后调用 post-step
            if proc_name in sub_step_post_procs:
                post_proc_name = sub_step_post_procs[proc_name]
                call_lines.append(f"{post_proc_name}\n")
    
    call_lines.append("# ========== End of auto-generated sub_steps calls ==========\n")
    
    return ''.join(call_lines)

