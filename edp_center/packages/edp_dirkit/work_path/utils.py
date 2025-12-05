#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Work Path Utils - 工具函数
"""

import os


def get_current_user() -> str:
    """
    获取当前用户名
    
    Returns:
        用户名字符串
    """
    # 尝试多个环境变量
    for env_var in ['USER', 'USERNAME', 'LOGNAME']:
        user = os.environ.get(env_var)
        if user:
            return user
    
    # 如果都获取不到，尝试系统默认
    import getpass
    try:
        return getpass.getuser()
    except Exception:
        return "unknown_user"

