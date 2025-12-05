#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志记录辅助函数
用于配合 EDP 异常包记录结构化日志
"""

import logging
from typing import Optional

try:
    from .exceptions import EDPError
except ImportError:
    # 向后兼容：如果 edp_common 不可用
    EDPError = Exception


def log_exception(logger: logging.Logger, error: EDPError, 
                  message: Optional[str] = None, include_traceback: bool = True):
    """
    记录 EDP 异常到日志
    
    Args:
        logger: Logger 对象
        error: EDP 异常对象
        message: 自定义消息（可选，默认使用 error.message）
        include_traceback: 是否包含堆栈跟踪
    """
    log_message = message or error.message
    
    # 获取异常的结构化信息，但避免与 LogRecord 的内置属性冲突
    error_dict = error.to_dict()
    # 移除 'message' 键，因为 LogRecord 已经有 message 属性
    # 如果需要，可以重命名为 'error_message'
    extra = {k: v for k, v in error_dict.items() if k != 'message'}
    if 'message' in error_dict:
        extra['error_message'] = error_dict['message']
    
    if include_traceback:
        # 使用 exception() 自动记录堆栈跟踪
        logger.exception(log_message, extra=extra if extra else None)
    else:
        # 只记录错误信息，不包含堆栈跟踪
        logger.error(log_message, extra=extra if extra else None)


def log_error_with_context(logger: logging.Logger, message: str, 
                           context: Optional[dict] = None, 
                           suggestion: Optional[str] = None,
                           level: int = logging.ERROR):
    """
    记录带上下文信息的错误日志
    
    Args:
        logger: Logger 对象
        message: 错误消息
        context: 错误上下文（字典）
        suggestion: 解决建议（字符串）
        level: 日志级别（默认 ERROR）
    """
    extra = {}
    if context:
        extra['context'] = context
    if suggestion:
        extra['suggestion'] = suggestion
    
    logger.log(level, message, extra=extra if extra else None)

