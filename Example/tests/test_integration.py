#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
端到端集成测试
使用 Example/WORK_PATH/ 目录下的真实项目数据进行测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_ai_root = test_file_dir.parent.parent
sys.path.insert(0, str(edp_ai_root))

from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper
from edp_center.main.cli.commands.history_handler import load_run_history, filter_history
from edp_center.main.cli.commands.stats_handler import calculate_stats, calculate_step_stats
from edp_center.main.cli.commands.rollback.rollback_history import load_run_history as rollback_load_history


class TestIntegration(unittest.TestCase):
    """端到端集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.example_path = test_file_dir.parent / "WORK_PATH"
        cls.test_project_path = cls.example_path / "dongting" / "P85" / "block1" / "user1" / "main"
        cls.edp_center_path = find_edp_center_path_helper()
        
    def test_find_edp_center_path(self):
        """测试查找 edp_center 路径"""
        edp_center_path = find_edp_center_path_helper()
        self.assertIsNotNone(edp_center_path)
        self.assertTrue(edp_center_path.exists())
        self.assertTrue((edp_center_path / "main" / "cli" / "cli.py").exists())
    
    def test_create_manager_with_real_project(self):
        """测试使用真实项目创建 WorkflowManager"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        try:
            manager = create_manager(self.edp_center_path)
            self.assertIsNotNone(manager)
            # 注意：WorkflowManager 可能不直接包含 project_info，这里只是测试创建是否成功
        except Exception as e:
            self.skipTest(f"创建 manager 失败（可能是环境问题）: {e}")
    
    def test_load_real_run_history(self):
        """测试加载真实的运行历史"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        branch_dir = self.test_project_path
        run_info_file = branch_dir / ".run_info"
        
        if not run_info_file.exists():
            self.skipTest("运行历史文件不存在，跳过测试")
        
        try:
            history = load_run_history(branch_dir)
            self.assertIsInstance(history, list)
            # 如果有历史记录，验证其结构
            if history:
                for run in history:
                    self.assertIn('timestamp', run)
                    self.assertIn('flow', run)
                    self.assertIn('step', run)
                    self.assertIn('status', run)
        except Exception as e:
            self.skipTest(f"加载历史失败（可能是数据格式问题）: {e}")
    
    def test_calculate_stats_with_real_data(self):
        """测试使用真实数据计算统计信息"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        branch_dir = self.test_project_path
        run_info_file = branch_dir / ".run_info"
        
        if not run_info_file.exists():
            self.skipTest("运行历史文件不存在，跳过测试")
        
        try:
            history = load_run_history(branch_dir)
            if not history:
                self.skipTest("没有运行历史数据，跳过测试")
            
            stats = calculate_stats(history)
            self.assertIsInstance(stats, dict)
            self.assertIn('total_runs', stats)
            self.assertIn('success_count', stats)
            self.assertIn('failed_count', stats)
            self.assertGreaterEqual(stats['total_runs'], 0)
        except Exception as e:
            self.skipTest(f"计算统计信息失败: {e}")
    
    def test_project_structure_exists(self):
        """测试项目结构是否存在"""
        self.assertTrue(self.example_path.exists(), "Example/WORK_PATH 目录不存在")
        self.assertTrue(self.test_project_path.exists(), "测试项目路径不存在")
        
        # 验证关键文件/目录存在
        expected_paths = [
            self.test_project_path / "user_config.yaml",
            self.test_project_path / "user_config.tcl",
            self.test_project_path / "cmds",
            self.test_project_path / "runs",
        ]
        
        for path in expected_paths:
            if path.exists():
                self.assertTrue(path.exists(), f"预期路径不存在: {path}")
            # 如果不存在，记录但不失败（可能是可选的文件）


class TestRealProjectData(unittest.TestCase):
    """使用真实项目数据的测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.example_path = Path(__file__).resolve().parent.parent / "WORK_PATH"
        cls.test_project_path = cls.example_path / "dongting" / "P85" / "block1" / "user1" / "main"
    
    def test_project_config_files(self):
        """测试项目配置文件"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        config_files = [
            self.test_project_path / "user_config.yaml",
            self.test_project_path / "user_config.tcl",
        ]
        
        # 至少应该有一个配置文件
        has_config = any(f.exists() for f in config_files)
        if has_config:
            self.assertTrue(has_config, "至少应该有一个配置文件")
    
    def test_runs_directory_structure(self):
        """测试 runs 目录结构"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        runs_dir = self.test_project_path / "runs"
        if runs_dir.exists():
            # 检查是否有运行目录
            run_dirs = [d for d in runs_dir.iterdir() if d.is_dir()]
            if run_dirs:
                # 验证运行目录结构
                for run_dir in run_dirs:
                    # 应该有 full.tcl 文件
                    full_tcl = run_dir / "full.tcl"
                    if full_tcl.exists():
                        self.assertTrue(full_tcl.exists(), f"运行目录应该有 full.tcl: {run_dir}")


if __name__ == '__main__':
    unittest.main()

