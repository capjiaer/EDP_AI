#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run Range Helper - 辅助函数，用于查找需要执行的步骤范围
"""

from typing import List, Set, Optional
from edp_center.packages.edp_flowkit.flowkit import Graph


def get_all_downstream_steps(graph: Graph, step_name: str, visited: Optional[Set[str]] = None) -> Set[str]:
    """
    递归获取指定步骤的所有后续步骤（包括直接和间接的后续步骤）
    
    Args:
        graph: 依赖图对象
        step_name: 起始步骤名称
        visited: 已访问的步骤集合（用于避免循环）
        
    Returns:
        所有后续步骤名称的集合（包括 step_name 本身）
    """
    if visited is None:
        visited = set()
    
    if step_name in visited:
        return set()
    
    visited.add(step_name)
    result = {step_name}
    
    # 获取直接后续步骤
    next_steps = graph.get_next_steps(step_name)
    for next_step in next_steps:
        result.update(get_all_downstream_steps(graph, next_step.name, visited))
    
    return result


def get_all_upstream_steps(graph: Graph, step_name: str, visited: Optional[Set[str]] = None) -> Set[str]:
    """
    递归获取指定步骤的所有前置步骤（包括直接和间接的前置步骤）
    
    Args:
        graph: 依赖图对象
        step_name: 目标步骤名称
        visited: 已访问的步骤集合（用于避免循环）
        
    Returns:
        所有前置步骤名称的集合（包括 step_name 本身）
    """
    if visited is None:
        visited = set()
    
    if step_name in visited:
        return set()
    
    visited.add(step_name)
    result = {step_name}
    
    # 获取直接前置步骤
    prev_steps = graph.get_prev_steps(step_name)
    for prev_step in prev_steps:
        result.update(get_all_upstream_steps(graph, prev_step.name, visited))
    
    return result


def get_steps_between(graph: Graph, from_step: str, to_step: str) -> Set[str]:
    """
    获取从 from_step 到 to_step 的所有步骤（包括 from_step 和 to_step）
    
    策略：
    1. 找到从 from_step 可达的所有后续步骤
    2. 找到 to_step 的所有前置步骤
    3. 取交集，得到从 from_step 到 to_step 的路径上的所有步骤
    4. **重要**：如果 to_step 有多个前置路径，需要包含所有前置路径，
       确保 to_step 可以执行（即使某些前置路径不在 from_step 的下游）
    
    例如：
        SA -> S2.1 -> S3
        SB -> S2.2 -> S3
    如果执行 --from SA --to S3，需要包含 SB 和 S2.2，否则 S3 无法执行
    
    Args:
        graph: 依赖图对象
        from_step: 起始步骤名称
        to_step: 目标步骤名称
        
    Returns:
        从 from_step 到 to_step 的所有步骤名称的集合（包括所有必要的前置步骤）
    """
    # 检查步骤是否存在
    if from_step not in graph:
        raise ValueError(f"步骤不存在: {from_step}")
    if to_step not in graph:
        raise ValueError(f"步骤不存在: {to_step}")
    
    # 找到从 from_step 可达的所有后续步骤
    downstream_from = get_all_downstream_steps(graph, from_step)
    
    # 找到 to_step 的所有前置步骤
    upstream_to = get_all_upstream_steps(graph, to_step)
    
    # 取交集，得到从 from_step 到 to_step 的路径上的所有步骤
    steps_between = downstream_from & upstream_to
    
    # 检查 to_step 是否在结果中
    if to_step not in steps_between:
        raise ValueError(f"无法找到从 {from_step} 到 {to_step} 的路径，它们之间可能没有依赖关系")
    
    # **关键改进**：如果 to_step 有多个前置步骤，需要确保所有前置步骤都在执行列表中
    # 否则 to_step 会因为前置步骤未完成而无法执行
    prev_steps = graph.get_prev_steps(to_step)
    if prev_steps:
        # 检查所有前置步骤是否都在 steps_between 中
        missing_prereqs = []
        for prev_step in prev_steps:
            if prev_step.name not in steps_between:
                missing_prereqs.append(prev_step.name)
        
        # 如果有缺失的前置步骤，需要将它们及其所有前置步骤都加入执行列表
        if missing_prereqs:
            for missing_step in missing_prereqs:
                # 将缺失步骤及其所有前置步骤加入执行列表
                missing_upstream = get_all_upstream_steps(graph, missing_step)
                steps_between.update(missing_upstream)
    
    return steps_between


def get_steps_to_execute(graph: Graph, 
                         run_from: Optional[str] = None,
                         run_to: Optional[str] = None,
                         single_step: Optional[str] = None) -> List[str]:
    """
    根据参数确定需要执行的步骤列表
    
    Args:
        graph: 依赖图对象
        run_from: 起始步骤（格式: flow.step）
        run_to: 目标步骤（格式: flow.step）
        single_step: 单个步骤（格式: flow.step），如果指定，则只执行这个步骤
        
    Returns:
        需要执行的步骤名称列表（按拓扑顺序）
    """
    if single_step:
        # 只执行单个步骤
        if single_step not in graph:
            raise ValueError(f"步骤不存在: {single_step}")
        return [single_step]
    
    if run_from and run_to:
        # 从 from_step 到 to_step
        steps_to_execute = get_steps_between(graph, run_from, run_to)
    elif run_from:
        # 从 from_step 开始的所有后续步骤
        if run_from not in graph:
            raise ValueError(f"步骤不存在: {run_from}")
        steps_to_execute = get_all_downstream_steps(graph, run_from)
    elif run_to:
        # 从开始到 to_step 的所有步骤
        if run_to not in graph:
            raise ValueError(f"步骤不存在: {run_to}")
        steps_to_execute = get_all_upstream_steps(graph, run_to)
    else:
        raise ValueError("必须指定 --run、--from、--to 中的至少一个")
    
    # 按拓扑顺序排序
    all_steps = graph.topological_sort()
    step_names = [step.name for step in all_steps if step.name in steps_to_execute]
    
    return step_names

