#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径检测模块
"""

from pathlib import Path
from typing import Optional, Dict
from .project_finder import ProjectFinder


class PathDetector:
    """路径检测器"""
    
    def __init__(self, config_path: Path):
        """
        初始化 PathDetector
        
        Args:
            config_path: edp_center 的 config 目录路径
        """
        self.config_path = config_path
        self.project_finder = ProjectFinder(config_path)
    
    def detect_project_path(self, path: Path, 
                           load_init_config_func) -> Optional[Dict[str, str]]:
        """
        从当前路径检测项目信息（改进版：更简单、更严格）
        
        检测逻辑：
        1. 获取所有已知的项目名称
        2. 在路径中查找项目名称
        3. 如果找到，验证路径结构是否符合 {project}/{project_node}/{block}
        4. 验证 init_project.yaml 配置是否匹配
        
        Args:
            path: 要检测的路径
            load_init_config_func: 加载 init_project 配置的函数
            
        Returns:
            包含项目信息的字典，如果检测失败返回 None
            {
                'work_path': WORK_PATH 根目录,
                'project_name': 项目名称,
                'project_node': 项目节点,
                'block_name': 块名称,
                'foundry': foundry,
                'node': node,
                'path': block 的完整路径
            }
        """
        # 1. 获取所有已知的项目名称及其信息
        all_projects = self.project_finder.list_projects()
        
        if not all_projects:
            return None
        
        # 2. 在路径中查找项目名称
        path_parts = path.parts
        
        for project_info in all_projects:
            project_name = project_info['project']
            
            # 在路径中查找项目名称
            if project_name in path_parts:
                # 找到项目名称在路径中的位置
                project_idx = path_parts.index(project_name)
                
                # 检查是否有足够的层数：{project}/{project_node}/{block}
                if project_idx + 3 <= len(path_parts):
                    possible_project = path_parts[project_idx]
                    possible_project_node = path_parts[project_idx + 1]
                    possible_block = path_parts[project_idx + 2]
                    
                    # 构建 work_path（项目名称之前的所有部分）
                    if project_idx > 0:
                        possible_work_path = Path(*path_parts[:project_idx])
                    else:
                        possible_work_path = Path(path_parts[0])
                    
                    # 确保 work_path 是绝对路径
                    if not possible_work_path.is_absolute():
                        possible_work_path = possible_work_path.resolve()
                    else:
                        possible_work_path = possible_work_path.resolve()
                    
                    # 验证路径是否存在且是目录
                    block_path = possible_work_path / possible_project / possible_project_node / possible_block
                    if not (block_path.exists() and block_path.is_dir()):
                        continue
                    
                    # 验证 project_node 目录下是否存在 .edp_version 隐藏文件
                    # 这是最可靠的验证方式：如果存在这个文件，说明这个目录确实是 project_node 目录
                    # 如果没有这个文件，一律视为非法，跳过这个候选
                    project_node_path = possible_work_path / possible_project / possible_project_node
                    version_info_file = project_node_path / '.edp_version'
                    if not version_info_file.exists():
                        # 如果没有 .edp_version 文件，不是合法的 project_node 目录
                        continue
                    
                    # 3. 读取 init_project.yaml 配置进行验证（可选）
                    foundry = project_info['foundry']
                    node = project_info['node']
                    
                    try:
                        init_config = load_init_config_func(foundry, node, project_name)
                        
                        # 验证 work_path（如果有配置）
                        if init_config and 'project' in init_config:
                            config_work_path = init_config['project'].get('work_path_name')
                            if config_work_path:
                                # 检查 work_path 的最后一部分是否匹配
                                if possible_work_path.name != config_work_path:
                                    continue
                        
                        # 所有验证通过，直接返回第一个匹配的结果
                        return {
                            'work_path': str(possible_work_path),
                            'project_name': possible_project,
                            'project_node': possible_project_node,
                            'block_name': possible_block,
                            'foundry': foundry,
                            'node': node,
                            'path': str(block_path)
                        }
                    except Exception:
                        # 验证失败，继续查找下一个项目
                        continue
        
        return None

