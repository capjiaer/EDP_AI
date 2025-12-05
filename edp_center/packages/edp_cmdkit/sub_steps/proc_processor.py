#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Proc Processor - Proc 内容处理模块

负责处理 Tcl proc 定义，包括 global 声明管理和 proc 生成。
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


def ensure_global_declarations_in_proc(proc_content: str, flow_name: Optional[str] = None) -> str:
    """
    确保 proc 中有基础的 global 声明
    
    自动添加 global edp project {flow_name}，并移除注释掉的 global 声明行。
    不检查是否已经存在，直接添加。
    
    Args:
        proc_content: proc 定义的内容（包括 proc 声明和 body）
        flow_name: 流程名称（如 pnr_innovus, pv_calibre），用于自动添加 global 声明
    
    Returns:
        处理后的 proc 内容
    """
    lines = proc_content.splitlines(keepends=False)
    if not lines:
        return proc_content
    
    # 找到 proc 声明的行（包含 proc 关键字）
    proc_start_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('proc '):
            proc_start_idx = i
            break
    
    if proc_start_idx == -1:
        return proc_content
    
    # 找到 proc body 的开始（最后一个 {）和结束（最后一个 }）
    brace_count = 0
    body_start_idx = -1
    body_end_idx = -1
    
    for i in range(proc_start_idx, len(lines)):
        line = lines[i]
        # 找到第一个 {（proc body 的开始）
        if '{' in line and body_start_idx == -1:
            # 找到这一行中最后一个 { 的位置
            last_brace_pos = line.rfind('{')
            if last_brace_pos != -1:
                body_start_idx = i
                brace_count = 1
                # 检查这一行是否也有 }
                if '}' in line[last_brace_pos + 1:]:
                    # 检查是否在同一行完成
                    remaining = line[last_brace_pos + 1:]
                    if remaining.count('}') >= remaining.count('{'):
                        body_end_idx = i
                        break
        elif body_start_idx != -1:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                body_end_idx = i
                break
    
    if body_start_idx == -1 or body_end_idx == -1:
        return proc_content
    
    # 提取 proc body 内容
    proc_decl_lines = lines[:body_start_idx]
    proc_decl_line = lines[body_start_idx]
    proc_end_line = lines[body_end_idx]
    
    # 从 proc_decl_line 中提取 { 之前和之后的部分
    first_brace_pos = proc_decl_line.rfind('{')
    proc_decl_prefix = proc_decl_line[:first_brace_pos + 1] if first_brace_pos != -1 else proc_decl_line
    
    # 从 proc_end_line 中提取 } 之后的部分
    last_brace_pos = proc_end_line.rfind('}')
    proc_end_suffix = proc_end_line[last_brace_pos:] if last_brace_pos != -1 else proc_end_line
    
    # 提取 body 内容
    body_lines = []
    if body_start_idx == body_end_idx:
        # 单行 body
        first_brace_pos = proc_decl_line.rfind('{')
        last_brace_pos = proc_end_line.rfind('}')
        if first_brace_pos != -1 and last_brace_pos != -1:
            body_content = proc_decl_line[first_brace_pos + 1:last_brace_pos].strip()
            if body_content:
                body_lines = [body_content]
    else:
        # 多行 body
        # 第一行：{ 之后的内容
        first_brace_pos = proc_decl_line.rfind('{')
        if first_brace_pos != -1:
            first_line_body = proc_decl_line[first_brace_pos + 1:].strip()
            if first_line_body:
                body_lines.append(first_line_body)
        
        # 中间行
        for i in range(body_start_idx + 1, body_end_idx):
            body_lines.append(lines[i])
        
        # 最后一行：} 之前的内容
        last_brace_pos = proc_end_line.rfind('}')
        if last_brace_pos != -1:
            last_line_body = proc_end_line[:last_brace_pos].strip()
            if last_line_body:
                body_lines.append(last_line_body)
    
    # 检测已有的有效 global 声明（不包括注释）
    has_global_edp = False
    has_global_project = False
    has_global_flow = False
    
    # 需要移除的注释行索引
    lines_to_remove = []
    
    for i, line in enumerate(body_lines):
        stripped = line.strip()
        # 跳过注释行
        if stripped.startswith('#'):
            # 检查是否是注释掉的 global 声明
            if 'global' in stripped.lower():
                # 这是注释掉的 global，需要移除
                lines_to_remove.append(i)
            continue
        
        # 检查有效的 global 声明
        if 'global' in stripped.lower():
            # 解析 global 声明中的变量名
            # 格式可能是：global edp project pnr_innovus
            # 或者：global edp
            # 或者：global project
            parts = stripped.split()
            if len(parts) > 1 and parts[0].lower() == 'global':
                for part in parts[1:]:
                    part_lower = part.lower()
                    if part_lower == 'edp':
                        has_global_edp = True
                    elif part_lower == 'project':
                        has_global_project = True
                    elif flow_name and part_lower == flow_name.lower():
                        has_global_flow = True
    
    # 确定需要添加的 global 变量
    need_add_edp = not has_global_edp
    need_add_project = not has_global_project
    need_add_flow = flow_name and not has_global_flow
    
    # 如果不需要添加任何内容且没有注释需要移除，直接返回
    if not (need_add_edp or need_add_project or need_add_flow) and not lines_to_remove:
        return proc_content
    
    # 获取缩进（从第一行非空内容行获取）
    indent = '    '  # 默认缩进
    for line in body_lines:
        if line.strip() and not line.strip().startswith('#'):
            # 计算前导空格
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                indent = ' ' * leading_spaces
            break
    
    # 构建新的 proc body
    new_body_lines = []
    
    # If we need to add any global declarations, add them
    if need_add_edp or need_add_project or need_add_flow:
        new_body_lines.append(f"{indent}# Global variable declarations (auto-added by framework)")
        global_vars = []
        if need_add_edp:
            global_vars.append('edp')
        if need_add_project:
            global_vars.append('project')
        if need_add_flow:
            global_vars.append(flow_name)
        new_body_lines.append(f"{indent}global {' '.join(global_vars)}")
        new_body_lines.append("")
    
    # 复制其他行，跳过注释掉的 global 声明
    for i, line in enumerate(body_lines):
        if i not in lines_to_remove:
            new_body_lines.append(line)
    
    # 重新组合
    result_lines = proc_decl_lines.copy()
    
    # 处理第一行 body（包含 {）
    result_lines.append(proc_decl_prefix)
    if new_body_lines:
        # 添加所有 body 行
        result_lines.extend(new_body_lines)
    
    # 添加结束的 }
    result_lines.append(proc_end_suffix)
    
    # 添加 proc 定义之后的内容
    if body_end_idx < len(lines) - 1:
        result_lines.extend(lines[body_end_idx + 1:])
    
    return '\n'.join(result_lines)


def generate_step_hook_proc(flow_name: str, step_name: str, hook_type: str, hook_content: str) -> str:
    """
    生成 step.pre 或 step.post hook 的 proc 定义
    
    自动将散装代码封装为 proc，用户只需要写逻辑代码，不需要关心 proc 定义。
    框架会自动添加常用的 global 声明（edp project flow_name）。
    生成的 proc 可以在 debug mode 中直接调用。
    
    Args:
        flow_name: 流程名称（如 pnr_innovus, pv_calibre）
        step_name: 步骤名称（如 place, ipmerge）
        hook_type: hook 类型（'pre' 或 'post'）
        hook_content: hook 内容（散装代码）
    
    Returns:
        生成的 proc 定义字符串
    """
    proc_name = f"{flow_name}::{step_name}_{hook_type}"
    proc_def = f"proc ::{proc_name} {{}} {{\n"
    
    # 自动添加常用的 global 声明（如果用户没有写）
    # 检查用户是否已经写了 global edp project flow_name（在同一行或不同行）
    has_global_edp = False
    has_global_project = False
    has_global_flow = False
    
    for line in hook_content.splitlines():
        line_stripped = line.strip()
        if 'global' in line_stripped.lower():
            line_lower = line_stripped.lower()
            if 'edp' in line_lower:
                has_global_edp = True
            if 'project' in line_lower:
                has_global_project = True
            if flow_name.lower() in line_lower:
                has_global_flow = True
    
    # If user hasn't declared, auto-add them
    if not (has_global_edp and has_global_project and has_global_flow):
        proc_def += "    # Global variable declarations (auto-added by framework)\n"
        proc_def += f"    global edp project {flow_name}\n"
        proc_def += "\n"
    
    # 添加用户代码（添加缩进）
    indented_content = '\n'.join('    ' + line if line.strip() else line 
                                  for line in hook_content.split('\n'))
    proc_def += indented_content
    proc_def += "\n}\n"
    return proc_def


def generate_sub_step_pre_proc(proc_name: str, pre_content: str, flow_name: Optional[str] = None) -> str:
    """
    生成 sub_step pre-step proc 定义
    
    自动将散装代码封装为 proc，用户只需要写逻辑代码，不需要关心 proc 定义。
    框架会自动添加常用的 global 声明（edp project flow_name）。
    生成的 proc 可以在 debug mode 中直接调用。
    
    Args:
        proc_name: sub_step proc 名称（如 pnr_innovus::restore_design）
        pre_content: pre hook 内容（散装代码）
        flow_name: 流程名称（如 pnr_innovus, pv_calibre），用于自动添加 global 声明
    
    Returns:
        生成的 proc 定义字符串
    """
    pre_proc_name = f"{proc_name}_pre"
    proc_def = f"proc {pre_proc_name} {{}} {{\n"
    
    # 自动添加常用的 global 声明（如果用户没有写）
    # 检查用户是否已经写了 global edp project flow_name
    has_global_edp = False
    has_global_project = False
    has_global_flow = False
    
    for line in pre_content.splitlines():
        line_stripped = line.strip()
        if 'global' in line_stripped.lower():
            line_lower = line_stripped.lower()
            if 'edp' in line_lower:
                has_global_edp = True
            if 'project' in line_lower:
                has_global_project = True
            if flow_name and flow_name.lower() in line_lower:
                has_global_flow = True
    
    # If user hasn't declared, auto-add them
    if not (has_global_edp and has_global_project):
        proc_def += "    # Global variable declarations (auto-added by framework)\n"
        if flow_name and not has_global_flow:
            proc_def += f"    global edp project {flow_name}\n"
        else:
            proc_def += "    global edp project\n"
        proc_def += "\n"
    
    # 添加用户代码（添加缩进）
    indented_content = '\n'.join('    ' + line if line.strip() else line 
                                  for line in pre_content.split('\n'))
    proc_def += indented_content
    proc_def += "\n}\n"
    return proc_def


def generate_sub_step_post_proc(proc_name: str, post_content: str, flow_name: Optional[str] = None) -> str:
    """
    生成 sub_step post-step proc 定义
    
    自动将散装代码封装为 proc，用户只需要写逻辑代码，不需要关心 proc 定义。
    框架会自动添加常用的 global 声明（edp project flow_name）。
    生成的 proc 可以在 debug mode 中直接调用。
    
    Args:
        proc_name: sub_step proc 名称（如 pnr_innovus::restore_design）
        post_content: post hook 内容（散装代码）
        flow_name: 流程名称（如 pnr_innovus, pv_calibre），用于自动添加 global 声明
    
    Returns:
        生成的 proc 定义字符串
    """
    post_proc_name = f"{proc_name}_post"
    proc_def = f"proc {post_proc_name} {{}} {{\n"
    
    # 自动添加常用的 global 声明（如果用户没有写）
    # 检查用户是否已经写了 global edp project flow_name
    has_global_edp = False
    has_global_project = False
    has_global_flow = False
    
    for line in post_content.splitlines():
        line_stripped = line.strip()
        if 'global' in line_stripped.lower():
            line_lower = line_stripped.lower()
            if 'edp' in line_lower:
                has_global_edp = True
            if 'project' in line_lower:
                has_global_project = True
            if flow_name and flow_name.lower() in line_lower:
                has_global_flow = True
    
    # If user hasn't declared, auto-add them
    if not (has_global_edp and has_global_project):
        proc_def += "    # Global variable declarations (auto-added by framework)\n"
        if flow_name and not has_global_flow:
            proc_def += f"    global edp project {flow_name}\n"
        else:
            proc_def += "    global edp project\n"
        proc_def += "\n"
    
    # 添加用户代码（添加缩进）
    indented_content = '\n'.join('    ' + line if line.strip() else line 
                                  for line in post_content.split('\n'))
    proc_def += indented_content
    proc_def += "\n}\n"
    return proc_def

