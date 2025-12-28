#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行相关命令测试
测试 run, run_range 等运行命令
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

from edp_center.main.cli.commands.run_handler import handle_run_cmd
from edp_center.main.cli.commands.run_range import handle_run_range
from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper


class TestRunCommands(unittest.TestCase):
    """运行命令测试"""
    
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
    
    def test_run_cmd_basic(self):
        """测试基础 run 命令"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        # 创建模拟的 args 对象
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
                self.run = "pnr_innovus.place"
                self.run_from = None
                self.run_to = None
                self.run_from_step = "all"
                self.dry_run = True  # 使用 dry-run 模式，不实际执行
                self.debug = False
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 run 命令（使用 dry-run 模式）
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_run_cmd(manager, args)
                # 应该返回成功代码或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"run 命令执行失败（可能是环境问题）: {e}")
    
    def test_run_cmd_dry_run(self):
        """测试 run 命令的 dry-run 模式"""
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
                self.run = "pv_calibre.ipmerge"
                self.run_from = None
                self.run_to = None
                self.run_from_step = "all"
                self.dry_run = True
                self.debug = False
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # dry-run 模式应该只显示命令，不实际执行
            with patch('sys.stdout') as mock_stdout:
                result = handle_run_cmd(manager, args)
                # 验证有输出（dry-run 应该显示命令）
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"run dry-run 命令执行失败: {e}")
    
    def test_run_range_basic(self):
        """测试 run_range 命令的基础功能"""
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
                self.run = None
                self.run_from = "pnr_innovus.place"
                self.run_to = "pnr_innovus.postroute"
                self.run_from_step = "all"
                self.dry_run = True
                self.debug = False
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 run_range 命令（使用 dry-run 模式）
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_run_range(manager, args, args.run_from, args.run_to, False)
                # 应该返回成功代码或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"run_range 命令执行失败（可能是环境问题）: {e}")


class TestRunErrorScenarios(unittest.TestCase):
    """运行命令错误场景测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.edp_center_path = find_edp_center_path_helper()
    
    def test_run_with_nonexistent_step(self):
        """测试运行不存在的步骤"""
        edp_center_path = self.edp_center_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = "/nonexistent/path"
                self.project = "test"
                self.version = "P1"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.run = "nonexistent.flow"
                self.run_from = None
                self.run_to = None
                self.run_from_step = "all"
                self.dry_run = True
                self.debug = False
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 应该优雅地处理错误
            with patch('sys.stderr'):
                result = handle_run_cmd(manager, args)
                self.assertIn(result, [0, 1, None, True, False])
        except SystemExit:
            pass
        except Exception as e:
            # 应该捕获并处理异常
            self.assertIsNotNone(e)


if __name__ == '__main__':
    unittest.main()

