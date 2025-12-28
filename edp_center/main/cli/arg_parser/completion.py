#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
参数补全函数设置模块
"""

# 尝试导入 argcomplete（可选依赖）
try:
    import argcomplete
    ARGCOMPLETE_AVAILABLE = True
except ImportError:
    ARGCOMPLETE_AVAILABLE = False


def setup_completions(parser, info_arg=None):
    """
    设置参数补全函数
    
    Args:
        parser: ArgumentParser 实例
        info_arg: info 参数的 Action 对象（用于补全）
    """
    if not ARGCOMPLETE_AVAILABLE:
        return
    
    # 导入补全辅助函数
    from ...completion import (
        complete_projects, complete_foundries, complete_nodes,
        complete_flows, complete_flow_steps, complete_blocks,
        complete_users, complete_branches, complete_versions
    )
    
    # 获取参数引用（用于补全功能）
    branch_arg = None
    release_arg = None
    run_arg = None
    project_arg = None
    version_arg = None
    block_arg = None
    user_arg = None
    foundry_arg = None
    node_arg = None
    
    for action in parser._actions:
        if hasattr(action, 'option_strings'):
            if '-b' in action.option_strings or '--branch' in action.option_strings:
                branch_arg = action
            elif '--release' in action.option_strings:
                release_arg = action
            elif '-run' in action.option_strings or '--run' in action.option_strings:
                run_arg = action
            elif '--project' in action.option_strings or '-prj' in action.option_strings:
                project_arg = action
            elif '--version' in action.option_strings or '-v' in action.option_strings:
                version_arg = action
            elif '--block' in action.option_strings:
                block_arg = action
            elif '--user' in action.option_strings:
                user_arg = action
            elif '--foundry' in action.option_strings:
                foundry_arg = action
            elif '--node' in action.option_strings:
                node_arg = action
    
    # 为项目参数添加补全
    if project_arg:
        def complete_project(prefix, parsed_args, **kwargs):
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            results = complete_projects(foundry=foundry, node=node)
            return [r for r in results if r.startswith(prefix)]
        project_arg.completer = complete_project
    
    # 为 foundry 参数添加补全
    if foundry_arg:
        def complete_foundry(prefix, parsed_args, **kwargs):
            results = complete_foundries()
            return [r for r in results if r.startswith(prefix)]
        foundry_arg.completer = complete_foundry
    
    # 为 node 参数添加补全（需要 foundry）
    if node_arg:
        def complete_node(prefix, parsed_args, **kwargs):
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            results = complete_nodes(foundry=foundry)
            return [r for r in results if r.startswith(prefix)]
        node_arg.completer = complete_node
    
    # 为 version 参数添加补全
    if version_arg:
        def complete_version(prefix, parsed_args, **kwargs):
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            results = complete_versions(project=project)
            return [r for r in results if r.startswith(prefix)]
        version_arg.completer = complete_version
    
    # 为 block 参数添加补全
    if block_arg:
        def complete_block(prefix, parsed_args, **kwargs):
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            results = complete_blocks(project=project)
            return [r for r in results if r.startswith(prefix)]
        block_arg.completer = complete_block
    
    # 为 user 参数添加补全（需要 block）
    if user_arg:
        def complete_user(prefix, parsed_args, **kwargs):
            block = getattr(parsed_args, 'block', None) if parsed_args else None
            results = complete_users(block=block)
            return [r for r in results if r.startswith(prefix)]
        user_arg.completer = complete_user
    
    # 为 branch 参数添加补全
    if branch_arg:
        def complete_branch(prefix, parsed_args, **kwargs):
            results = complete_branches()
            return [r for r in results if r.startswith(prefix)]
        branch_arg.completer = complete_branch
    
    # 为 -run 参数添加补全（flow.step 格式）
    if run_arg:
        def complete_run(prefix, parsed_args, **kwargs):
            """补全 -run 参数（flow.step 格式）"""
            # 如果已经输入了 flow.step 格式，尝试补全 step
            if '.' in prefix:
                flow, step_prefix = prefix.split('.', 1)
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                steps = complete_flow_steps(
                    flow=flow,
                    project=project,
                    foundry=foundry,
                    node=node
                )
                # 过滤以 prefix 开头的
                return [s for s in steps if s.startswith(prefix)]
            else:
                # 否则补全 flow 列表
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                flows = complete_flows(
                    project=project,
                    foundry=foundry,
                    node=node
                )
                return [f for f in flows if f.startswith(prefix)]
        run_arg.completer = complete_run
    
    # 为 -info 参数添加补全（flow 列表）
    if info_arg:
        def complete_info(prefix, parsed_args, **kwargs):
            try:
                project = getattr(parsed_args, 'project', None) if parsed_args else None
                foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
                node = getattr(parsed_args, 'node', None) if parsed_args else None
                results = complete_flows(project=project, foundry=foundry, node=node)
                if prefix:
                    return [r for r in results if r.startswith(prefix)]
                else:
                    return results
            except Exception:
                return []
        info_arg.completer = complete_info
    
    # 为 -history 参数添加补全（flow.step 格式）
    def complete_history(prefix, parsed_args, **kwargs):
        """补全 -history 参数（flow.step 格式）"""
        if '.' in prefix:
            flow, step_prefix = prefix.split('.', 1)
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            steps = complete_flow_steps(
                flow=flow,
                project=project,
                foundry=foundry,
                node=node
            )
            return [f"{flow}.{s}" for s in steps if s.startswith(step_prefix)]
        else:
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            flows = complete_flows(project=project, foundry=foundry, node=node)
            return [f for f in flows if f.startswith(prefix)]
    
    # 为 -stats 参数添加补全（flow.step 格式）
    def complete_stats(prefix, parsed_args, **kwargs):
        """补全 -stats 参数（flow.step 格式）"""
        if '.' in prefix:
            flow, step_prefix = prefix.split('.', 1)
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            steps = complete_flow_steps(
                flow=flow,
                project=project,
                foundry=foundry,
                node=node
            )
            return [f"{flow}.{s}" for s in steps if s.startswith(step_prefix)]
        else:
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            flows = complete_flows(project=project, foundry=foundry, node=node)
            return [f for f in flows if f.startswith(prefix)]
    
    # 为 -validate 参数添加补全（flow.step 格式）
    def complete_validate(prefix, parsed_args, **kwargs):
        """补全 -validate 参数（flow.step 格式）"""
        if '.' in prefix:
            flow, step_prefix = prefix.split('.', 1)
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            steps = complete_flow_steps(
                flow=flow,
                project=project,
                foundry=foundry,
                node=node
            )
            return [f"{flow}.{s}" for s in steps if s.startswith(step_prefix)]
        else:
            project = getattr(parsed_args, 'project', None) if parsed_args else None
            foundry = getattr(parsed_args, 'foundry', None) if parsed_args else None
            node = getattr(parsed_args, 'node', None) if parsed_args else None
            flows = complete_flows(project=project, foundry=foundry, node=node)
            return [f for f in flows if f.startswith(prefix)]
    
    # 查找并设置补全函数（需要找到对应的 action）
    for action in parser._actions:
        if hasattr(action, 'option_strings'):
            if '-history' in action.option_strings or '--history' in action.option_strings:
                action.completer = complete_history
            elif '-stats' in action.option_strings or '--stats' in action.option_strings:
                action.completer = complete_stats
            elif '-validate' in action.option_strings or '--validate' in action.option_strings:
                action.completer = complete_validate

