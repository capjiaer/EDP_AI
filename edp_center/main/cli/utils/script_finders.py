#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
脚本查找相关函数
"""

from pathlib import Path
from typing import Optional


def find_source_script(edp_center_path: Path, foundry: str, node: str,
                       project: Optional[str], flow_name: str, step_name: str,
                       cmd_filename: Optional[str] = None) -> Optional[Path]:
    """
    查找源脚本文件（优先项目特定，否则使用 common）
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选，如果为 None 则使用 common）
        flow_name: 流程名称
        step_name: 步骤名称
        cmd_filename: 命令文件名（从 dependency.yaml 的 cmd 字段获取，如 "test_tcl.tcl" 或 "test_py.py"）
                     如果提供，则使用此文件名；否则默认查找 {step_name}.tcl
        
    Returns:
        源脚本文件路径，如果找不到则返回 None
    """
    # 确定要查找的文件名
    if cmd_filename:
        # 使用 dependency.yaml 中指定的文件名（可能包含扩展名，如 .tcl, .py 等）
        script_filename = cmd_filename
    else:
        # 默认使用 {step_name}.tcl
        script_filename = f"{step_name}.tcl"
    
    # 优先查找项目特定的脚本
    # 支持多种路径结构（按优先级）：
    # 1. cmds/{flow_name}/steps/{flow_name}.{step_name}/{script_filename} (推荐：按 step 分目录)
    # 2. cmds/{flow_name}/steps/{step_name}/{script_filename} (简化：只用 step_name)
    # 3. cmds/{flow_name}/steps/{script_filename} (扁平结构：所有脚本在 steps/ 下)
    # 4. cmds/{flow_name}/{script_filename} (最简化：直接在 flow_name 下)
    if project:
        # 优先级 1：按 flow_name.step_name 分目录
        project_script_step_dir = (
            edp_center_path / 'flow' / 'initialize' / foundry / node / project /
            'cmds' / flow_name / 'steps' / f"{flow_name}.{step_name}" / script_filename
        )
        if project_script_step_dir.exists():
            return project_script_step_dir
        
        # 优先级 2：按 step_name 分目录
        project_script_step_simple = (
            edp_center_path / 'flow' / 'initialize' / foundry / node / project /
            'cmds' / flow_name / 'steps' / step_name / script_filename
        )
        if project_script_step_simple.exists():
            return project_script_step_simple
        
        # 优先级 3：扁平结构（steps/ 下直接放文件）
        project_script_steps = (
            edp_center_path / 'flow' / 'initialize' / foundry / node / project /
            'cmds' / flow_name / 'steps' / script_filename
        )
        if project_script_steps.exists():
            return project_script_steps
        
        # 优先级 4：最简化（直接在 cmds/{flow_name}/ 下）
        project_script = (
            edp_center_path / 'flow' / 'initialize' / foundry / node / project /
            'cmds' / flow_name / script_filename
        )
        if project_script.exists():
            return project_script
    
    # 查找 common 脚本（同样的优先级顺序）
    # 优先级 1：按 flow_name.step_name 分目录
    common_script_step_dir = (
        edp_center_path / 'flow' / 'initialize' / foundry / node / 'common' /
        'cmds' / flow_name / 'steps' / f"{flow_name}.{step_name}" / script_filename
    )
    if common_script_step_dir.exists():
        return common_script_step_dir
    
    # 优先级 2：按 step_name 分目录
    common_script_step_simple = (
        edp_center_path / 'flow' / 'initialize' / foundry / node / 'common' /
        'cmds' / flow_name / 'steps' / step_name / script_filename
    )
    if common_script_step_simple.exists():
        return common_script_step_simple
    
    # 优先级 3：扁平结构（steps/ 下直接放文件）
    common_script_steps = (
        edp_center_path / 'flow' / 'initialize' / foundry / node / 'common' /
        'cmds' / flow_name / 'steps' / script_filename
    )
    if common_script_steps.exists():
        return common_script_steps
    
    # 优先级 4：最简化（直接在 cmds/{flow_name}/ 下）
    common_script = (
        edp_center_path / 'flow' / 'initialize' / foundry / node / 'common' /
        'cmds' / flow_name / script_filename
    )
    if common_script.exists():
        return common_script
    
    return None

