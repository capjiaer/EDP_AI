#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug Mode 处理模块
处理 debug 模式下的交互式脚本生成
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
import logging
from .debug_execution_plan import parse_main_script_for_execution_plan

logger = logging.getLogger(__name__)


def escape_tcl_string(text: str) -> str:
    """
    转义 Tcl 代码中的特殊字符，用于嵌入到 proc 定义中
    
    注意：这里不是转义字符串，而是转义代码块，所以需要特殊处理
    对于多行代码，直接返回（因为会放在 proc {} 块中）
    """
    # 对于代码块，不需要转义，直接返回
    # 因为代码会放在 proc {} {} 的大括号中
    return text


# parse_main_script_for_execution_plan 已移动到 debug_execution_plan.py

def generate_debug_mode_script(original_content: str, step_name: str, 
                               input_file: Union[str, Path], 
                               edp_center_path: Optional[Union[str, Path]],
                               foundry: Optional[str], node: Optional[str],
                               project: Optional[str], flow_name: str,
                               parse_main_script_func,
                               hooks_dir: Optional[Path] = None) -> str:
    """
    生成 debug 模式的交互式脚本
    
    在 debug 模式下：
    1. Source 所有必要的文件（packages, sub_steps, full.tcl）- 已经在 prepend_content 中完成
    2. Source step.pre hook - 已经在 process_step_hooks 中完成
    3. 解析主脚本，提取中间代码，生成 proc
    4. 调用 edp_run -init 初始化环境（使用执行计划）
    5. return - 停止执行，进入交互模式（tclsh 会自动进入交互模式）
    
    Args:
        original_content: 原始脚本内容（已经包含了 step.pre hook 和主脚本）
        step_name: 步骤名称
        input_file: 原始主脚本文件路径
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称
        flow_name: 流程名称
        parse_main_script_func: 解析主脚本的函数（用于依赖注入）
    
    Returns:
        生成的交互式脚本内容
    """
    # 分离 step.pre hook、主脚本内容和 step.post hook
    # 注意：original_content 可能包含 prepend_content（source 语句），需要找到 step.pre hook 的开始位置
    step_pre_start = original_content.find("# ========== step.pre hook ==========")
    step_pre_end = original_content.find("# ========== end of step.pre hook ==========")
    step_post_start = original_content.find("# ========== step.post hook ==========")
    
    # 提取主脚本内容（已经处理过 #import 的完整代码）
    # 从 step.pre 之后到 step.post 之前（如果存在）
    if step_pre_end != -1:
        step_pre_end_pos = original_content.find("\n", step_pre_end) + 1
        main_script_start = step_pre_end_pos
    elif step_pre_start != -1:
        # 如果没有 end 标记，从 start 之后开始查找
        main_script_start = original_content.find("\n", step_pre_start) + 1
        # 跳过 step.pre hook 的内容，找到主脚本开始位置
        # 查找下一个非注释、非空行的开始
        lines = original_content[main_script_start:].split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                main_script_start += sum(len(l) + 1 for l in lines[:i])
                break
    else:
        main_script_start = 0
    
    main_script_end = step_post_start if step_post_start != -1 else len(original_content)
    main_script_content = original_content[main_script_start:main_script_end].strip()
    
    # 解析已处理的主脚本，提取 sub_steps 和 proc 调用
    # 注意：main_script_content 已经处理过所有 #import source
    # 我们只需要识别主脚本中的 proc 调用（sub_steps）
    execution_plan = parse_main_script_func(
        main_script_content, step_name, edp_center_path, foundry, node, project, flow_name, hooks_dir
    )
    
    # 提取主脚本内容（用于识别 sub_steps 调用）
    main_script_lines = main_script_content.split('\n')
    sub_step_proc_names = []
    if edp_center_path and foundry and node:
        from .sub_steps import read_sub_steps_from_dependency
        edp_center_path_obj = Path(edp_center_path)
        sub_steps = read_sub_steps_from_dependency(
            edp_center_path_obj, foundry, node, project, flow_name, step_name
        )
        for sub_step in sub_steps:
            if isinstance(sub_step, dict) and len(sub_step) == 1:
                _, proc_name = next(iter(sub_step.items()))
                sub_step_proc_names.append(proc_name)
    
    
    # 生成 debug 模式脚本
    # 核心原则：debug 模式只需要确保所有 proc 定义存在，然后用 edp_run 管理调用
    # 
    # 普通模式结构：
    #   1. source 语句（packages, sub_steps proc 定义）
    #   2. step.pre hook
    #   3. 主脚本内容
    #   4. sub_steps 调用（直接执行）
    #   5. step.post hook
    #
    # Debug 模式结构：
    #   1. source 语句（packages, sub_steps proc 定义）- 与普通模式相同
    #   2. step.pre hook proc（如果存在）- 与普通模式相同
    #   3. step.post hook proc（如果存在）- 与普通模式相同
    #   4. 移除 sub_steps 调用部分（由 edp_run 管理调用）
    #   5. 执行计划变量（包含 step.pre, sub_steps, step.post）
    #   6. edp_run -init
    #   7. return
    
    # 构建执行计划：step.pre (如果有) -> sub_steps (包括 pre/post hooks) -> step.post (如果有)
    final_execution_plan = []
    
    # 添加 step.pre hook 到执行计划（如果存在）
    if step_pre_start != -1:
        step_pre_proc_name = f"{flow_name}::{step_name}_pre"
        final_execution_plan.append(step_pre_proc_name)
    
    # 检查每个 sub_step 是否有 pre/post hooks，并按照正确顺序添加到执行计划
    # 顺序：sub_step.pre (如果有) -> sub_step proc -> sub_step.post (如果有)
    if hooks_dir and sub_step_proc_names:
        from .sub_steps.hooks import get_sub_step_pre, get_sub_step_post
        from .sub_steps import read_sub_steps_from_dependency
        
        edp_center_path_obj = Path(edp_center_path) if edp_center_path else None
        if edp_center_path_obj:
            sub_steps = read_sub_steps_from_dependency(
                edp_center_path_obj, foundry, node, project, flow_name, step_name
            )
            hooks_dir_path = Path(hooks_dir)
            
            for sub_step in sub_steps:
                if isinstance(sub_step, dict) and len(sub_step) == 1:
                    file_name, proc_name = next(iter(sub_step.items()))
                    # 确保文件名有 .tcl 扩展名
                    if not file_name.endswith('.tcl'):
                        file_name = file_name + '.tcl'
                    
                    # 检查是否有 pre hook
                    pre_content = get_sub_step_pre(file_name, proc_name, hooks_dir_path)
                    if pre_content:
                        pre_proc_name = f"{proc_name}_pre"
                        if pre_proc_name not in final_execution_plan:
                            final_execution_plan.append(pre_proc_name)
                    
                    # 添加 sub_step proc（如果还没有）
                    if proc_name not in final_execution_plan:
                        final_execution_plan.append(proc_name)
                    
                    # 检查是否有 post hook
                    post_content = get_sub_step_post(file_name, proc_name, hooks_dir_path)
                    if post_content:
                        post_proc_name = f"{proc_name}_post"
                        if post_proc_name not in final_execution_plan:
                            final_execution_plan.append(post_proc_name)
    else:
        # 如果没有 hooks_dir，直接使用 execution_plan 中的 sub_steps
        for proc_name in execution_plan:
            if proc_name not in final_execution_plan:
                final_execution_plan.append(proc_name)
    
    # 添加 step.post hook 到执行计划（如果存在）
    if step_post_start != -1:
        step_post_proc_name = f"{flow_name}::{step_name}_post"
        if step_post_proc_name not in final_execution_plan:
            final_execution_plan.append(step_post_proc_name)
    
    # 构建 debug 模式脚本
    # 核心思路：直接使用 normal 模式生成的脚本（original_content），它已经包含了所有 proc 定义
    # 只需要：
    # 1. 移除 sub_steps 调用部分（由 edp_run 管理调用）
    # 2. 添加 debug 模式的执行计划初始化代码
    debug_script = original_content.rstrip()
    
    # 移除 sub_steps 调用部分（如果存在，由 edp_run 管理调用）
    # 在 debug_script 中查找并移除（因为 debug_script 可能已经被修改过）
    sub_steps_calls_start = debug_script.find("# ========== Auto-generated sub_steps calls ==========")
    if sub_steps_calls_start != -1:
        sub_steps_calls_end = debug_script.find("# ========== End of auto-generated sub_steps calls ==========")
        if sub_steps_calls_end != -1:
            # 找到结束标记后的换行符位置
            sub_steps_calls_end_pos = debug_script.find("\n", sub_steps_calls_end)
            if sub_steps_calls_end_pos != -1:
                sub_steps_calls_end_pos += 1  # 包含换行符
            else:
                sub_steps_calls_end_pos = len(debug_script)
            
            # 移除整个 sub_steps 调用部分（包括前后的空行）
            sub_steps_calls_section = debug_script[sub_steps_calls_start:sub_steps_calls_end_pos]
            debug_script = debug_script.replace(sub_steps_calls_section, "").strip()
            
            # 清理可能留下的多余空行
            debug_script = re.sub(r'\n\n\n+', '\n\n', debug_script)
    
    # 生成执行计划变量（在 debug 脚本中设置）
    # 为每个 proc 名称添加引号（如果包含特殊字符）
    def quote_proc_name(name: str) -> str:
        if any(c in name for c in ' {}[]$\\'):
            return f'"{name}"'
        return name
    
    execution_plan_str = " ".join([quote_proc_name(proc_name) for proc_name in final_execution_plan])
    
    # 添加初始化代码
    debug_script += f"""
# ========== Debug Mode: Interactive Execution Plan Manager ==========
# Debug mode enabled. Initializing environment and entering interactive mode.
# Use 'edp_run -help' for available commands.

# Update execution plan variable (includes sub_steps and intermediate code procs)
# This will override the execution plan in full.tcl (if exists), adding intermediate code
set edp(execution_plan,{step_name}) {{{execution_plan_str}}}

# Initialize edp_sub_steps_manager (using execution plan)
edp_run -init edp(execution_plan,{step_name})

# Stop execution and enter interactive mode (tclsh will automatically enter interactive mode)
return

"""
    
    return debug_script


