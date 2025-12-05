#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径工具模块

提供路径格式转换、文件名清理等通用路径操作。
"""

from pathlib import Path
from typing import Union
import re
from datetime import datetime


def to_tcl_path(path: Union[str, Path]) -> str:
    """
    将路径转换为 Tcl 兼容格式（使用正斜杠）
    
    Tcl 使用正斜杠作为路径分隔符，即使在 Windows 上也是如此。
    此函数将 Windows 路径的反斜杠转换为正斜杠。
    
    Args:
        path: 路径（字符串或 Path 对象）
    
    Returns:
        Tcl 兼容的路径字符串（使用正斜杠）
    
    Example:
        >>> to_tcl_path(Path('C:/Users/test/file.tcl'))
        'C:/Users/test/file.tcl'
        >>> to_tcl_path('C:\\Users\\test\\file.tcl')
        'C:/Users/test/file.tcl'
        >>> to_tcl_path('/home/user/file.tcl')
        '/home/user/file.tcl'
    """
    if isinstance(path, Path):
        return str(path).replace('\\', '/')
    return str(path).replace('\\', '/')


def sanitize_filename(name: str, max_length: int = 255) -> str:
    """
    清理文件名，移除或替换不安全的字符
    
    用于生成安全的文件名，避免文件系统不支持的字符。
    
    Args:
        name: 原始文件名
        max_length: 最大长度（默认 255）
    
    Returns:
        清理后的文件名
    
    Example:
        >>> sanitize_filename('pnr_innovus.place')
        'pnr_innovus_place'
        >>> sanitize_filename('test<>file')
        'test__file'
    """
    # 替换点号为下划线（用于步骤名称，如 pnr_innovus.place -> pnr_innovus_place）
    name = name.replace('.', '_')
    
    # 移除其他不安全字符（Windows 和 Unix 都不支持）
    # < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    
    # 移除控制字符
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    
    # 限制长度
    if len(name) > max_length:
        name = name[:max_length]
    
    # 移除首尾空格和下划线
    name = name.strip(' _')
    
    # 如果结果为空，使用默认名称
    if not name:
        name = 'file'
    
    return name


def generate_log_filename(base_name: str, 
                         extension: str = '.log',
                         timestamp_format: str = '%Y%m%d_%H%M%S') -> str:
    """
    生成日志文件名
    
    格式：{sanitized_base_name}_{timestamp}{extension}
    
    Args:
        base_name: 基础名称（如步骤名称）
        extension: 文件扩展名（默认 .log）
        timestamp_format: 时间戳格式（默认 '%Y%m%d_%H%M%S'）
    
    Returns:
        完整的日志文件名
    
    Example:
        >>> generate_log_filename('pnr_innovus.place')
        'pnr_innovus_place_20240115_143022.log'
    """
    timestamp = datetime.now().strftime(timestamp_format)
    safe_name = sanitize_filename(base_name)
    return f'{safe_name}_{timestamp}{extension}'


def ensure_dir(path: Union[str, Path], parents: bool = True) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        parents: 是否创建父目录（默认 True）
    
    Returns:
        Path 对象
    
    Example:
        >>> ensure_dir('/path/to/dir')
        Path('/path/to/dir')
    """
    path = Path(path)
    path.mkdir(parents=parents, exist_ok=True)
    return path

