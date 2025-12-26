#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Foundry Adapter - Foundry适配器

统一的foundry适配器入口，根据foundry和node动态加载对应的适配器
"""

from pathlib import Path
from typing import Dict, List, Optional
import importlib

from .interface import BaseFoundryAdapter
from ..lib_info import LibInfo


class FoundryAdapter(BaseFoundryAdapter):
    """统一的foundry适配器"""
    
    def __init__(self, foundry: str, node: Optional[str] = None):
        self.foundry = foundry.lower()
        self.node = node.lower() if node else None
        self._node_adapter = None
        
        # 加载节点适配器
        if self.node:
            self._load_node_adapter()
    
    def _load_node_adapter(self):
        """动态加载节点适配器"""
        # 对于 Samsung、SMIC、TSMC，使用通用的 BaseNodeAdapter
        # 配置文件路径：{foundry}/{node_key}.config.yaml
        if self.foundry in ['samsung', 'smic', 'tsmc']:
            try:
                from .node_adapter import BaseNodeAdapter
                self._node_adapter = BaseNodeAdapter(self.foundry, self.node)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not load adapter for {self.foundry}/{self.node}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                self._node_adapter = None
        else:
            # 对于其他 foundry，尝试从节点目录加载 adapter.py（向后兼容）
            try:
                module_path = f"edp_center.packages.edp_libkit.foundry_adapters.{self.foundry}.{self.node}.adapter"
                module = importlib.import_module(module_path)
                adapter_class = getattr(module, 'NodeAdapter')
                self._node_adapter = adapter_class()
            except (ImportError, AttributeError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not load adapter for {self.foundry}/{self.node}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                self._node_adapter = None
    
    def get_supported_nodes(self) -> List[str]:
        """获取支持的节点列表（通过扫描 YAML 配置文件）"""
        # 扫描 foundry 目录下的 *.config.yaml 文件
        foundry_dir = Path(__file__).parent / self.foundry
        if not foundry_dir.exists():
            return []
        
        supported_nodes = []
        for config_file in foundry_dir.glob('*.config.yaml'):
            # 从文件名提取节点键名（例如：ln08lpu_gp.config.yaml -> ln08lpu_gp）
            node_key = config_file.stem.replace('.config', '')
            supported_nodes.append(node_key)
        
        return sorted(supported_nodes)
    
    def identify_library_directories(self, ori_path: Path) -> List[LibInfo]:
        """
        识别库目录（已废弃）
        
        注意：此方法已废弃。现在要求用户通过命令行参数明确指定库路径和类型。
        此方法保留仅为向后兼容，实际返回空列表。
        """
        return []
    
    def find_view_directories(self, lib_path: Path, lib_type: str = None, version: str = None) -> Dict[str, Path]:
        """查找视图目录"""
        if self._node_adapter:
            return self._node_adapter.find_view_directories(lib_path, lib_type, version=version)
        else:
            # 如果没有节点适配器，无法查找视图目录
            if self.node:
                raise RuntimeError(
                    f"无法加载节点适配器: {self.foundry}/{self.node}. "
                    f"无法查找视图目录。"
                )
            else:
                raise ValueError(
                    f"未指定节点（--node参数）。"
                    f"请使用 --node 参数指定工艺节点。"
                )
    
    def extract_lib_info(self, lib_path: Path) -> LibInfo:
        """提取库信息"""
        if self._node_adapter:
            return self._node_adapter.extract_lib_info(lib_path)
        else:
            # 如果没有节点适配器，返回基本的LibInfo
            # 但这种情况应该避免，建议指定node参数
            return LibInfo(
                lib_name=lib_path.name,
                lib_path=lib_path,
                lib_type='UNKNOWN',
                foundry=self.foundry,
                node=self.node
            )
    
    def get_standard_view_types(self, lib_type: str) -> List[str]:
        """获取标准视图类型列表"""
        if self._node_adapter:
            if hasattr(self._node_adapter, 'get_standard_view_types'):
                return self._node_adapter.get_standard_view_types(lib_type)
        return []
    
    def get_view_file_pattern(self, view_type: str) -> List[str]:
        """获取视图类型的文件匹配模式"""
        if self._node_adapter:
            # 如果节点适配器有这个方法，使用它的实现
            if hasattr(self._node_adapter, 'get_view_file_pattern'):
                return self._node_adapter.get_view_file_pattern(view_type)
        # 否则使用基类的默认实现
        return super().get_view_file_pattern(view_type)
    
    def extract_rc_corner(self, pvt_corner: str) -> str:
        """提取RC corner"""
        if self._node_adapter:
            # 如果节点适配器有这个方法，使用它的实现
            if hasattr(self._node_adapter, 'extract_rc_corner'):
                return self._node_adapter.extract_rc_corner(pvt_corner)
        # 默认实现
        if pvt_corner.startswith('ff'):
            return 'sigcmin'
        elif pvt_corner.startswith('ss'):
            return 'sigcmax'
        elif pvt_corner.startswith('tt'):
            return 'typical'
        else:
            return 'typical'


class AdapterFactory:
    """适配器工厂"""
    
    @staticmethod
    def create_adapter(foundry: str, node: Optional[str] = None) -> FoundryAdapter:
        """创建适配器实例"""
        return FoundryAdapter(foundry, node)
    
    @staticmethod
    def get_supported_foundries() -> List[str]:
        """获取支持的foundry列表"""
        # 扫描foundry_adapters目录下的子目录
        foundries_dir = Path(__file__).parent
        foundries = []
        
        for item in foundries_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # 检查是否有 *.config.yaml 文件（表示这是一个支持的 foundry）
                config_files = list(item.glob('*.config.yaml'))
                if config_files:
                    foundries.append(item.name)
        
        return sorted(foundries)
    
    @staticmethod
    def get_supported_nodes(foundry: str) -> List[str]:
        """获取指定foundry支持的节点列表"""
        adapter = FoundryAdapter(foundry)
        return adapter.get_supported_nodes()

