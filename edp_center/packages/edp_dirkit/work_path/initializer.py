#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WorkPathInitializer - 工作路径初始化工具主类

用于在 WORK_PATH 下初始化项目结构，包括项目节点（P85/P90等）和块（block1/block2等）。
"""

from pathlib import Path
from typing import Optional, List, Dict, Union
import logging
from .utils import get_current_user
from .config_loader import ConfigLoader
from .version_info import VersionInfoManager
from .branch_manager import BranchManager
from ..dirkit import DirKit
from ..initializer import ProjectInitializer
from ..project_finder import ProjectFinder
from ..path_detector import PathDetector
from ..branch_step_parser import BranchStepParser
from ..branch_linker import BranchLinker
from ..branch_source import BranchSource

# 导入框架异常类
from edp_center.packages.edp_common import EDPError, EDPFileNotFoundError, ProjectNotFoundError

logger = logging.getLogger(__name__)


class WorkPathInitializer:
    """工作路径初始化器"""
    
    def __init__(self, edp_center_path: Union[str, Path]):
        """
        初始化 WorkPathInitializer
        
        Args:
            edp_center_path: edp_center 资源库的路径
        """
        self.edp_center = Path(edp_center_path)
        if not self.edp_center.exists():
            raise EDPFileNotFoundError(
                file_path=str(edp_center_path),
                suggestion=(
                    "1. 检查 EDP Center 路径是否正确\n"
                    "2. 使用 'edp -init' 初始化项目\n"
                    "3. 或使用环境变量 EDP_CENTER_PATH 指定路径"
                )
            )
        
        self.config_path = self.edp_center / "config"
        self.initializer = ProjectInitializer(edp_center_path)
        
        # 初始化各个功能模块
        self.project_finder = ProjectFinder(self.config_path)
        self.path_detector = PathDetector(self.config_path)
        self.branch_parser = BranchStepParser()
        self.branch_linker = BranchLinker()
        self.branch_source = BranchSource()
        
        # 初始化新的模块
        self.config_loader = ConfigLoader(self.config_path)
        self.branch_manager = BranchManager()
    
    def find_project(self, project_name: str) -> List[Dict[str, str]]:
        """根据项目名称查找所有匹配的 foundry/node 组合"""
        return self.project_finder.find_project(project_name)
    
    def get_project_info(self, project_name: str, 
                         foundry: Optional[str] = None,
                         node: Optional[str] = None) -> Dict[str, str]:
        """获取项目信息（foundry 和 node）"""
        return self.project_finder.get_project_info(project_name, foundry, node)
    
    def list_projects(self, foundry: Optional[str] = None, 
                     node: Optional[str] = None) -> List[Dict[str, str]]:
        """列出所有可用的项目"""
        return self.project_finder.list_projects(foundry, node)
    
    def init_project(self, work_path: Union[str, Path],
                     project_name: str,
                     project_node: str,
                     blocks: Optional[List[str]] = None,
                     foundry: Optional[str] = None,
                     node: Optional[str] = None) -> Dict[str, Path]:
        """
        初始化项目结构到 WORK_PATH 下
        
        在 WORK_PATH/{project_name}/{project_node}/ 下创建项目结构
        
        Args:
            work_path: WORK_PATH 根目录路径
            project_name: 项目名称（如 dongting）
            project_node: 项目节点名称（如 P85, P90，表示项目阶段）
            blocks: 块名称列表（如 ['block1', 'block2']），如果为 None 则从配置文件读取
            foundry: 可选，如果项目在多个 foundry 下存在，需要指定
            node: 可选，如果项目在多个 node 下存在，需要指定
            
        Returns:
            包含创建的目录路径的字典
            
        Raises:
            ValueError: 如果找不到项目或找到多个匹配
            
        Note:
            - 采用增量更新模式：只会创建缺失的 blocks，不会删除已存在的 blocks
            - 已存在的 blocks 及其内容完全不受影响
            - 如果 yaml 中删除了某个 block，该 block 目录不会被自动删除（安全模式）
        """
        # 自动查找项目的 foundry 和 node
        project_info = self.project_finder.get_project_info(project_name, foundry, node)
        foundry = project_info['foundry']
        node = project_info['node']
        
        # 确保 work_path 是绝对路径
        work_path = Path(work_path).resolve()
        project_path = work_path / project_name / project_node
        
        dirkit = DirKit(base_path=work_path)
        
        created_paths = {}
        
        # 1. 读取 init_project 配置
        init_config = self.config_loader.load_init_project_config(foundry, node, project_name)
        
        # 2. 确定要创建的 blocks
        if blocks is None:
            project_config = init_config.get('project', {}) if init_config else {}
            if project_config and 'blocks' in project_config:
                blocks = [b['name'] if isinstance(b, dict) else b 
                         for b in project_config['blocks']]
            else:
                blocks = []
        
        # 3. 创建项目节点目录（使用绝对路径，确保在正确的位置创建）
        project_node_path = Path(project_name) / project_node
        # 确保在 work_path 下创建，而不是当前工作目录
        actual_project_path = work_path / project_node_path
        actual_project_path.mkdir(parents=True, exist_ok=True)
        created_paths['project_node'] = project_path
        created_paths['foundry'] = foundry
        created_paths['node'] = node
        created_paths['project'] = project_name
        
        # 3.1 创建或更新版本信息文件
        version_manager = VersionInfoManager(project_path)
        version_manager.create_or_update_version_info(
            project_name, project_node, foundry, node, blocks
        )
        
        # 4. 创建块目录结构
        if blocks:
            block_paths = {}
            for block_name in blocks:
                block_path = project_node_path / block_name
                dirkit.ensure_dir(block_path)
                block_paths[block_name] = work_path / block_path
            created_paths['blocks'] = block_paths
        
        created_paths['work_path'] = work_path
        
        return created_paths
    
    def detect_project_path(self, path: Union[str, Path] = None) -> Optional[Dict[str, str]]:
        """
        从当前路径检测项目信息
        
        Args:
            path: 要检测的路径，如果为 None 则使用当前工作目录
            
        Returns:
            包含项目信息的字典，如果检测失败返回 None
        """
        if path is None:
            path = Path.cwd()
        else:
            path = Path(path).resolve()
        
        return self.path_detector.detect_project_path(
            path, 
            self.config_loader.load_init_project_config
        )
    
    def init_user_workspace(self, work_path: Optional[Union[str, Path]] = None,
                           project_name: Optional[str] = None,
                           project_node: Optional[str] = None,
                           block_name: Optional[str] = None,
                           user_name: Optional[str] = None,
                           branch_name: str = "branch1",
                           from_branch_step: Optional[str] = None,
                           link_mode: bool = True,
                           current_dir: Optional[Union[str, Path]] = None) -> Dict[str, Path]:
        """
        初始化用户工作环境（创建 user/branch 目录结构）
        
        支持两种模式：
        1. 显式模式：提供所有参数
        2. 自动模式：从当前工作目录推断项目信息
        
        Args:
            work_path: WORK_PATH 根目录路径（可选，如果提供则使用显式模式）
            project_name: 项目名称（如 dongting），可选
            project_node: 项目节点名称（如 P85），可选
            block_name: 块名称（如 block1），可选
            user_name: 用户名（如 zhangsan），如果为 None 则自动获取系统用户名
            branch_name: 分支名称（如 branch1），默认为 "branch1"
            from_branch_step: 可选，从已有分支的特定步骤开始创建新分支
                             格式：'branch_name.step_name' 或 'user_name.branch_name.step_name'
                             例如：'branch1.pnr_innovus.init' 或 'zhangsan.branch1.pnr_innovus.init'
            link_mode: 如果为 True，使用符号链接而不是复制（适用于大文件，节省空间）
                       默认 True（链接模式），使用递归目录链接
            current_dir: 用于检测的目录，如果为 None 则使用当前工作目录
            
        Returns:
            包含创建的目录和文件路径的字典
            
        Raises:
            ValueError: 如果无法推断项目信息或源分支/步骤不存在
        """
        # 自动获取用户名
        if user_name is None:
            user_name = get_current_user()
        
        # 如果提供了 work_path，使用显式模式
        if work_path and project_name and project_node and block_name:
            # 显式模式：使用提供的所有参数
            work_path = Path(work_path)
            project_info = self.get_project_info(project_name)
            foundry = project_info['foundry']
            node = project_info['node']
        else:
            # 自动模式：从当前目录推断
            detected = self.detect_project_path(current_dir)
            if not detected:
                raise ValueError(
                    "无法从当前路径推断项目信息。请确保你在项目路径下，"
                    "或者显式提供 work_path, project_name, project_node, block_name 参数"
                )
            
            work_path = Path(detected['work_path'])
            # 确保 work_path 是绝对路径
            if not work_path.is_absolute():
                work_path = work_path.resolve()
            else:
                work_path = work_path.resolve()
            project_name = detected['project_name']
            project_node = detected['project_node']
            block_name = detected['block_name']
            foundry = detected['foundry']
            node = detected['node']
        
        # 确保 work_path 是绝对路径（显式模式也需要）
        if work_path and not work_path.is_absolute():
            work_path = work_path.resolve()
        elif work_path:
            work_path = work_path.resolve()
        
        # 构建完整的分支路径
        branch_path = work_path / project_name / project_node / block_name / user_name / branch_name
        
        # 读取配置文件中的 branch_template
        init_config = self.config_loader.load_init_project_config(foundry, node, project_name)
        branch_template = None
        if init_config:
            edp_config = init_config.get('edp', {})
            if 'branch_template' in edp_config:
                branch_template = edp_config['branch_template']
        
        # 创建分支结构
        result = self.branch_manager.create_branch_structure(branch_path, branch_template)
        
        # 自动创建所有 hooks 文件（空文件）
        # 这样用户就不需要手动查找有哪些 step 和 sub_step 了
        try:
            hooks_created = self.branch_manager.create_hooks_files(
                branch_path,
                edp_center_path=self.edp_center,
                foundry=foundry,
                node=node,
                project=project_name
            )
            result['hooks_created'] = hooks_created
            logger.info(f"自动创建了 {len(hooks_created['step_hooks'])} 个 step hooks 和 {len(hooks_created['sub_step_hooks'])} 个 sub_step hooks")
        except Exception as e:
            # 如果创建 hooks 失败，记录警告但不影响分支创建
            logger.warning(f"自动创建 hooks 文件时出错: {e}，但分支创建继续")
            result['hooks_created'] = {'step_hooks': [], 'sub_step_hooks': []}
        
        # 如果指定了 from_branch_step，从源分支复制/链接步骤输出和其他目录
        if from_branch_step:
            # 解析源分支信息
            source_user, source_branch, step_name = self.branch_parser.parse_from_branch_step(
                from_branch_step, user_name
            )
            source_branch_path = work_path / project_name / project_node / block_name / source_user / source_branch
            
            # 1. 链接/复制特定步骤
            copy_info = self.branch_linker.copy_step_from_branch(
                work_path, project_name, project_node, block_name,
                from_branch_step, branch_path, user_name, link_mode
            )
            
            # 2. 递归链接/复制其他目录（cmds, dbs, flow, hooks, logs, rpts）
            # 排除 runs 目录（因为已经特殊处理了）
            linked_dirs = self.branch_linker.link_other_dirs_from_branch(
                source_branch_path, branch_path, link_mode
            )
            
            result['copied_from'] = from_branch_step
            result['link_mode'] = link_mode
            result['linked_dirs'] = linked_dirs
            
            # 记录分支来源信息到隐藏文件
            self.branch_source.save_branch_source_info(branch_path, from_branch_step, copy_info, link_mode)
        
        return result
    
    def parse_from_branch_step(self, from_branch_step: str, current_user: str) -> tuple:
        """解析 from_branch_step 参数（委托给 BranchStepParser）"""
        return self.branch_parser.parse_from_branch_step(from_branch_step, current_user)
    
    def copy_step_from_branch(self, work_path: Path, project_name: str,
                              project_node: str, block_name: str,
                              from_branch_step: str, target_branch_path: Path,
                              current_user: str, link_mode: bool = True) -> Dict[str, Path]:
        """从源分支复制或链接指定步骤的输出到目标分支（委托给 BranchLinker）"""
        return self.branch_linker.copy_step_from_branch(
            work_path, project_name, project_node, block_name,
            from_branch_step, target_branch_path, current_user, link_mode
        )
    
    def link_other_dirs_from_branch(self, source_branch_path: Path,
                                     target_branch_path: Path,
                                     link_mode: bool = True) -> Dict[str, Dict]:
        """从源分支递归链接/复制其他目录（委托给 BranchLinker）"""
        return self.branch_linker.link_other_dirs_from_branch(
            source_branch_path, target_branch_path, link_mode
        )
    
    def get_branch_source_info(self, branch_path: Union[str, Path]) -> Optional[Dict]:
        """获取分支来源信息（委托给 BranchSource）"""
        branch_path = Path(branch_path)
        return self.branch_source.get_branch_source_info(branch_path)
    
    def create_branch_structure(self, branch_path: Union[str, Path],
                               branch_template: Optional[Dict] = None) -> Dict[str, Path]:
        """创建分支目录结构（委托给 BranchManager）"""
        return self.branch_manager.create_branch_structure(branch_path, branch_template)

