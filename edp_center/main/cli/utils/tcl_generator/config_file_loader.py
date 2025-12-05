#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件路径构建模块
负责构建所有 YAML 配置文件路径（按优先级顺序）
"""

from pathlib import Path
from typing import Optional, Dict


def build_config_file_paths(edp_center_path: Path, foundry: str, node: str, project: Optional[str],
                            work_path_info: Optional[Dict], flow_name: str,
                            current_dir: Optional[Path] = None) -> list:
    """
    构建所有 YAML 配置文件路径（按优先级顺序）
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        work_path_info: 工作路径信息字典（可选）
        flow_name: 流程名称
        current_dir: 当前目录（可选，用于查找 user_config.yaml）
        
    Returns:
        配置文件路径列表
    """
    config_files = []
    
    # 1. common/main/init_project.yaml
    common_init = edp_center_path / 'config' / foundry / node / 'common' / 'main' / 'init_project.yaml'
    if common_init.exists():
        config_files.append(str(common_init))
    
    # 2. common/main/config.yaml
    common_config = edp_center_path / 'config' / foundry / node / 'common' / 'main' / 'config.yaml'
    if common_config.exists():
        config_files.append(str(common_config))
    
    # 3. common/{flow_name}/config.yaml
    common_flow_config = edp_center_path / 'config' / foundry / node / 'common' / flow_name / 'config.yaml'
    if common_flow_config.exists():
        config_files.append(str(common_flow_config))
    
    # 4. {project}/main/init_project.yaml
    if project:
        project_init = edp_center_path / 'config' / foundry / node / project / 'main' / 'init_project.yaml'
        if project_init.exists():
            config_files.append(str(project_init))
    
    # 5. {project}/main/config.yaml
    if project:
        project_config = edp_center_path / 'config' / foundry / node / project / 'main' / 'config.yaml'
        if project_config.exists():
            config_files.append(str(project_config))
    
    # 6. {project}/{flow_name}/config.yaml
    if project:
        project_flow_config = edp_center_path / 'config' / foundry / node / project / flow_name / 'config.yaml'
        if project_flow_config.exists():
            config_files.append(str(project_flow_config))
    
    # 7. branch 里面的 config.yaml（优先 user_config.yaml）
    # 尝试从 work_path_info 构建完整路径
    branch_config_added = False
    if work_path_info and work_path_info.get('work_path') and work_path_info.get('project') and \
       work_path_info.get('version'):
        work_path = work_path_info['work_path']
        project = work_path_info['project']
        version = work_path_info.get('version')
        block = work_path_info.get('block')
        user = work_path_info.get('user')
        branch = work_path_info.get('branch')
        
        # 如果 work_path_info 完整（包含所有字段），尝试从完整路径查找
        if block and user and branch:
            branch_dir = work_path / project / version / block / user / branch
            
            # 优先使用 user_config.yaml
            user_config_yaml = branch_dir / 'user_config.yaml'
            if user_config_yaml.exists():
                config_files.append(str(user_config_yaml))
                branch_config_added = True
            else:
                # 如果找不到 user_config.yaml，尝试查找 user_config.tcl
                user_config_tcl = branch_dir / 'user_config.tcl'
                if user_config_tcl.exists():
                    config_files.append(str(user_config_tcl))
                    branch_config_added = True
                else:
                    # 否则使用 config.yaml
                    branch_config = branch_dir / 'config.yaml'
                    if branch_config.exists():
                        config_files.append(str(branch_config))
                        branch_config_added = True
    
    # 如果无法从 work_path_info 推断完整路径，或者从 work_path_info 推断的路径不存在，
    # 尝试从当前目录查找 user_config.yaml
    # 这种情况可能发生在用户从 branch 目录运行命令时，或者 work_path_info 不完整
    if not branch_config_added:
        if current_dir is None:
            current_dir = Path.cwd()
        
        # 尝试从当前目录及其父目录查找 user_config.yaml
        search_dir = current_dir
        # 向上搜索最多 5 层，找到 user_config.yaml、user_config.tcl 或 config.yaml
        for _ in range(5):
            potential_user_config_yaml = search_dir / 'user_config.yaml'
            if potential_user_config_yaml.exists():
                config_files.append(str(potential_user_config_yaml))
                break
            potential_user_config_tcl = search_dir / 'user_config.tcl'
            if potential_user_config_tcl.exists():
                config_files.append(str(potential_user_config_tcl))
                break
            potential_config = search_dir / 'config.yaml'
            if potential_config.exists():
                config_files.append(str(potential_config))
                break
            # 如果已经到达根目录，停止搜索
            if search_dir == search_dir.parent:
                break
            search_dir = search_dir.parent
    
    return config_files

