#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
类型信息输出模块
负责将类型信息写入 full.tcl 文件
"""

from typing import TextIO
from tkinter import Tcl


def write_type_info(shared_interp: Tcl, f: TextIO) -> None:
    """
    将类型信息写入 full.tcl
    
    Args:
        shared_interp: 共享的 Tcl interpreter
        f: 输出文件对象
    """
    has_type_info = shared_interp.eval("array exists __configkit_types__") == "1"
    if has_type_info:
        f.write("\n# Type information for configkit\n")
        f.write("array set __configkit_types__ {}\n")
        try:
            type_indices = shared_interp.eval("array names __configkit_types__").split()
            for idx in sorted(type_indices):  # 排序以便输出更有序
                try:
                    type_value = shared_interp.eval(f"set __configkit_types__({idx})")
                    # 正确引用索引和值
                    if ' ' in idx or any(c in idx for c in '{}[]$"\\'):
                        quoted_idx = f"{{{idx}}}"
                    else:
                        quoted_idx = idx
                    f.write(f"set __configkit_types__({quoted_idx}) {type_value}\n")
                except (RuntimeError, ValueError, SyntaxError):
                    # Tcl 执行错误，跳过该类型信息
                    continue
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，跳过类型信息写入
            pass

