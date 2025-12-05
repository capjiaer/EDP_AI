#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建新项目的文件夹结构
"""

import sys
import shutil
from pathlib import Path
from typing import Optional


def copy_directory_structure(source: Path, target: Path, exclude_patterns: Optional[list] = None) -> None:
    """
    复制目录结构（只复制目录，不复制文件内容）
    
    Args:
        source: 源目录路径
        target: 目标目录路径
        exclude_patterns: 要排除的目录名列表（如 ['.git', '__pycache__']）
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    if not source.exists():
        raise FileNotFoundError(f"源目录不存在: {source}")
    
    if not source.is_dir():
        raise ValueError(f"源路径不是目录: {source}")
    
    # 创建目标目录
    target.mkdir(parents=True, exist_ok=True)
    
    # 遍历源目录
    for item in source.iterdir():
        # 跳过排除的目录
        if item.name in exclude_patterns:
            continue
        
        target_item = target / item.name
        
        if item.is_dir():
            # 递归复制子目录
            copy_directory_structure(item, target_item, exclude_patterns)
        # 注意：这里不复制文件，只复制目录结构


def copy_directory_with_files(source: Path, target: Path, exclude_patterns: Optional[list] = None, skip_existing: bool = False) -> None:
    """
    复制目录及其文件内容（递归复制所有子目录和文件）
    
    Args:
        source: 源目录路径
        target: 目标目录路径
        exclude_patterns: 要排除的文件/目录名列表
        skip_existing: 如果为 True，已存在的文件不覆盖（用于 --force 模式）
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    if not source.exists():
        raise FileNotFoundError(f"源目录不存在: {source}")
    
    if not source.is_dir():
        raise ValueError(f"源路径不是目录: {source}")
    
    # 创建目标目录
    target.mkdir(parents=True, exist_ok=True)
    
    # 遍历源目录
    for item in source.iterdir():
        # 跳过排除的文件/目录
        if item.name in exclude_patterns:
            continue
        
        target_item = target / item.name
        
        if item.is_dir():
            # 递归复制子目录
            copy_directory_with_files(item, target_item, exclude_patterns, skip_existing)
        elif item.is_file():
            # 复制文件
            if skip_existing and target_item.exists():
                # 如果文件已存在且 skip_existing=True，跳过不覆盖
                continue
            shutil.copy2(item, target_item)


def create_project_structure(edp_center_path: Path, project_name: str, foundry: str, node: str) -> int:
    """
    创建新项目的文件夹结构
    
    Args:
        edp_center_path: EDP Center 根目录路径
        project_name: 项目名称（如 new_prj）
        foundry: 代工厂名称（如 TSMC）
        node: 工艺节点（如 n8）
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    try:
        edp_center = Path(edp_center_path).resolve()
        
        if not edp_center.exists():
            print(f"[ERROR] EDP Center 路径不存在: {edp_center}", file=sys.stderr)
            return 1
        
        # 1. 创建 flow/initialize/{foundry}/{node}/ 下的结构
        flow_initialize_base = edp_center / "flow" / "initialize" / foundry / node
        flow_initialize_base.mkdir(parents=True, exist_ok=True)
        
        # 检查目标 node 下是否有 common，如果没有，从模板复制
        common_flow_dir = flow_initialize_base / "common"
        if not common_flow_dir.exists():
            # 从模板 foundry_name/node_name/common 复制到目标 node 的 common
            template_common_dir = edp_center / "flow" / "initialize" / "foundry_name" / "node_name" / "common"
            if template_common_dir.exists():
                print(f"[INFO] 目标 node 下没有 common，正在从模板复制 common...")
                copy_directory_with_files(template_common_dir, common_flow_dir, skip_existing=True)
                print(f"[OK] 已创建 flow/initialize/{foundry}/{node}/common/")
            else:
                print(f"[ERROR] 模板 common 目录不存在: {template_common_dir}", file=sys.stderr)
                return 1
        
        # 从模板 prj_example 复制到新项目
        template_prj_example_dir = edp_center / "flow" / "initialize" / "foundry_name" / "node_name" / "prj_example"
        if not template_prj_example_dir.exists():
            print(f"[ERROR] 模板 prj_example 目录不存在: {template_prj_example_dir}", file=sys.stderr)
            return 1
        
        source_flow_dir = template_prj_example_dir
        source_name = "prj_example"
        
        # 创建项目目录（如果已存在，只创建缺失的内容，不覆盖已有文件）
        project_flow_dir = flow_initialize_base / project_name
        if project_flow_dir.exists():
            print(f"[INFO] 项目目录已存在，将补充缺失的目录和文件（已存在的文件不会覆盖）...")
        else:
            print(f"[INFO] 正在从 {source_name} 创建 flow/initialize/{foundry}/{node}/{project_name}/...")
        copy_directory_with_files(source_flow_dir, project_flow_dir, skip_existing=True)
        print(f"[OK] 已创建 flow/initialize/{foundry}/{node}/{project_name}/")
        
        # 2. 创建 config/{foundry}/{node}/ 下的结构
        config_base = edp_center / "config" / foundry
        config_base.mkdir(parents=True, exist_ok=True)
        
        config_node_dir = config_base / node
        config_node_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查目标 node 下是否有 common，如果没有，从模板复制
        common_config_dir = config_node_dir / "common"
        if not common_config_dir.exists():
            # 从模板 foundry_name/node_name/common 复制到目标 node 的 common
            template_common_config_dir = edp_center / "config" / "foundry_name" / "node_name" / "common"
            if template_common_config_dir.exists():
                print(f"[INFO] 目标 node 下没有 common，正在从模板复制 common...")
                copy_directory_with_files(template_common_config_dir, common_config_dir, skip_existing=True)
                print(f"[OK] 已创建 config/{foundry}/{node}/common/")
            else:
                print(f"[ERROR] 模板 common 目录不存在: {template_common_config_dir}", file=sys.stderr)
                return 1
        
        # 从模板 prj_example 复制到新项目
        template_prj_example_config_dir = edp_center / "config" / "foundry_name" / "node_name" / "prj_example"
        if not template_prj_example_config_dir.exists():
            print(f"[ERROR] 模板 prj_example 目录不存在: {template_prj_example_config_dir}", file=sys.stderr)
            return 1
        
        source_config_dir = template_prj_example_config_dir
        source_name = "prj_example"
        
        # 创建项目目录（如果已存在，只创建缺失的内容，不覆盖已有文件）
        project_config_dir = config_node_dir / project_name
        if project_config_dir.exists():
            print(f"[INFO] 项目配置目录已存在，将补充缺失的目录和文件（已存在的文件不会覆盖）...")
        else:
            print(f"[INFO] 正在从 {source_name} 创建 config/{foundry}/{node}/{project_name}/...")
        copy_directory_with_files(source_config_dir, project_config_dir, skip_existing=True)
        print(f"[OK] 已创建 config/{foundry}/{node}/{project_name}/")
        
        print(f"\n[OK] 项目 '{project_name}' 的文件夹结构已创建完成！")
        print(f"  - flow/initialize/{foundry}/{node}/{project_name}/")
        print(f"  - config/{foundry}/{node}/{project_name}/")
        print(f"\n[INFO] 现在可以在这些目录中填写项目特定的内容了。")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] 创建项目结构失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def handle_create_project(edp_center_path: Path, args) -> int:
    """
    处理 -create_project 命令
    
    Args:
        edp_center_path: EDP Center 路径
        args: 命令行参数对象（args.create_project 是一个包含 [project, foundry, node] 的列表）
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    if not args.create_project or len(args.create_project) != 3:
        print("[ERROR] -create_project 需要 3 个参数: PROJECT_NAME FOUNDRY NODE", file=sys.stderr)
        print("示例: edp -create_project new_prj TSMC n8", file=sys.stderr)
        return 1
    
    project_name, foundry, node = args.create_project
    
    return create_project_structure(edp_center_path, project_name, foundry, node)

