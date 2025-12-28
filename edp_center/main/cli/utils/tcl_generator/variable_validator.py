#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量验证模块
负责验证所有变量都是数组格式（带命名空间）
"""

import sys
from pathlib import Path
from tkinter import Tcl
from typing import List, Dict, Set, Optional

from edp_center.packages.edp_common.exceptions import ValidationError, ConfigError


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
        # 构建详细的错误消息
        error_msg = f"在文件 {abs_path} 中发现简单变量（非数组格式），不符合要求。"
        
        # 构建解决建议
        suggestion_parts = [
            "所有变量都必须是数组格式（带命名空间），请按以下方式修改：",
            "",
            "YAML 格式示例：",
            "  错误：",
            "    cpu_num: 32",
            "  正确：",
            "    pnr_innovus:",
            "      place:",
            "        cpu_num: 32  # 生成 set pnr_innovus(place,cpu_num) 32",
            "",
            "Tcl 格式示例：",
            "  错误：",
            "    set cpu_num 32",
            "  正确：",
            "    set pnr_innovus(place,cpu_num) 32"
        ]
        
        raise ValidationError(
            error_msg,
            field_name="变量格式",
            field_value=f"{len(simple_vars)} 个简单变量",
            expected="数组格式（带命名空间）",
            context={
                "config_file": str(abs_path),
                "invalid_variables": sorted(simple_vars),
                "variable_count": len(simple_vars)
            },
            suggestion="\n".join(suggestion_parts)
        )


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
        # 构建详细的错误消息
        error_msg = f"发现 {len(simple_vars)} 个简单变量（非数组格式），不符合要求。"
        
        # 构建解决建议
        suggestion_parts = [
            "所有变量都必须是数组格式（带命名空间），请按以下方式修改：",
            "",
            "YAML 格式示例：",
            "  错误：",
            "    cpu_num: 32",
            "  正确：",
            "    pnr_innovus:",
            "      place:",
            "        cpu_num: 32  # 生成 set pnr_innovus(place,cpu_num) 32",
            "",
            "Tcl 格式示例：",
            "  错误：",
            "    set cpu_num 32",
            "  正确：",
            "    set pnr_innovus(place,cpu_num) 32",
            "",
            f"需要修改的变量（共 {len(simple_vars)} 个）：",
        ]
        suggestion_parts.extend([f"  - {var}" for var in sorted(simple_vars)[:10]])
        if len(simple_vars) > 10:
            suggestion_parts.append(f"  ... 还有 {len(simple_vars) - 10} 个变量")
        
        raise ValidationError(
            error_msg,
            field_name="变量格式",
            field_value=f"{len(simple_vars)} 个简单变量",
            expected="数组格式（带命名空间）",
            context={
                "invalid_variables": sorted(simple_vars),
                "variable_count": len(simple_vars)
            },
            suggestion="\n".join(suggestion_parts)
        )


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

