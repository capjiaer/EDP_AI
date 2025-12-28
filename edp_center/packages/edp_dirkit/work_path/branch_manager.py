#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Branch Manager - 分支管理模块
"""

from pathlib import Path
from typing import Optional, Dict, Union, List
import logging
from ..dirkit import DirKit

logger = logging.getLogger(__name__)


class BranchManager:
    """分支管理器"""
    
    # 默认的分支目录结构
    # 注意：实际项目中使用的目录是 cmds, data, hooks, runs
    # logs 和 rpts 会在运行时自动创建，不需要在 init 时创建
    DEFAULT_BRANCH_DIRS = ['cmds', 'data', 'hooks', 'runs']
    
    # 默认的分支文件
    DEFAULT_BRANCH_FILES = ['user_config.tcl', 'user_config.yaml']
    
    def create_branch_structure(self, branch_path: Union[str, Path],
                               branch_template: Optional[Dict] = None) -> Dict[str, Path]:
        """
        创建分支目录结构
        
        Args:
            branch_path: 分支路径（如 WORK_PATH/dongting/P85/block1/user1/branch1）
            branch_template: 分支模板配置（如果为 None，使用默认模板）
            
        Returns:
            包含创建的目录和文件路径的字典
        """
        branch_path = Path(branch_path).resolve()
        dirkit = DirKit(base_path=branch_path.parent)
        
        created = {}
        
        # 确定要创建的目录和文件
        if branch_template:
            branch_dirs = branch_template.get('directories', self.DEFAULT_BRANCH_DIRS)
            branch_files = branch_template.get('files', self.DEFAULT_BRANCH_FILES)
        else:
            branch_dirs = self.DEFAULT_BRANCH_DIRS
            branch_files = self.DEFAULT_BRANCH_FILES
        
        # 确保分支目录存在
        branch_path.mkdir(parents=True, exist_ok=True)
        
        # 创建目录
        created_dirs = {}
        for dir_name in branch_dirs:
            dir_path = branch_path / dir_name
            dirkit.ensure_dir(dir_path)
            created_dirs[dir_name] = dir_path
        created['directories'] = created_dirs
        
        # 创建文件（空文件）
        created_files = {}
        for file_name in branch_files:
            file_path = branch_path / file_name
            if not file_path.exists():
                file_path.touch()
            created_files[file_name] = file_path
        created['files'] = created_files
        created['branch_path'] = branch_path
        
        return created
    
    def create_hooks_files(self, branch_path: Union[str, Path],
                          edp_center_path: Optional[Union[str, Path]] = None,
                          foundry: Optional[str] = None,
                          node: Optional[str] = None,
                          project: Optional[str] = None) -> Dict[str, List[Path]]:
        """
        自动创建所有 hooks 文件（空文件）
        
        从所有 flow 的 dependency.yaml 中提取 step 和 sub_step，自动创建对应的 hooks 文件。
        
        Args:
            branch_path: 分支路径
            edp_center_path: edp_center 路径（可选，如果为 None 则不创建 hooks）
            foundry: 代工厂名称（可选）
            node: 工艺节点（可选）
            project: 项目名称（可选）
        
        Returns:
            包含创建的 hooks 文件路径的字典 {'step_hooks': [...], 'sub_step_hooks': [...]}
        """
        branch_path = Path(branch_path).resolve()
        hooks_dir = branch_path / 'hooks'
        
        created = {
            'step_hooks': [],
            'sub_step_hooks': []
        }
        
        # 如果没有提供必要信息，跳过创建 hooks
        if not edp_center_path or not foundry or not node:
            logger.debug("缺少必要信息，跳过自动创建 hooks 文件")
            return created
        
        edp_center_path = Path(edp_center_path).resolve()
        if not hooks_dir.exists():
            hooks_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 导入必要的模块
            from edp_center.main.cli.utils.dependency_parser import list_available_flows
            from edp_center.packages.edp_cmdkit.sub_steps.reader import read_sub_steps_from_dependency
            
            # 获取所有 flow
            flows = list_available_flows(edp_center_path, foundry, node, project)
            
            # 遍历所有 flow 和 step
            for flow_name, steps_info in flows.items():
                # 为每个 step 创建 step.pre 和 step.post
                for step_name in steps_info.keys():
                    step_hooks_dir = hooks_dir / f"{flow_name}.{step_name}"
                    step_hooks_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 创建 step.pre
                    step_pre_file = step_hooks_dir / 'step.pre'
                    if not step_pre_file.exists():
                        step_pre_file.touch()
                        created['step_hooks'].append(step_pre_file)
                        logger.debug(f"创建 step.pre hook: {step_pre_file}")
                    
                    # 创建 step.post
                    step_post_file = step_hooks_dir / 'step.post'
                    if not step_post_file.exists():
                        step_post_file.touch()
                        created['step_hooks'].append(step_post_file)
                        logger.debug(f"创建 step.post hook: {step_post_file}")
                    
                    # 读取 sub_steps
                    try:
                        sub_steps = read_sub_steps_from_dependency(
                            edp_center_path, foundry, node, project, flow_name, step_name
                        )
                        
                        # 为每个 sub_step 创建 hooks 文件
                        for sub_step in sub_steps:
                            if isinstance(sub_step, dict) and len(sub_step) == 1:
                                file_name, proc_name = next(iter(sub_step.items()))
                                
                                # 确保文件名有 .tcl 扩展名
                                if not file_name.endswith('.tcl'):
                                    file_name = file_name + '.tcl'
                                
                                # 创建 sub_step.pre（推荐方式：完整文件名）
                                sub_pre_file = step_hooks_dir / f"{file_name}.pre"
                                if not sub_pre_file.exists():
                                    sub_pre_file.touch()
                                    created['sub_step_hooks'].append(sub_pre_file)
                                    logger.debug(f"创建 sub_step.pre hook: {sub_pre_file}")
                                
                                # 创建 sub_step.post（推荐方式：完整文件名）
                                sub_post_file = step_hooks_dir / f"{file_name}.post"
                                if not sub_post_file.exists():
                                    sub_post_file.touch()
                                    created['sub_step_hooks'].append(sub_post_file)
                                    logger.debug(f"创建 sub_step.post hook: {sub_post_file}")
                                
                                # 创建 sub_step.replace（推荐方式：完整文件名）
                                sub_replace_file = step_hooks_dir / f"{file_name}.replace"
                                if not sub_replace_file.exists():
                                    sub_replace_file.touch()
                                    created['sub_step_hooks'].append(sub_replace_file)
                                    logger.debug(f"创建 sub_step.replace hook: {sub_replace_file}")
                    
                    except Exception as e:
                        # 如果读取 sub_steps 失败，继续处理下一个 step
                        logger.warning(f"读取 {flow_name}.{step_name} 的 sub_steps 失败: {e}")
                        continue
        
        except Exception as e:
            # 如果创建 hooks 失败，记录警告但不影响分支创建
            logger.warning(f"自动创建 hooks 文件时出错: {e}，但分支创建继续")
        
        return created

