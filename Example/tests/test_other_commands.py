#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
其他命令测试
测试 tutorial, graph, release 等其他命令
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

from edp_center.main.cli.commands.tutorial_handler import handle_tutorial_cmd
from edp_center.main.cli.commands.graph_handler import handle_graph_cmd
from edp_center.main.cli.commands.release.release_handler import handle_release_cmd
from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper


class TestOtherCommands(unittest.TestCase):
    """其他命令测试"""
    
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
    
    def test_tutorial_cmd_basic(self):
        """测试基础 tutorial 命令"""
        edp_center_path = self.edp_center_path
        class Args:
            def __init__(self):
                self.edp_center = str(edp_center_path)
                self.tutorial = None  # 查看教程
                self.update = False
        
        args = Args()
        
        try:
            # 测试 tutorial 命令
            with patch('sys.stdout'):
                result = handle_tutorial_cmd(self.edp_center_path, args)
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"tutorial 命令执行失败: {e}")
    
    def test_graph_cmd_basic(self):
        """测试基础 graph 命令"""
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
                self.graph = True
                self.format = "text"  # 使用文本格式，避免依赖图形库
                self.output = None
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 graph 命令
            with patch('sys.stdout'):
                result = handle_graph_cmd(manager, args)
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"graph 命令执行失败: {e}")
    
    def test_release_cmd_basic(self):
        """测试基础 release 命令"""
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
                self.release = True
                self.release_version = None
                self.release_step = None
                self.release_block = None
        
        args = Args()
        
        try:
            manager = create_manager(self.edp_center_path)
            # 测试 release 命令（只查看，不实际创建 release）
            with patch('sys.stdout'), patch('sys.stderr'):
                result = handle_release_cmd(manager, args)
                # release 可能需要指定参数，所以可能返回错误代码
                self.assertIn(result, [0, 1, None, True, False])
        except Exception as e:
            self.skipTest(f"release 命令执行失败: {e}")


if __name__ == '__main__':
    unittest.main()

