#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基本使用示例 (Basic Usage Examples)

这个脚本展示了 configkit 库的基本用法。
This script demonstrates the basic usage of the configkit library.
"""

import os
import tempfile
from tkinter import Tcl
import yaml

from edp_center.packages.edp_configkit import (
    merge_dict,
    dict2tclinterp,
    tclinterp2dict,
    yamlfiles2tclfile,
    tclfiles2yamlfile,
    files2dict,
    yamlfiles2dict
)

def example_dict_operations():
    """字典操作示例 (Dictionary Operations Example)"""
    print("\n=== 字典操作示例 (Dictionary Operations Example) ===")
    
    # 创建两个字典
    dict1 = {'a': 1, 'b': {'c': 2}}
    dict2 = {'b': {'d': 3}, 'e': 4}
    
    # 合并字典
    result = merge_dict(dict1, dict2)
    print(f"dict1: {dict1}")
    print(f"dict2: {dict2}")
    print(f"merged: {result}")

def example_tcl_conversion():
    """Tcl 转换示例 (Tcl Conversion Example)"""
    print("\n=== Tcl 转换示例 (Tcl Conversion Example) ===")
    
    # 创建一个 Python 字典
    config = {
        'server': {
            'host': 'localhost',
            'port': 8080
        },
        'database': {
            'url': 'postgres://localhost/db'
        },
        'flags': [1, 2, 3],
        'enabled': True
    }
    
    print(f"Original dict: {config}")
    
    # 转换为 Tcl 解释器
    interp = dict2tclinterp(config)
    
    # 访问 Tcl 变量
    host = interp.eval('set server(host)')
    port = interp.eval('set server(port)')
    flags = interp.eval('set flags')
    
    print(f"Tcl variables - host: {host}, port: {port}, flags: {flags}")
    
    # 转换回 Python 字典
    result = tclinterp2dict(interp)
    print(f"Converted back to dict: {result}")

def example_file_conversion():
    """文件转换示例 (File Conversion Example)"""
    print("\n=== 文件转换示例 (File Conversion Example) ===")
    
    # 创建临时 YAML 文件
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_file:
        yaml_content = {
            'server': {
                'host': 'localhost',
                'port': 8080
            },
            'database': {
                'url': 'postgres://localhost/db'
            },
            'flags': [1, 2, 3],
            'enabled': True
        }
        yaml.dump(yaml_content, yaml_file)
        yaml_path = yaml_file.name
    
    # 创建临时 Tcl 文件路径
    tcl_path = yaml_path + '.tcl'
    
    try:
        # YAML 转 Tcl
        print(f"Converting YAML to Tcl: {yaml_path} -> {tcl_path}")
        yamlfiles2tclfile(yaml_path, output_file=tcl_path)
        
        # 读取 Tcl 文件内容
        with open(tcl_path, 'r', encoding='utf-8') as f:
            tcl_content = f.read()
        print(f"Tcl file content (excerpt):\n{tcl_content[:200]}...")
        
        # Tcl 转回 YAML
        yaml_path2 = tcl_path + '.yaml'
        print(f"Converting Tcl back to YAML: {tcl_path} -> {yaml_path2}")
        tclfiles2yamlfile(tcl_path, output_file=yaml_path2)
        
        # 读取新 YAML 文件内容
        with open(yaml_path2, 'r', encoding='utf-8') as f:
            yaml_content2 = yaml.safe_load(f)
        print(f"Converted YAML content: {yaml_content2}")
        
        # 使用 files2dict 直接加载
        print("Loading files directly to dict:")
        result_dict = files2dict(yaml_path, tcl_path)
        print(f"Result dict: {result_dict}")
        
    finally:
        # 清理临时文件
        for path in [yaml_path, tcl_path, yaml_path2]:
            if os.path.exists(path):
                os.remove(path)

def example_variable_references():
    """YAML 变量引用示例 (YAML Variable References Example)"""
    print("\n=== YAML 变量引用示例 (YAML Variable References Example) ===")
    
    # 创建包含变量引用的 YAML 文件
    yaml_content = """
# 简单变量引用
base_port: 8080
server_port: $base_port
api_port: ${base_port}

# 嵌套字典引用
database:
  host: localhost
  port: 5432
db_url: "postgres://${database(host)}:${database(port)}/mydb"

# 深层嵌套引用
app:
  config:
    timeout: 30
timeout_value: $app(config,timeout)

# 字符串中的变量引用
prefix: "http://"
suffix: "/api"
api_url: "${prefix}example.com${suffix}"
"""
    
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_file:
        yaml_file.write(yaml_content)
        yaml_path = yaml_file.name
    
    try:
        # 加载 YAML 文件（默认启用变量展开）
        config = yamlfiles2dict(yaml_path)
        
        print("YAML 内容:")
        print(yaml_content)
        print("\n解析结果（变量已展开）:")
        for key, value in config.items():
            print(f"  {key}: {repr(value)}")
        
        print("\n验证变量引用:")
        print(f"  base_port = {config.get('base_port')}")
        print(f"  server_port = {config.get('server_port')} (引用 base_port)")
        print(f"  api_port = {config.get('api_port')} (引用 base_port)")
        print(f"  db_url = {config.get('db_url')} (引用 database(host) 和 database(port))")
        print(f"  timeout_value = {config.get('timeout_value')} (引用 app(config,timeout))")
        print(f"  api_url = {config.get('api_url')} (引用 prefix 和 suffix)")
        
        # 测试禁用变量展开
        print("\n禁用变量展开:")
        config_no_expand = yamlfiles2dict(yaml_path, expand_variables=False)
        print(f"  server_port (未展开) = {config_no_expand.get('server_port')}")
        
    finally:
        if os.path.exists(yaml_path):
            os.remove(yaml_path)

if __name__ == "__main__":
    print("ConfigKit 使用示例 (Usage Examples)")
    example_dict_operations()
    example_tcl_conversion()
    example_file_conversion()
    example_variable_references()
