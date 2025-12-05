#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI Init 相关处理函数
"""

import sys
from pathlib import Path

from ...workflow_manager import WorkflowManager
from ..utils import get_current_user
from ..init import (
    infer_params_from_version_file,
    load_config_file,
    merge_params,
    validate_required_params,
    process_blocks_config,
    init_project_structure,
    create_user_directories,
    validate_init_permission
)


def handle_init_project(manager: WorkflowManager, args) -> int:
    """处理 init 命令（初始化到 user 级别）"""
    # 如果指定了 --gui，启动 GUI
    if getattr(args, 'gui', False):
        try:
            # 先检查 PyQt5 是否可用
            try:
                from PyQt5.QtWidgets import QApplication
            except ImportError as e:
                print(f"[ERROR] PyQt5 未安装或导入失败: {e}", file=sys.stderr)
                print("[INFO] 请安装 PyQt5: pip install PyQt5", file=sys.stderr)
                return 1
            
            # 导入 GUI 模块
            from ..gui import run_gui
            # 使用 manager 的 edp_center 路径（manager 已经通过 command_router 创建，包含了正确的路径）
            edp_center_path = manager.edp_center if hasattr(manager, 'edp_center') else None
            run_gui(edp_center_path)
            return 0
        except ImportError as e:
            print(f"[ERROR] 导入 GUI 模块失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        except Exception as e:
            print(f"[ERROR] 启动 GUI 失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    try:
        # 1. 如果参数缺失，尝试从 .edp_version 文件推断
        version = getattr(args, 'version', None)
        if not args.project or not version:
            infer_params_from_version_file(args, manager)
            version = getattr(args, 'version', None)
        
        # 2. 加载 config.yaml 文件
        work_path = Path(args.work_path).resolve()
        config_path = Path(args.config).resolve() if getattr(args, 'config', None) else None
        config = load_config_file(work_path, config_path)
        
        # 如果从 .edp_version 推断出了 work_path，重新加载 config.yaml
        if args.work_path:
            work_path = Path(args.work_path).resolve()
            config = load_config_file(work_path, config_path)
        
        # 3. 合并参数
        project, version, block, user = merge_params(args, config)
        
        # 4. 验证必需参数
        if not validate_required_params(project, version):
            return 1
        
        # 5. 验证是否允许在此路径执行 init
        is_allowed, error_msg = validate_init_permission(
            work_path=work_path,
            project=project,
            foundry=args.foundry,
            node=args.node,
            manager=manager,
            config_yaml=config
        )
        if not is_allowed:
            print(f"[ERROR] 不允许在此路径执行 init 操作", file=sys.stderr)
            if error_msg:
                print(f"[ERROR] {error_msg}", file=sys.stderr)
            print(f"[INFO] 当前工作路径: {work_path}", file=sys.stderr)
            print(f"[INFO] 请联系管理员配置 allowed_work_paths", file=sys.stderr)
            return 1
        
        # 6. 检查是否已经初始化过（在检查 blocks_to_init 之前）
        project_base_path = work_path / project / version
        version_info_file = project_base_path / '.edp_version'
        already_initialized = False
        existing_blocks = set()
        existing_users = {}
        
        if version_info_file.exists():
            try:
                import yaml
                with open(version_info_file, 'r', encoding='utf-8') as f:
                    version_info = yaml.safe_load(f) or {}
                if version_info.get('blocks'):
                    already_initialized = True
                    existing_blocks = set(version_info['blocks'].keys())
                    # 收集已存在的用户
                    for blk_name, blk_info in version_info['blocks'].items():
                        if isinstance(blk_info, dict) and 'users' in blk_info:
                            existing_users[blk_name] = set(blk_info['users'].keys())
            except Exception:
                pass
        
        # 7. 如果已经初始化过，且用户没有明确指定 --block 参数，直接提示并返回
        # 这样可以避免从 config.yaml 读取 blocks 配置，导致重复初始化
        if already_initialized and not args.block:
            print(f"\n[INFO] 检测到项目 '{project}/{version}' 已经初始化过", file=sys.stderr)
            if existing_blocks:
                print(f"[INFO] 已存在的 blocks: {', '.join(sorted(existing_blocks))}", file=sys.stderr)
                # 显示每个 block 下的 users
                for blk_name in sorted(existing_blocks):
                    users_in_block = existing_users.get(blk_name, set())
                    if users_in_block:
                        print(f"[INFO]   - {blk_name}: {', '.join(sorted(users_in_block))}", file=sys.stderr)
            
            print(f"\n[INFO] 提示：", file=sys.stderr)
            print(f"[INFO]   1. 如果要初始化新的 block，请使用: edp -init -blk <block_name>", file=sys.stderr)
            print(f"[INFO]   2. 如果要初始化新的 user，请使用: edp -init -blk <block_name> -user <user_name>", file=sys.stderr)
            print(f"[INFO]   3. 如果要在 WORK_PATH 根目录初始化整个项目，请使用: edp -init", file=sys.stderr)
            print(f"[INFO]      （需要在 WORK_PATH 根目录下有 config.yaml 文件）", file=sys.stderr)
            return 0
        
        # 8. 处理 blocks 配置
        # 从 project 下读取 blocks 配置
        project_config = config.get('project', {}) if config else {}
        if not isinstance(project_config, dict):
            print("[ERROR] config.yaml 格式错误：project 必须是字典格式", file=sys.stderr)
            return 1
        
        blocks_config = project_config.get('blocks', {})
        blocks_to_init = process_blocks_config(block, user, blocks_config)
        
        # 9. 如果已经初始化过，但没有指定新的 block/user，给出友好的提示
        if already_initialized and not blocks_to_init:
            print(f"\n[INFO] 检测到项目 '{project}/{version}' 已经初始化过", file=sys.stderr)
            if existing_blocks:
                print(f"[INFO] 已存在的 blocks: {', '.join(sorted(existing_blocks))}", file=sys.stderr)
                # 显示每个 block 下的 users
                for blk_name in sorted(existing_blocks):
                    users_in_block = existing_users.get(blk_name, set())
                    if users_in_block:
                        print(f"[INFO]   - {blk_name}: {', '.join(sorted(users_in_block))}", file=sys.stderr)
            
            print(f"\n[INFO] 提示：", file=sys.stderr)
            print(f"[INFO]   1. 如果要初始化新的 block，请使用: edp -init -blk <block_name>", file=sys.stderr)
            print(f"[INFO]   2. 如果要初始化新的 user，请使用: edp -init -blk <block_name> -user <user_name>", file=sys.stderr)
            print(f"[INFO]   3. 如果要在 WORK_PATH 根目录初始化整个项目，请使用: edp -init", file=sys.stderr)
            print(f"[INFO]      （需要在 WORK_PATH 根目录下有 config.yaml 文件）", file=sys.stderr)
            return 0
        
        if not blocks_to_init:
            print("[ERROR] 错误: 缺少 --block 参数，且 config.yaml 中未找到 blocks 或 block", file=sys.stderr)
            if already_initialized:
                print(f"[INFO] 提示：项目 '{project}/{version}' 已经初始化过", file=sys.stderr)
                print(f"[INFO] 如果要初始化新的 block，请使用: edp -init -blk <block_name>", file=sys.stderr)
            return 1
        
        # 10. 检查是否有重复的 block 或 user
        new_blocks = []
        new_users = {}
        existing_items = []
        
        for blk_name, users in blocks_to_init.items():
            if blk_name in existing_blocks:
                # block 已存在，检查 user
                existing_users_in_block = existing_users.get(blk_name, set())
                new_users_in_block = []
                for usr in users:
                    if usr in existing_users_in_block:
                        existing_items.append(f"{project}/{version}/{blk_name}/{usr}")
                    else:
                        new_users_in_block.append(usr)
                if new_users_in_block:
                    new_users[blk_name] = new_users_in_block
            else:
                # block 不存在，需要初始化
                new_blocks.append(blk_name)
                new_users[blk_name] = users
        
        # 11. 如果有已存在的项目，提醒用户
        if already_initialized:
            print(f"\n[INFO] 检测到项目 '{project}/{version}' 已经初始化过", file=sys.stderr)
            if existing_blocks:
                print(f"[INFO] 已存在的 blocks: {', '.join(sorted(existing_blocks))}", file=sys.stderr)
            if existing_items:
                print(f"[WARN] 以下 user 目录已存在，将跳过（不会覆盖）:", file=sys.stderr)
                for item in sorted(existing_items):
                    print(f"  - {item}", file=sys.stderr)
            if new_blocks or new_users:
                print(f"[INFO] 将初始化新的内容:", file=sys.stderr)
                if new_blocks:
                    print(f"  - 新的 blocks: {', '.join(sorted(new_blocks))}", file=sys.stderr)
                if new_users:
                    for blk_name, users in new_users.items():
                        print(f"  - {blk_name} 下的新 users: {', '.join(sorted(users))}", file=sys.stderr)
                print(f"[INFO] 注意：重复 init 不会覆盖已存在的目录和文件（安全模式）", file=sys.stderr)
                print()  # 空行分隔
        
        # 12. 初始化项目结构（如果还没有）
        if new_blocks:
            init_project_structure(manager, work_path, project, version, new_blocks, args.foundry, args.node)
        
        # 13. 创建用户目录并设置权限（只创建新的）
        if new_users:
            initialized_count = create_user_directories(work_path, project, version, new_users)
            print(f"\n[OK] 总共初始化了 {initialized_count} 个新的 user 目录")
        else:
            if existing_items:
                print(f"\n[INFO] 所有指定的 user 目录都已存在，无需重复初始化", file=sys.stderr)
            else:
                print(f"\n[OK] 项目结构已存在，无需重复初始化", file=sys.stderr)
        
        return 0
    except Exception as e:
        print(f"[ERROR] 初始化失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

