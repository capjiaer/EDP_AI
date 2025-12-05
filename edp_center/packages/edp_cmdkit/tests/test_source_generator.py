#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 source_generator 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.source_generator import generate_source_statement


class TestSourceGenerator(unittest.TestCase):
    """测试 source_generator 模块"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建搜索目录
        self.search_dir = self.temp_path / "search"
        self.search_dir.mkdir()
        
        # 创建测试文件
        self.test_file = self.search_dir / "test.tcl"
        self.test_file.write_text("# test file")
        
        # 当前文件
        self.current_file = self.temp_path / "current.tcl"
        self.current_file.write_text("# current script")

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_generate_source_statement(self):
        """测试生成 source 语句"""
        result = generate_source_statement(
            "test.tcl",
            self.current_file,
            [self.search_dir]
        )
        
        # 应该生成 source 语句，路径使用正斜杠
        expected_path = str(self.test_file).replace('\\', '/')
        self.assertIn("source", result)
        self.assertIn(expected_path, result)
        self.assertNotIn("\\", result)  # 不应该有反斜杠

    def test_generate_source_file_not_found(self):
        """测试文件不存在时抛出异常"""
        # 可能抛出 FileNotFoundError 或 EDPFileNotFoundError（框架异常）
        try:
            from edp_center.packages.edp_common import EDPFileNotFoundError
            expected_exception = (FileNotFoundError, EDPFileNotFoundError)
        except ImportError:
            expected_exception = FileNotFoundError
        
        with self.assertRaises(expected_exception):
            generate_source_statement(
                "nonexistent.tcl",
                self.current_file,
                [self.search_dir]
            )

    def test_generate_source_error_message(self):
        """测试错误信息包含详细信息"""
        try:
            generate_source_statement(
                "nonexistent.tcl",
                self.current_file,
                [self.search_dir]
            )
        except (FileNotFoundError, Exception) as e:
            error_msg = str(e)
            self.assertIn("nonexistent.tcl", error_msg)
            # 检查是否包含详细信息（框架异常会包含这些）
            if "详细信息" in error_msg or "当前文件" in error_msg or "搜索路径" in error_msg:
                # 框架异常格式
                self.assertIn("详细信息", error_msg)
                self.assertIn("建议", error_msg)
            else:
                # 标准异常格式（向后兼容）
                self.assertIn("无法找到文件", error_msg)


if __name__ == '__main__':
    unittest.main()

