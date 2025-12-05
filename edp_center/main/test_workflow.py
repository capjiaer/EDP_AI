#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 WorkflowManager 的工作流加载功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'edp_center' / 'packages' / 'edp_configkit'))

from edp_center.main.workflow_manager import WorkflowManager

def test_load_workflow():
    """测试工作流加载"""
    print("=" * 60)
    print("测试 WorkflowManager 工作流加载")
    print("=" * 60)
    
    # 创建 WorkflowManager
    try:
        manager = WorkflowManager('edp_center')
        print("✅ WorkflowManager 初始化成功\n")
    except Exception as e:
        print(f"❌ WorkflowManager 初始化失败: {e}")
        return
    
    # 获取所有 dependency.yaml 文件
    try:
        dependency_files = manager._get_all_dependency_files('SAMSUNG', 'S8', 'dongting', flow=None)
        print(f"找到 {len(dependency_files)} 个 dependency.yaml 文件:")
        for f in dependency_files:
            print(f"  - {f}")
        print()
    except Exception as e:
        print(f"❌ 获取 dependency 文件失败: {e}")
        return
    
    # 加载工作流
    try:
        graph = manager.load_workflow('SAMSUNG', 'S8', 'dongting', flow=None)
        print(f"✅ 工作流加载成功，包含 {len(graph.steps)} 个步骤\n")
    except Exception as e:
        print(f"❌ 工作流加载失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 显示步骤列表
    print("步骤列表:")
    for step_name in sorted(graph.steps.keys()):
        step = graph.steps[step_name]
        print(f"  - {step_name}:")
        print(f"      in: {step.inputs}")
        print(f"      out: {step.outputs}")
        print(f"      cmd: {step.cmd}")
    print()
    
    # 显示依赖关系
    print("依赖关系:")
    has_deps = False
    for step_name, deps in graph.dependencies.items():
        if deps['prev'] or deps['next']:
            has_deps = True
            print(f"  - {step_name}:")
            if deps['prev']:
                print(f"      前置: {deps['prev']}")
            if deps['next']:
                print(f"      后置: {deps['next']}")
    
    if not has_deps:
        print("  (无依赖关系)")
    
    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 验证跨 flow 依赖（通过文件匹配）
    print("\n验证跨 flow 依赖（文件匹配机制）:")
    print("  - pnr_innovus 的 postroute 步骤输出: postroute.pass")
    print("  - pv_calibre 的 ipmerge 步骤需要: postroute.pass")
    
    if 'postroute' in graph.steps and 'ipmerge' in graph.steps:
        postroute_step = graph.steps['postroute']
        ipmerge_step = graph.steps['ipmerge']
        
        if 'postroute.pass' in postroute_step.outputs and 'postroute.pass' in ipmerge_step.inputs:
            print("  ✅ 文件匹配成功：postroute.pass 匹配")
            
            # 检查依赖关系
            if 'postroute' in graph.dependencies.get('ipmerge', {}).get('prev', []):
                print("  ✅ 跨 flow 依赖已自动建立：postroute -> ipmerge")
                print("  ✅ 文件匹配机制正常工作！")
            else:
                print("  ⚠️  依赖关系未正确建立（可能需要检查 Graph 的依赖构建逻辑）")
        else:
            print("  ⚠️  文件匹配检查：")
            print(f"     postroute 输出: {postroute_step.outputs}")
            print(f"     ipmerge 输入: {ipmerge_step.inputs}")
    else:
        print("  ⚠️  步骤未找到")

if __name__ == '__main__':
    test_load_workflow()

