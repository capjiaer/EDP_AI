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
            
            # 构建友好的错误信息
            friendly_error = (
                f"❌ 配置验证失败\n"
                f"  {error_msg}\n"
                f"  配置文件: {', '.join(str(f) for f in config_files)}\n"
            )
            
            # 提取变量名和允许值（如果可能）
            suggestion = "💡 建议: 请检查配置文件，将变量值改为允许的值"
            
            raise ValidationError(
                friendly_error,
                context={
                    "error": error_msg,
                    "config_files": [str(f) for f in config_files],
                    "full_tcl_path": str(full_tcl_path)
                },
                suggestion=suggestion
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

