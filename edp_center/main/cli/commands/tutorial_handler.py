#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial Handler - 教程处理

提供简单的 HTML 生成和浏览器打开功能，替代复杂的 GUI。
"""

import sys
import webbrowser
import subprocess
import platform
from pathlib import Path

from .tutorial_html_generator import generate_tutorial_html
from edp_center.packages.edp_common.error_handler import handle_cli_error


def open_tutorial_in_browser(edp_center_path: Path, update: bool = False, force: bool = False, browser: str = None):
    """
    在浏览器中打开教程
    
    Args:
        edp_center_path: edp_center 路径
        update: 是否更新 HTML 文件（仅 PM 使用）
        force: 是否强制重新生成所有 HTML（需要 update=True）
        browser: 指定浏览器名称（例如: firefox, chrome, chromium），None 表示使用系统默认浏览器
    """
    html_file = edp_center_path / 'tutorial' / 'index.html'
    
    # 如果需要更新，生成 HTML
    if update:
        print("[INFO] Updating tutorial HTML files...")
        html_file = generate_tutorial_html(edp_center_path, output_dir=None, force=force)
        # 验证文件是否真的存在
        if not html_file.exists():
            raise FileNotFoundError(
                f"HTML file generation failed, file does not exist: {html_file}\n"
                f"Output directory: {html_file.parent}\n"
                f"Please check:\n"
                f"  1. Does edp_center/tutorial/ directory have write permission?\n"
                f"  2. Is disk space sufficient?\n"
                f"  3. Use --force to force regeneration"
            )
        print(f"[OK] Tutorial HTML updated: {html_file}")
    else:
        # 普通用户：直接打开已存在的 HTML 文件
        if not html_file.exists():
            print(f"[WARN] Tutorial HTML file does not exist: {html_file}", file=sys.stderr)
            print(f"[INFO] Please contact PM to update tutorial, or use `edp -tutor --update` (requires edp_center write permission)", file=sys.stderr)
            raise FileNotFoundError(f"Tutorial HTML file does not exist: {html_file}")
    
    # 在浏览器中打开
    file_url = html_file.as_uri()
    
    if browser:
        # 指定浏览器
        print(f"[INFO] Opening with {browser}: {file_url}")
        try:
            system = platform.system()
            if system == 'Linux':
                # Linux: 尝试使用 xdg-open 或直接调用浏览器命令
                try:
                    subprocess.Popen([browser, file_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except FileNotFoundError:
                    # 如果直接调用失败，尝试通过 xdg-open
                    subprocess.Popen(['xdg-open', file_url], env={'BROWSER': browser})
            elif system == 'Darwin':  # macOS
                subprocess.Popen(['open', '-a', browser, file_url])
            elif system == 'Windows':
                # Windows: 尝试直接调用浏览器
                subprocess.Popen([browser, file_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # 其他系统，使用 webbrowser 模块
                webbrowser.get(browser).open(file_url)
        except Exception as e:
            print(f"[WARN] Cannot use specified browser {browser}: {e}", file=sys.stderr)
            print("   Trying system default browser...", file=sys.stderr)
            webbrowser.open(file_url)
    else:
        # 使用系统默认浏览器
        print(f"[INFO] Opening in browser: {file_url}")
        system = platform.system()
        if system == 'Windows':
            # Windows: 优先尝试现代浏览器，避免使用 IE
            # 尝试按优先级顺序启动浏览器
            browser_paths = [
                # Chrome
                (r'C:\Program Files\Google\Chrome\Application\chrome.exe', 'Chrome'),
                (r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe', 'Chrome'),
                # Edge
                (r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', 'Edge'),
                (r'C:\Program Files\Microsoft\Edge\Application\msedge.exe', 'Edge'),
                # Firefox
                (r'C:\Program Files\Mozilla Firefox\firefox.exe', 'Firefox'),
                (r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe', 'Firefox'),
            ]
            
            browser_found = False
            for browser_path, browser_name in browser_paths:
                import os
                if os.path.exists(browser_path):
                    try:
                        subprocess.Popen([browser_path, file_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"   Using {browser_name}", file=sys.stderr)
                        browser_found = True
                        break
                    except Exception:
                        continue
            
            if not browser_found:
                # 如果找不到现代浏览器，尝试使用 start 命令（Windows 会使用默认浏览器，通常是 Edge）
                try:
                    subprocess.Popen(['start', file_url], shell=True)
                except Exception:
                    # 最后回退到 webbrowser 模块
                    webbrowser.open(file_url)
        else:
            # 其他系统使用标准方法
            webbrowser.open(file_url)


def open_tutorial_directory(edp_center_path: Path):
    """
    打开教程目录（使用系统默认的文件管理器）
    
    Args:
        edp_center_path: edp_center 路径
    """
    tutorial_dir = edp_center_path / 'tutorial'
    
    if not tutorial_dir.exists():
        print(f"错误: 教程目录不存在: {tutorial_dir}", file=sys.stderr)
        sys.exit(1)
    
    import platform
    import subprocess
    
    system = platform.system()
    if system == 'Windows':
        subprocess.Popen(['explorer', str(tutorial_dir)])
    elif system == 'Darwin':  # macOS
        subprocess.Popen(['open', str(tutorial_dir)])
    else:  # Linux
        subprocess.Popen(['xdg-open', str(tutorial_dir)])
    
    print(f"[OK] Tutorial directory opened: {tutorial_dir}")


@handle_cli_error(error_message="执行 tutorial 命令失败")
def handle_tutorial_cmd(edp_center_path: Path, args) -> int:
    """
    处理教程命令
    
    Args:
        edp_center_path: edp_center 路径
        args: 命令行参数
        
    Returns:
        退出代码
    """
    # 检查是否有 --open-dir 选项（打开目录）
    if hasattr(args, 'open_dir') and args.open_dir:
        open_tutorial_directory(edp_center_path)
        return 0
    
    # 检查是否有 --update 选项（更新 HTML 文件）
    update = hasattr(args, 'update') and args.update
    
    # 检查是否有 --force 选项（强制重新生成，需要 --update）
    force = hasattr(args, 'force') and args.force
    if force and not update:
        print("[WARN] --force option requires --update, ignoring", file=sys.stderr)
        force = False
    
    # 检查是否有 --browser 选项（指定浏览器）
    browser = getattr(args, 'browser', None)
    
    # 默认：直接打开已存在的 HTML 文件（如果不存在则提示）
    # 使用 --update 时才会生成/更新 HTML 文件
    try:
        open_tutorial_in_browser(edp_center_path, update=update, force=force, browser=browser)
        return 0
    except Exception as e:
        print(f"错误: 无法打开教程: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # 如果浏览器打开失败，尝试打开目录
        print("尝试打开教程目录...", file=sys.stderr)
        try:
            open_tutorial_directory(edp_center_path)
            return 0
        except Exception as e2:
            print(f"错误: 无法打开教程目录: {e2}", file=sys.stderr)
            return 1
