#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 initializer 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_dirkit.initializer import ProjectInitializer


class TestProjectInitializer(unittest.TestCase):
    """测试 ProjectInitializer 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 edp_center 目录结构
        self.edp_center = self.temp_path / "edp_center"
        self.edp_center.mkdir()
        
        # 创建 config 目录结构
        self.config_dir = self.edp_center / "config" / "FOUNDRY" / "NODE" / "project1"
        self.config_dir.mkdir(parents=True)
        
        # 创建 flow 目录结构
        self.flow_dir = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE"
        self.flow_dir.mkdir(parents=True)
        
        # 创建 common 目录
        self.common_dir = self.flow_dir / "common" / "cmds" / "test_flow"
        self.common_dir.mkdir(parents=True)
        
        # 创建项目目录
        self.project_dir = self.flow_dir / "project1" / "cmds" / "test_flow"
        self.project_dir.mkdir(parents=True)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        initializer = ProjectInitializer(str(self.edp_center))
        self.assertEqual(initializer.edp_center, self.edp_center)
        self.assertEqual(initializer.config_path, self.edp_center / "config")
        self.assertEqual(initializer.flow_path, self.edp_center / "flow")
    
    def test_init_with_invalid_path(self):
        """测试使用无效路径初始化"""
        invalid_path = self.temp_path / "nonexistent"
        
        # 注意：现在使用 EDPFileNotFoundError，但为了向后兼容，也接受 FileNotFoundError
        try:
            from edp_center.packages.edp_common import EDPFileNotFoundError
            expected_exception = EDPFileNotFoundError
        except ImportError:
            expected_exception = FileNotFoundError
        
        with self.assertRaises(expected_exception):
            ProjectInitializer(str(invalid_path))
    
    def test_init_project_basic(self):
        """测试基本项目初始化"""
        # 创建一些测试文件
        test_file = self.common_dir / "test.tcl"
        test_file.write_text("puts \"test\"")
        
        initializer = ProjectInitializer(str(self.edp_center))
        project_dir = self.temp_path / "test_project"
        project_dir.mkdir()
        
        created_paths = initializer.init_project(
            project_dir,
            "FOUNDRY",
            "NODE",
            "project1",
            link_mode=False,
            flows=["test_flow"]
        )
        
        # 检查创建的目录
        self.assertIn('config', created_paths)
        self.assertIn('flow', created_paths)
        self.assertIn('cmds', created_paths)
        self.assertIn('packages', created_paths)
        
        # 检查目录是否存在
        self.assertTrue((project_dir / "config").exists())
        self.assertTrue((project_dir / "flow").exists())
        self.assertTrue((project_dir / "flow" / "cmds").exists())
    
    def test_init_project_with_link_mode(self):
        """测试使用链接模式初始化项目"""
        # 创建一些测试文件
        test_file = self.common_dir / "test.tcl"
        test_file.write_text("puts \"test\"")
        
        initializer = ProjectInitializer(str(self.edp_center))
        project_dir = self.temp_path / "test_project_link"
        project_dir.mkdir()
        
        # 注意：在 Windows 上符号链接可能需要管理员权限
        # 这里只测试函数调用，不验证链接是否实际创建
        try:
            created_paths = initializer.init_project(
                project_dir,
                "FOUNDRY",
                "NODE",
                "project1",
                link_mode=True,
                flows=["test_flow"]
            )
            
            # 检查创建的目录
            self.assertIn('config', created_paths)
            self.assertIn('flow', created_paths)
        except (OSError, NotImplementedError):
            # 如果符号链接创建失败（Windows 权限问题等），跳过测试
            self.skipTest("符号链接创建失败，可能是权限问题")


if __name__ == '__main__':
    unittest.main()

