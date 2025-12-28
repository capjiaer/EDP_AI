#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Config Loader - 配置加载模块
"""

from pathlib import Path
from typing import Optional, Dict

try:
    from edp_center.packages.edp_configkit import files2dict
except ImportError:
    # 如果 configkit 不可用，提供一个简单的 fallback
    import yaml
    def files2dict(*files):
        result = {}
        for file in files:
            if Path(file).exists():
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    result.update(data)
        return result


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Path):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置目录路径
        """
        self.config_path = config_path
    
    def load_init_project_config(self, foundry: str, node: str, 
                                  project: str) -> Optional[Dict]:
        """
        加载 init_project 配置文件
        
        按优先级加载：
        1. common/main/init_project.yaml
        2. {project}/main/init_project.yaml
        
        Args:
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称
            
        Returns:
            合并后的配置字典，如果不存在则返回 None
        """
        config_files = []
        
        # 1. common/main/init_project.yaml
        common_init_file = (self.config_path / foundry / node / "common" / 
                           "main" / "init_project.yaml")
        if common_init_file.exists():
            config_files.append(common_init_file)
        
        # 2. {project}/main/init_project.yaml
        project_init_file = (self.config_path / foundry / node / project / 
                           "main" / "init_project.yaml")
        if project_init_file.exists():
            config_files.append(project_init_file)
        
        if config_files:
            return files2dict(*config_files)
        
        return None

