#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WorkflowManager - 工作流管理器

整合四个 KIT，提供统一的工作流管理接口：
1. edp_dirkit - 环境初始化
2. edp_configkit - 配置加载
3. edp_cmdkit - 脚本处理
4. edp_flowkit - 工作流执行
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Union, Any

# 导入四个 KIT
from edp_center.packages.edp_dirkit import ProjectInitializer, WorkPathInitializer
from edp_center.packages.edp_configkit import files2dict
from edp_center.packages.edp_cmdkit import CmdProcessor
from edp_center.packages.edp_flowkit.flowkit import Graph, execute_all_steps, ICCommandExecutor


class WorkflowManager:
    """工作流管理器 - 整合四个 KIT"""
    
    def __init__(self, edp_center_path: Union[str, Path]):
        """
        初始化 WorkflowManager
        
        Args:
            edp_center_path: edp_center 资源库的路径
        """
        self.edp_center = Path(edp_center_path).resolve()
        if not self.edp_center.exists():
            raise FileNotFoundError(f"EDP Center 路径不存在: {edp_center_path}")
        
        # 初始化各个 KIT
        self.project_initializer = ProjectInitializer(self.edp_center)
        self.work_path_initializer = WorkPathInitializer(self.edp_center)
        self.cmd_processor = CmdProcessor()
    
    # ==================== 环境初始化阶段 ====================
    
    def init_project(self, 
                     work_path: Union[str, Path],
                     project_name: str,
                     version: str,
                     blocks: Optional[List[str]] = None,
                     foundry: Optional[str] = None,
                     node: Optional[str] = None) -> Dict[str, Path]:
        """
        初始化项目环境（使用 edp_dirkit）
        
        Args:
            work_path: WORK_PATH 根目录路径
            project_name: 项目名称（如 dongting）
            version: 项目版本名称（如 P85）
            blocks: 块名称列表，如果为 None 则从配置文件读取
            foundry: 可选，如果项目在多个 foundry 下存在，需要指定
            node: 可选，如果项目在多个 node 下存在，需要指定
            
        Returns:
            包含创建的目录路径的字典
        """
        return self.work_path_initializer.init_project(
            work_path=work_path,
            project_name=project_name,
            project_node=version,  # 兼容旧参数名
            blocks=blocks,
            foundry=foundry,
            node=node
        )
    
    def init_user_workspace(self,
                           work_path: Union[str, Path],
                           project: str,
                           version: str,
                           block: str,
                           user: str,
                           branch: str,
                           foundry: Optional[str] = None,
                           node: Optional[str] = None,
                           from_branch_step: Optional[str] = None) -> Dict[str, Path]:
        """
        初始化用户工作空间（使用 edp_dirkit）
        
        Args:
            work_path: WORK_PATH 根目录路径
            project: 项目名称（如 dongting）
            version: 项目版本名称（如 P85）
            block: 块名称（如 block1）
            user: 用户名（如 zhangsan）
            branch: 分支名称（如 branch1）
            foundry: 可选，如果项目在多个 foundry 下存在，需要指定
            node: 可选，如果项目在多个 node 下存在，需要指定
            from_branch_step: 可选，从指定分支的步骤创建新分支（如 "branch1:pnr_innovus.init"）
            
        Returns:
            包含创建的目录路径的字典
        """
        return self.work_path_initializer.init_user_workspace(
            work_path=work_path,
            project_name=project,
            project_node=version,  # 兼容旧参数名
            block_name=block,
            user_name=user,
            branch_name=branch,
            from_branch_step=from_branch_step
        )
    
    # ==================== 配置加载阶段 ====================
    
    def load_config(self,
                   foundry: str,
                   node: str,
                   project: str,
                   flow: str,
                   config_files: Optional[List[Union[str, Path]]] = None) -> Dict[str, Any]:
        """
        加载配置文件（使用 edp_configkit）
        
        Args:
            foundry: 代工厂名称（如 SAMSUNG）
            node: 工艺节点（如 S8）
            project: 项目名称（如 dongting）
            flow: 流程名称（如 pv_calibre）
            config_files: 可选的配置文件列表，如果为 None，则自动从 edp_center 获取
            
        Returns:
            合并后的配置字典
        """
        if config_files is None:
            # 自动获取配置文件路径
            config_files = self.project_initializer.get_config_files(
                foundry=foundry,
                node=node,
                project=project,
                flow=flow
            )
        
        # 使用 edp_configkit 合并配置
        return files2dict(*config_files)
    
    # ==================== 脚本处理阶段 ====================
    
    def process_script(self,
                      input_file: Union[str, Path],
                      output_file: Optional[Union[str, Path]] = None,
                      search_paths: Optional[List[Union[str, Path]]] = None,
                      prepend_default_sources: bool = True,
                      full_tcl_path: Optional[Union[str, Path]] = None,
                      hooks_dir: Optional[Union[str, Path]] = None,
                      step_name: Optional[str] = None,
                      debug_mode: int = 0,
                      skip_sub_steps: Optional[List[str]] = None,
                      foundry: Optional[str] = None,
                      node: Optional[str] = None,
                      project: Optional[str] = None,
                      flow_name: Optional[str] = None) -> Optional[str]:
        """
        处理 Tcl 脚本（使用 edp_cmdkit）
        
        Args:
            input_file: 输入的 Tcl 文件路径
            output_file: 输出文件路径，如果为 None，返回处理后的内容字符串
            search_paths: 搜索路径列表，用于查找被导入的文件
            prepend_default_sources: 是否在文件头部添加默认的 source 语句
            full_tcl_path: full.tcl 文件路径，如果提供，会在文件头添加 source full.tcl
            hooks_dir: hooks 目录路径（如 hooks/pv_calibre/ipmerge），用于插入 hooks 文件
            step_name: 步骤名称（如 ipmerge），用于查找 step.pre 和 step.post
            debug_mode: Debug 模式：0=正常执行，1=交互式调试
            skip_sub_steps: 要跳过的 sub_steps 列表（从 user_config.yaml 读取）
            foundry: 代工厂名称（如 SAMSUNG），用于生成默认 source 语句
            node: 工艺节点（如 S8），用于生成默认 source 语句
            project: 项目名称（如 dongting），用于生成默认 source 语句
            flow_name: 流程名称（如 pnr_innovus），用于生成默认 source 语句
            
        Returns:
            如果 output_file 为 None，返回处理后的内容字符串
            如果 output_file 不为 None，返回 None（内容已写入文件）
        """
        # 自动推断路径信息
        return self.cmd_processor.process_file(
            input_file=input_file,
            output_file=output_file,
            search_paths=search_paths,
            edp_center_path=self.edp_center,
            prepend_default_sources=prepend_default_sources,
            full_tcl_path=full_tcl_path,
            hooks_dir=hooks_dir,
            step_name=step_name,
            debug_mode=debug_mode,
            skip_sub_steps=skip_sub_steps,
            foundry=foundry,
            node=node,
            project=project,
            flow_name=flow_name
        )
    
    # ==================== 工作流执行阶段 ====================
    
    def load_workflow(self,
                     foundry: str,
                     node: str,
                     project: str,
                     flow: Optional[str] = None,
                     dependency_files: Optional[List[Union[str, Path]]] = None) -> Graph:
        """
        加载工作流定义（使用 edp_flowkit）
        
        自动加载所有 flow 的 dependency.yaml，通过文件匹配自动建立跨 flow 依赖关系。
        
        Args:
            foundry: 代工厂名称（如 SAMSUNG）
            node: 工艺节点（如 S8）
            project: 项目名称（如 dongting）
            flow: 流程名称（可选，如果为 None，则加载所有 flow）
            dependency_files: 可选的 dependency.yaml 文件列表，如果为 None，则自动从 edp_center 获取
            
        Returns:
            Graph 对象（包含所有 flow 的步骤，依赖关系通过文件匹配自动建立）
        """
        if dependency_files is None:
            # 自动获取所有 flow 的 dependency.yaml 文件路径
            dependency_files = self._get_all_dependency_files(foundry, node, project, flow)
        
        # 从所有 YAML 文件构建图
        # Graph 会自动合并所有步骤，并通过输入输出文件匹配建立依赖关系（包括跨 flow 依赖）
        graph = Graph(yaml_files=dependency_files)
        return graph
    
    def execute_workflow(self,
                        graph: Graph,
                        work_path: Union[str, Path],
                        project: str,
                        version: str,
                        block: str,
                        user: str,
                        branch: str,
                        config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行工作流（使用 edp_flowkit）
        
        Args:
            graph: 工作流图对象
            work_path: WORK_PATH 根目录路径
            project: 项目名称（如 dongting）
            version: 项目版本名称（如 P85）
            block: 块名称（如 block1）
            user: 用户名（如 zhangsan）
            branch: 分支名称（如 branch1）
            config: 可选的配置字典，用于执行器
            
        Returns:
            执行结果字典
        """
        # 构建工作路径
        workspace_path = Path(work_path) / project / version / block / user / branch
        
        # 如果没有提供配置，使用默认配置
        if config is None:
            config = {"edp": {"lsf": 0, "tool_opt": "bash"}}
        
        # 创建执行器
        executor = ICCommandExecutor(str(workspace_path), config)
        
        # 执行工作流
        results = execute_all_steps(
            graph=graph,
            execute_func=executor.run_cmd,
            merged_var=config
        )
        
        return results
    
    # ==================== 完整工作流 ====================
    
    def run_full_workflow(self,
                         work_path: Union[str, Path],
                         project: str,
                         version: str,
                         block: str,
                         user: str,
                         branch: str,
                         flow: str,
                         foundry: Optional[str] = None,
                         node: Optional[str] = None,
                         from_branch_step: Optional[str] = None,
                         prepend_default_sources: bool = True) -> Dict[str, Any]:
        """
        运行完整工作流（整合四个 KIT）
        
        流程：
        1. 初始化用户工作空间（edp_dirkit）
        2. 加载配置（edp_configkit）
        3. 加载工作流定义（edp_flowkit）
        4. 处理脚本（edp_cmdkit）- 在工作流执行时自动调用
        5. 执行工作流（edp_flowkit）
        
        Args:
            work_path: WORK_PATH 根目录路径
            project: 项目名称（如 dongting）
            version: 项目版本名称（如 P85）
            block: 块名称（如 block1）
            user: 用户名（如 zhangsan）
            branch: 分支名称（如 branch1）
            flow: 流程名称（如 pv_calibre）
            foundry: 可选，如果项目在多个 foundry 下存在，需要指定
            node: 可选，如果项目在多个 node 下存在，需要指定
            from_branch_step: 可选，从指定分支的步骤创建新分支
            prepend_default_sources: 是否在脚本处理时添加默认 source 语句
            
        Returns:
            执行结果字典
        """
        # 1. 初始化用户工作空间
        workspace_paths = self.init_user_workspace(
            work_path=work_path,
            project=project,
            version=version,
            block=block,
            user=user,
            branch=branch,
            foundry=foundry,
            node=node,
            from_branch_step=from_branch_step
        )
        
        # 2. 获取项目信息（用于后续步骤）
        project_info = self.work_path_initializer.get_project_info(project, foundry, node)
        foundry = project_info['foundry']
        node = project_info['node']
        
        # 3. 加载配置
        config = self.load_config(foundry, node, project, flow)
        
        # 4. 加载工作流定义（加载所有 flow，自动发现跨 flow 依赖）
        # 即使只运行一个 flow，也需要加载所有 flow 的 dependency.yaml
        # 这样才能通过文件匹配自动建立跨 flow 依赖关系
        graph = self.load_workflow(foundry, node, project, flow=None)
        
        # 5. 执行工作流（脚本处理会在执行器内部自动调用）
        results = self.execute_workflow(
            graph=graph,
            work_path=work_path,
            project=project,
            version=version,
            block=block,
            user=user,
            branch=branch,
            config=config
        )
        
        return results
    
    # ==================== 辅助方法 ====================
    
    def _get_all_dependency_files(self,
                                   foundry: str,
                                   node: str,
                                   project: str,
                                   flow: Optional[str] = None) -> List[Path]:
        """
        获取所有 flow 的 dependency.yaml 文件路径
        
        加载所有 flow 的 dependency.yaml，这样跨 flow 的依赖关系会通过文件匹配自动建立。
        
        Args:
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称
            flow: 流程名称（可选，如果为 None，则加载所有 flow）
            
        Returns:
            dependency.yaml 文件路径列表（按优先级排序：common 优先，然后 project）
        """
        from edp_center.main.workflow_helpers import get_all_dependency_files
        return get_all_dependency_files(self.edp_center, foundry, node, project, flow)
    
    def _get_dependency_files(self,
                              foundry: str,
                              node: str,
                              project: str,
                              flow: str) -> List[Path]:
        """
        获取单个 flow 的 dependency.yaml 文件路径
        
        Args:
            foundry: 代工厂名称
            node: 工艺节点
            project: 项目名称
            flow: 流程名称
            
        Returns:
            dependency.yaml 文件路径列表（按优先级排序）
        """
        return self._get_all_dependency_files(foundry, node, project, flow)

