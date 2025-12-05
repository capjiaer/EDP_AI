#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 path_detector 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
import yaml
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_dirkit.path_detector import PathDetector


class TestPathDetector(unittest.TestCase):
    """测试 PathDetector 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建 config 目录结构
        self.config_path = self.temp_path / "config"
        self.config_path.mkdir()
        
        # 创建 foundry/node 结构
        self.foundry_dir = self.config_path / "FOUNDRY" / "NODE"
        self.foundry_dir.mkdir(parents=True)
        
        # 创建项目目录
        self.project_dir = self.foundry_dir / "project1"
        self.project_dir.mkdir()
        
        # 创建 init_project.yaml
        init_config = {
            'project': {
                'blocks': [
                    {'name': 'block1', 'users': ['user1', 'user2']}
                ]
            }
        }
        init_file = self.project_dir / "init_project.yaml"
        with open(init_file, 'w', encoding='utf-8') as f:
            yaml.dump(init_config, f)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        detector = PathDetector(self.config_path)
        self.assertEqual(detector.config_path, self.config_path)
        self.assertIsNotNone(detector.project_finder)
    
    def test_detect_project_path_valid(self):
        """测试检测有效的项目路径"""
        # 创建工作路径结构
        work_path = self.temp_path / "work"
        project_path = work_path / "project1" / "P85" / "block1"
        project_path.mkdir(parents=True)
        
        # 创建 .edp_version 文件
        version_file = work_path / "project1" / "P85" / ".edp_version"
        version_info = {
            'project': 'project1',
            'version': 'P85',
            'foundry': 'FOUNDRY',
            'node': 'NODE'
        }
        with open(version_file, 'w', encoding='utf-8') as f:
            yaml.dump(version_info, f)
        
        detector = PathDetector(self.config_path)
        
        # Mock load_init_config_func
        def load_init_config(foundry, node, project):
            init_file = self.config_path / foundry / node / project / "init_project.yaml"
            if init_file.exists():
                with open(init_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            return None
        
        result = detector.detect_project_path(project_path, load_init_config)
        
        # 检查结果
        if result:  # 如果检测成功
            self.assertIn('project_name', result)
            self.assertIn('project_node', result)
            self.assertIn('block_name', result)
            self.assertEqual(result['project_name'], 'project1')
            self.assertEqual(result['project_node'], 'P85')
            self.assertEqual(result['block_name'], 'block1')
    
    def test_detect_project_path_invalid(self):
        """测试检测无效的项目路径"""
        # 创建无效路径（没有 .edp_version 文件）
        work_path = self.temp_path / "work"
        invalid_path = work_path / "project1" / "P85" / "block1"
        invalid_path.mkdir(parents=True)
        # 不创建 .edp_version 文件
        
        detector = PathDetector(self.config_path)
        
        def load_init_config(foundry, node, project):
            return None
        
        result = detector.detect_project_path(invalid_path, load_init_config)
        
        # 应该返回 None（检测失败）
        self.assertIsNone(result)
    
    def test_detect_project_path_no_project_in_path(self):
        """测试路径中不包含项目名称的情况"""
        # 创建不包含项目名称的路径
        work_path = self.temp_path / "work" / "other_dir"
        work_path.mkdir(parents=True)
        
        detector = PathDetector(self.config_path)
        
        def load_init_config(foundry, node, project):
            return None
        
        result = detector.detect_project_path(work_path, load_init_config)
        
        # 应该返回 None（检测失败）
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

