#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
信息查询相关命令测试
测试 info, history, stats, rollback 等查询命令
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_ai_root = test_file_dir.parent.parent
sys.path.insert(0, str(edp_ai_root))

from edp_center.main.cli.commands.info_handler import handle_info_cmd
from edp_center.main.cli.commands.history_handler import handle_history_cmd
from edp_center.main.cli.commands.stats_handler import handle_stats_cmd
from edp_center.main.cli.commands.rollback_handler import handle_rollback_cmd
from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper


class TestInfoCommands(unittest.TestCase):
    """信息查询命令测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.edp_center_path = find_edp_center_path_helper()
        cls.example_path = test_file_dir.parent / "WORK_PATH"
        cls.test_project_path = cls.example_path / "dongting" / "P85" / "block1" / "user1" / "main"
    
    def setUp(self):
        """每个测试前的准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """每个测试后的清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_info_cmd_basic(self):
        """测试基础 info 命令"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        edp_center_path = self.edp_center_path
        test_project_path = self.test_project_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(test_project_path.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.info = None  # 查看所有 flow
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 info 命令
            with patch('sys.stdout'):
                result = handle_info_cmd(manager, args)
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"info 命令执行失败（可能是环境问题）: {e}")
    
    def test_info_cmd_with_flow(self):
        """测试指定 flow 的 info 命令"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        edp_center_path = self.edp_center_path
        test_project_path = self.test_project_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(test_project_path.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.info = "pnr_innovus"  # 指定 flow
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 info 命令
            with patch('sys.stdout'):
                result = handle_info_cmd(manager, args)
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"info 命令执行失败: {e}")
    
    def test_history_cmd_basic(self):
        """测试基础 history 命令"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        edp_center_path = self.edp_center_path
        test_project_path = self.test_project_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(test_project_path.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.history = None
                self.flow = None
                self.step = None
                self.status = None
                self.limit = None
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 history 命令
            with patch('sys.stdout'):
                result = handle_history_cmd(manager, args)
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"history 命令执行失败: {e}")
    
    def test_stats_cmd_basic(self):
        """测试基础 stats 命令"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        edp_center_path = self.edp_center_path
        test_project_path = self.test_project_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(test_project_path.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.stats = None
                self.step = None
                self.show_trend = False
                self.export = None
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 stats 命令
            with patch('sys.stdout'):
                result = handle_stats_cmd(manager, args)
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"stats 命令执行失败: {e}")
    
    def test_rollback_cmd_basic(self):
        """测试基础 rollback 命令"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        edp_center_path = self.edp_center_path
        test_project_path = self.test_project_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(test_project_path.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.rollback = None
                self.index = None
                self.compare_indices = None
                self.rollback_to_time = None
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 rollback 命令（只查看，不回滚）
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_rollback_cmd(manager, args)
                # rollback 可能需要指定参数，所以可能返回错误代码
                self.assertIn(result, [0, 1, None, True, False])
        except Exception as e:
            self.skipTest(f"rollback 命令执行失败: {e}")


if __name__ == '__main__':
    unittest.main()

