#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单个步骤执行模块
处理单个步骤的执行逻辑
"""

import sys
import logging
import os
import shutil
from pathlib import Path
from io import TextIOWrapper
from datetime import datetime

from ..utils import (
    infer_project_info, infer_work_path_info,
    find_source_script,
    generate_full_tcl, list_available_flows,
    get_cmd_filename_from_dependency,
    validate_work_path_info
)
from .common_handlers import show_project_list
from .run_helpers import (
    get_used_hooks,
    update_run_info,
    create_hooks_files
)
from .info_handler import show_flow_status

# 获取 logger
logger = logging.getLogger(__name__)


def execute_single_step(manager, args, flow_step: str) -> int:
    """
    执行单个步骤（内部函数，用于避免递归调用）
    
    Args:
        manager: WorkflowManager 实例
        args: 命令行参数对象
        flow_step: 步骤名称（格式: flow.step）
        
    Returns:
        退出代码（0 表示成功，非 0 表示失败）
    """
    try:
        # 解析 flow.step 格式
        if '.' not in flow_step:
            print(f"[ERROR] 无效的格式: {flow_step}", file=sys.stderr)
            print(f"[INFO] 格式应为: <flow_name>.<step_name>，例如: pv_calibre.ipmerge", file=sys.stderr)
            print(f"[INFO] 或使用: edp -info <flow_name> 查看该 flow 下所有 step", file=sys.stderr)
            logger.error(f"无效的格式: {flow_step}", extra={'flow_step': flow_step})
            return 1
        
        parts = flow_step.split('.', 1)
        flow_name = parts[0]
        step_name = parts[1]
        
        # 获取当前工作目录
        current_dir = Path.cwd().resolve()
        
        # 推断项目信息（从当前目录或 .edp_version 文件）
        project_info = infer_project_info(manager, current_dir, args)
        if not project_info:
            print(f"[ERROR] 无法推断项目信息，请确保在正确的工作目录下运行", file=sys.stderr)
            print(f"[INFO] 或者手动指定: --edp-center, --project, --foundry, --node", file=sys.stderr)
            
            logger.error("无法推断项目信息", extra={'current_dir': str(current_dir)})
            
            # 显示支持的 project 列表
            show_project_list(manager, current_dir, args)
            
            return 1
        
        edp_center_path = project_info['edp_center_path']
        foundry = project_info['foundry']
        node = project_info['node']
        project = project_info.get('project')  # 可能为 None（使用 common）
        
        # 从 dependency.yaml 获取 cmd 文件名（可能包含扩展名，如 .tcl, .py 等）
        cmd_filename = get_cmd_filename_from_dependency(edp_center_path, foundry, node, project, flow_name, step_name)
        
        # 构建源文件路径（优先项目特定，否则使用 common）
        # 使用 cmd_filename 支持 .tcl, .py 等扩展名
        source_script = find_source_script(
            edp_center_path, foundry, node, project, flow_name, step_name,
            cmd_filename=cmd_filename
        )
        if not source_script:
            print(f"[ERROR] 找不到源脚本文件", file=sys.stderr)
            print(f"[INFO] 查找路径:", file=sys.stderr)
            # 使用 cmd_filename 或默认的 {step_name}.tcl
            script_filename = cmd_filename if cmd_filename else f"{step_name}.tcl"
            if project:
                print(f"  - {edp_center_path}/flow/initialize/{foundry}/{node}/{project}/cmds/{flow_name}/steps/{script_filename}", file=sys.stderr)
            print(f"  - {edp_center_path}/flow/initialize/{foundry}/{node}/common/cmds/{flow_name}/steps/{script_filename}", file=sys.stderr)
            
            # 日志记录
            search_paths = []
            if project:
                search_paths.append(f"{edp_center_path}/flow/initialize/{foundry}/{node}/{project}/cmds/{flow_name}/steps")
            search_paths.append(f"{edp_center_path}/flow/initialize/{foundry}/{node}/common/cmds/{flow_name}/steps")
            
            logger.error("找不到源脚本文件", extra={
                'flow_name': flow_name,
                'step_name': step_name,
                'cmd_filename': cmd_filename,
                'script_filename': script_filename,
                'search_paths': search_paths
            })
            
            # 检查 dependency.yaml 中是否已声明这个 step
            if cmd_filename:
                print(f"\n[WARN] 该 step 已在 dependency.yaml 中声明，但源脚本文件尚未准备好", file=sys.stderr)
                print(f"[WARN] dependency.yaml 中声明的 cmd: {cmd_filename}", file=sys.stderr)
                print(f"[INFO] 请联系 flow owner 准备源脚本文件", file=sys.stderr)
                logger.warning("该 step 已在 dependency.yaml 中声明，但源脚本文件尚未准备好", extra={
                    'flow_name': flow_name,
                    'step_name': step_name,
                    'cmd_filename': cmd_filename
                })
            else:
                # 如果 dependency.yaml 中也没有声明，说明这个 step 不存在
                print(f"\n[INFO] 可用的 flow 和 step:", file=sys.stderr)
                available_flows = list_available_flows(edp_center_path, foundry, node, project)
                if available_flows:
                    for flow, steps_info in sorted(available_flows.items()):
                        # steps_info 是字典，key 是 step_name，value 是 {'ready': bool, 'cmd': str}
                        ready_steps = [step for step, info in steps_info.items() if info.get('ready', False)]
                        not_ready_steps = [step for step, info in steps_info.items() if not info.get('ready', False)]
                        
                        if ready_steps:
                            ready_str = ', '.join(sorted(ready_steps))
                            print(f"  {flow}: {ready_str}", file=sys.stderr)
                        if not_ready_steps:
                            not_ready_str = ', '.join(sorted(not_ready_steps))
                            print(f"  {flow} (未就绪): {not_ready_str}", file=sys.stderr)
                else:
                    print(f"  (未找到可用的 flow)", file=sys.stderr)
            return 1
        
        # 推断工作路径信息（work_path, project, version, block, user, branch）
        # 用于生成 full.tcl 文件
        # 注意：必须找到 .edp_version 文件才能推断工作路径信息
        work_path_info = infer_work_path_info(current_dir, args, project_info)
        if not work_path_info:
            print(f"[ERROR] 无法推断工作路径信息：未找到 .edp_version 文件", file=sys.stderr)
            print(f"[INFO] 请确保在正确的工作目录下运行（从当前目录向上查找必须能找到 .edp_version 文件）", file=sys.stderr)
            print(f"[INFO] 当前工作目录: {current_dir}", file=sys.stderr)
            print(f"[INFO] .edp_version 文件应该位于: <work_path>/<project>/<version>/.edp_version", file=sys.stderr)
            return 1
        
        # 验证 work_path_info 是否完整
        is_complete, missing_fields = validate_work_path_info(work_path_info)
        if not is_complete:
            print(f"[ERROR] 缺少必要的工作路径信息:", file=sys.stderr)
            for field in missing_fields:
                field_name = {
                    'work_path': '--work-path',
                    'project': '--project 或 -prj',
                    'version': '--version 或 -v',
                    'block': '--block 或 -blk',
                    'user': '--user',
                    'branch': '--branch 或 -b'
                }.get(field, f'--{field}')
                print(f"  - {field}: 请使用 {field_name} 指定", file=sys.stderr)
            print(f"[INFO] 当前工作目录: {current_dir}", file=sys.stderr)
            print(f"[INFO] 请确保在正确的目录下运行，或手动指定缺失的参数", file=sys.stderr)
            return 1
        
        # 生成 full.tcl 文件
        try:
            full_tcl_path = generate_full_tcl(
                edp_center_path, foundry, node, project,
                work_path_info, flow_name, step_name, current_dir=current_dir
            )
        except ValueError as e:
            # 变量格式验证失败，直接返回错误码
            # 错误信息已经在 generate_full_tcl 中输出了
            return 1
        
        if not full_tcl_path:
            # full.tcl 生成失败（可能是其他错误）
            print(f"[ERROR] 无法生成 full.tcl，请检查错误信息并修复问题", file=sys.stderr)
            return 1
        
        print(f"[INFO] 已生成 full.tcl: {full_tcl_path}", file=sys.stderr)
        
        # 确定 branch 目录路径（用于创建 cmds 和 hooks 目录）
        if work_path_info and work_path_info.get('work_path') and work_path_info.get('project') and \
           work_path_info.get('version') and work_path_info.get('block') and \
           work_path_info.get('user') and work_path_info.get('branch'):
            work_path = Path(work_path_info['work_path']).resolve()
            project = work_path_info['project']
            version = work_path_info.get('version')
            block = work_path_info['block']
            user = work_path_info['user']
            branch = work_path_info['branch']
            
            # 构建 branch 目录路径
            branch_dir = work_path / project / version / block / user / branch
        else:
            # 如果无法推断 branch 目录，抛出异常
            raise ValueError(
                f"无法推断 branch 目录。请确保在正确的工作目录下运行，"
                f"或使用 --branch/-b 参数指定 branch 名称。"
                f"当前目录: {current_dir}"
            )
        
        # 构建输出文件路径（branch 目录下的 cmds/<flow_name>/<step_name>.tcl）
        output_dir = branch_dir / 'cmds' / flow_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{step_name}.tcl"
        
        # 构建 hooks 目录路径（统一使用 flow_name.step_name 格式）
        step_dir_name = f"{flow_name}.{step_name}"  # 统一格式：flow_name.step_name
        hooks_dir = branch_dir / 'hooks' / step_dir_name
        
        # 自动创建缺失的 hooks 文件（如果目录不存在，会创建目录；如果文件缺失，会重新创建）
        create_hooks_files(hooks_dir, step_name)
        
        # 在处理脚本之前，先读取配置检查 tool_opt
        # 如果是非 Tcl 工具（如 python），不应该自动 source Tcl 库
        should_prepend_sources = True
        merged_config = {}  # 初始化为空字典，避免未定义错误
        try:
            from edp_center.packages.edp_configkit import tclfiles2tclinterp, tclinterp2dict
            from edp_center.packages.edp_flowkit.flowkit.run_graph import get_flow_var
            from edp_center.packages.edp_flowkit.flowkit import Step
            
            # 读取 full.tcl 获取配置
            tcl_interp = tclfiles2tclinterp(str(full_tcl_path))
            merged_config = tclinterp2dict(tcl_interp, mode="auto")
            
            # 创建临时 Step 对象用于获取 tool_opt
            temp_step = Step(id=f"{flow_name}.{step_name}", cmd=f"{step_name}.tcl")
            tool_opt = get_flow_var(temp_step, "tool_opt", merged_config, default="")
            
            # 检查 tool_opt 是否为非 Tcl 工具
            # 常见的非 Tcl 工具：python, python3, bash, sh, perl 等
            non_tcl_tools = ["python", "python3", "bash", "sh", "perl", "ruby"]
            tool_name = tool_opt.split()[0] if tool_opt else ""
            if tool_name in non_tcl_tools:
                should_prepend_sources = False
                print(f"[INFO] 检测到非 Tcl 工具 '{tool_opt}'，将不自动 source Tcl 库", file=sys.stderr)
        except Exception as e:
            # 如果读取配置失败，抛出异常
            raise RuntimeError(
                f"无法读取配置检查 tool_opt: {e}。请确保 full.tcl 文件已正确生成。"
            ) from e
        
        # 处理脚本（如果生成了 full.tcl，会在文件头添加 source full.tcl）
        # 日志记录（DEBUG 级别，默认不显示）
        logger.debug("处理脚本", extra={
            'source_script': str(source_script),
            'output_file': str(output_file),
            'hooks_dir': str(hooks_dir) if hooks_dir.exists() else None,
            'flow_name': flow_name,
            'step_name': step_name
        })
        
        # 获取 debug_mode 参数（布尔值）
        debug_mode = 1 if getattr(args, 'debug', False) else 0
        
        # 从配置中读取 skip_sub_step（如果存在）
        skip_sub_steps = []
        try:
            # 从 merged_config 中读取 skip_sub_step 配置
            # 配置格式：pnr_innovus.place.skip_sub_step: "sub_step1 sub_step2"
            flow_config = merged_config.get(flow_name, {})
            step_config = flow_config.get(step_name, {})
            skip_sub_step_str = step_config.get('skip_sub_step', '')
            if skip_sub_step_str:
                # 将字符串按空格分割，转换为列表
                skip_sub_steps = skip_sub_step_str.split()
                print(f"[INFO] 从配置中读取到要跳过的 sub_steps: {skip_sub_steps}", file=sys.stderr)
                logger.info(f"从配置中读取到要跳过的 sub_steps: {skip_sub_steps}", extra={'skip_sub_steps': skip_sub_steps})
        except Exception as e:
            # 如果读取配置失败，记录警告但继续（skip_sub_steps 是可选的）
            logger.warning(f"无法读取 skip_sub_step 配置: {e}，将使用默认行为（不跳过）", exc_info=True)
        
        manager.process_script(
            input_file=str(source_script),
            output_file=str(output_file),
            prepend_default_sources=should_prepend_sources,  # 根据 tool_opt 决定是否自动添加默认 source 语句
            full_tcl_path=str(full_tcl_path) if full_tcl_path else None,  # 添加 full.tcl 的 source 语句
            hooks_dir=str(hooks_dir) if hooks_dir.exists() else None,  # 添加 hooks 目录
            step_name=step_name,  # 添加步骤名称
            debug_mode=debug_mode,  # Debug 模式：0=正常执行，1=交互式调试
            skip_sub_steps=skip_sub_steps,  # 要跳过的 sub_steps 列表
            foundry=foundry,  # 传递 foundry 参数，用于生成默认 source 语句
            node=node,  # 传递 node 参数，用于生成默认 source 语句
            project=project,  # 传递 project 参数，用于生成默认 source 语句
            flow_name=flow_name  # 传递 flow_name 参数，用于生成默认 source 语句
        )
        
        print(f"[OK] 脚本已生成: {output_file}", file=sys.stderr)
        logger.debug(f"脚本已生成: {output_file}", extra={
            'output_file': str(output_file),
            'flow_name': flow_name,
            'step_name': step_name
        })
        
        # ==================== 执行生成的脚本 ====================
        # 从 full.tcl 中读取配置
        from edp_center.packages.edp_configkit import tclfiles2tclinterp, tclinterp2dict
        from edp_center.packages.edp_flowkit.flowkit import Step
        from edp_center.packages.edp_flowkit.flowkit import ICCommandExecutor
        
        try:
            # 读取 full.tcl 文件，转换为 Python 字典
            tcl_interp = tclfiles2tclinterp(str(full_tcl_path))
            merged_config = tclinterp2dict(tcl_interp, mode="auto")
            
            # 创建 Step 对象
            step_full_name = f"{flow_name}.{step_name}"
            step = Step(
                id=step_full_name,
                cmd=f"{step_name}.tcl"  # 命令文件名
            )
            
            # 创建执行器
            # 从 args 中获取 dry_run 参数（如果提供了 --dry-run 或 -dry_run）
            dry_run = getattr(args, 'dry_run', False)
            executor = ICCommandExecutor(
                base_dir=str(branch_dir),
                config=merged_config,
                dry_run=dry_run
            )
            
            # 设置日志文件 handler，将执行过程中的所有输出记录到日志文件
            # 日志文件路径：logs/{flow_name}.{step_name}/edp_run_{timestamp}.log
            log_dir = branch_dir / 'logs' / f"{flow_name}.{step_name}"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 在创建新 log 之前，将旧的 edp_run_*.log 文件移动到 old_logs/ 目录
            old_logs_dir = log_dir / 'old_logs'
            old_logs_dir.mkdir(exist_ok=True)
            for old_log_file in log_dir.glob('edp_run_*.log'):
                try:
                    shutil.move(str(old_log_file), str(old_logs_dir / old_log_file.name))
                except Exception as e:
                    # 如果移动失败，记录警告但继续执行
                    logger.warning(f"无法移动旧日志文件 {old_log_file}: {e}")
            
            # 添加时间戳到文件名，格式：edp_run_20251119_133549.log
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            edp_run_log_file = log_dir / f'edp_run_{timestamp}.log'
            
            # 添加文件 handler 到 root logger，记录所有日志
            file_handler = logging.FileHandler(str(edp_run_log_file), encoding='utf-8', mode='a')
            file_handler.setLevel(logging.DEBUG)  # 记录所有级别的日志
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                               datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(file_formatter)
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
            
            # 创建一个辅助函数，同时输出到终端和日志文件
            def log_and_print(message, level='INFO'):
                """同时输出到终端和日志文件"""
                print(message, file=sys.stderr)
                # 添加时间戳到日志内容
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(edp_run_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp_str}] {message}\n")
            
            try:
                # 在日志文件开头写入运行信息
                with open(edp_run_log_file, 'w', encoding='utf-8') as f:
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"=== EDP Run Log ===\n")
                    f.write(f"开始时间: {timestamp_str}\n")
                    f.write(f"步骤: {step_full_name}\n")
                    f.write(f"工作目录: {branch_dir}\n")
                    f.write(f"{'=' * 50}\n\n")
                
                # 执行命令
                log_and_print(f"[INFO] 开始执行: {step_full_name}")
                
                success = executor.run_cmd(step, merged_config)
                
                # 执行后更新 .run_info 文件（记录运行信息和使用的 hooks，包括执行信息）
                if work_path_info and work_path_info.get('work_path') and work_path_info.get('project') and \
                   work_path_info.get('version') and work_path_info.get('block') and \
                   work_path_info.get('user') and work_path_info.get('branch'):
                    
                    # 获取实际使用的 hooks
                    used_hooks = get_used_hooks(hooks_dir, step_name)
                    
                    # 更新 .run_info 文件（包含执行信息）
                    # step 对象现在包含 execution_info（由 ICCommandExecutor.run_cmd 设置）
                    update_run_info(branch_dir, flow_name, step_name, used_hooks, step=step)
                
                if success:
                    log_and_print(f"[OK] 执行成功: {step_full_name}")
                    return 0
                else:
                    log_and_print(f"[ERROR] 执行失败: {step_full_name}")
                    return 1
            finally:
                # 移除文件 handler，避免影响后续操作
                root_logger.removeHandler(file_handler)
                file_handler.close()
                
        except Exception as e:
            print(f"[ERROR] 执行脚本时发生错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        
    except Exception as e:
        print(f"[ERROR] 生成 cmds 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

