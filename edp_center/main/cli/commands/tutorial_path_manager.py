#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial Path Manager - 教程路径管理

负责确定教程 HTML 文件的输出目录（用户可写位置）。
"""

import os
import tempfile
from pathlib import Path


def get_tutorial_output_dir(edp_center_path: Path) -> Path:
    """
    获取教程 HTML 输出目录（统一输出到 edp_center/tutorial/）
    
    现在 HTML 文件统一生成在 edp_center/tutorial/ 目录下，由 PM 负责更新。
    普通用户直接打开已生成的 HTML 文件，不需要本地生成。
    
    Args:
        edp_center_path: edp_center 路径（用于读取源文件）
        
    Returns:
        输出目录路径（edp_center/tutorial/）
    """
    return edp_center_path / 'tutorial'

