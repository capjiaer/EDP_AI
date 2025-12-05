#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用户工作环境初始化命令行接口
"""

import argparse
import sys
from pathlib import Path
from .work_path import WorkPathInitializer


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description='DirKit - 用户工作环境初始化工具'
    )
    
    parser.add_argument(
        '--edp-center',
        required=True,
        help='EDP Center 资源库路径'
    )
    
    parser.add_argument(
        '--work-path',
        help='WORK_PATH 根目录路径（可选，如果不提供则从当前路径推断）'
    )
    
    parser.add_argument(
        '--project',
        '--project-name',
        dest='project',
        help='项目名称（如 dongting），如果不提供则从当前路径推断'
    )
    
    parser.add_argument(
        '--project-node',
        help='项目节点名称（如 P85），如果不提供则从当前路径推断'
    )
    
    parser.add_argument(
        '--block',
        '--block-name',
        dest='block',
        help='块名称（如 block1），如果不提供则从当前路径推断'
    )
    
    parser.add_argument(
        '--user',
        '--user-name',
        dest='user',
        help='用户名（如 zhangsan），如果不提供则自动获取系统用户名'
    )
    
    parser.add_argument(
        '--branch',
        '--branch-name',
        dest='branch',
        default='branch1',
        help='分支名称（默认：branch1）'
    )
    
    parser.add_argument(
        '--from',
        '--from-branch-step',
        dest='from_branch_step',
        help='从已有分支的特定步骤开始创建新分支\n'
             '格式: "branch_name.step_name" 或 "user_name.branch_name.step_name"\n'
             '例如: "branch1.pnr_innovus.init" 或 "zhangsan.branch1.pnr_innovus.init"'
    )
    
    parser.add_argument(
        '--no-link',
        '--no-link-mode',
        dest='no_link_mode',
        action='store_true',
        help='不使用符号链接，使用复制模式（独立副本）\n'
             '默认使用链接模式（节省空间，适用于大文件）'
    )
    
    parser.add_argument(
        '--cwd',
        help='用于检测项目信息的目录（默认：当前工作目录）'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建初始化器
        initializer = WorkPathInitializer(args.edp_center)
        
        # 初始化用户工作环境
        # 默认使用链接模式，除非指定 --no-link
        link_mode = not args.no_link_mode
        
        result = initializer.init_user_workspace(
            work_path=args.work_path,
            project_name=args.project,
            project_node=args.project_node,
            block_name=args.block,
            user_name=args.user,
            branch_name=args.branch,
            from_branch_step=args.from_branch_step,
            link_mode=link_mode,
            current_dir=args.cwd
        )
        
        print(f"用户工作环境初始化成功！")
        print(f"分支路径: {result['branch_path']}")
        
        # 显示检测到的信息（如果使用了自动模式）
        if not args.work_path or not args.project or not args.project_node or not args.block:
            detected = initializer.detect_project_path(args.cwd)
            if detected:
                print(f"自动检测到的项目信息:")
                print(f"  项目: {detected['project_name']}")
                print(f"  项目节点: {detected['project_node']}")
                print(f"  块: {detected['block_name']}")
        
        if not args.user:
            from .work_path import get_current_user
            print(f"自动获取的用户名: {get_current_user()}")
        
        print(f"创建的目录:")
        for dir_name, dir_path in result['directories'].items():
            print(f"  {dir_name}: {dir_path}")
        print(f"创建的文件:")
        for file_name, file_path in result['files'].items():
            print(f"  {file_name}: {file_path}")
        
        # 如果从其他分支复制/链接了步骤，显示信息
        if 'copied_from' in result:
            mode = "链接" if result.get('link_mode', False) else "复制"
            print(f"\n从源分支{mode}步骤:")
            print(f"  源: {result['copied_from']}")
            print(f"  模式: {'符号链接' if result.get('link_mode', False) else '复制'}")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

