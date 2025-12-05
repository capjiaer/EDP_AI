#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl 变量输出模块
负责将 Tcl 变量写入到输出文件
"""

from tkinter import Tcl

from .tcl_expander import expand_and_format_value
from .tcl_formatter import format_tcl_value


def write_array_variables(shared_interp: Tcl, var: str, indices: list, output_file) -> None:
    """
    写入数组变量到输出文件
    
    Args:
        shared_interp: 共享的 Tcl interpreter
        var: 变量名
        indices: 数组索引列表
        output_file: 输出文件对象
    """
    for idx in sorted(indices):  # 排序以便输出更有序
        try:
            # 从共享 interpreter 获取值（可能已经展开了变量引用）
            value = shared_interp.eval(f"set {var}({idx})")
            # 展开变量引用
            value = expand_and_format_value(shared_interp, value)
            # 格式化值
            formatted_value = format_tcl_value(value)
            output_file.write(f"set {var}({idx}) {formatted_value}\n")
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，跳过该变量
            continue


def write_simple_variables(shared_interp: Tcl, var: str, has_type_info: bool, output_file) -> None:
    """
    写入简单变量到输出文件
    
    Args:
        shared_interp: 共享的 Tcl interpreter
        var: 变量名
        has_type_info: 是否有类型信息
        output_file: 输出文件对象
    """
    try:
        # 从共享 interpreter 获取值（可能已经展开了变量引用）
        value = shared_interp.eval(f"set {var}")
        # 展开变量引用
        value = expand_and_format_value(shared_interp, value)
        
        # 检查是否是列表类型（根据类型信息）
        is_list = False
        if has_type_info:
            try:
                var_type = shared_interp.eval(f"set __configkit_types__({var})")
                is_list = (var_type == "list")
            except (RuntimeError, ValueError, SyntaxError):
                # Tcl 执行错误，跳过类型检查
                pass
        
        # 格式化值
        formatted_value = format_tcl_value(value, is_list=is_list)
        output_file.write(f"set {var} {formatted_value}\n")
    except Exception:
        # 跳过该变量
        pass

