#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl 值格式化模块
负责格式化 Tcl 值，确保是有效的 Tcl 语法
"""


def format_tcl_value(value: str, is_list: bool = False) -> str:
    """
    格式化 Tcl 值，确保是有效的 Tcl 语法
    
    Args:
        value: 要格式化的值
        is_list: 是否是列表类型
        
    Returns:
        格式化后的值（用于 set 命令）
    """
    # Handle empty string specially - use braces to ensure it's set correctly
    if value == "":
        return "{}"
    
    if is_list:
        # 对于列表，需要用大括号包裹整个值，否则 Tcl 会认为这是多个参数
        # configkit 返回的 value 可能是：
        # 1. {elem1 elem2 ...} 格式（已经有大括号）
        # 2. elem1 elem2 ... 格式（没有大括号）
        # 无论哪种情况，我们都需要外面再加大括号，确保是 {{elem1 elem2 ...}} 格式
        return f"{{{value}}}"
    else:
        # 对于其他类型，正确引用值以确保是有效的 Tcl
        if ' ' in value or any(c in value for c in '{}[]$"\\'):
            return f"{{{value}}}"
        else:
            return value

