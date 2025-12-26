#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LibInfo - 库信息数据类

用于存储库的基本信息和增强的元数据。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, List, Set
from datetime import datetime
import hashlib


@dataclass
class FileInfo:
    """文件信息数据类"""
    
    file_path: Path
    """文件路径"""
    
    file_type: str
    """文件类型，如 gds, lef, db, cdl"""
    
    pvt_corner: Optional[str] = None
    """PVT corner，如 ffpg0p825v125c"""
    
    rc_corner: Optional[str] = None
    """RC corner，如 sigcmin, sigcmax, typical"""
    
    checksum: Optional[str] = None
    """文件校验和（用于变更检测）"""
    
    size: Optional[int] = None
    """文件大小（字节）"""
    
    modified_time: Optional[datetime] = None
    """文件修改时间"""
    
    def calculate_checksum(self) -> str:
        """计算文件校验和"""
        if not self.file_path.exists():
            return ""
        
        hash_md5 = hashlib.md5()
        # 只计算文件大小和修改时间的哈希，避免读取大文件
        stat = self.file_path.stat()
        hash_md5.update(str(stat.st_size).encode())
        hash_md5.update(str(stat.st_mtime).encode())
        return hash_md5.hexdigest()
    
    def update_metadata(self):
        """更新文件元数据"""
        if self.file_path.exists():
            stat = self.file_path.stat()
            self.size = stat.st_size
            self.modified_time = datetime.fromtimestamp(stat.st_mtime)
            self.checksum = self.calculate_checksum()


@dataclass
class ViewInfo:
    """视图信息数据类"""
    
    view_type: str
    """视图类型，如 gds, lef, liberty"""
    
    view_path: Path
    """视图目录路径"""
    
    files: List[FileInfo] = field(default_factory=list)
    """该视图下的所有文件"""
    
    pvt_corners: Set[str] = field(default_factory=set)
    """支持的PVT corners"""
    
    supported_tools: List[str] = field(default_factory=list)
    """支持的EDA工具"""
    
    @property
    def file_count(self) -> int:
        """文件数量"""
        return len(self.files)
    
    @property
    def total_size(self) -> int:
        """总文件大小"""
        return sum(f.size or 0 for f in self.files)


@dataclass
class LibraryStatistics:
    """库统计信息数据类"""
    
    total_files: int = 0
    """总文件数"""
    
    total_size: int = 0
    """总大小（字节）"""
    
    view_counts: Dict[str, int] = field(default_factory=dict)
    """各视图类型的文件数量"""
    
    pvt_corner_coverage: Dict[str, int] = field(default_factory=dict)
    """PVT corner覆盖情况"""
    
    completeness_score: float = 0.0
    """完整性评分（0-100）"""
    
    missing_components: List[str] = field(default_factory=list)
    """缺失的组件列表"""
    
    last_updated: Optional[datetime] = None
    """最后更新时间"""
    
    def calculate_completeness_score(self, expected_views: List[str], expected_corners: List[str]) -> float:
        """计算完整性评分"""
        if not expected_views and not expected_corners:
            return 100.0
        
        view_score = 0.0
        if expected_views:
            found_views = len([v for v in expected_views if v in self.view_counts and self.view_counts[v] > 0])
            view_score = (found_views / len(expected_views)) * 50.0
        
        corner_score = 0.0
        if expected_corners:
            found_corners = len([c for c in expected_corners if c in self.pvt_corner_coverage])
            corner_score = (found_corners / len(expected_corners)) * 50.0
        
        self.completeness_score = view_score + corner_score
        return self.completeness_score


@dataclass
class LibInfo:
    """增强的库信息数据类"""
    
    lib_name: str
    """库名称，如 sa08nvghlogl20hsf068f"""
    
    lib_path: Path
    """库路径"""
    
    lib_type: str
    """库类型：STD（标准单元库）、IP（IP库）、MEM（内存库）"""
    
    version: Optional[str] = None
    """版本信息，如 1.01a, 2.00A"""
    
    foundry: Optional[str] = None
    """Foundry名称，如 Samsung"""
    
    node: Optional[str] = None
    """工艺节点，如 LN08LPU_GP"""
    
    # 增强的元数据字段
    views: Dict[str, ViewInfo] = field(default_factory=dict)
    """视图信息字典 {view_type: ViewInfo}"""
    
    statistics: LibraryStatistics = field(default_factory=LibraryStatistics)
    """库统计信息"""
    
    metadata: Dict[str, str] = field(default_factory=dict)
    """额外的元数据信息"""
    
    created_at: Optional[datetime] = None
    """创建时间"""
    
    updated_at: Optional[datetime] = None
    """更新时间"""
    
    # 用于精细化适配器的字段
    adapter_type: Optional[str] = None
    """使用的适配器类型，如 SamsungLN08STDAdapter"""
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_view(self, view_info: ViewInfo):
        """添加视图信息"""
        self.views[view_info.view_type] = view_info
        self.updated_at = datetime.now()
    
    def get_supported_pvt_corners(self) -> Set[str]:
        """获取所有支持的PVT corners"""
        corners = set()
        for view in self.views.values():
            corners.update(view.pvt_corners)
        return corners
    
    def get_supported_view_types(self) -> List[str]:
        """获取所有支持的视图类型"""
        return list(self.views.keys())
    
    def update_statistics(self):
        """更新统计信息"""
        self.statistics.total_files = sum(view.file_count for view in self.views.values())
        self.statistics.total_size = sum(view.total_size for view in self.views.values())
        self.statistics.view_counts = {vt: view.file_count for vt, view in self.views.items()}
        
        # 更新PVT corner覆盖情况
        self.statistics.pvt_corner_coverage.clear()
        for view in self.views.values():
            for corner in view.pvt_corners:
                self.statistics.pvt_corner_coverage[corner] = self.statistics.pvt_corner_coverage.get(corner, 0) + 1
        
        self.statistics.last_updated = datetime.now()
        self.updated_at = datetime.now()
    
    def get_unique_id(self) -> str:
        """获取库的唯一标识符"""
        parts = [self.foundry or "unknown", self.node or "unknown", self.lib_type, self.lib_name]
        if self.version:
            parts.append(self.version)
        return "_".join(parts)
    
    def __str__(self) -> str:
        """字符串表示"""
        parts = [self.lib_name]
        if self.version:
            # 如果版本已经以v开头，就不再添加v前缀
            version_str = self.version if self.version.startswith('v') else f"v{self.version}"
            parts.append(version_str)
        if self.lib_type:
            parts.append(f"({self.lib_type})")
        if self.foundry and self.node:
            parts.append(f"[{self.foundry}/{self.node}]")
        return " ".join(parts)

