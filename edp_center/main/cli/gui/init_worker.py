#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init Worker - 初始化工作线程

在后台线程中执行初始化操作，避免阻塞 GUI。
"""

from pathlib import Path
from typing import Dict
from PyQt5.QtCore import QThread, pyqtSignal

from ...workflow_manager import WorkflowManager
from ..init import (
    load_config_file,
    validate_init_permission,
    init_project_structure,
    create_user_directories,
)


class InitWorker(QThread):
    """初始化工作线程，避免阻塞 GUI"""
    
    finished = pyqtSignal(bool, str)  # (success, message)
    progress = pyqtSignal(str)  # progress message
    
    def __init__(self, manager: WorkflowManager, params: Dict):
        super().__init__()
        self.manager = manager
        self.params = params
    
    def run(self):
        """执行初始化操作"""
        try:
            work_path = Path(self.params['work_path'])
            project = self.params['project']
            version = self.params['version']
            foundry = self.params.get('foundry')
            node = self.params.get('node')
            
            # 从 GUI 表格获取 blocks 配置
            gui_blocks_config = self.params.get('blocks_config', {})
            
            # 加载配置文件
            config = load_config_file(work_path, None)
            file_blocks_config = config.get('project', {}).get('blocks', {}) if config else {}
            
            # 合并配置：GUI 配置优先
            if gui_blocks_config:
                blocks_to_init = gui_blocks_config
            else:
                # 如果没有 GUI 配置，使用文件配置
                blocks_to_init = {}
                if isinstance(file_blocks_config, dict):
                    for block_name, users in file_blocks_config.items():
                        if isinstance(users, list):
                            blocks_to_init[block_name] = users
                        elif isinstance(users, str):
                            blocks_to_init[block_name] = [u.strip() for u in users.split() if u.strip()]
                        else:
                            blocks_to_init[block_name] = [str(users)]
            
            if not blocks_to_init:
                self.finished.emit(False, "错误: 请至少配置一个 Block 和 User")
                return
            
            # 验证权限
            is_allowed, error_msg = validate_init_permission(
                work_path=work_path,
                project=project,
                foundry=foundry,
                node=node,
                manager=self.manager,
                config_yaml=config
            )
            if not is_allowed:
                self.finished.emit(False, f"不允许在此路径执行 init 操作: {error_msg}")
                return
            
            # 初始化项目结构
            new_blocks = []
            new_users = {}
            for blk_name, users in blocks_to_init.items():
                if not (work_path / project / version / blk_name).exists():
                    new_blocks.append(blk_name)
                new_users[blk_name] = users
            
            if new_blocks:
                self.progress.emit(f"正在初始化项目结构: {project}/{version}")
                init_project_structure(
                    self.manager, work_path, project, version, new_blocks, foundry, node
                )
            
            # 创建用户目录
            if new_users:
                self.progress.emit("正在创建用户目录...")
                initialized_count = create_user_directories(work_path, project, version, new_users)
                self.finished.emit(True, f"初始化成功！共创建了 {initialized_count} 个用户目录")
            else:
                self.finished.emit(True, "初始化完成（无需创建新目录）")
                
        except Exception as e:
            import traceback
            error_msg = f"初始化失败: {str(e)}\n{traceback.format_exc()}"
            self.finished.emit(False, error_msg)

