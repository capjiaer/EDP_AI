#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
依赖关系可视化命令处理
"""

import sys
from pathlib import Path
from typing import Optional

from ...workflow_manager import WorkflowManager
from ..utils.graph_visualizer import GraphVisualizer
from ..utils.param_inference import infer_all_params, get_foundry_node
from edp_center.packages.edp_common.error_handler import handle_cli_error


@handle_cli_error(error_message="生成依赖关系图失败")
def handle_graph_cmd(manager: WorkflowManager, args) -> int:
    """
    处理依赖关系可视化命令
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 获取项目信息
    project = args.project
    foundry = args.foundry
    node = args.node
    
    # 如果缺少参数，尝试从当前目录推断
    if not project or not foundry or not node:
        try:
            # 使用统一的参数推断逻辑
            params = infer_all_params(manager)
            project = project or params['project']
            foundry = foundry or params['foundry']
            node = node or params['node']
            
            # 更新 args，以便后续使用
            args.project = project
            args.foundry = foundry
            args.node = node
            
            if foundry and node:
                print(f"[OK] 自动推断项目信息:")
                print(f"  project: {project}")
                print(f"  foundry: {foundry}")
                print(f"  node: {node}")
        except ValueError as e:
            # 如果推断失败，尝试其他方法
            if not project:
                # 尝试从路径推断
                from ..init.workspace_helpers import infer_params_from_path
                current_dir = Path.cwd()
                detected = infer_params_from_path(manager, current_dir, args)
                
                if detected:
                    project = args.project
                    # 再次尝试获取 foundry 和 node
                    if project:
                        try:
                            foundry, node = get_foundry_node(manager, project, foundry, node)
                            args.foundry = foundry
                            args.node = node
                        except ValueError:
                            pass
    
    # 最终检查
    if not project:
        print("[ERROR] 缺少必需参数: --project", file=sys.stderr)
        print("[INFO] 提示: 可以在项目目录下运行，系统会自动推断参数", file=sys.stderr)
        return 1
    
    if not foundry or not node:
        print("[ERROR] 无法推断 foundry 和 node", file=sys.stderr)
        print(f"[INFO] 项目 '{project}' 可能存在于多个 foundry/node 组合中", file=sys.stderr)
        print("[INFO] 请手动指定: --foundry <foundry> --node <node>", file=sys.stderr)
        
        # 尝试列出所有匹配的项目
        try:
            matches = manager.work_path_initializer.find_project(project)
            if matches:
                print(f"[INFO] 找到 {len(matches)} 个匹配的项目:", file=sys.stderr)
                for match in matches:
                    print(f"[INFO]   - foundry: {match['foundry']}, node: {match['node']}", file=sys.stderr)
        except Exception:
            pass
        
        return 1
    
    # 加载工作流图
    flow = getattr(args, 'flow', None)
    graph = manager.load_workflow(
        foundry=foundry,
        node=node,
        project=project,
        flow=flow
    )
    
    if not graph or len(graph.steps) == 0:
        print("[ERROR] 没有找到步骤", file=sys.stderr)
        return 1
    
    # 创建可视化器
    visualizer = GraphVisualizer(graph)
    
    # 获取聚焦步骤和深度
    focus_step = getattr(args, 'focus_step', None)
    depth = getattr(args, 'depth', None)
    output_format = getattr(args, 'format', 'text')
    output_file = getattr(args, 'output', None)
    
    # 根据格式生成可视化
    if output_format == 'text':
        # 文本树形图
        result = visualizer.to_text_tree(focus_step=focus_step, depth=depth)
        print(result)
        
        if output_file:
            Path(output_file).write_text(result, encoding='utf-8')
            print(f"\n[INFO] 已保存到: {output_file}")
    
    elif output_format == 'dot':
        # Graphviz DOT 格式
        dot_content = visualizer.to_graphviz(
            focus_step=focus_step,
            depth=depth,
            format='dot'
        )
        
        if output_file:
            Path(output_file).write_text(dot_content, encoding='utf-8')
            print(f"[INFO] DOT 文件已保存到: {output_file}")
        else:
            print(dot_content)
    
    elif output_format in ['png', 'svg', 'pdf']:
        # Graphviz 图片格式
        if not output_file:
            output_file = f"dependency_graph.{output_format}"
        
        output_path = Path(output_file)
        visualizer.to_graphviz(
            output_file=output_path,
            format=output_format,
            focus_step=focus_step,
            depth=depth,
            layout=getattr(args, 'layout', 'dot')
        )
        print(f"[INFO] 图片已保存到: {output_path.absolute()}")
    
    elif output_format == 'mermaid':
        # Mermaid 格式
        result = visualizer.to_mermaid(focus_step=focus_step, depth=depth)
        
        if output_file:
            Path(output_file).write_text(result, encoding='utf-8')
            print(f"[INFO] Mermaid 图表已保存到: {output_file}")
        else:
            print(result)
    
    elif output_format == 'web':
        # Web 交互式可视化
        if not output_file:
            output_file = "dependency_graph.html"
        
        output_path = Path(output_file)
        title = getattr(args, 'title', None)
        if not title:
            title = f"依赖关系图 - {project}" if project else "EDP 依赖关系图"
        
        visualizer.to_web_html(
            output_file=output_path,
            focus_step=focus_step,
            depth=depth,
            title=title
        )
        
        print(f"[INFO] Web 可视化已保存到: {output_path.absolute()}")
        print(f"[INFO] 在浏览器中打开: file://{output_path.absolute()}")
        
        # 可选：自动打开浏览器
        if getattr(args, 'open_browser', False):
            try:
                import webbrowser
                webbrowser.open(f"file://{output_path.absolute()}")
            except Exception as e:
                print(f"[WARN] 无法自动打开浏览器: {e}", file=sys.stderr)
    
    else:
        print(f"[ERROR] 不支持的格式: {output_format}", file=sys.stderr)
        print("[INFO] 支持的格式: text, dot, png, svg, pdf, mermaid, web", file=sys.stderr)
        return 1
    
    return 0

