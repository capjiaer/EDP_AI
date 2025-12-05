#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl 类型信息处理模块
负责保存和恢复 Tcl 类型信息
"""

from typing import Dict
from tkinter import Tcl


def save_type_info(interp: Tcl) -> Dict[str, str]:
    """
    保存当前的类型信息（因为 dict2tclinterp 会重新初始化）
    
    Args:
        interp: Tcl interpreter
        
    Returns:
        类型信息字典
    """
    type_info = {}
    try:
        if interp.eval("array exists __configkit_types__") == "1":
            type_indices = interp.eval("array names __configkit_types__").split()
            for idx in type_indices:
                try:
                    type_value = interp.eval(f"set __configkit_types__({idx})")
                    type_info[idx] = type_value
                except (RuntimeError, ValueError, SyntaxError):
                    # Tcl 执行错误，跳过该类型信息
                    pass
    except (RuntimeError, ValueError, SyntaxError):
        # Tcl 执行错误，跳过类型信息获取
        pass
    return type_info


def restore_type_info(interp: Tcl, type_info: Dict[str, str]) -> None:
    """
    恢复类型信息（因为 dict2tclinterp 会重新初始化）
    
    Args:
        interp: Tcl interpreter
        type_info: 类型信息字典
    """
    for idx, type_value in type_info.items():
        try:
            interp.eval(f"set __configkit_types__({idx}) {type_value}")
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，跳过该类型信息恢复
            pass

