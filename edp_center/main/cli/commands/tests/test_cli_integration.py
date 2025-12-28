#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI 命令集成测试

端到端测试 CLI 命令，确保命令能够正确执行并产生预期结果。
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 调整路径以便导入模块
# 从 test 文件到 edp_center 根目录
test_file_dir = Path(__file__).resolve().parent
edp_center_root = test_file_dir.parent.parent.parent.parent
sys.path.insert(0, str(edp_center_root))

from main.cli.cli import main
from main.cli.arg_parser import create_parser
from main.cli.command_router import create_manager, find_edp_center_path
from main.workflow_manager import WorkflowManager


class TestCLIIntegration(unittest.TestCase):
    """CLI 命令集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp(prefix='edp_test_')
        self.test_path = Path(self.test_dir)
        
        # 查找 edp_center 路径
        current_file = Path(__file__).resolve()
        edp_center_root = current_file.parent.parent.parent.parent.parent
        self.edp_center_path = edp_center_root
        
        # 设置工作路径
        self.work_path = self.test_path / 'work'
        self.work_path.mkdir(parents=True, exist_ok=True)
        
        # 创建基本的项目结构（最小化）
        self.project = 'test_project'
        self.version = 'P85'
        self.block = 'block1'
        self.user = 'test_user'
        self.branch = 'test_branch'
        self.foundry = 'SAMSUNG'
        self.node = 'S8'
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时目录
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_test_args(self, **kwargs):
        """创建测试用的 args 对象"""
        class TestArgs:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # 默认参数
        defaults = {
            'edp_center': None,
            'work_path': str(self.work_path),
            'project': self.project,
            'version': self.version,
            'block': self.block,
            'user': self.user,
            'branch': self.branch,
            'foundry': self.foundry,
            'node': self.node,
            'from_branch_step': None,
            'run': None,
            'run_from': None,
            'run_to': None,
            'run_from_step': 'all',
            'dry_run': False,
            'debug': 0,
            'release': False,
            'release_version': None,
            'release_step': None,
            'release_block': None,
            'append': False,
            'overwrite': False,
            'strict': False,
            'workflow_web': False,
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
            'flow': None
        }
        
        # 合并用户提供的参数
        defaults.update(kwargs)
        return TestArgs(**defaults)
    
    def test_parser_creation(self):
        """测试参数解析器创建"""
        parser = create_parser()
        self.assertIsNotNone(parser)
        
        # 测试解析基本参数
        args = parser.parse_args(['-b', 'test_branch'])
        self.assertEqual(args.branch, 'test_branch')
    
    def test_find_edp_center_path(self):
        """测试 edp_center 路径查找"""
        from main.cli.command_router import find_edp_center_path
        
        args = self._create_test_args()
        edp_center_path = find_edp_center_path(args)
        
        # 应该能找到 edp_center 目录
        self.assertIsNotNone(edp_center_path)
        self.assertTrue(edp_center_path.exists())
        self.assertTrue((edp_center_path / 'packages').exists())
    
    def test_create_manager(self):
        """测试 WorkflowManager 创建"""
        args = self._create_test_args()
        edp_center_path = find_edp_center_path(args)
        manager = create_manager(edp_center_path)
        
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, WorkflowManager)
    
    @patch('main.cli.commands.init.handle_init_project')
    def test_branch_command(self, mock_handle):
        """测试 -branch 命令"""
        mock_handle.return_value = 0
        
        args = self._create_test_args(branch='test_branch')
        edp_center_path = find_edp_center_path(args)
        manager = create_manager(edp_center_path)
        
        # 测试参数解析
        parser = create_parser()
        parsed_args = parser.parse_args(['-b', 'test_branch'])
        self.assertEqual(parsed_args.branch, 'test_branch')
    
    def test_run_command(self):
        """测试 -run 命令参数解析"""
        parser = create_parser()
        
        # 测试参数解析
        parsed_args = parser.parse_args(['-run', 'pv_calibre.ipmerge'])
        self.assertEqual(parsed_args.run, 'pv_calibre.ipmerge')
    
    # 已移除 load-workflow 命令测试
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效参数
        parser = create_parser()
        
        # 应该能够处理无效参数而不崩溃
        with self.assertRaises(SystemExit):
            parser.parse_args(['--invalid-arg'])
    
    def test_common_args(self):
        """测试通用参数解析"""
        parser = create_parser()
        
        # 测试项目参数
        args = parser.parse_args(['-prj', 'test_project'])
        self.assertEqual(args.project, 'test_project')
        
        # 测试版本参数
        args = parser.parse_args(['-v', 'P85'])
        self.assertEqual(args.version, 'P85')
        
        # 测试 foundry 和 node
        args = parser.parse_args(['--foundry', 'SAMSUNG', '--node', 'S8'])
        self.assertEqual(args.foundry, 'SAMSUNG')
        self.assertEqual(args.node, 'S8')


if __name__ == '__main__':
    unittest.main()

