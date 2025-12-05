#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
推断验证模块
提供推断结果验证功能
"""

from typing import Optional, Dict, List, Tuple


def validate_work_path_info(work_path_info: Optional[Dict], 
                            required_fields: List[str] = None) -> Tuple[bool, List[str]]:
    """
    验证工作路径信息是否完整
    
    Args:
        work_path_info: 工作路径信息字典
        required_fields: 必需字段列表，默认为 ['work_path', 'project', 'version', 'block', 'user', 'branch']
        
    Returns:
        (is_complete, missing_fields) 元组
    """
    if required_fields is None:
        required_fields = ['work_path', 'project', 'version', 'block', 'user', 'branch']
    
    if not work_path_info:
        return False, required_fields
    
    missing_fields = []
    for field in required_fields:
        if not work_path_info.get(field):
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields

