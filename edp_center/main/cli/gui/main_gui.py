#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一主 GUI 窗口
包含多个功能 TAB：项目初始化、Timing Compare 等
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
    )
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from ...workflow_manager import WorkflowManager
from .init_gui import InitProjectGUI
from .release_tab import ReleaseTab


class MainGUIWindow(QMainWindow):
    """统一主 GUI 窗口"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None, 
                 edp_center_path: Optional[Path] = None):
        super().__init__()
        self.manager = manager
        self.edp_center_path = edp_center_path
        
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("EDP AI - 统一图形界面")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建 Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Tab 1: 项目初始化
        # 创建一个包装 widget，将 InitProjectGUI 的内容嵌入
        init_widget = QWidget()
        init_layout = QVBoxLayout(init_widget)
        init_layout.setContentsMargins(0, 0, 0, 0)
        init_layout.setSpacing(0)
        
        # 创建 InitProjectGUI 但不显示（我们只使用其内容）
        self.init_gui = InitProjectGUI(self.manager, self.edp_center_path)
        # 获取 InitProjectGUI 的中央部件并嵌入到 Tab 中
        init_central = self.init_gui.centralWidget()
        if init_central:
            # 从原父布局中移除
            init_central.setParent(init_widget)
            init_layout.addWidget(init_central)
        
        self.tab_widget.addTab(init_widget, "项目初始化")
        
        # Tab 2: RELEASE 管理
        release_tab = ReleaseTab(self.manager, self.edp_center_path)
        self.tab_widget.addTab(release_tab, "RELEASE 管理")
        
        # 注意：工作流执行已迁移到独立的 Web 界面
        # 使用命令: edp -workflow-web 启动
        
        main_layout.addWidget(self.tab_widget)
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 清理资源
        try:
            if hasattr(self, 'init_gui'):
                # 检查是否有正在运行的工作线程
                if hasattr(self.init_gui, 'worker') and self.init_gui.worker:
                    if self.init_gui.worker.isRunning():
                        # 停止工作线程
                        self.init_gui.worker.terminate()
                        self.init_gui.worker.wait(3000)  # 等待最多3秒
        except Exception as e:
            # 忽略清理时的异常，确保窗口能正常关闭
            import traceback
            print(f"[WARN] 清理资源时出现异常: {e}", file=sys.stderr)
            traceback.print_exc()
        
        event.accept()


def run_main_gui(edp_center_path: Optional[Path] = None):
    """运行统一主 GUI 应用"""
    if not PYQT5_AVAILABLE:
        raise ImportError("PyQt5 未安装，请使用: pip install PyQt5")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 如果 edp_center_path 为 None，尝试自动检测
    if edp_center_path is None:
        try:
            import os
            env_path = os.environ.get('EDP_CENTER_PATH')
            if env_path:
                edp_center_path = Path(env_path)
            
            if edp_center_path is None or not edp_center_path.exists():
                current = Path.cwd()
                for parent in [current] + list(current.parents):
                    if (parent / 'edp_center').exists() and (parent / 'edp_center' / 'config').exists():
                        edp_center_path = parent / 'edp_center'
                        break
        except Exception:
            pass
    
    # 创建 WorkflowManager
    manager = None
    if edp_center_path and edp_center_path.exists():
        try:
            manager = WorkflowManager(edp_center_path)
        except Exception as e:
            print(f"[WARN] 无法初始化 WorkflowManager: {e}", file=sys.stderr)
            manager = None
    
    # 创建主窗口
    window = MainGUIWindow(manager, edp_center_path)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_main_gui()

