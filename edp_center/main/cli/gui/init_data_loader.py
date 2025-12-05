#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init Data Loader - 初始化数据加载器

负责加载项目列表、从配置文件推断参数等数据操作。
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import yaml

from ...workflow_manager import WorkflowManager
from ..init import load_config_file
from ..utils import infer_project_info


class InitDataLoader:
    """初始化数据加载器"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None):
        self.manager = manager
    
    def load_project_list(self, edp_center_path: Optional[Path] = None) -> List[Tuple[str, str, str, str]]:
        """
        加载所有项目列表（使用现有的 list_projects 方法）
        
        Args:
            edp_center_path: EDP Center 路径
            
        Returns:
            项目列表，格式：[(display_text, project, foundry, node), ...]
        """
        # 确定 edp_center_path
        if not edp_center_path:
            if self.manager and hasattr(self.manager, 'edp_center'):
                edp_center_path = self.manager.edp_center
            else:
                return []
        
        if not edp_center_path or not edp_center_path.exists():
            return []
        
        # 使用现有的 WorkPathInitializer 来获取项目列表
        try:
            # 使用绝对导入（与其他文件保持一致）
            from edp_center.packages.edp_dirkit.work_path import WorkPathInitializer
            initializer = WorkPathInitializer(edp_center_path)
            projects = initializer.list_projects()
            
            # 转换为需要的格式
            project_items = []
            for proj_info in projects:
                project_name = proj_info['project']
                foundry = proj_info['foundry']
                node = proj_info['node']
                display_text = f"{project_name} ({foundry}/{node})"
                project_items.append((display_text, project_name, foundry, node))
            
            # 按项目名称排序
            project_items.sort(key=lambda x: (x[1], x[2], x[3]))
            return project_items
            
        except Exception as e:
            # 打印错误信息以便调试
            import traceback
            print(f"[ERROR] 加载项目列表失败: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            # 如果使用现有方法失败，返回空列表
            return []
    
    def parse_project_display_text(self, display_text: str, 
                                   project_data: Dict[str, Tuple[str, str, str]]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        解析项目显示文本，获取 project、foundry、node
        
        Args:
            display_text: 显示文本（格式：project (foundry/node)）
            project_data: 项目数据字典 {display_text: (project, foundry, node)}
            
        Returns:
            (project, foundry, node) 元组
        """
        if not display_text or display_text not in project_data:
            return None, None, None
        return project_data[display_text]
    
    def load_from_config_file(self, work_path: Path) -> Optional[Dict]:
        """
        从配置文件加载参数
        
        Args:
            work_path: 工作路径
            
        Returns:
            配置字典，如果加载失败返回 None
        """
        try:
            config = load_config_file(work_path, None)
            return config
        except Exception as e:
            return None
    
    def infer_from_version_file(self, work_path: Path) -> Optional[Dict]:
        """
        从 .edp_version 文件推断参数
        
        Args:
            work_path: 工作路径
            
        Returns:
            版本信息字典，如果加载失败返回 None
        """
        version_file = work_path / '.edp_version'
        if not version_file.exists():
            return None
        
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = yaml.safe_load(f) or {}
            return version_info
        except Exception as e:
            return None
    
    def infer_from_path(self, work_path: Path) -> Optional[Dict]:
        """
        从路径推断项目信息
        
        Args:
            work_path: 工作路径
            
        Returns:
            项目信息字典，如果推断失败返回 None
        """
        try:
            # 创建一个简单的 args 对象
            class Args:
                pass
            args = Args()
            project_info = infer_project_info(self.manager, work_path, args)
            return project_info
        except Exception as e:
            return None
    
    def find_matching_project(self, project_name: str, 
                              project_data: Dict[str, Tuple[str, str, str]]) -> Optional[str]:
        """
        在项目数据中查找匹配的项目显示文本
        
        Args:
            project_name: 项目名称
            project_data: 项目数据字典 {display_text: (project, foundry, node)}
            
        Returns:
            匹配的显示文本，如果未找到返回 None
        """
        for display_text in project_data.keys():
            if display_text.startswith(f"{project_name} ("):
                return display_text
        return None

