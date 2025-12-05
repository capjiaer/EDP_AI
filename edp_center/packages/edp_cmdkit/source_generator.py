#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Source 语句生成模块
提供生成 source 语句的功能
"""

from pathlib import Path
from typing import List, Optional
import logging

from .file_finder import find_file

# 导入框架异常类（使用别名避免与内置异常冲突）
from edp_center.packages.edp_common import EDPFileNotFoundError

logger = logging.getLogger(__name__)


def _find_similar_files(file_name: str, search_paths: List[Path], max_results: int = 5) -> List[str]:
    """
    查找相似文件名（用于拼写错误检测）
    
    Args:
        file_name: 要查找的文件名
        search_paths: 搜索路径列表
        max_results: 最大返回结果数
    
    Returns:
        相似文件名列表
    """
    from pathlib import Path
    import difflib
    
    similar_files = []
    file_base = Path(file_name).stem  # 文件名（不含扩展名）
    
    # 收集所有可能的文件
    all_files = []
    for search_path in search_paths:
        if not search_path.exists():
            continue
        try:
            # 递归查找所有文件
            for file_path in search_path.rglob('*'):
                if file_path.is_file():
                    all_files.append(file_path.name)
        except (PermissionError, OSError):
            continue
    
    # 查找相似文件名
    for candidate in all_files:
        candidate_base = Path(candidate).stem
        similarity = difflib.SequenceMatcher(None, file_base.lower(), candidate_base.lower()).ratio()
        if similarity > 0.6:  # 相似度阈值
            similar_files.append(candidate)
    
    # 按相似度排序并返回前几个
    similar_files.sort(key=lambda x: difflib.SequenceMatcher(
        None, file_base.lower(), Path(x).stem.lower()
    ).ratio(), reverse=True)
    
    return similar_files[:max_results]


def generate_source_statement(import_file: str, current_file: Path,
                             search_paths: List[Path], recursive: bool = True) -> str:
    """
    生成 source 模式：转换成 source 语句
    
    Args:
        import_file: 要导入的文件名或路径
        current_file: 当前正在处理的文件
        search_paths: 搜索路径列表
        recursive: 是否递归查找
    
    Returns:
        source 语句
    
    Raises:
        FileNotFoundError: 如果文件未找到
    """
    # 查找文件
    target_file = find_file(import_file, current_file, search_paths, recursive)
    
    if not target_file:
        # 尝试查找相似文件名（拼写错误检测）
        similar_files = _find_similar_files(import_file, search_paths)
        
        # 使用框架异常类，提供详细的错误信息
        raise EDPFileNotFoundError(
            file_path=import_file,
            search_paths=[str(p) for p in search_paths],
            current_file=str(current_file),
            similar_files=similar_files
        )
    
    # 生成 source 语句（使用绝对路径，转换为 Tcl 兼容格式）
    tcl_path = to_tcl_path(target_file)
    source_line = f"source {tcl_path}\n"
    
    return source_line

