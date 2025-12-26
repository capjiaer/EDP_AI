#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CacheManager - 缓存管理器

提供基于时间戳的智能缓存失效机制。
"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, data: Any, source_path: Optional[Path] = None):
        """
        初始化缓存条目
        
        Args:
            data: 缓存的数据
            source_path: 源文件路径（用于时间戳检查）
        """
        self.data = data
        self.source_path = source_path
        self.created_at = datetime.now()
        self.accessed_at = datetime.now()
        
        # 记录源文件的修改时间
        self.source_mtime = None
        if source_path and source_path.exists():
            self.source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime)
    
    def is_valid(self, max_age: Optional[timedelta] = None) -> bool:
        """
        检查缓存条目是否有效
        
        Args:
            max_age: 最大缓存时间，如果为None则只检查源文件时间戳
            
        Returns:
            缓存是否有效
        """
        # 检查最大缓存时间
        if max_age and (datetime.now() - self.created_at) > max_age:
            return False
        
        # 检查源文件是否被修改
        if self.source_path and self.source_path.exists():
            current_mtime = datetime.fromtimestamp(self.source_path.stat().st_mtime)
            if self.source_mtime and current_mtime > self.source_mtime:
                return False
        elif self.source_path and not self.source_path.exists():
            # 源文件被删除
            return False
        
        return True
    
    def touch(self):
        """更新访问时间"""
        self.accessed_at = datetime.now()


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_memory_entries: int = 1000):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录，如果为None则使用默认目录
            max_memory_entries: 内存缓存的最大条目数
        """
        if cache_dir is None:
            # 使用默认缓存目录
            libkit_dir = Path(__file__).parent
            cache_dir = libkit_dir / 'cache'
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_memory_entries = max_memory_entries
        
        # 内存缓存
        self._memory_cache: Dict[str, CacheEntry] = {}
        
        # 缓存统计
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存键的哈希值"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def get(self, key: str, max_age: Optional[timedelta] = None) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            max_age: 最大缓存时间
            
        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        cache_key = self._get_cache_key(key)
        
        # 首先检查内存缓存
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if entry.is_valid(max_age):
                entry.touch()
                self._stats['hits'] += 1
                logger.debug(f"内存缓存命中: {key}")
                return entry.data
            else:
                # 缓存过期，删除
                del self._memory_cache[cache_key]
        
        # 检查磁盘缓存
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                
                if entry.is_valid(max_age):
                    # 加载到内存缓存
                    entry.touch()
                    self._add_to_memory_cache(cache_key, entry)
                    self._stats['hits'] += 1
                    logger.debug(f"磁盘缓存命中: {key}")
                    return entry.data
                else:
                    # 缓存过期，删除文件
                    cache_file.unlink()
            
            except Exception as e:
                logger.warning(f"读取缓存文件失败: {e}")
                # 删除损坏的缓存文件
                try:
                    cache_file.unlink()
                except:
                    pass
        
        self._stats['misses'] += 1
        logger.debug(f"缓存未命中: {key}")
        return None
    
    def set(self, key: str, data: Any, source_path: Optional[Path] = None, 
            persist_to_disk: bool = True) -> bool:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            source_path: 源文件路径（用于时间戳检查）
            persist_to_disk: 是否持久化到磁盘
            
        Returns:
            是否成功设置
        """
        try:
            cache_key = self._get_cache_key(key)
            entry = CacheEntry(data, source_path)
            
            # 添加到内存缓存
            self._add_to_memory_cache(cache_key, entry)
            
            # 持久化到磁盘
            if persist_to_disk:
                cache_file = self._get_cache_file_path(cache_key)
                with open(cache_file, 'wb') as f:
                    pickle.dump(entry, f)
            
            logger.debug(f"已缓存: {key}")
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def _add_to_memory_cache(self, cache_key: str, entry: CacheEntry):
        """添加条目到内存缓存"""
        # 检查是否需要清理内存缓存
        if len(self._memory_cache) >= self.max_memory_entries:
            self._evict_lru_entries()
        
        self._memory_cache[cache_key] = entry
    
    def _evict_lru_entries(self):
        """清理最近最少使用的缓存条目"""
        if not self._memory_cache:
            return
        
        # 按访问时间排序，删除最旧的条目
        sorted_entries = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].accessed_at
        )
        
        # 删除最旧的25%条目
        evict_count = max(1, len(sorted_entries) // 4)
        for i in range(evict_count):
            cache_key, _ = sorted_entries[i]
            del self._memory_cache[cache_key]
            self._stats['evictions'] += 1
        
        logger.debug(f"已清理 {evict_count} 个内存缓存条目")
    
    def invalidate(self, key: str) -> bool:
        """
        使缓存失效
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功失效
        """
        cache_key = self._get_cache_key(key)
        
        # 从内存缓存删除
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        
        # 删除磁盘缓存文件
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.debug(f"已失效缓存: {key}")
                return True
            except Exception as e:
                logger.error(f"删除缓存文件失败: {e}")
                return False
        
        return True
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        使匹配模式的缓存失效
        
        Args:
            pattern: 缓存键模式（支持通配符）
            
        Returns:
            失效的缓存数量
        """
        import fnmatch
        
        invalidated_count = 0
        
        # 内存缓存中查找匹配的键
        keys_to_remove = []
        for cache_key in self._memory_cache.keys():
            # 这里需要反向查找原始key，简化处理，直接清空内存缓存
            pass
        
        # 磁盘缓存中查找匹配的文件
        for cache_file in self.cache_dir.glob("*.cache"):
            # 简化处理：如果模式是通配符，删除所有缓存文件
            if '*' in pattern or '?' in pattern:
                try:
                    cache_file.unlink()
                    invalidated_count += 1
                except:
                    pass
        
        # 如果是通配符模式，清空内存缓存
        if '*' in pattern or '?' in pattern:
            memory_count = len(self._memory_cache)
            self._memory_cache.clear()
            invalidated_count += memory_count
        
        logger.debug(f"已失效 {invalidated_count} 个缓存条目")
        return invalidated_count
    
    def clear_all(self):
        """清空所有缓存"""
        # 清空内存缓存
        self._memory_cache.clear()
        
        # 删除所有磁盘缓存文件
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
            except:
                pass
        
        logger.info("已清空所有缓存")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'evictions': self._stats['evictions'],
            'hit_rate': f"{hit_rate:.1f}%",
            'memory_entries': len(self._memory_cache),
            'disk_files': len(list(self.cache_dir.glob("*.cache")))
        }
    
    def cleanup_expired(self, max_age: timedelta = timedelta(days=7)):
        """
        清理过期的缓存文件
        
        Args:
            max_age: 最大缓存时间
        """
        cleaned_count = 0
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                # 检查文件修改时间
                file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if (datetime.now() - file_mtime) > max_age:
                    cache_file.unlink()
                    cleaned_count += 1
            except:
                # 删除无法访问的文件
                try:
                    cache_file.unlink()
                    cleaned_count += 1
                except:
                    pass
        
        logger.info(f"已清理 {cleaned_count} 个过期缓存文件")