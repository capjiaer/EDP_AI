#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 版本管理模块
负责版本号唯一性检查和冲突处理
"""

from pathlib import Path
from typing import List, Tuple


def get_existing_steps(release_dir: Path) -> List[str]:
    """
    获取已存在的步骤列表
    
    Args:
        release_dir: RELEASE 目录
        
    Returns:
        步骤名称列表：['pnr_innovus.place', 'pnr_innovus.postroute', ...]
    """
    existing_steps = []
    data_dir = release_dir / 'data'
    
    if data_dir.exists():
        for step_dir in data_dir.iterdir():
            if step_dir.is_dir():
                existing_steps.append(step_dir.name)
    
    return existing_steps


def ensure_version_unique(release_root: Path, base_version: str, 
                         steps: List[Tuple[str, str]], strict: bool, append: bool, overwrite: bool) -> Tuple[str, str, List[str], List[str], List[str]]:
    """
    确保版本号唯一性（支持多步骤追加模式）
    
    默认行为（不使用 --append）：
    - 如果版本号不存在：直接使用
    - 如果版本号已存在：自动添加时间戳后缀创建新版本（如 v001_20240115_103045）
    - 如果指定 --strict，则版本号存在时报错
    
    追加模式（使用 --append）：
    - 如果版本号已存在但包含不同的步骤：追加到现有版本
    - 如果版本号已存在且包含相同的步骤：报错（或使用 --overwrite 覆盖）
    
    Args:
        release_root: RELEASE 根目录
        base_version: 基础版本号
        steps: 要发布的步骤列表：[(flow_name, step_name), ...]
        strict: 严格模式（如果存在则报错，否则自动添加时间戳创建新版本）
        append: 追加模式（如果版本存在，追加到现有版本而不是创建新版本）
        overwrite: 覆盖模式（如果步骤已存在则覆盖，需要配合 --append 使用）
        
    Returns:
        (最终版本号, 操作类型, 已存在的步骤列表, 新追加的步骤列表, 将覆盖的步骤列表)
        操作类型: 'new' | 'append' | 'overwrite' | 'timestamp'
    """
    release_dir = release_root / base_version
    new_steps = [f"{f}.{s}" for f, s in steps]
    
    if not release_dir.exists():
        return (base_version, 'new', [], new_steps, [])
    
    if strict:
        raise ValueError(f"版本号 {base_version} 已存在，请使用不同的版本号或移除 --strict 选项")
    
    # 如果不使用 --append，默认创建带时间戳的新版本
    if not append:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_version = f"{base_version}_{timestamp}"
        return (timestamped_version, 'timestamp', [], new_steps, [])
    
    # 追加模式：检查已存在的步骤
    existing_steps = get_existing_steps(release_dir)
    
    # 检查冲突
    conflicts = set(existing_steps) & set(new_steps)
    if conflicts:
        if overwrite:
            # 覆盖模式
            overwrite_steps = list(conflicts)
            append_steps = [s for s in new_steps if s not in conflicts]
            return (base_version, 'overwrite', existing_steps, append_steps, overwrite_steps)
        else:
            raise ValueError(
                f"步骤 {conflicts} 已存在于版本 {base_version}，"
                f"使用 --append --overwrite 选项覆盖或使用不同的版本号"
            )
    
    # 如果没有冲突，使用原版本号（追加模式）
    append_steps = [s for s in new_steps if s not in existing_steps]
    return (base_version, 'append', existing_steps, append_steps, [])

