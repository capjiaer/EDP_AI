#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Main - 统一的工作流管理模块

整合七个核心模块，提供统一的工作流管理接口：
1. edp_dirkit - 环境初始化
2. edp_configkit - 配置加载
3. edp_cmdkit - 脚本处理
4. edp_flowkit - 工作流执行
5. edp_libkit - 库配置生成
6. edp_common - 公共工具
7. edp_webkit - Web服务
"""

from .workflow_manager import WorkflowManager

__version__ = '0.1.0'
__all__ = ['WorkflowManager']

