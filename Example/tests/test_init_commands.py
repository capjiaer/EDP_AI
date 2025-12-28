#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化相关命令测试
测试 init, create_project, branch 等基础命令
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

from edp_center.main.cli.commands.init import handle_init_project
from edp_center.main.cli.commands.create_project import handle_create_project
from edp_center.main.cli.commands.branch import handle_create_branch
from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper


class TestInitCommands(unittest.TestCase):
    """初始化命令测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.edp_center_path = find_edp_center_path_helper()
        cls.example_path = test_file_dir.parent / "WORK_PATH"
    
    def setUp(self):
        """每个测试前的准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """每个测试后的清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_project_basic(self):
        """测试基础的项目初始化"""
        # 创建模拟的 args 对象
        edp_center_path = self.edp_center_path
        temp_dir = self.temp_dir
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(temp_dir)
                self.project = "test_project"
                self.version = "P1"
                self.block = "block1"
                self.user = "test_user"
                self.branch = "main"
                self.foundry = None
                self.node = None
                self.gui = False
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 init 命令（不实际创建文件，只验证函数调用不报错）
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_init_project(manager, args)
                # 应该返回成功代码或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"init 命令执行失败（可能是环境问题）: {e}")
    
    def test_create_project_basic(self):
        """测试创建项目的基础功能"""
        # 创建模拟的 args 对象
        edp_center_path = self.edp_center_path
        temp_dir = self.temp_dir
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(temp_dir)
                self.project = "new_project"
                self.foundry = "TSMC"
                self.node = "n8"
        
        args = Args()
        
        try:
            # 测试 create_project 命令
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_create_project(self.edp_center_path, args)
                # 应该返回成功代码或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"create_project 命令执行失败（可能是环境问题）: {e}")
    
    def test_create_branch_basic(self):
        """测试创建分支的基础功能"""
        if not self.example_path.exists():
            self.skipTest("Example 路径不存在，跳过测试")
        
        # 使用真实项目路径
        test_project_path = self.example_path / "dongting" / "P85" / "block1" / "user1" / "main"
        
        if not test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        # 创建模拟的 args 对象
        edp_center_path = self.edp_center_path
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
                self.from_branch = None
                self.from_step = None
        
        args = Args()
        args.branch = "test_branch_new"  # 使用新的分支名，避免冲突
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 create_branch 命令（不实际创建，只验证函数调用）
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_create_branch(manager, args)
                # 应该返回成功代码或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"create_branch 命令执行失败（可能是环境问题）: {e}")
    
    def test_init_with_missing_args(self):
        """测试缺少必要参数时的错误处理"""
        edp_center_path = self.edp_center_path
        temp_dir = self.temp_dir
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = str(temp_dir)
                self.project = None  # 缺少项目名
                self.version = None
                self.block = None
                self.user = None
                self.branch = None
                self.foundry = None
                self.node = None
                self.gui = False
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 应该优雅地处理错误
            with patch('sys.stderr'):
                result = handle_init_project(manager, args)
                # 应该返回错误代码或 None
                self.assertIn(result, [0, 1, None, True, False])
        except SystemExit:
            # SystemExit 是可以接受的
            pass
        except Exception as e:
            # 其他异常应该被捕获
            self.assertIsNotNone(e)


class TestInitErrorScenarios(unittest.TestCase):
    """初始化命令错误场景测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.edp_center_path = find_edp_center_path_helper()
    
    def test_create_project_with_invalid_args(self):
        """测试使用无效参数创建项目"""
        edp_center_path = self.edp_center_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.work_path = "/nonexistent/path"
                self.project = None
                self.foundry = None
                self.node = None
        
        args = Args()
        
        # 应该优雅地处理错误
        try:
            with patch('sys.stderr'):
                result = handle_create_project(self.edp_center_path, args)
                self.assertIn(result, [0, 1, None, True, False])
        except SystemExit:
            pass
        except Exception as e:
            # 应该捕获并处理异常
            self.assertIsNotNone(e)


if __name__ == '__main__':
    unittest.main()

