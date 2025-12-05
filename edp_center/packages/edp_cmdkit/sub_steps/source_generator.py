#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Source Generator - Sub Steps Source 语句生成模块

负责从 dependency.yaml 读取 sub_steps，生成对应的 source 语句。
"""

from pathlib import Path
from typing import List, Optional
import logging

from .reader import read_sub_steps_from_dependency
from .proc_processor import ensure_global_declarations_in_proc
from edp_center.packages.edp_common.path_utils import to_tcl_path
from .hooks_integration import (
    collect_sub_step_hooks,
    generate_replace_hooks_code,
    generate_pre_hooks_code,
    generate_post_hooks_code
)

logger = logging.getLogger(__name__)


def _find_dependency_yaml_path(edp_center_path: Path, foundry: str, node: str,
                                project: Optional[str], flow_name: str) -> Optional[Path]:
    """
    查找 dependency.yaml 文件路径
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
    
    Returns:
        dependency.yaml 文件路径，如果不存在返回 None
    """
    config_path = edp_center_path / 'config' / foundry / node
    config_search_paths = []
    
    # 1. common 路径（优先级低）
    common_path = config_path / 'common'
    if common_path.exists():
        config_search_paths.append(common_path)
    
    # 2. 项目特定路径（优先级高，会覆盖 common）
    if project:
        project_path = config_path / project
        if project_path.exists():
            config_search_paths.append(project_path)
    
    # 从高优先级到低优先级查找（项目特定的会覆盖 common）
    for config_dir in reversed(config_search_paths):
        flow_dir = config_dir / flow_name
        dependency_file = flow_dir / 'dependency.yaml'
        if dependency_file.exists():
            return dependency_file
    
    return None


def _extract_namespaces(sub_steps: List[dict]) -> set:
    """
    从 sub_steps 中提取所有使用的 namespace
    
    Args:
        sub_steps: sub_steps 列表，格式为 [{file_name: proc_name}, ...]
    
    Returns:
        namespace 集合
    """
    namespaces = set()
    for sub_step in sub_steps:
        if isinstance(sub_step, dict) and len(sub_step) == 1:
            _, proc_name = next(iter(sub_step.items()))
            # 提取 namespace（如果 proc_name 包含 ::）
            if '::' in proc_name:
                # 处理以 :: 开头的情况（如 ::pnr_innovus::restore_design）
                parts = proc_name.split('::')
                # 过滤掉空字符串（由开头的 :: 产生）
                parts = [p for p in parts if p]
                if len(parts) >= 2:  # 至少要有 namespace 和 proc_name
                    namespace = parts[0]
                    namespaces.add(namespace)
    return namespaces


def _build_search_paths(edp_center_path: Path, foundry: str, node: str,
                        project: Optional[str], flow_name: str,
                        search_paths: List[Path]) -> List[Path]:
    """
    构建 sub_step 文件的搜索路径
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        search_paths: 原始搜索路径列表
    
    Returns:
        合并后的搜索路径列表
    """
    sub_steps_search_paths = []
    
    # 1. 优先查找项目特定的 sub_steps 目录（如果存在项目）
    if project:
        project_sub_steps_dir = (edp_center_path / 'flow' / 'initialize' / foundry / node / 
                               project / 'cmds' / flow_name / 'sub_steps')
        if project_sub_steps_dir.exists():
            sub_steps_search_paths.append(project_sub_steps_dir)
            logger.debug(f"找到项目 sub_steps 目录: {project_sub_steps_dir}")
    
    # 2. 查找 common 的 sub_steps 目录（作为后备）
    common_sub_steps_dir = (edp_center_path / 'flow' / 'initialize' / foundry / node / 
                          'common' / 'cmds' / flow_name / 'sub_steps')
    if common_sub_steps_dir.exists():
        sub_steps_search_paths.append(common_sub_steps_dir)
        logger.debug(f"找到 common sub_steps 目录: {common_sub_steps_dir}")
    
    # 合并搜索路径：sub_steps 目录优先，然后是 helpers 目录，最后是原始 search_paths
    # helpers 目录用于 sub_steps 文件中的 #import source
    helpers_search_paths = []
    if project:
        project_helpers_dir = (edp_center_path / 'flow' / 'initialize' / foundry / node / 
                             project / 'cmds' / flow_name / 'helpers')
        if project_helpers_dir.exists():
            helpers_search_paths.append(project_helpers_dir)
    common_helpers_dir = (edp_center_path / 'flow' / 'initialize' / foundry / node / 
                         'common' / 'cmds' / flow_name / 'helpers')
    if common_helpers_dir.exists():
        helpers_search_paths.append(common_helpers_dir)
    
    return sub_steps_search_paths + helpers_search_paths + search_paths


def _process_sub_step_file(sub_step_file: Path, proc_name: str, flow_name: str,
                           final_search_paths: List[Path]) -> Optional[str]:
    """
    处理单个 sub_step 文件
    
    Args:
        sub_step_file: sub_step 文件路径
        proc_name: proc 名称
        flow_name: 流程名称
        final_search_paths: 最终搜索路径列表
    
    Returns:
        处理后的文件内容，如果处理失败返回 None
    """
    # 读取文件内容并处理其中的 #import source 指令
    try:
        sub_step_content = sub_step_file.read_text(encoding='utf-8')
    except Exception as e:
        logger.warning(f"无法读取 sub_step 文件 {sub_step_file}: {e}，跳过")
        return None
    
    # 处理文件中的 #import source 指令（递归处理）
    from ..import_processor import ImportProcessor
    import_processor = ImportProcessor(set())  # 使用新的 processed_files 集合
    processed_content = import_processor.process_content(
        sub_step_file, final_search_paths, hooks_dir=None, step_name=None
    )
    
    # 确保 proc 中有有效的 global 声明（移除注释掉的，自动添加缺失的）
    processed_content = ensure_global_declarations_in_proc(processed_content, flow_name)
    
    # 在 proc 定义前面添加源文件路径注释
    # 将路径转换为 Tcl 兼容格式（使用正斜杠）
    tcl_file_path = to_tcl_path(sub_step_file)
    
    # 找到第一个 proc 定义的位置，在前面插入路径注释
    lines = processed_content.splitlines(keepends=True)
    proc_insert_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        # 找到第一个 proc 定义（忽略注释）
        if stripped.startswith('proc ') and not stripped.startswith('#'):
            proc_insert_idx = i
            break
    
    if proc_insert_idx >= 0:
        # 在 proc 定义前面插入路径注释
        lines.insert(proc_insert_idx, f"# {tcl_file_path}\n")
        processed_content = ''.join(lines)
    
    # 确保 processed_content 以换行符结尾（避免注释直接跟在 } 后面）
    if processed_content and not processed_content.endswith('\n'):
        processed_content += '\n'
    
    return processed_content


def generate_sub_steps_sources(edp_center_path: Path, foundry: str, node: str,
                                project: Optional[str], flow_name: str, step_name: str,
                                current_file: Path, search_paths: List[Path],
                                hooks_dir: Optional[Path] = None) -> str:
    """
    从 dependency.yaml 读取 sub_steps，生成对应的 source 语句
    
    sub_steps 格式：字典格式 {file_name: proc_name}
    - 例如：{"innovus_restore_design.tcl": "pnr_innovus::restore_design"}
    - 在 dependency.yaml 中：sub_steps: {file_name: proc_name, ...}
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        step_name: 步骤名称
        current_file: 当前文件路径（用于推断 flow 目录）
        search_paths: 搜索路径列表（作为后备搜索路径）
        hooks_dir: hooks 目录路径
    
    Returns:
        生成的 source 语句字符串
    """
    # 从 dependency.yaml 读取 sub_steps
    sub_steps = read_sub_steps_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
    if not sub_steps:
        return ""
    
    source_lines = []
    
    # 添加注释头
    dependency_yaml_path = _find_dependency_yaml_path(edp_center_path, foundry, node, project, flow_name)
    if dependency_yaml_path:
        tcl_path = to_tcl_path(dependency_yaml_path)
        source_lines.append(f"# Auto-generated sub_steps source statements based on {tcl_path}\n")
    else:
        source_lines.append("# Auto-generated sub_steps source statements\n")
    
    # 创建 namespace
    namespaces = _extract_namespaces(sub_steps)
    if namespaces:
        source_lines.append("# Create namespaces for sub_step procs\n")
        for namespace in sorted(namespaces):  # 排序以保证一致性
            source_lines.append(f"namespace eval {namespace} {{}}\n")
        source_lines.append("\n")
    
    # 收集所有 hooks
    hooks_info = collect_sub_step_hooks(sub_steps, hooks_dir, flow_name)
    sub_step_replace_hooks = hooks_info['replace']
    sub_step_pre_procs = hooks_info['pre']
    sub_step_post_procs = hooks_info['post']
    
    # 构建搜索路径
    final_search_paths = _build_search_paths(edp_center_path, foundry, node, project, flow_name, search_paths)
    
    # 第一阶段：处理所有 sub_step 文件，生成 source 语句
    for sub_step in sub_steps:
        # sub_steps 应该是字典格式：{file_name: proc_name}
        if not isinstance(sub_step, dict):
            logger.warning(f"sub_step 格式错误，应该是字典格式 {{file_name: proc_name}}: {sub_step}，跳过")
            continue
        
        if len(sub_step) != 1:
            logger.warning(f"sub_step 字典格式错误，应该是单个键值对: {sub_step}，跳过")
            continue
        
        file_name, proc_name = next(iter(sub_step.items()))
        # 确保文件名有 .tcl 扩展名
        if not file_name.endswith('.tcl'):
            file_name = file_name + '.tcl'
        
        try:
            # 查找 sub_step 文件
            from ..file_finder import find_file
            sub_step_file = find_file(file_name, current_file, final_search_paths, recursive=True)
            
            if not sub_step_file:
                logger.warning(f"未找到 sub_step 文件: {file_name}，跳过")
                continue
            
            # 处理 sub_step 文件
            processed_content = _process_sub_step_file(sub_step_file, proc_name, flow_name, final_search_paths)
            if not processed_content:
                continue
            
            # 直接展开处理后的内容，而不是生成 source 语句
            source_lines.append(f"# ========== Sub_step: {file_name} (proc: {proc_name}) ==========\n")
            source_lines.append(processed_content)
            source_lines.append(f"# ========== End of Sub_step: {file_name} ==========\n\n")
            logger.debug(f"已展开 sub_step 内容: {file_name} (proc: {proc_name})")
        except Exception as e:
            logger.warning(f"处理 sub_step 文件 {file_name} 时出错: {e}，跳过")
            continue
    
    # 第二阶段：添加所有 replace hooks（在所有 source 之后）
    source_lines.extend(generate_replace_hooks_code(sub_step_replace_hooks))
    
    # 第三阶段：生成 pre-step procs（在所有 replace hooks 之后）
    source_lines.extend(generate_pre_hooks_code(sub_step_pre_procs, flow_name))
    
    # 第四阶段：生成 post-step procs（在所有 pre-step procs 之后）
    source_lines.extend(generate_post_hooks_code(sub_step_post_procs, flow_name))
    
    return ''.join(source_lines) if source_lines else ""

