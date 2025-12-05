"""UI components for Init Project GUI."""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout
)
from typing import Optional
from pathlib import Path

from .init_ui_builder import InitUIBuilder


class InitGUIUIBuilder:
    """Builder for Init Project GUI UI components."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
        # UI components (will be populated)
        self.edp_center_edit = None
        self.work_path_edit = None
        self.project_combo = None
        self.version_edit = None
        self.block_user_table = None
        self.init_btn = None
        self.log_text = None
    
    def build_ui(self):
        """Build the complete UI layout."""
        self.main_window.setWindowTitle("EDP AI - 项目初始化")
        self.main_window.setGeometry(100, 100, 900, 750)
        
        # 中央部件
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 15)
        central_widget.setLayout(main_layout)
        
        # 标题
        main_layout.addWidget(InitUIBuilder.create_title())
        
        # 路径配置组
        path_group, self.edp_center_edit, self.work_path_edit, edp_browse_btn, work_path_browse_btn = \
            InitUIBuilder.create_path_group(self.main_window)
        main_layout.addWidget(path_group)
        
        # 项目配置组
        project_group, self.project_combo, self.version_edit, refresh_projects_btn = \
            InitUIBuilder.create_project_group()
        main_layout.addWidget(project_group)
        
        # Block 和 User 配置组
        block_user_group, self.block_user_table, add_row_btn, remove_row_btn = \
            InitUIBuilder.create_block_user_group()
        # 先断开之前的连接（如果存在），防止重复连接
        try:
            add_row_btn.clicked.disconnect()
        except TypeError:
            pass  # 没有连接，忽略
        try:
            remove_row_btn.clicked.disconnect()
        except TypeError:
            pass  # 没有连接，忽略
        # 防止按钮的默认行为导致双重触发
        add_row_btn.setAutoDefault(False)
        add_row_btn.setDefault(False)
        remove_row_btn.setAutoDefault(False)
        remove_row_btn.setDefault(False)
        main_layout.addWidget(block_user_group)
        
        # 按钮组
        button_layout, load_config_btn, auto_infer_btn, self.init_btn, cancel_btn = \
            InitUIBuilder.create_button_group()
        main_layout.addLayout(button_layout)
        
        # 日志输出区域
        log_group, self.log_text = InitUIBuilder.create_log_group()
        main_layout.addWidget(log_group)
        
        # 返回需要连接信号的组件
        return {
            'edp_browse_btn': edp_browse_btn,
            'work_path_browse_btn': work_path_browse_btn,
            'refresh_projects_btn': refresh_projects_btn,
            'add_row_btn': add_row_btn,
            'remove_row_btn': remove_row_btn,
            'load_config_btn': load_config_btn,
            'auto_infer_btn': auto_infer_btn,
            'cancel_btn': cancel_btn,
        }

