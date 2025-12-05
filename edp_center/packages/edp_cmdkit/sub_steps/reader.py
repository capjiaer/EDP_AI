#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sub Steps Reader - 读取 sub_steps 配置
"""

from pathlib import Path
from typing import List, Optional
import logging
import yaml

logger = logging.getLogger(__name__)


def read_sub_steps_from_dependency(edp_center_path: Path, foundry: str, node: str,
                                    project: Optional[str], flow_name: str, step_name: str) -> List[dict]:
    """
    从 dependency.yaml 文件中读取指定 step 的 sub_steps
    
    sub_steps 格式：字典 {file_name: proc_name}
    - 如果 sub_steps 是字典，转换为列表中的字典格式 [{file_name: proc_name}, ...]
    - 如果 sub_steps 是列表，直接返回
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        step_name: 步骤名称
    
    Returns:
        sub_steps 列表（每个元素是字典 {file_name: proc_name}），如果未找到则返回空列表
    """
    sub_steps = []
    config_path = edp_center_path / 'config' / foundry / node
    
    # 搜索路径：项目特定和 common（按优先级从低到高）
    search_paths = []
    
    # 1. common 路径（优先级低）
    common_path = config_path / 'common'
    if common_path.exists():
        search_paths.append(common_path)
    
    # 2. 项目特定路径（优先级高，会覆盖 common）
    if project:
        project_path = config_path / project
        if project_path.exists():
            search_paths.append(project_path)
    
    # 从高优先级到低优先级查找（项目特定的会覆盖 common）
    for config_dir in reversed(search_paths):
        flow_dir = config_dir / flow_name
        dependency_file = flow_dir / 'dependency.yaml'
        
        if not dependency_file.exists():
            continue
        
        try:
            with open(dependency_file, 'r', encoding='utf-8') as f:
                dependency_config = yaml.safe_load(f) or {}
            
            if flow_name not in dependency_config:
                continue
            
            flow_config = dependency_config[flow_name]
            if 'dependency' not in flow_config:
                continue
            
            dependency = flow_config['dependency']
            
            # 递归查找 step_name 并提取 sub_steps
            def find_step_recursive(data):
                """递归查找 step_name 并提取 sub_steps"""
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == step_name and isinstance(value, dict):
                            # 找到目标 step，提取 sub_steps
                            if 'sub_steps' in value:
                                return value['sub_steps']
                        # 继续递归查找
                        result = find_step_recursive(value)
                        if result is not None:
                            return result
                elif isinstance(data, list):
                    for item in data:
                        result = find_step_recursive(item)
                        if result is not None:
                            return result
                return None
            
            found_sub_steps = find_step_recursive(dependency)
            if found_sub_steps:
                # 如果 sub_steps 是字典（格式：{file_name: proc_name}），转换为列表
                if isinstance(found_sub_steps, dict):
                    # 字典格式：{file_name: proc_name}，转换为列表中的字典格式
                    sub_steps = [{k: v} for k, v in found_sub_steps.items()]
                elif isinstance(found_sub_steps, list):
                    # 列表格式（每个元素应该是字典）
                    sub_steps = found_sub_steps
                else:
                    logger.warning(f"sub_steps 格式错误，应该是字典或列表: {found_sub_steps}")
                    sub_steps = []
                break  # 找到后停止搜索（项目特定的会覆盖 common）
        
        except yaml.YAMLError as e:
            # YAML 解析错误，使用框架异常
            logger.warning(f"读取 dependency.yaml 失败: {e}")
            # 记录错误但继续查找其他路径
            continue
        except Exception as e:
            # 其他异常，记录但继续
            logger.warning(f"读取 dependency.yaml 时发生错误: {e}")
            continue
    
    return sub_steps

