#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl 变量展开模块
负责展开 Tcl 变量引用（如 $a -> 1）
"""

from tkinter import Tcl


def expand_single_value(interp: Tcl, value: str) -> str:
    """
    展开单个值中的变量引用（辅助函数）
    
    Args:
        interp: Tcl interpreter
        value: 要展开的值
        
    Returns:
        展开后的值
    """
    if '$' not in value:
        return value
    
    # 如果值被大括号包裹，去掉大括号再展开
    value_to_subst = value
    if value.startswith('{') and value.endswith('}') and len(value) > 2:
        value_to_subst = value[1:-1]
    
    try:
        expanded = interp.eval(f"subst {{{value_to_subst}}}")
        return expanded if expanded != value_to_subst else value
    except (RuntimeError, ValueError, SyntaxError):
        # Tcl 执行错误（如语法错误、变量不存在等），返回原值
        return value


def expand_variable_references(interp: Tcl) -> None:
    """
    对 interpreter 中包含 $ 的变量使用 subst 展开变量引用
    
    这样 b: $a 会被展开为 b: 1（如果 a=1 已经定义）
    
    Args:
        interp: Tcl interpreter
    """
    all_vars = interp.eval("info vars").split()
    for var in all_vars:
        if var.startswith("tcl_") or var.startswith("auto_") or var == "__configkit_types__":
            continue
        try:
            # 检查是否是数组
            is_array = interp.eval(f"array exists {var}")
            if is_array == "1":
                # 处理数组
                indices = interp.eval(f"array names {var}").split()
                for idx in indices:
                    try:
                        value = interp.eval(f"set {var}({idx})")
                        expanded = expand_single_value(interp, value)
                        if expanded != value:
                            interp.eval(f"set {var}({idx}) {{{expanded}}}")
                    except (RuntimeError, ValueError, SyntaxError):
                        # Tcl 执行错误，跳过该变量
                        continue
            else:
                # 处理简单变量
                value = interp.eval(f"set {var}")
                expanded = expand_single_value(interp, value)
                if expanded != value:
                    interp.eval(f"set {var} {{{expanded}}}")
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，跳过该变量
            continue


def expand_and_format_value(interp: Tcl, value: str) -> str:
    """
    展开变量引用并返回展开后的值（用于输出时的变量展开）
    
    Args:
        interp: Tcl interpreter
        value: 要展开的值
        
    Returns:
        展开后的值
    """
    if '$' in value:
        try:
            # 如果值被大括号包裹（如 {$a}），需要去掉大括号再展开
            # 否则 subst 无法展开变量
            value_to_subst = value
            if value.startswith('{') and value.endswith('}') and len(value) > 2:
                # 去掉外层大括号
                value_to_subst = value[1:-1]
            # 使用 subst 命令展开变量引用
            expanded = interp.eval(f"subst {{{value_to_subst}}}")
            # 如果展开后的值不同，说明有变量被替换了
            if expanded != value_to_subst:
                return expanded
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，如果展开失败，使用原值
            pass
    return value

