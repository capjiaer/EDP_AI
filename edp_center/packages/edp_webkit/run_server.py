import sys
import os
import threading
import webbrowser
import time

# 1. 修复路径问题
# current_dir: .../edp_center/packages/edp_webkit
current_dir = os.path.dirname(os.path.abspath(__file__))

# target: .../EDP_AI (包含 edp_center 的父目录)
# edp_center/packages/edp_webkit -> ../../../ -> EDP_AI
project_root = os.path.abspath(os.path.join(current_dir, '../../../'))

# 确保 project_root 在 sys.path 中，这样才能 import edp_center
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from edp_center.packages.edp_webkit.webkit.app import create_app
    import uvicorn
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Project Root calculated as: {project_root}")
    sys.exit(1)

def open_browser(url):
    """延迟打开浏览器"""
    time.sleep(1.5) # 等待 Server 启动
    print(f"Opening browser at {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print(f"Starting EDP WebKit Server...")
    print(f"Root Path: {project_root}")
    
    app = create_app()
    
    # 2. 自动打开浏览器 (指向 API 文档页面，方便验证)
    port = 8000
    host = "0.0.0.0"
    url = f"http://localhost:{port}/docs"
    
    # 使用线程在后台打开浏览器，不阻塞 Server 启动
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    
    uvicorn.run(app, host=host, port=port)
