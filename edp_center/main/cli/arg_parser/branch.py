#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分支相关参数定义模块
"""

import argparse


def add_branch_args(parser: argparse.ArgumentParser) -> None:
    """添加 -branch 相关参数"""
    parser.add_argument(
        '-b', '-branch', '--branch',
        help='创建新的 branch（分支名称，如 branch1）'
    )
    parser.add_argument(
        '--from-branch-step', '-from-step',
        help='从指定分支的步骤创建新分支（如 "branch1:pnr_innovus.init"）'
    )

