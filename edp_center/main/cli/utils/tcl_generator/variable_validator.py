#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量验证模块
负责验证所有变量都是数组格式（带命名空间）
"""

import sys
from pathlib import Path
from tkinter import Tcl
from typing import List, Dict, Set


def validate_file_variables_are_arrays(temp_interp: Tcl, abs_path: Path) -> None:
    """
    验证文件定义的变量都是数组格式（带命名空间）
    
    如果发现简单变量（非数组格式），抛出 ValueError
    
    Args:
        temp_interp: 临时 interpreter，包含当前文件定义的变量
        abs_path: 配置文件绝对路径
        
    Raises:
        ValueError: 如果发现简单变量（非数组格式）
    """
    # 从临时 interpreter 获取该文件定义的所有变量
    temp_vars = temp_interp.eval("info vars").split()
    # 过滤掉系统变量
    file_vars = {v for v in temp_vars if not (v.startswith("tcl_") or v.startswith("auto_") or 
                                               v in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"])}
    
    # 使用核心验证逻辑
    simple_vars = _check_variables_are_arrays(temp_interp, file_vars)
    
    # 如果发现简单变量，抛出错误
    if simple_vars:
        error_msg = f"在文件 {abs_path} 中发现简单变量（非数组格式），不符合要求。所有变量都必须是数组格式（带命名空间）。\n"
        error_msg += "不符合要求的变量：\n"
        for var in sorted(simple_vars):
            error_msg += f"  - {var}\n"
        error_msg += "\n请将所有变量改为数组格式，例如：\n"
        error_msg += "  错误：a: 1\n"
        error_msg += "  正确：project: {a: 1}  # 生成 set project(a) 1\n"
        raise ValueError(error_msg)


def validate_all_variables_are_arrays(shared_interp: Tcl) -> None:
    """
    验证所有变量都是数组格式（带命名空间）
    
    如果发现简单变量（非数组格式），抛出 ValueError
    
    Args:
        shared_interp: 共享的 Tcl interpreter，包含所有变量
        
    Raises:
        ValueError: 如果发现简单变量（非数组格式）
    """
    # 获取所有变量
    all_vars = shared_interp.eval("info vars").split()
    
    # 过滤掉系统变量
    vars_to_check = {v for v in all_vars if not (v.startswith("tcl_") or v.startswith("auto_") or
                                                  v in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"])}
    
    # 使用核心验证逻辑
    simple_vars = _check_variables_are_arrays(shared_interp, vars_to_check)
    
    # 如果发现简单变量，抛出错误
    if simple_vars:
        error_msg = "发现简单变量（非数组格式），不符合要求。所有变量都必须是数组格式（带命名空间）。\n"
        error_msg += "不符合要求的变量：\n"
        for var in sorted(simple_vars):
            error_msg += f"  - {var}\n"
        error_msg += "\n请将所有变量改为数组格式，例如：\n"
        error_msg += "  错误：a: 1\n"
        error_msg += "  正确：project: {a: 1}  # 生成 set project(a) 1\n"
        raise ValueError(error_msg)


def _check_variables_are_arrays(interp: Tcl, vars_to_check: set) -> List[str]:
    """
    核心验证逻辑：检查变量是否是数组格式
    
    Args:
        interp: Tcl interpreter
        vars_to_check: 要检查的变量集合
        
    Returns:
        简单变量列表（非数组格式的变量）
    """
    simple_vars = []
    for var in vars_to_check:
        try:
            # 检查是否是数组
            is_array = interp.eval(f"array exists {var}")
            if is_array != "1":
                # 不是数组，记录为简单变量
                simple_vars.append(var)
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，跳过该变量
            continue
    return simple_vars

