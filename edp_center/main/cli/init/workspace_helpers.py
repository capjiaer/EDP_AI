#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init workspace 相关的辅助函数
"""

import sys
import yaml
from pathlib import Path
from typing import Optional, Dict

from ..utils import get_current_user
from .params import find_edp_version_file


def infer_params_from_path(manager, current_dir: Path, args) -> Optional[Dict[str, str]]:
    """
    从当前路径推断参数（使用 detect_project_path）
    
    Args:
        manager: WorkflowManager 实例
        current_dir: 当前目录
        args: 命令行参数对象
        
    Returns:
        检测到的项目信息字典，如果失败返回 None
    """
    search_dir = current_dir
    detected = None
    
    # 向上查找，直到根目录或找到有效路径
    while search_dir != search_dir.parent:
        detected = manager.work_path_initializer.path_detector.detect_project_path(
            search_dir,
            manager.work_path_initializer.config_loader.load_init_project_config
        )
        if detected:
            detected_work_path = Path(detected['work_path']).resolve()
            
            # 检查当前目录是否在检测到的 work_path 下
            try:
                current_dir.relative_to(detected_work_path)
                # 当前目录在 work_path 下，使用检测到的 work_path
                args.work_path = str(detected_work_path)
            except ValueError:
                # 当前目录不在 work_path 下，继续向上查找
                search_dir = search_dir.parent
                continue
            
            # 使用检测到的信息填充缺失的参数
            if not args.project:
                args.project = detected['project_name']
            # 注意：detect_project_path 返回的是 'project_node'，需要映射到 'version'
            version = detected.get('version') or detected.get('project_node')
            if not getattr(args, 'version', None):
                if hasattr(args, 'version'):
                    args.version = version
            if not args.block:
                args.block = detected['block_name']
            
            # 从当前路径中提取 user（如果当前目录在 user 目录下）
            path_parts = current_dir.parts
            detected_work_path_parts = detected_work_path.parts
            if len(path_parts) > len(detected_work_path_parts):
                # 当前目录比 work_path 更深
                # 检查是否是 {project}/{version}/{block}/{user} 结构
                if args.project in path_parts:
                    project_idx = path_parts.index(args.project)
                    # 检查路径结构：{project}/{version}/{block}/{user}
                    if project_idx + 3 < len(path_parts):
                        if not args.user:
                            args.user = path_parts[project_idx + 3]
            
            print("[OK] 从当前目录自动推断：")
            print(f"  work_path: {args.work_path}")
            print(f"  project: {args.project}")
            print(f"  version: {version}")
            print(f"  block: {args.block}")
            if args.user:
                print(f"  user: {args.user}")
            return detected
        
        search_dir = search_dir.parent
    
    return None


# 注意：infer_params_from_version_file 已统一到 params.py 中
# 如果需要使用，请从 params 模块导入：from .params import infer_params_from_version_file


def validate_block(work_path: Path, project: str, version: str, block: str) -> bool:
    """
    验证 block 是否存在且合法
    
    Args:
        work_path: WORK_PATH 根目录
        project: 项目名称
        version: 项目版本名称
        block: block 名称
        
    Returns:
        是否验证通过
    """
    # 验证 block 是否存在（必须通过 init 创建）
    block_path = work_path / project / version / block
    if not block_path.exists() or not block_path.is_dir():
        print(f"[ERROR] block '{block}' 不存在", file=sys.stderr)
        print(f"[ERROR] 请先运行 'edp -init -blk {block}' 创建 block", file=sys.stderr)
        return False
    
    # 验证 block 是否在 .edp_version 中记录（确保是通过 init 创建的）
    version_info_file = work_path / project / version / '.edp_version'
    if version_info_file.exists():
        try:
            with open(version_info_file, 'r', encoding='utf-8') as f:
                version_info = yaml.safe_load(f) or {}
            blocks = version_info.get('blocks', {})
            if block not in blocks:
                print(f"[ERROR] block '{block}' 未通过 'edp -init' 创建", file=sys.stderr)
                print(f"[ERROR] 请先运行 'edp -init -blk {block}' 创建 block", file=sys.stderr)
                return False
        except Exception:
            # 如果读取失败，至少验证目录存在
            pass
    
    return True


def format_workspace_output(paths: dict):
    """
    格式化输出工作空间初始化结果
    
    Args:
        paths: 工作空间路径信息字典
    """
    # 格式化输出：分支路径
    if 'branch_path' in paths:
        print(f"分支路径:")
        print(f"  {paths['branch_path']}")
        print()
    
    # 格式化输出：目录
    if 'directories' in paths and paths['directories']:
        print("创建的目录:")
        for dir_name, dir_path in sorted(paths['directories'].items()):
            print(f"  - {dir_name:12s} {dir_path}")
        print()
    
    # 格式化输出：文件
    if 'files' in paths and paths['files']:
        print("创建的文件:")
        for file_name, file_path in sorted(paths['files'].items()):
            print(f"  - {file_name:20s} {file_path}")

