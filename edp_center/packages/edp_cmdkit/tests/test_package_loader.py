#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 package_loader 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.package_loader import PackageLoader


class TestPackageLoader(unittest.TestCase):
    """测试 PackageLoader 类"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 edp_center 结构
        self.edp_center = self.temp_path / "edp_center"
        self.edp_center.mkdir()
        
        # 创建 config 和 flow 目录
        self.config_path = self.edp_center / "config"
        self.config_path.mkdir()
        
        self.flow_path = self.edp_center / "flow"
        self.flow_path.mkdir()
        
        # 创建 PackageLoader 实例
        self.loader = PackageLoader(self.edp_center)

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        loader = PackageLoader(self.edp_center)
        self.assertEqual(loader.edp_center, self.edp_center)
        self.assertEqual(loader.flow_path, self.edp_center / "flow")
        self.assertEqual(loader.config_path, self.edp_center / "config")

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
            PackageLoader(invalid_path)

    def test_find_project_info_single_match(self):
        """测试查找单个匹配的项目"""
        # 创建项目结构
        project_dir = self.config_path / "FOUNDRY" / "NODE" / "project1"
        project_dir.mkdir(parents=True)
        
        result = self.loader.find_project_info("project1")
        self.assertIsNotNone(result)
        self.assertEqual(result['foundry'], 'FOUNDRY')
        self.assertEqual(result['node'], 'NODE')
        self.assertEqual(result['project'], 'project1')

    def test_find_project_info_multiple_matches(self):
        """测试查找多个匹配的项目（应该返回第一个）"""
        # 创建多个项目结构
        project1_dir = self.config_path / "FOUNDRY1" / "NODE1" / "project1"
        project1_dir.mkdir(parents=True)
        
        project2_dir = self.config_path / "FOUNDRY2" / "NODE2" / "project1"
        project2_dir.mkdir(parents=True)
        
        result = self.loader.find_project_info("project1")
        self.assertIsNotNone(result)
        # 应该返回第一个匹配的
        self.assertIn(result['foundry'], ['FOUNDRY1', 'FOUNDRY2'])

    def test_find_project_info_not_found(self):
        """测试找不到项目的情况"""
        result = self.loader.find_project_info("nonexistent")
        self.assertIsNone(result)

    def test_parse_script_path_common(self):
        """测试解析 common 脚本路径"""
        # 创建脚本路径
        script_path = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE" / "common" / "cmds" / "flow1" / "step1.tcl"
        script_path.parent.mkdir(parents=True)
        script_path.write_text("# script")
        
        result = self.loader.parse_script_path(script_path)
        self.assertIsNotNone(result)
        self.assertEqual(result['foundry'], 'FOUNDRY')
        self.assertEqual(result['node'], 'NODE')
        self.assertIsNone(result.get('project'))  # common 没有 project
        self.assertEqual(result['flow_name'], 'flow1')

    def test_parse_script_path_project(self):
        """测试解析项目脚本路径"""
        # 创建脚本路径
        script_path = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE" / "project1" / "cmds" / "flow1" / "step1.tcl"
        script_path.parent.mkdir(parents=True)
        script_path.write_text("# script")
        
        result = self.loader.parse_script_path(script_path)
        self.assertIsNotNone(result)
        self.assertEqual(result['foundry'], 'FOUNDRY')
        self.assertEqual(result['node'], 'NODE')
        self.assertEqual(result['project'], 'project1')
        self.assertEqual(result['flow_name'], 'flow1')

    def test_parse_script_path_invalid(self):
        """测试解析无效路径"""
        # 创建不在 flow/initialize 下的路径
        invalid_path = self.temp_path / "some" / "path" / "script.tcl"
        invalid_path.parent.mkdir(parents=True)
        invalid_path.write_text("# script")
        
        result = self.loader.parse_script_path(invalid_path)
        self.assertIsNone(result)

    def test_get_util_search_paths(self):
        """测试获取 util 搜索路径"""
        # 创建脚本路径
        script_path = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE" / "common" / "cmds" / "flow1" / "step1.tcl"
        script_path.parent.mkdir(parents=True)
        script_path.write_text("# script")
        
        # 创建 util 目录
        util_dir = self.edp_center / "flow" / "initialize" / "FOUNDRY" / "NODE" / "common" / "cmds" / "flow1" / "util"
        util_dir.mkdir(parents=True)
        
        search_paths = self.loader.get_util_search_paths(script_path)
        self.assertIsNotNone(search_paths)
        self.assertGreater(len(search_paths), 0)
        # 应该包含 util 目录
        self.assertTrue(any('util' in str(p) for p in search_paths))


if __name__ == '__main__':
    unittest.main()

