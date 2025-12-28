#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Foundry Adapters Package

目录结构：
- interface.py: 适配器接口定义
- foundry_adapter.py: Foundry适配器（统一入口和代理层）
- node_adapter.py: 节点适配器实现（所有 foundry 共享）
- samsung/: Samsung foundry 配置文件目录
  - *.config.yaml: 各节点的 YAML 配置文件
- tsmc/: TSMC foundry 配置文件目录
  - *.config.yaml: 各节点的 YAML 配置文件
- smic/: SMIC foundry 配置文件目录
  - *.config.yaml: 各节点的 YAML 配置文件
"""

from .interface import BaseFoundryAdapter
from .foundry_adapter import FoundryAdapter, AdapterFactory

__all__ = [
    'BaseFoundryAdapter',
    'FoundryAdapter', 
    'AdapterFactory',
]

