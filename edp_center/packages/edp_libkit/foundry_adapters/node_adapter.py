#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Node Adapter - 节点适配器实现

包含所有 foundry 节点共享的逻辑，通过 foundry 参数区分不同 foundry 的特殊处理
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

from .interface import BaseFoundryAdapter
from ..lib_info import LibInfo

logger = logging.getLogger(__name__)


class BaseNodeAdapter(BaseFoundryAdapter):
    """节点适配器实现类"""
    
    def __init__(self, foundry: str, node_key: str):
        """
        初始化适配器
        
        Args:
            foundry: Foundry 名称（如 'samsung', 'smic', 'tsmc'）
            node_key: 节点键名（如 'ln08lpu_gp', 'n7', 'n5'）
        """
        self.foundry = foundry
        self.node_key = node_key
        
        # 从节点目录加载 YAML 配置表（包含元数据、PVT corner映射、视图类型和文件模式）
        self._load_node_config()
        
        # 验证节点配置是否加载成功
        if not self.node_info:
            raise ValueError(f"未知的节点或配置文件不存在: {foundry}/{node_key}")
    
    def _load_node_config(self):
        """
        从 foundry 目录加载 YAML 配置文件
        
        配置文件路径：foundry_adapters/{foundry}/{node_key}.config.yaml
        配置文件包含：
        - node_info: 节点元数据（name, description等）
        - pvt_corner_mapping: PVT corner 映射规则
        - standard_view_types: 视图类型配置
        - view_file_patterns: 文件模式配置
        """
        # 获取当前文件所在目录的父目录（foundry_adapters）
        current_file = Path(__file__)
        foundry_adapters_dir = current_file.parent
        foundry_dir = foundry_adapters_dir / self.foundry
        config_file = foundry_dir / f'{self.node_key}.config.yaml'
        
        # 初始化配置
        self.node_info = {}
        self.pvt_corner_mapping = {}
        self.standard_view_types = {}
        self.view_file_patterns = {}
        
        if config_file.exists():
            if yaml is None:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"无法加载节点配置 {config_file}: 需要安装 PyYAML (pip install pyyaml)")
                return
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                # 加载节点元数据
                self.node_info = config.get('node_info', {})
                
                # 加载 PVT corner 映射规则
                self.pvt_corner_mapping = config.get('pvt_corner_mapping', {})
                
                # 加载视图类型配置
                self.standard_view_types = config.get('standard_view_types', {})
                
                # 加载文件模式配置
                self.view_file_patterns = config.get('view_file_patterns', {})
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"无法加载节点配置 {config_file}: {e}")
                # 使用空配置，避免崩溃
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"节点配置文件不存在: {config_file}")
    
    def get_standard_view_types(self, lib_type: str) -> List[str]:
        """
        获取指定库类型的标准视图类型列表
        
        从节点的 YAML 配置文件中读取。
        
        Args:
            lib_type: 库类型（STD/IP/MEM）
            
        Returns:
            视图类型列表，如 ['gds', 'lef', 'ccs_lvf', ...]
        """
        return self.standard_view_types.get(lib_type, [])
    
    def get_view_file_pattern(self, view_type: str):
        """
        获取视图类型的文件匹配模式
        
        从节点的 YAML 配置文件中读取。
        支持返回单个模式字符串或模式列表。
        
        Args:
            view_type: 视图类型（gds, lef, ccs_lvf等）
            
        Returns:
            文件匹配模式（字符串）或模式列表（列表）
        """
        patterns = self.view_file_patterns.get(view_type, ['*'])
        
        # 如果只有一个模式，返回字符串（向后兼容）
        if len(patterns) == 1:
            return patterns[0]
        
        # 多个模式返回列表
        return patterns
    
    def identify_library_directories(self, ori_path: Path) -> List[LibInfo]:
        """
        识别库目录（已废弃）
        
        注意：此方法已废弃。现在要求用户通过命令行参数明确指定库路径和类型。
        此方法保留仅为向后兼容，实际返回空列表。
        """
        return []
    
    def find_view_directories(self, lib_path: Path, lib_type: str = None, version: str = None) -> Dict[str, Path]:
        """
        查找视图目录
        
        Args:
            lib_path: 库路径
            lib_type: 库类型（可选）
            version: 指定版本号（可选）。如果指定，只查找该版本的目录
        """
        view_dirs = {}
        
        # 判断库类型并使用相应的查找逻辑
        if lib_type == 'IP' or self._is_ip_library(lib_path):
            view_dirs.update(self._find_ip_view_directories(lib_path, version=version))
        elif lib_type == 'MEM' or self._is_mem_library(lib_path):
            view_dirs.update(self._find_mem_view_directories(lib_path, version=version))
        else:
            view_dirs.update(self._find_std_view_directories(lib_path, version=version))
        
        return view_dirs
    
    def _find_std_view_directories(self, lib_path: Path, version: str = None) -> Dict[str, Path]:
        """
        查找标准单元库视图目录
        
        Args:
            lib_path: 库路径
            version: 指定版本号（可选）。如果指定，只查找该版本的目录；如果为None，使用最新版本
        """
        view_dirs = {}
        
        # 检查是否是安装目录（包含 v-logic_* 子目录）
        # 如果是，自动查找并处理第一个 v-logic_* 子目录
        if lib_path.is_dir():
            v_logic_dirs = list(lib_path.glob('v-logic_*'))
            if v_logic_dirs and not any(lib_path / vt for vt in self.get_standard_view_types('STD') if (lib_path / vt).exists()):
                # 这是安装目录，使用第一个 v-logic_* 子目录
                actual_lib_path = v_logic_dirs[0]
                logger.debug(f"检测到安装目录，使用子目录: {actual_lib_path}")
                lib_path = actual_lib_path
        
        # 确定要查找的版本
        target_version = version
        if not target_version:
            # 如果没有指定版本，使用最新版本
            target_version = self._extract_version(lib_path)
        
        if target_version:
            # 查找指定版本的目录
            version_path = self._find_version_path(lib_path, target_version)
            if version_path:
                # 在版本目录下查找视图
                for root, dirs, files in os.walk(version_path):
                    root_path = Path(root)
                    
                    # 使用 get_standard_view_types() 方法获取视图类型列表
                    for view_type in self.get_standard_view_types('STD'):
                        view_dir = root_path / view_type
                        if view_dir.exists() and view_dir.is_dir():
                            if view_type == 'liberty':
                                # Liberty目录下的子目录
                                for subdir in ['ccs_lvf', 'ccs_power', 'logic_synth']:
                                    subdir_path = view_dir / subdir
                                    if subdir_path.exists():
                                        view_dirs[subdir] = subdir_path
                            else:
                                if view_type not in view_dirs:
                                    view_dirs[view_type] = view_dir
        
        # 如果通过版本路径没有找到足够的视图目录，回退到遍历所有目录
        # 这样可以处理版本提取错误或缺少部分视图目录的情况
        if len(view_dirs) < 2:
            # 遍历所有目录查找视图
            for root, dirs, files in os.walk(lib_path):
                root_path = Path(root)
                
                # 跳过视图目录的子目录（如 lef/5.8 中的 5.8）
                # 避免把视图目录的子目录当作版本目录
                if root_path.parent.name in self.get_standard_view_types('STD'):
                    continue
                
                # 使用 get_standard_view_types() 方法获取视图类型列表
                for view_type in self.get_standard_view_types('STD'):
                    view_dir = root_path / view_type
                    if view_dir.exists() and view_dir.is_dir():
                        if view_type == 'liberty':
                            # Liberty目录下的子目录
                            for subdir in ['ccs_lvf', 'ccs_power', 'logic_synth']:
                                subdir_path = view_dir / subdir
                                if subdir_path.exists():
                                    view_dirs[subdir] = subdir_path
                        else:
                            if view_type not in view_dirs:
                                view_dirs[view_type] = view_dir
        
        return view_dirs
    
    def _find_version_path(self, lib_path: Path, version: str) -> Optional[Path]:
        """
        查找包含指定版本的目录路径
        
        Args:
            lib_path: 库根目录
            version: 版本字符串（如 '2.00A'）
            
        Returns:
            包含该版本的目录路径，如果未找到返回None
        """
        # 在库目录下查找包含该版本名的目录
        for root, dirs, files in os.walk(lib_path):
            if version in dirs:
                version_path = Path(root) / version
                if version_path.exists() and version_path.is_dir():
                    return version_path
        
        return None
    
    def _find_ip_view_directories(self, lib_path: Path, version: str = None) -> Dict[str, Path]:
        """查找IP库视图目录"""
        view_dirs = {}
        
        # FE-Common和BE-Common目录
        for common_dir in ['FE-Common', 'BE-Common']:
            common_path = lib_path / common_dir
            if common_path.exists():
                for item in common_path.iterdir():
                    if item.is_dir():
                        view_type = item.name.lower()
                        if view_type == 'liberty':
                            view_type = 'ccs_lvf'
                        view_dirs[view_type] = item
        
        return view_dirs
    
    def _find_mem_view_directories(self, lib_path: Path, version: str = None) -> Dict[str, Path]:
        """查找MEM库视图目录"""
        view_dirs = {}
        
        # MEM库的视图类型 - 使用 get_standard_view_types() 方法
        mem_view_types = self.get_standard_view_types('MEM')
        if not mem_view_types:
            # 如果没有定义，使用默认值
            mem_view_types = ['gds', 'lef', 'liberty', 'verilog', 'spice']
        
        for view_type in mem_view_types:
            view_dir = lib_path / view_type
            if view_dir.exists() and view_dir.is_dir():
                if view_type == 'liberty':
                    # Liberty目录下的子目录
                    for subdir in ['ccs_lvf', 'ccs_power', 'logic_synth']:
                        subdir_path = view_dir / subdir
                        if subdir_path.exists():
                            view_dirs[subdir] = subdir_path
                else:
                    if view_type not in view_dirs:
                        view_dirs[view_type] = view_dir
        
        return view_dirs
    
    def extract_lib_info(self, lib_path: Path) -> LibInfo:
        """
        提取库信息
        
        注意：库类型现在由用户通过命令行参数指定，不再自动判断。
        此方法只提取库名称和版本信息。
        """
        lib_name = lib_path.name
        version = None
        actual_lib_path = lib_path
        
        # 检查是否是安装目录（包含 v-logic_* 子目录）
        # 如果是，使用第一个 v-logic_* 子目录作为实际库路径
        if lib_path.is_dir():
            v_logic_dirs = list(lib_path.glob('v-logic_*'))
            if v_logic_dirs and not any(lib_path / vt for vt in self.get_standard_view_types('STD') if (lib_path / vt).exists()):
                # 这是安装目录，使用第一个 v-logic_* 子目录
                actual_lib_path = v_logic_dirs[0]
                lib_name = actual_lib_path.name
        
        # 检查是否是版本目录（如 v1.12, v2.0, 1.01a）
        # 版本目录的特征：以v开头后跟数字，或者直接是数字版本号
        is_version_dir = False
        if lib_name.startswith('v'):
            # 检查 v1.12, v2.0 等格式
            remaining = lib_name[1:]  # 去掉v
            if re.match(r'^\d+\.\d+', remaining) or remaining.replace('.', '').isdigit():
                is_version_dir = True
        elif re.match(r'^\d+\.\d+[A-Za-z]?$', lib_name):
            # 检查 1.01a, 2.00A 等格式
            is_version_dir = True
        
        if is_version_dir:
            # 这是版本目录，使用父目录名作为库名
            lib_name = actual_lib_path.parent.name
            version = actual_lib_path.name
        elif lib_name.startswith('v-logic_'):
            # STD库的v-logic_前缀
            lib_name = lib_name.replace('v-logic_', '')
        elif lib_name.startswith('v-'):
            # 其他v-开头的去掉前缀
            lib_name = lib_name.replace('v-', '', 1)
        
        # 如果还没有提取到版本，尝试从路径中提取（使用实际库路径）
        if not version:
            version = self._extract_version(actual_lib_path)
        
        # 库类型由用户指定，这里使用默认值（会被覆盖）
        lib_type = 'STD'  # 默认值，实际会被用户指定的类型覆盖
        
        return LibInfo(
            lib_name=lib_name,
            lib_path=lib_path,  # 保持原始路径，但查找时使用 actual_lib_path
            lib_type=lib_type,  # 这个会被用户指定的类型覆盖
            foundry=self.foundry,
            node=self.node_key,
            version=version
        )
    
    def extract_rc_corner(self, pvt_corner: str) -> str:
        """
        提取RC corner
        
        根据 foundry 的不同，使用不同的匹配策略：
        - Samsung: 使用 startswith 匹配（支持 'ff', 'ss', 'tt' 等）
          同时支持带前缀的情况（如 'dlvl_ffpg...', 'pg_tt...'）
          还支持变体格式（如 'sfg' 可能是 'ss' 的变体）
        - SMIC/TSMC: 使用精确匹配（get）
        
        PVT corner 格式示例：
        - 最简单版本：ffpg0p715v125c, sfg0p675vn40c
        - 带前缀的版本：ulvl_ffpg..., dlvl_ffpg..., udlvl_ffpg..., pg_tt...
        - 带前缀和额外电压参数：dlvl_ffpg0p715v125c_i0p825v
        
        注意：
        - Level Shifter 前缀：
          - 'ulvl' = Up Level Shifters（向上电平转换器）
          - 'dlvl' = Down Level Shifters（向下电平转换器）
          - 'udlvl' = Up Down Level Shifters（双向电平转换器）
        - 'pg' = Power Gate（电源门控）
        - 不存在 'ulvt' 格式
        """
        pvt_corner_lower = pvt_corner.lower()
        
        # 对于 Samsung，使用 startswith 匹配（因为可能有 'ff', 'ffgs', 'sfg' 等变体）
        if self.foundry == 'samsung':
            # 首先尝试直接匹配（最简单版本）
            for prefix, rc_corner in self.pvt_corner_mapping.items():
                if pvt_corner_lower.startswith(prefix):
                    return rc_corner
            
            # 检查变体格式（如 'sfg' 可能是 'ss' 的变体）
            # 'sfg' 可能是 'slow-fast' 或类似的组合，通常归类为 'ss'（worst case）
            if pvt_corner_lower.startswith('sfg'):
                return 'sigcmax'  # slow-fast 通常归类为 worst case
            
            # 如果直接匹配失败，检查是否包含下划线（可能是带前缀的版本）
            # 例如：dlvl_ffpg0p715v125c -> 检查第二部分是否以 ff/ss/tt 开头
            # 例如：pg_tt0p85v85c -> 检查第二部分是否以 tt 开头
            if '_' in pvt_corner_lower:
                parts = pvt_corner_lower.split('_')
                # 检查每个部分，找到以 ff/ss/tt 开头的部分
                for part in parts:
                    for prefix, rc_corner in self.pvt_corner_mapping.items():
                        if part.startswith(prefix):
                            return rc_corner
                    # 检查变体格式
                    if part.startswith('sfg'):
                        return 'sigcmax'
        else:
            # 对于 SMIC 和 TSMC，使用精确匹配
            return self.pvt_corner_mapping.get(pvt_corner_lower, 'typical')
        
        return 'typical'
    
    def _is_ip_library(self, lib_path: Path) -> bool:
        """判断是否为IP库"""
        return (lib_path / 'FE-Common').exists() or (lib_path / 'BE-Common').exists()
    
    def _is_mem_library(self, lib_path: Path) -> bool:
        """判断是否为MEM库"""
        lib_name_lower = lib_path.name.lower()
        mem_keywords = ['mem', 'sram', 'memory']
        for keyword in mem_keywords:
            if keyword in lib_name_lower:
                return True
        
        # 检查父目录
        for ancestor in lib_path.parents:
            parent_name_lower = ancestor.name.lower()
            for keyword in mem_keywords:
                if keyword in parent_name_lower:
                    return True
        
        return False
    
    def _extract_version(self, lib_path: Path) -> Optional[str]:
        """
        提取版本信息（返回最新版本）
        
        如果找到多个版本，返回最新的版本。
        """
        versions = self._find_all_versions(lib_path)
        if not versions:
            return None
        
        # 返回最新版本
        return self._get_latest_version(versions)
    
    def _find_all_versions(self, lib_path: Path) -> List[str]:
        """
        查找所有版本目录
        
        Returns:
            版本字符串列表，如 ['2.00A', '1.01a', '1.0']
        """
        versions = []
        
        for root, dirs, files in os.walk(lib_path):
            for dir_name in dirs:
                # 匹配格式：数字.数字字母（如 2.00A, 1.01a）
                if re.match(r'^\d+\.\d+[A-Za-z]?$', dir_name):
                    versions.append(dir_name)
                # 匹配格式：v数字.数字（如 v1.12, v2.0）
                elif re.match(r'^v\d+\.\d+', dir_name):
                    versions.append(dir_name)
        
        return versions
    
    def _get_latest_version(self, versions: List[str]) -> str:
        """
        从版本列表中获取最新版本
        
        Args:
            versions: 版本字符串列表
            
        Returns:
            最新版本的字符串
        """
        if not versions:
            return None
        
        if len(versions) == 1:
            return versions[0]
        
        # 使用版本比较函数排序
        sorted_versions = sorted(versions, key=self._parse_version_for_sort, reverse=True)
        return sorted_versions[0]
    
    def _parse_version_for_sort(self, version: str) -> tuple:
        """
        解析版本字符串用于排序
        
        返回一个元组，可以用于比较：
        - (主版本号, 次版本号, 字母部分)
        
        例如：
        - '2.00A' -> (2, 0, 'A')
        - '1.01a' -> (1, 1, 'a')
        - 'v1.12' -> (1, 12, '')
        """
        # 去掉 'v' 前缀
        version_clean = version.lstrip('v')
        
        # 提取数字和字母部分
        match = re.match(r'^(\d+)\.(\d+)([A-Za-z]?)$', version_clean)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            letter = match.group(3) if match.group(3) else ''
            # 字母转换为数字用于比较（A=65, a=97，但通常大写字母版本更新）
            letter_value = ord(letter.upper()) if letter else 0
            return (major, minor, letter_value)
        
        # 如果格式不匹配，返回 (0, 0, 0) 作为默认值
        return (0, 0, 0)

