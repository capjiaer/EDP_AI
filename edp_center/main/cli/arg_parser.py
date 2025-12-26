#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令行参数定义模块
负责定义所有命令行参数和补全函数
"""

import argparse
import sys

# 尝试导入 argcomplete（可选依赖）
try:
    import argcomplete
    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False


def _add_global_args(parser: argparse.ArgumentParser) -> None:
    """添加全局参数"""
    parser.add_argument(
        '--edp-center',
        type=str,
        default=None,
        help='EDP Center 资源库路径（默认：自动检测）'
    )


def _add_branch_args(parser: argparse.ArgumentParser) -> None:
    """添加 -branch 相关参数"""
    parser.add_argument(
        '-b', '-branch', '--branch',
        help='创建新的 branch（分支名称，如 branch1）'
    )
    parser.add_argument(
        '--from-branch-step', '-from-step',
        help='从指定分支的步骤创建新分支（如 "branch1:pnr_innovus.init"）'
    )


def _add_release_args(parser: argparse.ArgumentParser) -> None:
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


def _add_workflow_web_args(parser: argparse.ArgumentParser) -> None:
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


def _add_view_args(parser: argparse.ArgumentParser) -> None:
    """添加 -view 相关参数"""
    parser.add_argument(
        '-view', '--view', '-dashboard',
        action='store_true',
        help='启动 Metrics Dashboard（查看运行数据分析）'
    )


def _add_stats_web_args(parser: argparse.ArgumentParser) -> None:
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


def _add_gui_args(parser: argparse.ArgumentParser) -> None:
    """添加 -gui 相关参数"""
    parser.add_argument(
        '-gui', '--gui',
        action='store_true',
        help='启动统一图形界面（包含项目初始化、Timing Compare 等功能）'
    )


def _add_graph_args(parser: argparse.ArgumentParser) -> None:
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
    # 注意：--flow 参数已在 _add_common_args 中定义，这里不再重复添加


def _add_tutorial_args(parser: argparse.ArgumentParser) -> None:
    """添加 -tutorial 相关参数"""
    parser.add_argument(
        '-tutorial', '--tutorial', '-tutor',
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


def _add_info_args(parser: argparse.ArgumentParser):
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
        nargs='?',  # 可选参数
        metavar='FLOW.STEP',
        help='回滚到历史状态（不提供参数时回滚到上一次成功，提供 flow.step 时回滚到指定步骤的最后一次成功）'
    )
    parser.add_argument(
        '--index',
        type=int,
        help='回滚到指定的历史记录索引（用于 -rollback 选项）'
    )
    parser.add_argument(
        '--to-time',
        type=str,
        dest='rollback_to_time',
        help='回滚到指定时间点（用于 -rollback 选项，格式: YYYY-MM-DD HH:MM:SS）'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        dest='rollback_dry_run',
        help='预览回滚操作，不实际执行（用于 -rollback 选项）'
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


def _add_lib_args(parser: argparse.ArgumentParser) -> None:
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


def _add_run_args(parser: argparse.ArgumentParser) -> None:
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


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """添加通用参数（项目、版本等）
    
    注意：--branch 已在 _add_branch_args 中定义，--flow 已在 _add_graph_args 中定义
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


def _add_legacy_command_args(parser: argparse.ArgumentParser) -> None:
    """添加旧版命令参数（向后兼容）"""
    # 已移除 init-workspace，请使用 -b/--branch
    pass


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog='edp',
        description='EDP - 运行相关命令（执行流程、创建分支等）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 创建 branch（在 user 目录下，自动推断参数）
  edp -b branch1
  # 或使用完整参数名
  edp -branch branch1
  
  # 创建 branch（显式指定参数）
  edp -b branch1 -prj dongting -v P85 --block block1 --user zhangsan
  
  # 从已有分支创建新分支
  edp -b branch2 --from-branch-step "branch1:pnr_innovus.init"
  
  # 运行流程/步骤（自动推断项目信息）
  edp -run pv_calibre.ipmerge
  
  # 运行流程/步骤（显式指定项目信息）
  edp -run pv_calibre.ipmerge -prj dongting --foundry SAMSUNG --node S8
  
  # 运行流程/步骤（指定完整路径信息）
  edp -run pv_calibre.ipmerge -prj dongting -v P85 --block block1 --user zhangsan --branch branch1
  
  # 演示模式：只显示构建的命令，不实际执行
  edp -run pv_calibre.ipmerge --dry-run
  
  # 调试模式：交互式调试
  edp -run pv_calibre.ipmerge --debug
  
  # 执行多个步骤（使用短别名）
  edp -run -fr pnr_innovus.place -to pv_calibre.drc -fs skip-downstream
  
  # 查看教程（快捷方式，等同于 edp_info -tutorial）
  edp -tutor  # 打开已生成的教程 HTML（普通用户）
  edp -tutor --update  # 更新教程 HTML（仅 PM 使用，需要 edp_center 写入权限）
  edp -tutor --update --force  # 强制重新生成所有 HTML
  edp -tutor --browser firefox  # 指定浏览器
  
  # 创建 RELEASE（发布运行结果，使用别名）
  edp -release -rver v09001 --step pnr_innovus.postroute
  edp -release -rver v09001 --step pnr_innovus.postroute --note "Initial release"
  edp -release -rver v09001 --step pnr_innovus.postroute --strict  # 如果版本存在则报错（默认会自动添加时间戳创建新版本）
  
  # 追加到现有版本
  edp -release -rver v09001 --step pnr_innovus.route --append  # 追加新步骤到 v09001
  edp -release -rver v09001 --step pnr_innovus.postroute --append --overwrite  # 覆盖已存在的步骤
  
  # Release 多个步骤
  edp -release -rver v09001 --step pnr_innovus.place --step pnr_innovus.postroute
  
  # Release 整个 flow（从 dependency.yaml 读取所有步骤）
  edp -release -rver v09001 --step pnr_innovus
  
  # 指定 block（如果不在 block 目录下，使用别名）
  edp -release -rver v09001 --step pnr_innovus.postroute -rblock block1
  
  # 覆盖已存在的步骤
  edp -release -rver v09001 --step pnr_innovus.postroute --overwrite
  
  # 生成库配置文件（lib_config.tcl，使用别名）
  edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD -odir /path/to/output
  edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib1 /path/to/lib2 --lib-type STD -odir /path/to/output
  edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD --lib-version 2.00A -odir /path/to/output
  edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD --lib-all-versions -odir /path/to/output
  edp -lib --lib-gui  # 启动图形界面
  
注意：
  - 初始化相关命令请使用 edp_init
  - 所有功能已统一到 edp 命令，包括信息查询（-info, -history, -stats, -rollback, -validate）
        """
    )
    
    # 添加所有参数组
    _add_global_args(parser)
    _add_branch_args(parser)
    _add_release_args(parser)
    _add_workflow_web_args(parser)
    _add_view_args(parser)
    _add_stats_web_args(parser)
    _add_gui_args(parser)
    _add_graph_args(parser)
    _add_tutorial_args(parser)
    _add_lib_args(parser)
    _add_run_args(parser)
    info_arg = _add_info_args(parser)  # 信息查询相关参数
    _add_common_args(parser)
    _add_legacy_command_args(parser)
    
    # 获取参数引用（用于补全功能）
    branch_arg = None
    release_arg = None
    run_arg = None
    for action in parser._actions:
        if hasattr(action, 'option_strings'):
            if '-b' in action.option_strings or '--branch' in action.option_strings:
                branch_arg = action
            elif '--release' in action.option_strings:
                release_arg = action
            elif '-run' in action.option_strings or '--run' in action.option_strings:
                run_arg = action
    
    # 获取通用参数引用（用于补全功能）
    project_arg = None
    version_arg = None
    block_arg = None
    user_arg = None
    foundry_arg = None
    node_arg = None
    for action in parser._actions:
        if hasattr(action, 'option_strings'):
            if '--project' in action.option_strings or '-prj' in action.option_strings:
                project_arg = action
            elif '--version' in action.option_strings or '-v' in action.option_strings:
                version_arg = action
            elif '--block' in action.option_strings:
                block_arg = action
            elif '--user' in action.option_strings:
                user_arg = action
            elif '--foundry' in action.option_strings:
                foundry_arg = action
            elif '--node' in action.option_strings:
                node_arg = action
    
    # 导入补全辅助函数
    from .completion import (
        complete_projects, complete_foundries, complete_nodes,
        complete_flows, complete_flow_steps, complete_blocks,
        complete_users, complete_branches, complete_versions
    )
    
    # 如果 argcomplete 可用，设置补全函数
    if ARGCOMPLETE_AVAILABLE:
        # argcomplete 的 completer 函数签名: completer(prefix, parsed_args, **kwargs)
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
        
        # 为 version 参数添加补全
        def complete_version(prefix, parsed_args, **kwargs):
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            results = complete_versions(project=project)
            return [r for r in results if r.startswith(prefix)]
        
        version_arg.completer = complete_version
        
        # 为 block 参数添加补全
        def complete_block(prefix, parsed_args, **kwargs):
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            results = complete_blocks(project=project)
            return [r for r in results if r.startswith(prefix)]
        
        block_arg.completer = complete_block
        
        # 为 user 参数添加补全（需要 block）
        def complete_user(prefix, parsed_args, **kwargs):
            block = getattr(parsed_args, 'block', None) if parsed_args else None
            results = complete_users(block=block)
            return [r for r in results if r.startswith(prefix)]
        
        user_arg.completer = complete_user
        
        # 为 branch 参数添加补全
        def complete_branch(prefix, parsed_args, **kwargs):
            results = complete_branches()
            return [r for r in results if r.startswith(prefix)]
        
        branch_arg.completer = complete_branch
        
        # 为 -run 参数添加补全（flow.step 格式）
        def complete_run(prefix, parsed_args, **kwargs):
            """补全 -run 参数（flow.step 格式）"""
            # 如果已经输入了 flow.step 格式，尝试补全 step
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
                # 过滤以 prefix 开头的
                return [s for s in steps if s.startswith(prefix)]
            else:
                # 否则补全 flow 列表
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                flows = complete_flows(
                    project=project,
                    foundry=foundry,
                    node=node
                )
                return [f for f in flows if f.startswith(prefix)]
        
        run_arg.completer = complete_run
        
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
        
        if info_arg:
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
    
    # 子命令（用于其他功能）
    # 注意：只有当没有使用 -branch、-run 时才需要子命令
    # 已移除 load-workflow 命令，请使用 edp -info 查看流程信息
    subparsers = parser.add_subparsers(dest='command', help='可用命令', required=False)
    
    return parser

