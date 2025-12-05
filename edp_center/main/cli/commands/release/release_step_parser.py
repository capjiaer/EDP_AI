#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 步骤解析模块
负责解析步骤列表，支持多步骤和 release 整个 flow
"""

import sys
from typing import List, Tuple, Optional


def parse_steps(step_list: List[str], manager, foundry: str, node: str, 
                project: Optional[str]) -> List[Tuple[str, str]]:
    """
    解析步骤列表（支持多步骤和 release 整个 flow）
    
    Args:
        step_list: 步骤列表（可能是 ['pnr_innovus.postroute'] 或 ['pnr_innovus']）
        manager: WorkflowManager 实例
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        
    Returns:
        解析后的步骤列表：[(flow_name, step_name), ...]
    """
    parsed_steps = []
    
    # 获取所有可用的 flow 和 step（用于验证）
    from ...utils.dependency_parser import list_available_flows
    edp_center_path = manager.edp_center
    available_flows = list_available_flows(edp_center_path, foundry, node, project)
    
    for step_str in step_list:
        if '.' not in step_str:
            # 可能是 flow 名称（release 整个 flow）
            flow_name = step_str
            flow_steps = get_flow_steps(manager, foundry, node, project, flow_name)
            if flow_steps:
                parsed_steps.extend(flow_steps)
                print(f"[INFO] 从 flow {flow_name} 找到 {len(flow_steps)} 个步骤")
            else:
                print(f"[WARN] 未找到 flow {flow_name} 的步骤，跳过", file=sys.stderr)
        else:
            # 格式：flow_name.step_name
            flow_name, step_name = step_str.split('.', 1)
            
            # 验证 step 是否存在于 dependency.yaml（必须存在才允许 release）
            if flow_name not in available_flows:
                print(f"错误: Flow {flow_name} 在 dependency.yaml 中不存在", file=sys.stderr)
                print(f"提示: 请检查 flow 名称是否正确，或确保该 flow 已在 dependency.yaml 中定义", file=sys.stderr)
                continue
            elif step_name not in available_flows[flow_name]:
                print(f"错误: 步骤 {flow_name}.{step_name} 在 dependency.yaml 中不存在", file=sys.stderr)
                print(f"提示: 请检查 step 名称是否正确，或确保该 step 已在 dependency.yaml 中定义", file=sys.stderr)
                # 显示该 flow 下可用的 step
                available_steps = sorted(available_flows[flow_name].keys())
                if available_steps:
                    print(f"提示: {flow_name} 下可用的 step: {', '.join(available_steps)}", file=sys.stderr)
                continue
            
            parsed_steps.append((flow_name, step_name))
    
    return parsed_steps


def get_flow_steps(manager, foundry: str, node: str, project: Optional[str], flow_name: str) -> List[Tuple[str, str]]:
    """
    从 dependency.yaml 获取 flow 的所有步骤
    
    Args:
        manager: WorkflowManager 实例
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        
    Returns:
        步骤列表：[(flow_name, step_name), ...]
    """
    from ...utils.dependency_parser import list_available_flows
    
    edp_center_path = manager.edp_center
    flows = list_available_flows(edp_center_path, foundry, node, project)
    
    if flow_name not in flows:
        return []
    
    steps = []
    for step_name in flows[flow_name].keys():
        steps.append((flow_name, step_name))
    
    return steps

