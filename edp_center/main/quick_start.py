#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
快速开始示例
演示如何使用 WorkflowManager
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'edp_center' / 'packages' / 'edp_configkit'))

from edp_center.main import WorkflowManager

def example_1_init_workspace():
    """示例 1: 初始化用户工作空间"""
    print("=" * 60)
    print("示例 1: 初始化用户工作空间")
    print("=" * 60)
    
    manager = WorkflowManager('edp_center')
    
    paths = manager.init_user_workspace(
        work_path='WORK_PATH',
        project='dongting',
        project_node='P85',
        block='block1',
        user='zhangsan',
        branch='branch1'
    )
    
    print("✅ 工作空间初始化成功！")
    print(f"创建的目录：{paths}")
    print()


def example_2_load_config():
    """示例 2: 加载配置"""
    print("=" * 60)
    print("示例 2: 加载配置")
    print("=" * 60)
    
    manager = WorkflowManager('edp_center')
    
    # 获取项目信息
    project_info = manager.work_path_initializer.get_project_info('dongting')
    foundry = project_info['foundry']
    node = project_info['node']
    
    config = manager.load_config(
        foundry=foundry,
        node=node,
        project='dongting',
        flow='pv_calibre'
    )
    
    print("✅ 配置加载成功！")
    print(f"配置键：{list(config.keys())}")
    print()


def example_3_process_script():
    """示例 3: 处理脚本"""
    print("=" * 60)
    print("示例 3: 处理脚本（展开 #import 指令）")
    print("=" * 60)
    
    manager = WorkflowManager('edp_center')
    
    # 假设脚本路径（使用 steps/ 目录）
    script_path = Path('edp_center/flow/initialize/SAMSUNG/S8/dongting/cmds/pv_calibre/steps/ipmerge.tcl')
    
    if script_path.exists():
        result = manager.process_script(
            input_file=str(script_path),
            output_file='output/ipmerge_expanded.tcl',
            prepend_default_sources=True
        )
        print("✅ 脚本处理成功！")
        print(f"输出文件：output/ipmerge_expanded.tcl")
    else:
        print(f"⚠️  脚本文件不存在：{script_path}")
    print()


def example_4_load_workflow():
    """示例 4: 加载工作流"""
    print("=" * 60)
    print("示例 4: 加载工作流（自动发现跨 flow 依赖）")
    print("=" * 60)
    
    manager = WorkflowManager('edp_center')
    
    # 获取项目信息
    project_info = manager.work_path_initializer.get_project_info('dongting')
    foundry = project_info['foundry']
    node = project_info['node']
    
    # 加载所有 flow 的 dependency.yaml
    graph = manager.load_workflow(
        foundry=foundry,
        node=node,
        project='dongting',
        flow=None  # None 表示加载所有 flow
    )
    
    print(f"✅ 工作流加载成功！")
    print(f"包含 {len(graph.steps)} 个步骤")
    print(f"步骤列表：{list(graph.steps.keys())}")
    print()


def example_5_run_full_workflow():
    """示例 5: 执行完整工作流"""
    print("=" * 60)
    print("示例 5: 执行完整工作流")
    print("=" * 60)
    
    manager = WorkflowManager('edp_center')
    
    print("注意：这个示例需要实际的工作路径和配置")
    print("实际使用时，取消注释下面的代码：")
    print()
    print("""
    results = manager.run_full_workflow(
        work_path='WORK_PATH',
        project='dongting',
        project_node='P85',
        block='block1',
        user='zhangsan',
        branch='branch1',
        flow='pv_calibre'
    )
    print(f"✅ 工作流执行完成！结果：{results}")
    """)


def example_6_from_branch():
    """示例 6: 从已有分支创建新分支"""
    print("=" * 60)
    print("示例 6: 从已有分支创建新分支")
    print("=" * 60)
    
    manager = WorkflowManager('edp_center')
    
    paths = manager.init_user_workspace(
        work_path='WORK_PATH',
        project='dongting',
        project_node='P85',
        block='block1',
        user='zhangsan',
        branch='branch2',
        from_branch_step='branch1:pnr_innovus.init'  # 从 branch1 的 pnr_innovus.init 创建
    )
    
    print("✅ 从已有分支创建新分支成功！")
    print(f"创建的目录：{paths}")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("EDP Main 使用示例")
    print("=" * 60 + "\n")
    
    try:
        example_1_init_workspace()
        example_2_load_config()
        example_3_process_script()
        example_4_load_workflow()
        example_5_run_full_workflow()
        example_6_from_branch()
        
        print("\n" + "=" * 60)
        print("所有示例演示完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 示例执行出错：{e}")
        import traceback
        traceback.print_exc()

