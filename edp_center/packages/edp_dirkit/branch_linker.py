#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分支链接模块
"""

from pathlib import Path
from typing import Dict
from .dirkit import DirKit
from .branch_step_parser import BranchStepParser

# 导入框架异常类
from edp_center.packages.edp_common import WorkflowError, ValidationError


class BranchLinker:
    """分支链接器"""
    
    def __init__(self):
        """初始化 BranchLinker"""
        self.parser = BranchStepParser()
    
    def copy_step_from_branch(self, work_path: Path, project_name: str,
                              project_node: str, block_name: str,
                              from_branch_step: str, target_branch_path: Path,
                              current_user: str, link_mode: bool = True) -> Dict[str, Path]:
        """
        从源分支复制或链接指定步骤的输出到目标分支
        
        Args:
            work_path: WORK_PATH 根目录
            project_name: 项目名称
            project_node: 项目节点名称
            block_name: 块名称
            from_branch_step: 源分支步骤字符串（格式：'branch.step' 或 'user.branch.step'）
            target_branch_path: 目标分支路径
            current_user: 当前用户名
            link_mode: 如果为 True，使用符号链接而不是复制（适用于大文件，节省空间）
                      默认 True（链接模式），使用递归目录链接
            
        Returns:
            包含复制/链接操作的详细信息
            
        Raises:
            ValueError: 如果源分支或步骤不存在
        """
        # 解析 from_branch_step
        source_user, source_branch, step_name = self.parser.parse_from_branch_step(
            from_branch_step, current_user
        )
        
        # 构建源分支路径
        source_branch_path = work_path / project_name / project_node / block_name / source_user / source_branch
        
        if not source_branch_path.exists():
            raise WorkflowError(
                message=f"源分支不存在: {source_branch_path}",
                step_name=step_name,
                context={
                    'source_branch': source_branch,
                    'source_user': source_user,
                    'expected_path': f"WORK_PATH/{project_name}/{project_node}/{block_name}/{source_user}/{source_branch}"
                },
                suggestion=(
                    f"请确保分支路径正确: WORK_PATH/{project_name}/{project_node}/{block_name}/{source_user}/{source_branch}\n"
                    "使用 'edp -b <branch_name>' 创建新分支"
                )
            )
        
        # 步骤输出在 runs/{flow_name}.{step_name}/ 目录中（统一格式）
        # 例如：pnr_innovus.place -> runs/pnr_innovus.place/
        # 统一使用 flow_name.step_name 格式（与 path_builder.py 保持一致）
        step_path = step_name  # step_name 已经是 flow_name.step_name 格式
        source_step_path = source_branch_path / "runs" / step_path
        
        if not source_step_path.exists():
            raise WorkflowError(
                message=f"源步骤输出不存在: {source_step_path}",
                step_name=step_name,
                context={
                    'source_branch': source_branch,
                    'step_path': step_path,
                    'expected_path': str(source_step_path)
                },
                suggestion=(
                    f"请确保步骤 '{step_name}' (路径: {step_path}) 已在该分支运行完成。\n"
                    f"使用 'edp -run {step_name}' 在源分支运行该步骤"
                )
            )
        
        # 目标步骤路径
        target_step_path = target_branch_path / "runs" / step_path
        
        # 确保目标目录存在
        target_step_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 DirKit 复制或链接步骤输出（不使用 base_path，直接使用绝对路径）
        dirkit = DirKit()
        
        # 根据 link_mode 选择复制或链接
        if link_mode:
            # 使用符号链接模式（节省空间，适用于大文件）
            # 使用递归目录链接：目录本身是链接，这样可以节省空间
            # 用户如果需要修改文件，可以在文件层面处理
            if source_step_path.is_dir():
                dirkit.link_dir(str(source_step_path), str(target_step_path), overwrite=True)
            else:
                # 如果是文件，直接链接
                dirkit.link_file(str(source_step_path), str(target_step_path), overwrite=True)
        else:
            # 使用复制模式（独立副本）
            if source_step_path.is_dir():
                dirkit.copy_dir(str(source_step_path), str(target_step_path), overwrite=True)
            else:
                # 如果是文件，直接复制
                dirkit.copy_file(str(source_step_path), str(target_step_path), overwrite=True)
        
        return {
            'source_branch': str(source_branch_path),
            'source_user': source_user,
            'source_branch_name': source_branch,
            'source_step': str(source_step_path),
            'target_step': str(target_step_path),
            'step_name': step_name,
            'step_path': step_path  # 分级路径，如 pnr_innovus/init
        }
    
    def link_other_dirs_from_branch(self, source_branch_path: Path,
                                     target_branch_path: Path,
                                     link_mode: bool = True) -> Dict[str, Dict]:
        """
        从源分支递归链接/复制其他目录（cmds, dbs, flow, hooks, logs, rpts）
        
        注意：runs 目录不在此处处理，由 copy_step_from_branch 单独处理
        
        Args:
            source_branch_path: 源分支路径
            target_branch_path: 目标分支路径
            link_mode: 如果为 True，使用符号链接（默认）；如果为 False，使用复制
            
        Returns:
            包含链接/复制的目录信息
        """
        dirkit = DirKit()
        linked_dirs = {}
        
        # 需要链接的目录（排除 runs，因为已经特殊处理了）
        dirs_to_link = ['cmds', 'dbs', 'flow', 'hooks', 'logs', 'rpts']
        
        for dir_name in dirs_to_link:
            source_dir = source_branch_path / dir_name
            target_dir = target_branch_path / dir_name
            
            # 如果源目录存在，进行链接/复制
            if source_dir.exists() and source_dir.is_dir():
                try:
                    if link_mode:
                        # 使用符号链接（递归链接整个目录）
                        dirkit.link_dir(str(source_dir), str(target_dir), overwrite=True)
                        linked_dirs[dir_name] = {
                            'path': str(target_dir),
                            'type': 'symlink',
                            'source': str(source_dir)
                        }
                    else:
                        # 使用复制（递归复制整个目录）
                        dirkit.copy_dir(str(source_dir), str(target_dir), overwrite=True)
                        linked_dirs[dir_name] = {
                            'path': str(target_dir),
                            'type': 'copy',
                            'source': str(source_dir)
                        }
                except Exception as e:
                    # 如果链接/复制失败，记录错误但继续处理其他目录
                    print(f"警告: 无法链接/复制目录 {dir_name}: {e}")
                    linked_dirs[dir_name] = {
                        'path': str(target_dir),
                        'type': 'error',
                        'error': str(e)
                    }
            else:
                # 源目录不存在，跳过
                linked_dirs[dir_name] = {
                    'path': str(target_dir),
                    'type': 'skipped',
                    'reason': '源目录不存在'
                }
        
        return linked_dirs

