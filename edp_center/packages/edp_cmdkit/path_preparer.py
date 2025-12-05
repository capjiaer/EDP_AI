#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径准备模块
负责准备搜索路径和推断路径信息（foundry/node/project/flow_name）
"""

from pathlib import Path
from typing import List, Optional, Union, Tuple
import logging
from .package_loader import PackageLoader

logger = logging.getLogger(__name__)


def prepare_search_paths(
    input_file: Path,
    edp_center_path: Optional[Union[str, Path]],
    foundry: Optional[str],
    node: Optional[str],
    project: Optional[str],
    flow_name: Optional[str],
    search_paths: Optional[List[Union[str, Path]]],
    base_dir: Path,
    default_search_paths: List[Path]
) -> Tuple[Optional[Path], Optional[str], Optional[str], Optional[str], Optional[str], List[Path]]:
    """
    准备搜索路径和推断路径信息
    
    Args:
        input_file: 输入文件路径
        edp_center_path: edp_center 路径（可选）
        foundry: 代工厂名称（可选）
        node: 工艺节点（可选）
        project: 项目名称（可选）
        flow_name: 流程名称（可选）
        search_paths: 搜索路径列表（可选）
        base_dir: 基础目录
        default_search_paths: 默认搜索路径列表
    
    Returns:
        (edp_center_path, foundry, node, project, flow_name, search_paths)
    """
    # 如果未提供 edp_center_path，尝试从脚本路径自动推断
    # 方法：以 flow/initialize 为分割点，前面的部分就是 edp_center 的绝对路径
    if not edp_center_path:
        path_str = str(input_file).replace('\\', '/')
        split_pattern = '/flow/initialize/'
        if split_pattern in path_str:
            # 分割路径
            parts = path_str.split(split_pattern)
            if len(parts) == 2:
                edp_center_path = Path(parts[0])
                if edp_center_path.exists() and (edp_center_path / 'flow').exists():
                    logger.info(f"自动推断 edp_center_path: {edp_center_path}")
                else:
                    edp_center_path = None
    
    # 如果提供了 edp_center_path（或自动推断的），先处理路径推断和 util 搜索路径
    if edp_center_path:
        try:
            package_loader = PackageLoader(edp_center_path)
            
            # 如果未提供完整信息，尝试从脚本路径推断
            # parse_script_path 会返回包含 _edp_center_path 的字典（如果能够解析）
            path_info = None
            if not foundry or not node or not flow_name or project is None:
                path_info = package_loader.parse_script_path(input_file)
                if path_info:
                    foundry = foundry or path_info.get('foundry')
                    node = node or path_info.get('node')
                    # project 可能是 None（common 的情况），所以只有当明确找到时才使用
                    if project is None:
                        project = path_info.get('project')
                    flow_name = flow_name or path_info.get('flow_name')
                    logger.debug(
                        f"从脚本路径推断: foundry={foundry}, node={node}, "
                        f"project={project}, flow_name={flow_name}"
                    )
            
            # 自动获取 util 搜索路径
            util_paths = package_loader.get_util_search_paths(input_file)
            if util_paths:
                # 将 util 路径添加到搜索路径的最前面（优先级最高）
                if search_paths is None:
                    search_paths = []
                # 将 util 路径添加到最前面，但避免重复
                for util_path in reversed(util_paths):
                    if util_path not in search_paths:
                        search_paths.insert(0, util_path)
                logger.debug(f"自动添加 util 搜索路径: {[str(p) for p in util_paths]}")
        except Exception as e:
            # 非关键错误，记录警告但继续处理
            logger.warning(f"处理 edp_center 路径失败: {e}，继续处理")
            # 不抛出异常，允许使用默认搜索路径
    
    # 确定搜索路径
    if search_paths is None:
        # 使用默认搜索路径：文件所在目录、默认搜索路径、base_dir
        resolved_paths = []
        resolved_paths.append(input_file.parent)
        if default_search_paths:
            resolved_paths.extend(default_search_paths)
        if base_dir not in resolved_paths:
            resolved_paths.append(base_dir)
        search_paths = resolved_paths
    else:
        # 转换并解析路径
        resolved_paths = []
        for p in search_paths:
            resolved = Path(p).resolve()
            if resolved.exists() and resolved.is_dir():
                resolved_paths.append(resolved)
            else:
                logger.warning(f"搜索路径不存在或不是目录，将跳过: {p}")
        
        search_paths = resolved_paths
        
        # 文件所在目录不在搜索路径中时，添加到最前面作为后备
        if input_file.parent not in search_paths:
            search_paths.insert(0, input_file.parent)
    
    return edp_center_path, foundry, node, project, flow_name, search_paths

