#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init 参数推断和解析相关函数
"""

import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Tuple

from ..utils import get_current_user


def find_edp_version_file(start_dir: Path) -> Tuple[Optional[Path], Optional[dict]]:
    """
    向上查找 .edp_version 文件，直到根目录
    
    Args:
        start_dir: 起始目录
        
    Returns:
        (version_file_path, version_info) 或 (None, None)
    """
    search_dir = start_dir
    while search_dir != search_dir.parent:  # 直到根目录
        version_file = search_dir / '.edp_version'
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_info = yaml.safe_load(f) or {}
                return version_file, version_info
            except Exception:
                pass
        search_dir = search_dir.parent
    return None, None


def infer_params_from_version_file(args, manager, current_dir: Optional[Path] = None) -> bool:
    """
    从 .edp_version 文件推断参数（project, version, work_path, block, user）
    
    使用统一推断模块进行推断
    
    Args:
        args: 命令行参数对象
        manager: WorkflowManager 实例（必需）
        current_dir: 可选的当前目录（如果提供，使用此目录；否则使用 Path.cwd()）
        
    Returns:
        是否成功推断参数
    
    Raises:
        ValueError: 如果 manager 为 None
    """
    if manager is None:
        raise ValueError("manager 参数是必需的，不能为 None")
    version = getattr(args, 'version', None)
    if args.project and version:
        return False  # 已经有参数，不需要推断
    
    if current_dir is None:
        current_dir = Path.cwd()
    
    # 使用统一推断模块
    from ..utils import UnifiedInference
    inference = UnifiedInference(manager.edp_center)
    work_path_info = inference.infer_work_path_info(current_dir, args)
        
    if work_path_info:
        # 从推断结果填充参数
        # 如果 work_path 是默认值 '.' 或者当前目录在推断出的 work_path 下，使用推断出的 work_path
        inferred_work_path = work_path_info['work_path']
        current_work_path = Path(getattr(args, 'work_path', '.')).resolve()
        
        # 如果当前 work_path 是默认值 '.'，或者当前目录在推断出的 work_path 下，使用推断出的 work_path
        if not args.work_path or args.work_path == '.':
            args.work_path = str(inferred_work_path)
        else:
            # 检查当前 work_path 是否在推断出的 work_path 下
            try:
                current_work_path.relative_to(inferred_work_path)
                # 当前 work_path 在推断出的 work_path 下，使用推断出的 work_path
                args.work_path = str(inferred_work_path)
            except ValueError:
                # 当前 work_path 不在推断出的 work_path 下，保持使用当前 work_path
                pass
        
        if not args.project:
            args.project = work_path_info['project']
        version = work_path_info['version']
        if not getattr(args, 'version', None):
            if hasattr(args, 'version'):
                args.version = version
        
        # 填充 block 和 user（如果存在且未设置）
        if not args.block and work_path_info.get('block'):
            args.block = work_path_info['block']
        if not args.user and work_path_info.get('user'):
            args.user = work_path_info['user']
        
        print(f"[OK] 从 .edp_version 文件推断：")
        print(f"  work_path: {args.work_path}")
        print(f"  project: {args.project}")
        print(f"  version: {version}")
        if args.block:
            print(f"  block: {args.block}")
        if args.user:
            print(f"  user: {args.user}")
        return True
    
    return False


def load_config_file(work_path: Path, config_path: Optional[Path] = None) -> dict:
    """
    加载 config.yaml 文件
    
    Args:
        work_path: WORK_PATH 根目录
        config_path: 指定的配置文件路径（可选，如果提供则使用此路径，否则使用 work_path/config.yaml）
        
    Returns:
        配置字典，如果文件不存在返回空字典
    """
    if config_path:
        # 如果指定了配置文件路径，使用指定的路径
        config_file = Path(config_path).resolve()
    else:
        # 否则使用默认路径
        config_file = work_path / 'config.yaml'
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            print(f"[OK] 找到 config.yaml: {config_file}")
            return config
        except Exception:
            pass
    return {}


def merge_params(args, config: dict) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    合并参数：优先使用命令行参数，然后从 config.yaml 读取
    
    Args:
        args: 命令行参数对象
        config: config.yaml 配置字典
        
    Returns:
        (project, version, block, user)
    """
    project = args.project
    version = getattr(args, 'version', None)
    block = args.block
    user = args.user
    
    if config:
        # 如果存在 config.yaml，优先使用 config.yaml 的参数（但命令行参数优先级更高）
        # 所有配置都在 project 下
        project_config = config.get('project', {})
        if not isinstance(project_config, dict):
            # 如果 project 不是字典，说明配置格式错误
            print("[ERROR] config.yaml 格式错误：project 必须是字典格式", file=sys.stderr)
            print("[ERROR] 正确格式：", file=sys.stderr)
            print("[ERROR]   project:", file=sys.stderr)
            print("[ERROR]     name: dongting", file=sys.stderr)
            print("[ERROR]     version: P85", file=sys.stderr)
            print("[ERROR]     blocks: {...}", file=sys.stderr)
            return None, None, None, None
        
        # 从 project 下读取所有配置
        project = project or project_config.get('name')
        version = version or project_config.get('version')
        if not block:
            block = project_config.get('block')
        if not user:
            user = project_config.get('user')
    
    return project, version, block, user


def validate_required_params(project: Optional[str], version: Optional[str]) -> bool:
    """
    验证必需参数
    
    Args:
        project: 项目名称
        version: 项目版本名称
        
    Returns:
        是否验证通过
    """
    if not project:
        print("[ERROR] 错误: 缺少 --project 参数，且 config.yaml 和 .edp_version 中未找到 project", file=sys.stderr)
        return False
    if not version:
        print("[ERROR] 错误: 缺少 --version 参数，且 config.yaml 和 .edp_version 中未找到 version", file=sys.stderr)
        return False
    return True


def process_blocks_config(block: Optional[str], user: Optional[str], blocks_config: dict) -> Dict[str, list]:
    """
    处理 blocks 配置，返回需要初始化的 blocks 和 users
    
    Args:
        block: 命令行指定的 block（单个值）
        user: 命令行指定的 user（单个值）
        blocks_config: config.yaml 中的 blocks 配置
        
    Returns:
        {block_name: [user1, user2, ...]} 字典
    """
    # 如果命令行参数指定了 block 和 user，只初始化指定的
    if block and user:
        return {block: [user]}
    
    # 如果命令行参数指定了 block，但没有指定 user
    if block:
        # 如果 block 在 config.yaml 中，从 config 中获取该 block 的所有 user
        if blocks_config.get(block):
            users = blocks_config[block]
            # 支持字符串（空格分隔）或列表格式
            if isinstance(users, str):
                users = users.split()
            return {block: users}
        else:
            # 如果 block 不在 config.yaml 中，使用当前系统用户作为默认 user
            return {block: [get_current_user()]}
    
    # 如果命令行参数都没有指定，从 config 中获取所有 blocks
    if blocks_config:
        blocks_to_init = {}
        for blk_name, users in blocks_config.items():
            # 支持字符串（空格分隔）或列表格式
            if isinstance(users, str):
                users = users.split()
            blocks_to_init[blk_name] = users
        return blocks_to_init
    
    # 如果都没有，返回空字典（调用者需要处理错误）
    return {}

