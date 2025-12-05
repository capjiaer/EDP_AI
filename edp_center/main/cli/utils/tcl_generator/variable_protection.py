#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量保护代码生成器
负责根据 constraint、protect、description 数组自动生成保护代码
"""

import sys
import re
from tkinter import Tcl
from typing import TextIO


def generate_variable_protection_code(shared_interp: Tcl, f: TextIO) -> None:
    """
    根据新的嵌套结构生成变量保护代码
    
    新格式：变量名后缀（*_protect, *_constraint, *_description）
    - var_name(protect) 1/0 -> edp_protect_var var_name <current_value>（protect 为 1 时）
    - var_name(constraint) "value1 value2" -> edp_constraint_var var_name "value1 value2"
    - var_name(description) "description" -> edp_descript_var var_name "description"
    
    注意：protect 只能是布尔值（1/0），表示是否启用保护。如果为 1，保护值为变量的当前值。
    
    Args:
        shared_interp: 共享的 Tcl interpreter，包含所有变量
        f: 输出文件对象
    """
    try:
        # 检查是否存在新格式（扫描所有变量，查找 *_protect, *_constraint, *_description 后缀）
        new_format_vars = _scan_for_new_format(shared_interp)
        
        if not new_format_vars:
            # 没有新格式变量，直接返回
            return
        
        # 生成保护代码
        f.write("\n# Variable protection and constraints\n")
        f.write("# Generated automatically from new nested format\n")
        
        # 处理新格式（*_protect, *_constraint, *_description 后缀）
        if new_format_vars:
            for var_name, metadata in sorted(new_format_vars.items()):
                try:
                    # 处理 protect（布尔标志：1/0 表示是否启用保护）
                    if 'protect' in metadata:
                        protect_flag = metadata['protect']
                        
                        # 检查 protect 是否是布尔标志（1, true, "1", "true"）
                        # protect 只能是布尔值，表示是否启用保护
                        is_protected = (
                            protect_flag in (1, True, "1", "true", "True", "TRUE") or
                            (isinstance(protect_flag, str) and protect_flag.lower() == "true")
                        )
                        
                        if is_protected:
                            # 启用保护：使用变量的当前值作为保护值
                            # 注意：此时所有配置文件已经处理完成，变量的值已经是最终值
                            try:
                                # var_name 格式可能是：
                                # - 简单变量：var_name
                                # - 数组变量：var_name(parent_keys)
                                # 直接使用 var_name 获取值即可（Tcl 会自动处理）
                                current_value = shared_interp.eval(f"set {var_name}")
                                quoted_var_name = _quote_var_name(var_name)
                                quoted_value = _quote_value(current_value)
                                f.write(f"edp_protect_var {quoted_var_name} {quoted_value}\n")
                            except Exception as e:
                                # 如果无法获取当前值，跳过保护（不应该发生）
                                # 输出警告以便调试
                                print(f"[WARN] 无法获取变量 {var_name} 的当前值用于保护: {e}", file=sys.stderr)
                                continue
                        # 如果 protect 为 0/false，不生成保护代码（不保护）
                    
                    # 处理 constraint
                    if 'constraint' in metadata:
                        constraint_value = metadata['constraint']
                        quoted_var_name = _quote_var_name(var_name)
                        quoted_value = _quote_value(constraint_value)
                        f.write(f"edp_constraint_var {quoted_var_name} {quoted_value}\n")
                    
                    # 处理 description
                    if 'description' in metadata:
                        description_value = metadata['description']
                        quoted_var_name = _quote_var_name(var_name)
                        quoted_value = _quote_value(description_value)
                        f.write(f"edp_descript_var {quoted_var_name} {quoted_value}\n")
                except (RuntimeError, ValueError, SyntaxError) as e:
                    # Tcl 执行错误，跳过该变量
                    continue
        
    except Exception as e:
        # 发生错误时，不中断整个流程，只输出警告
        import traceback
        print(f"[WARN] 生成变量保护代码时发生错误: {e}", file=sys.stderr)
        traceback.print_exc()


def _scan_for_new_format(shared_interp: Tcl) -> dict:
    """
    扫描所有变量，查找新格式（*_protect, *_constraint, *_description 后缀）
    
    Args:
        shared_interp: Tcl interpreter
        
    Returns:
        字典，键为变量名，值为包含 protect/constraint/description 的字典
    """
    result = {}
    
    try:
        # 获取所有变量
        all_vars = shared_interp.eval("info vars").split()
        
        # 过滤掉系统变量
        vars_to_check = [v for v in all_vars if not (v.startswith("tcl_") or v.startswith("auto_") or
                                                     v in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"])]
        
        # 检查每个变量是否是数组
        for var in vars_to_check:
            try:
                is_array = shared_interp.eval(f"array exists {var}")
                if is_array == "1":
                    # 获取所有数组索引
                    indices = shared_interp.eval(f"array names {var}").split()
                    
                    # 检查是否有 protect/constraint/description 后缀
                    # 新格式：var_name(parent_keys,protect) 或 var_name(parent_keys,constraint) 或 var_name(parent_keys,description)
                    # 需要从索引中提取变量名
                    for idx in indices:
                        # 检查索引是否以 protect/constraint/description 结尾
                        # 格式：parent_keys,protect 或 parent_keys,constraint 或 parent_keys,description
                        for metadata_type in ['protect', 'constraint', 'description']:
                            var_name_with_idx, value = _extract_metadata_from_index(
                                var, idx, metadata_type, shared_interp
                            )
                            if var_name_with_idx:
                                if var_name_with_idx not in result:
                                    result[var_name_with_idx] = {}
                                result[var_name_with_idx][metadata_type] = value
            except Exception:
                continue
    except Exception:
        pass
    
    return result


def _extract_metadata_from_index(var: str, idx: str, metadata_type: str, 
                                  shared_interp: Tcl) -> tuple:
    """
    从索引中提取变量名和元数据值
    
    Args:
        var: 变量名（数组名）
        idx: 数组索引
        metadata_type: 元数据类型（'protect'、'constraint'、'description'）
        shared_interp: Tcl interpreter
        
    Returns:
        (var_name_with_idx, value) 元组，如果索引不匹配则返回 (None, None)
    """
    suffix = f",{metadata_type}"
    
    if idx == metadata_type:
        # 简单变量：var(protect)
        var_name_with_idx = var
    elif idx.endswith(suffix):
        # 复杂变量：var(parent_keys,protect) -> var(parent_keys)
        base_idx = idx[:-len(suffix)]
        var_name_with_idx = f"{var}({base_idx})"
    else:
        return None, None
    
    try:
        value = shared_interp.eval(f"set {var}({idx})")
        return var_name_with_idx, value
    except (RuntimeError, ValueError, SyntaxError):
        return None, None


def _quote_var_name(var_name: str) -> str:
    """
    引用变量名，如果包含特殊字符，用大括号包裹
    
    Args:
        var_name: 变量名
        
    Returns:
        引用后的变量名
    """
    if ' ' in var_name or '(' in var_name or ',' in var_name or any(c in var_name for c in '{}[]$"\\'):
        return f"{{{var_name}}}"
    else:
        return var_name


def _quote_value(value: str) -> str:
    """
    引用值，如果包含特殊字符，用大括号包裹
    
    Args:
        value: 值
        
    Returns:
        引用后的值
    """
    if ' ' in value or any(c in value for c in '{}[]$"\\'):
        return f"{{{value}}}"
    else:
        return value

