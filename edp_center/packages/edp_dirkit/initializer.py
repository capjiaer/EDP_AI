#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ProjectInitializer - 项目环境初始化工具

从 edp_center 资源库中提取配置和流程，初始化项目工作环境。
"""

import os
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Union
from .dirkit import DirKit

# 导入框架异常类
from edp_center.packages.edp_common import EDPFileNotFoundError, ProjectNotFoundError


class ProjectInitializer:
    """项目环境初始化器"""
    
    def __init__(self, edp_center_path: Union[str, Path]):
        """
        初始化 ProjectInitializer
        
        Args:
            edp_center_path: edp_center 资源库的路径
        """
        self.edp_center = Path(edp_center_path)
        if not self.edp_center.exists():
            raise EDPFileNotFoundError(
                file_path=str(edp_center_path),
                suggestion=(
                    "请检查 EDP Center 路径是否正确。\n"
                    "可以使用 '--edp-center' 参数指定路径，或确保当前目录在 edp_center 内。"
                )
            )
        
        self.config_path = self.edp_center / "config"
        self.flow_path = self.edp_center / "flow"
    
    def init_project(self, project_dir: Union[str, Path],
                     foundry: str, node: str, project: str,
                     link_mode: bool = False, 
                     flows: Optional[List[str]] = None) -> Dict[str, Path]:
        """
        初始化项目环境
        
        Args:
            project_dir: 项目目录路径
            foundry: 代工厂名称（如 SAMSUNG）
            node: 工艺节点（如 S8）
            project: 项目名称（如 dongting）
            link_mode: 是否使用符号链接而不是复制（默认：False，使用复制）
            flows: 需要初始化的流程列表（None 表示初始化所有流程）
            
        Returns:
            包含创建的目录路径的字典
        """
        project_path = Path(project_dir)
        dirkit = DirKit(base_path=project_path)
        
        created_paths = {}
        
        # 1. 创建基础目录结构
        config_dir = dirkit.ensure_dir("config")
        flow_dir = dirkit.ensure_dir("flow")
        cmds_dir = dirkit.ensure_dir("flow/cmds")
        packages_dir = dirkit.ensure_dir("flow/packages")
        
        created_paths['config'] = config_dir
        created_paths['flow'] = flow_dir
        created_paths['cmds'] = cmds_dir
        created_paths['packages'] = packages_dir
        
        # 2. 复制/链接项目配置
        self._init_project_config(dirkit, foundry, node, project, link_mode)
        
        # 3. 初始化流程
        if flows is None:
            flows = self._get_available_flows(foundry, node)
        
        for flow_name in flows:
            self._init_flow(dirkit, foundry, node, project, flow_name, link_mode)
        
        # 4. 初始化 packages
        self._init_packages(dirkit, foundry, node, project, link_mode)
        
        return created_paths
    
    def _init_project_config(self, dirkit: DirKit, foundry: str, 
                            node: str, project: str, link_mode: bool):
        """初始化项目配置"""
        src_config_path = self.config_path / foundry / node / project
        
        if not src_config_path.exists():
            raise ProjectNotFoundError(
                project_name=project,
                foundry=foundry,
                node=node,
                config_path=str(src_config_path.parent.parent.parent),
                suggestion=(
                    f"项目配置不存在: {src_config_path}\n"
                    f"路径结构应为: config/{foundry}/{node}/{project}/\n"
                    f"使用 'edp -create_project {project} {foundry} {node}' 创建项目配置"
                )
            )
        
        # 复制/链接整个配置目录到项目根目录下的 config 目录
        # 保持相同的目录结构：config/{foundry}/{node}/{project}/
        target_config_path = dirkit.base_path / "config" / foundry / node / project
        
        if link_mode:
            dirkit.link_dir(src_config_path, target_config_path, overwrite=True)
        else:
            dirkit.copy_dir(src_config_path, target_config_path, overwrite=True)
    
    def _init_flow(self, dirkit: DirKit, foundry: str, node: str, 
                   project: str, flow_name: str, link_mode: bool):
        """初始化单个流程"""
        # 检查 common 流程是否存在
        common_flow_path = (self.flow_path / "initialize" / foundry / 
                           node / "common" / "cmds" / flow_name)
        
        if not common_flow_path.exists():
            print(f"警告: 流程 {flow_name} 在 common 中不存在，跳过")
            return
        
        # 复制/链接 common 流程到项目
        target_flow_path = dirkit.base_path / "flow" / "cmds" / flow_name
        
        if link_mode:
            dirkit.link_dir(common_flow_path, target_flow_path, overwrite=True)
        else:
            dirkit.copy_dir(common_flow_path, target_flow_path, overwrite=True)
        
        # 检查是否有项目特定的覆盖
        project_flow_path = (self.flow_path / "initialize" / foundry / 
                            node / project / "cmds" / flow_name)
        
        if project_flow_path.exists():
            # 项目特定的流程覆盖 common 流程
            # 这里我们需要合并而不是完全替换
            self._merge_project_flow_override(dirkit, project_flow_path, 
                                            target_flow_path, link_mode)
    
    def _merge_project_flow_override(self, dirkit: DirKit, 
                                    src_path: Path, dst_path: Path, 
                                    link_mode: bool):
        """合并项目特定的流程覆盖"""
        # 对于文件和目录，项目特定的版本会覆盖 common 版本
        for item in src_path.rglob('*'):
            if item.is_dir():
                continue
            
            relative_path = item.relative_to(src_path)
            target_file = dst_path / relative_path
            
            if link_mode:
                # 对于链接模式，直接链接文件
                dirkit.link_file(item, target_file, overwrite=True)
            else:
                # 对于复制模式，复制文件（会覆盖）
                dirkit.copy_file(item, target_file, overwrite=True)
    
    def _init_packages(self, dirkit: DirKit, foundry: str, node: str,
                      project: str, link_mode: bool):
        """初始化 packages"""
        packages_dir = dirkit.base_path / "flow" / "packages"
        
        # 按优先级顺序初始化 packages
        package_sources = [
            # 1. 通用默认包
            (self.flow_path / "common" / "packages" / "tcl" / "default", 
             "default"),
            # 2. 通用流程包（将在具体流程中处理）
            # 3. 代工厂节点通用包
            (self.flow_path / "initialize" / foundry / node / 
             "common" / "packages" / "tcl" / "default", "default"),
            # 4. 项目特定包
            (self.flow_path / "initialize" / foundry / node / project /
             "packages" / "tcl" / "default", "default"),
        ]
        
        for src_pkg_dir, pkg_name in package_sources:
            if src_pkg_dir.exists():
                target_pkg_dir = packages_dir / pkg_name
                if link_mode:
                    dirkit.link_dir(src_pkg_dir, target_pkg_dir, overwrite=True)
                else:
                    dirkit.copy_dir(src_pkg_dir, target_pkg_dir, overwrite=True)
        
        # 初始化流程特定的 packages
        flows = self._get_available_flows(foundry, node)
        for flow_name in flows:
            flow_package_sources = [
                (self.flow_path / "common" / "packages" / "tcl" / flow_name,
                 flow_name),
                (self.flow_path / "initialize" / foundry / node /
                 "common" / "packages" / "tcl" / flow_name, flow_name),
                (self.flow_path / "initialize" / foundry / node / project /
                 "packages" / "tcl" / flow_name, flow_name),
            ]
            
            for src_pkg_dir, pkg_name in flow_package_sources:
                if src_pkg_dir.exists():
                    target_pkg_dir = packages_dir / pkg_name
                    if link_mode:
                        dirkit.link_dir(src_pkg_dir, target_pkg_dir, 
                                      overwrite=True)
                    else:
                        dirkit.copy_dir(src_pkg_dir, target_pkg_dir, 
                                      overwrite=True)
    
    def _get_available_flows(self, foundry: str, node: str) -> List[str]:
        """获取可用的流程列表"""
        common_cmds_path = (self.flow_path / "initialize" / foundry / 
                           node / "common" / "cmds")
        
        if not common_cmds_path.exists():
            return []
        
        flows = []
        for item in common_cmds_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                flows.append(item.name)
        
        return sorted(flows)
    
    def get_config_files(self, foundry: str, node: str, 
                        project: str, flow: Optional[str] = None) -> List[Path]:
        """
        获取配置文件路径列表，按优先级排序
        
        配置加载顺序（优先级从低到高）：
        1. common/main/* (所有文件)
        2. common/{flow}/* (所有文件)
        3. {project}/main/* (所有文件)
        4. {project}/{flow}/* (所有文件)
        
        Args:
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称
            flow: 流程名称（可选）
            
        Returns:
            配置文件路径列表，按加载顺序排列
        """
        config_files = []
        
        # 1. common/main/* (所有文件)
        common_main_dir = self.config_path / foundry / node / "common" / "main"
        if common_main_dir.exists():
            for config_file in common_main_dir.glob("*"):
                if config_file.is_file() and config_file.suffix in ['.yaml', '.yml']:
                    config_files.append(config_file)
        
        # 2. common/{flow}/* (所有文件)
        if flow:
            common_flow_dir = self.config_path / foundry / node / "common" / flow
            if common_flow_dir.exists():
                for config_file in common_flow_dir.glob("*"):
                    if config_file.is_file() and config_file.suffix in ['.yaml', '.yml']:
                        config_files.append(config_file)
        
        # 3. {project}/main/* (所有文件)
        project_main_dir = self.config_path / foundry / node / project / "main"
        if project_main_dir.exists():
            for config_file in project_main_dir.glob("*"):
                if config_file.is_file() and config_file.suffix in ['.yaml', '.yml']:
                    config_files.append(config_file)
        
        # 4. {project}/{flow}/* (所有文件)
        if flow:
            project_flow_dir = self.config_path / foundry / node / project / flow
            if project_flow_dir.exists():
                for config_file in project_flow_dir.glob("*"):
                    if config_file.is_file() and config_file.suffix in ['.yaml', '.yml']:
                        config_files.append(config_file)
        
        return config_files

