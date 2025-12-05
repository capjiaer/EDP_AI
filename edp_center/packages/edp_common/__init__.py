#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP Common - 公共模块
提供框架通用的功能和异常类
"""

from .exceptions import (
    EDPError,
    ConfigError,
    FileNotFoundError as EDPFileNotFoundError,
    ProjectNotFoundError,
    WorkflowError,
    ValidationError
)
from .logging_config import setup_logging, get_logger
from .logging_helpers import log_exception, log_error_with_context
from .error_handler import (
    handle_error,
    error_context,
    handle_cli_error,
    safe_call
)
from .path_utils import to_tcl_path, sanitize_filename, generate_log_filename, ensure_dir

__all__ = [
    'EDPError',
    'ConfigError',
    'EDPFileNotFoundError',
    'ProjectNotFoundError',
    'WorkflowError',
    'ValidationError',
    'setup_logging',
    'get_logger',
    'log_exception',
    'log_error_with_context',
    'handle_error',
    'error_context',
    'handle_cli_error',
    'safe_call',
    'to_tcl_path',
    'sanitize_filename',
    'generate_log_filename',
    'ensure_dir'
]

