#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Source 前置处理模块
负责在文件头部添加默认的 source 语句（package source、sub_steps source、full.tcl source）
"""

from pathlib import Path
from typing import List, Optional, Union
import logging
from .package_loader import PackageLoader
from .sub_steps import generate_sub_steps_sources
from edp_center.packages.edp_common.path_utils import to_tcl_path

logger = logging.getLogger(__name__)


def add_prepend_sources(
    content: str,
    input_file: Path,
    edp_center_path: Union[str, Path],
    foundry: Optional[str],
    node: Optional[str],
    project: Optional[str],
    flow_name: Optional[str],
    step_name: Optional[str],
    full_tcl_path: Optional[Union[str, Path]],
    output_file: Optional[Union[str, Path]],
    search_paths: List[Path],
    hooks_dir: Optional[Union[str, Path]]
) -> str:
    """
    在文件头部添加默认的 source 语句
    
    Args:
        content: 脚本内容
        input_file: 输入文件路径
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称
        flow_name: 流程名称
        step_name: 步骤名称
        full_tcl_path: full.tcl 文件路径
        output_file: 输出文件路径
        search_paths: 搜索路径列表
        hooks_dir: hooks 目录路径
    
    Returns:
        添加了前置 source 语句的内容
    """
    try:
        package_loader = PackageLoader(edp_center_path)
        
        # 如果未提供完整信息，尝试从脚本路径推断
        path_info = None
        if not foundry or not node or not flow_name or project is None:
            path_info = package_loader.parse_script_path(input_file)
            if path_info:
                foundry = foundry or path_info.get('foundry')
                node = node or path_info.get('node')
                if project is None:
                    project = path_info.get('project')
                flow_name = flow_name or path_info.get('flow_name')
        
        # 如果还没有完整信息，使用之前推断的信息
        if not foundry or not node or not flow_name:
            if not path_info:
                path_info = package_loader.parse_script_path(input_file)
            if path_info:
                foundry = foundry or path_info.get('foundry')
                node = node or path_info.get('node')
                if project is None:
                    project = path_info.get('project')
                flow_name = flow_name or path_info.get('flow_name')
        
        # 检查必需参数：foundry 和 node 是必需的，flow_name 是可选的
        if not foundry or not node:
            logger.warning(
                f"Cannot generate default source statements: missing required parameters foundry or node "
                f"(foundry={foundry}, node={node}, flow_name={flow_name}). "
                f"Please ensure these parameters are provided, or the script path follows the standard format."
            )
            # 不抛出异常，继续处理（允许不使用默认 source 语句）
            default_sources = ""
        else:
            try:
                default_sources = package_loader.generate_default_sources(
                    foundry=foundry,
                    node=node,
                    project=project,
                    flow_name=flow_name,
                    include_sub_steps=False  # 不再从 packages 加载 sub_steps
                )
            except Exception as e:
                logger.warning(f"生成默认 source 语句时出错: {e}，继续处理")
                default_sources = ""
        
        # 准备在文件头部添加默认 source 语句（package 相关的）
        # 先收集所有要添加的内容
        prepend_content = default_sources if default_sources else ""
        
        # 如果提供了 full_tcl_path，在 package source 之后、namespace eval 之前添加 source full.tcl
        if full_tcl_path:
            full_tcl_path = Path(full_tcl_path).resolve()
            if full_tcl_path.exists():
                # 计算相对于输出文件的路径（如果提供了输出文件）
                if output_file:
                    output_file_path = Path(output_file).resolve()
                    try:
                        # 尝试计算相对路径
                        rel_path = full_tcl_path.relative_to(output_file_path.parent)
                        # 转换为 Tcl 兼容格式（Windows 路径使用正斜杠）
                        tcl_path = to_tcl_path(rel_path)
                        source_line = f"source {tcl_path}\n"
                    except ValueError:
                        # 如果无法计算相对路径，使用绝对路径
                        tcl_path = to_tcl_path(full_tcl_path)
                        source_line = f"source {tcl_path}\n"
                else:
                    # 如果没有输出文件，使用绝对路径
                    tcl_path = to_tcl_path(full_tcl_path)
                    source_line = f"source {tcl_path}\n"
                
                # 在 package source 之后添加 source full.tcl（在 namespace eval 之前）
                prepend_content = prepend_content + source_line
                logger.debug(f"已在 package source 语句之后添加 source full.tcl: {full_tcl_path}")
            else:
                logger.warning(f"full.tcl 文件不存在: {full_tcl_path}")
        
        # 生成 sub_steps 的 source 语句（从 dependency.yaml 读取，放在 proc 目录）
        # 注意：这会在 namespace eval 之后，所以 full.tcl 应该在它之前
        if step_name and flow_name:
            sub_steps_sources = generate_sub_steps_sources(
                edp_center_path, foundry, node, project, flow_name, step_name, input_file, search_paths, hooks_dir
            )
            if sub_steps_sources:
                prepend_content = prepend_content + sub_steps_sources
                logger.debug(f"已添加 sub_steps source 语句")
        
        # 在文件头部添加所有内容（package source + source full.tcl + sub_steps source）
        if prepend_content:
            content = prepend_content + content
            logger.debug(f"已在文件头部添加默认 source 语句")
    except Exception as e:
        # 非关键错误，记录警告但继续处理
        logger.warning(f"生成默认 source 语句失败: {e}，继续处理")
        # 不抛出异常，允许不使用默认 source 语句
    
    return content

