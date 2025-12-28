#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
View 命令处理器
处理 -view 选项：启动 Metrics Dashboard Web 服务
"""

import sys
import os
import subprocess
import time
import webbrowser
import threading

from edp_center.packages.edp_common.error_handler import handle_cli_error

@handle_cli_error(error_message="启动 view 服务失败")
def handle_view_cmd(args) -> int:
    """
    处理 -view 命令：启动 Web 服务并打开浏览器
    
    Args:
        args: 命令行参数
        
    Returns:
        退出代码
    """
    print("[INFO] 正在启动 Metrics Dashboard...", file=sys.stderr)
    
    # 1. 定位 run_server.py
    # edp_center/main/cli/commands/view_handler.py -> ../../../../
    # 目标: edp_center/packages/edp_webkit/run_server.py
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # current_dir: .../edp_center/main/cli/commands
    
    edp_center_root = os.path.abspath(os.path.join(current_dir, '../../../../edp_center'))
    run_server_script = os.path.join(edp_center_root, 'packages', 'edp_webkit', 'run_server.py')
    
    if not os.path.exists(run_server_script):
        print(f"[ERROR] 找不到 Web 服务启动脚本: {run_server_script}", file=sys.stderr)
        return 1
        
    # 2. 启动子进程运行 Server
    # 使用 sys.executable 确保使用相同的 Python 解释器
    try:
        # 检查依赖是否安装
        try:
            import fastapi
            import uvicorn
        except ImportError:
            print("[ERROR] 缺少必要的依赖包: fastapi, uvicorn", file=sys.stderr)
            print("[INFO] 请运行: pip install fastapi uvicorn pydantic pyyaml", file=sys.stderr)
            return 1

        print(f"[INFO] 服务脚本: {run_server_script}", file=sys.stderr)
        
        # 直接调用 subprocess.run 会阻塞，我们希望它一直运行直到用户按 Ctrl+C
        # run_server.py 内部已经有了打开浏览器的逻辑，这里只需要启动即可
        subprocess.run([sys.executable, run_server_script], check=True)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[INFO] 服务已停止", file=sys.stderr)
        return 0

