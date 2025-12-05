#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 handlers.py 迁移后的错误处理功能

验证 @handle_cli_error 装饰器是否正常工作
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
sys.path.insert(0, project_root)

from edp_center.main.cli.commands.handlers import (
    handle_load_config,
    handle_process_script,
    handle_load_workflow,
    handle_run_workflow
)
from edp_center.packages.edp_common import EDPError, ConfigError


class TestHandlersMigration(unittest.TestCase):
    """测试 handlers.py 迁移后的错误处理"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟的 manager 和 args
        self.manager = Mock()
        self.args = Mock()
        
        # 设置默认的 args 属性
        self.args.project = 'test_project'
        self.args.foundry = 'SAMSUNG'
        self.args.node = 'S8'
        self.args.flow = 'pv_calibre'
        self.args.output = None
        self.args.input = None
        self.args.search_paths = None
        self.args.no_prepend_sources = False
        self.args.work_path = '/test/work'
        self.args.block = 'block1'
        self.args.user = 'user1'
        self.args.branch = 'main'
        self.args.version = None
        self.args.from_branch_step = None
    
    def test_handle_load_config_success(self):
        """测试 handle_load_config 成功情况"""
        # 模拟成功场景
        self.manager.work_path_initializer.get_project_info.return_value = {
            'foundry': 'SAMSUNG',
            'node': 'S8'
        }
        self.manager.load_config.return_value = {'test': 'config'}
        
        # 应该返回 0（成功）
        result = handle_load_config(self.manager, self.args)
        self.assertEqual(result, 0)
        
        # 验证调用了正确的方法
        self.manager.work_path_initializer.get_project_info.assert_called_once()
        self.manager.load_config.assert_called_once()
    
    def test_handle_load_config_error(self):
        """测试 handle_load_config 错误处理"""
        # 模拟错误场景
        self.manager.work_path_initializer.get_project_info.side_effect = Exception("测试错误")
        
        # 应该返回 1（失败），并且不会抛出异常
        with patch('sys.stderr'):
            result = handle_load_config(self.manager, self.args)
            self.assertEqual(result, 1)
    
    def test_handle_process_script_success(self):
        """测试 handle_process_script 成功情况"""
        # 模拟成功场景
        self.manager.process_script.return_value = "processed content"
        
        # 应该返回 0（成功）
        result = handle_process_script(self.manager, self.args)
        self.assertEqual(result, 0)
        
        # 验证调用了正确的方法
        self.manager.process_script.assert_called_once()
    
    def test_handle_process_script_error(self):
        """测试 handle_process_script 错误处理"""
        # 模拟错误场景
        self.manager.process_script.side_effect = Exception("处理失败")
        
        # 应该返回 1（失败），并且不会抛出异常
        with patch('sys.stderr'):
            result = handle_process_script(self.manager, self.args)
            self.assertEqual(result, 1)
    
    def test_handle_load_workflow_success(self):
        """测试 handle_load_workflow 成功情况"""
        # 模拟成功场景
        self.manager.work_path_initializer.get_project_info.return_value = {
            'foundry': 'SAMSUNG',
            'node': 'S8'
        }
        
        # 创建模拟的 graph 对象
        mock_graph = Mock()
        mock_graph.steps = {
            'step1': Mock(status='ready'),
            'step2': Mock(status='pending')
        }
        self.manager.load_workflow.return_value = mock_graph
        
        # 应该返回 0（成功）
        result = handle_load_workflow(self.manager, self.args)
        self.assertEqual(result, 0)
        
        # 验证调用了正确的方法
        self.manager.work_path_initializer.get_project_info.assert_called_once()
        self.manager.load_workflow.assert_called_once()
    
    def test_handle_load_workflow_error(self):
        """测试 handle_load_workflow 错误处理"""
        # 模拟错误场景
        self.manager.work_path_initializer.get_project_info.side_effect = Exception("加载失败")
        
        # 应该返回 1（失败），并且不会抛出异常
        with patch('sys.stderr'):
            result = handle_load_workflow(self.manager, self.args)
            self.assertEqual(result, 1)
    
    def test_handle_run_workflow_success(self):
        """测试 handle_run_workflow 成功情况"""
        # 模拟成功场景
        self.manager.run_full_workflow.return_value = {'result': 'success'}
        
        # 应该返回 0（成功）
        result = handle_run_workflow(self.manager, self.args)
        self.assertEqual(result, 0)
        
        # 验证调用了正确的方法
        self.manager.run_full_workflow.assert_called_once()
    
    def test_handle_run_workflow_error(self):
        """测试 handle_run_workflow 错误处理"""
        # 模拟错误场景
        self.manager.run_full_workflow.side_effect = Exception("执行失败")
        
        # 应该返回 1（失败），并且不会抛出异常
        with patch('sys.stderr'):
            result = handle_run_workflow(self.manager, self.args)
            self.assertEqual(result, 1)
    
    def test_handle_cli_error_with_edp_error(self):
        """测试装饰器处理 EDPError"""
        # 模拟抛出 EDPError
        self.manager.load_config.side_effect = ConfigError(
            message="配置错误",
            config_file="/test/config.yaml",
            suggestion="请检查配置文件"
        )
        
        # 应该返回 1（失败），并且不会抛出异常
        with patch('sys.stderr'):
            result = handle_load_config(self.manager, self.args)
            self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()

