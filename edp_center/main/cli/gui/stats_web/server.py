#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能分析 Web 服务器
提供独立的性能分析 Web 界面
"""

import sys
import threading
from pathlib import Path
from typing import Optional

try:
    from flask import Flask, render_template, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from ....workflow_manager import WorkflowManager
from ...commands.stats_handler import load_run_history, calculate_stats, calculate_step_stats, filter_history
from ...utils import infer_work_path_info, infer_project_info


class StatsWebServer:
    """性能分析 Web 服务器"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None,
                 edp_center_path: Optional[Path] = None,
                 port: int = 8889):
        self.manager = manager
        self.edp_center_path = edp_center_path
        self.port = port
        self.app = None
        
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
            return render_template('stats.html')
        
        @self.app.route('/api/stats/overall', methods=['GET'])
        def get_overall_stats():
            """获取总体性能统计"""
            try:
                # 获取当前工作目录（从请求参数或使用默认值）
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
                    return jsonify({'success': False, 'error': '无法推断项目信息，请提供 work_path 参数'}), 400
                
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
        
        print(f"[INFO] 性能分析 Web 服务器启动: {url}", file=sys.stderr)
        self.app.run(host='0.0.0.0', port=self.port, debug=False)


def run_stats_web(manager: Optional[WorkflowManager] = None,
                  edp_center_path: Optional[Path] = None,
                  port: int = 8889,
                  open_browser: bool = True):
    """运行性能分析 Web 服务器"""
    server = StatsWebServer(manager, edp_center_path, port)
    server.run(open_browser)

