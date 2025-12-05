#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blocks 处理模块
负责处理 blocks 替换逻辑（替换而不是追加）
"""

from typing import Dict
from tkinter import Tcl
from edp_center.packages.edp_configkit.configkit.configkit import dict2tclinterp

from .tcl_type_handler import restore_type_info
from .tcl_expander import expand_variable_references


def handle_blocks_replacement(shared_interp: Tcl, config_dict: Dict, type_info_before: Dict[str, str]) -> None:
    """
    处理 blocks 替换逻辑（替换而不是追加）
    
    Args:
        shared_interp: 共享的 Tcl interpreter
        config_dict: 配置字典
        type_info_before: 之前的类型信息
    """
    # 如果 blocks 已经存在，先删除旧的 blocks 变量
    if 'blocks' in shared_interp.eval("info vars"):
        try:
            # 检查 blocks 是否是数组
            if shared_interp.eval("array exists blocks") == "1":
                # 删除所有数组元素
                indices = shared_interp.eval("array names blocks").split()
                for idx in indices:
                    shared_interp.eval(f"unset blocks({idx})")
                    # 同时删除类型信息
                    try:
                        shared_interp.eval(f"unset __configkit_types__(blocks,{idx})")
                    except (RuntimeError, ValueError, SyntaxError):
                        # Tcl 执行错误，跳过该类型信息删除
                        pass
            else:
                # 删除简单变量
                shared_interp.eval("unset blocks")
                # 同时删除类型信息
                try:
                    shared_interp.eval("unset __configkit_types__(blocks)")
                except (RuntimeError, ValueError, SyntaxError):
                    # Tcl 执行错误，跳过该类型信息删除
                    pass
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl 执行错误，跳过 blocks 删除
            pass
    
    # 移除 blocks 后合并其他配置
    blocks_value = config_dict.pop('blocks')
    # 先转换其他配置
    dict2tclinterp(config_dict, interp=shared_interp)
    # 恢复类型信息（因为 dict2tclinterp 会重新初始化）
    restore_type_info(shared_interp, type_info_before)
    # 然后单独设置 blocks（确保替换而不是追加）
    dict2tclinterp({'blocks': blocks_value}, interp=shared_interp)
    # 再次恢复类型信息
    restore_type_info(shared_interp, type_info_before)
    
    # 对包含 $ 的变量使用 subst 展开变量引用
    expand_variable_references(shared_interp)

