#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lib 相关参数定义模块
"""

import argparse


def add_lib_args(parser: argparse.ArgumentParser) -> None:
    """添加 -lib 相关参数"""
    parser.add_argument(
        '-lib', '--lib',
        action='store_true',
        help='生成库配置文件（lib_config.tcl）'
    )
    parser.add_argument(
        '--lib-path', '-lpath',
        type=str,
        nargs='+',
        help='库目录路径（可以指定多个，或使用 --lib-paths-file）'
    )
    parser.add_argument(
        '--lib-paths-file',
        type=str,
        help='包含库路径列表的文件（每行一个路径，可选）'
    )
    parser.add_argument(
        '--lib-type',
        choices=['STD', 'IP', 'MEM'],
        help='库类型（STD: 标准单元库, IP: IP库, MEM: 内存库，必须指定）'
    )
    parser.add_argument(
        '--lib-version',
        type=str,
        help='指定版本号（如 2.00A, 1.00B）。如果未指定，默认使用最新版本'
    )
    parser.add_argument(
        '--lib-all-versions',
        action='store_true',
        help='处理所有版本：最新版本生成 lib_config.tcl，其他版本生成 lib_config.{version}.tcl。与 --lib-version 互斥'
    )
    parser.add_argument(
        '--lib-output-dir', '-odir',
        type=str,
        help='lib_config.tcl输出目录（必须指定）'
    )
    parser.add_argument(
        '--lib-array-name',
        type=str,
        help='lib_config.tcl中的数组变量名（默认：LIBRARY）'
    )
    parser.add_argument(
        '--lib-gui',
        action='store_true',
        help='启动库配置生成图形界面'
    )

