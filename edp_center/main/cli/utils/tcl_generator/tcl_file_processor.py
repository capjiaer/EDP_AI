#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl 文件处理模块
负责处理 Tcl 配置文件
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set
from tkinter import Tcl
from edp_center.packages.edp_configkit.configkit.configkit import tclinterp2dict

from .tcl_type_handler import save_type_info, restore_type_info
from .tcl_expander import expand_variable_references
from .blocks_handler import handle_blocks_replacement


def process_tcl_file(config_file: Path, shared_interp: Tcl) -> Tcl:
    """
    处理 Tcl 配置文件
    
    Args:
        config_file: Tcl 文件路径
        shared_interp: 共享的 Tcl interpreter
        
    Returns:
        临时 interpreter，包含当前文件设置的变量
        
    Raises:
        RuntimeError, ValueError, SyntaxError: Tcl 执行错误
    """
    abs_path = config_file.resolve()
    
    # 读取 Tcl 文件内容
    with open(config_file, 'r', encoding='utf-8') as tf:
        tcl_content = tf.read()
    
    # 解析 Tcl 文件，找出所有 set 命令设置的变量
    set_pattern = r'set\s+(\w+)(?:\(([^)]+)\))?'
    set_matches = re.findall(set_pattern, tcl_content)
    
    # 提取所有设置的变量名（包括数组）
    tcl_file_vars = set()
    for match in set_matches:
        var_name = match[0]
        tcl_file_vars.add(var_name)
    
    # 在共享的 interpreter 中执行 Tcl 文件（这样它可以访问之前定义的变量）
    try:
        shared_interp.eval(tcl_content)
    except (RuntimeError, ValueError, SyntaxError) as e:
        print(f"[ERROR] Tcl 文件解析失败: {abs_path}", file=sys.stderr)
        print(f"[ERROR] 错误信息: {e}", file=sys.stderr)
        print(f"[ERROR] 请检查 Tcl 文件格式是否正确", file=sys.stderr)
        raise
    
    # 创建一个临时的 interpreter，只包含当前文件设置的变量
    temp_tcl_interp = Tcl()
    temp_tcl_interp.eval("array set __configkit_types__ {}")
    
    for var in tcl_file_vars:
        try:
            # 检查是否是数组
            is_array = shared_interp.eval(f"array exists {var}")
            if is_array == "1":
                # 复制数组
                indices = shared_interp.eval(f"array names {var}").split()
                for idx in indices:
                    value = shared_interp.eval(f"set {var}({idx})")
                    temp_tcl_interp.eval(f"set {var}({idx}) {{{value}}}")
            else:
                # 复制简单变量
                value = shared_interp.eval(f"set {var}")
                temp_tcl_interp.eval(f"set {var} {{{value}}}")
        except (RuntimeError, ValueError, SyntaxError):
            continue
    
    # 将临时 interpreter 转换为字典（用于后续处理）
    config_dict = tclinterp2dict(temp_tcl_interp) or {}
    
    # 保存当前的类型信息
    type_info_before = save_type_info(shared_interp)
    
    # 对于 blocks，如果后面的文件也定义了，应该替换而不是追加
    if 'blocks' in config_dict:
        handle_blocks_replacement(shared_interp, config_dict, type_info_before)
    else:
        # 恢复类型信息
        restore_type_info(shared_interp, type_info_before)
    
    # 对共享 interpreter 中的变量使用 subst 展开变量引用
    expand_variable_references(shared_interp)
    
    return temp_tcl_interp

