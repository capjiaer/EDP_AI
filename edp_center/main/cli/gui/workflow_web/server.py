#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工作流执行 Web 服务器
提供 Web 界面用于工作流可视化和管理
"""

import sys
import threading
from pathlib import Path
from typing import Optional, Dict

try:
    from flask import Flask, render_template, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from ....workflow_manager import WorkflowManager
from . import handlers


class WorkflowWebServer:
    """工作流 Web 服务器"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None,
                 edp_center_path: Optional[Path] = None,
                 port: int = 8888):
        self.manager = manager
        self.edp_center_path = edp_center_path
        self.port = port
        self.app = None
        self.execution_threads = {}  # step_name -> thread
        self.step_status = {}  # step_name -> {'status': 'pending'|'running'|'success'|'failed'|'skipped', ...}
        
        if FLASK_AVAILABLE:
            # 设置 Flask 模板和静态文件路径
            template_dir = Path(__file__).parent / 'templates'
            static_dir = Path(__file__).parent / 'static'
            self.app = Flask(__name__, 
                           template_folder=str(template_dir),
                           static_folder=str(static_dir))
            self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.route('/')
        def index():
            """主页面"""
            return render_template('index.html')
        
        @self.app.route('/api/workflow/load', methods=['GET'])
        def load_workflow():
            """加载工作流"""
            try:
                graph_data = handlers.load_workflow_data(self.manager, self.step_status)
                return jsonify({'success': True, 'data': graph_data})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/workflow/execute', methods=['POST'])
        def execute_step():
            """执行步骤"""
            data = request.json
            step_name = data.get('step_name')
            debug_mode = data.get('debug_mode', 0)  # 默认为 0（正常模式）
            use_terminal = data.get('use_terminal', True)  # 默认使用终端模式
            
            if not step_name:
                return jsonify({'success': False, 'error': '缺少 step_name'}), 400
            
            try:
                handlers.execute_step(self.manager, step_name, 
                                    self.step_status, self.execution_threads,
                                    debug_mode=debug_mode,
                                    use_terminal=use_terminal)
                
                # 检查是否使用了终端模式
                terminal_mode = self.step_status.get(step_name, {}).get('terminal_mode', False)
                return jsonify({
                    'success': True,
                    'terminal_mode': terminal_mode,
                    'message': f'已开始执行: {step_name}' + ('（在独立终端中）' if terminal_mode else '')
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/workflow/skip', methods=['POST'])
        def skip_step():
            """跳过步骤"""
            data = request.json
            step_name = data.get('step_name')
            
            if not step_name:
                return jsonify({'success': False, 'error': '缺少 step_name'}), 400
            
            self.step_status[step_name] = {'status': 'skipped'}
            return jsonify({'success': True})
        
        @self.app.route('/api/workflow/stop', methods=['POST'])
        def stop_step():
            """中断步骤"""
            data = request.json
            step_name = data.get('step_name')
            
            if not step_name:
                return jsonify({'success': False, 'error': '缺少 step_name'}), 400
            
            if step_name in self.execution_threads:
                thread = self.execution_threads[step_name]
                if thread.is_alive():
                    # 注意：这只是一个简单的实现，实际可能需要更复杂的终止逻辑
                    self.step_status[step_name] = {'status': 'failed', 'message': '已中断'}
                    return jsonify({'success': True})
            
            return jsonify({'success': False, 'error': '步骤未在运行'}), 400
        
        @self.app.route('/api/workflow/status', methods=['GET'])
        def get_status():
            """获取所有步骤状态"""
            return jsonify({'success': True, 'data': self.step_status})
        
        @self.app.route('/api/workflow/logs/<step_name>', methods=['GET'])
        def get_step_logs(step_name):
            """获取步骤的执行日志"""
            if step_name in self.step_status:
                status_info = self.step_status[step_name]
                log_content = status_info.get('log_content', '')
                log_file = status_info.get('log_file', '')
                
                # 如果日志文件存在，尝试读取最新内容
                if log_file:
                    try:
                        from pathlib import Path
                        log_path = Path(log_file)
                        if log_path.exists():
                            with open(log_path, 'r', encoding='utf-8') as f:
                                log_content = f.read()
                    except Exception:
                        pass
                
                return jsonify({
                    'success': True,
                    'data': {
                        'status': status_info.get('status'),
                        'message': status_info.get('message', ''),
                        'log_file': log_file,
                        'log_content': log_content,
                        'error': status_info.get('error', ''),
                        'exit_code': status_info.get('exit_code')
                    }
                })
            return jsonify({'success': False, 'error': '步骤不存在'}), 404
    
    def run(self, open_browser: bool = True):
        """运行服务器"""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask 未安装，请使用: pip install flask")
        
        if not self.app:
            raise ValueError("Flask app 未初始化")
        
        import webbrowser
        url = f"http://localhost:{self.port}"
        
        if open_browser:
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        
        print(f"[INFO] 工作流 Web 服务器启动: {url}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)


def run_workflow_web(manager: Optional[WorkflowManager] = None,
                     edp_center_path: Optional[Path] = None,
                     port: int = 8888,
                     open_browser: bool = True):
    """运行工作流 Web 服务器"""
    server = WorkflowWebServer(manager, edp_center_path, port)
    server.run(open_browser)

