#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CacheManager 缓存失效逻辑属性测试

**Feature: edp-libkit-enhancement, Property 12: Intelligent caching behavior**
**Validates: Requirements 7.2**

测试缓存管理器的智能缓存失效机制。
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import time
import os

# 导入被测试的模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from cache_manager import CacheManager, CacheEntry


# 测试数据生成策略
@st.composite
def cache_data_strategy(draw):
    """生成缓存数据"""
    data_type = draw(st.sampled_from(['string', 'dict', 'list', 'int']))
    
    if data_type == 'string':
        return draw(st.text(min_size=0, max_size=1000))
    elif data_type == 'dict':
        return draw(st.dictionaries(st.text(min_size=1, max_size=20), st.integers(), min_size=0, max_size=10))
    elif data_type == 'list':
        return draw(st.lists(st.integers(), min_size=0, max_size=20))
    else:  # int
        return draw(st.integers())


@st.composite
def cache_key_strategy(draw):
    """生成缓存键"""
    return draw(st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))))


@st.composite
def temp_file_strategy(draw):
    """生成临时文件用于测试"""
    temp_dir = Path(tempfile.gettempdir()) / "cache_test"
    temp_dir.mkdir(exist_ok=True)
    
    filename = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    file_path = temp_dir / f"{filename}.txt"
    
    content = draw(st.text(min_size=0, max_size=1000))
    file_path.write_text(content)
    
    return file_path


class TestCacheManagerProperties:
    """CacheManager 属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时缓存目录
        self.temp_cache_dir = Path(tempfile.gettempdir()) / "cache_manager_test"
        if self.temp_cache_dir.exists():
            import shutil
            shutil.rmtree(self.temp_cache_dir)
        
        self.cache_manager = CacheManager(cache_dir=self.temp_cache_dir, max_memory_entries=100)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        if hasattr(self, 'cache_manager'):
            self.cache_manager.clear_all()
        
        if hasattr(self, 'temp_cache_dir') and self.temp_cache_dir.exists():
            import shutil
            shutil.rmtree(self.temp_cache_dir)
    
    @given(cache_key_strategy(), cache_data_strategy())
    def test_cache_set_get_consistency_property(self, key, data):
        """
        属性测试：缓存设置和获取的一致性
        
        对于任何键值对，设置缓存后立即获取应该返回相同的数据
        """
        # 设置缓存
        success = self.cache_manager.set(key, data)
        assert success
        
        # 立即获取
        retrieved_data = self.cache_manager.get(key)
        
        # 验证数据一致性
        assert retrieved_data == data
    
    @given(cache_key_strategy(), cache_data_strategy(), temp_file_strategy())
    def test_cache_timestamp_invalidation_property(self, key, data, source_file):
        """
        属性测试：基于时间戳的缓存失效
        
        对于任何缓存项，当源文件被修改后，缓存应该自动失效
        """
        assume(source_file.exists())
        
        # 设置带源文件的缓存
        success = self.cache_manager.set(key, data, source_path=source_file)
        assert success
        
        # 验证缓存有效
        retrieved_data = self.cache_manager.get(key)
        assert retrieved_data == data
        
        # 等待一小段时间，然后修改源文件
        time.sleep(0.01)
        source_file.write_text("modified content")
        
        # 缓存应该失效
        retrieved_data_after_modification = self.cache_manager.get(key)
        assert retrieved_data_after_modification is None
    
    @given(cache_key_strategy(), cache_data_strategy())
    def test_cache_max_age_invalidation_property(self, key, data):
        """
        属性测试：基于最大年龄的缓存失效
        
        对于任何缓存项，超过最大年龄后应该自动失效
        """
        # 设置缓存
        success = self.cache_manager.set(key, data)
        assert success
        
        # 使用很短的最大年龄检查缓存
        very_short_age = timedelta(microseconds=1)
        
        # 等待超过最大年龄
        time.sleep(0.001)
        
        # 缓存应该因为超过最大年龄而失效
        retrieved_data = self.cache_manager.get(key, max_age=very_short_age)
        assert retrieved_data is None
        
        # 但是不指定最大年龄时应该仍然有效
        retrieved_data_no_age = self.cache_manager.get(key)
        assert retrieved_data_no_age == data
    
    @given(st.lists(st.tuples(cache_key_strategy(), cache_data_strategy()), min_size=1, max_size=20))
    def test_cache_memory_eviction_property(self, key_data_pairs):
        """
        属性测试：内存缓存的LRU清理机制
        
        对于任何缓存项列表，当超过内存限制时应该正确清理最少使用的项
        """
        # 创建小容量的缓存管理器
        small_cache = CacheManager(cache_dir=self.temp_cache_dir / "small", max_memory_entries=5)
        
        try:
            # 添加缓存项
            for key, data in key_data_pairs:
                small_cache.set(key, data, persist_to_disk=False)  # 只存内存
            
            # 获取统计信息
            stats = small_cache.get_stats()
            
            # 验证内存缓存数量不超过限制
            assert stats['memory_entries'] <= 5
            
            # 如果输入项超过限制，验证清理发生了
            if len(key_data_pairs) > 5:
                assert stats['evictions'] > 0
        
        finally:
            small_cache.clear_all()
    
    @given(cache_key_strategy(), cache_data_strategy())
    def test_cache_invalidation_property(self, key, data):
        """
        属性测试：缓存失效操作的正确性
        
        对于任何缓存项，调用失效操作后应该无法再获取到数据
        """
        # 设置缓存
        success = self.cache_manager.set(key, data)
        assert success
        
        # 验证缓存存在
        retrieved_data = self.cache_manager.get(key)
        assert retrieved_data == data
        
        # 使缓存失效
        invalidate_success = self.cache_manager.invalidate(key)
        assert invalidate_success
        
        # 验证缓存已失效
        retrieved_data_after_invalidation = self.cache_manager.get(key)
        assert retrieved_data_after_invalidation is None
    
    @given(st.lists(st.tuples(cache_key_strategy(), cache_data_strategy()), min_size=1, max_size=10))
    def test_cache_persistence_property(self, key_data_pairs):
        """
        属性测试：缓存持久化的正确性
        
        对于任何缓存项，持久化到磁盘后重新创建缓存管理器应该能够恢复数据
        """
        # 设置持久化缓存
        for key, data in key_data_pairs:
            success = self.cache_manager.set(key, data, persist_to_disk=True)
            assert success
        
        # 创建新的缓存管理器（模拟重启）
        new_cache_manager = CacheManager(cache_dir=self.temp_cache_dir, max_memory_entries=100)
        
        try:
            # 验证数据可以从磁盘恢复
            for key, expected_data in key_data_pairs:
                retrieved_data = new_cache_manager.get(key)
                assert retrieved_data == expected_data
        
        finally:
            new_cache_manager.clear_all()
    
    @given(temp_file_strategy())
    def test_cache_entry_validity_property(self, source_file):
        """
        属性测试：CacheEntry 有效性检查的正确性
        
        对于任何缓存条目，有效性检查应该正确反映源文件状态和时间限制
        """
        assume(source_file.exists())
        
        # 创建缓存条目
        test_data = "test data"
        entry = CacheEntry(test_data, source_file)
        
        # 新创建的条目应该有效
        assert entry.is_valid()
        assert entry.is_valid(timedelta(hours=1))
        
        # 超过时间限制应该无效
        very_short_age = timedelta(microseconds=1)
        time.sleep(0.001)
        assert not entry.is_valid(very_short_age)
        
        # 修改源文件后应该无效
        original_content = source_file.read_text()
        time.sleep(0.01)
        source_file.write_text("modified content")
        
        assert not entry.is_valid()
        
        # 恢复原内容，但修改时间已变，仍应无效
        source_file.write_text(original_content)
        assert not entry.is_valid()
    
    @given(st.lists(cache_key_strategy(), min_size=1, max_size=20))
    def test_cache_pattern_invalidation_property(self, keys):
        """
        属性测试：模式匹配缓存失效的正确性
        
        对于任何键列表，模式匹配失效应该正确处理通配符
        """
        test_data = "test data"
        
        # 设置所有缓存
        for key in keys:
            self.cache_manager.set(key, test_data)
        
        # 验证所有缓存都存在
        for key in keys:
            assert self.cache_manager.get(key) == test_data
        
        # 使用通配符模式失效所有缓存
        invalidated_count = self.cache_manager.invalidate_pattern("*")
        
        # 验证所有缓存都被失效
        for key in keys:
            assert self.cache_manager.get(key) is None
        
        # 验证失效数量正确（至少应该等于设置的数量）
        assert invalidated_count >= len(keys)
    
    @given(st.lists(st.tuples(cache_key_strategy(), cache_data_strategy()), min_size=1, max_size=10))
    def test_cache_statistics_property(self, key_data_pairs):
        """
        属性测试：缓存统计信息的正确性
        
        对于任何缓存操作序列，统计信息应该正确反映缓存的使用情况
        """
        initial_stats = self.cache_manager.get_stats()
        initial_hits = initial_stats['hits']
        initial_misses = initial_stats['misses']
        
        # 执行缓存操作
        for key, data in key_data_pairs:
            # 第一次获取应该是miss
            result = self.cache_manager.get(key)
            assert result is None
            
            # 设置缓存
            self.cache_manager.set(key, data)
            
            # 第二次获取应该是hit
            result = self.cache_manager.get(key)
            assert result == data
        
        # 检查统计信息
        final_stats = self.cache_manager.get_stats()
        
        # 验证miss数量增加
        expected_misses = initial_misses + len(key_data_pairs)
        assert final_stats['misses'] == expected_misses
        
        # 验证hit数量增加
        expected_hits = initial_hits + len(key_data_pairs)
        assert final_stats['hits'] == expected_hits
        
        # 验证命中率计算
        total_requests = final_stats['hits'] + final_stats['misses']
        if total_requests > 0:
            expected_hit_rate = (final_stats['hits'] / total_requests) * 100
            assert f"{expected_hit_rate:.1f}%" == final_stats['hit_rate']


class TestCacheEntryProperties:
    """CacheEntry 属性测试类"""
    
    @given(cache_data_strategy())
    def test_cache_entry_creation_property(self, data):
        """
        属性测试：CacheEntry 创建的正确性
        
        对于任何数据，创建的缓存条目应该正确存储数据和时间戳
        """
        entry = CacheEntry(data)
        
        # 验证数据存储
        assert entry.data == data
        
        # 验证时间戳
        assert entry.created_at is not None
        assert entry.accessed_at is not None
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.accessed_at, datetime)
        
        # 创建时间和访问时间应该相近
        time_diff = abs((entry.created_at - entry.accessed_at).total_seconds())
        assert time_diff < 0.1  # 应该在100毫秒内
    
    @given(cache_data_strategy())
    def test_cache_entry_touch_property(self, data):
        """
        属性测试：CacheEntry touch 操作的正确性
        
        对于任何缓存条目，touch 操作应该更新访问时间
        """
        entry = CacheEntry(data)
        original_accessed_at = entry.accessed_at
        
        # 等待一小段时间
        time.sleep(0.01)
        
        # Touch 操作
        entry.touch()
        
        # 验证访问时间更新
        assert entry.accessed_at > original_accessed_at
        assert entry.created_at <= entry.accessed_at


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])