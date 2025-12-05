#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Log Handler - 日志处理模块

负责日志文件的创建、写入和读取。
"""

import sys
from pathlib import Path
from io import StringIO
from datetime import datetime
from typing import Optional

from edp_center.packages.edp_common.path_utils import generate_log_filename


class TeeOutput:
    """同时写入文件和捕获内容的输出类"""
    
    def __init__(self, file_handle, original_stream):
        self.file_handle = file_handle
        self.original_stream = original_stream
        self.buffer = StringIO()
    
    def write(self, text):
        """写入文件并保存到缓冲区"""
        # 写入文件
        self.file_handle.write(text)
        self.file_handle.flush()
        # 保存到缓冲区
        self.buffer.write(text)
        # 不写入原始流（避免混在服务器日志中）
    
    def flush(self):
        """刷新文件句柄和原始流"""
        self.file_handle.flush()
        self.original_stream.flush()
    
    def getvalue(self):
        """获取缓冲区内容"""
        return self.buffer.getvalue()


def create_log_file(step_name: str, base_dir: Optional[Path] = None) -> Path:
    """
    创建日志文件
    
    Args:
        step_name: 步骤名称
        base_dir: 基础目录（默认：当前目录）
    
    Returns:
        日志文件路径
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    log_dir = base_dir / '.edp_web_logs'
    log_dir.mkdir(exist_ok=True)
    
    # 使用统一的日志文件名生成逻辑
    log_filename = generate_log_filename(step_name)
    log_file = log_dir / log_filename
    
    return log_file


def setup_log_redirect(log_file: Path) -> tuple:
    """
    设置日志重定向
    
    Args:
        log_file: 日志文件路径
    
    Returns:
        (log_file_handle, old_stdout, old_stderr, tee_stdout, tee_stderr) 元组
    """
    log_file_handle = open(log_file, 'w', encoding='utf-8')
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    tee_stdout = TeeOutput(log_file_handle, old_stdout)
    tee_stderr = TeeOutput(log_file_handle, old_stderr)
    
    sys.stdout = tee_stdout
    sys.stderr = tee_stderr
    
    return log_file_handle, old_stdout, old_stderr, tee_stdout, tee_stderr


def restore_log_redirect(log_file_handle, old_stdout, old_stderr):
    """
    恢复日志重定向
    
    Args:
        log_file_handle: 日志文件句柄
        old_stdout: 原始 stdout
        old_stderr: 原始 stderr
    """
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    if not log_file_handle.closed:
        log_file_handle.close()


def read_log_content(log_file: Path, fallback_content: Optional[str] = None) -> str:
    """
    读取日志文件内容
    
    Args:
        log_file: 日志文件路径
        fallback_content: 如果读取失败，返回的备用内容
    
    Returns:
        日志内容字符串
    """
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return fallback_content or ""


def write_log_header(step_name: str, debug_mode: int = 0):
    """
    写入日志头部信息
    
    Args:
        step_name: 步骤名称
        debug_mode: Debug 模式
    """
    print(f"[EDP_WEB] 开始执行步骤: {step_name}")
    print(f"[EDP_WEB] 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[EDP_WEB] Debug 模式: {debug_mode}")
    print("=" * 80)


def write_log_footer(step_name: str, exit_code: int):
    """
    写入日志尾部信息
    
    Args:
        step_name: 步骤名称
        exit_code: 退出码
    """
    print("=" * 80)
    if exit_code == 0:
        print(f"[EDP_WEB] 执行成功: {step_name}")
    else:
        print(f"[EDP_WEB] 执行失败: {step_name} (退出码: {exit_code})")

