#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug Mode 执行计划解析器
解析主脚本，构建执行计划
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
import logging
from .sub_steps import read_sub_steps_from_dependency

logger = logging.getLogger(__name__)


def parse_main_script_for_execution_plan(main_script_content: str, step_name: str,
                                          edp_center_path: Optional[Union[str, Path]],
                                          foundry: Optional[str], node: Optional[str],
                                          project: Optional[str], flow_name: str,
                                          hooks_dir: Optional[Path] = None) -> Tuple[List[str], Dict[str, str]]:
    """
    解析主脚本，构建执行计划
    
    主脚本可以包含：
    1. #import source 语句（生成 source 语句，加载文件）
    2. sub_step proc 调用
    3. 自由代码（允许，但建议放在 step.pre/step.post hooks 中）
    
    注意：自由代码在 debug 模式下会被自动封装为 proc（code_between_X_Y 或 code_after_step_end）
    
    返回：
        execution_plan: 执行计划列表（proc 名称列表）
    """
    # 1. 获取 sub_steps 列表
    sub_steps = []
    if edp_center_path and foundry and node:
        edp_center_path_obj = Path(edp_center_path)
        sub_steps = read_sub_steps_from_dependency(
            edp_center_path_obj, foundry, node, project, flow_name, step_name
        )
    
    # 提取 sub_step proc 名称列表
    sub_step_proc_names = []
    for sub_step in sub_steps:
        if isinstance(sub_step, dict) and len(sub_step) == 1:
            _, proc_name = next(iter(sub_step.items()))
            sub_step_proc_names.append(proc_name)
    
    # 2. 解析主脚本，识别 sub_step proc 调用
    lines = main_script_content.split('\n')
    execution_plan = []
    
    # 收集所有可能的 proc 名称
    all_proc_names = set(sub_step_proc_names)
    
    # 识别 sub_step proc 调用的位置
    sub_step_positions = []  # [(line_idx, proc_name), ...]
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 跳过注释行和空行
        if not stripped or stripped.startswith('#'):
            continue
        
        # 检查是否是 sub_step proc 调用
        for proc_name in sub_step_proc_names:
            # 使用正则匹配，确保是完整的 proc 调用（不是 proc 定义）
            pattern = r'\b' + re.escape(proc_name) + r'\b'
            if re.search(pattern, stripped):
                # 确保不是 proc 定义
                if not re.search(r'^\s*proc\s+' + re.escape(proc_name), stripped):
                    sub_step_positions.append((i, proc_name))
                    break
    
    # 2.3 按照顺序构建执行计划：sub_step proc 调用
    # 添加 sub_step proc 调用位置
    for line_idx, proc_name in sub_step_positions:
        # 检查是否有对应的 pre-step
        if proc_name in sub_step_proc_names:
            pre_proc_name = f"{proc_name}_pre"
            # 检查前一行是否是 pre-step 调用
            if line_idx > 0:
                prev_line = lines[line_idx-1].strip()
                pre_pattern = r'\b' + re.escape(pre_proc_name) + r'\b'
                if re.search(pre_pattern, prev_line):
                    # 先添加 pre-step 到执行计划（如果还没有）
                    if pre_proc_name not in execution_plan:
                        execution_plan.append(pre_proc_name)
                        logger.debug(f"识别到 sub_step pre-step: {pre_proc_name}")
        
        # 添加 sub_step proc 到执行计划
        if proc_name not in execution_plan:
            execution_plan.append(proc_name)
            logger.debug(f"识别到 sub_step proc 调用: {proc_name}")
    
    logger.info(f"构建执行计划: {len(execution_plan)} 个步骤")
    
    return execution_plan

