#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主参数解析器模块
整合所有参数定义模块
"""

import argparse

from .common import add_global_args, add_common_args
from .branch import add_branch_args
from .release import add_release_args
from .gui import add_workflow_web_args, add_view_args, add_stats_web_args, add_gui_args
from .graph import add_graph_args
from .tutorial import add_tutorial_args
from .lib import add_lib_args
from .run import add_run_args
from .info import add_info_args
from .completion import setup_completions


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
    add_global_args(parser)
    add_branch_args(parser)
    add_release_args(parser)
    add_workflow_web_args(parser)
    add_view_args(parser)
    add_stats_web_args(parser)
    add_gui_args(parser)
    add_graph_args(parser)
    add_tutorial_args(parser)
    add_lib_args(parser)
    add_run_args(parser)
    info_arg = add_info_args(parser)  # 信息查询相关参数
    add_common_args(parser)
    
    # 设置补全函数
    setup_completions(parser, info_arg)
    
    # 子命令（用于其他功能）
    # 注意：只有当没有使用 -branch、-run 时才需要子命令
    # 已移除 load-workflow 命令，请使用 edp -info 查看流程信息
    subparsers = parser.add_subparsers(dest='command', help='可用命令', required=False)
    
    return parser

