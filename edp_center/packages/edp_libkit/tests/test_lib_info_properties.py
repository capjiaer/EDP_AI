#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LibInfo 模型属性测试

**Feature: edp-libkit-enhancement, Property 1: Library metadata completeness**
**Validates: Requirements 1.2, 6.1**

测试增强的 LibInfo 模型的正确性和完整性。
"""

import pytest
from hypothesis import given, strategies as st, assume
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import os

# 导入被测试的模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib_info import LibInfo, ViewInfo, FileInfo, LibraryStatistics


# 测试数据生成策略
@st.composite
def file_info_strategy(draw):
    """生成 FileInfo 测试数据"""
    # 创建临时文件用于测试
    temp_dir = Path(tempfile.gettempdir()) / "libkit_test"
    temp_dir.mkdir(exist_ok=True)
    
    file_name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    file_path = temp_dir / f"{file_name}.gds"
    
    # 创建测试文件
    file_path.write_text("test content")
    
    file_type = draw(st.sampled_from(['gds', 'lef', 'db', 'cdl', 'v']))
    pvt_corner = draw(st.one_of(st.none(), st.sampled_from(['ffpg0p825v125c', 'sspg0p675v125c', 'tt0p75v125c'])))
    rc_corner = draw(st.one_of(st.none(), st.sampled_from(['sigcmin', 'sigcmax', 'typical'])))
    
    return FileInfo(
        file_path=file_path,
        file_type=file_type,
        pvt_corner=pvt_corner,
        rc_corner=rc_corner
    )


@st.composite
def view_info_strategy(draw):
    """生成 ViewInfo 测试数据"""
    view_type = draw(st.sampled_from(['gds', 'lef', 'liberty', 'cdl', 'verilog']))
    
    temp_dir = Path(tempfile.gettempdir()) / "libkit_test" / view_type
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    files = draw(st.lists(file_info_strategy(), min_size=0, max_size=10))
    pvt_corners = draw(st.sets(st.sampled_from(['ffpg0p825v125c', 'sspg0p675v125c', 'tt0p75v125c']), min_size=0, max_size=3))
    supported_tools = draw(st.lists(st.sampled_from(['innovus', 'icc2', 'primetime']), min_size=0, max_size=3))
    
    return ViewInfo(
        view_type=view_type,
        view_path=temp_dir,
        files=files,
        pvt_corners=pvt_corners,
        supported_tools=supported_tools
    )


@st.composite
def lib_info_strategy(draw):
    """生成 LibInfo 测试数据"""
    lib_name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    
    temp_dir = Path(tempfile.gettempdir()) / "libkit_test" / lib_name
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    lib_type = draw(st.sampled_from(['STD', 'IP', 'MEM']))
    version = draw(st.one_of(st.none(), st.sampled_from(['1.01a', '2.00A', 'v1.12'])))
    foundry = draw(st.one_of(st.none(), st.sampled_from(['Samsung', 'TSMC', 'SMIC'])))
    node = draw(st.one_of(st.none(), st.sampled_from(['LN08LPU_GP', 'LN05LPE', 'N7', 'N5'])))
    
    return LibInfo(
        lib_name=lib_name,
        lib_path=temp_dir,
        lib_type=lib_type,
        version=version,
        foundry=foundry,
        node=node
    )


class TestLibInfoProperties:
    """LibInfo 属性测试类"""
    
    @given(file_info_strategy())
    def test_file_info_metadata_update_property(self, file_info):
        """
        属性测试：FileInfo 元数据更新的正确性
        
        对于任何 FileInfo 对象，调用 update_metadata() 后应该正确设置文件大小、修改时间和校验和
        """
        # 确保文件存在
        assume(file_info.file_path.exists())
        
        # 更新元数据
        file_info.update_metadata()
        
        # 验证元数据被正确设置
        assert file_info.size is not None
        assert file_info.size > 0  # 测试文件有内容
        assert file_info.modified_time is not None
        assert isinstance(file_info.modified_time, datetime)
        assert file_info.checksum is not None
        assert len(file_info.checksum) == 32  # MD5 哈希长度
        
        # 验证校验和的一致性
        checksum1 = file_info.calculate_checksum()
        checksum2 = file_info.calculate_checksum()
        assert checksum1 == checksum2
    
    @given(view_info_strategy())
    def test_view_info_statistics_property(self, view_info):
        """
        属性测试：ViewInfo 统计信息的正确性
        
        对于任何 ViewInfo 对象，其统计属性应该与实际文件列表一致
        """
        # 验证文件数量
        assert view_info.file_count == len(view_info.files)
        
        # 验证总大小计算
        expected_size = sum(f.size or 0 for f in view_info.files)
        assert view_info.total_size == expected_size
        
        # 如果有文件，验证 PVT corners
        if view_info.files:
            file_corners = set()
            for f in view_info.files:
                if f.pvt_corner:
                    file_corners.add(f.pvt_corner)
            # view_info.pvt_corners 可能包含额外的 corners，但应该包含文件中的所有 corners
            assert file_corners.issubset(view_info.pvt_corners) or len(file_corners) == 0
    
    @given(lib_info_strategy())
    def test_lib_info_unique_id_property(self, lib_info):
        """
        属性测试：LibInfo 唯一标识符的正确性
        
        对于任何 LibInfo 对象，其唯一标识符应该包含所有关键信息且保持一致
        """
        # 获取唯一标识符
        unique_id1 = lib_info.get_unique_id()
        unique_id2 = lib_info.get_unique_id()
        
        # 验证一致性
        assert unique_id1 == unique_id2
        
        # 验证包含关键信息
        assert lib_info.lib_type in unique_id1
        assert lib_info.lib_name in unique_id1
        
        if lib_info.foundry:
            assert lib_info.foundry in unique_id1
        if lib_info.node:
            assert lib_info.node in unique_id1
        if lib_info.version:
            assert lib_info.version in unique_id1
    
    @given(lib_info_strategy(), st.lists(view_info_strategy(), min_size=0, max_size=5))
    def test_lib_info_view_management_property(self, lib_info, views):
        """
        属性测试：LibInfo 视图管理的正确性
        
        对于任何 LibInfo 对象和视图列表，添加视图后应该正确更新相关信息
        """
        initial_view_count = len(lib_info.views)
        
        # 添加视图
        for view in views:
            lib_info.add_view(view)
        
        # 验证视图数量
        expected_count = initial_view_count + len(views)
        assert len(lib_info.views) <= expected_count  # 可能有重复的 view_type
        
        # 验证支持的视图类型
        supported_views = lib_info.get_supported_view_types()
        for view in views:
            assert view.view_type in supported_views
        
        # 验证 PVT corners
        supported_corners = lib_info.get_supported_pvt_corners()
        for view in views:
            assert view.pvt_corners.issubset(supported_corners) or len(view.pvt_corners) == 0
    
    @given(lib_info_strategy())
    def test_lib_info_statistics_update_property(self, lib_info):
        """
        属性测试：LibInfo 统计信息更新的正确性
        
        对于任何 LibInfo 对象，更新统计信息后应该反映当前的视图状态
        """
        # 添加一些测试视图
        test_view = ViewInfo(
            view_type='gds',
            view_path=lib_info.lib_path / 'gds',
            files=[],
            pvt_corners={'ffpg0p825v125c'},
            supported_tools=['innovus']
        )
        lib_info.add_view(test_view)
        
        # 更新统计信息
        lib_info.update_statistics()
        
        # 验证统计信息
        assert lib_info.statistics.total_files == sum(view.file_count for view in lib_info.views.values())
        assert lib_info.statistics.total_size == sum(view.total_size for view in lib_info.views.values())
        assert lib_info.statistics.last_updated is not None
        assert lib_info.updated_at is not None
        
        # 验证视图计数
        for view_type, view in lib_info.views.items():
            assert lib_info.statistics.view_counts.get(view_type, 0) == view.file_count
    
    @given(lib_info_strategy())
    def test_lib_info_timestamp_property(self, lib_info):
        """
        属性测试：LibInfo 时间戳管理的正确性
        
        对于任何 LibInfo 对象，时间戳应该正确设置和更新
        """
        # 验证初始时间戳
        assert lib_info.created_at is not None
        assert lib_info.updated_at is not None
        assert isinstance(lib_info.created_at, datetime)
        assert isinstance(lib_info.updated_at, datetime)
        
        # 记录初始时间
        initial_updated_at = lib_info.updated_at
        
        # 等待一小段时间后更新
        import time
        time.sleep(0.01)
        
        # 添加视图应该更新 updated_at
        test_view = ViewInfo(
            view_type='lef',
            view_path=lib_info.lib_path / 'lef'
        )
        lib_info.add_view(test_view)
        
        # 验证时间戳更新
        assert lib_info.updated_at > initial_updated_at
        assert lib_info.created_at <= lib_info.updated_at
    
    @given(st.lists(lib_info_strategy(), min_size=2, max_size=10))
    def test_lib_info_uniqueness_property(self, lib_infos):
        """
        属性测试：不同 LibInfo 对象的唯一性
        
        对于任何不同的 LibInfo 对象列表，它们的唯一标识符应该能够区分它们
        """
        unique_ids = set()
        
        for lib_info in lib_infos:
            unique_id = lib_info.get_unique_id()
            
            # 如果ID已存在，验证是否确实是相同的库
            if unique_id in unique_ids:
                # 查找具有相同ID的库
                for other_lib in lib_infos:
                    if other_lib.get_unique_id() == unique_id and other_lib is not lib_info:
                        # 验证关键属性确实相同
                        assert other_lib.foundry == lib_info.foundry
                        assert other_lib.node == lib_info.node
                        assert other_lib.lib_type == lib_info.lib_type
                        assert other_lib.lib_name == lib_info.lib_name
                        assert other_lib.version == lib_info.version
                        break
            
            unique_ids.add(unique_id)


class TestLibraryStatistics:
    """LibraryStatistics 属性测试类"""
    
    @given(
        st.lists(st.sampled_from(['gds', 'lef', 'liberty', 'cdl']), min_size=1, max_size=5),
        st.lists(st.sampled_from(['ffpg0p825v125c', 'sspg0p675v125c', 'tt0p75v125c']), min_size=1, max_size=3)
    )
    def test_completeness_score_property(self, expected_views, expected_corners):
        """
        属性测试：完整性评分计算的正确性
        
        对于任何期望的视图和corner列表，完整性评分应该在0-100之间且反映实际完整度
        """
        stats = LibraryStatistics()
        
        # 模拟部分完整的库
        stats.view_counts = {view: 1 for view in expected_views[:len(expected_views)//2]}
        stats.pvt_corner_coverage = {corner: 1 for corner in expected_corners[:len(expected_corners)//2]}
        
        # 计算完整性评分
        score = stats.calculate_completeness_score(expected_views, expected_corners)
        
        # 验证评分范围
        assert 0.0 <= score <= 100.0
        
        # 验证评分逻辑
        if len(expected_views) > 0:
            expected_view_score = (len(stats.view_counts) / len(expected_views)) * 50.0
        else:
            expected_view_score = 0.0
            
        if len(expected_corners) > 0:
            expected_corner_score = (len(stats.pvt_corner_coverage) / len(expected_corners)) * 50.0
        else:
            expected_corner_score = 0.0
        
        expected_total = expected_view_score + expected_corner_score
        assert abs(score - expected_total) < 0.01  # 浮点数比较
        
        # 验证完全匹配时得分为100
        stats.view_counts = {view: 1 for view in expected_views}
        stats.pvt_corner_coverage = {corner: 1 for corner in expected_corners}
        full_score = stats.calculate_completeness_score(expected_views, expected_corners)
        assert abs(full_score - 100.0) < 0.01


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])