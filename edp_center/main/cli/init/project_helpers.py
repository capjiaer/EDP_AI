#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init 项目相关的辅助函数
"""

import yaml
import datetime
from pathlib import Path
from typing import Optional, Dict
from getpass import getuser

from ..utils import set_user_directory_permissions


def init_project_structure(manager, work_path: Path, project: str, version: str, blocks: list, foundry: Optional[str], node: Optional[str]):
    """
    初始化项目结构（如果还没有）
    
    Args:
        manager: WorkflowManager 实例
        work_path: WORK_PATH 根目录
        project: 项目名称
        version: 项目版本名称
        blocks: 需要初始化的 blocks 列表
        foundry: 代工厂名称（可选）
        node: 工艺节点（可选）
    """
    project_base_path = work_path / project / version
    version_info_file = project_base_path / '.edp_version'
    
    # 确保 .edp_version 文件存在（即使 block 目录已存在）
    if not version_info_file.exists():
        # 如果文件不存在，调用 manager.init_project 创建它
        manager.init_project(
            work_path=str(work_path),
            project_name=project,
            version=version,
            blocks=blocks,  # 传入所有 blocks，让 manager.init_project 处理
            foundry=foundry,
            node=node
        )
        print(f"[OK] 项目结构初始化成功（已创建 .edp_version 文件）")
    else:
        # 如果文件已存在，只初始化不存在的 block 目录
        for blk in blocks:
            block_path = project_base_path / blk
            if not block_path.exists():
                manager.init_project(
                    work_path=str(work_path),
                    project_name=project,
                    version=version,
                    blocks=[blk],
                    foundry=foundry,
                    node=node
                )
                print(f"[OK] 项目结构初始化成功: {blk}")


def create_user_directories(work_path: Path, project: str, version: str, blocks_to_init: Dict[str, list]) -> int:
    """
    创建用户目录并设置权限
    
    Args:
        work_path: WORK_PATH 根目录
        project: 项目名称
        version: 项目版本名称
        blocks_to_init: {block_name: [user1, user2, ...]} 字典
        
    Returns:
        初始化的用户数量
    """
    initialized_count = 0
    current_time = datetime.datetime.now().isoformat()
    current_user = getuser()
    
    project_base_path = work_path / project / version
    version_info_file = project_base_path / '.edp_version'
    
    # 读取现有的 .edp_version 文件
    version_info = {}
    if version_info_file.exists():
        try:
            with open(version_info_file, 'r', encoding='utf-8') as f:
                version_info = yaml.safe_load(f) or {}
        except Exception:
            pass
    
    # 确保 blocks 结构存在
    if 'blocks' not in version_info:
        version_info['blocks'] = {}
    
    # 创建用户目录
    for blk_name, users in blocks_to_init.items():
        block_path = project_base_path / blk_name
        
        # 确保 block 记录存在
        if blk_name not in version_info['blocks']:
            version_info['blocks'][blk_name] = {
                'created_at': current_time,
                'created_by': current_user,
                'users': {}
            }
        
        # 确保 users 结构存在
        if 'users' not in version_info['blocks'][blk_name]:
            version_info['blocks'][blk_name]['users'] = {}
        
        for usr in users:
            user_path = block_path / usr
            user_path.mkdir(parents=True, exist_ok=True)
            
            # 记录 user 信息（如果不存在或需要更新）
            if usr not in version_info['blocks'][blk_name]['users']:
                version_info['blocks'][blk_name]['users'][usr] = {
                    'created_at': current_time,
                    'created_by': current_user
                }
            
            # 设置目录权限，确保只有对应的用户可以访问
            if set_user_directory_permissions(user_path, usr):
                print(f"[OK] 初始化成功（已设置权限）: {project}/{version}/{blk_name}/{usr}")
            else:
                print(f"[OK] 初始化成功: {project}/{version}/{blk_name}/{usr}")
            
            initialized_count += 1
    
    # 保存更新后的 .edp_version 文件（如果文件不存在，也要创建它）
    # 如果文件不存在，需要创建基本结构
    if not version_info_file.exists():
        # 从 config 或其他地方获取 foundry 和 node（如果可能）
        # 这里先创建基本结构，foundry 和 node 可以在后续更新
        version_info.setdefault('project', project)
        version_info.setdefault('version', version)
        version_info.setdefault('init_version', '1.0')
        if 'created_at' not in version_info:
            version_info['created_at'] = current_time
        if 'created_by' not in version_info:
            version_info['created_by'] = current_user
    
    # 保存文件（无论是否存在）
    try:
        with open(version_info_file, 'w', encoding='utf-8') as f:
            yaml.dump(version_info, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception:
        # 如果写入失败，不影响主流程
        pass
    
    return initialized_count

