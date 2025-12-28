#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constraint 验证器
通过在临时 Tcl interpreter 中执行 full.tcl 来验证 constraint
"""

import sys
import logging
from pathlib import Path
from tkinter import Tcl

from edp_center.packages.edp_common import ValidationError

# 获取 logger
logger = logging.getLogger(__name__)


def validate_full_tcl_constraints(full_tcl_path: Path, config_files: list, edp_center_path: Path) -> None:
    """
    通过在临时 Tcl interpreter 中执行 full.tcl 来验证 constraint
    
    核心思路：
    1. 在临时 interpreter 中执行 full.tcl（只执行到 edp_constraint_var 部分）
    2. edp_constraint_var 在设置 constraint 时会立即验证当前值
    3. 如果值不在允许列表中，edp_constraint_var 会直接 error 退出
    4. 捕获错误，提供友好的错误信息
    
    Args:
        full_tcl_path: full.tcl 文件路径
        config_files: 配置文件路径列表（用于错误信息）
        edp_center_path: edp_center 路径（用于查找 edp_dealwith_var.tcl）
        
    Raises:
        ValidationError: 如果发现值不在允许列表中
    """
    # 读取 full.tcl 内容
    with open(full_tcl_path, 'r', encoding='utf-8') as f:
        full_tcl_content = f.read()
    
    # 创建临时 Tcl interpreter
    temp_interp = Tcl()
    
    # 需要先 source edp_dealwith_var.tcl（包含 edp_constraint_var 的定义）
    # edp_dealwith_var.tcl 在 flow/common/packages/tcl/default/ 目录下
    edp_dealwith_var_path = edp_center_path / "flow" / "common" / "packages" / "tcl" / "default" / "edp_dealwith_var.tcl"
    if not edp_dealwith_var_path.exists():
        raise FileNotFoundError(
            f"找不到 edp_dealwith_var.tcl: {edp_dealwith_var_path}，无法进行 constraint 验证"
        )
    
    # 先 source edp_dealwith_var.tcl
    with open(edp_dealwith_var_path, 'r', encoding='utf-8') as f:
        edp_dealwith_var_content = f.read()
    temp_interp.eval(edp_dealwith_var_content)
    
    try:
        # 执行 full.tcl（会在 edp_constraint_var 处验证）
        temp_interp.eval(full_tcl_content)
    except RuntimeError as e:
        # Tcl 执行错误，可能是 edp_constraint_var 报错
        error_msg = str(e)
        
        # 检查是否是 constraint 验证错误
        if "is not in constraint list" in error_msg or "Allowed values are" in error_msg:
            # 解析错误信息
            # 格式：ERROR: Value '64' of variable 'pv_calibre(ipmerge,cpu_num)' is not in constraint list. Allowed values are: 1 2 4 8 16 32
            
            # 尝试提取变量名和允许值
            variable_name = None
            current_value = None
            allowed_values = None
            
            # 解析错误消息
            if "variable '" in error_msg and "' is not in constraint list" in error_msg:
                # 提取变量名
                start = error_msg.find("variable '") + len("variable '")
                end = error_msg.find("' is not in constraint list")
                if start > len("variable '") - 1 and end > start:
                    variable_name = error_msg[start:end]
            
            if "Value '" in error_msg:
                # 提取当前值
                start = error_msg.find("Value '") + len("Value '")
                end = error_msg.find("' of variable")
                if start > len("Value '") - 1 and end > start:
                    current_value = error_msg[start:end]
            
            if "Allowed values are:" in error_msg:
                # 提取允许值
                start = error_msg.find("Allowed values are:") + len("Allowed values are:")
                allowed_values_str = error_msg[start:].strip()
                allowed_values = allowed_values_str.split()
            
            # 构建友好的错误信息
            friendly_error = f"配置验证失败：变量值不在允许的约束列表中"
            
            # 构建详细的解决建议
            suggestion_parts = [
                "请检查配置文件，将变量值改为允许的值：",
                ""
            ]
            
            if variable_name:
                suggestion_parts.append(f"变量名: {variable_name}")
            if current_value:
                suggestion_parts.append(f"当前值: {current_value}")
            if allowed_values:
                suggestion_parts.append(f"允许的值: {', '.join(allowed_values)}")
                suggestion_parts.append("")
                suggestion_parts.append("修改示例：")
                if variable_name and current_value:
                    # 尝试解析变量名（格式：flow_name(step_name,var_name)）
                    if '(' in variable_name and ')' in variable_name:
                        var_parts = variable_name.split('(')
                        flow_step = var_parts[0]
                        var_name = var_parts[1].rstrip(')')
                        suggestion_parts.append(f"  在配置文件中找到 {flow_step} -> {var_name}，将值改为允许的值之一")
            
            suggestion_parts.append("")
            suggestion_parts.append("相关配置文件：")
            for config_file in config_files[:5]:  # 最多显示5个文件
                suggestion_parts.append(f"  - {config_file}")
            if len(config_files) > 5:
                suggestion_parts.append(f"  ... 还有 {len(config_files) - 5} 个配置文件")
            
            raise ValidationError(
                friendly_error,
                field_name=variable_name or "配置变量",
                field_value=current_value,
                expected=f"允许的值: {', '.join(allowed_values) if allowed_values else '未知'}",
                context={
                    "error": error_msg,
                    "variable_name": variable_name,
                    "current_value": current_value,
                    "allowed_values": allowed_values,
                    "config_files": [str(f) for f in config_files],
                    "full_tcl_path": str(full_tcl_path)
                },
                suggestion="\n".join(suggestion_parts)
            )
        else:
            # 其他 Tcl 错误，可能是 full.tcl 本身的语法错误
            # 这种情况下，我们不应该抛出 ValidationError，而是让调用者知道是其他错误
            # 但为了不中断流程，我们可以输出警告
            print(f"[WARN] 执行 full.tcl 时发生错误（可能是语法错误）: {error_msg}", file=sys.stderr)
            print(f"[WARN] 跳过 constraint 验证，继续执行", file=sys.stderr)
            logger.warning(f"执行 full.tcl 时发生错误（可能是语法错误）: {error_msg}，跳过 constraint 验证", exc_info=True)
            return
    
    # 验证通过，没有错误

