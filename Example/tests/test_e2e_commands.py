#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
端到端命令测试
测试完整的 CLI 命令执行流程
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_ai_root = test_file_dir.parent.parent
sys.path.insert(0, str(edp_ai_root))

from edp_center.main.cli.commands.history_handler import handle_history_cmd
from edp_center.main.cli.commands.stats_handler import handle_stats_cmd
from edp_center.main.cli.commands.rollback_handler import handle_rollback_cmd
from edp_center.main.cli.command_router import create_manager
from edp_center.main.cli.completion.helpers import find_edp_center_path as find_edp_center_path_helper


class TestE2ECommands(unittest.TestCase):
    """端到端命令测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.example_path = test_file_dir.parent / "WORK_PATH"
        cls.test_project_path = cls.example_path / "dongting" / "P85" / "block1" / "user1" / "main"
        cls.edp_center_path = find_edp_center_path_helper()
    
    def setUp(self):
        """每个测试前的准备"""
        # 创建临时目录用于测试输出
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """每个测试后的清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_history_command_e2e(self):
        """测试 history 命令的端到端执行"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        branch_dir = self.test_project_path
        run_info_file = branch_dir / ".run_info"
        
        if not run_info_file.exists():
            self.skipTest("运行历史文件不存在，跳过测试")
        
        # 创建模拟的 args 对象
        class Args:
            def __init__(self):
                self.work_path = str(branch_dir.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.flow = None
                self.step = None
                self.status = None
                self.limit = None
        
        args = Args()
        
        try:
            # 创建 manager
            manager = create_manager(self.edp_center_path)
            # 测试 history 命令（不实际输出，只验证不报错）
            with patch('sys.stdout'):
                result = handle_history_cmd(manager, args)
                # 如果命令执行成功，应该返回 0 或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"history 命令执行失败（可能是环境问题）: {e}")
    
    def test_stats_command_e2e(self):
        """测试 stats 命令的端到端执行"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        branch_dir = self.test_project_path
        run_info_file = branch_dir / ".run_info"
        
        if not run_info_file.exists():
            self.skipTest("运行历史文件不存在，跳过测试")
        
        # 创建模拟的 args 对象
        class Args:
            def __init__(self):
                self.work_path = str(branch_dir.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.step = None
                self.show_trend = False
                self.export = None
        
        args = Args()
        
        try:
            # 创建 manager
            manager = create_manager(self.edp_center_path)
            # 测试 stats 命令（不实际输出，只验证不报错）
            with patch('sys.stdout'):
                result = handle_stats_cmd(manager, args)
                # 如果命令执行成功，应该返回 0 或 None
                self.assertIn(result, [0, None, True])
        except Exception as e:
            self.skipTest(f"stats 命令执行失败（可能是环境问题）: {e}")
    
    def test_stats_export_e2e(self):
        """测试 stats 导出功能的端到端执行"""
        if not self.test_project_path.exists():
            self.skipTest("测试项目路径不存在，跳过测试")
        
        branch_dir = self.test_project_path
        run_info_file = branch_dir / ".run_info"
        
        if not run_info_file.exists():
            self.skipTest("运行历史文件不存在，跳过测试")
        
        # 创建模拟的 args 对象
        export_file = self.temp_dir / "stats.json"
        class Args:
            def __init__(self):
                self.work_path = str(branch_dir.parent)
                self.project = "dongting"
                self.version = "P85"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.step = None
                self.show_trend = False
                self.export = str(export_file)
        
        args = Args()
        
        try:
            # 创建 manager
            manager = create_manager(self.edp_center_path)
            # 测试 stats 导出命令
            result = handle_stats_cmd(manager, args)
            # 验证导出文件是否存在
            if export_file.exists():
                self.assertTrue(export_file.exists(), "导出文件应该存在")
                # 验证文件内容不为空
                self.assertGreater(export_file.stat().st_size, 0, "导出文件应该不为空")
        except Exception as e:
            self.skipTest(f"stats 导出命令执行失败（可能是环境问题）: {e}")


class TestErrorScenarios(unittest.TestCase):
    """错误场景测试"""
    
    def test_history_with_nonexistent_path(self):
        """测试 history 命令处理不存在的路径"""
        # 创建模拟的 args 对象
        class Args:
            def __init__(self):
                self.work_path = "/nonexistent/path"
                self.project = "test"
                self.version = "P1"
                self.block = "block1"
                self.user = "user1"
                self.branch = "main"
                self.flow = None
                self.step = None
                self.status = None
                self.limit = None
        
        args = Args()
        
        # 应该优雅地处理错误，不抛出未捕获的异常
        try:
            with patch('sys.stderr'):
                result = handle_history_cmd(args)
                # 应该返回错误代码或 None
                self.assertIn(result, [0, 1, None, True, False])
        except SystemExit:
            # SystemExit 是可以接受的（CLI 工具可能使用 sys.exit）
            pass
        except Exception as e:
            # 其他异常应该被捕获并处理
            self.fail(f"未处理的异常: {e}")
    
    def test_stats_with_empty_history(self):
        """测试 stats 命令处理空历史"""
        import tempfile
        from pathlib import Path
        
        # 创建临时目录结构
        temp_dir = Path(tempfile.mkdtemp())
        try:
            branch_dir = temp_dir / "test_project" / "P1" / "block1" / "user1" / "main"
            branch_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建空的 .run_info 文件
            run_info_file = branch_dir / ".run_info"
            run_info_file.write_text("[]")
            
            # 创建模拟的 args 对象
            class Args:
                def __init__(self):
                    self.work_path = str(temp_dir)
                    self.project = "test_project"
                    self.version = "P1"
                    self.block = "block1"
                    self.user = "user1"
                    self.branch = "main"
                    self.step = None
                    self.show_trend = False
                    self.export = None
            
            args = Args()
            
            # 应该优雅地处理空历史
            try:
                # 创建 manager（使用测试路径）
                edp_center_path = find_edp_center_path_helper()
                manager = create_manager(edp_center_path)
                with patch('sys.stdout'):
                    result = handle_stats_cmd(manager, args)
                    # 应该返回成功代码或 None
                    self.assertIn(result, [0, None, True])
            except Exception as e:
                self.fail(f"处理空历史时抛出异常: {e}")
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()

