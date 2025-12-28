#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
信息查询相关命令的参数解析器
负责定义 edp_info 命令的所有参数
"""

import argparse
import sys

# 尝试导入 argcomplete（可选依赖）
try:
    import argcomplete
    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False


def create_parser() -> argparse.ArgumentParser:
    """
    创建信息查询相关命令的参数解析器
    
    Returns:
        ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog='edp_info',
        description='EDP Info - 信息查询相关命令（查看信息、历史、统计、验证等）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 查看所有可用的 flow
  edp_info -info
  # 或使用短别名
  edp_info -i
  
  # 查看指定 flow 下所有 step 的状态
  edp_info -info pv_calibre
  # 或使用短别名
  edp_info -i pv_calibre
  
  # 查看运行历史
  edp_info -history
  edp_info -history pv_calibre.ipmerge
  
  # 性能统计
  edp_info -stats
  edp_info -stats pv_calibre.ipmerge
  
  # 回滚
  edp_info -rollback
  edp_info -rollback --index 5
  
  # 结果验证
  edp_info -validate
  edp_info -validate --timing-compare branch1 branch2
  
  # 查看教程
  edp_info -tutorial
  
        """
    )
    
    # 全局参数
    parser.add_argument(
        '--edp-center',
        type=str,
        default=None,
        help='EDP Center 资源库路径（默认：自动检测）'
    )
    
    # ==================== -info 选项 ====================
    info_arg = parser.add_argument(
        '-i', '-info', '--info',
        dest='info',
        nargs='?',  # 可选参数：不提供时显示所有 flow，提供时显示指定 flow 的 step
        metavar='FLOW',  # 明确指定参数名称
        help='显示 flow 信息（不提供参数时显示所有 flow，提供 flow_name 时显示该 flow 下所有 step 的状态）'
    )
    
    # ==================== -tutorial 选项 ====================
    parser.add_argument(
        '-tutorial', '--tutorial',
        action='store_true',
        help='生成教程 HTML 索引并在浏览器中打开'
    )
    
    parser.add_argument(
        '--open-dir',
        action='store_true',
        help='打开教程目录（用于 -tutorial 选项）'
    )
    parser.add_argument(
        '--update', '-update',
        action='store_true',
        help='更新教程 HTML 文件（用于 -tutorial 选项，仅 PM 使用，会在 edp_center/tutorial/ 生成 HTML）'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新生成所有 HTML 文件（用于 -tutorial --update 选项）'
    )
    parser.add_argument(
        '--browser',
        type=str,
        default=None,
        help='指定浏览器（用于 -tutorial 选项，例如: firefox, chrome, chromium）'
    )
    
    # ==================== -history 选项（新增） ====================
    parser.add_argument(
        '-history', '--history',
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
        '--from',
        type=str,
        dest='history_from',
        help='历史记录的起始时间（用于 -history 选项，格式: YYYY-MM-DD）'
    )
    parser.add_argument(
        '--to',
        type=str,
        dest='history_to',
        help='历史记录的结束时间（用于 -history 选项，格式: YYYY-MM-DD）'
    )
    
    # ==================== -stats 选项（新增） ====================
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
    
    # ==================== -rollback 选项（新增） ====================
    parser.add_argument(
        '-rollback', '--rollback',
        dest='rollback',
        nargs='?',  # 可选参数
        metavar='FLOW.STEP',
        help='回滚到历史状态（不提供参数时回滚到上一次成功，提供 flow.step 时回滚到指定步骤的最后一次成功）'
    )
    parser.add_argument(
        '--index',
        type=int,
        dest='rollback_index',
        help='回滚到指定的历史记录索引（用于 -rollback 选项，索引从1开始，1表示最近一次）'
    )
    parser.add_argument(
        '--compare-index',
        type=int,
        nargs=2,
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
        '--dry-run',
        action='store_true',
        dest='rollback_dry_run',
        help='预览回滚操作，不实际执行（用于 -rollback 选项）'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        dest='rollback_dry_run',
        help='预览回滚操作，不实际执行（用于 -rollback 选项，等同于 --dry-run）'
    )
    parser.add_argument(
        '--compare-branch',
        type=str,
        dest='compare_branch',
        help='跨 branch 对比配置差异（用于 -rollback 选项，指定要对比的 branch 名称）'
    )
    
    # ==================== -validate 选项（新增） ====================
    parser.add_argument(
        '-validate', '--validate',
        dest='validate',
        nargs='?',  # 可选参数
        metavar='FLOW.STEP',
        help='验证执行结果（不提供参数时验证最后一次执行，提供 flow.step 时验证指定步骤）'
    )
    parser.add_argument(
        '--timing-compare',
        nargs=2,
        metavar=('BRANCH1', 'BRANCH2'),
        help='Timing compare：对比两个分支的结果（用于 -validate 选项）'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成验证报告（用于 -validate 选项）'
    )
    
    # 通用参数
    parser.add_argument('--work-path', default='.', help='WORK_PATH 根目录路径（默认：当前目录）')
    parser.add_argument('--config', '-config', '-cfg', help='指定配置文件路径（默认：work_path/config.yaml）')
    
    # 导入补全辅助函数
    from .completion import (
        complete_projects, complete_foundries, complete_nodes,
        complete_flows, complete_flow_steps
    )
    
    # 为参数添加补全函数
    project_arg = parser.add_argument('--project', '-prj', help='项目名称（如 dongting），如果存在 config.yaml 则从中读取')
    foundry_arg = parser.add_argument('--foundry', help='代工厂名称（可选）')
    node_arg = parser.add_argument('--node', help='工艺节点（可选）')
    
    # 如果 argcomplete 可用，设置补全函数
    if ARGCOMPLETE_AVAILABLE:
        # 为项目参数添加补全
        def complete_project(prefix, parsed_args, **kwargs):
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            results = complete_projects(foundry=foundry, node=node)
            return [r for r in results if r.startswith(prefix)]
        
        project_arg.completer = complete_project
        
        # 为 foundry 参数添加补全
        def complete_foundry(prefix, parsed_args, **kwargs):
            results = complete_foundries()
            return [r for r in results if r.startswith(prefix)]
        
        foundry_arg.completer = complete_foundry
        
        # 为 node 参数添加补全（需要 foundry）
        def complete_node(prefix, parsed_args, **kwargs):
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            results = complete_nodes(foundry=foundry)
            return [r for r in results if r.startswith(prefix)]
        
        node_arg.completer = complete_node
        
        # 为 -info 参数添加补全（flow 列表）
        def complete_info(prefix, parsed_args, **kwargs):
            try:
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                results = complete_flows(project=project, foundry=foundry, node=node)
                if prefix:
                    return [r for r in results if r.startswith(prefix)]
                else:
                    return results
            except Exception:
                return []
        
        info_arg.completer = complete_info
        
        # 为 -history 参数添加补全（flow.step 格式）
        def complete_history(prefix, parsed_args, **kwargs):
            """补全 -history 参数（flow.step 格式）"""
            if '.' in prefix:
                flow, step_prefix = prefix.split('.', 1)
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                steps = complete_flow_steps(
                    flow=flow,
                    project=project,
                    foundry=foundry,
                    node=node
                )
                return [f"{flow}.{s}" for s in steps if s.startswith(step_prefix)]
            else:
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                flows = complete_flows(project=project, foundry=foundry, node=node)
                return [f for f in flows if f.startswith(prefix)]
        
        # 为 -stats 参数添加补全（flow.step 格式）
        def complete_stats(prefix, parsed_args, **kwargs):
            """补全 -stats 参数（flow.step 格式）"""
            if '.' in prefix:
                flow, step_prefix = prefix.split('.', 1)
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                steps = complete_flow_steps(
                    flow=flow,
                    project=project,
                    foundry=foundry,
                    node=node
                )
                return [f"{flow}.{s}" for s in steps if s.startswith(step_prefix)]
            else:
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                flows = complete_flows(project=project, foundry=foundry, node=node)
                return [f for f in flows if f.startswith(prefix)]
        
        # 为 -validate 参数添加补全（flow.step 格式）
        def complete_validate(prefix, parsed_args, **kwargs):
            """补全 -validate 参数（flow.step 格式）"""
            if '.' in prefix:
                flow, step_prefix = prefix.split('.', 1)
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                steps = complete_flow_steps(
                    flow=flow,
                    project=project,
                    foundry=foundry,
                    node=node
                )
                return [f"{flow}.{s}" for s in steps if s.startswith(step_prefix)]
            else:
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                flows = complete_flows(project=project, foundry=foundry, node=node)
                return [f for f in flows if f.startswith(prefix)]
    
    return parser

