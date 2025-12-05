#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP DirKit - 文件和目录操作工具

用于从 edp_center 资源库初始化项目环境，处理文件和目录相关操作。
"""

from .dirkit import DirKit
from .initializer import ProjectInitializer
from .work_path import WorkPathInitializer, get_current_user

__version__ = '0.1.0'
__all__ = ['DirKit', 'ProjectInitializer', 'WorkPathInitializer', 'get_current_user']

