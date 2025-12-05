#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Version Info Manager - 版本信息管理模块
"""

from pathlib import Path
from typing import Dict, List
import datetime
import yaml
from getpass import getuser


class VersionInfoManager:
    """版本信息管理器"""
    
    def __init__(self, project_path: Path):
        """
        初始化版本信息管理器
        
        Args:
            project_path: 项目路径
        """
        self.project_path = project_path
        self.version_info_file = project_path / '.edp_version'
    
    def create_or_update_version_info(self, project_name: str, project_node: str,
                                      foundry: str, node: str, blocks: List[str]) -> None:
        """
        创建或更新版本信息文件
        
        Args:
            project_name: 项目名称
            project_node: 项目节点名称
            foundry: 代工厂名称
            node: 工艺节点名称
            blocks: 块名称列表
        """
        current_time = datetime.datetime.now().isoformat()
        current_user = getuser()
        
        if not self.version_info_file.exists():
            # 首次创建，记录基本信息
            version_info = {
                'project': project_name,
                'version': project_node,  # 项目版本名称（如 P85）
                'foundry': foundry,
                'node': node,
                'created_at': current_time,
                'created_by': current_user,
                'init_version': '1.0',  # 初始化文件格式版本号，用于未来兼容性
                'blocks': {}  # 记录 blocks 和 users 信息
            }
        else:
            # 读取现有文件，更新信息
            try:
                with open(self.version_info_file, 'r', encoding='utf-8') as f:
                    version_info = yaml.safe_load(f) or {}
                if 'blocks' not in version_info:
                    version_info['blocks'] = {}
                # 清理旧键：迁移逻辑
                # 1. 如果存在旧的 'version' 键且值为 '1.0'（可能是文件格式版本号），迁移到 'init_version'
                if 'version' in version_info and version_info['version'] == '1.0' and 'init_version' not in version_info:
                    version_info['init_version'] = version_info.pop('version')
                # 2. 如果存在 project_node，迁移到 version（如果 version 不存在或值为 '1.0'）
                if 'project_node' in version_info:
                    if 'version' not in version_info or version_info['version'] == '1.0':
                        version_info['version'] = version_info.pop('project_node')
                    else:
                        # 如果 version 已存在且不是 '1.0'，只删除 project_node
                        del version_info['project_node']
                # 3. 确保 version 存在（项目版本名称）
                if 'version' not in version_info:
                    version_info['version'] = project_node
                # 4. 确保 init_version 存在（初始化文件格式版本号）
                if 'init_version' not in version_info:
                    version_info['init_version'] = '1.0'
            except Exception:
                # 如果读取失败，重新创建
                version_info = {
                    'project': project_name,
                    'version': project_node,  # 项目版本名称（如 P85）
                    'foundry': foundry,
                    'node': node,
                    'created_at': current_time,
                    'created_by': current_user,
                    'init_version': '1.0',  # 初始化文件格式版本号，用于未来兼容性
                    'blocks': {}
                }
        
        # 记录本次初始化的 blocks
        for block_name in blocks:
            if block_name not in version_info['blocks']:
                version_info['blocks'][block_name] = {
                    'created_at': current_time,
                    'created_by': current_user,
                    'users': {}
                }
        
        # 保存更新后的文件
        try:
            with open(self.version_info_file, 'w', encoding='utf-8') as f:
                yaml.dump(version_info, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except Exception as e:
            # 如果写入失败，不影响主流程
            pass

