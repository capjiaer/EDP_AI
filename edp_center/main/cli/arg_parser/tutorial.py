#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial 相关参数定义模块
"""

import argparse


def add_tutorial_args(parser: argparse.ArgumentParser) -> None:
    """添加 -tutorial 相关参数"""
    parser.add_argument(
        '-tutorial', '--tutorial', '-tutor',
        action='store_true',
        help='打开教程（快捷方式，等同于 edp_info -tutorial）'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='更新教程 HTML（仅 PM 使用，需要 edp_center 写入权限）'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新生成所有 HTML（需要配合 --update 使用）'
    )
    parser.add_argument(
        '--browser',
        help='指定浏览器（如 firefox, chrome, edge）'
    )
    parser.add_argument(
        '--open-dir',
        action='store_true',
        help='打开教程目录（而不是打开 HTML 文件）'
    )

