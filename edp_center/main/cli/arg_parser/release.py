#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Release 相关参数定义模块
"""

import argparse


def add_release_args(parser: argparse.ArgumentParser) -> None:
    """添加 -release 相关参数"""
    parser.add_argument(
        '-release', '--release',
        action='store_true',
        help='创建 RELEASE（发布运行结果）'
    )
    parser.add_argument(
        '--release-version', '-rver',
        dest='release_version',
        help='RELEASE 版本号（如 v09001）'
    )
    parser.add_argument(
        '--step',
        dest='release_step',
        action='append',
        help='要发布的步骤（格式: flow_name.step_name，如 pnr_innovus.postroute）。可多次指定以 release 多个步骤，或指定 flow_name 以 release 整个 flow'
    )
    parser.add_argument(
        '--release-block', '-rblock',
        dest='release_block',
        help='块名称（如 block1，默认：从当前目录自动推断）'
    )
    parser.add_argument(
        '--note',
        dest='release_note',
        help='发布说明（可选，会写入 release_note.txt）'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='严格模式：如果版本号已存在则报错（默认：自动添加时间戳后缀创建新版本）。如果某个步骤的数据不存在，也会报错（默认：跳过）'
    )
    parser.add_argument(
        '--append',
        action='store_true',
        help='追加模式：如果版本已存在，将新步骤追加到现有版本（默认：创建带时间戳的新版本）'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='覆盖模式：如果版本已存在且包含相同的步骤，则覆盖（需要配合 --append 使用）'
    )
    parser.add_argument(
        '--include-all',
        action='store_true',
        help='包含所有文件（忽略配置中的 file_mappings）'
    )
    parser.add_argument(
        '--include-patterns',
        help='包含的文件模式（逗号分隔，如 "*.def,*.sdf"）'
    )
    parser.add_argument(
        '--exclude-patterns',
        help='排除的文件模式（逗号分隔，如 "*.tmp,*.bak"）'
    )

