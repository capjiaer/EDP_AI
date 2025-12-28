#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
范围执行模块
处理 --from 和 --to 参数，支持并行执行多个步骤
"""

import sys
import logging
from pathlib import Path

from ..utils import (
    infer_and_validate_project_info, infer_work_path_info,
    validate_work_path_info, get_current_dir
)
from .run_range_helper import get_steps_to_execute
from .run_single_step import execute_single_step
from edp_center.packages.edp_common.error_handler import handle_cli_error

# 获取 logger
logger = logging.getLogger(__name__)


@handle_cli_error(error_message="执行步骤范围失败")
def handle_run_range(manager, args, run_from, run_to, single_step) -> int:
    """
    处理 --from 和 --to 参数，执行多个步骤（支持并行执行）
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        run_from: 起始步骤（格式: flow.step）
        run_to: 目标步骤（格式: flow.step）
        single_step: 单个步骤（格式: flow.step），如果指定，则只执行这个步骤
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    # 获取当前工作目录
    current_dir = get_current_dir()
    
    # 推断项目信息
    project_info = infer_and_validate_project_info(manager, current_dir, args)
    if not project_info:
        return 1
    
    edp_center_path = project_info['edp_center_path']
    foundry = project_info['foundry']
    node = project_info['node']
    project = project_info.get('project')
    
    # 加载依赖图（加载所有 flow，自动发现跨 flow 依赖）
    graph = manager.load_workflow(foundry, node, project, flow=None)
    
    # 找到需要执行的步骤列表
    try:
        steps_to_execute = get_steps_to_execute(graph, run_from, run_to, single_step)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    
    if not steps_to_execute:
        print(f"[ERROR] 没有找到需要执行的步骤", file=sys.stderr)
        return 1
    
    print(f"[INFO] 将执行以下步骤:", file=sys.stderr)
    for i, step_name in enumerate(steps_to_execute, 1):
        print(f"  {i}. {step_name}", file=sys.stderr)
    
    # 推断工作路径信息
    work_path_info = infer_work_path_info(current_dir, args, project_info)
    if not work_path_info:
        print(f"[ERROR] 无法推断工作路径信息：未找到 .edp_version 文件", file=sys.stderr)
        return 1
    
    # 验证 work_path_info 是否完整
    is_complete, missing_fields = validate_work_path_info(work_path_info)
    if not is_complete:
        print(f"[ERROR] 缺少必要的工作路径信息:", file=sys.stderr)
        for field in missing_fields:
            field_name = {
                'work_path': '--work-path',
                'project': '--project 或 -prj',
                'version': '--version 或 -v',
                'block': '--block 或 -blk',
                'user': '--user',
                'branch': '--branch 或 -b'
            }.get(field, f'--{field}')
            print(f"  - {field}: 请使用 {field_name} 指定", file=sys.stderr)
        return 1
    
    # 确定 branch 目录路径
    branch_dir = build_branch_dir(work_path_info)
    
    # 创建一个步骤名称集合，用于快速查找
    steps_to_execute_set = set(steps_to_execute)
    
    # 重置所有需要执行的步骤的状态为 INIT
    from edp_center.packages.edp_flowkit.flowkit.step import StepStatus
    for step_name in steps_to_execute:
        step = graph.get_specific_step(step_name)
        if step:
            step.update_status(StepStatus.INIT)
    
    # 创建自定义的 execute_func，用于执行单个步骤
    def execute_step_func(step, merged_var):
            """
            执行单个步骤的自定义函数（用于并行执行）
            
            Args:
                step: Step 对象
                merged_var: 合并后的配置字典（这里不使用，因为我们使用 execute_single_step）
                
            Returns:
                bool: 执行是否成功
            """
            step_name = step.name
            
            # 为这个步骤创建一个临时的 args 对象
            class StepArgs:
                def __init__(self, base_args, flow_step):
                    self.run = flow_step
                    self.work_path = base_args.work_path
                    self.project = base_args.project
                    self.version = base_args.version
                    self.block = base_args.block
                    self.user = base_args.user
                    self.branch = base_args.branch
                    self.foundry = base_args.foundry
                    self.node = base_args.node
                    self.dry_run = getattr(base_args, 'dry_run', False)
                    # debug 现在是布尔值，转换为整数
                    debug_flag = getattr(base_args, 'debug', False)
                    self.debug = 1 if debug_flag else 0
                    self.edp_center = base_args.edp_center
                    self.config = getattr(base_args, 'config', None)
            
            step_args = StepArgs(args, step_name)
            
            # 执行单个步骤
            result = execute_single_step(manager, step_args, step_name)
            
            # 更新步骤状态
            if result == 0:
                step.update_status(StepStatus.FINISHED)
                return True
            else:
                step.update_status(StepStatus.FAILED)
                return False
    
    # 使用事件驱动模式：步骤完成后立即检查并启动新的可执行步骤
    # 这样可以最大化并行度，提前发现问题
    dry_run = getattr(args, 'dry_run', False)
    failure_strategy = getattr(args, 'failure_strategy', 'strict')
    all_results = {}
    success_count = 0
    failed_steps = []
    should_stop = False  # stop 策略标志
    
    # 使用 ThreadPoolExecutor 进行事件驱动的并行执行
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from threading import Lock
    from edp_center.packages.edp_flowkit.flowkit.step import StepStatus
    
    executor = ThreadPoolExecutor(max_workers=None)  # 使用默认的并行数
    future_to_step = {}  # Future 到 Step 的映射
    lock = Lock()  # 保护共享状态
    
    def can_execute_step(step, failed_steps_set, strategy):
            """
            根据失败策略判断步骤是否可以执行
            
            Args:
                step: Step 对象
                failed_steps_set: 失败步骤名称集合
                strategy: 失败处理策略
                
            Returns:
                bool: 是否可以执行
            """
            prev_steps = graph.get_prev_steps(step.name)
            
            if not prev_steps:
                return True  # 没有前置步骤，可以执行
            
            failed_prereqs = [p for p in prev_steps if p.name in failed_steps_set]
            
            if strategy == "strict":
                # 所有前置必须成功
                return len(failed_prereqs) == 0
            
            elif strategy == "continue":
                # 即使前置失败也继续（会在执行时标记为 SKIPPED）
                return True
            
            elif strategy == "skip-downstream":
                # 如果所有前置都失败，则跳过
                # 如果至少有一个前置成功，则继续
                return len(failed_prereqs) < len(prev_steps)
            
            elif strategy == "stop":
                # stop 策略在步骤失败时设置标志，这里只检查前置
                return len(failed_prereqs) == 0
            
            return False
    
    def get_ready_steps_with_strategy(failed_steps_set, strategy):
            """
            根据失败策略获取可执行的步骤
            
            Args:
                failed_steps_set: 失败步骤名称集合
                strategy: 失败处理策略
                
            Returns:
                list: 可执行的步骤列表
            """
            ready_steps = []
            
            for step_name, step in graph.steps.items():
                # 检查步骤当前状态是否为INIT
                if step.status != StepStatus.INIT:
                    continue
                
                # 检查是否在要执行的步骤列表中
                if step_name not in steps_to_execute_set:
                    continue
                
                # 根据策略判断是否可以执行
                if can_execute_step(step, failed_steps_set, strategy):
                    ready_steps.append(step)
            
            return False
    
    def submit_ready_steps():
        """提交所有可执行的步骤到线程池"""
        with lock:
            if should_stop:
                return  # stop 策略：不再提交新步骤
            
            # 获取失败步骤集合
            failed_steps_set = set(failed_steps)
            
            # 根据策略获取可执行的步骤
            ready_steps = get_ready_steps_with_strategy(failed_steps_set, failure_strategy)
            
            # 过滤掉已经执行或正在执行的步骤
            ready_steps = [step for step in ready_steps 
                          if step.name not in all_results  # 避免重复提交
                          and step.name not in [s.name for s in future_to_step.values()]]  # 避免正在执行
            
            for step in ready_steps:
                # 检查前置步骤状态（用于 continue 策略的提示）
                prev_steps = graph.get_prev_steps(step.name)
                if prev_steps:
                    failed_prereqs = [p.name for p in prev_steps if p.name in failed_steps_set]
                    if failed_prereqs and failure_strategy in ["continue", "skip-downstream"]:
                        print(f"[WARN] 步骤 {step.name} 的前置步骤失败: {', '.join(failed_prereqs)}，但将继续执行（策略: {failure_strategy}）", file=sys.stderr)
                
                # 更新状态为运行中
                step.update_status(StepStatus.RUNNING)
                
                # 提交任务
                future = executor.submit(execute_step_func, step, {})
                future_to_step[future] = step
                
                print(f"[INFO] 启动步骤: {step.name}", file=sys.stderr)
    
    # 初始提交：启动所有初始可执行的步骤
    submit_ready_steps()
    
    # 事件驱动循环：每当一个步骤完成，立即检查并启动新的步骤
    while future_to_step:
        # 等待至少一个步骤完成（as_completed 会阻塞直到有步骤完成）
        # 注意：需要传入字典的 keys()，因为 as_completed 会迭代这些 Future
        for future in as_completed(list(future_to_step.keys())):
            # 从字典中移除（可能已经被其他线程移除）
            step = future_to_step.pop(future, None)
            if step is None:
                continue  # 已经被处理过了
            
            try:
                success = future.result()
                all_results[step.name] = success
                
                if success:
                    success_count += 1
                    print(f"[OK] 步骤 {step.name} 执行成功", file=sys.stderr)
                else:
                    failed_steps.append(step.name)
                    print(f"[ERROR] 步骤 {step.name} 执行失败", file=sys.stderr)
                    
                    # stop 策略：遇到第一个失败就停止
                    if failure_strategy == "stop":
                        print(f"[INFO] 使用 stop 策略：遇到失败，停止执行后续步骤", file=sys.stderr)
                        should_stop = True
                        # 取消所有正在执行的步骤
                        with lock:
                            for future_to_cancel in list(future_to_step.keys()):
                                future_to_cancel.cancel()
                
                # **关键**：步骤完成后，立即检查是否有新的步骤可以执行
                # 这就是事件驱动：不等待其他步骤，立即响应完成事件
                submit_ready_steps()
                
            except Exception as e:
                print(f"[ERROR] 执行步骤 {step.name} 时发生异常: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                if step:
                    step.update_status(StepStatus.FAILED)
                    all_results[step.name] = False
                    failed_steps.append(step.name)
                    
                    # stop 策略：遇到第一个失败就停止
                    if failure_strategy == "stop":
                        print(f"[INFO] 使用 stop 策略：遇到失败，停止执行后续步骤", file=sys.stderr)
                        should_stop = True
                        # 取消所有正在执行的步骤
                        with lock:
                            for future_to_cancel in list(future_to_step.keys()):
                                future_to_cancel.cancel()
                
                # 即使失败，也检查是否有新的步骤可以执行
                submit_ready_steps()
            
            # 处理完一个步骤后，跳出循环重新检查 future_to_step
            # 这样可以立即响应下一个完成事件，而不是等待所有步骤完成
            break
    
    # 关闭线程池
    executor.shutdown(wait=True)
    
    # 检查是否有未执行的步骤，并明确原因
    unexecuted_steps = [step_name for step_name in steps_to_execute 
                       if step_name in graph and graph[step_name].status == StepStatus.INIT]
    if unexecuted_steps:
        print(f"\n[WARN] 以下步骤未执行: {', '.join(unexecuted_steps)}", file=sys.stderr)
        
        # 分析未执行的原因
        failed_steps_set = set(failed_steps)
        for step_name in unexecuted_steps:
            step = graph.get_specific_step(step_name)
            if step:
                prev_steps = graph.get_prev_steps(step_name)
                if prev_steps:
                    # 检查前置步骤的状态
                    failed_prereqs = [prev.name for prev in prev_steps 
                                    if prev.name in failed_steps_set]
                    running_prereqs = [prev.name for prev in prev_steps 
                                      if prev.status == StepStatus.RUNNING]
                    
                    if failed_prereqs:
                        if failure_strategy == "skip-downstream":
                            # 检查是否因为所有前置都失败而被跳过
                            if len(failed_prereqs) == len(prev_steps):
                                print(f"[WARN]   {step_name}: 所有前置步骤失败，已跳过（策略: skip-downstream） - {', '.join(failed_prereqs)}", file=sys.stderr)
                            else:
                                print(f"[WARN]   {step_name}: 部分前置步骤失败 - {', '.join(failed_prereqs)}", file=sys.stderr)
                        else:
                            print(f"[WARN]   {step_name}: 前置步骤失败 - {', '.join(failed_prereqs)}", file=sys.stderr)
                    elif running_prereqs:
                        print(f"[WARN]   {step_name}: 前置步骤仍在运行 - {', '.join(running_prereqs)}", file=sys.stderr)
                    else:
                        print(f"[WARN]   {step_name}: 可能存在循环依赖或其他问题", file=sys.stderr)
                elif failure_strategy == "stop" and should_stop:
                    print(f"[WARN]   {step_name}: 因 stop 策略而停止执行", file=sys.stderr)
        
        # 将未执行的步骤也计入失败（因为它们没有完成）
        failed_steps.extend(unexecuted_steps)
    
    # 总结
    print(f"\n[INFO] ========== 执行完成 ==========", file=sys.stderr)
    print(f"[INFO] 成功: {success_count}/{len(steps_to_execute)}", file=sys.stderr)
    if failed_steps:
        print(f"[ERROR] 失败: {len(failed_steps)}/{len(steps_to_execute)}", file=sys.stderr)
        print(f"[ERROR] 失败的步骤: {', '.join(failed_steps)}", file=sys.stderr)
        return 1
    else:
        print(f"[OK] 所有步骤执行成功！", file=sys.stderr)
        return 0

