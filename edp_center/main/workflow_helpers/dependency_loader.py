#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
依赖文件加载辅助模块
提供 dependency.yaml 文件查找和加载功能
"""

from pathlib import Path
from typing import List, Optional


def get_all_dependency_files(edp_center: Path,
                            foundry: str,
                            node: str,
                            project: str,
                            flow: Optional[str] = None) -> List[Path]:
    """
    获取所有 flow 的 dependency.yaml 文件路径
    
    加载所有 flow 的 dependency.yaml，这样跨 flow 的依赖关系会通过文件匹配自动建立。
    
    Args:
        edp_center: edp_center 资源库路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称
        flow: 流程名称（可选，如果为 None，则加载所有 flow）
        
    Returns:
        dependency.yaml 文件路径列表（按优先级排序：common 优先，然后 project）
    """
    dependency_files = []
    
    config_base = edp_center / "config" / foundry / node
    
    # 确定要加载的 flow 列表
    flows_to_load = []
    if flow:
        # 如果指定了 flow，只加载该 flow
        flows_to_load = [flow]
    else:
        # 如果没有指定 flow，加载所有 flow
        # 从 common 和 project 目录中收集所有 flow
        common_dir = config_base / "common"
        project_dir = config_base / project
        
        flow_set = set()
        if common_dir.exists():
            for item in common_dir.iterdir():
                if item.is_dir() and item.name != "main":
                    flow_set.add(item.name)
        if project_dir.exists():
            for item in project_dir.iterdir():
                if item.is_dir() and item.name != "main":
                    flow_set.add(item.name)
        
        flows_to_load = sorted(flow_set)
    
    # 按优先级加载每个 flow 的 dependency.yaml
    # 优先级：common 优先，project 其次（project 的配置会覆盖 common 的）
    for flow_name in flows_to_load:
        # 1. common/{flow}/dependency.yaml
        common_flow_dep = config_base / "common" / flow_name / "dependency.yaml"
        if common_flow_dep.exists():
            dependency_files.append(common_flow_dep)
        
        # 2. {project}/{flow}/dependency.yaml
        project_flow_dep = config_base / project / flow_name / "dependency.yaml"
        if project_flow_dep.exists():
            dependency_files.append(project_flow_dep)
    
    return dependency_files

