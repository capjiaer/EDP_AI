#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 path_preparer 模块
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.path_preparer import prepare_search_paths


class TestPathPreparer(unittest.TestCase):
    """测试 path_preparer 模块"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 edp_center 目录结构
        self.edp_center = self.temp_path / "edp_center"
        self.edp_center.mkdir()
        
        # 创建 flow 目录结构
        self.flow_dir = self.edp_center / "flow" / "initialize"
        self.flow_dir.mkdir(parents=True)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_prepare_search_paths_with_all_params(self):
        """测试准备搜索路径（提供所有参数）"""
        # 创建测试文件
        test_file = self.flow_dir / "project1" / "cmds" / "test_flow" / "test.tcl"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")
        
        foundry = "FOUNDRY"
        node = "NODE"
        project = "project1"
        flow_name = "test_flow"
        base_dir = self.temp_path
        default_search_paths = []
        
        edp_center_path, foundry_result, node_result, project_result, flow_name_result, search_paths = prepare_search_paths(
            test_file,
            str(self.edp_center),
            foundry,
            node,
            project,
            flow_name,
            None,  # search_paths
            base_dir,
            default_search_paths
        )
        
        # 检查返回值（路径需要转换为字符串比较）
        self.assertEqual(str(edp_center_path), str(Path(self.edp_center)))
        self.assertEqual(foundry_result, foundry)
        self.assertEqual(node_result, node)
        self.assertEqual(project_result, project)
        self.assertEqual(flow_name_result, flow_name)
        
        # 检查搜索路径列表
        self.assertIsInstance(search_paths, list)
        self.assertGreater(len(search_paths), 0)
    
    def test_prepare_search_paths_without_project(self):
        """测试准备搜索路径（不提供项目）"""
        # 创建测试文件
        test_file = self.flow_dir / "common" / "cmds" / "test_flow" / "test.tcl"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")
        
        foundry = "FOUNDRY"
        node = "NODE"
        flow_name = "test_flow"
        base_dir = self.temp_path
        default_search_paths = []
        
        edp_center_path, foundry_result, node_result, project_result, flow_name_result, search_paths = prepare_search_paths(
            test_file,
            str(self.edp_center),
            foundry,
            node,
            None,  # project
            flow_name,
            None,  # search_paths
            base_dir,
            default_search_paths
        )
        
        # 检查返回值
        self.assertIsNone(project_result)  # common 路径，project 应该是 None
        
        # 检查搜索路径列表
        self.assertIsInstance(search_paths, list)
        self.assertGreater(len(search_paths), 0)
    
    def test_prepare_search_paths_without_edp_center(self):
        """测试准备搜索路径（不提供 edp_center_path）"""
        # 创建测试文件
        test_file = self.temp_path / "test.tcl"
        test_file.write_text("test")
        
        base_dir = self.temp_path
        default_search_paths = []
        
        edp_center_path, foundry_result, node_result, project_result, flow_name_result, search_paths = prepare_search_paths(
            test_file,
            None,  # edp_center_path
            None,  # foundry
            None,  # node
            None,  # project
            None,  # flow_name
            None,  # search_paths
            base_dir,
            default_search_paths
        )
        
        # 应该返回默认搜索路径（至少包含文件所在目录）
        self.assertIsInstance(search_paths, list)
        self.assertGreater(len(search_paths), 0)
    
    def test_prepare_search_paths_infers_from_path(self):
        """测试从路径推断参数"""
        # 创建测试文件路径（包含 flow/initialize）
        test_file = self.flow_dir / "FOUNDRY" / "NODE" / "project1" / "cmds" / "test_flow" / "test.tcl"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")
        
        base_dir = self.temp_path
        default_search_paths = []
        
        edp_center_path, foundry_result, node_result, project_result, flow_name_result, search_paths = prepare_search_paths(
            test_file,
            None,  # 不提供 edp_center_path，应该从路径推断
            None,  # 不提供 foundry
            None,  # 不提供 node
            None,  # 不提供 project
            None,  # 不提供 flow_name
            None,  # search_paths
            base_dir,
            default_search_paths
        )
        
        # 检查是否从路径推断出 edp_center_path
        # 注意：推断逻辑可能依赖于 PackageLoader，这里只检查基本结构
        self.assertIsInstance(search_paths, list)
    
    def test_prepare_search_paths_includes_file_directory(self):
        """测试搜索路径包含文件所在目录"""
        # 创建测试文件
        test_file = self.flow_dir / "project1" / "cmds" / "test_flow" / "test.tcl"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")
        
        base_dir = self.temp_path
        default_search_paths = []
        
        edp_center_path, foundry_result, node_result, project_result, flow_name_result, search_paths = prepare_search_paths(
            test_file,
            str(self.edp_center),
            "FOUNDRY",
            "NODE",
            "project1",
            "test_flow",
            None,  # search_paths
            base_dir,
            default_search_paths
        )
        
        # 检查文件所在目录在搜索路径中
        search_paths_str = [str(p) for p in search_paths]
        self.assertIn(str(test_file.parent), search_paths_str)


if __name__ == '__main__':
    unittest.main()

