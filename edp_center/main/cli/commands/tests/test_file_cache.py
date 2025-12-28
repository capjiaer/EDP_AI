#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件搜索缓存测试
测试文件搜索缓存机制是否正常工作
"""

import unittest
import sys
import time
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
test_file_dir = Path(__file__).resolve().parent
edp_center_root = test_file_dir.parent.parent.parent.parent
sys.path.insert(0, str(edp_center_root))

# 导入 file_finder
try:
    from edp_center.packages.edp_cmdkit.file_finder import find_file, clear_file_cache
except ImportError:
    # 如果导入失败，尝试直接导入
    import importlib.util
    file_finder_path = edp_center_root / 'packages' / 'edp_cmdkit' / 'file_finder.py'
    spec = importlib.util.spec_from_file_location("file_finder", file_finder_path)
    file_finder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_finder)
    find_file = file_finder.find_file
    clear_file_cache = file_finder.clear_file_cache


class TestFileCache(unittest.TestCase):
    """文件搜索缓存测试类"""
    
    def setUp(self):
        """每个测试前的设置"""
        # 清除缓存，确保测试独立性
        clear_file_cache()
        
        # 创建临时目录结构
        self.temp_dir = tempfile.mkdtemp(prefix='edp_cache_test_')
        self.temp_path = Path(self.temp_dir)
        
        # 创建搜索目录
        self.search_dir = self.temp_path / "search"
        self.search_dir.mkdir()
        
        # 创建子目录
        self.sub_dir = self.search_dir / "subdir"
        self.sub_dir.mkdir()
        
        # 创建测试文件
        self.test_file = self.sub_dir / "helper.tcl"
        self.test_file.write_text("# test helper file")
        
        # 当前文件（用于相对路径查找）
        self.current_file = self.temp_path / "current.tcl"
        self.current_file.write_text("# current file")
    
    def tearDown(self):
        """每个测试后的清理"""
        # 清除缓存
        clear_file_cache()
        
        # 删除临时目录
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_cache_hit(self):
        """测试缓存命中"""
        search_paths = [self.search_dir]
        
        # 第一次搜索（应该会搜索并缓存）
        start_time = time.time()
        result1 = find_file("helper.tcl", self.current_file, search_paths, recursive=True)
        time1 = (time.time() - start_time) * 1000
        
        self.assertIsNotNone(result1)
        self.assertEqual(result1, self.test_file)
        
        # 第二次搜索（应该使用缓存）
        start_time = time.time()
        result2 = find_file("helper.tcl", self.current_file, search_paths, recursive=True)
        time2 = (time.time() - start_time) * 1000
        
        self.assertIsNotNone(result2)
        self.assertEqual(result2, self.test_file)
        self.assertEqual(result1, result2)
        
        # 验证性能提升（缓存应该更快）
        # 注意：在非常快的系统上，时间差可能很小，所以只检查缓存没有变慢
        self.assertGreaterEqual(time1, time2, "缓存应该至少不会比直接搜索慢")
    
    def test_cache_clear(self):
        """测试缓存清除"""
        search_paths = [self.search_dir]
        
        # 先搜索一次，建立缓存
        result1 = find_file("helper.tcl", self.current_file, search_paths, recursive=True)
        self.assertIsNotNone(result1)
        
        # 清除缓存
        clear_file_cache()
        
        # 再次搜索（应该重新搜索，不使用缓存）
        result2 = find_file("helper.tcl", self.current_file, search_paths, recursive=True)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2)
    
    def test_cache_invalidation_on_file_change(self):
        """测试文件变化时的缓存失效"""
        search_paths = [self.search_dir]
        
        # 第一次搜索
        result1 = find_file("helper.tcl", self.current_file, search_paths, recursive=True)
        self.assertIsNotNone(result1)
        
        # 修改文件（更新修改时间）
        import time as time_module
        time_module.sleep(0.1)  # 确保时间戳变化
        self.test_file.write_text("# modified helper file")
        
        # 再次搜索（应该重新搜索，因为文件被修改了）
        result2 = find_file("helper.tcl", self.current_file, search_paths, recursive=True)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2)  # 路径应该相同
    
    def test_cache_not_found_result(self):
        """测试缓存未找到的结果"""
        search_paths = [self.search_dir]
        
        # 第一次搜索不存在的文件
        result1 = find_file("nonexistent.tcl", self.current_file, search_paths, recursive=True)
        self.assertIsNone(result1)
        
        # 第二次搜索相同的不存在文件（应该使用缓存）
        start_time = time.time()
        result2 = find_file("nonexistent.tcl", self.current_file, search_paths, recursive=True)
        time2 = (time.time() - start_time) * 1000
        
        self.assertIsNone(result2)
        
        # 验证缓存提升了性能（应该很快）
        self.assertLess(time2, 10, "缓存查询应该很快（<10ms）")
    
    def test_multiple_searches_performance(self):
        """测试多次搜索的性能"""
        search_paths = [self.search_dir]
        test_files = ["helper.tcl", "helper.tcl", "helper.tcl"]  # 重复搜索
        
        # 清除缓存，从头开始
        clear_file_cache()
        
        times = []
        for test_file in test_files:
            start_time = time.time()
            result = find_file(test_file, self.current_file, search_paths, recursive=True)
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
            self.assertIsNotNone(result)
        
        # 验证缓存提升了性能
        # 第一次搜索应该最慢，后续搜索应该更快
        if len(times) > 1:
            first_time = times[0]
            cached_times = times[1:]
            avg_cached_time = sum(cached_times) / len(cached_times)
            
            # 缓存应该至少不会比直接搜索慢
            self.assertGreaterEqual(first_time, avg_cached_time, 
                                  "缓存搜索应该至少不会比直接搜索慢")


if __name__ == '__main__':
    unittest.main()

