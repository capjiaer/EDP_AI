#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自动变量生成模块
负责生成 full.tcl 中的自动变量（如 project(block_name), project(foundry) 等）
"""

from pathlib import Path
from typing import Optional, Dict, TextIO, List
import yaml


def write_auto_variables(work_path_info: Optional[Dict], foundry: str, node: str, 
                        project: Optional[str], flow_name: str, step_name: str,
                        full_tcl_path: Path, edp_center_path: Optional[Path] = None, f: TextIO = None) -> None:
    """
    写入自动生成的变量到 full.tcl 文件
    
    这些变量包括：
    - project(project_name): 项目名称
    - project(version): 项目版本
    - project(block_name): 块名称
    - project(user_name): 用户名
    - project(branch_name): 分支名称
    - project(foundry): 代工厂名称
    - project(node): 工艺节点
    - project(init_path): 工作路径的绝对路径（本质上是 init_path）
    - project(work_path): 实际路径到 runs/flow_name.step_name
    - project(flow_name): 流程名称
    - project(step_name): 步骤名称
    - edp(edp_center_path): EDP 平台的根路径（绝对路径）
    - edp(config_path): 配置文件的路径（绝对路径）
    - edp(flow_path): flow 文件的路径（绝对路径）
    - edp(execution_plan,step_name): 该步骤的执行计划列表（从 dependency.yaml 读取，包含 sub_steps 的 proc 名称）
    
    Args:
        work_path_info: 工作路径信息字典（可选）
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        step_name: 步骤名称
        full_tcl_path: full.tcl 文件路径（用于计算 work_path）
        edp_center_path: EDP 平台根路径（可选）
        f: 输出文件对象
    """
    f.write("# Auto-generated project variables\n")
    
    # 写入项目相关变量（从 work_path_info 获取）
    _write_project_var(f, 'project_name', project, work_path_info, 'project')
    _write_project_var(f, 'version', None, work_path_info, 'version')
    _write_project_var(f, 'block_name', None, work_path_info, 'block')
    _write_project_var(f, 'user_name', None, work_path_info, 'user')
    _write_project_var(f, 'branch_name', None, work_path_info, 'branch')
    
    # 写入固定变量（不需要从 work_path_info 获取）
    _write_simple_var(f, 'project', 'foundry', foundry)
    _write_simple_var(f, 'project', 'node', node)
    _write_simple_var(f, 'project', 'flow_name', flow_name)
    _write_simple_var(f, 'project', 'step_name', step_name)
    
    # 写入路径变量
    _write_path_var(f, 'project', 'init_path', work_path_info, 'work_path')
    _write_work_path_var(f, full_tcl_path)
    
    # 写入 EDP 平台相关变量
    if edp_center_path:
        _write_edp_path_var(f, 'edp_center_path', edp_center_path)
        _write_edp_path_var(f, 'config_path', edp_center_path, 'config')
        _write_edp_path_var(f, 'flow_path', edp_center_path, 'flow')
    
    # 写入执行计划变量（从 dependency.yaml 读取 sub_steps）
    # 注意：这里只包含 sub_steps，中间代码会在 debug 模式下解析主脚本后添加
    if edp_center_path:
        sub_steps = _read_sub_steps_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
        if sub_steps:
            # sub_steps 是字典列表 [{file_name: proc_name}, ...]
            # 生成执行计划格式：{proc_name proc_name ...}（只有 proc 名称）
            execution_plan = []
            for sub_step in sub_steps:
                if isinstance(sub_step, dict) and len(sub_step) == 1:
                    _, proc_name = next(iter(sub_step.items()))
                    execution_plan.append(_quote_value(proc_name))
            
            if execution_plan:
                execution_plan_str = ' '.join(execution_plan)
                f.write(f"set edp(execution_plan,{step_name}) {{{execution_plan_str}}}\n")
    
    f.write("\n")


def _write_project_var(f: TextIO, var_name: str, fallback_value: Optional[str],
                       work_path_info: Optional[Dict], key: str) -> None:
    """
    写入 project 变量（从 work_path_info 获取，如果不存在则使用 fallback_value）
    
    Args:
        f: 输出文件对象
        var_name: 变量名（如 'project_name'）
        fallback_value: 备用值（如果 work_path_info 中没有该键）
        work_path_info: 工作路径信息字典（可选）
        key: work_path_info 中的键名
    """
    if work_path_info and work_path_info.get(key):
        value = work_path_info[key]
        _write_simple_var(f, 'project', var_name, value)
    elif fallback_value is not None:
        _write_simple_var(f, 'project', var_name, fallback_value)


def _write_simple_var(f: TextIO, namespace: str, var_name: str, value: str) -> None:
    """
    写入简单变量（不需要特殊处理）
    
    Args:
        f: 输出文件对象
        namespace: 命名空间（如 'project' 或 'edp'）
        var_name: 变量名
        value: 变量值
    """
    f.write(f"set {namespace}({var_name}) {_quote_value(value)}\n")


def _write_path_var(f: TextIO, namespace: str, var_name: str,
                    work_path_info: Optional[Dict], key: str) -> None:
    """
    写入路径变量（从 work_path_info 获取绝对路径）
    
    Args:
        f: 输出文件对象
        namespace: 命名空间（如 'project'）
        var_name: 变量名（如 'init_path'）
        work_path_info: 工作路径信息字典（可选）
        key: work_path_info 中的键名（如 'work_path'）
    """
    if work_path_info and work_path_info.get(key):
        path = Path(work_path_info[key]).resolve()
        _write_simple_var(f, namespace, var_name, str(path))


def _write_work_path_var(f: TextIO, full_tcl_path: Path) -> None:
    """
    写入 work_path 变量（full.tcl 文件所在的目录）
    
    Args:
        f: 输出文件对象
        full_tcl_path: full.tcl 文件路径
    """
    work_path_dir = full_tcl_path.parent.resolve()
    _write_simple_var(f, 'project', 'work_path', str(work_path_dir))


def _read_sub_steps_from_dependency(edp_center_path: Path, foundry: str, node: str,
                                    project: Optional[str], flow_name: str, step_name: str) -> List[dict]:
    """
    从 dependency.yaml 文件中读取指定 step 的 sub_steps 列表
    
    Args:
        edp_center_path: edp_center 路径
        foundry: 代工厂名称
        node: 工艺节点
        project: 项目名称（可选）
        flow_name: 流程名称
        step_name: 步骤名称
    
    Returns:
        sub_steps 列表（每个元素是字典 {file_name: proc_name}），如果未找到则返回空列表
    """
    sub_steps = []
    config_path = edp_center_path / 'config' / foundry / node
    
    # 搜索路径：项目特定和 common（按优先级从低到高）
    search_paths = []
    
    # 1. common 路径（优先级低）
    common_path = config_path / 'common'
    if common_path.exists():
        search_paths.append(common_path)
    
    # 2. 项目特定路径（优先级高，会覆盖 common）
    if project:
        project_path = config_path / project
        if project_path.exists():
            search_paths.append(project_path)
    
    # 从高优先级到低优先级查找（项目特定的会覆盖 common）
    for config_dir in reversed(search_paths):
        flow_dir = config_dir / flow_name
        dependency_file = flow_dir / 'dependency.yaml'
        
        if not dependency_file.exists():
            continue
        
        try:
            with open(dependency_file, 'r', encoding='utf-8') as f:
                dependency_config = yaml.safe_load(f) or {}
            
            if flow_name not in dependency_config:
                continue
            
            flow_config = dependency_config[flow_name]
            if 'dependency' not in flow_config:
                continue
            
            dependency = flow_config['dependency']
            
            # 递归查找 step_name 并提取 sub_steps
            def find_step_recursive(data):
                """递归查找 step_name 并提取 sub_steps"""
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key == step_name and isinstance(value, dict):
                            # 找到目标 step，提取 sub_steps
                            if 'sub_steps' in value:
                                return value['sub_steps']
                        # 继续递归查找
                        result = find_step_recursive(value)
                        if result is not None:
                            return result
                elif isinstance(data, list):
                    for item in data:
                        result = find_step_recursive(item)
                        if result is not None:
                            return result
                return None
            
            found_sub_steps = find_step_recursive(dependency)
            if found_sub_steps:
                # 如果 sub_steps 是字典（格式：{file_name: proc_name}），转换为列表
                if isinstance(found_sub_steps, dict):
                    # 字典格式：{file_name: proc_name}，转换为列表中的字典格式
                    sub_steps = [{k: v} for k, v in found_sub_steps.items()]
                elif isinstance(found_sub_steps, list):
                    # 列表格式（每个元素应该是字典）
                    sub_steps = found_sub_steps
                else:
                    sub_steps = []
                break  # 找到后停止搜索（项目特定的会覆盖 common）
        
        except Exception:
            # 如果读取失败，继续查找下一个文件
            continue
    
    return sub_steps


def _write_edp_path_var(f: TextIO, var_name: str, edp_center_path: Path, 
                        subpath: Optional[str] = None) -> None:
    """
    写入 edp 路径变量（绝对路径）
    
    Args:
        f: 输出文件对象
        var_name: 变量名（如 'edp_center_path'、'config_path'、'flow_path'）
        edp_center_path: EDP 平台根路径
        subpath: 子路径（可选，如 'config'、'flow'）
    """
    if subpath:
        path = Path(edp_center_path) / subpath
    else:
        path = Path(edp_center_path)
    path_resolved = path.resolve()
    _write_simple_var(f, 'edp', var_name, str(path_resolved))


def _quote_value(value: str) -> str:
    """
    为 Tcl 值添加引号（如果需要）
    
    Args:
        value: 要引用的值
        
    Returns:
        引用后的值
    """
    # 如果值包含空格或特殊字符，需要用大括号或引号包裹
    if not value:
        return '""'
    
    # 如果包含空格、大括号、方括号、美元符号等，需要用大括号包裹
    if any(c in value for c in ' {}[]$\\'):
        # 转义大括号
        escaped = value.replace('{', '\\{').replace('}', '\\}')
        return f'"{escaped}"'
    
    return value

