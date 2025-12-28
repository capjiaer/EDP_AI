#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rollback Comparison - 回滚对比模块

负责对比配置差异并显示结果。
"""

from typing import Dict, List, Any


def format_value(value: Any) -> str:
    """
    格式化配置值，用于显示
    
    Args:
        value: 配置值
        
    Returns:
        格式化后的字符串
    """
    if isinstance(value, (list, tuple)):
        return ' '.join(str(v) for v in value)
    elif isinstance(value, dict):
        return str(value)
    elif value is None:
        return '(空)'
    else:
        return str(value)


def compare_configs(config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, List]:
    """
    对比两个配置字典，找出差异
    
    Args:
        config1: 第一个配置（通常是成功的执行）
        config2: 第二个配置（通常是失败的执行）
        
    Returns:
        包含差异信息的字典：
        {
            'added': [(key, value)],      # 新增的变量
            'removed': [(key, value)],    # 删除的变量
            'modified': [(key, old_value, new_value)]  # 修改的变量
        }
    """
    differences = {
        'added': [],
        'removed': [],
        'modified': []
    }
    
    # 扁平化配置字典，转换为 (namespace, key) -> value 的格式
    def flatten_config(config: Dict, prefix: str = '') -> Dict[str, Any]:
        """将嵌套字典扁平化"""
        result = {}
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(flatten_config(value, full_key))
            else:
                result[full_key] = value
        return result
    
    flat_config1 = flatten_config(config1)
    flat_config2 = flatten_config(config2)
    
    # 找出所有键
    all_keys = set(flat_config1.keys()) | set(flat_config2.keys())
    
    for key in sorted(all_keys):
        val1 = flat_config1.get(key)
        val2 = flat_config2.get(key)
        
        if key not in flat_config1:
            # 新增的变量
            differences['added'].append((key, val2))
        elif key not in flat_config2:
            # 删除的变量
            differences['removed'].append((key, val1))
        elif val1 != val2:
            # 修改的变量
            differences['modified'].append((key, val1, val2))
    
    return differences


def display_config_diff(differences: Dict[str, List], success_run: Dict, failed_run: Dict):
    """
    显示配置差异
    
    Args:
        differences: 差异信息字典
        success_run: 成功的运行记录
        failed_run: 失败的运行记录
    """
    print("━" * 80)
    print("配置差异对比")
    print("━" * 80)
    print()
    
    # 显示对比的记录信息
    print("对比记录:")
    run1_status = success_run.get('status', 'unknown')
    run2_status = failed_run.get('status', 'unknown')
    run1_icon = '[OK]' if run1_status == 'success' else '[FAIL]' if run1_status == 'failed' else '[?]'
    run2_icon = '[OK]' if run2_status == 'success' else '[FAIL]' if run2_status == 'failed' else '[?]'
    print(f"  记录1 (基准): [{success_run.get('timestamp', 'N/A')}] | "
          f"{success_run.get('flow', 'N/A')}.{success_run.get('step', 'N/A')} | "
          f"{run1_icon} {run1_status}")
    print(f"  记录2 (对比): [{failed_run.get('timestamp', 'N/A')}] | "
          f"{failed_run.get('flow', 'N/A')}.{failed_run.get('step', 'N/A')} | "
          f"{run2_icon} {run2_status}")
    print()
    
    # 显示 full.tcl 文件位置
    success_full_tcl = success_run.get('full_tcl_path')
    failed_full_tcl = failed_run.get('full_tcl_path')
    if success_full_tcl or failed_full_tcl:
        print("full.tcl 文件位置:")
        if success_full_tcl:
            print(f"  成功执行: {success_full_tcl}")
        if failed_full_tcl:
            print(f"  失败执行: {failed_full_tcl}")
        print()
    
    # 显示差异
    has_diff = False
    
    if differences['added']:
        has_diff = True
        print("新增的配置:")
        for key, value in differences['added']:
            print(f"  + {key} = {format_value(value)}")
        print()
    
    if differences['removed']:
        has_diff = True
        print("删除的配置:")
        for key, value in differences['removed']:
            print(f"  - {key} = {format_value(value)}")
        print()
    
    if differences['modified']:
        has_diff = True
        print("修改的配置:")
        for key, old_value, new_value in differences['modified']:
            print(f"  ~ {key}")
            print(f"    之前: {format_value(old_value)}")
            print(f"    现在: {format_value(new_value)}")
        print()
    
    if not has_diff:
        print("[OK] 未发现配置差异")
        print()
    
    # 显示关键配置变化提示
    key_configs = ['cpu_num', 'memory', 'queue', 'lsf', 'tool_opt']
    key_changes = []
    for key, old_value, new_value in differences['modified']:
        if any(kc in key.lower() for kc in key_configs):
            key_changes.append((key, old_value, new_value))
    
    if key_changes:
        print("[WARN] 关键配置变化:")
        for key, old_value, new_value in key_changes:
            print(f"  - {key}: {format_value(old_value)} → {format_value(new_value)}")
        print()
    
    print("━" * 80)

