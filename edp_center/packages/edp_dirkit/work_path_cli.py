#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WorkPathInitializer 命令行接口
"""

import argparse
import sys
from pathlib import Path
from .work_path import WorkPathInitializer


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description='DirKit - 工作路径初始化工具'
    )
    
    parser.add_argument(
        '--edp-center',
        required=True,
        help='EDP Center 资源库路径'
    )
    
    parser.add_argument(
        '--work-path',
        required=True,
        help='WORK_PATH 根目录路径'
    )
    
    parser.add_argument(
        '--project',
        '--project-name',
        dest='project',
        required=True,
        help='项目名称（如 dongting），会自动查找对应的 foundry 和 node'
    )
    
    parser.add_argument(
        '--foundry',
        help='可选：代工厂名称（如 SAMSUNG），如果项目在多个 foundry 下存在时需要指定'
    )
    
    parser.add_argument(
        '--node',
        help='可选：工艺节点（如 S8），如果项目在多个 node 下存在时需要指定'
    )
    
    parser.add_argument(
        '--project-node',
        required=True,
        help='项目节点名称（如 P85, P90，表示项目阶段）'
    )
    
    parser.add_argument(
        '--blocks',
        nargs='+',
        help='块名称列表（如 block1 block2），如果不提供则从配置文件读取'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建初始化器
        initializer = WorkPathInitializer(args.edp_center)
        
        # 初始化项目结构
        result = initializer.init_project(
            work_path=args.work_path,
            project_name=args.project,
            project_node=args.project_node,
            blocks=args.blocks,
            foundry=args.foundry,
            node=args.node
        )
        
        print(f"工作路径初始化成功！")
        print(f"工作路径: {Path(args.work_path).resolve()}")
        print(f"项目: {result['project']} (foundry={result['foundry']}, node={result['node']})")
        print(f"项目节点: {result['project_node']}")
        if 'blocks' in result:
            print(f"创建的块:")
            for block_name, block_path in result['blocks'].items():
                print(f"  {block_name}: {block_path}")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

