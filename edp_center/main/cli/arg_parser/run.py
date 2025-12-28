#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run 相关参数定义模块
"""

import argparse


def add_run_args(parser: argparse.ArgumentParser) -> None:
    """添加 -run 相关参数"""
    parser.add_argument(
        '-run', '--run',
        dest='run',
        help='生成 cmds（格式: <flow_name>.<step_name>，例如: pv_calibre.ipmerge）。可以与 --from 和 --to 配合使用来执行多个步骤'
    )
    parser.add_argument(
        '--from', '-fr',
        dest='run_from',
        help='起始步骤（格式: <flow_name>.<step_name>，例如: pnr_innovus.place）'
    )
    parser.add_argument(
        '--to', '-to',
        dest='run_to',
        help='结束步骤（格式: <flow_name>.<step_name>，例如: pv_calibre.drc）'
    )
    parser.add_argument(
        '--from-step', '-fs',
        dest='run_from_step',
        choices=['skip-upstream', 'skip-downstream', 'all'],
        default='all',
        help='执行范围：skip-upstream=跳过上游步骤，skip-downstream=跳过下游步骤，all=执行所有相关步骤（默认）'
    )
    parser.add_argument(
        '--work-path', '-wpath',
        default='.',
        help='WORK_PATH 根目录路径（默认：当前目录）'
    )
    parser.add_argument(
        '--config', '-config', '-cfg',
        help='指定配置文件路径（默认：work_path/config.yaml）'
    )
    parser.add_argument(
        '--dry-run', '-dry_run',
        action='store_true',
        help='演示模式：只显示构建的命令，不实际执行（仅用于 -run 选项）'
    )
    parser.add_argument(
        '-debug', '--debug',
        action='store_true',
        help='调试模式：启用交互式调试模式（仅用于 -run 选项）'
    )

