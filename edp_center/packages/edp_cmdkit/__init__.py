#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP CmdKit - Tcl 命令脚本处理工具

用于处理 Tcl 脚本中的 #import 指令：
- #import source <file> - 生成 source 语句（推荐使用）

注意：已移除 #import util 机制，统一使用 #import source
"""

from .cmd_processor import CmdProcessor
from .package_loader import PackageLoader

__version__ = '0.1.0'
__all__ = ['CmdProcessor', 'PackageLoader']

