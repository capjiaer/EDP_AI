#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI 和 Web 相关参数定义模块
"""

import argparse


def add_workflow_web_args(parser: argparse.ArgumentParser) -> None:
    """添加 -workflow-web 相关参数"""
    parser.add_argument(
        '-workflow', '-workflow-web', '--workflow', '--workflow-web',
        action='store_true',
        dest='workflow_web',
        help='启动工作流 Web 服务器（使用浏览器访问）'
    )
    parser.add_argument(
        '--web-port', '-port',
        type=int,
        default=8888,
        help='Web 服务器端口（默认: 8888）'
    )
    parser.add_argument(
        '--no-open-browser',
        action='store_true',
        help='不自动打开浏览器'
    )


def add_view_args(parser: argparse.ArgumentParser) -> None:
    """添加 -view 相关参数"""
    parser.add_argument(
        '-view', '--view', '-dashboard',
        action='store_true',
        help='启动 Metrics Dashboard（查看运行数据分析）'
    )


def add_stats_web_args(parser: argparse.ArgumentParser) -> None:
    """添加 -stats-web 相关参数"""
    parser.add_argument(
        '-stats-web', '--stats-web',
        action='store_true',
        dest='stats_web',
        help='启动性能分析 Web 服务器（使用浏览器访问）'
    )
    parser.add_argument(
        '--stats-port',
        type=int,
        default=8889,
        help='性能分析 Web 服务器端口（默认: 8889）'
    )


def add_gui_args(parser: argparse.ArgumentParser) -> None:
    """添加 -gui 相关参数"""
    parser.add_argument(
        '-gui', '--gui',
        action='store_true',
        help='启动统一图形界面（包含项目初始化、Timing Compare 等功能）'
    )

