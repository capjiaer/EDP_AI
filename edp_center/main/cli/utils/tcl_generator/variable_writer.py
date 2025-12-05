#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量输出模块
负责将变量写入 full.tcl 文件
"""

from pathlib import Path
from typing import TextIO, Set
from tkinter import Tcl

from .tcl_writer import write_array_variables, write_simple_variables


def write_file_variables(shared_interp: Tcl, temp_interp: Tcl, abs_path: Path, f: TextIO) -> None:
    """
    将文件定义的变量写入 full.tcl
    
    Args:
        shared_interp: 共享的 Tcl interpreter，包含所有变量
        temp_interp: 临时 interpreter，包含当前文件定义的变量
        abs_path: 配置文件绝对路径
        f: 输出文件对象
    """
    f.write(f"\n# From {abs_path}\n")
    
    # 从临时 interpreter 获取该文件定义的所有变量
    temp_vars = temp_interp.eval("info vars").split()
    # 过滤掉系统变量
    file_vars = {v for v in temp_vars if not (v.startswith("tcl_") or v.startswith("auto_") or 
                                               v in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"])}
    
    # 检查是否有类型信息
    has_type_info = shared_interp.eval("array exists __configkit_types__") == "1"
    
    # 处理该文件的变量（从共享 interpreter 获取值，这样可以引用前面定义的变量）
    for var in sorted(file_vars):  # 排序以便输出更有序
        # 检查是否是数组
        is_array = shared_interp.eval(f"array exists {var}")
        
        if is_array == "1":
            # 获取所有数组索引
            try:
                indices = shared_interp.eval(f"array names {var}").split()
                write_array_variables(shared_interp, var, indices, f)
            except (RuntimeError, ValueError, SyntaxError):
                # Tcl 执行错误，跳过该变量
                continue
        else:
            # 简单变量
            write_simple_variables(shared_interp, var, has_type_info, f)

