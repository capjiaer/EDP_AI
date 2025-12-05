#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init Project GUI - 项目初始化图形界面

使用 PyQt 提供图形界面来配置项目初始化参数，无需手动编辑配置文件。
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt

from ...workflow_manager import WorkflowManager
from .init_gui_ui import InitGUIUIBuilder
from .init_gui_data import InitGUIDataManager
from .init_gui_handlers import InitGUIHandlers
from .init_gui_init import InitGUIInitManager


class InitProjectGUI(QMainWindow):
    """项目初始化 GUI 主窗口"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None, edp_center_path: Optional[Path] = None):
        super().__init__()
        self.manager = manager
        self.edp_center_path = edp_center_path
        
        # Initialize managers
        self.data_manager = InitGUIDataManager(manager)
        self.ui_builder = InitGUIUIBuilder(self)
        self.handlers = None  # Will be initialized after UI
        self.init_manager = None  # Will be initialized after UI
        
        # Build UI
        button_connections = self.ui_builder.build_ui()
        
        # Initialize handlers and init manager after UI is built
        self.handlers = InitGUIHandlers(self, self.ui_builder, self.data_manager)
        self.init_manager = InitGUIInitManager(self, self.ui_builder, self.data_manager, manager)
        
        # Connect signals
        self.setup_connections(button_connections)
        
        # Load initial data
        self.load_initial_data()
    
    def setup_connections(self, button_connections):
        """设置信号连接"""
        # 当 EDP Center 路径改变时，重新加载项目列表
        self.ui_builder.edp_center_edit.textChanged.connect(self.on_edp_center_changed)
        
        # 连接按钮信号
        button_connections['edp_browse_btn'].clicked.connect(self.handlers.browse_edp_center)
        button_connections['work_path_browse_btn'].clicked.connect(self.handlers.browse_work_path)
        button_connections['refresh_projects_btn'].clicked.connect(self.load_project_options)
        button_connections['add_row_btn'].clicked.connect(self.handlers.add_block_user_row)
        button_connections['remove_row_btn'].clicked.connect(self.handlers.remove_block_user_row)
        button_connections['load_config_btn'].clicked.connect(self.handlers.load_from_config)
        button_connections['auto_infer_btn'].clicked.connect(self.handlers.auto_infer_params)
        button_connections['cancel_btn'].clicked.connect(self.close)
        
        # 初始化按钮连接到 init_manager
        self.ui_builder.init_btn.clicked.connect(self.init_manager.start_init)
    
    def load_initial_data(self):
        """加载初始数据"""
        # 设置默认值（暂时断开信号连接，避免触发两次加载）
        try:
            self.ui_builder.edp_center_edit.textChanged.disconnect()
        except TypeError:
            pass  # 如果没有连接，忽略
        
        if self.edp_center_path:
            self.ui_builder.edp_center_edit.setText(str(self.edp_center_path))
        elif self.manager and hasattr(self.manager, 'edp_center'):
            self.ui_builder.edp_center_edit.setText(str(self.manager.edp_center))
        
        # 重新连接信号
        self.ui_builder.edp_center_edit.textChanged.connect(self.on_edp_center_changed)
        
        # 自动推断 Work Path（从当前目录向上查找 .edp_version）
        self.data_manager.auto_detect_work_path(
            self.ui_builder.work_path_edit,
            self.ui_builder.log_text
        )
        
        # 加载项目列表
        self.load_project_options()
        
        # 添加一行默认的 block/user
        self.handlers.add_block_user_row()
    
    def on_edp_center_changed(self):
        """当 EDP Center 路径改变时"""
        self.load_project_options()
    
    def load_project_options(self):
        """加载所有项目选项"""
        edp_center_path = None
        if self.ui_builder.edp_center_edit.text():
            edp_center_path = Path(self.ui_builder.edp_center_edit.text())
        elif self.manager and hasattr(self.manager, 'edp_center'):
            edp_center_path = self.manager.edp_center
        
        self.data_manager.load_project_list(
            edp_center_path,
            self.ui_builder.project_combo,
            self.ui_builder.log_text
        )
    
    def on_progress(self, message: str):
        """处理进度消息（委托给 init_manager）"""
        self.init_manager.on_progress(message)
    
    def on_finished(self, success: bool, message: str):
        """处理完成信号（委托给 init_manager）"""
        self.init_manager.on_finished(success, message)
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 清理工作线程
        if self.init_manager:
            self.init_manager.cleanup_worker()
        # 调用父类的 closeEvent
        super().closeEvent(event)


def run_gui(edp_center_path: Optional[Path] = None):
    """运行 GUI 应用"""
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
                    if (parent / 'edp_center').exists() and (parent / 'edp_center' / 'flow').exists():
                        edp_center_path = parent / 'edp_center'
                        break
        except Exception:
            pass
    
    # 创建主窗口
    manager = None
    if edp_center_path and edp_center_path.exists():
        try:
            manager = WorkflowManager(edp_center_path)
        except Exception as e:
            print(f"[WARN] 无法初始化 WorkflowManager: {e}", file=sys.stderr)
            manager = None
    
    window = InitProjectGUI(manager, edp_center_path)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_gui()
