#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一的推断模块
整合所有推断逻辑，提供统一的推断接口

核心思路：
1. 从 edp_center 位置可以知道：有哪些 project，每个 project 隶属于什么 node 和 foundry
2. 从当前工作目录可以推断：project, version, block, user, branch 等信息
"""

from pathlib import Path
from typing import Optional, Dict, List, Tuple

from .inference.project_inference import (
    get_edp_center_path as _get_edp_center_path,
    list_projects_direct,
    infer_project_info as _infer_project_info_func
)
from .inference.path_inference import infer_work_path_info as _infer_work_path_info_func
from .inference.inference_validator import validate_work_path_info as _validate_work_path_info_func


class UnifiedInference:
    """统一的推断类"""
    
    def __init__(self, edp_center_path: Path):
        """
        初始化统一推断类
        
        Args:
            edp_center_path: edp_center 的路径
        """
        self.edp_center_path = Path(edp_center_path).resolve()
        self.config_path = self.edp_center_path / "config"
        
        # 初始化项目查找器
        try:
            from edp_center.packages.edp_dirkit import ProjectFinder
            self.project_finder = ProjectFinder(self.config_path)
        except ImportError:
            self.project_finder = None
    
    def get_edp_center_path(self, args) -> Optional[Path]:
        """
        获取 edp_center 路径
        
        优先级：
        1. 命令行参数 --edp-center
        2. 从当前目录向上查找 edp_center 目录
        3. 使用初始化时提供的 edp_center_path
        
        Args:
            args: 命令行参数对象
            
        Returns:
            edp_center 路径，如果找不到返回 None
        """
        return _get_edp_center_path(self.edp_center_path, args)
    
    def list_projects(self, foundry: Optional[str] = None, 
                     node: Optional[str] = None) -> List[Dict[str, str]]:
        """
        列出所有可用的项目
        
        从 edp_center/config 目录结构推断：
        - config/{foundry}/{node}/{project}/
        
        Args:
            foundry: 可选，过滤指定的 foundry
            node: 可选，过滤指定的 node
            
        Returns:
            项目信息列表，每个包含 foundry, node, project
        """
        if not self.project_finder:
            # 如果 project_finder 未初始化，尝试直接扫描目录
            return list_projects_direct(self.config_path, foundry=foundry, node=node)
        
        return self.project_finder.list_projects(foundry=foundry, node=node)
    
    def get_project_info(self, project_name: str, 
                         foundry: Optional[str] = None,
                         node: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        获取项目信息（foundry 和 node）
        
        从 edp_center/config 目录查找项目，返回其所属的 foundry 和 node
        
        Args:
            project_name: 项目名称
            foundry: 可选，如果指定则只在该 foundry 下查找
            node: 可选，如果指定则只在该 node 下查找
            
        Returns:
            包含 foundry 和 node 的字典，如果找不到返回 None
        """
        if not self.project_finder:
            return None
        
        try:
            return self.project_finder.get_project_info(project_name, foundry, node)
        except ValueError:
            return None
    
    def infer_project_info(self, current_dir: Path, args) -> Optional[Dict]:
        """
        推断项目信息（edp_center_path, foundry, node, project）
        
        逻辑：
        1. 获取 edp_center_path（从命令行参数或自动查找）
        2. 从 .edp_version 文件读取 foundry, node, project
        3. 从命令行参数读取 foundry, node, project
        4. 从路径结构推断 foundry, node（如果路径中包含 foundry 名称）
        5. 如果知道 project，从 edp_center/config 查找其所属的 foundry 和 node
        
        Args:
            current_dir: 当前工作目录
            args: 命令行参数对象
            
        Returns:
            包含项目信息的字典，如果无法推断则返回 None
            {
                'edp_center_path': Path,
                'foundry': str,
                'node': str,
                'project': Optional[str]  # 可能为 None（使用 common）
            }
        """
        return _infer_project_info_func(
            self.edp_center_path,
            self.config_path,
            self.project_finder,
            current_dir,
            args
        )
    
    def infer_work_path_info(self, current_dir: Path, args, 
                             project_info: Optional[Dict] = None) -> Optional[Dict]:
        """
        推断工作路径信息（work_path, project, version, block, user, branch）
        
        逻辑：
        1. 向上查找 .edp_version 文件（必须找到，否则返回 None）
        2. 找到后，.edp_version 所在的目录就是 version
        3. version 的父目录就是 project_name
        4. version 的父目录的父目录就是 work_path
        5. 从当前目录到 version 之间的路径部分就是 block/user/branch
        
        注意：此函数严格要求找到 .edp_version 文件，如果找不到，返回 None。
        
        Args:
            current_dir: 当前工作目录
            args: 命令行参数对象
            project_info: 可选，项目信息字典（包含 edp_center_path, foundry, node, project）
            
        Returns:
            包含工作路径信息的字典，如果无法推断（找不到 .edp_version）则返回 None
            {
                'work_path': Path,
                'project': str,
                'version': str,
                'block': Optional[str],
                'user': Optional[str],
                'branch': Optional[str]
            }
        """
        return _infer_work_path_info_func(current_dir, args, project_info)
    
    def infer_all_info(self, current_dir: Path, args) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        统一推断所有信息
        
        同时推断项目信息和工作路径信息
        
        Args:
            current_dir: 当前工作目录
            args: 命令行参数对象
            
        Returns:
            (project_info, work_path_info) 元组
            - project_info: 项目信息字典（edp_center_path, foundry, node, project）
            - work_path_info: 工作路径信息字典（work_path, project, version, block, user, branch）
        """
        # 推断项目信息
        project_info = self.infer_project_info(current_dir, args)
        
        # 推断工作路径信息
        work_path_info = self.infer_work_path_info(current_dir, args, project_info)
        
        return project_info, work_path_info
    
    def validate_work_path_info(self, work_path_info: Optional[Dict], 
                                required_fields: List[str] = None) -> Tuple[bool, List[str]]:
        """
        验证工作路径信息是否完整
        
        Args:
            work_path_info: 工作路径信息字典
            required_fields: 必需字段列表，默认为 ['work_path', 'project', 'version', 'block', 'user', 'branch']
            
        Returns:
            (is_complete, missing_fields) 元组
        """
        return _validate_work_path_info_func(work_path_info, required_fields)


def infer_project_info(manager, current_dir: Path, args) -> Optional[Dict]:
    """
    推断项目信息
    
    Args:
        manager: WorkflowManager 实例
        current_dir: 当前工作目录
        args: 命令行参数对象
        
    Returns:
        包含项目信息的字典，如果无法推断则返回 None
    """
    inference = UnifiedInference(manager.edp_center)
    return inference.infer_project_info(current_dir, args)


def infer_work_path_info(current_dir: Path, args, project_info: Dict) -> Optional[Dict]:
    """
    推断工作路径信息
    
    Args:
        current_dir: 当前工作目录
        args: 命令行参数对象
        project_info: 项目信息字典
        
    Returns:
        包含工作路径信息的字典，如果无法推断则返回 None
    """
    # 从 project_info 获取 edp_center_path
    edp_center_path = project_info.get('edp_center_path')
    if not edp_center_path:
        return None
    
    inference = UnifiedInference(edp_center_path)
    return inference.infer_work_path_info(current_dir, args, project_info)


def validate_work_path_info(work_path_info: Optional[Dict], 
                            required_fields: List[str] = None) -> Tuple[bool, List[str]]:
    """
    验证工作路径信息是否完整（独立函数，不依赖 UnifiedInference 实例）
    
    Args:
        work_path_info: 工作路径信息字典
        required_fields: 必需字段列表，默认为 ['work_path', 'project', 'version', 'block', 'user', 'branch']
        
    Returns:
        (is_complete, missing_fields) 元组
    """
    return _validate_work_path_info_func(work_path_info, required_fields)
