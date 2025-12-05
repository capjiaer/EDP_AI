#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug 模式处理模块
负责处理 debug 模式，生成交互式脚本
"""

from pathlib import Path
from typing import Optional, Union
import logging
from .package_loader import PackageLoader
from .debug_mode_handler import generate_debug_mode_script
from .debug_execution_plan import parse_main_script_for_execution_plan

logger = logging.getLogger(__name__)


def handle_debug_mode(
    content: str,
    input_file: Path,
    edp_center_path: Optional[Union[str, Path]],
    foundry: Optional[str],
    node: Optional[str],
    project: Optional[str],
    flow_name: Optional[str],
    step_name: str,
    hooks_dir: Optional[Union[str, Path]]
) -> str:
    """
    处理 debug 模式：生成交互式脚本
    
    Args:
        content: 脚本内容
        input_file: 输入文件路径
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称
        flow_name: 流程名称
        step_name: 步骤名称
        hooks_dir: hooks 目录路径
    
    Returns:
        处理后的内容（如果是 debug 模式）
    """
    # 尝试从路径推断 flow_name（如果未提供）
    inferred_flow_name = flow_name
    if not inferred_flow_name and edp_center_path:
        try:
            package_loader = PackageLoader(edp_center_path)
            path_info = package_loader.parse_script_path(input_file)
            if path_info:
                inferred_flow_name = path_info.get('flow_name')
        except Exception:
            pass
    
    if inferred_flow_name:
        content = generate_debug_mode_script(
            content, step_name, input_file, edp_center_path, foundry, node, project, inferred_flow_name,
            parse_main_script_for_execution_plan, hooks_dir
        )
        logger.info(f"已生成 debug 模式交互式脚本")
    else:
        logger.warning(f"无法推断 flow_name，跳过 debug 模式处理")
    
    return content

