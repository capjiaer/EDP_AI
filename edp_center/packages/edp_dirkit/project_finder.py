#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目查找和信息获取模块
"""

from pathlib import Path
from typing import List, Dict, Optional

# 导入框架异常类
from edp_center.packages.edp_common import ProjectNotFoundError


class ProjectFinder:
    """项目查找器"""
    
    def __init__(self, config_path: Path):
        """
        初始化 ProjectFinder
        
        Args:
            config_path: edp_center 的 config 目录路径
        """
        self.config_path = config_path
    
    def find_project(self, project_name: str) -> List[Dict[str, str]]:
        """
        根据项目名称查找所有匹配的 foundry/node 组合
        
        Args:
            project_name: 项目名称（如 dongting）
            
        Returns:
            包含 foundry 和 node 的字典列表
            例如: [{'foundry': 'SAMSUNG', 'node': 'S8'}, ...]
        """
        matches = []
        
        if not self.config_path.exists():
            return matches
        
        # 遍历 config 目录查找项目
        for foundry_dir in self.config_path.iterdir():
            if not foundry_dir.is_dir() or foundry_dir.name.startswith('.'):
                continue
            
            for node_dir in foundry_dir.iterdir():
                if not node_dir.is_dir() or node_dir.name.startswith('.'):
                    continue
                
                # 检查是否有该项目的配置目录
                project_dir = node_dir / project_name
                if project_dir.exists() and project_dir.is_dir():
                    matches.append({
                        'foundry': foundry_dir.name,
                        'node': node_dir.name,
                        'project': project_name
                    })
        
        return matches
    
    def get_project_info(self, project_name: str, 
                         foundry: Optional[str] = None,
                         node: Optional[str] = None) -> Dict[str, str]:
        """
        获取项目信息（foundry 和 node）
        
        Args:
            project_name: 项目名称
            foundry: 可选，如果指定则只在该 foundry 下查找
            node: 可选，如果指定则只在该 node 下查找
            
        Returns:
            包含 foundry 和 node 的字典
            
        Raises:
            ValueError: 如果找不到项目或找到多个匹配
        """
        matches = self.find_project(project_name)
        
        # 如果指定了 foundry，进行过滤
        if foundry:
            matches = [m for m in matches if m['foundry'] == foundry]
        
        # 如果指定了 node，进行过滤
        if node:
            matches = [m for m in matches if m['node'] == node]
        
        if len(matches) == 0:
            # 获取所有可用项目（用于错误提示）
            available_projects = self.list_projects()
            
            # 使用框架异常类
            raise ProjectNotFoundError(
                project_name=project_name,
                available_projects=available_projects,
                foundry=foundry,
                node=node,
                config_path=str(self.config_path)
            )
        elif len(matches) == 1:
            return matches[0]
        else:
            # 多个匹配，提供详细信息
            match_info = "\n".join([f"  - {m['foundry']}/{m['node']}" for m in matches])
            # 使用框架异常类，但保留原有的详细错误信息
            raise ProjectNotFoundError(
                f"找到多个匹配的项目 '{project_name}'，请指定 foundry 和/或 node:\n{match_info}",
                context={
                    'project_name': project_name,
                    'matches': matches,
                    'foundry': foundry,
                    'node': node
                },
                suggestion=f"请使用以下格式指定:\n  - foundry={matches[0]['foundry']}, node={matches[0]['node']}"
            )
    
    def list_projects(self, foundry: Optional[str] = None, 
                     node: Optional[str] = None) -> List[Dict[str, str]]:
        """
        列出所有可用的项目
        
        Args:
            foundry: 可选，过滤指定的 foundry
            node: 可选，过滤指定的 node
            
        Returns:
            项目信息列表，每个包含 foundry, node, project
        """
        projects = []
        
        if not self.config_path.exists():
            return projects
        
        # 遍历 config 目录
        for foundry_dir in self.config_path.iterdir():
            if not foundry_dir.is_dir() or foundry_dir.name.startswith('.'):
                continue
            
            if foundry and foundry_dir.name != foundry:
                continue
            
            for node_dir in foundry_dir.iterdir():
                if not node_dir.is_dir() or node_dir.name.startswith('.'):
                    continue
                
                if node and node_dir.name != node:
                    continue
                
                # 查找项目目录（排除 common 项目）
                for item in node_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        # 跳过 common 项目（common 是特殊项目，不应该出现在项目列表中）
                        if item.name == 'common':
                            continue
                        projects.append({
                            'foundry': foundry_dir.name,
                            'node': node_dir.name,
                            'project': item.name
                        })
        
        return sorted(projects, key=lambda x: (x['foundry'], x['node'], x['project']))

