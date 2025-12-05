#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sub-steps 处理模块
负责处理 sub_steps 相关的逻辑（插入 pre 调用、条件包装、自动生成调用）
"""

import re
from pathlib import Path
from typing import List, Optional
import logging
from .sub_steps import (
    read_sub_steps_from_dependency,
    get_sub_step_pre,
    generate_sub_steps_calls
)

logger = logging.getLogger(__name__)


class SubStepsProcessor:
    """Sub-steps 处理器"""
    
    def insert_sub_step_pre_calls(
        self,
        content: str,
        edp_center_path: Path,
        foundry: str,
        node: str,
        project: Optional[str],
        flow_name: str,
        step_name: str,
        hooks_dir: Path
    ) -> str:
        """
        在主脚本中插入 sub_step pre-step 调用
        
        检测 sub_step proc 调用，并在调用之前插入 pre-step 调用（如果存在 pre hook）
        
        Args:
            content: 处理后的脚本内容
            edp_center_path: edp_center 路径
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称（可选）
            flow_name: 流程名称
            step_name: 步骤名称
            hooks_dir: hooks 目录路径
        
        Returns:
            插入 pre-step 调用后的内容
        """
        # 获取 sub_steps 列表
        sub_steps = read_sub_steps_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
        if not sub_steps:
            return content
        
        # 提取 sub_step proc 名称列表，并检查哪些有 pre hook
        sub_step_proc_names = []
        sub_step_pre_procs = {}  # {proc_name: pre_proc_name}
        
        for sub_step in sub_steps:
            if isinstance(sub_step, dict) and len(sub_step) == 1:
                file_name, proc_name = next(iter(sub_step.items()))
                sub_step_proc_names.append(proc_name)
                
                # 确保文件名有 .tcl 扩展名
                if not file_name.endswith('.tcl'):
                    file_name = file_name + '.tcl'
                
                # 检查是否有 pre hook（优先使用 file_name，更直观）
                pre_content = get_sub_step_pre(file_name, proc_name, hooks_dir)
                if pre_content:
                    pre_proc_name = f"{proc_name}_pre"
                    sub_step_pre_procs[proc_name] = pre_proc_name
        
        if not sub_step_pre_procs:
            return content  # 没有 pre hook，直接返回
        
        # 扫描内容，在 sub_step proc 调用之前插入 pre-step 调用
        lines = content.splitlines(keepends=True)
        result_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检查是否是 sub_step proc 调用
            for proc_name in sub_step_proc_names:
                if proc_name in sub_step_pre_procs:  # 只处理有 pre hook 的
                    # 使用正则匹配，确保是完整的 proc 调用
                    pattern = r'\b' + re.escape(proc_name) + r'\b'
                    if re.search(pattern, stripped):
                        # 检查前一行是否已经是 pre-step 调用（避免重复插入）
                        if i > 0:
                            prev_line = lines[i-1].strip()
                            pre_proc_name = sub_step_pre_procs[proc_name]
                            if pre_proc_name in prev_line:
                                # 已经插入过了，跳过
                                result_lines.append(line)
                                break
                        
                        # 插入 pre-step 调用
                        pre_proc_name = sub_step_pre_procs[proc_name]
                        result_lines.append(f"{pre_proc_name}\n")
                        result_lines.append(line)
                        logger.debug(f"已在 {proc_name} 之前插入 {pre_proc_name} 调用")
                        break
            else:
                # 不是 sub_step proc 调用，直接保留
                result_lines.append(line)
        
        return ''.join(result_lines)
    
    def wrap_sub_steps_with_conditions(
        self,
        content: str,
        edp_center_path: Path,
        foundry: str,
        node: str,
        project: Optional[str],
        flow_name: str,
        step_name: str,
        skip_sub_steps: List[str]
    ) -> str:
        """
        将指定的 sub_step 调用包装在条件判断中，使其可以被跳过
        
        如果 sub_step 在 skip_sub_steps 列表中，将其调用包装为：
        if {![info exists edp(skip,proc_name)]} {
            proc_name
        }
        
        这样，如果设置了 edp(skip,proc_name) 变量，该 sub_step 就会被跳过
        
        Args:
            content: 处理后的脚本内容
            edp_center_path: edp_center 路径
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称（可选）
            flow_name: 流程名称
            step_name: 步骤名称
            skip_sub_steps: 要跳过的 sub_steps 列表（proc 名称列表）
        
        Returns:
            条件化后的内容
        """
        # 获取 sub_steps 列表
        sub_steps = read_sub_steps_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
        if not sub_steps:
            return content
        
        # 提取 sub_step proc 名称列表，并构建要跳过的 proc 名称集合
        sub_step_proc_names = []
        skip_proc_set = set(skip_sub_steps)  # 转换为集合以便快速查找
        
        for sub_step in sub_steps:
            if isinstance(sub_step, dict) and len(sub_step) == 1:
                _, proc_name = next(iter(sub_step.items()))
                sub_step_proc_names.append(proc_name)
        
        # 如果没有要跳过的 sub_step，直接返回
        if not skip_proc_set:
            return content
        
        # 在文件开头添加初始化代码，设置 edp(skip,proc_name) 变量
        init_code = "\n# ========== Skip sub_steps configuration ==========\n"
        for proc_name in skip_proc_set:
            init_code += f"set edp(skip,{proc_name}) 1\n"
        init_code += "# ====================================================\n\n"
        
        # 扫描内容，将需要跳过的 sub_step proc 调用包装在条件判断中
        lines = content.splitlines(keepends=True)
        result_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检查是否是 sub_step proc 调用（且需要跳过）
            for proc_name in sub_step_proc_names:
                if proc_name in skip_proc_set:
                    # 使用正则匹配，确保是完整的 proc 调用
                    pattern = r'\b' + re.escape(proc_name) + r'\b'
                    if re.search(pattern, stripped):
                        # 检查前一行是否已经是条件判断（避免重复包装）
                        if i > 0:
                            prev_line = lines[i-1].strip()
                            if prev_line.startswith('if {![info exists edp(skip,') and proc_name in prev_line:
                                # 已经包装过了，跳过
                                result_lines.append(line)
                                break
                        
                        # 检查是否是注释行（跳过注释）
                        if stripped.startswith('#'):
                            result_lines.append(line)
                            break
                        
                        # 获取当前行的缩进
                        indent = len(line) - len(line.lstrip())
                        indent_str = ' ' * indent
                        
                        # 包装为条件判断
                        result_lines.append(f"{indent_str}if {{![info exists edp(skip,{proc_name})]}} {{\n")
                        result_lines.append(line)
                        result_lines.append(f"{indent_str}}}\n")
                        logger.debug(f"已将 {proc_name} 调用包装在条件判断中")
                        break
            else:
                # 不是需要跳过的 sub_step proc 调用，直接保留
                result_lines.append(line)
        
        # 在文件开头添加初始化代码（在第一个非注释行之前）
        final_lines = []
        init_added = False
        for line in result_lines:
            if not init_added and line.strip() and not line.strip().startswith('#'):
                # 找到第一个非注释行，在此之前插入初始化代码
                final_lines.append(init_code)
                init_added = True
            final_lines.append(line)
        
        # 如果没有找到非注释行，在开头添加
        if not init_added:
            final_lines.insert(0, init_code)
        
        return ''.join(final_lines)
    
    def insert_auto_generated_sub_steps(
        self,
        content: str,
        edp_center_path: Path,
        foundry: str,
        node: str,
        project: Optional[str],
        flow_name: str,
        step_name: str,
        hooks_dir: Optional[Path] = None
    ) -> str:
        """
        在主脚本的 pre_step 部分之后、step.post hook 之前自动插入 sub_steps 调用
        
        最终执行顺序：
        1. pre_step（step.pre hook，如果有）
        2. pre_step（主脚本内容，包括所有 #import 指令和自由代码）
        3. pre_sub_steps（sub_step.pre hooks，如果有，自动包含在 sub_steps 调用中）
        4. sub_steps（自动生成的 sub_step 调用，从 dependency.yaml 读取）
        5. post_step（step.post hook，如果有）
        
        注意：主脚本中的所有逻辑都属于 pre_step 部分
        
        Args:
            content: 处理后的脚本内容
            edp_center_path: edp_center 路径
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称（可选）
            flow_name: 流程名称
            step_name: 步骤名称
            hooks_dir: hooks 目录路径
        
        Returns:
            插入 sub_steps 调用后的内容
        """
        # 生成 sub_steps 调用代码
        sub_steps_calls = generate_sub_steps_calls(
            edp_center_path, foundry, node, project, flow_name, step_name, hooks_dir
        )
        
        # 如果没有 sub_steps，直接返回
        if not sub_steps_calls:
            return content
        
        # 查找 step.post hook 的位置
        step_post_marker = "# ========== step.post hook =========="
        step_post_start = content.find(step_post_marker)
        
        if step_post_start != -1:
            # 如果存在 step.post hook，在它之前插入 sub_steps 调用
            before_post = content[:step_post_start]
            after_post = content[step_post_start:]
            
            # 在 step.post 之前插入 sub_steps 调用
            result = before_post.rstrip() + "\n" + sub_steps_calls + after_post
            logger.debug(f"已在 step.post hook 之前插入自动生成的 sub_steps 调用")
        else:
            # 如果没有 step.post hook，在内容末尾插入 sub_steps 调用
            result = content.rstrip() + "\n" + sub_steps_calls
            logger.debug(f"已在脚本末尾插入自动生成的 sub_steps 调用")
        
        return result

