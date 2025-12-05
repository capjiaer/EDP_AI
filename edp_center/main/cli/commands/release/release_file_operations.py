#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 文件操作模块
负责文件复制、查找和权限设置
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple, Optional


def copy_files_to_release(file_mappings: List[Tuple], 
                          data_dir: Path, 
                          data_target_dir: Path) -> None:
    """
    复制文件到 RELEASE 目录
    
    Args:
        file_mappings: [(source_path, target_dir, keep_structure, type), ...]
        data_dir: 源数据目录（data/{flow}.{step}/）
        data_target_dir: 目标 step 目录（data/{flow}.{step}/）
    """
    for source_path, target_dir, keep_structure, file_type in file_mappings:
        target_base = data_target_dir / target_dir
        target_base.mkdir(parents=True, exist_ok=True)
        
        if file_type == 'directory':
            # 复制整个目录
            target_path = target_base / source_path.name
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
            print(f"[INFO] 已复制目录: {source_path.name} -> {target_dir}/")
        else:
            # 复制文件
            if keep_structure:
                # 保持源目录结构，但要去掉最外层目录（如果目标目录名和源目录名相同）
                rel_path = source_path.relative_to(data_dir)
                parts = rel_path.parts
                
                # 如果 rel_path 的第一层目录名和 target_dir 相同，则去掉这一层
                if len(parts) > 1 and parts[0] == target_dir:
                    rel_path = Path(*parts[1:])
                
                target_path = target_base / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                # 只复制文件名
                target_path = target_base / source_path.name
            
            shutil.copy2(source_path, target_path)
            print(f"[INFO] 已复制文件: {source_path.name} -> {target_dir}/")


def find_lib_settings(branch_dir: Path, runs_dir: Path) -> Optional[Path]:
    """查找 lib_settings.tcl"""
    # 优先在 runs 目录查找
    if runs_dir.exists():
        lib_settings = runs_dir / 'lib_settings.tcl'
        if lib_settings.exists():
            return lib_settings
    
    # 在 branch 根目录查找
    lib_settings = branch_dir / 'lib_settings.tcl'
    if lib_settings.exists():
        return lib_settings
    
    return None


def set_readonly(release_dir: Path) -> None:
    """设置目录为只读"""
    # 创建 .readonly 标记文件
    readonly_marker = release_dir / '.readonly'
    readonly_marker.touch()
    
    # 设置目录权限（Unix 系统）
    if os.name != 'nt':  # 非 Windows 系统
        import stat
        # 设置目录为只读（555）
        os.chmod(release_dir, stat.S_IRUSR | stat.S_IXUSR | 
                                stat.S_IRGRP | stat.S_IXGRP | 
                                stat.S_IROTH | stat.S_IXOTH)
        
        # 递归设置所有文件为只读（444）
        for root, dirs, files in os.walk(release_dir):
            for d in dirs:
                os.chmod(Path(root) / d, stat.S_IRUSR | stat.S_IXUSR | 
                                            stat.S_IRGRP | stat.S_IXGRP | 
                                            stat.S_IROTH | stat.S_IXOTH)
            for f in files:
                os.chmod(Path(root) / f, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    
    print(f"[INFO] 已设置只读权限")

