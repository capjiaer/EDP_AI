#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Step Executor - 步骤执行模块

负责执行步骤，包括终端模式和日志文件模式。
"""

import threading
import time
from pathlib import Path
from typing import Dict
from argparse import Namespace

from ....workflow_manager import WorkflowManager
from ...commands.run_single_step import execute_single_step
from ...utils.param_inference import prepare_execution_args
from .terminal_executor import open_terminal_and_execute
from .log_handler import (
    create_log_file,
    setup_log_redirect,
    restore_log_redirect,
    read_log_content,
    write_log_header,
    write_log_footer
)


def execute_step(manager: WorkflowManager, step_name: str, 
                 step_status: Dict, execution_threads: Dict,
                 debug_mode: int = 0, use_terminal: bool = True) -> None:
    """
    执行步骤（在后台线程中或新终端中）
    
    Args:
        manager: WorkflowManager 实例
        step_name: 步骤名称
        step_status: 步骤状态字典
        execution_threads: 执行线程字典
        debug_mode: Debug 模式
        use_terminal: 是否使用新终端窗口执行（默认 True）
    """
    # 如果使用终端模式，尝试在新终端中执行
    if use_terminal:
        work_dir = Path.cwd()
        edp_center_path = manager.edp_center if manager else None
        if open_terminal_and_execute(step_name, work_dir, debug_mode, edp_center_path):
            # 成功启动终端，设置状态为运行中
            step_status[step_name] = {
                'status': 'running',
                'message': f'已在独立终端中启动执行: {step_name}',
                'terminal_mode': True
            }
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=_monitor_terminal_execution,
                args=(step_name, step_status)
            )
            monitor_thread.daemon = True
            execution_threads[step_name] = monitor_thread
            monitor_thread.start()
            return
    
    # 如果不使用终端或终端启动失败，回退到日志文件模式
    thread = threading.Thread(
        target=_execute_in_thread,
        args=(manager, step_name, step_status, execution_threads, debug_mode)
    )
    thread.daemon = True
    execution_threads[step_name] = thread
    thread.start()


def _monitor_terminal_execution(step_name: str, step_status: Dict):
    """
    监控终端中的执行状态
    
    Args:
        step_name: 步骤名称
        step_status: 步骤状态字典
    """
    # 等待一段时间后开始检查
    time.sleep(2)
    
    # 通过检查日志文件或 .run_info 来判断执行状态
    # 这里简化处理，设置一个较长的等待时间
    max_wait_time = 3600  # 最多等待1小时
    check_interval = 5  # 每5秒检查一次
    elapsed = 0
    
    while elapsed < max_wait_time:
        time.sleep(check_interval)
        elapsed += check_interval
        
        # 检查步骤是否已完成（通过检查日志文件或状态文件）
        # 这里需要根据实际的状态检查逻辑来实现
        # 暂时保持运行状态，由用户手动刷新或前端轮询来更新
        
        # 如果步骤状态被外部更新（如用户手动刷新），退出监控
        if step_name in step_status:
            current_status = step_status[step_name].get('status')
            if current_status in ['success', 'failed']:
                break
    
    # 如果超时仍未检测到完成，保持运行状态
    if step_name in step_status and step_status[step_name].get('status') == 'running':
        step_status[step_name]['message'] = '执行中（请查看终端窗口或刷新状态）'


def _execute_in_thread(manager: WorkflowManager, step_name: str,
                       step_status: Dict, execution_threads: Dict,
                       debug_mode: int):
    """
    在线程中执行步骤（日志文件模式）
    
    Args:
        manager: WorkflowManager 实例
        step_name: 步骤名称
        step_status: 步骤状态字典
        execution_threads: 执行线程字典
        debug_mode: Debug 模式
    """
    step_status[step_name] = {'status': 'running', 'message': '执行中...'}
    
    # 创建日志文件
    log_file = create_log_file(step_name)
    
    # 设置日志重定向
    log_file_handle, old_stdout, old_stderr, tee_stdout, tee_stderr = setup_log_redirect(log_file)
    
    try:
        # 写入日志头部
        write_log_header(step_name, debug_mode)
        
        # 准备参数
        args = _prepare_execution_args(manager, debug_mode)
        
        # 执行步骤
        exit_code = execute_single_step(manager, args, step_name)
        
        # 写入日志尾部
        write_log_footer(step_name, exit_code)
        
        # 恢复输出
        restore_log_redirect(log_file_handle, old_stdout, old_stderr)
        
        # 读取日志内容
        log_content = read_log_content(log_file, tee_stdout.getvalue() + tee_stderr.getvalue())
        
        # 更新状态
        if exit_code == 0:
            step_status[step_name] = {
                'status': 'success',
                'message': '执行成功',
                'log_file': str(log_file),
                'log_content': log_content
            }
        else:
            step_status[step_name] = {
                'status': 'failed',
                'exit_code': exit_code,
                'message': f'执行失败 (退出码: {exit_code})',
                'log_file': str(log_file),
                'log_content': log_content
            }
    except Exception as e:
        # 恢复输出
        restore_log_redirect(log_file_handle, old_stdout, old_stderr)
        
        # 读取日志内容
        log_content = read_log_content(log_file, f"执行异常: {str(e)}\n")
        
        # 更新状态
        step_status[step_name] = {
            'status': 'failed',
            'error': str(e),
            'message': f'执行异常: {str(e)}',
            'log_file': str(log_file),
            'log_content': log_content
        }
    finally:
        if step_name in execution_threads:
            del execution_threads[step_name]


def _prepare_execution_args(manager: WorkflowManager, debug_mode: int) -> Namespace:
    """
    准备执行参数
    
    Args:
        manager: WorkflowManager 实例
        debug_mode: Debug 模式
    
    Returns:
        Namespace 对象，包含执行所需的参数
    """
    # 使用统一的参数准备逻辑
    return prepare_execution_args(manager, debug_mode)

