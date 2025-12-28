#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rollback Parser - 回滚解析模块

负责解析 full.tcl 文件。
"""

from pathlib import Path
from typing import Dict, Any

from edp_center.packages.edp_configkit import tclfiles2tclinterp, tclinterp2dict


def parse_full_tcl(full_tcl_path: Path) -> Dict[str, Any]:
    """
    解析 full.tcl 文件，提取所有变量
    
    Args:
        full_tcl_path: full.tcl 文件路径
        
    Returns:
        包含所有变量的字典
    """
    if not full_tcl_path.exists():
        raise FileNotFoundError(f"full.tcl 文件不存在: {full_tcl_path}")
    
    try:
        # 使用 configkit 的解析函数
        tcl_interp = tclfiles2tclinterp(str(full_tcl_path))
        config_dict = tclinterp2dict(tcl_interp, mode="auto")
        return config_dict
    except Exception as e:
        raise RuntimeError(f"解析 full.tcl 文件失败: {e}") from e

