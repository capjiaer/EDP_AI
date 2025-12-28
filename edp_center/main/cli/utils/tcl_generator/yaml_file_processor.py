#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
YAML 文件处理模块
负责处理 YAML 配置文件
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Optional
from tkinter import Tcl
from edp_center.packages.edp_configkit import dict2tclinterp
from edp_center.packages.edp_common.error_handler import handle_error
from edp_center.packages.edp_common.exceptions import ConfigError

from .tcl_type_handler import save_type_info, restore_type_info
from .tcl_expander import expand_variable_references
from .blocks_handler import handle_blocks_replacement
from .variable_metadata_handler import process_dict_with_metadata, has_metadata_keys, _format_tcl_value, _record_type_info


def _check_for_new_format(config_dict: Dict) -> bool:
    """
    检查配置字典是否包含新的嵌套结构（value/protect/constraint/description）
    
    Args:
        config_dict: 配置字典
        
    Returns:
        如果包含新格式，返回 True；否则返回 False
    """
    def _check_dict(d: Dict) -> bool:
        if not isinstance(d, dict):
            return False
        
        # 检查是否有元数据键
        if has_metadata_keys(d):
            return True
        
        # 递归检查嵌套字典
        for value in d.values():
            if isinstance(value, dict):
                if _check_dict(value):
                    return True
        
        return False
    
    return _check_dict(config_dict)


def _copy_interp_vars(source_interp: Tcl, target_interp: Tcl) -> None:
    """
    将源 interpreter 的所有变量复制到目标 interpreter
    
    Args:
        source_interp: 源 Tcl interpreter
        target_interp: 目标 Tcl interpreter
    """
    # 获取所有变量
    all_vars = source_interp.eval("info vars").split()
    
    for var in all_vars:
        # 跳过系统变量
        if (var.startswith("tcl_") or var.startswith("auto_") or
            var in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"]):
            continue
        
        # 检查是否是数组
        is_array = source_interp.eval(f"array exists {var}")
        
        if is_array == "1":
            # 复制数组
            try:
                indices = source_interp.eval(f"array names {var}").split()
                for idx in indices:
                    value = source_interp.eval(f"set {var}({idx})")
                    # 正确引用值
                    if ' ' in value or any(c in value for c in '{}[]$"\\'):
                        target_interp.eval(f"set {var}({idx}) {{{value}}}")
                    else:
                        target_interp.eval(f"set {var}({idx}) {value}")
            except Exception:
                continue
        else:
            # 复制简单变量
            try:
                value = source_interp.eval(f"set {var}")
                # 正确引用值
                if ' ' in value or any(c in value for c in '{}[]$"\\'):
                    target_interp.eval(f"set {var} {{{value}}}")
                else:
                    target_interp.eval(f"set {var} {value}")
            except Exception:
                continue
    
    # 复制类型信息
    if source_interp.eval("array exists __configkit_types__") == "1":
        try:
            type_indices = source_interp.eval("array names __configkit_types__").split()
            for idx in type_indices:
                type_value = source_interp.eval(f"set __configkit_types__({idx})")
                target_interp.eval(f"set __configkit_types__({idx}) {type_value}")
        except Exception:
            pass


@handle_error(error_message="YAML 文件解析失败", reraise=True)
def process_yaml_file(config_file: Path, shared_interp: Tcl) -> Optional[Tcl]:
    """
    处理 YAML 配置文件
    
    Args:
        config_file: YAML 文件路径
        shared_interp: 共享的 Tcl interpreter
        
    Returns:
        临时 interpreter，包含当前文件设置的变量，如果文件为空则返回 None
        
    Raises:
        yaml.YAMLError: YAML 解析错误
    """
    abs_path = config_file.resolve()
    
    # 读取 YAML 文件
    with open(config_file, 'r', encoding='utf-8') as yf:
        try:
            config_dict = yaml.safe_load(yf) or {}
        except yaml.YAMLError as e:
            # 转换为 ConfigError，提供更多上下文信息
            error_msg = str(e)
            
            # 尝试提取行号和列号信息
            line_number = None
            column_number = None
            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                line_number = mark.line + 1  # YAML 行号从 0 开始
                column_number = mark.column + 1  # YAML 列号从 0 开始
            
            # 构建详细的解决建议
            suggestion_parts = [
                "请检查 YAML 文件格式是否正确：",
                ""
            ]
            
            if line_number:
                suggestion_parts.append(f"错误位置：第 {line_number} 行")
                if column_number:
                    suggestion_parts.append(f"          第 {column_number} 列")
                suggestion_parts.append("")
            
            suggestion_parts.extend([
                "常见问题：",
                "1. 缩进错误：",
                "   - YAML 使用空格缩进，不要使用 Tab",
                "   - 确保缩进一致（通常使用 2 个空格）",
                "",
                "2. 引号问题：",
                "   - 确保所有引号（单引号 ' 或双引号 \"）都已正确闭合",
                "   - 如果字符串包含特殊字符，需要用引号括起来",
                "",
                "3. 列表和字典格式：",
                "   - 列表使用 - 开头",
                "   - 字典使用 key: value 格式",
                "   - 确保冒号后面有空格",
                "",
                "4. 特殊字符：",
                "   - 如果值包含冒号、引号等特殊字符，需要用引号括起来",
                "   - 检查是否有未转义的特殊字符"
            ])
            
            context = {
                "config_file": str(abs_path),
                "error_type": type(e).__name__,
                "error_message": error_msg
            }
            if line_number:
                context["line_number"] = line_number
            if column_number:
                context["column_number"] = column_number
            
            raise ConfigError(
                f"YAML 文件解析失败: {error_msg}",
                config_file=str(abs_path),
                context=context,
                suggestion="\n".join(suggestion_parts)
            ) from e
    
    if not config_dict:
        return None
    
    # 检查是否有列表中的字典（Tcl 8.5 之前不支持，给出警告）
    warned_vars = set()
    for key, value in config_dict.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if key not in warned_vars:
                        print(f"[WARN] 在文件 {abs_path} 中检测到列表 '{key}' 包含字典元素", file=sys.stderr)
                        print(f"[WARN] 这种结构在 Tcl 8.5 之前的版本中不支持，建议避免使用", file=sys.stderr)
                        warned_vars.add(key)
                    break
    
    # 保存当前的类型信息
    type_info_before = save_type_info(shared_interp)
    
    # 检查是否包含新的嵌套结构（value/protect/constraint/description）
    has_new_format = _check_for_new_format(config_dict)
    
    if has_new_format:
        # 新格式：使用新的处理函数
        temp_interp = Tcl()
        temp_interp.eval("array set __configkit_types__ {}")
        
        # 处理新的嵌套结构
        for key, value in config_dict.items():
            if isinstance(value, dict):
                process_dict_with_metadata(value, temp_interp, key)
            else:
                # 简单变量，直接设置
                tcl_value = _format_tcl_value(value)
                temp_interp.eval(f"set {key} {tcl_value}")
                _record_type_info(temp_interp, key, value)
        
        # 对于 blocks，如果后面的文件也定义了，应该替换而不是追加
        if 'blocks' in config_dict:
            handle_blocks_replacement(shared_interp, config_dict, type_info_before)
        else:
            # 将临时 interpreter 的变量复制到共享 interpreter
            _copy_interp_vars(temp_interp, shared_interp)
            # 恢复类型信息
            restore_type_info(shared_interp, type_info_before)
            
            # 对包含 $ 的变量使用 subst 展开变量引用
            expand_variable_references(shared_interp)
    else:
        # 旧格式：使用旧的 dict2tclinterp（用于非嵌套结构的简单 YAML）
        temp_interp = dict2tclinterp(config_dict)
        
        # 对于 blocks，如果后面的文件也定义了，应该替换而不是追加
        if 'blocks' in config_dict:
            handle_blocks_replacement(shared_interp, config_dict, type_info_before)
        else:
            # 正常转换（使用共享的 interpreter，可以引用前面定义的变量）
            dict2tclinterp(config_dict, interp=shared_interp)
            # 恢复类型信息（因为 dict2tclinterp 会重新初始化）
            restore_type_info(shared_interp, type_info_before)
            
            # 对包含 $ 的变量使用 subst 展开变量引用
            expand_variable_references(shared_interp)
    
    return temp_interp

