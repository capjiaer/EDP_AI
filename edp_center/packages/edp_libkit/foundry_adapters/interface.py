#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Foundry Adapter Interface - Foundry适配器接口

定义所有foundry适配器必须实现的接口。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from ..lib_info import LibInfo


class BaseFoundryAdapter(ABC):
    """Foundry适配器基类"""
    
    def identify_library_directories(self, ori_path: Path) -> List[LibInfo]:
        """
        识别库目录（已废弃，不再使用自动识别）
        
        注意：此方法已废弃。现在要求用户通过命令行参数明确指定库路径和类型。
        此方法保留仅为向后兼容，实际返回空列表。
        
        Args:
            ori_path: ori目录路径
            
        Returns:
            空列表（不再自动识别）
        """
        return []
    
    @abstractmethod
    def find_view_directories(self, lib_path: Path, lib_type: str = None, version: str = None) -> Dict[str, Path]:
        """
        找到视图目录
        
        在库目录中查找包含各种视图类型的目录（gds, lef, ccs_lvf等）。
        
        Args:
            lib_path: 库路径
            lib_type: 库类型（可选，用于优化查找逻辑）
            version: 指定版本号（可选）。如果指定，只查找该版本的目录
            
        Returns:
            {view_type: view_path} 字典
            例如：{'gds': Path(...), 'lef': Path(...), 'ccs_lvf': Path(...)}
            如果某个视图类型不存在，则不包含在字典中
        """
        pass
    
    @abstractmethod
    def extract_lib_info(self, lib_path: Path) -> LibInfo:
        """
        从路径提取库信息
        
        从库目录路径中提取库名称、版本等信息。
        
        Args:
            lib_path: 库路径
            
        Returns:
            LibInfo对象
        """
        pass
    
    def get_view_file_pattern(self, view_type: str) -> str:
        """
        获取视图类型的文件匹配模式
        
        Args:
            view_type: 视图类型（gds, lef, ccs_lvf等）
            
        Returns:
            文件匹配模式，如 '*.gds', '*.db' 等
        """
        patterns = {
            'gds': '*.gds',
            'lef': '*.lef',
            'ccs_lvf': '*.db',
            'cdl': '*.cdl',
            'liberty': '*.db',
            'verilog': '*.v',
        }
        return patterns.get(view_type, '*')

