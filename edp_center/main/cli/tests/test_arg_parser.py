#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 arg_parser 模块
"""

import unittest
import sys
import os
import argparse

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from edp_center.main.cli.arg_parser.main import create_parser


class TestArgParser(unittest.TestCase):
    """测试 arg_parser 模块"""
    
    def setUp(self):
        """设置测试环境"""
        self.parser = create_parser()
    
    def test_parse_init_command(self):
        """测试解析 init 命令"""
        args = self.parser.parse_args([
            '-init',
            '--work-path', '/test/work',
            '--project', 'test_project',
            '--version', 'P85',
            '--block', 'block1',
            '--user', 'user1'
        ])
        
        self.assertTrue(args.init)
        self.assertEqual(args.work_path, '/test/work')
        self.assertEqual(args.project, 'test_project')
        self.assertEqual(args.version, 'P85')
        self.assertEqual(args.block, 'block1')
        self.assertEqual(args.user, 'user1')
    
    def test_parse_run_command(self):
        """测试解析 run 命令"""
        args = self.parser.parse_args([
            '-run', 'test_flow.test_step',
            '--work-path', '/test/work',
            '--project', 'test_project'
        ])
        
        self.assertEqual(args.run, 'test_flow.test_step')
        self.assertEqual(args.work_path, '/test/work')
        self.assertEqual(args.project, 'test_project')
    
    def test_parse_create_project_command(self):
        """测试解析 create_project 命令"""
        args = self.parser.parse_args([
            '-create_project', 'new_project', 'FOUNDRY', 'NODE'
        ])
        
        self.assertIsNotNone(args.create_project)
        self.assertEqual(args.create_project, ['new_project', 'FOUNDRY', 'NODE'])
    
    def test_parse_gui_flag(self):
        """测试解析 GUI 标志"""
        args = self.parser.parse_args([
            '-init',
            '--gui'
        ])
        
        self.assertTrue(args.gui)
    
    def test_parse_info_command(self):
        """测试解析 info 命令"""
        # info 命令可以不带参数（显示所有 flow）
        args = self.parser.parse_args(['-info'])
        self.assertIsNone(args.info)
        
        # info 命令可以带 flow 参数
        args = self.parser.parse_args(['-info', 'test_flow'])
        self.assertEqual(args.info, 'test_flow')


if __name__ == '__main__':
    unittest.main()

