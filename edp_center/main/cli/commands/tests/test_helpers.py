#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试辅助函数和工具
提供测试中常用的工具函数和 fixtures
"""

import sys
import os
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Dict, Optional
from unittest.mock import MagicMock

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_center_root = test_file_dir.parent.parent.parent.parent
sys.path.insert(0, str(edp_center_root))

from main.workflow_manager import WorkflowManager
from main.cli.command_router import create_manager, find_edp_center_path


class TestArgs:
    """测试用的参数对象"""
    def __init__(self, **kwargs):
        # 设置默认值
        defaults = {
            'edp_center': None,
            'work_path': None,
            'project': None,
            'version': None,
            'block': None,
            'user': None,
            'branch': None,
            'foundry': None,
            'node': None,
            'run': None,
            'run_from': None,
            'run_to': None,
            'run_from_step': 'all',
            'dry_run': False,
            'debug': False,
            'release': False,
            'release_version': None,
            'release_step': None,
            'release_block': None,
            'info': None,
            'history': None,
            'stats': None,
            'rollback': False,
            'rollback_dry_run': False,
            'rollback_index': None,
            'rollback_compare_indices': None,
            'rollback_compare_branch': None,
            'validate': False,
            'graph': False,
            'graph_format': 'text',
            'tutorial': False,
            'tutorial_update': False,
            'tutorial_force': False,
            'tutorial_browser': None,
            'view': False,
            'gui': False,
            'no_prepend_sources': False,
            'config': None,
            'input': None,
            'output': None,
            'flow': None,
            'from_branch_step': None,
            'append': False,
            'overwrite': False,
            'strict': False,
            'workflow_web': False,
        }
        
        # 合并用户提供的参数
        defaults.update(kwargs)
        for key, value in defaults.items():
            setattr(self, key, value)


def create_test_project_structure(base_path: Path, project: str, version: str, 
                                  block: str, user: str, branch: str) -> Path:
    """
    创建测试用的项目目录结构
    
    Args:
        base_path: 基础路径
        project: 项目名称
        version: 版本
        block: 块名称
        user: 用户名
        branch: 分支名称
        
    Returns:
        branch 目录路径
    """
    branch_dir = base_path / project / version / block / user / branch
    branch_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建基本目录结构
    (branch_dir / 'cmds').mkdir(exist_ok=True)
    (branch_dir / 'hooks').mkdir(exist_ok=True)
    (branch_dir / 'runs').mkdir(exist_ok=True)
    (branch_dir / 'logs').mkdir(exist_ok=True)
    (branch_dir / 'data').mkdir(exist_ok=True)
    
    return branch_dir


def create_test_run_info(branch_dir: Path, runs: list) -> None:
    """
    创建测试用的 .run_info 文件
    
    Args:
        branch_dir: branch 目录
        runs: 运行记录列表
    """
    run_info_file = branch_dir / '.run_info'
    data = {'runs': runs}
    with open(run_info_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def create_test_manager(edp_center_path: Optional[Path] = None) -> WorkflowManager:
    """
    创建测试用的 WorkflowManager
    
    Args:
        edp_center_path: edp_center 路径，如果为 None 则自动查找
        
    Returns:
        WorkflowManager 实例
    """
    if edp_center_path is None:
        # 自动查找 edp_center 路径
        current_file = Path(__file__).resolve()
        edp_center_root = current_file.parent.parent.parent.parent.parent
        edp_center_path = edp_center_root
    
    return create_manager(edp_center_path)


def create_test_args(**kwargs) -> TestArgs:
    """
    创建测试用的参数对象
    
    Args:
        **kwargs: 参数键值对
        
    Returns:
        TestArgs 实例
    """
    return TestArgs(**kwargs)


class TestFixture:
    """测试 Fixture 类，提供完整的测试环境"""
    
    def __init__(self, edp_center_path: Optional[Path] = None):
        """
        初始化测试 Fixture
        
        Args:
            edp_center_path: edp_center 路径，如果为 None 则自动查找
        """
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp(prefix='edp_test_')
        self.test_path = Path(self.test_dir)
        
        # 查找或设置 edp_center 路径
        if edp_center_path is None:
            current_file = Path(__file__).resolve()
            edp_center_root = current_file.parent.parent.parent.parent.parent
            self.edp_center_path = edp_center_root
        else:
            self.edp_center_path = edp_center_path
        
        # 设置工作路径
        self.work_path = self.test_path / 'work'
        self.work_path.mkdir(parents=True, exist_ok=True)
        
        # 默认项目信息
        self.project = 'test_project'
        self.version = 'P85'
        self.block = 'block1'
        self.user = 'test_user'
        self.branch = 'test_branch'
        self.foundry = 'SAMSUNG'
        self.node = 'S8'
        
        # 创建项目结构
        self.branch_dir = create_test_project_structure(
            self.work_path, self.project, self.version,
            self.block, self.user, self.branch
        )
        
        # 创建 WorkflowManager
        self.manager = create_test_manager(self.edp_center_path)
    
    def create_args(self, **kwargs) -> TestArgs:
        """
        创建测试用的参数对象（使用默认值）
        
        Args:
            **kwargs: 覆盖默认值的参数
            
        Returns:
            TestArgs 实例
        """
        defaults = {
            'edp_center': str(self.edp_center_path),
            'work_path': str(self.work_path),
            'project': self.project,
            'version': self.version,
            'block': self.block,
            'user': self.user,
            'branch': self.branch,
            'foundry': self.foundry,
            'node': self.node,
        }
        defaults.update(kwargs)
        return create_test_args(**defaults)
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

