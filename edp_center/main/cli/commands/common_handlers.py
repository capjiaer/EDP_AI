#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
公共命令处理函数
包含 info 和 run 命令的公共逻辑
"""

import sys
from collections import defaultdict
from pathlib import Path

from ..utils import UnifiedInference


def show_project_list(manager, current_dir: Path, args) -> None:
    """
    显示支持的 project 列表（公共函数）
    
    Args:
        manager: WorkflowManager 实例
        current_dir: 当前工作目录
        args: 命令行参数对象
    """
    try:
        # 使用 UnifiedInference 的方法来查找 edp_center_path（避免重复实现）
        inference = UnifiedInference(manager.edp_center if hasattr(manager, 'edp_center') else current_dir)
        edp_center_path = inference.get_edp_center_path(args)
        
        if edp_center_path:
            projects = inference.list_projects()
            if projects:
                print(f"\n[INFO] 支持的 project:", file=sys.stderr)
                # 按 foundry/node 分组显示
                grouped = defaultdict(list)
                for p in projects:
                    key = f"{p['foundry']}/{p['node']}"
                    grouped[key].append(p['project'])
                
                for key in sorted(grouped.keys()):
                    projects_str = ', '.join(sorted(set(grouped[key])))
                    print(f"  {key}: {projects_str}", file=sys.stderr)
            else:
                # 调试信息：检查为什么没有找到项目
                config_path = edp_center_path / "config"
                print(f"\n[WARN] 未找到任何 project 配置", file=sys.stderr)
                print(f"[DEBUG] edp_center_path: {edp_center_path}", file=sys.stderr)
                print(f"[DEBUG] config_path 存在: {config_path.exists()}", file=sys.stderr)
                if config_path.exists():
                    # 列出 config 目录下的内容
                    foundries = [d.name for d in config_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
                    print(f"[DEBUG] 找到的 foundry: {foundries}", file=sys.stderr)
                    if foundries:
                        # 检查第一个 foundry 下的内容
                        first_foundry = config_path / foundries[0]
                        nodes = [d.name for d in first_foundry.iterdir() if d.is_dir() and not d.name.startswith('.')]
                        print(f"[DEBUG] {foundries[0]} 下的 node: {nodes}", file=sys.stderr)
                        if nodes:
                            # 检查第一个 node 下的内容（排除 common）
                            first_node = first_foundry / nodes[0]
                            projects_in_node = [d.name for d in first_node.iterdir() 
                                               if d.is_dir() and not d.name.startswith('.') and d.name != 'common']
                            print(f"[DEBUG] {foundries[0]}/{nodes[0]} 下的 project: {projects_in_node}", file=sys.stderr)
                print(f"[INFO] 请检查 edp_center/config 目录结构", file=sys.stderr)
        else:
            print(f"\n[WARN] 无法找到 edp_center 路径，无法列出支持的 project", file=sys.stderr)
            print(f"[INFO] 请使用 --edp-center 参数指定 edp_center 路径", file=sys.stderr)
    except Exception as e:
        # 输出错误信息以便调试
        import traceback
        print(f"\n[WARN] 获取项目列表失败: {e}", file=sys.stderr)
        traceback.print_exc()

