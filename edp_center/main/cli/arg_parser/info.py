#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Info 相关参数定义模块
包含 -info, -history, -stats, -rollback, -validate 等参数
"""

import argparse


def add_info_args(parser: argparse.ArgumentParser):
    """添加信息查询相关参数（-info, -history, -stats, -rollback, -validate）"""
    # ==================== -info 选项 ====================
    info_arg = parser.add_argument(
        '-i', '-info', '--info',
        dest='info',
        nargs='?',  # 可选参数：不提供时显示所有 flow，提供时显示指定 flow 的 step
        metavar='FLOW',  # 明确指定参数名称
        help='显示 flow 信息（不提供参数时显示所有 flow，提供 flow_name 时显示该 flow 下所有 step 的状态）'
    )
    
    # ==================== -history 选项 ====================
    parser.add_argument(
        '-history', '--history', '-hist',
        dest='history',
        nargs='?',  # 可选参数
        metavar='FLOW.STEP',
        help='查看运行历史（不提供参数时显示所有历史，提供 flow.step 时显示指定步骤的历史）'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='限制显示的历史记录数量（用于 -history 选项）'
    )
    parser.add_argument(
        '--status',
        type=str,
        choices=['success', 'failed', 'running', 'cancelled'],
        default=None,
        help='过滤历史记录的状态（用于 -history 选项）'
    )
    parser.add_argument(
        '--from-date',
        type=str,
        dest='history_from',
        help='历史记录的起始时间（用于 -history 选项，格式: YYYY-MM-DD）'
    )
    parser.add_argument(
        '--to-date',
        type=str,
        dest='history_to',
        help='历史记录的结束时间（用于 -history 选项，格式: YYYY-MM-DD）'
    )
    
    # ==================== -stats 选项 ====================
    parser.add_argument(
        '-stats', '--stats',
        dest='stats',
        nargs='?',  # 可选参数
        metavar='FLOW.STEP',
        help='性能统计（不提供参数时显示所有步骤的统计，提供 flow.step 时显示指定步骤的统计）'
    )
    parser.add_argument(
        '--trend',
        action='store_true',
        help='显示性能趋势（用于 -stats 选项）'
    )
    parser.add_argument(
        '--export',
        type=str,
        help='导出性能报告到文件（用于 -stats 选项，例如: --export report.html）'
    )
    
    # ==================== -rollback 选项 ====================
    parser.add_argument(
        '-rollback', '--rollback',
        dest='rollback',
        nargs='?',  # 可选参数，不提供时为 None，提供时为参数值
        const=True,  # 当没有参数时，设置为 True
        metavar='FLOW.STEP',
        help='回滚到历史状态（不提供参数时回滚到上一次成功，提供 flow.step 时回滚到指定步骤的最后一次成功）'
    )
    parser.add_argument(
        '--index',
        type=int,
        help='回滚到指定的历史记录索引（用于 -rollback 选项）'
    )
    parser.add_argument(
        '--compare-index',
        nargs=2,
        type=int,
        metavar=('INDEX1', 'INDEX2'),
        dest='compare_indices',
        help='对比指定的两个历史记录索引（用于 -rollback 选项，例如: --compare-index 1 3）'
    )
    parser.add_argument(
        '--to-time',
        type=str,
        dest='rollback_to_time',
        help='回滚到指定时间点（用于 -rollback 选项，格式: YYYY-MM-DD HH:MM:SS）'
    )
    parser.add_argument(
        '--rollback-dry-run',
        action='store_true',
        dest='rollback_dry_run',
        help='预览回滚操作，不实际执行（用于 -rollback 选项）'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        dest='rollback_dry_run',
        help='预览回滚操作，不实际执行（用于 -rollback 选项，同 --dry-run）'
    )
    parser.add_argument(
        '--compare-branch',
        type=str,
        help='对比指定 branch 的成功运行与当前 branch 的失败运行（用于 -rollback 选项）'
    )
    
    # ==================== -validate 选项 ====================
    parser.add_argument(
        '-validate', '--validate', '-val',
        dest='validate',
        nargs='?',  # 可选参数
        metavar='FLOW.STEP',
        help='验证执行结果（不提供参数时验证最后一次执行，提供 flow.step 时验证指定步骤）'
    )
    parser.add_argument(
        '--timing-compare', '-tcompare',
        nargs=2,
        metavar=('BRANCH1', 'BRANCH2'),
        help='Timing compare：对比两个分支的结果（用于 -validate 选项）'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成验证报告（用于 -validate 选项）'
    )
    
    return info_arg  # 返回 info_arg 用于补全功能

