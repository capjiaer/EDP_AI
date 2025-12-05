#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件查找模块
提供在搜索路径中查找文件的功能
支持文件搜索缓存以提升性能
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
import os

# 文件搜索缓存
# 结构: {(search_path, file_name): (result_path, timestamp)}
_file_cache: Dict[Tuple[Path, str], Tuple[Optional[Path], float]] = {}

# 目录时间戳缓存
# 结构: {search_path: timestamp}
_dir_timestamps: Dict[Path, float] = {}


def _get_dir_timestamp(search_path: Path) -> float:
    """
    获取目录的修改时间戳（用于缓存失效判断）
    
    Args:
        search_path: 搜索路径
        
    Returns:
        目录的修改时间戳
    """
    if search_path not in _dir_timestamps:
        try:
            # 获取目录的修改时间
            _dir_timestamps[search_path] = os.path.getmtime(str(search_path))
        except OSError:
            # 如果目录不存在或无法访问，返回 0
            _dir_timestamps[search_path] = 0.0
    
    return _dir_timestamps[search_path]


def _is_cache_valid(search_path: Path, file_name: str) -> bool:
    """
    检查缓存是否有效
    
    Args:
        search_path: 搜索路径
        file_name: 文件名
        
    Returns:
        如果缓存有效返回 True，否则返回 False
    """
    cache_key = (search_path, file_name)
    
    if cache_key not in _file_cache:
        return False
    
    # 检查目录是否被修改（获取最新时间戳）
    try:
        current_timestamp = os.path.getmtime(str(search_path))
    except OSError:
        # 如果目录不存在或无法访问，缓存失效
        return False
    
    # 获取缓存时的时间戳
    _, cached_timestamp = _file_cache[cache_key]
    
    # 如果目录时间戳发生变化，缓存失效
    if current_timestamp != cached_timestamp:
        # 更新目录时间戳缓存
        _dir_timestamps[search_path] = current_timestamp
        return False
    
    return True


def _get_cached_result(search_path: Path, file_name: str) -> Optional[Path]:
    """
    从缓存获取搜索结果
    
    Args:
        search_path: 搜索路径
        file_name: 文件名
        
    Returns:
        缓存的搜索结果，如果缓存无效或不存在返回 None
    """
    if not _is_cache_valid(search_path, file_name):
        return None
    
    cache_key = (search_path, file_name)
    result, _ = _file_cache[cache_key]
    return result


def _cache_result(search_path: Path, file_name: str, result: Optional[Path]):
    """
    缓存搜索结果
    
    Args:
        search_path: 搜索路径
        file_name: 文件名
        result: 搜索结果
    """
    cache_key = (search_path, file_name)
    timestamp = _get_dir_timestamp(search_path)
    _file_cache[cache_key] = (result, timestamp)


def clear_file_cache():
    """
    清除文件搜索缓存
    
    用于在目录结构发生重大变化时手动清除缓存
    """
    global _file_cache, _dir_timestamps
    _file_cache.clear()
    _dir_timestamps.clear()


def find_file(import_file: str, current_file: Path, search_paths: List[Path], recursive: bool = True) -> Optional[Path]:
    """
    在搜索路径中查找文件
    
    查找顺序：
    1. 如果是绝对路径，直接检查
    2. 相对当前文件的路径
    3. 在搜索路径列表中查找（按顺序）
    
    Args:
        import_file: 要查找的文件名或路径
        current_file: 当前文件（用于解析相对路径）
        search_paths: 搜索路径列表
        recursive: 是否递归查找子目录
    
    Returns:
        找到的文件路径，如果未找到返回 None
    """
    import_path = Path(import_file)
    
    # 如果是绝对路径，直接检查
    if import_path.is_absolute():
        if import_path.exists():
            return import_path
        return None
    
    # 尝试相对当前文件的路径
    relative_to_current = (current_file.parent / import_path).resolve()
    if relative_to_current.exists():
        return relative_to_current
    
    # 在搜索路径中查找
    for search_path in search_paths:
        # 直接查找（不使用缓存，因为这是快速路径）
        candidate = (search_path / import_path).resolve()
        if candidate.exists():
            return candidate
        
        # 递归查找子目录（如果直接查找失败且 recursive=True）
        # 只在 import_path 不包含路径分隔符时递归查找
        if recursive:
            if '/' not in str(import_path) and '\\' not in str(import_path):
                # 检查缓存
                cached_result = _get_cached_result(search_path, import_file)
                if cached_result is not None:
                    # 验证缓存的文件是否仍然存在
                    if cached_result.exists():
                        return cached_result
                    # 如果缓存的文件不存在了，清除该缓存项
                    cache_key = (search_path, import_file)
                    if cache_key in _file_cache:
                        del _file_cache[cache_key]
                elif _is_cache_valid(search_path, import_file):
                    # 缓存有效且结果为 None（之前确认未找到）
                    # 验证目录是否仍然未修改（如果修改了，可能新增了文件）
                    return None
                
                # 递归搜索所有子目录（性能瓶颈所在）
                result = None
                for subdir in search_path.rglob('*'):
                    if subdir.is_dir():
                        candidate = (subdir / import_path).resolve()
                        if candidate.exists():
                            result = candidate
                            break
                
                # 缓存结果（包括未找到的情况）
                _cache_result(search_path, import_file, result)
                
                if result:
                    return result
    
    return None

