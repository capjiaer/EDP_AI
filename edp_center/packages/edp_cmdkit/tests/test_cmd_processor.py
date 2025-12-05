#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 CmdProcessor 核心功能
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.cmd_processor import CmdProcessor


class TestCmdProcessor(unittest.TestCase):
    """测试 CmdProcessor 类"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建测试目录
        self.util_dir = self.temp_path / "util"
        self.util_dir.mkdir()
        
        # 创建测试文件
        self.helper_tcl = self.util_dir / "helper.tcl"
        self.helper_tcl.write_text("proc helper_proc {} { puts \"Helper\" }")
        
        self.common_tcl = self.util_dir / "common.tcl"
        self.common_tcl.write_text("set common_var 42")
        
        # 创建主脚本
        self.main_script = self.temp_path / "main.tcl"
        
        # 创建 CmdProcessor 实例
        self.processor = CmdProcessor(base_dir=self.temp_path)

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_process_import_source(self):
        """测试处理 #import source 指令"""
        self.main_script.write_text("#import source helper.tcl\nputs \"Main script\"")
        
        result = self.processor.process_file(
            self.main_script,
            search_paths=[self.util_dir]
        )
        
        # 应该包含 source 语句
        self.assertIn("source", result)
        self.assertIn("helper.tcl", result)
        self.assertIn("Main script", result)

    # 注意：已移除 #import util 机制，以下测试已删除
    # def test_process_import_util(self):
    #     """测试处理 #import util 指令（已废弃）"""
    #     # 此测试不再需要，因为 #import util 机制已移除

    def test_process_multiple_imports(self):
        """测试处理多个 #import source 指令"""
        common_tcl = self.util_dir / "common.tcl"
        common_tcl.write_text("set common_var 42")
        
        self.main_script.write_text(
            "#import source helper.tcl\n"
            "#import source common.tcl\n"
            "puts \"Main script\""
        )
        
        result = self.processor.process_file(
            self.main_script,
            search_paths=[self.util_dir]
        )
        
        # 应该包含 source 语句
        self.assertIn("source", result)
        self.assertIn("Main script", result)

    def test_process_file_not_found(self):
        """测试文件不存在的情况"""
        self.main_script.write_text("#import source nonexistent.tcl")
        
        # 可能抛出 FileNotFoundError 或 EDPFileNotFoundError（框架异常）
        try:
            from edp_center.packages.edp_common import EDPFileNotFoundError
            expected_exception = (FileNotFoundError, EDPFileNotFoundError)
        except ImportError:
            expected_exception = FileNotFoundError
        
        # 根据文件重要性，可能抛出异常或继续处理
        # 默认所有文件都是关键的，所以应该抛出异常
        with self.assertRaises(expected_exception):
            self.processor.process_file(
                self.main_script,
                search_paths=[self.util_dir]
            )

    def test_process_file_with_output_file(self):
        """测试指定输出文件"""
        self.main_script.write_text("#import source helper.tcl")
        output_file = self.temp_path / "output.tcl"
        
        result = self.processor.process_file(
            self.main_script,
            output_file=output_file,
            search_paths=[self.util_dir]
        )
        
        # 应该返回 None（内容已写入文件）
        self.assertIsNone(result)
        # 输出文件应该存在
        self.assertTrue(output_file.exists())
        # 输出文件应该包含处理后的内容
        output_content = output_file.read_text()
        self.assertIn("source", output_content)

    def test_process_nested_imports(self):
        """测试嵌套的 #import source 指令"""
        # 创建一个被导入的文件，它也包含 #import source
        nested_tcl = self.util_dir / "nested.tcl"
        nested_tcl.write_text("#import source helper.tcl\nset nested_var 100")
        
        self.main_script.write_text("#import source nested.tcl")
        
        result = self.processor.process_file(
            self.main_script,
            search_paths=[self.util_dir]
        )
        
        # 应该递归处理嵌套的 import source
        # 注意：nested_var 不会出现在结果中，因为 #import source 只生成 source 语句
        self.assertIn("source", result)


if __name__ == '__main__':
    unittest.main()

