#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
内容整合模块
实现"先整合后处理"策略：先整合所有内容（包括 hooks），然后统一处理 #import

处理流程：
1. 整合阶段（本模块）：
   - 整合 step.pre hook（原始内容）
   - 整合主脚本（将 #import util 替换为完整的 util 结构，包括 util hooks）
   - 整合 step.post hook（原始内容）
   - 注意：此阶段不处理 #import 指令，只是拼接内容

2. 处理阶段（cmd_processor.py::_process_imports_in_content）：
   - 递归处理整合后的内容中的所有 #import 指令
   - 包括 hooks 中的 #import 指令

这样设计的好处：
- 所有 hooks 中的 #import 指令都能被正确处理
- 处理逻辑统一，易于维护
- 支持递归处理，支持复杂的依赖关系
"""

from pathlib import Path
from typing import List, Optional, Union
import re
import logging
from .hooks_handler import is_hook_file_empty
from .file_finder import find_file
from .util_proc_detector import get_util_proc_name

logger = logging.getLogger(__name__)

# 匹配 #import 指令的正则表达式（只支持 source）
IMPORT_PATTERN = re.compile(r'^\s*#\s*import\s+source\s+(.+)$', re.IGNORECASE)


def validate_no_import_between_sub_steps(main_script_content: str,
                                          edp_center_path: Optional[Path],
                                          foundry: Optional[str],
                                          node: Optional[str],
                                          project: Optional[str],
                                          flow_name: Optional[str],
                                          step_name: Optional[str]) -> None:
    """
    检查主脚本中是否在 sub_steps 之间使用了 #import 指令
    
    如果检测到 sub_steps 之间有 #import 指令，抛出 ValueError
    
    Args:
        main_script_content: 主脚本内容
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称
        flow_name: 流程名称
        step_name: 步骤名称
    
    Raises:
        ValueError: 如果检测到 sub_steps 之间有 #import 指令
    """
    # 如果没有必要的信息，跳过检查
    if not (edp_center_path and foundry and node and flow_name and step_name):
        return
    
    try:
        from .sub_steps import read_sub_steps_from_dependency
        
        # 读取 sub_steps 列表
        sub_steps = read_sub_steps_from_dependency(
            edp_center_path, foundry, node, project, flow_name, step_name
        )
        
        # 如果没有 sub_steps，不需要检查
        if not sub_steps:
            return
        
        # 提取 sub_step proc 名称列表
        sub_step_proc_names = []
        for sub_step in sub_steps:
            if isinstance(sub_step, dict) and len(sub_step) == 1:
                _, proc_name = next(iter(sub_step.items()))
                sub_step_proc_names.append(proc_name)
        
        if not sub_step_proc_names:
            return
        
        # 识别主脚本中的 sub_step proc 调用位置
        lines = main_script_content.splitlines(keepends=False)
        sub_step_positions = []  # [(line_idx, proc_name), ...]
        
        for line_idx, line in enumerate(lines):
            stripped = line.strip()
            # 跳过注释行
            if stripped.startswith('#'):
                continue
            
            # 检查是否是 sub_step proc 调用
            for proc_name in sub_step_proc_names:
                # 使用正则匹配，确保是完整的 proc 调用
                pattern = r'\b' + re.escape(proc_name) + r'\b'
                if re.search(pattern, stripped):
                    sub_step_positions.append((line_idx, proc_name))
                    break
        
        # 如果少于 2 个 sub_step 调用，不需要检查
        if len(sub_step_positions) < 2:
            return
        
        # 检查每两个相邻的 sub_step 调用之间是否有 #import 指令
        for i in range(len(sub_step_positions) - 1):
            start_line_idx, start_proc_name = sub_step_positions[i]
            end_line_idx, end_proc_name = sub_step_positions[i + 1]
            
            # 检查这两行之间的所有行
            for line_idx in range(start_line_idx + 1, end_line_idx):
                line = lines[line_idx]
                stripped = line.strip()
                
                # 检查是否是 #import 指令
                match = IMPORT_PATTERN.match(stripped)
                if match:
                    import_file = match.group(1).strip()
                    raise ValueError(
                        f"#import directive is not allowed between sub_steps!\n"
                        f"  Location: Line {line_idx + 1}\n"
                        f"  Directive: #import source {import_file}\n"
                        f"  Between: {start_proc_name} and {end_proc_name}\n"
                        f"  Suggestion: Move #import source directive before all sub_steps, or use step.pre hook"
                    )
    except ValueError:
        # 重新抛出 ValueError（这是我们的检查错误）
        raise
    except Exception as e:
        # 其他错误（如读取 sub_steps 失败）只记录警告，不阻止处理
        logger.warning(f"检查 sub_steps 之间的 #import 指令时出错: {e}")


def assemble_content_with_hooks(main_script_file: Path,
                                 search_paths: List[Path],
                                 hooks_dir: Optional[Path] = None,
                                 step_name: Optional[str] = None,
                                 edp_center_path: Optional[Path] = None,
                                 foundry: Optional[str] = None,
                                 node: Optional[str] = None,
                                 project: Optional[str] = None,
                                 flow_name: Optional[str] = None) -> str:
    """
    整合主脚本和所有 hooks 的内容（不处理 #import，只是拼接）
    
    整合顺序：
    1. step.pre（原始内容）
    2. 主脚本（原始内容）
    3. step.post（原始内容）
    
    注意：支持 #import source，会在后续阶段统一处理
    注意：如果提供了必要信息，会检查是否在 sub_steps 之间使用了 #import 指令
    
    Args:
        main_script_file: 主脚本文件路径
        search_paths: 搜索路径列表
        hooks_dir: hooks 目录路径
        step_name: 步骤名称
        edp_center_path: edp_center 路径（用于检查 sub_steps）
        foundry: 代工厂名称（用于检查 sub_steps）
        node: 工艺节点（用于检查 sub_steps）
        project: 项目名称（用于检查 sub_steps）
        flow_name: 流程名称（用于检查 sub_steps）
    
    Returns:
        整合后的完整内容（所有 #import 还未处理）
    
    Raises:
        ValueError: 如果检测到 sub_steps 之间有 #import 指令
    """
    result_parts = []
    
    # 1. 添加 step.pre hook（如果存在，封装为 proc）
    if hooks_dir and step_name and flow_name:
        hooks_dir_path = Path(hooks_dir)
        if hooks_dir_path.exists():
            step_pre_file = hooks_dir_path / 'step.pre'
            if step_pre_file.exists():
                step_pre_content = step_pre_file.read_text(encoding='utf-8')
                if not is_hook_file_empty(step_pre_content):
                    # 导入生成函数（从 generator 导入，向后兼容）
                    from ..sub_steps import generate_step_hook_proc
                    # 生成 proc 定义
                    step_pre_proc = generate_step_hook_proc(flow_name, step_name, 'pre', step_pre_content)
                    result_parts.append(f"# ========== step.pre hook ==========\n")
                    result_parts.append(step_pre_proc)
                    result_parts.append(f"# ========== end of step.pre hook ==========\n")
                    # Add proc call
                    result_parts.append(f"# Call step.pre hook\n")
                    result_parts.append(f"::{flow_name}::{step_name}_pre\n")
                    result_parts.append("\n")
                    logger.info(f"已整合 step.pre hook: {step_pre_file}（已封装为 proc）")
    
    # 2. 处理主脚本（处理 #import source 指令）
    try:
        main_script_content = main_script_file.read_text(encoding='utf-8')
    except Exception as e:
        raise IOError(f"Failed to read main script file {main_script_file}: {e}")
    
    # 检查是否在 sub_steps 之间使用了 #import 指令（如果提供了必要信息）
    if edp_center_path and foundry and node and flow_name and step_name:
        validate_no_import_between_sub_steps(
            main_script_content, edp_center_path, foundry, node, project, flow_name, step_name
        )
    
    # 处理主脚本（所有 #import source 指令都会在第二阶段统一处理）
    processed_lines = main_script_content.splitlines(keepends=True)
    
    result_parts.append(''.join(processed_lines))
    
    # 3. 添加 step.post hook（如果存在，封装为 proc）
    if hooks_dir and step_name and flow_name:
        hooks_dir_path = Path(hooks_dir)
        if hooks_dir_path.exists():
            step_post_file = hooks_dir_path / 'step.post'
            if step_post_file.exists():
                step_post_content = step_post_file.read_text(encoding='utf-8')
                if not is_hook_file_empty(step_post_content):
                    # 导入生成函数（从 generator 导入，向后兼容）
                    from ..sub_steps import generate_step_hook_proc
                    # 生成 proc 定义
                    step_post_proc = generate_step_hook_proc(flow_name, step_name, 'post', step_post_content)
                    result_parts.append(f"\n# ========== step.post hook ==========\n")
                    result_parts.append(step_post_proc)
                    result_parts.append(f"# ========== end of step.post hook ==========\n")
                    # Add proc call
                    result_parts.append(f"# Call step.post hook\n")
                    result_parts.append(f"::{flow_name}::{step_name}_post\n")
                    logger.info(f"已整合 step.post hook: {step_post_file}（已封装为 proc）")
    
    return ''.join(result_parts)


# 注意：_assemble_util_structure 函数已移除
# 已移除 #import util 机制，统一使用 #import source，不再需要此函数

