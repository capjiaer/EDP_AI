#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分支来源信息管理模块
"""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class BranchSource:
    """分支来源信息管理器"""
    
    @staticmethod
    def save_branch_source_info(branch_path: Path, from_branch_step: str,
                                 copy_info: Dict, link_mode: bool):
        """
        保存分支来源信息到隐藏文件
        
        Args:
            branch_path: 分支路径
            from_branch_step: 源分支步骤字符串
            copy_info: 复制/链接操作的详细信息
            link_mode: 是否为链接模式
        """
        import yaml
        
        # 创建分支来源信息
        source_info = {
            'created_at': datetime.now().isoformat(),
            'source': {
                'from_branch_step': from_branch_step,
                'source_user': copy_info.get('source_user'),
                'source_branch': copy_info.get('source_branch_name'),
                'source_branch_path': copy_info.get('source_branch'),
                'source_step': copy_info.get('source_step'),
                'step_name': copy_info.get('step_name')
            },
            'target': {
                'branch_path': str(branch_path),
                'target_step': copy_info.get('target_step')
            },
            'mode': {
                'link_mode': link_mode,
                'description': '符号链接模式（节省空间）' if link_mode else '复制模式（独立副本）'
            }
        }
        
        # 写入隐藏文件 .branch_source.yaml
        source_file = branch_path / '.branch_source.yaml'
        with open(source_file, 'w', encoding='utf-8') as f:
            yaml.dump(source_info, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    @staticmethod
    def get_branch_source_info(branch_path: Path) -> Optional[Dict]:
        """
        获取分支来源信息
        
        Args:
            branch_path: 分支路径
            
        Returns:
            分支来源信息字典，如果不存在则返回 None
        """
        import yaml
        
        source_file = branch_path / '.branch_source.yaml'
        
        if not source_file.exists():
            return None
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None

