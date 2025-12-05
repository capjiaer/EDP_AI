#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Terminal Executor - 终端执行模块

负责在新终端窗口中执行步骤。
"""

import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional


def open_terminal_and_execute(step_name: str, work_dir: Path, debug_mode: int = 0, 
                               edp_center_path: Optional[Path] = None) -> bool:
    """
    在新终端窗口中执行步骤
    
    Args:
        step_name: 步骤名称（格式: flow.step）
        work_dir: 工作目录
        debug_mode: Debug 模式（0=正常, 1=debug）
        edp_center_path: edp_center 路径（用于找到 edp_env.csh）
        
    Returns:
        bool: 是否成功启动终端
    """
    system = platform.system()
    work_dir_str = str(work_dir.resolve())
    
    # 构建 edp 命令
    edp_cmd = f"edp -run {step_name}"
    if debug_mode > 0:
        edp_cmd += " --debug"
    
    # 获取 edp_env.csh 路径
    edp_env_csh_path = None
    if edp_center_path:
        edp_env_csh = edp_center_path / 'bin' / 'edp_env.csh'
        if edp_env_csh.exists():
            edp_env_csh_path = str(edp_env_csh.resolve())
    
    # 构建完整的命令：先 source edp_env.csh，然后 cd 到工作目录，最后执行 edp 命令
    # 注意：tcsh 中 && 和 ; 都可以用，但为了兼容性，使用 ; 更安全
    if edp_env_csh_path:
        # 使用 tcsh，先 source edp_env.csh，然后执行命令
        # tcsh 中 source 后需要用 ; 连接命令
        full_cmd = f'source "{edp_env_csh_path}" ; cd "{work_dir_str}" ; {edp_cmd}'
    else:
        # 如果找不到 edp_env.csh，直接执行（可能 edp 已经在 PATH 中）
        full_cmd = f'cd "{work_dir_str}" ; {edp_cmd}'
    
    # 添加等待用户按键的命令（tcsh 语法：使用 set line = $< 等待输入）
    full_cmd += ' ; echo "" ; echo "按 Enter 键关闭窗口..." ; set line = $<'
    
    # 根据操作系统选择终端
    if system == 'Linux':
        return _open_linux_terminal(step_name, full_cmd, work_dir_str)
    elif system == 'Windows':
        return _open_windows_terminal(step_name, edp_cmd, work_dir_str)
    elif system == 'Darwin':  # macOS
        return _open_macos_terminal(step_name, edp_cmd, work_dir_str)
    
    return False


def _open_linux_terminal(step_name: str, full_cmd: str, work_dir_str: str) -> bool:
    """在 Linux 上打开终端"""
    terminals = [
        ('xterm', ['-title', f'EDP: {step_name}', '-e', 'tcsh', '-c', full_cmd]),
        ('gnome-terminal', ['--title', f'EDP: {step_name}', '--', 'tcsh', '-c', full_cmd]),
        ('konsole', ['--title', f'EDP: {step_name}', '-e', 'tcsh', '-c', full_cmd]),
        ('xfce4-terminal', ['--title', f'EDP: {step_name}', '-e', f'tcsh -c "{full_cmd}"']),
    ]
    
    for term_name, term_args in terminals:
        if shutil.which(term_name):
            try:
                subprocess.Popen([term_name] + term_args, cwd=work_dir_str)
                return True
            except Exception:
                continue
    
    return False


def _open_windows_terminal(step_name: str, edp_cmd: str, work_dir_str: str) -> bool:
    """在 Windows 上打开终端"""
    try:
        # 尝试 Windows Terminal (wt.exe)
        if shutil.which('wt.exe'):
            wt_cmd = f'wt.exe -d "{work_dir_str}" cmd /k "{edp_cmd} & echo. & echo 按任意键关闭窗口... & pause >nul"'
            subprocess.Popen(wt_cmd, shell=True)
            return True
    except Exception:
        pass
    
    try:
        # 尝试 PowerShell
        ps_cmd = f'powershell.exe -NoExit -Command "cd \'{work_dir_str}\'; {edp_cmd}; Write-Host \'\'; Write-Host \'按 Enter 键关闭窗口...\'; Read-Host"'
        subprocess.Popen(ps_cmd, shell=True)
        return True
    except Exception:
        pass
    
    try:
        # 回退到 cmd.exe
        cmd_cmd = f'cmd.exe /k "cd /d "{work_dir_str}" && {edp_cmd} && echo. && echo 按任意键关闭窗口... && pause >nul"'
        subprocess.Popen(cmd_cmd, shell=True)
        return True
    except Exception:
        return False


def _open_macos_terminal(step_name: str, edp_cmd: str, work_dir_str: str) -> bool:
    """在 macOS 上打开终端"""
    try:
        # 尝试 iTerm2
        if shutil.which('osascript'):
            script = f'''
            tell application "iTerm2"
                tell current window
                    create tab with default profile
                    tell current session of current tab
                        write text "cd '{work_dir_str}' && {edp_cmd}"
                    end tell
                end tell
            end tell
            '''
            subprocess.Popen(['osascript', '-e', script])
            return True
    except Exception:
        pass
    
    try:
        # 回退到 Terminal.app
        if shutil.which('osascript'):
            script = f'''
            tell application "Terminal"
                activate
                do script "cd '{work_dir_str}' && {edp_cmd}"
            end tell
            '''
            subprocess.Popen(['osascript', '-e', script])
            return True
    except Exception:
        return False

