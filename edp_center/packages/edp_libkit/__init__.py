#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP LibKit - 库配置生成工具

提供库目录扫描和lib_config.tcl生成功能，支持多种foundry的适配器。
"""

from .lib_info import LibInfo
from .foundry_adapters import FoundryAdapter, AdapterFactory
from .lib_generator import LibGenerator
from .generator import LibConfigGenerator

__all__ = [
    'LibInfo',
    'FoundryAdapter',
    'AdapterFactory',
    'LibGenerator',
    'LibConfigGenerator',
]

__version__ = '0.1.0'

