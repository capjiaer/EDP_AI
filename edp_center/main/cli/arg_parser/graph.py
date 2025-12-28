#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Graph 相关参数定义模块
"""

import argparse


def add_graph_args(parser: argparse.ArgumentParser) -> None:
    """添加 -graph 相关参数"""
    parser.add_argument(
        '-graph', '--graph',
        action='store_true',
        help='生成依赖关系可视化图'
    )
    parser.add_argument(
        '--graph-format', '--format', '-format',
        dest='graph_format',
        choices=['text', 'dot', 'png', 'svg', 'pdf', 'mermaid', 'web'],
        default='text',
        help='输出格式：text=文本树形图（默认），dot=Graphviz DOT，png/svg/pdf=图片，mermaid=Mermaid图表，web=交互式HTML'
    )
    parser.add_argument(
        '--graph-output', '--output', '-output',
        dest='graph_output',
        help='输出文件路径（可选，默认输出到控制台或生成默认文件名）'
    )
    parser.add_argument(
        '--graph-focus', '--focus-step',
        dest='graph_focus_step',
        help='聚焦的步骤名称（只显示相关子图）'
    )
    parser.add_argument(
        '--graph-depth', '--depth',
        dest='graph_depth',
        type=int,
        help='深度限制（只显示指定深度的依赖关系）'
    )
    parser.add_argument(
        '--graph-layout', '--layout',
        dest='graph_layout',
        choices=['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo'],
        default='dot',
        help='Graphviz 布局引擎（仅用于图片格式）'
    )
    parser.add_argument(
        '--graph-title', '--title',
        dest='graph_title',
        help='图表标题（仅用于 web 格式）'
    )
    parser.add_argument(
        '--open-browser',
        action='store_true',
        help='自动打开浏览器（仅用于 web 格式）'
    )
    parser.add_argument(
        '--flow',
        help='流程名称（如 pnr_innovus, pv_calibre）'
    )

