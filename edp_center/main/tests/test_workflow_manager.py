#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 workflow_manager 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_center.main.workflow_manager import WorkflowManager


class TestWorkflowManager(unittest.TestCase):
    """测试 WorkflowManager 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 edp_center 目录结构
        self.edp_center = self.temp_path / "edp_center"
        self.edp_center.mkdir()
        
        # 创建 config 目录
        self.config_dir = self.edp_center / "config"
        self.config_dir.mkdir()
        
        # 创建 flow 目录
        self.flow_dir = self.edp_center / "flow"
        self.flow_dir.mkdir()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_valid_path(self):
        """测试使用有效路径初始化 WorkflowManager"""
        manager = WorkflowManager(str(self.edp_center))
        self.assertEqual(manager.edp_center, self.edp_center)
        self.assertIsNotNone(manager.project_initializer)
        self.assertIsNotNone(manager.work_path_initializer)
        self.assertIsNotNone(manager.cmd_processor)
    
    def test_init_with_invalid_path(self):
        """测试使用无效路径初始化 WorkflowManager"""
        invalid_path = self.temp_path / "nonexistent"
        
        with self.assertRaises(FileNotFoundError):
            WorkflowManager(str(invalid_path))
    
    def test_workflow_manager_attributes(self):
        """测试 WorkflowManager 的属性"""
        manager = WorkflowManager(str(self.edp_center))
        
        # 检查所有必要的属性都存在
        self.assertTrue(hasattr(manager, 'project_initializer'))
        self.assertTrue(hasattr(manager, 'work_path_initializer'))
        self.assertTrue(hasattr(manager, 'cmd_processor'))


if __name__ == '__main__':
    unittest.main()

