#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DirKit 命令行接口
"""

import argparse
import sys
from pathlib import Path
from .initializer import ProjectInitializer


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description='DirKit - 项目环境初始化工具'
    )
    
    parser.add_argument(
        '--edp-center',
        required=True,
        help='EDP Center 资源库路径'
    )
    
    parser.add_argument(
        '--project-dir',
        required=True,
        help='项目目录路径'
    )
    
    parser.add_argument(
        '--foundry',
        required=True,
        help='代工厂名称（如 SAMSUNG）'
    )
    
    parser.add_argument(
        '--node',
        required=True,
        help='工艺节点（如 S8）'
    )
    
    parser.add_argument(
        '--project',
        required=True,
        help='项目名称（如 dongting）'
    )
    
    parser.add_argument(
        '--link',
        action='store_true',
        help='使用符号链接而不是复制（默认：复制）'
    )
    
    parser.add_argument(
        '--flows',
        nargs='+',
        help='要初始化的流程列表（默认：所有可用流程）'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建初始化器
        initializer = ProjectInitializer(args.edp_center)
        
        # 初始化项目
        result = initializer.init_project(
            project_dir=args.project_dir,
            foundry=args.foundry,
            node=args.node,
            project=args.project,
            link_mode=args.link,
            flows=args.flows
        )
        
        print(f"项目环境初始化成功！")
        print(f"项目目录: {Path(args.project_dir).resolve()}")
        print(f"创建的目录:")
        for name, path in result.items():
            print(f"  {name}: {path}")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

