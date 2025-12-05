#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Workflow Loader - 工作流数据加载模块

负责加载工作流数据，包括参数推断、图加载和状态信息添加。
"""

from pathlib import Path
from typing import Dict
from argparse import Namespace

from ....workflow_manager import WorkflowManager
from ...utils.graph_visualizer import GraphVisualizer
from ...utils.dependency_parser import list_available_flows
from ...utils.param_inference import infer_all_params


def load_workflow_data(manager: WorkflowManager, step_status: Dict) -> Dict:
    """
    加载工作流数据
    
    Args:
        manager: WorkflowManager 实例
        step_status: 步骤状态字典
    
    Returns:
        工作流图数据（包含节点、边和状态信息）
    
    Raises:
        ValueError: 如果无法推断参数或加载工作流
    """
    if not manager:
        raise ValueError("WorkflowManager 未初始化")
    
    # 推断项目参数
    project, foundry, node = _infer_project_params(manager)
    
    # 加载工作流图
    graph = manager.load_workflow(
        foundry=foundry,
        node=node,
        project=project
    )
    
    if not graph or len(graph.steps) == 0:
        raise ValueError("没有找到步骤")
    
    # 创建可视化器并提取数据
    visualizer = GraphVisualizer(graph)
    graph_data = visualizer.extract_graph_data()
    
    # 添加状态信息和 ready 状态
    _add_step_status_info(graph_data, step_status, manager, foundry, node, project)
    
    return graph_data


def _infer_project_params(manager: WorkflowManager) -> tuple:
    """
    推断项目参数（project, foundry, node）
    
    Args:
        manager: WorkflowManager 实例
    
    Returns:
        (project, foundry, node) 元组
    
    Raises:
        ValueError: 如果无法推断参数
    """
    # 使用统一的参数推断逻辑
    params = infer_all_params(manager)
    return params['project'], params['foundry'], params['node']


def _add_step_status_info(graph_data: Dict, step_status: Dict, 
                          manager: WorkflowManager, foundry: str, node: str, 
                          project: str) -> None:
    """
    为图数据添加步骤状态信息和 ready 状态
    
    Args:
        graph_data: 图数据字典（会被修改）
        step_status: 步骤状态字典
        manager: WorkflowManager 实例
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称
    """
    # 获取所有可用的 flow 和 step 信息（检查步骤是否 ready）
    edp_center_path = manager.edp_center
    available_flows = list_available_flows(edp_center_path, foundry, node, project)
    
    # 添加状态信息和 ready 状态
    for node_data in graph_data['nodes']:
        step_name = node_data['id']
        
        # 添加执行状态
        if step_name in step_status:
            node_data['status'] = step_status[step_name]['status']
        else:
            node_data['status'] = 'pending'
        
        # 检查步骤本身是否 ready（flow 是否准备好，源脚本是否存在）
        # step_name 格式: flow_name.step_name
        node_data['flow_ready'] = _check_step_ready(step_name, available_flows)


def _check_step_ready(step_name: str, available_flows: Dict) -> bool:
    """
    检查步骤是否 ready
    
    Args:
        step_name: 步骤名称（格式: flow_name.step_name）
        available_flows: 可用的 flow 信息字典
    
    Returns:
        bool: 步骤是否 ready
    """
    if '.' not in step_name:
        # 格式不正确，认为不 ready
        return False
    
    flow_name, step_name_only = step_name.split('.', 1)
    
    if flow_name not in available_flows:
        # flow 不存在
        return False
    
    if step_name_only not in available_flows[flow_name]:
        # 步骤在 dependency.yaml 中不存在
        return False
    
    # 步骤在 dependency.yaml 中定义，检查是否 ready
    step_info = available_flows[flow_name][step_name_only]
    return step_info.get('ready', False)

