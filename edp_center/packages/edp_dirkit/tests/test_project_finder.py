#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 ProjectFinder 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_dirkit.project_finder import ProjectFinder


class TestProjectFinder(unittest.TestCase):
    """测试 ProjectFinder 类"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 config 目录结构
        self.config_path = self.temp_path / "config"
        self.config_path.mkdir()
        
        # 创建 foundry/node 结构
        self.foundry1 = self.config_path / "FOUNDRY1"
        self.foundry1.mkdir()
        self.node1 = self.foundry1 / "NODE1"
        self.node1.mkdir()
        self.node2 = self.foundry1 / "NODE2"
        self.node2.mkdir()
        
        self.foundry2 = self.config_path / "FOUNDRY2"
        self.foundry2.mkdir()
        self.node3 = self.foundry2 / "NODE3"
        self.node3.mkdir()
        
        # 创建项目目录
        self.project1_dir = self.node1 / "project1"
        self.project1_dir.mkdir()
        
        self.project2_dir = self.node1 / "project2"
        self.project2_dir.mkdir()
        
        self.project1_dir2 = self.node2 / "project1"  # 同名项目在不同 node
        self.project1_dir2.mkdir()
        
        # 创建 ProjectFinder 实例
        self.finder = ProjectFinder(self.config_path)

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_find_project_single_match(self):
        """测试查找单个匹配的项目"""
        matches = self.finder.find_project("project2")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['foundry'], 'FOUNDRY1')
        self.assertEqual(matches[0]['node'], 'NODE1')
        self.assertEqual(matches[0]['project'], 'project2')

    def test_find_project_multiple_matches(self):
        """测试查找多个匹配的项目"""
        matches = self.finder.find_project("project1")
        self.assertEqual(len(matches), 2)
        # 应该包含两个 foundry/node 组合
        foundries_nodes = {(m['foundry'], m['node']) for m in matches}
        self.assertIn(('FOUNDRY1', 'NODE1'), foundries_nodes)
        self.assertIn(('FOUNDRY1', 'NODE2'), foundries_nodes)

    def test_find_project_not_found(self):
        """测试查找不存在的项目"""
        matches = self.finder.find_project("nonexistent")
        self.assertEqual(len(matches), 0)

    def test_get_project_info_single_match(self):
        """测试获取单个匹配的项目信息"""
        info = self.finder.get_project_info("project2")
        self.assertEqual(info['foundry'], 'FOUNDRY1')
        self.assertEqual(info['node'], 'NODE1')
        self.assertEqual(info['project'], 'project2')

    def test_get_project_info_with_foundry_node(self):
        """测试指定 foundry 和 node 获取项目信息"""
        info = self.finder.get_project_info("project1", foundry="FOUNDRY1", node="NODE1")
        self.assertEqual(info['foundry'], 'FOUNDRY1')
        self.assertEqual(info['node'], 'NODE1')

    def test_get_project_info_multiple_matches(self):
        """测试多个匹配时抛出异常"""
        # 可能抛出 ValueError 或 ProjectNotFoundError（框架异常）
        try:
            from edp_center.packages.edp_common import ProjectNotFoundError
            expected_exception = (ValueError, ProjectNotFoundError)
        except ImportError:
            expected_exception = ValueError
        
        with self.assertRaises(expected_exception) as context:
            self.finder.get_project_info("project1")
        
        error_msg = str(context.exception)
        self.assertIn("多个匹配", error_msg or "找到多个匹配")

    def test_get_project_info_not_found(self):
        """测试项目不存在时抛出异常"""
        # 可能抛出 ValueError 或 ProjectNotFoundError（框架异常）
        try:
            from edp_center.packages.edp_common import ProjectNotFoundError
            expected_exception = (ValueError, ProjectNotFoundError)
        except ImportError:
            expected_exception = ValueError
        
        with self.assertRaises(expected_exception) as context:
            self.finder.get_project_info("nonexistent")
        
        error_msg = str(context.exception)
        # 检查是否包含"找不到项目"或"找不到项目"（框架异常格式）
        self.assertTrue(
            "找不到项目" in error_msg or 
            "找不到" in error_msg or
            "nonexistent" in error_msg
        )

    def test_list_projects_all(self):
        """测试列出所有项目"""
        projects = self.finder.list_projects()
        self.assertEqual(len(projects), 3)  # project1 (2个), project2 (1个)
        
        # 检查是否包含所有项目
        project_names = {p['project'] for p in projects}
        self.assertIn('project1', project_names)
        self.assertIn('project2', project_names)

    def test_list_projects_with_foundry(self):
        """测试按 foundry 过滤"""
        projects = self.finder.list_projects(foundry="FOUNDRY1")
        self.assertEqual(len(projects), 3)  # 都在 FOUNDRY1 下
        
        for p in projects:
            self.assertEqual(p['foundry'], 'FOUNDRY1')

    def test_list_projects_with_node(self):
        """测试按 node 过滤"""
        projects = self.finder.list_projects(node="NODE1")
        self.assertEqual(len(projects), 2)  # project1 和 project2
        
        for p in projects:
            self.assertEqual(p['node'], 'NODE1')

    def test_list_projects_with_foundry_and_node(self):
        """测试同时按 foundry 和 node 过滤"""
        projects = self.finder.list_projects(foundry="FOUNDRY1", node="NODE1")
        self.assertEqual(len(projects), 2)
        
        for p in projects:
            self.assertEqual(p['foundry'], 'FOUNDRY1')
            self.assertEqual(p['node'], 'NODE1')


if __name__ == '__main__':
    unittest.main()

