#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CmdProcessor - Tcl 脚本处理器

用于处理 Tcl 脚本中的 #import 指令。
"""

from pathlib import Path
from typing import List, Optional, Union
import logging
from .content_assembler import assemble_content_with_hooks
from .path_preparer import prepare_search_paths
from .source_prepend_processor import add_prepend_sources
from .debug_mode_processor import handle_debug_mode
from .import_processor import ImportProcessor
from .sub_steps_processor import SubStepsProcessor

# 导入框架异常类
from edp_center.packages.edp_common import EDPFileNotFoundError

logger = logging.getLogger(__name__)


class CmdProcessor:
    """Tcl 命令脚本处理器"""
    
    def __init__(self, 
                 base_dir: Optional[Path] = None,
                 default_search_paths: Optional[List[Union[str, Path]]] = None,
                 default_recursive: bool = True):
        """
        初始化 CmdProcessor
        
        Args:
            base_dir: 基础目录，用于解析相对路径。如果为 None，使用当前工作目录
            default_search_paths: 默认搜索路径列表，用于查找被导入的文件
            default_recursive: 默认是否递归查找子目录。默认为 True
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.processed_files = set()  # 防止循环引用
        self.default_search_paths = []
        if default_search_paths:
            for p in default_search_paths:
                resolved = Path(p).resolve()
                if resolved.exists() and resolved.is_dir():
                    self.default_search_paths.append(resolved)
                else:
                    logger.warning(f"默认搜索路径不存在或不是目录，将跳过: {p}")
        self.default_recursive = default_recursive
        
        # 初始化各个处理器
        self.import_processor = ImportProcessor(self.processed_files)
        self.sub_steps_processor = SubStepsProcessor()
    
    def process_file(self, 
                     input_file: Union[str, Path],
                     output_file: Optional[Union[str, Path]] = None,
                     search_paths: Optional[List[Union[str, Path]]] = None,
                     recursive: Optional[bool] = None,
                     # 包加载相关参数
                     edp_center_path: Optional[Union[str, Path]] = None,
                     foundry: Optional[str] = None,
                     node: Optional[str] = None,
                     project: Optional[str] = None,
                     flow_name: Optional[str] = None,
                     prepend_default_sources: bool = False,
                     full_tcl_path: Optional[Union[str, Path]] = None,
            # Hooks 相关参数
            hooks_dir: Optional[Union[str, Path]] = None,
            step_name: Optional[str] = None,
            # Debug 模式参数
            debug_mode: int = 0,
            # Skip sub_steps 参数
            skip_sub_steps: Optional[List[str]] = None) -> Optional[str]:
        """
        处理 Tcl 文件，解析 #import 指令并生成最终脚本
        
        这是推荐的使用方式：输入文件 -> 在指定目录中查找 util 文件替换 -> 输出文件
        
        Args:
            input_file: 输入的 Tcl 文件路径
            output_file: 输出文件路径。如果为 None，返回处理后的内容字符串
            search_paths: 搜索路径列表，用于查找被导入的文件。
                         如果为 None，使用默认搜索路径或文件所在目录和 base_dir。
                         查找顺序：
                         1. 相对当前文件的路径
                         2. search_paths 中的路径（按顺序，如果 recursive=True 会递归查找子目录）
                         3. 文件所在目录和 base_dir（作为后备）
            recursive: 是否在搜索路径中递归查找子目录。
                      如果为 None，使用默认值（初始化时设置的 default_recursive）
            edp_center_path: edp_center 资源库的路径，用于生成默认 source 语句
            foundry: 代工厂名称（如 SAMSUNG），用于生成默认 source 语句。
                    如果为 None 且提供了 project，会尝试自动查找
            node: 工艺节点（如 S8），用于生成默认 source 语句。
                  如果为 None 且提供了 project，会尝试自动查找
            project: 项目名称（如 dongting），用于生成默认 source 语句。
                    如果提供了 project 但没有提供 foundry 和 node，会尝试自动查找
            flow_name: 流程名称（如 pv_calibre），用于生成默认 source 语句
            prepend_default_sources: 是否在文件头部添加默认的 source 语句。
                                   默认为 False。需要提供 edp_center_path 和 foundry/node 或 project
            full_tcl_path: full.tcl 文件路径，如果提供，会在默认 source 语句之后添加 source full.tcl
            hooks_dir: hooks 目录路径（如 hooks/pv_calibre/ipmerge），用于插入 hooks 文件
            step_name: 步骤名称（如 ipmerge），用于查找 step.pre 和 step.post
            debug_mode: Debug 模式：0=正常执行，1=交互式调试
            skip_sub_steps: 要跳过的 sub_steps 列表（从 user_config.yaml 读取）
        
        Returns:
            如果 output_file 为 None，返回处理后的内容字符串
            如果 output_file 不为 None，返回 None（内容已写入文件）
        """
        # 使用默认值
        if recursive is None:
            recursive = self.default_recursive
        
        # 转换为 Path 对象
        input_file = Path(input_file).resolve()
        
        if not input_file.exists():
            raise EDPFileNotFoundError(
                file_path=str(input_file),
                suggestion="请检查文件路径是否正确，或使用绝对路径"
            )
        
        # 重置已处理文件集合（新文件处理开始时）
        self.processed_files.clear()
        
        # 准备搜索路径和推断路径信息
        edp_center_path, foundry, node, project, flow_name, search_paths = prepare_search_paths(
            input_file, edp_center_path, foundry, node, project, flow_name, search_paths,
            self.base_dir, self.default_search_paths
        )
        
        # 方法A：先整合后处理
        # 
        # 阶段1：整合阶段 - 整合主脚本和所有 hooks（不处理 #import，只是拼接）
        # 整合顺序：
        #   1. step.pre hook（原始内容）
        #   2. 主脚本（处理 #import source 指令）
        #   3. step.post hook（原始内容）
        # 注意：此阶段不处理 #import 指令，只是拼接内容
        assembled_content = assemble_content_with_hooks(
            input_file, search_paths, hooks_dir=hooks_dir, step_name=step_name,
            edp_center_path=edp_center_path, foundry=foundry, node=node,
            project=project, flow_name=flow_name
        )
        
        # 阶段2：处理阶段 - 递归处理整合后的内容中的所有 #import source 指令
        # 包括：
        #   - 主脚本中的 #import source 指令
        #   - hooks 中的 #import source 指令
        #   - 被 source 的文件内部的 #import source 指令（递归处理）
        # 注意：使用字符串处理方式，不需要创建临时文件
        hooks_dir_path = Path(hooks_dir) if hooks_dir else None
        result = self.import_processor.process_imports_in_content(
            assembled_content, input_file, search_paths, hooks_dir=hooks_dir_path, step_name=step_name
        )
        
        # 阶段2.5：自动插入 sub_steps 调用（如果存在 sub_steps）
        # 在主脚本的 pre_step 部分之后、step.post hook 之前插入自动生成的 sub_steps 调用
        if step_name and flow_name and edp_center_path:
            edp_center_path_obj = Path(edp_center_path)
            result = self.sub_steps_processor.insert_auto_generated_sub_steps(
                result, edp_center_path_obj, foundry, node, project, flow_name, step_name, hooks_dir_path
            )
        
        
        # 阶段4：条件化 sub_step 调用（如果指定了 skip_sub_steps）
        if skip_sub_steps and step_name and flow_name and edp_center_path:
            edp_center_path_obj = Path(edp_center_path)
            result = self.sub_steps_processor.wrap_sub_steps_with_conditions(
                result, edp_center_path_obj, foundry, node, project, flow_name, step_name, skip_sub_steps
            )
        
        # 如果需要，在文件头部添加默认的 source 语句
        if prepend_default_sources and edp_center_path:
            result = add_prepend_sources(
                result, input_file, edp_center_path, foundry, node, project, flow_name,
                step_name, full_tcl_path, output_file, search_paths, hooks_dir
            )
        
        # 注意：step hooks 已经在整合阶段添加，不需要再次处理
        
        # Debug 模式处理：如果 debug_mode=1，生成交互式脚本
        if debug_mode == 1 and step_name:
            result = handle_debug_mode(
                result, input_file, edp_center_path, foundry, node, project, flow_name, step_name, hooks_dir
            )
        
        # 如果指定了输出文件，写入文件
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(result, encoding='utf-8')
            logger.debug(f"处理后的脚本已写入: {output_file}")
            return None  # 写入文件时返回 None
        
        return result  # 未指定输出文件时返回内容
    
