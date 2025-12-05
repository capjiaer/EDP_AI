#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Info 命令处理模块
处理 -info 命令，显示指定 flow 下所有 step 的状态
"""

import sys
import yaml
from pathlib import Path

from ..utils import (
    infer_project_info,
    infer_work_path_info,
    list_available_flows,
    get_cmd_filename_from_dependency,
    find_step_flow
)
from .common_handlers import show_project_list
from edp_center.packages.edp_cmdkit.sub_steps import read_sub_steps_from_dependency


def get_step_execution_status(branch_dir: Path, flow_name: str, step_name: str) -> tuple:
    """
    从 .run_info 文件获取步骤的执行状态
    
    Args:
        branch_dir: branch 目录路径
        flow_name: flow 名称
        step_name: step 名称
        
    Returns:
        tuple: (has_run_info, status, last_timestamp)
        - has_run_info: 是否有运行记录
        - status: 'success', 'failed', 或 None（如果未运行）
        - last_timestamp: 最后一次运行的时间戳
    """
    run_info_file = branch_dir / '.run_info'
    if not run_info_file.exists():
        return (False, None, None)
    
    try:
        with open(run_info_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            runs = data.get('runs', [])
            
            # 查找该步骤的最后一次运行记录
            matching_runs = [
                run for run in runs
                if run.get('flow') == flow_name and run.get('step') == step_name
            ]
            
            if not matching_runs:
                return (False, None, None)
            
            # 获取最后一次运行（按时间戳排序，最新的在前）
            last_run = sorted(matching_runs, key=lambda x: x.get('timestamp', ''), reverse=True)[0]
            status = last_run.get('status')
            timestamp = last_run.get('timestamp')
            
            return (True, status, timestamp)
    except Exception:
        # 如果读取失败，返回未运行状态
        return (False, None, None)


def show_flow_status(manager, edp_center_path, foundry, node, project, flow_name, branch_dir: Path = None):
    """
    显示指定 flow 的状态信息（辅助函数，可被其他模块调用）
    
    Args:
        manager: WorkflowManager 实例
        edp_center_path: EDP Center 路径
        foundry: Foundry 名称
        node: Node 名称
        project: Project 名称（可能为 None）
        flow_name: Flow 名称
        
    Returns:
        bool: 是否成功显示（True=成功，False=失败）
    """
    try:
        # 获取所有可用的 flow
        available_flows = list_available_flows(edp_center_path, foundry, node, project)
        
        # 检查 flow 是否存在
        if flow_name not in available_flows:
            print(f"[WARN] Flow '{flow_name}' 不存在，无法显示状态", file=sys.stderr)
            return False
        
        # 加载 workflow graph 以获取依赖关系
        try:
            graph = manager.load_workflow(foundry, node, project, flow=None)
        except Exception as e:
            print(f"[WARN] 加载 workflow 失败: {e}，将显示简化状态", file=sys.stderr)
            graph = None
        
        steps_info = available_flows[flow_name]
        
        # 获取拓扑排序后的步骤顺序（只包含属于当前 flow 的步骤）
        try:
            if graph:
                sorted_steps = graph.topological_sort()
                # 过滤出属于当前 flow 的步骤，并保持拓扑顺序
                flow_step_order = []
                for step in sorted_steps:
                    step_flow = find_step_flow(edp_center_path, foundry, node, project, step.name)
                    if step_flow == flow_name and step.name in steps_info:
                        flow_step_order.append(step.name)
                
                # 对于不在图中的步骤（可能没有依赖关系），按字母顺序添加到末尾
                remaining_steps = set(steps_info.keys()) - set(flow_step_order)
                if remaining_steps:
                    flow_step_order.extend(sorted(remaining_steps))
            else:
                flow_step_order = sorted(steps_info.keys())
        except Exception:
            # 如果拓扑排序失败（例如有循环依赖），回退到字母顺序
            flow_step_order = sorted(steps_info.keys())
        
        # 显示分隔线
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"[INFO] Flow '{flow_name}' 当前状态:", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        
        # 按拓扑顺序显示
        for step_name in flow_step_order:
            info = steps_info[step_name]
            ready = info.get('ready', False)
            
            # 格式化 step 名称（小写）
            step_display = step_name.lower()
            print(f"\n{step_display}:", file=sys.stderr)
            
            # STATUS
            # 首先检查配置就绪状态
            if not ready:
                print(f"     STATUS: ERROR, PLEASE CONNECT WITH FLOW OWNER FOR MORE INFORMATION", file=sys.stderr)
            else:
                # 如果配置就绪，检查执行状态
                if branch_dir:
                    has_run_info, exec_status, last_timestamp = get_step_execution_status(branch_dir, flow_name, step_name)
                    if has_run_info:
                        if exec_status == 'success':
                            print(f"     STATUS: OK (执行成功)", file=sys.stderr)
                            if last_timestamp:
                                print(f"     LAST_RUN: {last_timestamp}", file=sys.stderr)
                        elif exec_status == 'failed':
                            print(f"     STATUS: ERROR (执行失败)", file=sys.stderr)
                            if last_timestamp:
                                print(f"     LAST_RUN: {last_timestamp}", file=sys.stderr)
                        else:
                            print(f"     STATUS: OK (配置就绪，未运行)", file=sys.stderr)
                    else:
                        print(f"     STATUS: OK (配置就绪，未运行)", file=sys.stderr)
                else:
                    print(f"     STATUS: OK (配置就绪)", file=sys.stderr)
            
            # PRE_STEP 和 POST_STEP
            pre_steps = []
            post_steps = []
            
            if graph and step_name in graph.steps:
                # 获取前置步骤
                prev_steps = graph.get_prev_steps(step_name)
                # 将 step_name 映射回 flow_name.step_name 格式
                for step in prev_steps:
                    # 查找该 step 属于哪个 flow
                    step_flow = find_step_flow(edp_center_path, foundry, node, project, step.name)
                    if step_flow:
                        pre_steps.append(f"{step_flow}.{step.name}")
                    else:
                        pre_steps.append(step.name)
                
                # 获取后置步骤
                next_steps = graph.get_next_steps(step_name)
                # 将 step_name 映射回 flow_name.step_name 格式
                for step in next_steps:
                    # 查找该 step 属于哪个 flow
                    step_flow = find_step_flow(edp_center_path, foundry, node, project, step.name)
                    if step_flow:
                        post_steps.append(f"{step_flow}.{step.name}")
                    else:
                        post_steps.append(step.name)
            
            # 显示 PRE_STEP
            if pre_steps:
                pre_str = ', '.join(sorted(pre_steps))
                print(f"     PRE_STEP: {pre_str}", file=sys.stderr)
            else:
                print(f"     PRE_STEP: NONE", file=sys.stderr)
            
            # 显示 POST_STEP
            if post_steps:
                post_str = ', '.join(sorted(post_steps))
                print(f"     POST_STEP: {post_str}", file=sys.stderr)
            else:
                print(f"     POST_STEP: NONE", file=sys.stderr)
            
            # 显示 SUB_STEPS（如果存在）
            try:
                sub_steps = read_sub_steps_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
                if sub_steps:
                    # 提取 proc 名称列表
                    sub_step_proc_names = []
                    for sub_step in sub_steps:
                        if isinstance(sub_step, dict) and len(sub_step) == 1:
                            _, proc_name = next(iter(sub_step.items()))
                            sub_step_proc_names.append(proc_name)
                    
                    if sub_step_proc_names:
                        sub_steps_str = ', '.join(sub_step_proc_names)
                        print(f"     SUB_STEPS: {sub_steps_str}", file=sys.stderr)
            except Exception:
                # 如果读取 sub_steps 失败，忽略（不影响主流程）
                pass
        
        print(f"\n{'='*60}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"[WARN] 显示 flow 状态失败: {e}", file=sys.stderr)
        return False


def handle_info_cmd(manager, args) -> int:
    """
    处理 -info 命令，显示指定 flow 下所有 step 的状态
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    try:
        # 处理 nargs='?' 的情况（args.info 可能是 None、字符串或列表）
        if args.info is None:
            flow_name = None
        elif isinstance(args.info, list):
            flow_name = args.info[0] if args.info else None
        else:
            flow_name = args.info
        
        # 获取当前工作目录
        current_dir = Path.cwd().resolve()
        
        # 推断项目信息
        project_info = infer_project_info(manager, current_dir, args)
        if not project_info:
            print(f"[ERROR] 无法推断项目信息，请确保在正确的工作目录下运行", file=sys.stderr)
            print(f"[INFO] 或者手动指定: --edp-center, --project, --foundry, --node", file=sys.stderr)
            
            # 显示支持的 project 列表
            show_project_list(manager, current_dir, args)
            
            return 1
        
        edp_center_path = project_info['edp_center_path']
        foundry = project_info['foundry']
        node = project_info['node']
        project = project_info.get('project')
        
        # 获取所有可用的 flow
        available_flows = list_available_flows(edp_center_path, foundry, node, project)
        
        # 如果没有提供 flow_name，显示所有 flow
        if flow_name is None:
            print(f"[INFO] 可用的 flow:", file=sys.stderr)
            if available_flows:
                for flow in sorted(available_flows.keys()):
                    steps_info = available_flows[flow]
                    ready_steps = [step for step, info in steps_info.items() if info.get('ready', False)]
                    not_ready_steps = [step for step, info in steps_info.items() if not info.get('ready', False)]
                    
                    if ready_steps:
                        ready_str = ', '.join(sorted(ready_steps))
                        print(f"  {flow}: {ready_str}", file=sys.stderr)
                    if not_ready_steps:
                        not_ready_str = ', '.join(sorted(not_ready_steps))
                        print(f"  {flow} (未就绪): {not_ready_str}", file=sys.stderr)
            else:
                print(f"  (未找到可用的 flow)", file=sys.stderr)
            return 0
        
        # 如果提供了 flow_name，显示该 flow 的所有 step 信息
        if flow_name not in available_flows:
            print(f"[ERROR] Flow '{flow_name}' 不存在", file=sys.stderr)
            print(f"\n[INFO] 可用的 flow:", file=sys.stderr)
            if available_flows:
                for flow in sorted(available_flows.keys()):
                    print(f"  {flow}", file=sys.stderr)
            else:
                print(f"  (未找到可用的 flow)", file=sys.stderr)
            return 1
        
        # 尝试推断工作路径信息（如果可能）
        branch_dir = None
        try:
            work_path_info = infer_work_path_info(current_dir, args, project_info)
            if work_path_info and work_path_info.get('work_path') and work_path_info.get('project') and \
               work_path_info.get('version') and work_path_info.get('block') and \
               work_path_info.get('user') and work_path_info.get('branch'):
                from pathlib import Path
                work_path = Path(work_path_info['work_path']).resolve()
                project = work_path_info['project']
                version = work_path_info.get('version')
                block = work_path_info['block']
                user = work_path_info['user']
                branch = work_path_info['branch']
                branch_dir = work_path / project / version / block / user / branch
        except Exception:
            # 如果推断失败，继续使用 None（只显示配置状态）
            pass
        
        # 使用辅助函数显示 flow 状态
        show_flow_status(manager, edp_center_path, foundry, node, project, flow_name, branch_dir=branch_dir)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] 显示 flow 信息失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

