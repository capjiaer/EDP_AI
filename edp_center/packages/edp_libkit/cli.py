#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP LibKit CLI - 命令行接口

提供库配置生成的命令行工具。
"""

import sys
import argparse
from pathlib import Path
from typing import List
import logging

try:
    from edp_center.packages.edp_common.logging_config import setup_logging
except ImportError:
    # 如果edp_common不可用，使用标准库logging
    import logging
    def setup_logging(level='INFO'):
        logging.basicConfig(level=getattr(logging, level.upper()))

from .generator import LibConfigGenerator
from .foundry_adapters import AdapterFactory

logger = logging.getLogger(__name__)


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='EDP LibKit - 库配置生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个STD库
  edp-libkit gen-lib --foundry Samsung --lib-path /path/to/std_library_dir --lib-type STD --node ln08lpu_gp
  
  # 批量处理多个库（指定多个路径）
  edp-libkit gen-lib --foundry Samsung --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 --lib-type STD --node ln08lpu_gp
  
  # 从文件读取库路径列表（每行一个路径）
  edp-libkit gen-lib --foundry Samsung --lib-paths-file /path/to/lib_paths.txt --lib-type STD --node ln08lpu_gp
  
  # 处理IP库
  edp-libkit gen-lib --foundry Samsung --lib-path /path/to/ip_library_dir --lib-type IP --node ln08lpu_gp
  
  # 指定输出目录（必须）
  edp-libkit gen-lib --foundry Samsung --lib-path /path/to/library_dir --lib-type STD --node ln08lpu_gp --output-dir /path/to/output
  
  # 指定特定版本
  edp-libkit gen-lib --foundry Samsung --lib-path /path/to/library_dir --lib-type STD --node ln08lpu_gp --version 1.00B --output-dir /path/to/output
  
  # 处理所有版本
  edp-libkit gen-lib --foundry Samsung --lib-path /path/to/library_dir --lib-type STD --node ln08lpu_gp --all-versions --output-dir /path/to/output
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # gui 命令
    gui_parser = subparsers.add_parser(
        'gui',
        help='启动图形用户界面'
    )
    
    # gen-lib 命令
    gen_lib_parser = subparsers.add_parser(
        'gen-lib',
        help='生成库的lib_config.tcl文件'
    )
    gen_lib_parser.add_argument(
        '--foundry',
        required=True,
        choices=['Samsung', 'SMIC'],
        help='Foundry名称'
    )
    gen_lib_parser.add_argument(
        '--lib-path',
        type=Path,
        nargs='+',
        help='库目录路径（可以指定多个，或使用 --lib-paths-file）'
    )
    gen_lib_parser.add_argument(
        '--lib-paths-file',
        type=Path,
        help='包含库路径列表的文件（每行一个路径，可选）'
    )
    gen_lib_parser.add_argument(
        '--lib-type',
        choices=['STD', 'IP', 'MEM'],
        required=True,
        help='库类型（STD: 标准单元库, IP: IP库, MEM: 内存库，必须指定）'
    )
    gen_lib_parser.add_argument(
        '--node',
        type=str,
        help='工艺节点（如 ln08lpu_gp）'
    )
    gen_lib_parser.add_argument(
        '--version',
        type=str,
        help='指定版本号（如 2.00A, 1.00B）。如果未指定，默认使用最新版本'
    )
    gen_lib_parser.add_argument(
        '--all-versions',
        action='store_true',
        help='处理所有版本：最新版本生成 lib_config.tcl，其他版本生成 lib_config.{version}.tcl。与 --version 互斥'
    )
    gen_lib_parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='lib_config.tcl输出目录（必须指定）'
    )
    gen_lib_parser.add_argument(
        '--array-name',
        type=str,
        help='lib_config.tcl中的数组变量名（默认：LIBRARY）'
    )
    gen_lib_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(level=log_level)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'gui':
            from .gui import main as gui_main
            gui_main()
            return 0
        elif args.command == 'gen-lib':
            return handle_gen_lib(args)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


def _is_valid_library_directory(lib_path: Path, adapter, lib_type: str) -> bool:
    """
    检查目录是否是有效的库目录
    
    直接使用适配器的 find_view_directories 方法来检测，这样最准确。
    
    Args:
        lib_path: 要检查的目录路径
        adapter: FoundryAdapter 实例
        lib_type: 库类型（STD/IP/MEM）
        
    Returns:
        如果是有效的库目录返回 True，否则返回 False
    """
    if not lib_path.exists() or not lib_path.is_dir():
        return False
    
    try:
        # 直接使用适配器的方法来查找视图目录
        # 这是最准确的方式，因为它使用了和实际处理相同的逻辑
        view_dirs = adapter.find_view_directories(lib_path, lib_type)
        # 如果找到至少2个视图目录，认为是有效的库目录
        return len(view_dirs) >= 2
    except Exception:
        # 如果查找过程中出错，认为不是有效的库目录
        return False


def _find_library_directories(parent_path: Path, adapter, lib_type: str) -> List[Path]:
    """
    在父目录下查找所有有效的库目录
    
    Args:
        parent_path: 父目录路径
        adapter: FoundryAdapter 实例
        lib_type: 库类型（STD/IP/MEM）
        
    Returns:
        找到的库目录路径列表
    """
    library_dirs = []
    
    # 首先检查父目录本身是否直接包含视图目录（不是通过子目录找到的）
    # 获取视图类型列表
    view_types = adapter.get_standard_view_types(lib_type)
    if not view_types:
        view_types = ['gds', 'lef', 'liberty', 'verilog']
    
    # 检查父目录是否直接包含视图目录
    has_direct_views = False
    for view_type in view_types[:3]:  # 只检查前3个常见的
        if (parent_path / view_type).exists() and (parent_path / view_type).is_dir():
            has_direct_views = True
            break
    
    if has_direct_views:
        # 父目录本身是库目录
        return [parent_path]
    
    # 父目录不是库目录，检查子目录
    if parent_path.exists() and parent_path.is_dir():
        for item in parent_path.iterdir():
            if item.is_dir():
                # 检查子目录是否是库目录
                if _is_valid_library_directory(item, adapter, lib_type):
                    library_dirs.append(item)
    
    return sorted(library_dirs)


def handle_gen_lib(args) -> int:
    """处理gen-lib命令"""
    # 检查参数：必须提供 lib-path 或 lib-paths-file 之一
    if not args.lib_path and not args.lib_paths_file:
        print("[ERROR] 必须提供 --lib-path 或 --lib-paths-file 参数", file=sys.stderr)
        return 1
    
    if args.lib_path and args.lib_paths_file:
        print("[ERROR] 不能同时提供 --lib-path 和 --lib-paths-file", file=sys.stderr)
        return 1
    
    if not args.lib_type:
        print("[ERROR] 必须提供 --lib-type 参数（STD/IP/MEM）", file=sys.stderr)
        return 1
    
    if not args.node:
        print("[ERROR] 必须提供 --node 参数（如 ln08lpu_gp）", file=sys.stderr)
        return 1
    
    # 收集所有要处理的库路径
    lib_paths = []
    
    if args.lib_path:
        # 从命令行参数获取
        lib_paths = [Path(p).resolve() for p in args.lib_path]
    elif args.lib_paths_file:
        # 从文件读取
        paths_file = Path(args.lib_paths_file).resolve()
        if not paths_file.exists():
            print(f"[ERROR] 库路径列表文件不存在: {paths_file}", file=sys.stderr)
            return 1
        
        with open(paths_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # 忽略空行和注释
                    lib_paths.append(Path(line).resolve())
        
        if not lib_paths:
            print(f"[ERROR] 库路径列表文件为空或没有有效路径: {paths_file}", file=sys.stderr)
            return 1
    
    # 检查版本参数冲突
    if args.version and args.all_versions:
        print("[ERROR] 不能同时指定 --version 和 --all-versions", file=sys.stderr)
        return 1
    
    print(f"[INFO] Foundry: {args.foundry}")
    print(f"[INFO] Node: {args.node}")
    print(f"[INFO] Library Type: {args.lib_type}")
    if args.version:
        print(f"[INFO] 指定版本: {args.version}")
    elif args.all_versions:
        print(f"[INFO] 处理模式: 所有版本")
    else:
        print(f"[INFO] 处理模式: 最新版本（默认）")
    print(f"[INFO] 待处理库数量: {len(lib_paths)}")
    print(f"[INFO] 输出目录: {args.output_dir}")
    print()
    
    # 创建适配器用于检测库目录
    try:
        adapter = AdapterFactory.create_adapter(args.foundry, args.node)
    except Exception as e:
        print(f"[ERROR] 无法创建适配器: {e}", file=sys.stderr)
        return 1
    
    # 验证所有路径并展开安装目录
    expanded_lib_paths = []
    for lib_path in lib_paths:
        if not lib_path.exists():
            print(f"[ERROR] 库目录不存在: {lib_path}", file=sys.stderr)
            return 1
        if not lib_path.is_dir():
            print(f"[ERROR] 路径不是目录: {lib_path}", file=sys.stderr)
            return 1
        
        # 检查是否是安装目录（包含多个库目录）
        # 通过检查目录下是否包含视图目录来判断
        library_dirs = _find_library_directories(lib_path, adapter, args.lib_type)
        
        if len(library_dirs) > 1:
            # 这是安装目录，包含多个库
            print(f"[INFO] 检测到安装目录，包含 {len(library_dirs)} 个子库:")
            for lib_dir in library_dirs:
                print(f"  - {lib_dir.name}")
            expanded_lib_paths.extend(library_dirs)
        elif len(library_dirs) == 1:
            # 只有一个库目录，直接使用
            expanded_lib_paths.append(library_dirs[0])
        else:
            # 没有找到库目录，可能是路径本身就是一个库目录（但检查失败）
            # 或者路径层级不对，直接使用原路径（让后续处理报错）
            print(f"[WARNING] 未在 {lib_path} 下找到有效的库目录，尝试直接使用该路径")
            expanded_lib_paths.append(lib_path)
    
    if not expanded_lib_paths:
        print("[ERROR] 没有找到任何库目录", file=sys.stderr)
        return 1
    
    # 更新库路径列表
    lib_paths = expanded_lib_paths
    if len(lib_paths) != len([p for p in lib_paths if p.exists()]):
        print(f"[INFO] 展开后待处理库数量: {len(lib_paths)}")
    
    # 批量处理
    all_generated_files = []
    success_count = 0
    fail_count = 0
    
    for idx, lib_path in enumerate(lib_paths, 1):
        print(f"[{idx}/{len(lib_paths)}] 处理库: {lib_path.name}")
        
        try:
            # 创建生成器（使用库目录的父目录作为 ori_path，但实际上不会用到）
            generator = LibConfigGenerator(
                foundry=args.foundry,
                ori_path=lib_path.parent,  # 临时值，不会用到
                output_base_dir=args.output_dir,
                array_name=args.array_name,
                node=args.node
            )
            
            # 根据版本参数选择处理方式
            if args.all_versions:
                # 处理所有版本
                generated_files = generator.generate_all_versions(lib_path, lib_type=args.lib_type)
            else:
                # 处理指定版本或最新版本
                generated_files = generator.generate_from_directory(
                    lib_path, 
                    lib_type=args.lib_type,
                    version=args.version  # 如果为None，会使用最新版本
                )
            all_generated_files.extend(generated_files)
            success_count += 1
            
            for file_path in generated_files:
                print(f"  [OK] 已生成: {file_path.name}")
        
        except Exception as e:
            fail_count += 1
            logger.exception(f"处理库 {lib_path.name} 时出错")
            print(f"  [ERROR] 失败: {e}", file=sys.stderr)
            continue
    
    # 输出总结
    print()
    print("=" * 60)
    print(f"[SUMMARY] 处理完成:")
    print(f"  成功: {success_count}/{len(lib_paths)}")
    if fail_count > 0:
        print(f"  失败: {fail_count}/{len(lib_paths)}")
    print(f"  共生成: {len(all_generated_files)} 个lib_config.tcl文件")
    print("=" * 60)
    
    if all_generated_files:
        print("\n生成的文件列表:")
        for file_path in all_generated_files:
            print(f"  - {file_path}")
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

