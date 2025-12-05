#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Util Proc 检测模块
检测 util 文件是否是 proc 形式，并提取 proc 名称
"""

import re
from pathlib import Path
from typing import Optional, Tuple


def detect_util_proc(util_file: Path) -> Optional[str]:
    """
    检测 util 文件是否是 proc 形式，并返回主 proc 名称
    
    规则：
    1. 如果文件包含 `proc {util_name} {}`，返回该 proc 名称
    2. 如果文件包含 `proc {util_name_with_underscore} {}`，返回该 proc 名称
    3. 否则返回 None（表示不是 proc 形式）
    
    Args:
        util_file: util 文件路径
        
    Returns:
        主 proc 名称，如果不是 proc 形式返回 None
    """
    if not util_file.exists():
        return None
    
    try:
        content = util_file.read_text(encoding='utf-8')
    except Exception:
        return None
    
    # 提取 util 名称（去掉扩展名）
    util_name = util_file.stem
    
    # 模式1：proc {util_name} {}
    pattern1 = rf'^\s*proc\s+{re.escape(util_name)}\s*\{{'
    if re.search(pattern1, content, re.MULTILINE):
        return util_name
    
    # 模式2：proc {util_name_with_underscore} {}（如 helper_get_timing）
    # 这里我们只检查是否有以 util_name 开头的 proc
    pattern2 = rf'^\s*proc\s+{re.escape(util_name)}[_\w]*\s*\{{'
    match = re.search(pattern2, content, re.MULTILINE)
    if match:
        # 提取完整的 proc 名称
        proc_match = re.search(rf'^\s*proc\s+({re.escape(util_name)}[_\w]*)\s*\{{', content, re.MULTILINE)
        if proc_match:
            return proc_match.group(1)
    
    return None


def get_util_proc_name(util_file: Path, util_name: Optional[str] = None) -> Optional[str]:
    """
    获取 util 文件的主 proc 名称
    
    Args:
        util_file: util 文件路径
        util_name: util 名称（如果为 None，从文件名提取）
        
    Returns:
        主 proc 名称，如果不是 proc 形式返回 None
    """
    if util_name is None:
        util_name = util_file.stem
    
    return detect_util_proc(util_file)

