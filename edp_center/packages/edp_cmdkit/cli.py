#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CmdKit 命令行接口
"""

import sys
import argparse
from pathlib import Path
from .cmd_processor import CmdProcessor


def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description='EDP CmdKit - Tcl 命令脚本处理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个文件并输出到控制台
  edp-cmdkit process cmds_example/my_example.tcl

  # 处理文件并保存到输出文件
  edp-cmdkit process cmds_example/my_example.tcl -o output.tcl

  # 指定搜索路径
  edp-cmdkit process cmds_example/my_example.tcl -d cmds_example -d helpers/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # process 命令
    process_parser = subparsers.add_parser('process', help='处理 Tcl 脚本文件')
    process_parser.add_argument(
        'input_file',
        type=str,
        help='输入的 Tcl 文件路径'
    )
    process_parser.add_argument(
        '--search-paths', '-d',
        action='append',
        dest='search_paths',
        help='搜索目录列表，可以多次指定（用于查找被导入的文件）。'
             '示例: -d cmds -d util'
    )
    process_parser.add_argument(
        '-o', '--output',
        type=str,
        help='输出文件路径（如果不指定，输出到控制台）'
    )
    process_parser.add_argument(
        '--base-dir',
        type=str,
        help='基础目录（默认为当前工作目录）'
    )
    process_parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='不在搜索目录中递归查找子目录（默认会递归查找）'
    )
    process_parser.add_argument(
        '--edp-center',
        type=str,
        help='edp_center 资源库路径（用于生成默认 source 语句）'
    )
    process_parser.add_argument(
        '--foundry',
        type=str,
        help='代工厂名称（如 SAMSUNG），用于生成默认 source 语句。'
             '如果提供了 --project，可以自动查找'
    )
    process_parser.add_argument(
        '--node',
        type=str,
        help='工艺节点（如 S8），用于生成默认 source 语句。'
             '如果提供了 --project，可以自动查找'
    )
    process_parser.add_argument(
        '--project',
        type=str,
        help='项目名称（如 dongting），用于生成默认 source 语句。'
             '如果提供了 --project 但没有提供 --foundry 和 --node，会自动查找'
    )
    process_parser.add_argument(
        '--flow-name',
        type=str,
        help='流程名称（如 pv_calibre），用于生成默认 source 语句'
    )
    process_parser.add_argument(
        '--prepend-default-sources',
        action='store_true',
        help='在文件头部添加默认的 source 语句（需要配合 --edp-center, --foundry, --node 使用）'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'process':
            # 创建处理器
            base_dir = Path(args.base_dir).resolve() if args.base_dir else None
            processor = CmdProcessor(base_dir=base_dir)
            
            # 处理文件
            result = processor.process_file(
                input_file=args.input_file,
                output_file=args.output,
                search_paths=args.search_paths,
                recursive=not args.no_recursive,  # 默认递归，--no-recursive 时禁用
                edp_center_path=args.edp_center,
                foundry=args.foundry,
                node=args.node,
                project=args.project,
                flow_name=args.flow_name,
                prepend_default_sources=args.prepend_default_sources
            )
            
            # 如果未指定输出文件，输出到控制台
            if result is not None:
                print(result, end='')
            
            return 0
        
        else:
            parser.print_help()
            return 1
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

