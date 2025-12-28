#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI Branch 相关处理函数
"""

import sys
from pathlib import Path

from ...workflow_manager import WorkflowManager
from ..utils import get_current_user
from ..init.workspace_helpers import (
    infer_params_from_path,
    validate_block,
    format_workspace_output
)
from ..init.params import infer_params_from_version_file


def handle_create_branch(manager: WorkflowManager, args) -> int:
    """处理 -b/--branch 命令（创建分支）"""
    try:
        current_dir = Path.cwd()
        
        version = getattr(args, 'version', None)
        
        # 如果未提供 work_path, project, version, block，尝试从当前目录推断
        if not (args.work_path and args.project and version and args.block):
            try:
                # 方法1：尝试使用 detect_project_path（适用于 block 目录或更深）
                detected = infer_params_from_path(manager, current_dir, args)
                
                # 方法2：如果方法1失败，尝试查找 .edp_version 文件
                if not detected:
                    # 使用统一的推断函数（返回 bool）
                    success = infer_params_from_version_file(args, manager, current_dir)
                    if success:
                        # 如果成功，构建检测结果字典（保持兼容性）
                        version = getattr(args, 'version', None)
                        detected = {'project_name': args.project, 'version': version}
                        if args.block:
                            detected['block'] = args.block
                        if args.user:
                            detected['user'] = args.user
                
                if not detected:
                    # 如果无法推断，但提供了部分参数，尝试继续
                    version = getattr(args, 'version', None)
                    if not (args.work_path and args.project and version and args.block):
                        print("[ERROR] 无法从当前目录推断项目信息", file=sys.stderr)
                        print("[ERROR] 请显式提供参数，例如：", file=sys.stderr)
                        print("[ERROR]   edp -b branch_name -prj dongting -v ABC --block block1 --user user1", file=sys.stderr)
                        print("[ERROR] 或者在 user 目录下运行：edp -b branch_name", file=sys.stderr)
                        return 1
            except Exception as e:
                print(f"[WARN] 路径推断失败: {e}，尝试使用提供的参数")
                import traceback
                traceback.print_exc()
        
        # 如果仍未提供 user，尝试使用当前系统用户
        version = getattr(args, 'version', None)
        if not args.user:
            if not (args.work_path and args.project and version and args.block):
                print("[ERROR] 无法推断 user，请显式指定 --user 参数", file=sys.stderr)
                print("[ERROR] 例如：edp -b branch_name --user user1", file=sys.stderr)
                return 1
            args.user = get_current_user()
            print(f"[OK] 使用当前系统用户: {args.user}")
        
        # 确保 work_path 是绝对路径
        work_path = Path(args.work_path or '.').resolve()
        
        # 验证 block 是否存在且合法
        if not validate_block(work_path, args.project, version, args.block):
            return 1
        
        # 检查 branch 是否已存在
        branch_path = work_path / args.project / version / args.block / args.user / args.branch
        if branch_path.exists():
            print(f"[WARN] 分支 '{args.branch}' 已存在: {branch_path}", file=sys.stderr)
            
            # 检查是否指定了 from_branch_step
            if args.from_branch_step:
                print(f"[WARN] 如果继续，将更新现有分支结构：", file=sys.stderr)
                print(f"  - 基础目录结构：只创建缺失的目录和文件（不会删除现有内容）", file=sys.stderr)
                print(f"  - 从源分支链接/复制的目录（cmds, dbs, flow, hooks, logs, rpts）：", file=sys.stderr)
                print(f"    如果这些目录已存在，将被删除并重新创建（覆盖现有内容）", file=sys.stderr)
            else:
                print(f"[WARN] 如果继续，将更新现有分支结构（只创建缺失的目录和文件，不会删除现有内容）", file=sys.stderr)
            
            print(f"[INFO] 如需创建新分支，请使用不同的分支名称", file=sys.stderr)
            print(f"[INFO] 如需删除现有分支，请手动删除: {branch_path}", file=sys.stderr)
            
            # 询问用户是否继续
            try:
                response = input("\n是否继续？(y/n): ").strip().lower()
                if response not in ['y', 'yes', '是']:
                    print("[INFO] 已取消操作", file=sys.stderr)
                    return 1
            except (EOFError, KeyboardInterrupt):
                # 非交互式环境或用户中断
                print("\n[INFO] 已取消操作（非交互式环境或用户中断）", file=sys.stderr)
                return 1
        
        # 初始化工作空间
        version = getattr(args, 'version', None)
        paths = manager.init_user_workspace(
            work_path=str(work_path),
            project=args.project,
            version=version,
            block=args.block,
            user=args.user,
            branch=args.branch,
            foundry=args.foundry,
            node=args.node,
            from_branch_step=args.from_branch_step
        )
        print("[OK] 用户工作空间初始化成功！")
        print()
        
        # 格式化输出
        format_workspace_output(paths)
        
        return 0
    except Exception as e:
        print(f"[ERROR] 用户工作空间初始化失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

