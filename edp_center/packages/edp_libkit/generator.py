#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LibConfigGenerator - 库配置生成器主类

        协调各个组件，完成从ori目录扫描到lib_config.tcl生成的完整流程。
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .lib_info import LibInfo
from .foundry_adapters import FoundryAdapter, AdapterFactory
from .lib_generator import LibGenerator

logger = logging.getLogger(__name__)


class LibConfigGenerator:
    """库配置生成器"""
    
    def __init__(self, foundry: str, ori_path: Path, output_base_dir: Optional[Path] = None,
                 array_name: Optional[str] = None, node: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            foundry: Foundry名称（如 'Samsung'）
            ori_path: ori目录路径
            output_base_dir: lib_config.tcl输出基础目录（如果为None，则放在框架内部）
            array_name: lib_config.tcl中的数组变量名（默认：LIBRARY）
            node: 工艺节点（如 'ln08lpu_gp'，可选）
        """
        self.foundry = foundry
        self.ori_path = Path(ori_path).resolve()
        self.output_base_dir = output_base_dir
        self.node = node
        
        # 创建适配器
        self.adapter = AdapterFactory.create_adapter(foundry, node)
        logger.info(f"使用适配器: {type(self.adapter).__name__}")
        
        # 根据foundry设置默认array_name
        if array_name is None:
            array_name = 'LIBRARY'  # 默认都是 LIBRARY
        
        self.lib_generator = LibGenerator(array_name=array_name)
    

    
    def scan_and_generate(self) -> List[Path]:
        """
        扫描ori目录并生成所有库的lib_config.tcl（已废弃）
        
        注意：此方法已废弃。现在要求用户通过命令行参数明确指定库路径和类型。
        此方法保留仅为向后兼容，实际返回空列表。
        
        Returns:
            空列表
        """
        logger.warning("scan_and_generate() 方法已废弃。请使用 generate_from_directory() 并明确指定库路径和类型。")
        return []
    
    def generate_single_library(self, lib_path: Path) -> List[Path]:
        """
        直接处理单个库目录（已废弃）
        
        注意：此方法已废弃。请使用 generate_from_directory() 并明确指定库类型。
        
        Args:
            lib_path: 库目录路径
            
        Returns:
            生成的lib_config.tcl文件路径列表
        """
        logger.warning("generate_single_library() 方法已废弃。请使用 generate_from_directory() 并明确指定库类型。")
        raise ValueError("请使用 generate_from_directory() 方法，并明确指定 --lib-type 参数")
    
    def _collect_files(self, view_dirs: Dict[str, any]) -> Dict[str, any]:
        """
        收集各个视图目录中的文件
        
        Args:
            view_dirs: {view_type: view_path} 字典
                对于SMIC，可能包含特殊结构：
                - 'root': Path
                - 'pvt_dirs': {pvt_name: Path}
            
        Returns:
            {view_type: files_or_structure} 字典
                对于SMIC，返回特殊结构以支持PVT目录处理
        """
        # 检查是否是SMIC格式（通过view_dirs结构判断）
        is_smic_format = 'root' in view_dirs or 'pvt_dirs' in view_dirs
        
        if is_smic_format:
            # SMIC格式：直接返回view_dirs结构，让lib_generator处理
            return view_dirs
        
        # Samsung格式：收集文件列表
        view_files = {}
        
        for view_type, view_path in view_dirs.items():
            # 获取文件匹配模式（可能是字符串或列表）
            pattern = self.adapter.get_view_file_pattern(view_type)
            
            # 查找匹配的文件
            files = []
            if isinstance(pattern, list):
                # 多个模式：匹配所有模式的文件
                for p in pattern:
                    matched = list(view_path.glob(p))
                    files.extend(matched)
                    if matched:
                        logger.debug(f"{view_type}: 模式 '{p}' 找到 {len(matched)} 个文件")
            else:
                # 单个模式：向后兼容
                files = list(view_path.glob(pattern))
            
            # 去重并排序
            if files:
                files = sorted(set(files))  # 使用 set 去重
                view_files[view_type] = files
                logger.debug(f"{view_type}: 总共找到 {len(files)} 个文件")
        
        return view_files
    
    def _determine_output_path(self, lib_info: LibInfo) -> Path:
        """
        确定lib_config.tcl的输出路径
        
        输出路径结构：{output_base_dir}/{lib_name}/lib_config.tcl
        不再包含版本目录层级，版本信息通过文件名区分（lib_config.tcl 或 lib_config_{version}.tcl）
        不再包含 foundry 和 lib_type 层级，因为用户可能已经在 output_base_dir 中包含了这些信息
        """
        if not self.output_base_dir:
            raise ValueError("output_base_dir 必须指定，请使用 --output-dir 参数")
        
        # 简化路径结构：只保留库名，不包含版本目录
        output_path = self.output_base_dir / lib_info.lib_name
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / 'lib_config.tcl'
    
    def generate_from_directory(self, lib_dir: Path, lib_type: str, version: Optional[str] = None) -> List[Path]:
        """
        从给定目录生成lib_config.tcl（必须指定库类型）
        
        这是现在推荐使用的方法，要求用户明确指定库类型，不依赖自动识别。
        
        Args:
            lib_dir: 库目录路径（可以是任意目录，不要求特定前缀）
            lib_type: 库类型（STD/IP/MEM），必须由用户指定
            version: 指定版本号（如 '2.00A'）。如果为None，自动选择最新版本
            
        Returns:
            生成的lib_config.tcl文件路径列表
        """
        logger.info(f"处理目录: {lib_dir}, 库类型: {lib_type}")
        
        if not lib_dir.exists():
            raise ValueError(f"目录不存在: {lib_dir}")
        
        if not lib_dir.is_dir():
            raise ValueError(f"路径不是目录: {lib_dir}")
        
        # 使用适配器提取库信息（名称、版本等）
        lib_info = self.adapter.extract_lib_info(lib_dir)
        # 覆盖为用户指定的库类型（不依赖自动识别）
        lib_info.lib_type = lib_type
        
        # 如果指定了版本，覆盖提取的版本
        if version:
            lib_info.version = version
            logger.info(f"使用指定版本: {version}")
        elif not lib_info.version:
            # 如果没有指定版本且未提取到版本，尝试提取最新版本
            if hasattr(self.adapter, '_node_adapter') and self.adapter._node_adapter:
                all_versions = self.adapter._node_adapter._find_all_versions(lib_dir)
                if all_versions:
                    lib_info.version = self.adapter._node_adapter._get_latest_version(all_versions)
                    logger.info(f"自动选择最新版本: {lib_info.version}")
        
        logger.info(f"库信息: {lib_info}")
        
        try:
            # 找到视图目录（根据库类型使用不同的查找逻辑，如果指定了版本则只查找该版本）
            view_dirs = self.adapter.find_view_directories(lib_info.lib_path, lib_type, version=version)
            logger.debug(f"找到视图目录: {list(view_dirs.keys())}")
            
            if not view_dirs:
                logger.warning(f"库 {lib_info.lib_name} 没有找到任何视图目录")
                return []
            
            # 收集文件
            view_files = self._collect_files(view_dirs)
            
            # 确定输出路径
            output_path = self._determine_output_path(lib_info)
            
            # 生成lib_config.tcl
            self.lib_generator.generate(lib_info, view_files, output_path, self.adapter)
            logger.info(f"已生成: {output_path}")
            
            return [output_path]
            
        except Exception as e:
            logger.error(f"处理库 {lib_info.lib_name} 时出错: {e}", exc_info=True)
            raise
    
    def generate_all_versions(self, lib_dir: Path, lib_type: str) -> List[Path]:
        """
        处理库目录下的所有版本，生成配置文件
        
        策略：
        - 最新版本：生成 lib_config.tcl（默认使用）
        - 其他版本：生成 lib_config_{version}.tcl（如 lib_config_1.00B.tcl）
        
        Args:
            lib_dir: 库目录路径
            lib_type: 库类型（STD/IP/MEM）
            
        Returns:
            生成的lib_config.tcl文件路径列表
        """
        logger.info(f"处理目录的所有版本: {lib_dir}, 库类型: {lib_type}")
        
        if not lib_dir.exists():
            raise ValueError(f"目录不存在: {lib_dir}")
        
        if not lib_dir.is_dir():
            raise ValueError(f"路径不是目录: {lib_dir}")
        
        # 找到所有版本
        if not hasattr(self.adapter, '_node_adapter') or not self.adapter._node_adapter:
            raise ValueError("无法访问节点适配器，无法查找版本")
        
        all_versions = self.adapter._node_adapter._find_all_versions(lib_dir)
        if not all_versions:
            logger.warning(f"库目录下没有找到任何版本: {lib_dir}")
            return []
        
        # 排序版本，找出最新版本
        sorted_versions = sorted(all_versions, key=self.adapter._node_adapter._parse_version_for_sort, reverse=True)
        latest_version = sorted_versions[0]
        
        logger.info(f"找到 {len(all_versions)} 个版本: {all_versions}")
        logger.info(f"最新版本: {latest_version}")
        
        generated_files = []
        
        # 先提取库基本信息（用于确定输出目录）
        base_lib_info = self.adapter.extract_lib_info(lib_dir)
        base_lib_info.lib_type = lib_type
        
        # 确定基础输出目录（库名目录，不包含版本）
        base_output_dir = self.output_base_dir / base_lib_info.lib_name
        base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 对每个版本生成配置文件
        for version in sorted_versions:
            logger.info(f"处理版本: {version}")
            try:
                # 提取库信息
                lib_info = self.adapter.extract_lib_info(lib_dir)
                lib_info.lib_type = lib_type
                lib_info.version = version
                
                # 找到视图目录
                view_dirs = self.adapter.find_view_directories(lib_info.lib_path, lib_type, version=version)
                
                if not view_dirs:
                    logger.warning(f"版本 {version} 没有找到任何视图目录")
                    continue
                
                # 收集文件
                view_files = self._collect_files(view_dirs)
                
                # 确定输出文件名
                # 最新版本：lib_config.tcl
                # 其他版本：lib_config.{version}.tcl（使用点分隔，更统一自然）
                if version == latest_version:
                    output_filename = 'lib_config.tcl'
                else:
                    output_filename = f'lib_config.{version}.tcl'
                
                # 所有版本的文件都放在库名目录下（不包含版本子目录）
                output_path = base_output_dir / output_filename
                
                # 生成lib_config.tcl
                self.lib_generator.generate(lib_info, view_files, output_path, self.adapter)
                logger.info(f"已生成: {output_path}")
                generated_files.append(output_path)
                
            except Exception as e:
                logger.error(f"处理版本 {version} 时出错: {e}", exc_info=True)
                continue
        
        logger.info(f"完成！共生成 {len(generated_files)} 个配置文件")
        return generated_files

