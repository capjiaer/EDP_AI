#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 命令主处理器
实现 edp -release 功能的主入口
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from .release_step_parser import parse_steps
from .release_step_processor import release_single_step
from .release_version_manager import ensure_version_unique


def handle_release_cmd(manager, args) -> int:
    """
    处理 -release 命令（支持多步骤）
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    try:
        # 1. 验证必需参数
        if not args.release_version:
            print("错误: 必须指定 --release-version 参数（如 --release-version v09001）", file=sys.stderr)
            return 1
        
        if not args.release_step:
            print("错误: 必须指定至少一个 --step 参数（如 --step pnr_innovus.postroute）", file=sys.stderr)
            return 1
        
        # 2. 推断项目信息和工作路径信息
        current_dir = Path.cwd()
        from ...utils import infer_project_info, infer_work_path_info
        project_info = infer_project_info(manager, current_dir, args)
        
        if not project_info:
            print("错误: 无法推断项目信息，请确保在正确的目录下运行或显式指定参数", file=sys.stderr)
            return 1
        
        # 推断工作路径信息（包含 block, user, branch 等）
        work_path_info = infer_work_path_info(current_dir, args, project_info)
        
        if not work_path_info:
            print("错误: 无法推断工作路径信息，请确保在正确的目录下运行", file=sys.stderr)
            return 1
        
        work_path = Path(work_path_info.get('work_path', '.'))
        project = work_path_info.get('project') or project_info.get('project')
        version = work_path_info.get('version')
        block = args.release_block or work_path_info.get('block')
        user = work_path_info.get('user')
        branch = work_path_info.get('branch', 'main')
        
        if not block:
            print("错误: 无法推断 block 名称，请使用 --block 参数指定", file=sys.stderr)
            return 1
        
        if not user:
            print("错误: 无法推断 user 名称", file=sys.stderr)
            return 1
        
        # 3. 构建路径
        branch_dir = work_path / project / version / block / user / branch
        if not branch_dir.exists():
            print(f"错误: 分支目录不存在: {branch_dir}", file=sys.stderr)
            return 1
        
        # 4. 解析步骤列表（支持多步骤和 release 整个 flow）
        foundry = project_info.get('foundry')
        node = project_info.get('node')
        parsed_steps = parse_steps(args.release_step, manager, foundry, node, project)
        
        if not parsed_steps:
            print("错误: 没有找到有效的步骤", file=sys.stderr)
            return 1
        
        # 去重
        parsed_steps = list(set(parsed_steps))
        
        # 5. 确定 RELEASE 目录
        release_root = work_path / project / version / 'RELEASE' / block / user
        release_root.mkdir(parents=True, exist_ok=True)
        
        # 6. 处理版本号唯一性（支持追加模式）
        base_version = args.release_version
        final_version, operation_type, existing_steps, append_steps, overwrite_steps = ensure_version_unique(
            release_root, base_version, parsed_steps, args.strict, args.append, args.overwrite
        )
        
        release_dir = release_root / final_version
        release_dir.mkdir(parents=True, exist_ok=True)
        data_target_dir = release_dir / 'data'
        data_target_dir.mkdir(exist_ok=True)
        
        # 7. 输出操作类型和步骤信息
        print(f"\n[INFO] RELEASE 版本: {final_version}")
        print(f"[INFO] RELEASE 目录: {release_dir}")
        
        if operation_type == 'new':
            print(f"[INFO] 操作类型: 创建新版本")
            print(f"[INFO] 将添加 {len(parsed_steps)} 个步骤: {[f'{f}.{s}' for f, s in parsed_steps]}")
        elif operation_type == 'timestamp':
            print(f"[INFO] 操作类型: 创建新版本（版本 {base_version} 已存在，自动添加时间戳）")
            print(f"[INFO] 最终版本号: {final_version}")
            print(f"[INFO] 将添加 {len(parsed_steps)} 个步骤: {[f'{f}.{s}' for f, s in parsed_steps]}")
            print(f"[INFO] 提示: 如需追加到现有版本，请使用 --append 选项")
        elif operation_type == 'append':
            print(f"[INFO] 操作类型: 追加到现有版本")
            if existing_steps:
                print(f"[INFO] 已存在的步骤: {existing_steps}")
            if append_steps:
                print(f"[INFO] 将追加 {len(append_steps)} 个新步骤: {append_steps}")
        elif operation_type == 'overwrite':
            print(f"[INFO] 操作类型: 覆盖现有步骤")
            if existing_steps:
                print(f"[INFO] 已存在的步骤: {existing_steps}")
            if overwrite_steps:
                print(f"[INFO] 将覆盖 {len(overwrite_steps)} 个步骤: {overwrite_steps}")
            if append_steps:
                print(f"[INFO] 将追加 {len(append_steps)} 个新步骤: {append_steps}")
        
        print(f"\n[INFO] 开始处理步骤...")
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for idx, (flow_name, step_name) in enumerate(parsed_steps, 1):
            step_dir_name = f"{flow_name}.{step_name}"
            
            # 判断步骤操作类型
            step_operation = 'new'
            if step_dir_name in existing_steps:
                if step_dir_name in overwrite_steps:
                    step_operation = 'overwrite'
                else:
                    step_operation = 'skip'  # 已存在但不覆盖，应该不会到这里
            
            print(f"\n[INFO] 处理步骤 {idx}/{len(parsed_steps)}: {step_dir_name}")
            if step_operation == 'overwrite':
                print(f"[INFO] 操作: 覆盖已存在的步骤")
            elif step_dir_name in existing_steps:
                print(f"[INFO] 操作: 跳过（已存在）")
            else:
                print(f"[INFO] 操作: 添加新步骤")
            
            try:
                result = release_single_step(
                    manager, args, branch_dir, release_dir, data_target_dir,
                    flow_name, step_name, project_info, project
                )
                
                if result == 'success':
                    success_count += 1
                    if step_operation == 'overwrite':
                        print(f"[INFO] 步骤 {step_dir_name} 覆盖完成")
                    else:
                        print(f"[INFO] 步骤 {step_dir_name} 添加完成")
                elif result == 'skip':
                    skip_count += 1
                    print(f"[INFO] 步骤 {step_dir_name} 已跳过")
                else:
                    error_count += 1
                    print(f"[ERROR] 步骤 {step_dir_name} 处理失败")
                    
            except Exception as e:
                error_count += 1
                if args.strict:
                    print(f"[ERROR] 步骤 {step_dir_name} 处理失败: {e}", file=sys.stderr)
                    raise
                else:
                    print(f"[WARN] 步骤 {step_dir_name} 处理失败: {e}，跳过", file=sys.stderr)
        
        # 9. 创建共享的 release_note.txt
        if args.release_note:
            release_note_path = release_dir / 'release_note.txt'
            release_note_path.write_text(args.release_note, encoding='utf-8')
            print(f"\n[INFO] 已创建 release_note.txt")
        
        # 10. 设置只读权限
        from .release_file_operations import set_readonly
        set_readonly(release_dir)
        
        # 11. 输出总结
        operation_type_names = {
            'new': '创建新版本',
            'timestamp': '创建新版本（带时间戳）',
            'append': '追加到现有版本',
            'overwrite': '覆盖现有步骤'
        }
        operation_name = operation_type_names.get(operation_type, operation_type)
        
        print(f"\n{'='*60}")
        print(f"[INFO] RELEASE 操作完成")
        print(f"[INFO] RELEASE 版本: {final_version}")
        if operation_type == 'timestamp':
            print(f"[INFO] 基础版本号: {base_version}")
        print(f"[INFO] RELEASE 目录: {release_dir}")
        print(f"[INFO] 操作类型: {operation_name}")
        if existing_steps:
            print(f"[INFO] 已存在的步骤: {existing_steps}")
        print(f"[INFO] 统计: 成功 {success_count}, 跳过 {skip_count}, 失败 {error_count}")
        print(f"{'='*60}")
        
        if error_count > 0:
            return 1
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

