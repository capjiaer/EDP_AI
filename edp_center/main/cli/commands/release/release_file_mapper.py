#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 文件映射模块
负责文件映射规则的解析和文件匹配
"""

import os
import fnmatch
from pathlib import Path
from typing import Dict, List, Tuple


def get_file_mappings(config: Dict, flow_name: str, step_name: str, 
                     data_dir: Path, args) -> List[Tuple[Path, str, bool, str]]:
    """
    获取文件映射列表
    
    Returns:
        [(source_path, target_dir, keep_structure, type), ...]
    """
    # 1. 获取配置中的 file_mappings
    release_config = config.get('release', {})
    
    # 先使用通用规则
    file_mappings_config = release_config.get('file_mappings', {}).copy()
    
    # 检查是否有 step 特定规则（增量覆盖，只覆盖指定的映射）
    step_rules = release_config.get('step_rules', {})
    if step_name in step_rules:
        step_rule = step_rules[step_name]
        step_specific_mappings = step_rule.get('file_mappings', {})
        
        # 处理排除列表（如果指定了 exclude）
        exclude_list = step_rule.get('exclude', [])
        for exclude_key in exclude_list:
            if exclude_key in file_mappings_config:
                del file_mappings_config[exclude_key]
        
        # 增量覆盖：只更新 step 特定规则中指定的映射
        # 如果映射值为 null 或空字符串，则排除该映射
        for key, value in step_specific_mappings.items():
            if value is None or value == "":
                # 排除该映射
                if key in file_mappings_config:
                    del file_mappings_config[key]
            else:
                # 更新映射
                file_mappings_config[key] = value
    
    keep_structure_dirs = release_config.get('keep_structure', [])
    
    # 2. 应用命令行参数覆盖
    if args.include_all:
        # 包含所有文件（使用默认映射）
        file_mappings_config = get_default_mappings()
    elif args.include_patterns:
        # 从模式构建映射
        patterns = [p.strip() for p in args.include_patterns.split(',')]
        file_mappings_config = build_mappings_from_patterns(patterns)
    
    # 3. 解析并匹配文件
    file_mappings = []
    
    for target_dir, source_paths_str in file_mappings_config.items():
        # 解析源文件路径列表
        if isinstance(source_paths_str, str):
            source_paths = source_paths_str.split()
        else:
            source_paths = source_paths_str
        
        keep_structure = target_dir in keep_structure_dirs
        
        # 处理每个源路径
        for source_path in source_paths:
            if source_path.startswith('@'):
                # 目录类型：@libs -> 复制整个 libs 目录
                dir_name = source_path[1:]
                full_dir_path = data_dir / dir_name
                if full_dir_path.exists() and full_dir_path.is_dir():
                    file_mappings.append((full_dir_path, target_dir, keep_structure, 'directory'))
            else:
                # 文件类型：匹配文件
                matched_files = match_files_by_pattern(data_dir, source_path)
                for file_path in matched_files:
                    file_mappings.append((file_path, target_dir, keep_structure, 'file'))
    
    # 4. 应用排除模式
    if args.exclude_patterns:
        exclude_patterns = [p.strip() for p in args.exclude_patterns.split(',')]
        file_mappings = filter_excluded_files(file_mappings, exclude_patterns, data_dir)
    
    return file_mappings


def get_default_mappings() -> Dict[str, str]:
    """获取默认的文件映射"""
    return {
        'def': '**/*.def',
        'db': '**/*.db',
        'sdf': '**/*.sdf',
        'spef': '**/*.spef',
        'verilog': '**/*.v **/*.vg',
        'config': '**/*.tcl **/*.sdc',
    }


def build_mappings_from_patterns(patterns: List[str]) -> Dict[str, str]:
    """从模式列表构建映射"""
    # 简单实现：将所有模式映射到对应的目录
    mappings = {}
    for pattern in patterns:
        # 根据文件扩展名推断目标目录
        ext = pattern.split('.')[-1] if '.' in pattern else 'other'
        target_dir = ext.lower()
        if target_dir not in mappings:
            mappings[target_dir] = []
        mappings[target_dir].append(pattern)
    
    # 转换为字符串格式
    return {k: ' '.join(v) for k, v in mappings.items()}


def match_files_by_pattern(data_dir: Path, pattern: str) -> List[Path]:
    """
    根据模式匹配文件
    
    Args:
        data_dir: data/{flow}.{step}/ 目录
        pattern: 文件路径模式（如 "a_dir/*.def", "**/*.def", "xxx.def"）
        
    Returns:
        匹配的文件路径列表
    """
    matched_files = []
    
    if '**' in pattern:
        # 递归搜索：** 表示匹配任意深度的目录
        # 将模式拆分为前缀和后缀
        # 例如：timing/**/*.csv -> prefix='timing', suffix='*.csv'
        pattern_parts = pattern.split('**')
        if len(pattern_parts) == 2:
            prefix = pattern_parts[0].rstrip('/').rstrip(os.sep)
            suffix = pattern_parts[1].lstrip('/').lstrip(os.sep)
            
            # 如果 prefix 为空，表示从根目录开始
            # 如果 suffix 为空，表示匹配所有文件
            if prefix:
                # 有前缀：从指定目录开始递归搜索
                search_base = data_dir / prefix
                if search_base.exists():
                    for root, dirs, files in os.walk(search_base):
                        root_path = Path(root)
                        for file in files:
                            if suffix:
                                # 有后缀：检查文件是否匹配后缀模式
                                file_rel_path = root_path.relative_to(search_base) / file
                                file_rel_str = str(file_rel_path).replace(os.sep, '/')
                                if fnmatch.fnmatch(file_rel_str, suffix) or fnmatch.fnmatch(file, suffix.split('/')[-1]):
                                    matched_files.append(root_path / file)
                            else:
                                # 无后缀：匹配所有文件
                                matched_files.append(root_path / file)
            else:
                # 无前缀：从根目录递归搜索所有匹配后缀的文件
                for root, dirs, files in os.walk(data_dir):
                    root_path = Path(root)
                    for file in files:
                        if suffix:
                            file_rel_path = root_path.relative_to(data_dir) / file
                            file_rel_str = str(file_rel_path).replace(os.sep, '/')
                            if fnmatch.fnmatch(file_rel_str, suffix) or fnmatch.fnmatch(file, suffix.split('/')[-1]):
                                matched_files.append(root_path / file)
                        else:
                            matched_files.append(root_path / file)
        else:
            # 多个 **，简化处理：递归搜索所有文件
            for root, dirs, files in os.walk(data_dir):
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    rel_path = file_path.relative_to(data_dir)
                    rel_path_str = str(rel_path).replace(os.sep, '/')
                    # 尝试匹配（将 ** 替换为 *）
                    pattern_simple = pattern.replace('**', '*')
                    if fnmatch.fnmatch(rel_path_str, pattern_simple):
                        matched_files.append(file_path)
    elif '*' in pattern or '?' in pattern:
        # 通配符匹配
        pattern_parts = pattern.split('/')
        if len(pattern_parts) > 1:
            # 有目录部分
            pattern_dir = '/'.join(pattern_parts[:-1])
            pattern_file = pattern_parts[-1]
            search_dir = data_dir / pattern_dir
        else:
            # 只有文件名
            pattern_file = pattern
            search_dir = data_dir
        
        if search_dir.exists():
            for root, dirs, files in os.walk(search_dir):
                root_path = Path(root)
                for file in files:
                    if fnmatch.fnmatch(file, pattern_file):
                        matched_files.append(root_path / file)
    else:
        # 精确文件路径
        file_path = data_dir / pattern
        if file_path.exists() and file_path.is_file():
            matched_files.append(file_path)
    
    return matched_files


def filter_excluded_files(file_mappings: List[Tuple], 
                          exclude_patterns: List[str], 
                          data_dir: Path) -> List[Tuple]:
    """过滤排除的文件"""
    filtered = []
    for source_path, target_dir, keep_structure, file_type in file_mappings:
        if file_type == 'directory':
            # 目录暂时不过滤
            filtered.append((source_path, target_dir, keep_structure, file_type))
        else:
            rel_path = source_path.relative_to(data_dir)
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(str(rel_path), pattern) or \
                   fnmatch.fnmatch(source_path.name, pattern):
                    should_exclude = True
                    break
            if not should_exclude:
                filtered.append((source_path, target_dir, keep_structure, file_type))
    return filtered

