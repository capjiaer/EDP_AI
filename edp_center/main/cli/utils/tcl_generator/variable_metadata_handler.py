#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量元数据处理模块
负责处理新的嵌套结构（value/protect/constraint/description）
"""

from typing import Dict, Any, List, Tuple
from tkinter import Tcl


# 特殊键名，用于变量元数据
METADATA_KEYS = {'value', 'protect', 'constraint', 'description'}


def process_dict_with_metadata(data: Dict, interp: Tcl, var_name: str = None, parent_keys: List[str] = None) -> None:
    """
    递归处理字典，支持新的嵌套结构（value/protect/constraint/description）
    
    如果遇到包含 value/protect/constraint/description 的字典，按照新格式处理：
    - value → set var_name value
    - protect → set var_name(protect) value
    - constraint → set var_name(constraint) "value1 value2"
    - description → set var_name(description) "..."
    
    否则，按照旧方式处理（递归处理嵌套字典）
    
    Args:
        data: 要处理的字典
        interp: Tcl interpreter
        var_name: 变量名（根级别）
        parent_keys: 父级键列表（用于构建完整的变量名）
    """
    if parent_keys is None:
        parent_keys = []
    
    for key, value in data.items():
        # 跳过特殊标记
        if key == '__metadata__':
            continue
        
        new_keys = parent_keys + [key]
        
        if isinstance(value, dict):
            # 检查是否包含元数据键
            if has_metadata_keys(value):
                # 新格式：包含 value/protect/constraint/description
                # 构建完整的变量名：var_name(parent_keys, key)
                if var_name is None:
                    # 根级别，使用 key 作为变量名
                    process_variable_metadata(value, interp, key, [])
                else:
                    # 嵌套结构，使用 var_name 和 new_keys 构建变量名
                    # 例如：pv_calibre(ipmerge,cpu_num) 中的 cpu_num
                    # var_name = pv_calibre, parent_keys = [ipmerge], key = cpu_num
                    # new_keys = [ipmerge, cpu_num]
                    # 最终变量名应该是 pv_calibre(ipmerge,cpu_num)
                    process_variable_metadata(value, interp, var_name, new_keys)
            else:
                # 旧格式：递归处理嵌套字典
                if var_name is None:
                    # 根级别，使用 key 作为新的变量名
                    process_dict_with_metadata(value, interp, key, [])
                else:
                    # 嵌套结构，继续使用 var_name
                    process_dict_with_metadata(value, interp, var_name, new_keys)
        else:
            # 普通值，按照旧方式处理
            if var_name is None:
                # 根级别变量
                tcl_value = _format_tcl_value(value)
                interp.eval(f"set {key} {tcl_value}")
                _record_type_info(interp, key, value)
            else:
                # 数组变量
                array_indices = ','.join(new_keys)
                tcl_value = _format_tcl_value(value)
                interp.eval(f"set {var_name}({array_indices}) {tcl_value}")
                type_key = f"{var_name}({array_indices})"
                _record_type_info(interp, type_key, value)


def process_variable_metadata(data: Dict, interp: Tcl, var_name: str, parent_keys: List[str] = None) -> None:
    """
    处理包含元数据的变量（新格式）
    
    如果遇到包含 value/protect/constraint/description 的字典，按照新格式处理：
    - value → set var_name value
    - protect → set var_name(protect) value
    - constraint → set var_name(constraint) "value1 value2"
    - description → set var_name(description) "..."
    
    Args:
        data: 包含元数据的字典
        interp: Tcl interpreter
        var_name: 变量名
        parent_keys: 父级键列表（用于构建完整的变量名）
    """
    if parent_keys is None:
        parent_keys = []
    
    # 构建完整的变量名（用于 value）
    if parent_keys:
        full_var_name = f"{var_name}({','.join(parent_keys)})"
    else:
        full_var_name = var_name
    
    # 处理 value（必需）
    if 'value' in data:
        value = data['value']
        tcl_value = _format_tcl_value(value)
        interp.eval(f"set {full_var_name} {tcl_value}")
        
        # 记录类型信息
        _record_type_info(interp, full_var_name, value)
    
    # 处理元数据键（protect/constraint/description）
    for metadata_key in ['protect', 'constraint', 'description']:
        if metadata_key in data:
            _process_metadata_key(data, interp, var_name, parent_keys, metadata_key)


def _process_metadata_key(data: Dict, interp: Tcl, var_name: str, 
                          parent_keys: List[str], key: str) -> None:
    """
    处理单个元数据键（protect/constraint/description）
    
    Args:
        data: 包含元数据的字典
        interp: Tcl interpreter
        var_name: 变量名
        parent_keys: 父级键列表（用于构建完整的变量名）
        key: 元数据键名（'protect'、'constraint'、'description'）
    """
    value = data[key]
    tcl_value = _format_tcl_value(value)
    
    # 构建元数据变量名：var_name(parent_keys,key)
    if parent_keys:
        metadata_var_name = f"{var_name}({','.join(parent_keys)},{key})"
    else:
        metadata_var_name = f"{var_name}({key})"
    
    interp.eval(f"set {metadata_var_name} {tcl_value}")
    _record_type_info(interp, metadata_var_name, value)


def has_metadata_keys(data: Dict) -> bool:
    """
    检查字典是否包含元数据键（value/protect/constraint/description）
    
    Args:
        data: 要检查的字典
        
    Returns:
        如果包含元数据键，返回 True；否则返回 False
    """
    if not isinstance(data, dict):
        return False
    
    # 检查是否有任何元数据键
    return bool(METADATA_KEYS.intersection(data.keys()))


def _format_tcl_value(value: Any) -> str:
    """
    格式化 Python 值为 Tcl 值
    
    Args:
        value: Python 值
        
    Returns:
        Tcl 格式的值字符串
    """
    if value is None:
        return "{}"
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        # 列表转换为空格分隔的字符串，并用大括号包裹
        list_str = " ".join(str(v) for v in value)
        return f"{{{list_str}}}"
    else:
        # 字符串，需要检查是否需要引号
        value_str = str(value)
        if ' ' in value_str or any(c in value_str for c in '{}[]$"\\'):
            return f"{{{value_str}}}"
        else:
            return value_str


def _record_type_info(interp: Tcl, var_name: str, value: Any) -> None:
    """
    记录变量的类型信息
    
    Args:
        interp: Tcl interpreter
        var_name: 变量名
        value: 变量值
    """
    if isinstance(value, list):
        interp.eval(f"set __configkit_types__({var_name}) list")
    elif isinstance(value, bool):
        interp.eval(f"set __configkit_types__({var_name}) bool")
    elif value is None:
        interp.eval(f"set __configkit_types__({var_name}) none")
    elif isinstance(value, (int, float)):
        interp.eval(f"set __configkit_types__({var_name}) number")
    else:
        interp.eval(f"set __configkit_types__({var_name}) string")


def preprocess_dict_for_metadata(data: Dict) -> Dict:
    """
    预处理字典，处理包含元数据的嵌套结构
    
    递归遍历字典，如果遇到包含 value/protect/constraint/description 的字典，
    将其标记为需要特殊处理。
    
    Args:
        data: 要预处理的字典
        
    Returns:
        处理后的字典（可能包含标记）
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            # 检查是否包含元数据键
            if has_metadata_keys(value):
                # 标记为需要特殊处理
                result[key] = {'__metadata__': True, **value}
            else:
                # 递归处理嵌套字典
                result[key] = preprocess_dict_for_metadata(value)
        else:
            result[key] = value
    
    return result

