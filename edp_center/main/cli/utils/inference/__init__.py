#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
推断模块
提供项目信息和路径信息的推断功能
"""

from .project_inference import (
    get_edp_center_path,
    list_projects_direct,
    infer_project_info_from_version_file,
    infer_project_info_from_path,
    infer_project_info as infer_project_info_func
)
from .path_inference import infer_work_path_info
from .inference_validator import validate_work_path_info

__all__ = [
    'get_edp_center_path',
    'list_projects_direct',
    'infer_project_info_from_version_file',
    'infer_project_info_from_path',
    'infer_project_info_func',
    'infer_work_path_info',
    'validate_work_path_info',
]

