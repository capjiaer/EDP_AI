#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 步骤处理模块
负责处理单个步骤的 release 操作
"""

import shutil
from pathlib import Path
from typing import Dict, Optional

from .release_file_mapper import get_file_mappings
from .release_file_operations import copy_files_to_release, find_lib_settings


def release_single_step(manager, args, branch_dir: Path, release_dir: Path,
                       data_target_dir: Path, flow_name: str, step_name: str,
                       project_info: Dict, project: Optional[str]) -> str:
    """
    Release 单个步骤的数据
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        branch_dir: 分支目录
        release_dir: RELEASE 目录
        data_target_dir: 目标 data 目录
        flow_name: 流程名称
        step_name: 步骤名称
        project_info: 项目信息
        project: 项目名称（可选）
        
    Returns:
        'success', 'skip', 或 'error'
    """
    # 1. 确定数据源目录
    step_dir_name = f"{flow_name}.{step_name}"
    data_dir = branch_dir / 'data' / step_dir_name
    runs_dir = branch_dir / 'runs' / step_dir_name
    
    # 2. 检查数据是否存在（允许创建空目录占位）
    has_data = data_dir.exists() or runs_dir.exists()
    if not has_data:
        print(f"[INFO] 步骤 {step_dir_name} 的数据目录不存在，将创建空目录占位")
    
    # 3. 加载配置
    foundry = project_info.get('foundry')
    node = project_info.get('node')
    try:
        config = manager.load_config(
            foundry=foundry,
            node=node,
            project=project or 'common',
            flow=flow_name
        )
    except Exception as e:
        print(f"[WARN] 无法加载步骤 {step_dir_name} 的配置: {e}，将使用默认设置")
        config = {}
    
    # 4. 创建 step 目录（统一使用 data/{step}/ 结构）
    step_target_dir = data_target_dir / step_dir_name
    step_target_dir.mkdir(parents=True, exist_ok=True)
    
    # 5. 获取文件映射（仅当数据存在时）
    if has_data:
        file_mappings = get_file_mappings(
            config, flow_name, step_name, data_dir, args
        )
        
        # 6. 复制文件到 step 目录
        copy_files_to_release(file_mappings, data_dir, step_target_dir)
    else:
        print(f"[INFO] 步骤 {step_dir_name} 无数据文件，仅创建目录结构")
    
    # 7. 复制 lib_settings.tcl 到 step 目录（如果存在）
    if runs_dir.exists():
        lib_settings_source = find_lib_settings(branch_dir, runs_dir)
        if lib_settings_source and lib_settings_source.exists():
            shutil.copy2(lib_settings_source, step_target_dir / 'lib_settings.tcl')
            print(f"[INFO] 已复制 lib_settings.tcl 到 {step_dir_name}/")
        else:
            print(f"[WARN] 未找到 lib_settings.tcl，跳过")
        
        # 8. 复制 full.tcl 到 step 目录（如果存在）
        full_tcl_source = runs_dir / 'full.tcl'
        if full_tcl_source.exists():
            shutil.copy2(full_tcl_source, step_target_dir / 'full.tcl')
            print(f"[INFO] 已复制 full.tcl 到 {step_dir_name}/")
    else:
        print(f"[INFO] 步骤 {step_dir_name} 无 runs 目录，跳过 lib_settings.tcl 和 full.tcl")
    
    return 'success'

