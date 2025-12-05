#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 work_path_initializer 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_dirkit.work_path import WorkPathInitializer, get_current_user


class TestWorkPathInitializer(unittest.TestCase):
    """测试 WorkPathInitializer 类"""
    
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
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        initializer = WorkPathInitializer(str(self.edp_center))
        self.assertEqual(initializer.edp_center, self.edp_center)
        self.assertEqual(initializer.config_path, self.config_dir)
    
    def test_init_with_invalid_path(self):
        """测试使用无效路径初始化"""
        invalid_path = self.temp_path / "nonexistent"
        
        # 检查是否抛出异常
        try:
            from edp_center.packages.edp_common import EDPFileNotFoundError
            expected_exception = EDPFileNotFoundError
        except ImportError:
            expected_exception = FileNotFoundError
        
        with self.assertRaises(expected_exception):
            WorkPathInitializer(str(invalid_path))
    
    def test_get_current_user(self):
        """测试获取当前用户名"""
        user = get_current_user()
        self.assertIsInstance(user, str)
        self.assertGreater(len(user), 0)
        self.assertNotEqual(user, "")
    
    def test_list_projects(self):
        """测试列出所有项目"""
        # 创建项目配置目录
        project1_dir = self.config_dir / "FOUNDRY1" / "NODE1" / "project1"
        project1_dir.mkdir(parents=True)
        
        project2_dir = self.config_dir / "FOUNDRY2" / "NODE2" / "project2"
        project2_dir.mkdir(parents=True)
        
        initializer = WorkPathInitializer(str(self.edp_center))
        projects = initializer.list_projects()
        
        # 检查项目列表
        self.assertIsInstance(projects, list)
        self.assertGreater(len(projects), 0)
        # 检查项目格式（应该是字典格式，包含 foundry, node, project）
        for project in projects:
            self.assertIsInstance(project, dict)
            self.assertIn('project', project)
            self.assertIn('foundry', project)
            self.assertIn('node', project)


if __name__ == '__main__':
    unittest.main()

