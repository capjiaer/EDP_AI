#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一错误处理模块

提供装饰器和上下文管理器，统一框架的错误处理模式。
"""

import sys
import traceback
import functools
from typing import Optional, Callable, Any, Type
from contextlib import contextmanager

try:
    from .exceptions import EDPError
    from .logging_helpers import log_exception
except ImportError:
    # 向后兼容：如果 edp_common 不可用
    EDPError = Exception
    log_exception = None

import logging

logger = logging.getLogger(__name__)


def handle_error(
    error_message: Optional[str] = None,
    exit_code: int = 1,
    log_error: bool = True,
    reraise: bool = False,
    error_type: Optional[Type[Exception]] = None
):
    """
    错误处理装饰器
    
    统一处理函数中的异常，提供友好的错误输出和日志记录。
    
    Args:
        error_message: 自定义错误消息（可选）
        exit_code: 退出码（默认 1）
        log_error: 是否记录日志（默认 True）
        reraise: 是否重新抛出异常（默认 False）
        error_type: 只捕获特定类型的异常（默认捕获所有异常）
    
    Returns:
        装饰器函数
    
    Example:
        @handle_error(error_message="执行失败", exit_code=1)
        def my_function():
            # 如果这里抛出异常，会被统一处理
            raise ValueError("Something went wrong")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except error_type if error_type else Exception as e:
                # 格式化错误消息
                if error_message:
                    msg = f"{error_message}: {e}"
                else:
                    msg = str(e)
                
                # 输出到 stderr
                print(f"[ERROR] {msg}", file=sys.stderr)
                
                # 如果是 EDPError，使用其格式化输出
                if isinstance(e, EDPError):
                    print(str(e), file=sys.stderr)
                else:
                    # 其他异常打印堆栈跟踪
                    traceback.print_exc()
                
                # 记录日志
                if log_error and logger:
                    if isinstance(e, EDPError) and log_exception:
                        log_exception(logger, e)
                    else:
                        logger.exception(msg)
                
                # 重新抛出或返回退出码
                if reraise:
                    raise
                
                # 返回退出码（CLI 命令通常返回退出码）
                return exit_code
        
        return wrapper
    return decorator


@contextmanager
def error_context(
    error_message: Optional[str] = None,
    log_error: bool = True,
    reraise: bool = False,
    error_type: Optional[Type[Exception]] = None
):
    """
    错误处理上下文管理器
    
    统一处理代码块中的异常，提供友好的错误输出和日志记录。
    
    Args:
        error_message: 自定义错误消息（可选）
        log_error: 是否记录日志（默认 True）
        reraise: 是否重新抛出异常（默认 False）
        error_type: 只捕获特定类型的异常（默认捕获所有异常）
    
    Yields:
        None
    
    Example:
        with error_context(error_message="处理文件失败"):
            # 如果这里抛出异常，会被统一处理
            process_file()
    """
    try:
        yield
    except error_type if error_type else Exception as e:
        # 格式化错误消息
        if error_message:
            msg = f"{error_message}: {e}"
        else:
            msg = str(e)
        
        # 输出到 stderr
        print(f"[ERROR] {msg}", file=sys.stderr)
        
        # 如果是 EDPError，使用其格式化输出
        if isinstance(e, EDPError):
            print(str(e), file=sys.stderr)
        else:
            # 其他异常打印堆栈跟踪
            traceback.print_exc()
        
        # 记录日志
        if log_error and logger:
            if isinstance(e, EDPError) and log_exception:
                log_exception(logger, e)
            else:
                logger.exception(msg)
        
        # 重新抛出
        if reraise:
            raise


def handle_cli_error(
    func: Optional[Callable] = None,
    *,
    error_message: Optional[str] = None,
    exit_code: int = 1,
    log_error: bool = True
):
    """
    CLI 命令错误处理装饰器
    
    专门用于 CLI 命令函数，自动处理异常并返回退出码。
    
    Args:
        func: 被装饰的函数（如果作为装饰器使用）
        error_message: 自定义错误消息（可选）
        exit_code: 退出码（默认 1）
        log_error: 是否记录日志（默认 True）
    
    Returns:
        装饰器函数或装饰后的函数
    
    Example:
        @handle_cli_error(error_message="命令执行失败")
        def my_command(args):
            # CLI 命令逻辑
            return 0
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> int:
            try:
                result = f(*args, **kwargs)
                # 如果函数返回 int，直接返回
                if isinstance(result, int):
                    return result
                # 否则返回 0（成功）
                return 0
            except EDPError as e:
                # EDPError 已经有友好的格式化输出
                print(f"[ERROR] {e.message}", file=sys.stderr)
                print(str(e), file=sys.stderr)
                
                if log_error and logger and log_exception:
                    log_exception(logger, e)
                
                return exit_code
            except Exception as e:
                # 其他异常
                if error_message:
                    msg = f"{error_message}: {e}"
                else:
                    msg = str(e)
                
                print(f"[ERROR] {msg}", file=sys.stderr)
                traceback.print_exc()
                
                if log_error and logger:
                    logger.exception(msg)
                
                return exit_code
        
        return wrapper
    
    # 支持 @handle_cli_error 和 @handle_cli_error(...) 两种用法
    if func is None:
        return decorator
    else:
        return decorator(func)


def safe_call(
    func: Callable,
    *args,
    error_message: Optional[str] = None,
    default_return: Any = None,
    log_error: bool = True,
    **kwargs
) -> Any:
    """
    安全调用函数
    
    捕获异常并返回默认值，而不是抛出异常。
    
    Args:
        func: 要调用的函数
        *args: 函数位置参数
        error_message: 自定义错误消息（可选）
        default_return: 发生异常时的默认返回值（默认 None）
        log_error: 是否记录日志（默认 True）
        **kwargs: 函数关键字参数
    
    Returns:
        函数返回值或默认值
    
    Example:
        result = safe_call(risky_function, arg1, arg2, default_return=[])
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if error_message:
            msg = f"{error_message}: {e}"
        else:
            msg = f"调用 {func.__name__} 失败: {e}"
        
        if log_error and logger:
            logger.warning(msg, exc_info=True)
        
        return default_return

