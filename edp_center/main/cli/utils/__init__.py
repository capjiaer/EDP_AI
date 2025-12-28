#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具模块
包含各种工具函数和辅助类
"""

from .cli_utils import get_current_user, set_user_directory_permissions
# 直接从 unified_inference 导入（移除 path_inference 中间层）
from .unified_inference import (
    UnifiedInference,
    infer_project_info,
    infer_work_path_info,
    validate_work_path_info
)
from .script_finders import find_source_script
# 直接从源模块导入（移除 config_helpers 中间层）
from .full_tcl_generator import generate_full_tcl
from .dependency_parser import (
    list_available_flows,
    find_step_flow,
    get_cmd_filename_from_dependency
)
from .param_inference import (
    create_default_args,
    infer_all_params,
    get_foundry_node,
    prepare_execution_args
)
from .command_helpers import (
    get_current_dir,
    infer_and_validate_project_info,
    infer_and_validate_work_path_info,
    build_branch_dir,
    infer_all_info
)

__all__ = [
    'get_current_user',
    'set_user_directory_permissions',
    'infer_project_info',
    'infer_work_path_info',
    'validate_work_path_info',
    'find_source_script',
    'UnifiedInference',
    'generate_full_tcl',
    'list_available_flows',
    'get_cmd_filename_from_dependency',
    'find_step_flow',
    'create_default_args',
    'infer_all_params',
    'get_foundry_node',
    'prepare_execution_args',
    'get_current_dir',
    'infer_and_validate_project_info',
    'infer_and_validate_work_path_info',
    'build_branch_dir',
    'infer_all_info',
]

