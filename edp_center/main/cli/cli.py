#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Main CLI - 统一的命令行接口

整合四个 KIT 的命令行功能，提供统一的入口。
"""

import sys

from .arg_parser import create_parser
from .command_router import route_subcommands

# 初始化日志系统
from edp_center.packages.edp_common.logging_config import setup_logging
_logging_initialized = False


def main():
    """运行相关命令的主入口"""
    # 初始化日志系统
    global _logging_initialized
    if not _logging_initialized:
        setup_logging()
        _logging_initialized = True
    
    # 创建参数解析器
    parser = create_parser()
    
    # 解析参数
    args = parser.parse_args()
    
    # 自动检测 edp_center 路径
    from .command_router import find_edp_center_path, create_manager
    edp_center_path = find_edp_center_path(args)
    
    # 处理 -branch 命令
    if args.branch:
        manager = create_manager(edp_center_path)
        from .commands import handle_create_branch
        
        # 创建一个临时的 args 对象来传递参数
        class BranchArgs:
            def __init__(self, args):
                self.work_path = args.work_path
                self.project = args.project
                self.version = args.version
                self.block = args.block
                self.user = args.user
                self.branch = args.branch
                self.foundry = args.foundry
                self.node = args.node
                self.from_branch_step = args.from_branch_step
        
        branch_args = BranchArgs(args)
        return handle_create_branch(manager, branch_args)
    
    # 处理 -release 命令
    if args.release:
        manager = create_manager(edp_center_path)
        from .commands.release import handle_release_cmd
        return handle_release_cmd(manager, args)
    
    # 处理 -tutorial 命令（快捷方式，等同于 edp_info -tutorial）
    if args.tutorial:
        try:
            from .commands.tutorial_handler import handle_tutorial_cmd
            return handle_tutorial_cmd(edp_center_path, args)
        except ImportError as e:
            print(f"[ERROR] 无法导入教程处理器: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"[ERROR] 启动教程失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    # 处理 -run 命令
    if args.run:
        manager = create_manager(edp_center_path)
        from .commands import handle_run_cmd
        return handle_run_cmd(manager, args)
    
    # 处理 -view 命令
    if args.view:
        try:
            # 导入 view 处理器
            from .commands.view_handler import handle_view_cmd
            return handle_view_cmd(args)
        except ImportError as e:
            print(f"[ERROR] 导入 View 模块失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        except Exception as e:
            print(f"[ERROR] 启动 Dashboard 失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1

    # 处理 -stats-web 命令（独立性能分析 Web 服务器）
    if getattr(args, 'stats_web', False):
        try:
            # 检查 Flask 是否安装
            try:
                import flask
            except ImportError:
                print(f"[ERROR] Flask 未安装", file=sys.stderr)
                print(f"[INFO] 请安装 Flask: pip install flask", file=sys.stderr)
                return 1
            
            # 创建 manager
            manager = create_manager(edp_center_path)
            
            from .gui.stats_web import run_stats_web
            stats_port = getattr(args, 'stats_port', 8889)
            open_browser = not getattr(args, 'no_open_browser', False)
            
            run_stats_web(
                manager=manager,
                edp_center_path=edp_center_path,
                port=stats_port,
                open_browser=open_browser
            )
            return 0
        except Exception as e:
            print(f"[ERROR] 启动性能分析 Web 服务器失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    # 处理 -workflow-web 命令（独立 Web 服务器）
    if args.workflow_web:
        try:
            # 检查 Flask 是否安装
            try:
                import flask
            except ImportError:
                print(f"[ERROR] Flask 未安装", file=sys.stderr)
                print(f"[INFO] 请安装 Flask: pip install flask", file=sys.stderr)
                return 1
            
            # 创建 manager
            manager = create_manager(edp_center_path)
            
            # 在启动 Web 服务器之前，先尝试推断参数
            # 如果无法推断，给出友好提示，不启动 Web 服务器
            from pathlib import Path
            from .utils.param_inference import infer_all_params
            
            try:
                # 使用统一的参数推断逻辑
                params = infer_all_params(manager)
                # 验证推断结果
                if not params.get('project') or not params.get('foundry') or not params.get('node'):
                    raise ValueError("推断的参数不完整")
            except ValueError as e:
                print(f"[ERROR] 无法从当前目录推断项目参数: {e}", file=sys.stderr)
                print(f"[INFO] 当前目录: {Path.cwd()}", file=sys.stderr)
                print(f"[INFO] 请进入一个合理的项目目录，例如：", file=sys.stderr)
                print(f"[INFO]   - WORK_PATH/<project>/<version>/<block>/<user>/<branch>/", file=sys.stderr)
                print(f"[INFO]   - 或者包含 .edp_version 文件的目录", file=sys.stderr)
                print(f"[INFO] 然后重新运行: edp -workflow", file=sys.stderr)
                return 1
            
            from .gui.workflow_web import run_workflow_web
            run_workflow_web(
                manager=manager,
                edp_center_path=edp_center_path,
                port=args.web_port,
                open_browser=not args.no_open_browser
            )
            return 0
        except ImportError as e:
            print(f"[ERROR] 导入 Web 服务器模块失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        except Exception as e:
            print(f"[ERROR] 启动 Web 服务器失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    # 处理 -gui 命令
    if args.gui:
        try:
            # 先检查 PyQt5 是否可用
            try:
                from PyQt5.QtWidgets import QApplication
            except ImportError as e:
                print(f"[ERROR] PyQt5 未安装或导入失败: {e}", file=sys.stderr)
                print("[INFO] 请安装 PyQt5: pip install PyQt5", file=sys.stderr)
                return 1
            
            # 导入并启动统一 GUI
            from .gui.main_gui import run_main_gui
            run_main_gui(edp_center_path)
            return 0
        except ImportError as e:
            print(f"[ERROR] 导入 GUI 模块失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        except Exception as e:
            print(f"[ERROR] 启动 GUI 失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    # 处理 -graph 命令
    if args.graph:
        manager = create_manager(edp_center_path)
        from .commands.graph_handler import handle_graph_cmd
        
        # 创建一个临时的 args 对象来传递参数
        class GraphArgs:
            def __init__(self, args):
                self.project = args.project
                self.foundry = args.foundry
                self.node = args.node
                self.flow = getattr(args, 'flow', None)
                self.format = getattr(args, 'graph_format', 'text')
                self.output = getattr(args, 'graph_output', None)
                self.focus_step = getattr(args, 'graph_focus_step', None)
                self.depth = getattr(args, 'graph_depth', None)
                self.layout = getattr(args, 'graph_layout', 'dot')
                self.title = getattr(args, 'graph_title', None)
                self.open_browser = getattr(args, 'open_browser', False)
                # 添加 work_path 属性（推断函数需要）
                self.work_path = getattr(args, 'work_path', '.')
                self.version = getattr(args, 'version', None)
                self.block = getattr(args, 'block', None)
                self.user = getattr(args, 'user', None)
        
        graph_args = GraphArgs(args)
        return handle_graph_cmd(manager, graph_args)
    
    # 处理 -lib 命令
    if args.lib:
        try:
            from .commands.lib_handler import handle_lib_cmd
            return handle_lib_cmd(args)
        except ImportError as e:
            print(f"[ERROR] 导入 Lib 模块失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        except Exception as e:
            print(f"[ERROR] 执行 Lib 命令失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    # 处理信息查询相关命令（-info, -history, -stats, -rollback, -validate）
    from .command_router import route_shortcut_commands
    result = route_shortcut_commands(args)
    if result is not None:
        return result
    
    # 处理子命令
    result = route_subcommands(args)
    if result is not None:
        return result
    
    # 如果没有提供命令，显示帮助
    if not args.branch and not args.run and not args.command and not args.graph and not args.workflow_web and not args.lib:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
