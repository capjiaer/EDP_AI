#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 file_finder 模块
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from edp_cmdkit.file_finder import find_file, clear_file_cache


class TestFileFinder(unittest.TestCase):
    """测试 file_finder 模块"""

    def setUp(self):
        """每个测试前的设置"""
        # 清除缓存，确保测试独立性
        clear_file_cache()
        
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建测试目录结构
        self.search_dir1 = self.temp_path / "search1"
        self.search_dir2 = self.temp_path / "search2"
        self.search_dir1.mkdir()
        self.search_dir2.mkdir()
        
        # 创建子目录
        self.sub_dir = self.search_dir1 / "subdir"
        self.sub_dir.mkdir()
        
        # 创建测试文件
        self.test_file1 = self.search_dir1 / "test1.tcl"
        self.test_file1.write_text("# test file 1")
        
        self.test_file2 = self.search_dir2 / "test2.tcl"
        self.test_file2.write_text("# test file 2")
        
        self.test_file3 = self.sub_dir / "test3.tcl"
        self.test_file3.write_text("# test file 3")
        
        # 当前文件（用于相对路径测试）
        self.current_file = self.temp_path / "current" / "script.tcl"
        self.current_file.parent.mkdir()
        self.current_file.write_text("# current script")
        
        # 相对当前文件的测试文件
        self.relative_file = self.current_file.parent / "relative.tcl"
        self.relative_file.write_text("# relative file")

    def tearDown(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)

    def test_find_absolute_path(self):
        """测试查找绝对路径"""
        result = find_file(
            str(self.test_file1),
            self.current_file,
            [self.search_dir1, self.search_dir2]
        )
        self.assertEqual(result, self.test_file1)

    def test_find_relative_to_current(self):
        """测试查找相对当前文件的路径"""
        result = find_file(
            "relative.tcl",
            self.current_file,
            [self.search_dir1, self.search_dir2]
        )
        self.assertEqual(result, self.relative_file)

    def test_find_in_search_paths(self):
        """测试在搜索路径中查找"""
        result = find_file(
            "test1.tcl",
            self.current_file,
            [self.search_dir1, self.search_dir2]
        )
        self.assertEqual(result, self.test_file1)

    def test_find_in_multiple_search_paths(self):
        """测试在多个搜索路径中查找（按顺序）"""
        # 在 search_dir2 中也有 test1.tcl
        test_file1_in_dir2 = self.search_dir2 / "test1.tcl"
        test_file1_in_dir2.write_text("# test file 1 in dir2")
        
        # 应该找到第一个（search_dir1 中的）
        result = find_file(
            "test1.tcl",
            self.current_file,
            [self.search_dir1, self.search_dir2]
        )
        self.assertEqual(result, self.test_file1)

    def test_find_recursive(self):
        """测试递归查找"""
        result = find_file(
            "test3.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        self.assertEqual(result, self.test_file3)

    def test_find_non_recursive(self):
        """测试非递归查找（应该找不到子目录中的文件）"""
        result = find_file(
            "test3.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=False
        )
        self.assertIsNone(result)

    def test_file_not_found(self):
        """测试文件不存在的情况"""
        result = find_file(
            "nonexistent.tcl",
            self.current_file,
            [self.search_dir1, self.search_dir2]
        )
        self.assertIsNone(result)

    def test_absolute_path_not_exists(self):
        """测试绝对路径不存在的情况"""
        nonexistent = self.temp_path / "nonexistent.tcl"
        result = find_file(
            str(nonexistent),
            self.current_file,
            [self.search_dir1, self.search_dir2]
        )
        self.assertIsNone(result)

    def test_cache_functionality(self):
        """测试缓存功能"""
        import time
        
        # 第一次查找应该执行实际搜索
        result1 = find_file(
            "test3.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        self.assertEqual(result1, self.test_file3)
        
        # 第二次查找应该使用缓存（更快）
        start_time = time.time()
        result2 = find_file(
            "test3.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        elapsed_time = time.time() - start_time
        
        # 结果应该相同
        self.assertEqual(result2, self.test_file3)
        # 第二次查找应该很快（使用缓存）
        # 注意：这个测试可能在某些系统上不够稳定，但通常缓存查找应该 < 0.001 秒
        self.assertLess(elapsed_time, 0.1, "缓存查找应该比实际搜索快得多")

    def test_cache_invalidation(self):
        """测试缓存失效（文件被删除后）"""
        # 第一次查找
        result1 = find_file(
            "test1.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        self.assertEqual(result1, self.test_file1)
        
        # 删除文件
        self.test_file1.unlink()
        
        # 再次查找应该返回 None（缓存应该失效）
        result2 = find_file(
            "test1.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        self.assertIsNone(result2)

    def test_clear_cache(self):
        """测试清除缓存功能"""
        # 先进行一次查找，填充缓存
        find_file(
            "test3.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        
        # 清除缓存
        clear_file_cache()
        
        # 再次查找应该仍然能找到文件（只是缓存被清除了）
        result = find_file(
            "test3.tcl",
            self.current_file,
            [self.search_dir1],
            recursive=True
        )
        self.assertEqual(result, self.test_file3)


if __name__ == '__main__':
    unittest.main()

