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
        
        # ==================== 性能分析 API ====================
        @self.app.route('/api/stats/overall', methods=['GET'])
        def get_overall_stats():
            """获取总体性能统计"""
            try:
                from ...commands.stats_handler import load_run_history, calculate_stats
                from ...utils import infer_work_path_info, infer_project_info
                from pathlib import Path
                
                # 获取当前工作目录（从请求参数或使用默认值）
                work_path_param = request.args.get('work_path')
                if work_path_param:
                    current_dir = Path(work_path_param).resolve()
                else:
                    # 如果没有提供，尝试从 manager 获取
                    if self.manager:
                        # 尝试从 manager 获取基础路径
                        current_dir = Path.cwd()
                    else:
                        return jsonify({'success': False, 'error': '无法确定工作路径，请提供 work_path 参数'}), 400
                
                # 推断项目信息
                class Args:
                    pass
                args = Args()
                project_info = infer_project_info(self.manager, current_dir, args)
                if not project_info:
                    return jsonify({'success': False, 'error': '无法推断项目信息'}), 400
                
                # 推断工作路径信息
                work_path_info = infer_work_path_info(current_dir, args, project_info)
                if not work_path_info:
                    return jsonify({'success': False, 'error': '无法推断工作路径信息'}), 400
                
                # 构建 branch 目录路径
                work_path = Path(work_path_info['work_path']).resolve()
                project = work_path_info['project']
                version = work_path_info['version']
                block = work_path_info['block']
                user = work_path_info['user']
                branch = work_path_info['branch']
                branch_dir = work_path / project / version / block / user / branch
                
                runs = load_run_history(branch_dir)
                stats = calculate_stats(runs)
                
                return jsonify({'success': True, 'data': stats})
            except Exception as e:
                import traceback
                return jsonify({'success': False, 'error': f'{str(e)}\n{traceback.format_exc()}'}), 500
        
        @self.app.route('/api/stats/steps', methods=['GET'])
        def get_step_stats():
            """获取按步骤分组的性能统计"""
            try:
                from ...commands.stats_handler import load_run_history, calculate_step_stats
                from ...utils import infer_work_path_info, infer_project_info
                from pathlib import Path
                
                # 获取当前工作目录
                work_path_param = request.args.get('work_path')
                if work_path_param:
                    current_dir = Path(work_path_param).resolve()
                else:
                    current_dir = Path.cwd()
                
                # 推断项目信息
                class Args:
                    pass
                args = Args()
                project_info = infer_project_info(self.manager, current_dir, args)
                if not project_info:
                    return jsonify({'success': False, 'error': '无法推断项目信息'}), 400
                
                # 推断工作路径信息
                work_path_info = infer_work_path_info(current_dir, args, project_info)
                if not work_path_info:
                    return jsonify({'success': False, 'error': '无法推断工作路径信息'}), 400
                
                # 构建 branch 目录路径
                work_path = Path(work_path_info['work_path']).resolve()
                project = work_path_info['project']
                version = work_path_info['version']
                block = work_path_info['block']
                user = work_path_info['user']
                branch = work_path_info['branch']
                branch_dir = work_path / project / version / block / user / branch
                
                runs = load_run_history(branch_dir)
                step_stats = calculate_step_stats(runs)
                
                return jsonify({'success': True, 'data': step_stats})
            except Exception as e:
                import traceback
                return jsonify({'success': False, 'error': f'{str(e)}\n{traceback.format_exc()}'}), 500
        
        @self.app.route('/api/stats/history', methods=['GET'])
        def get_stats_history():
            """获取历史记录（用于趋势分析）"""
            try:
                from ...commands.stats_handler import load_run_history, filter_history
                from ...utils import infer_work_path_info, infer_project_info
                from pathlib import Path
                
                # 获取当前工作目录
                work_path_param = request.args.get('work_path')
                if work_path_param:
                    current_dir = Path(work_path_param).resolve()
                else:
                    current_dir = Path.cwd()
                
                # 推断项目信息
                class Args:
                    pass
                args = Args()
                project_info = infer_project_info(self.manager, current_dir, args)
                if not project_info:
                    return jsonify({'success': False, 'error': '无法推断项目信息'}), 400
                
                # 推断工作路径信息
                work_path_info = infer_work_path_info(current_dir, args, project_info)
                if not work_path_info:
                    return jsonify({'success': False, 'error': '无法推断工作路径信息'}), 400
                
                # 构建 branch 目录路径
                work_path = Path(work_path_info['work_path']).resolve()
                project = work_path_info['project']
                version = work_path_info['version']
                block = work_path_info['block']
                user = work_path_info['user']
                branch = work_path_info['branch']
                branch_dir = work_path / project / version / block / user / branch
                
                runs = load_run_history(branch_dir)
                
                # 应用过滤器
                step_filter = request.args.get('step', None)
                if step_filter:
                    runs = filter_history(runs, step_filter=step_filter)
                
                # 限制返回数量
                limit = request.args.get('limit', type=int)
                if limit:
                    runs = runs[-limit:]  # 取最近 N 条
                
                return jsonify({'success': True, 'data': runs})
            except Exception as e:
                import traceback
                return jsonify({'success': False, 'error': f'{str(e)}\n{traceback.format_exc()}'}), 500
        
        @self.app.route('/stats')
        def stats_page():
            """性能分析页面"""
            return render_template('stats.html')
        
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

