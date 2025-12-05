#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP 框架统一日志配置
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    统一配置 EDP 框架的日志系统
    
    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
              如果为 None，从环境变量 EDP_LOG_LEVEL 读取，默认为 INFO
        log_file: 日志文件路径（可选）
        format_string: 日志格式字符串（可选）
    
    Returns:
        配置好的根 logger
    """
    # 确定日志级别
    if level is None:
        level = os.environ.get('EDP_LOG_LEVEL', 'INFO').upper()
    
    log_level = getattr(logging, level, logging.INFO)
    
    # 确定日志格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(
        format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 获取根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 根 logger 设置为最低级别
    
    # 清除现有的处理器（避免重复添加）
    root_logger.handlers.clear()
    
    # 控制台处理器（输出到 stderr）
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的 logger（便捷函数）
    
    Args:
        name: logger 名称（通常是 __name__）
    
    Returns:
        Logger 对象
    """
    return logging.getLogger(name)

