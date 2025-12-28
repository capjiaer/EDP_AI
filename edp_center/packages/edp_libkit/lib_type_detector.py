#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Library Type Detector - 库类型自动检测器

根据目录结构自动识别库类型（STD/IP/MEM）
"""

from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class LibraryTypeDetector:
    """库类型自动检测器"""
    
    # IP库的特征目录
    IP_MARKERS = ['FE-Common', 'BE-Common']
    
    # STD库的特征目录/文件名模式
    STD_MARKERS = ['v-logic_', 'DesignWare_logic_libs', 'STD_Cell']
    
    # MEM库的特征目录
    MEM_MARKERS = ['mem_compiler', 'memory', 'SRAM', 'MEM', 'sram']
    
    @classmethod
    def detect_library_type(cls, lib_path: Path) -> Optional[str]:
        """
        自动检测库类型
        
        Args:
            lib_path: 库目录路径
            
        Returns:
            库类型：'STD', 'IP', 'MEM' 或 None（无法识别）
        """
        if not lib_path.exists() or not lib_path.is_dir():
            return None
        
        # 检查IP库特征
        if cls._is_ip_library(lib_path):
            return 'IP'
        
        # 检查MEM库特征
        if cls._is_mem_library(lib_path):
            return 'MEM'
        
        # 检查STD库特征
        if cls._is_std_library(lib_path):
            return 'STD'
        
        # 如果无法确定，尝试从父目录结构推断
        return cls._infer_from_parent_structure(lib_path)
    
    @classmethod
    def _is_ip_library(cls, lib_path: Path) -> bool:
        """判断是否为IP库"""
        # IP库通常有FE-Common或BE-Common目录
        for marker in cls.IP_MARKERS:
            if (lib_path / marker).exists():
                return True
        
        # 检查父目录是否为IP目录
        parent = lib_path.parent
        if parent.name == 'IP' or 'IP' in parent.name:
            # 检查是否有版本目录（v1.0, v1.12等）
            if lib_path.name.startswith('v') or lib_path.name.replace('.', '').isdigit():
                return True
        
        return False
    
    @classmethod
    def _is_mem_library(cls, lib_path: Path) -> bool:
        """判断是否为MEM库"""
        # 检查目录名是否包含MEM相关关键词
        lib_name_lower = lib_path.name.lower()
        for marker in cls.MEM_MARKERS:
            if marker.lower() in lib_name_lower:
                return True
        
        # 检查父目录是否为MEM相关目录
        parent = lib_path.parent
        parent_name_lower = parent.name.lower()
        for marker in cls.MEM_MARKERS:
            if marker.lower() in parent_name_lower:
                return True
        
        # 检查是否在MEM相关目录下
        for ancestor in lib_path.parents:
            if any(marker.lower() in ancestor.name.lower() for marker in cls.MEM_MARKERS):
                return True
        
        return False
    
    @classmethod
    def _is_std_library(cls, lib_path: Path) -> bool:
        """判断是否为STD库"""
        # STD库通常有v-logic_前缀
        if lib_path.name.startswith('v-logic_'):
            return True
        
        # 检查是否有DesignWare_logic_libs目录
        if (lib_path / 'DesignWare_logic_libs').exists():
            return True
        
        # 检查父目录是否为STD_Cell
        parent = lib_path.parent
        if parent.name == 'STD_Cell' or 'STD_Cell' in str(parent):
            return True
        
        # 检查是否在STD_Cell目录下
        for ancestor in lib_path.parents:
            if 'STD_Cell' in ancestor.name:
                return True
        
        return False
    
    @classmethod
    def _infer_from_parent_structure(cls, lib_path: Path) -> Optional[str]:
        """从父目录结构推断库类型"""
        # 检查父目录结构
        path_str = str(lib_path)
        
        if '/IP/' in path_str or '\\IP\\' in path_str:
            return 'IP'
        
        if '/STD_Cell/' in path_str or '\\STD_Cell\\' in path_str:
            return 'STD'
        
        if any(marker in path_str for marker in cls.MEM_MARKERS):
            return 'MEM'
        
        return None
    
    @classmethod
    def detect_library_info(cls, lib_path: Path, foundry: str, node: Optional[str] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        检测库类型、库名称和版本
        
        Args:
            lib_path: 库目录路径
            foundry: Foundry名称
            node: 节点名称（可选）
            
        Returns:
            (lib_type, lib_name, version) 元组
        """
        lib_type = cls.detect_library_type(lib_path)
        
        # 提取库名称和版本
        lib_name = None
        version = None
        
        if lib_type == 'IP':
            # IP库：目录结构通常是 IP/ip_name/version/
            # 如果当前目录是版本目录，父目录是库名
            if lib_path.name.startswith('v') or lib_path.name.replace('.', '').isdigit():
                lib_name = lib_path.parent.name
                version = lib_path.name
            else:
                lib_name = lib_path.name
                # 查找版本目录
                for item in lib_path.iterdir():
                    if item.is_dir() and (item.name.startswith('v') or item.name.replace('.', '').isdigit()):
                        version = item.name
                        break
        
        elif lib_type == 'STD':
            # STD库：目录名通常是 v-logic_libname
            if lib_path.name.startswith('v-logic_'):
                lib_name = lib_path.name.replace('v-logic_', '')
            else:
                lib_name = lib_path.name
            
            # 尝试从路径中提取版本
            for ancestor in lib_path.parents:
                # 查找版本号模式（如 2.00A, 1.01a）
                import re
                if re.match(r'^\d+\.\d+[A-Za-z]?$', ancestor.name):
                    version = ancestor.name
                    break
        
        elif lib_type == 'MEM':
            # MEM库：目录名通常是库名
            lib_name = lib_path.name
        
        else:
            # 无法识别，使用目录名作为库名
            lib_name = lib_path.name
        
        return lib_type, lib_name, version

