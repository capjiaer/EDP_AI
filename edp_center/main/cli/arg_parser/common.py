#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
通用参数定义模块
包含全局参数和通用参数（项目、版本等）
"""

import argparse


def add_global_args(parser: argparse.ArgumentParser) -> None:
    """添加全局参数"""
    parser.add_argument(
        '--edp-center',
        type=str,
        default=None,
        help='EDP Center 资源库路径（默认：自动检测）'
    )


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """添加通用参数（项目、版本等）
    
    注意：--branch 已在 branch 模块中定义，--flow 已在 graph 模块中定义
    """
    parser.add_argument(
        '-prj', '--project', '--prj',
        dest='project',
        help='项目名称（如 dongting）'
    )
    parser.add_argument(
        '-v', '--version',
        dest='version',
        help='项目版本（如 P85, P90）'
    )
    parser.add_argument(
        '--foundry',
        help='代工厂名称（如 SAMSUNG, TSMC）'
    )
    parser.add_argument(
        '--node',
        help='工艺节点（如 S8, N5）'
    )
    parser.add_argument(
        '--block',
        help='块名称（如 block1, block2）'
    )
    parser.add_argument(
        '--user',
        help='用户名称（如 user1, zhangsan）'
    )

