#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化模块
包含项目和工作空间初始化相关的功能
"""

from .params import (
    find_edp_version_file,
    infer_params_from_version_file,
    load_config_file,
    merge_params,
    validate_required_params,
    process_blocks_config
)
from .project_helpers import (
    init_project_structure,
    create_user_directories
)
from .validators import validate_init_permission
# 注意：infer_work_path_info 和 validate_work_path_info 在 utils 模块中，不在 init 模块中

__all__ = [
    'find_edp_version_file',
    'infer_params_from_version_file',
    'load_config_file',
    'merge_params',
    'validate_required_params',
    'process_blocks_config',
    'init_project_structure',
    'create_user_directories',
    'validate_init_permission',
    # 注意：infer_work_path_info 和 validate_work_path_info 在 utils 模块中
]

