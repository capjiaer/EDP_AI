#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LibraryIndex - 库索引管理器

提供集中式的库目录管理和快速搜索功能。
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from datetime import datetime
import logging

from .lib_info import LibInfo, LibraryStatistics

logger = logging.getLogger(__name__)


class LibraryIndex:
    """库索引管理器"""
    
    def __init__(self, index_path: Optional[Path] = None):
        """
        初始化库索引
        
        Args:
            index_path: 索引文件路径，如果为None则使用默认路径
        """
        if index_path is None:
            # 使用默认路径：libkit目录下的index.db
            libkit_dir = Path(__file__).parent
            index_path = libkit_dir / 'index.db'
        
        self.index_path = Path(index_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 内存中的索引缓存
        self._libraries: Dict[str, LibInfo] = {}
        self._foundries: Set[str] = set()
        self._nodes: Set[str] = set()
        self._lib_types: Set[str] = set()
        
        # 初始化数据库
        self._init_database()
        
        # 加载现有索引
        self._load_index()
    
    def _init_database(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(self.index_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS libraries (
                    id TEXT PRIMARY KEY,
                    lib_name TEXT NOT NULL,
                    lib_path TEXT NOT NULL,
                    lib_type TEXT NOT NULL,
                    version TEXT,
                    foundry TEXT,
                    node TEXT,
                    adapter_type TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata TEXT,
                    statistics TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS views (
                    lib_id TEXT,
                    view_type TEXT,
                    view_path TEXT,
                    file_count INTEGER,
                    total_size INTEGER,
                    pvt_corners TEXT,
                    FOREIGN KEY (lib_id) REFERENCES libraries (id)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_foundry_node ON libraries (foundry, node)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_lib_type ON libraries (lib_type)
            ''')
            
            conn.commit()
    
    def _load_index(self):
        """从数据库加载索引到内存"""
        try:
            with sqlite3.connect(self.index_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM libraries')
                
                for row in cursor:
                    lib_info = self._row_to_libinfo(row)
                    self._libraries[lib_info.get_unique_id()] = lib_info
                    
                    # 更新集合
                    if lib_info.foundry:
                        self._foundries.add(lib_info.foundry)
                    if lib_info.node:
                        self._nodes.add(lib_info.node)
                    self._lib_types.add(lib_info.lib_type)
                
                logger.info(f"已加载 {len(self._libraries)} 个库到索引")
        
        except Exception as e:
            logger.warning(f"加载索引失败: {e}")
    
    def _row_to_libinfo(self, row: sqlite3.Row) -> LibInfo:
        """将数据库行转换为LibInfo对象"""
        lib_info = LibInfo(
            lib_name=row['lib_name'],
            lib_path=Path(row['lib_path']),
            lib_type=row['lib_type'],
            version=row['version'],
            foundry=row['foundry'],
            node=row['node'],
            adapter_type=row['adapter_type']
        )
        
        # 解析时间戳
        if row['created_at']:
            lib_info.created_at = datetime.fromisoformat(row['created_at'])
        if row['updated_at']:
            lib_info.updated_at = datetime.fromisoformat(row['updated_at'])
        
        # 解析元数据
        if row['metadata']:
            lib_info.metadata = json.loads(row['metadata'])
        
        # 解析统计信息
        if row['statistics']:
            stats_data = json.loads(row['statistics'])
            lib_info.statistics = LibraryStatistics(**stats_data)
        
        return lib_info
    
    def add_library(self, lib_info: LibInfo) -> bool:
        """
        添加库到索引
        
        Args:
            lib_info: 库信息
            
        Returns:
            是否成功添加
        """
        try:
            lib_id = lib_info.get_unique_id()
            
            # 更新内存索引
            self._libraries[lib_id] = lib_info
            
            # 更新集合
            if lib_info.foundry:
                self._foundries.add(lib_info.foundry)
            if lib_info.node:
                self._nodes.add(lib_info.node)
            self._lib_types.add(lib_info.lib_type)
            
            # 更新数据库
            self._save_library_to_db(lib_info)
            
            logger.debug(f"已添加库到索引: {lib_info}")
            return True
            
        except Exception as e:
            logger.error(f"添加库到索引失败: {e}")
            return False
    
    def _save_library_to_db(self, lib_info: LibInfo):
        """保存库信息到数据库"""
        with sqlite3.connect(self.index_path) as conn:
            lib_id = lib_info.get_unique_id()
            
            # 序列化复杂数据
            metadata_json = json.dumps(lib_info.metadata) if lib_info.metadata else None
            statistics_json = json.dumps({
                'total_files': lib_info.statistics.total_files,
                'total_size': lib_info.statistics.total_size,
                'view_counts': lib_info.statistics.view_counts,
                'pvt_corner_coverage': lib_info.statistics.pvt_corner_coverage,
                'completeness_score': lib_info.statistics.completeness_score,
                'missing_components': lib_info.statistics.missing_components,
                'last_updated': lib_info.statistics.last_updated.isoformat() if lib_info.statistics.last_updated else None
            })
            
            # 插入或更新库信息
            conn.execute('''
                INSERT OR REPLACE INTO libraries 
                (id, lib_name, lib_path, lib_type, version, foundry, node, adapter_type, 
                 created_at, updated_at, metadata, statistics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lib_id,
                lib_info.lib_name,
                str(lib_info.lib_path),
                lib_info.lib_type,
                lib_info.version,
                lib_info.foundry,
                lib_info.node,
                lib_info.adapter_type,
                lib_info.created_at.isoformat() if lib_info.created_at else None,
                lib_info.updated_at.isoformat() if lib_info.updated_at else None,
                metadata_json,
                statistics_json
            ))
            
            # 删除旧的视图信息
            conn.execute('DELETE FROM views WHERE lib_id = ?', (lib_id,))
            
            # 插入视图信息
            for view_type, view_info in lib_info.views.items():
                conn.execute('''
                    INSERT INTO views (lib_id, view_type, view_path, file_count, total_size, pvt_corners)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    lib_id,
                    view_type,
                    str(view_info.view_path),
                    view_info.file_count,
                    view_info.total_size,
                    json.dumps(list(view_info.pvt_corners))
                ))
            
            conn.commit()
    
    def get_library(self, lib_id: str) -> Optional[LibInfo]:
        """根据ID获取库信息"""
        return self._libraries.get(lib_id)
    
    def search_libraries(self, 
                        foundry: Optional[str] = None,
                        node: Optional[str] = None,
                        lib_type: Optional[str] = None,
                        lib_name_pattern: Optional[str] = None) -> List[LibInfo]:
        """
        搜索库
        
        Args:
            foundry: Foundry名称
            node: 节点名称
            lib_type: 库类型
            lib_name_pattern: 库名称模式（支持通配符）
            
        Returns:
            匹配的库列表
        """
        results = []
        
        for lib_info in self._libraries.values():
            # 检查foundry
            if foundry and lib_info.foundry != foundry:
                continue
            
            # 检查node
            if node and lib_info.node != node:
                continue
            
            # 检查lib_type
            if lib_type and lib_info.lib_type != lib_type:
                continue
            
            # 检查库名称模式
            if lib_name_pattern:
                import fnmatch
                if not fnmatch.fnmatch(lib_info.lib_name, lib_name_pattern):
                    continue
            
            results.append(lib_info)
        
        return results
    
    def get_foundries(self) -> List[str]:
        """获取所有foundry列表"""
        return sorted(list(self._foundries))
    
    def get_nodes(self, foundry: Optional[str] = None) -> List[str]:
        """获取节点列表"""
        if foundry:
            nodes = set()
            for lib_info in self._libraries.values():
                if lib_info.foundry == foundry and lib_info.node:
                    nodes.add(lib_info.node)
            return sorted(list(nodes))
        else:
            return sorted(list(self._nodes))
    
    def get_lib_types(self, foundry: Optional[str] = None, node: Optional[str] = None) -> List[str]:
        """获取库类型列表"""
        if foundry or node:
            lib_types = set()
            for lib_info in self._libraries.values():
                if foundry and lib_info.foundry != foundry:
                    continue
                if node and lib_info.node != node:
                    continue
                lib_types.add(lib_info.lib_type)
            return sorted(list(lib_types))
        else:
            return sorted(list(self._lib_types))
    
    def get_statistics(self) -> Dict[str, int]:
        """获取索引统计信息"""
        return {
            'total_libraries': len(self._libraries),
            'foundries': len(self._foundries),
            'nodes': len(self._nodes),
            'lib_types': len(self._lib_types)
        }
    
    def remove_library(self, lib_id: str) -> bool:
        """从索引中移除库"""
        try:
            if lib_id in self._libraries:
                del self._libraries[lib_id]
                
                # 从数据库删除
                with sqlite3.connect(self.index_path) as conn:
                    conn.execute('DELETE FROM views WHERE lib_id = ?', (lib_id,))
                    conn.execute('DELETE FROM libraries WHERE id = ?', (lib_id,))
                    conn.commit()
                
                # 重新构建集合（简单方法）
                self._rebuild_sets()
                
                logger.debug(f"已从索引移除库: {lib_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"从索引移除库失败: {e}")
            return False
    
    def _rebuild_sets(self):
        """重新构建foundry/node/lib_type集合"""
        self._foundries.clear()
        self._nodes.clear()
        self._lib_types.clear()
        
        for lib_info in self._libraries.values():
            if lib_info.foundry:
                self._foundries.add(lib_info.foundry)
            if lib_info.node:
                self._nodes.add(lib_info.node)
            self._lib_types.add(lib_info.lib_type)
    
    def clear_index(self):
        """清空索引"""
        self._libraries.clear()
        self._foundries.clear()
        self._nodes.clear()
        self._lib_types.clear()
        
        with sqlite3.connect(self.index_path) as conn:
            conn.execute('DELETE FROM views')
            conn.execute('DELETE FROM libraries')
            conn.commit()
        
        logger.info("已清空库索引")