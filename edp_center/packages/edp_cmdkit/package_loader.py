#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PackageLoader - Tcl 包加载器

用于生成默认的 source 语句，自动加载 edp_center 中的 packages。
"""

from pathlib import Path
from typing import List, Optional, Union, Dict
import logging

logger = logging.getLogger(__name__)


class PackageLoader:
    """Tcl 包加载器"""
    
    def __init__(self, edp_center_path: Union[str, Path]):
        """
        初始化 PackageLoader
        
        Args:
            edp_center_path: edp_center 资源库的路径
        """
        # 导入框架异常类
        from edp_center.packages.edp_common import EDPFileNotFoundError, ValidationError
        
        self.edp_center = Path(edp_center_path).resolve()
        if not self.edp_center.exists():
            raise EDPFileNotFoundError(
                file_path=str(edp_center_path),
                suggestion=(
                    "请检查 EDP Center 路径是否正确。\n"
                    "可以使用 '--edp-center' 参数指定路径，或确保当前目录在 edp_center 内。"
                )
            )
        
        self.flow_path = self.edp_center / "flow"
        self.config_path = self.edp_center / "config"
    
    def find_project_info(self, project_name: str) -> Optional[Dict[str, str]]:
        """
        根据项目名称查找 foundry 和 node
        
        Args:
            project_name: 项目名称（如 dongting）
            
        Returns:
            包含 foundry 和 node 的字典，如果找不到或找到多个则返回 None
        """
        if not self.config_path.exists():
            return None
        
        matches = []
        
        # 遍历 config 目录查找项目
        for foundry_dir in self.config_path.iterdir():
            if not foundry_dir.is_dir() or foundry_dir.name.startswith('.'):
                continue
            
            for node_dir in foundry_dir.iterdir():
                if not node_dir.is_dir() or node_dir.name.startswith('.'):
                    continue
                
                # 检查是否有该项目的配置目录
                project_dir = node_dir / project_name
                if project_dir.exists() and project_dir.is_dir():
                    matches.append({
                        'foundry': foundry_dir.name,
                        'node': node_dir.name,
                        'project': project_name
                    })
        
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return matches[0]
        else:
            # 多个匹配，返回第一个（或者可以让调用者指定）
            logger.warning(
                f"找到多个匹配的项目 '{project_name}'，使用第一个: "
                f"{matches[0]['foundry']}/{matches[0]['node']}"
            )
            return matches[0]
    
    def parse_script_path(self, script_path: Union[str, Path]) -> Optional[Dict[str, str]]:
        """
        从脚本路径解析 foundry, node, project, flow_name
        
        支持的路径格式（新结构，主脚本直接在 cmds/{flow_name}/ 下）：
        - edp_center/flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/<script_file>
        - edp_center/flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/<script_file>
        
        路径结构：以 flow/initialize 为分割点
        - 前面部分：edp_center 的绝对路径
        - 后面部分：<foundry>/<node>/<project_name>/cmds/<flow_name>/<step_name>.tcl
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            包含 foundry, node, project (可能为 None), flow_name 的字典
            如果无法解析则返回 None
        """
        script_path = Path(script_path).resolve()
        
        # 转换为字符串以便搜索（统一使用正斜杠）
        path_str = str(script_path).replace('\\', '/')
        
        # 以 flow/initialize 为分割点
        split_pattern = '/flow/initialize/'
        if split_pattern not in path_str:
            return None
        
        # 分割路径
        parts = path_str.split(split_pattern)
        if len(parts) != 2:
            return None
        
        # 前面部分：edp_center 的绝对路径（去除末尾的 /flow）
        edp_center_str = parts[0]
        # 后面部分：<foundry>/<node>/<project_name>/cmds/<flow_name>/<step_name>.tcl
        path_after_initialize = parts[1]
        
        # 解析路径部分
        path_parts = path_after_initialize.split('/')
        if len(path_parts) < 4:  # 至少需要 foundry/node/cmds/flow_name
            return None
        
        # 解析路径组件
        foundry = path_parts[0]
        node = path_parts[1]
        
        # 判断是 common 还是 project
        project = None
        flow_name = None
        
        if path_parts[2] == 'common':
            # flow/initialize/FOUNDRY/NODE/common/cmds/<flow_name>/<step_name>.tcl
            if len(path_parts) >= 4 and path_parts[3] == 'cmds':
                if len(path_parts) >= 5:
                    flow_name = path_parts[4]
        else:
            # flow/initialize/FOUNDRY/NODE/<PROJECT>/cmds/<flow_name>/<step_name>.tcl
            project = path_parts[2]
            if len(path_parts) >= 5 and path_parts[3] == 'cmds':
                if len(path_parts) >= 6:
                    flow_name = path_parts[4]
        
        if not foundry or not node or not flow_name:
            return None
        
        # 更新 self.edp_center（如果还没有设置）
        if not hasattr(self, '_parsed_edp_center') or self._parsed_edp_center != edp_center_str:
            edp_center_path = Path(edp_center_str)
            if edp_center_path.exists() and (edp_center_path / 'flow').exists():
                # 使用解析出的路径（如果不同）
                self._parsed_edp_center = edp_center_str
        
        return {
            'foundry': foundry,
            'node': node,
            'project': project,
            'flow_name': flow_name,
            '_edp_center_path': edp_center_str  # 内部使用，返回 edp_center 路径
        }
    
    def get_util_search_paths(self, script_path: Union[str, Path]) -> List[Path]:
        """
        根据脚本路径获取 helpers 搜索路径
        
        返回的搜索路径包括（按优先级顺序）：
        1. 项目特定的 helpers 目录（如果存在）
        2. common 的 helpers 目录
        
        Args:
            script_path: 脚本文件路径
        
        Returns:
            helpers 搜索路径列表
        """
        script_path = Path(script_path).resolve()
        
        # 解析路径信息
        path_info = self.parse_script_path(script_path)
        if not path_info:
            return []
        
        foundry = path_info['foundry']
        node = path_info['node']
        project = path_info.get('project')
        flow_name = path_info['flow_name']
        
        util_paths = []
        
        # 1. 项目特定的 helpers 目录（如果存在项目）
        if project:
            project_helpers_dir = (self.flow_path / "initialize" / foundry / node / project /
                                  "cmds" / flow_name / "helpers")
            if project_helpers_dir.exists() and project_helpers_dir.is_dir():
                util_paths.append(project_helpers_dir)
        
        # 2. common 的 helpers 目录
        common_helpers_dir = (self.flow_path / "initialize" / foundry / node / "common" /
                             "cmds" / flow_name / "helpers")
        if common_helpers_dir.exists() and common_helpers_dir.is_dir():
            util_paths.append(common_helpers_dir)
        
        return util_paths
    
    def generate_default_sources(self,
                                 foundry: Optional[str] = None,
                                 node: Optional[str] = None,
                                 project: Optional[str] = None,
                                 flow_name: Optional[str] = None,
                                 include_sub_steps: bool = False) -> str:
        """
        生成默认的 source 语句
        
        按照以下优先级顺序生成 source 语句：
        1. flow/common/packages/tcl/default/*
        2. flow/common/packages/tcl/<flow_name>/*
        3. flow/initialize/<FOUNDRY>/<NODE>/common/packages/tcl/default/*
        4. flow/initialize/<FOUNDRY>/<NODE>/common/packages/tcl/<flow_name>/*
        5. flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/packages/tcl/default/*
        6. flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/packages/tcl/<flow_name>/*
        
        注意：sub_steps 现在放在 sub_steps 目录下（flow/sub_steps/），通过 dependency.yaml 配置自动生成 source 语句。
        不再从 packages 目录加载 sub_steps。
        
        Args:
            foundry: 代工厂名称（如 SAMSUNG）。如果为 None 且提供了 project，会尝试自动查找
            node: 工艺节点（如 S8）。如果为 None 且提供了 project，会尝试自动查找
            project: 项目名称（如 dongting）。如果提供了 project 但没有提供 foundry 和 node，会尝试自动查找
            flow_name: 流程名称（如 pv_calibre），可选
            include_sub_steps: 是否包含 sub_steps 目录（已弃用，sub_steps 现在放在 sub_steps 目录），默认为 False
        
        Returns:
            生成的 source 语句字符串（每行一个 source 语句）
        """
        # 如果提供了 project 但没有提供 foundry 和 node，尝试自动查找
        if project and (not foundry or not node):
            project_info = self.find_project_info(project)
            if project_info:
                foundry = foundry or project_info['foundry']
                node = node or project_info['node']
                logger.info(f"自动查找项目信息: {project} -> {foundry}/{node}")
            else:
                if not foundry or not node:
                    raise ValidationError(
                        message=f"无法自动查找项目 '{project}' 的 foundry 和 node",
                        field_name="project",
                        field_value=project,
                        expected="foundry 和 node 参数",
                        suggestion=(
                            f"项目 '{project}' 未找到或存在多个匹配。\n"
                            "请手动指定 foundry 和 node 参数，或使用 'edp -create_project' 创建新项目。"
                        )
                    )
        
        if not foundry or not node:
            raise ValidationError(
                message="必须提供 foundry 和 node",
                expected="foundry 和 node 参数（可以直接提供，或通过 project 自动查找）",
                suggestion=(
                    "请提供 foundry 和 node 参数，例如：\n"
                    "  - foundry='SAMSUNG', node='S8'\n"
                    "  - 或通过 project 参数自动查找"
                )
            )
        source_lines = []
        
        # 1. All packages from general common package default path
        # flow/common/packages/tcl/default/*
        common_default_dir = self.flow_path / "common" / "packages" / "tcl" / "default"
        common_default_sources = self._generate_sources_from_dir(common_default_dir)
        if common_default_sources:
            source_lines.append("# All packages from general common package default path")
            source_lines.extend(common_default_sources)
            source_lines.append("")  # 空行分隔
        
        # flow/common/packages/tcl/<flow_name>/* (if flow_name specified)
        if flow_name:
            common_flow_dir = self.flow_path / "common" / "packages" / "tcl" / flow_name
            common_flow_sources = self._generate_sources_from_dir(common_flow_dir)
            if common_flow_sources:
                source_lines.extend(common_flow_sources)
                source_lines.append("")  # 空行分隔
        
        # 2. All packages from foundry node level default path
        # flow/initialize/<FOUNDRY>/<NODE>/common/packages/tcl/default/*
        foundry_node_common_default = (self.flow_path / "initialize" / foundry / node /
                                      "common" / "packages" / "tcl" / "default")
        foundry_node_default_sources = self._generate_sources_from_dir(foundry_node_common_default)
        if foundry_node_default_sources:
            source_lines.append("# All packages from foundry node level default path")
            source_lines.extend(foundry_node_default_sources)
            source_lines.append("")  # 空行分隔
        
        # flow/initialize/<FOUNDRY>/<NODE>/common/packages/tcl/<flow_name>/* (if flow_name specified)
        if flow_name:
            foundry_node_common_flow = (self.flow_path / "initialize" / foundry / node /
                                       "common" / "packages" / "tcl" / flow_name)
            foundry_node_flow_sources = self._generate_sources_from_dir(foundry_node_common_flow)
            if foundry_node_flow_sources:
                source_lines.extend(foundry_node_flow_sources)
                source_lines.append("")  # 空行分隔
        
        # 3. All packages from project level default path
        # flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/packages/tcl/default/*
        if project:
            project_default_dir = (self.flow_path / "initialize" / foundry / node / project /
                                  "packages" / "tcl" / "default")
            project_default_sources = self._generate_sources_from_dir(project_default_dir)
            if project_default_sources:
                source_lines.append("# All packages from project level default path")
                source_lines.extend(project_default_sources)
                source_lines.append("")  # 空行分隔
            
            # flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/packages/tcl/<flow_name>/* (if flow_name specified)
            if flow_name:
                project_flow_dir = (self.flow_path / "initialize" / foundry / node / project /
                                   "packages" / "tcl" / flow_name)
                project_flow_sources = self._generate_sources_from_dir(project_flow_dir)
                if project_flow_sources:
                    source_lines.extend(project_flow_sources)
                    source_lines.append("")  # 空行分隔
        
        # 注意：sub_steps 现在放在 sub_steps 目录下（flow/sub_steps/），通过 dependency.yaml 配置自动生成 source 语句
        # 不再从 packages 目录加载 sub_steps
        
        # 移除末尾的空行（如果有）
        result = '\n'.join(source_lines)
        if result and not result.endswith('\n'):
            result += '\n'
        return result
    
    def _generate_sources_from_dir(self, dir_path: Path) -> List[str]:
        """
        从指定目录生成 source 语句列表
        
        Args:
            dir_path: 目录路径
        
        Returns:
            source 语句列表
        """
        source_lines = []
        
        if not dir_path.exists() or not dir_path.is_dir():
            return source_lines
        
        # 查找所有 .tcl 文件（按文件名排序，确保顺序一致）
        tcl_files = sorted(dir_path.glob('*.tcl'))
        
        for tcl_file in tcl_files:
            if tcl_file.is_file():
                # 生成 source 语句（使用绝对路径，转换为 Tcl 兼容格式）
                file_path = tcl_file.resolve()
                # 将 Windows 路径的反斜杠转换为正斜杠（Tcl 兼容）
                tcl_path = str(file_path).replace('\\', '/')
                source_lines.append(f"source {tcl_path}")
        
        return source_lines

