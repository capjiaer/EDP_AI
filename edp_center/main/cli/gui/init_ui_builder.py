#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Init UI Builder - 初始化 UI 构建器

负责构建和布局 GUI 界面元素。
"""

from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QFileDialog, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class InitUIBuilder:
    """初始化 UI 构建器"""
    
    @staticmethod
    def create_path_group(parent_widget) -> tuple:
        """
        创建路径配置组
        
        Returns:
            (group_widget, edp_center_edit, work_path_edit) 元组
        """
        path_group = QGroupBox("路径配置")
        path_layout = QVBoxLayout()
        path_layout.setSpacing(12)
        
        # EDP Center 路径
        edp_layout = QHBoxLayout()
        edp_label = QLabel("EDP Center 路径:")
        edp_label.setMinimumWidth(120)
        edp_layout.addWidget(edp_label)
        edp_center_edit = QLineEdit()
        edp_center_edit.setPlaceholderText("选择 EDP Center 资源库路径")
        edp_browse_btn = QPushButton("浏览...")
        edp_browse_btn.setFixedWidth(80)
        edp_layout.addWidget(edp_center_edit, 1)  # 设置拉伸因子
        edp_layout.addWidget(edp_browse_btn)
        path_layout.addLayout(edp_layout)
        
        # Work Path 路径
        work_path_layout = QHBoxLayout()
        work_path_label = QLabel("Work Path 路径:")
        work_path_label.setMinimumWidth(120)
        work_path_layout.addWidget(work_path_label)
        work_path_edit = QLineEdit()
        default_work_path = str(Path.cwd())
        work_path_edit.setText(default_work_path)
        work_path_edit.setPlaceholderText("选择工作路径（将在此路径下初始化项目）")
        work_path_browse_btn = QPushButton("浏览...")
        work_path_browse_btn.setFixedWidth(80)
        work_path_layout.addWidget(work_path_edit, 1)  # 设置拉伸因子
        work_path_layout.addWidget(work_path_browse_btn)
        path_layout.addLayout(work_path_layout)
        
        path_group.setLayout(path_layout)
        return path_group, edp_center_edit, work_path_edit, edp_browse_btn, work_path_browse_btn
    
    @staticmethod
    def create_project_group() -> tuple:
        """
        创建项目配置组
        
        Returns:
            (group_widget, project_combo, version_edit, refresh_projects_btn) 元组
        """
        project_group = QGroupBox("项目配置")
        project_layout = QVBoxLayout()
        project_layout.setSpacing(12)
        
        # 项目选择（包含 foundry/node 信息）
        project_select_layout = QHBoxLayout()
        project_label = QLabel("项目:")
        project_label.setMinimumWidth(120)
        project_select_layout.addWidget(project_label)
        project_combo = QComboBox()
        project_combo.setEditable(False)
        project_combo.setPlaceholderText("选择项目")
        project_select_layout.addWidget(project_combo, 1)
        
        # 添加刷新按钮
        refresh_projects_btn = QPushButton("刷新")
        refresh_projects_btn.setMaximumWidth(60)
        refresh_projects_btn.setToolTip("刷新项目列表")
        project_select_layout.addWidget(refresh_projects_btn)
        
        project_layout.addLayout(project_select_layout)
        
        # 项目版本
        version_layout = QHBoxLayout()
        version_label = QLabel("项目版本:")
        version_label.setMinimumWidth(120)
        version_layout.addWidget(version_label)
        version_edit = QLineEdit()
        version_edit.setPlaceholderText("例如: P85, P90")
        version_edit.setMaximumWidth(200)
        version_layout.addWidget(version_edit)
        version_layout.addStretch()  # 添加弹性空间
        project_layout.addLayout(version_layout)
        
        project_group.setLayout(project_layout)
        return project_group, project_combo, version_edit, refresh_projects_btn
    
    @staticmethod
    def create_block_user_group() -> tuple:
        """
        创建 Block 和 User 配置组
        
        Returns:
            (group_widget, table_widget, add_btn, remove_btn) 元组
        """
        block_user_group = QGroupBox("Block 和 User 配置")
        block_user_layout = QVBoxLayout()
        block_user_layout.setSpacing(10)
        
        # 说明文字
        info_label = QLabel("每个 Block 可以配置一个或多个 User（多个 User 用逗号分隔）")
        block_user_layout.addWidget(info_label)
        
        # 表格：Block 和 User
        block_user_table = QTableWidget()
        block_user_table.setColumnCount(2)
        block_user_table.setHorizontalHeaderLabels(["Block 名称", "User 名称（多个用逗号分隔）"])
        block_user_table.horizontalHeader().setStretchLastSection(True)
        block_user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        block_user_table.setMinimumHeight(180)
        block_user_table.setAlternatingRowColors(True)  # 交替行颜色
        block_user_layout.addWidget(block_user_table)
        
        # 表格操作按钮
        table_btn_layout = QHBoxLayout()
        add_row_btn = QPushButton("添加行")
        add_row_btn.setFixedWidth(100)
        remove_row_btn = QPushButton("删除选中行")
        remove_row_btn.setFixedWidth(100)
        table_btn_layout.addWidget(add_row_btn)
        table_btn_layout.addWidget(remove_row_btn)
        table_btn_layout.addStretch()
        block_user_layout.addLayout(table_btn_layout)
        
        block_user_group.setLayout(block_user_layout)
        return block_user_group, block_user_table, add_row_btn, remove_row_btn
    
    @staticmethod
    def create_button_group() -> tuple:
        """
        创建按钮组
        
        Returns:
            (layout, load_config_btn, auto_infer_btn, init_btn, cancel_btn) 元组
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        load_config_btn = QPushButton("从配置文件加载")
        load_config_btn.setFixedWidth(140)
        auto_infer_btn = QPushButton("自动推断参数")
        auto_infer_btn.setFixedWidth(140)
        init_btn = QPushButton("开始初始化")
        init_btn.setFixedWidth(120)
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedWidth(80)
        
        button_layout.addWidget(load_config_btn)
        button_layout.addWidget(auto_infer_btn)
        button_layout.addStretch()
        button_layout.addWidget(init_btn)
        button_layout.addWidget(cancel_btn)
        
        return button_layout, load_config_btn, auto_infer_btn, init_btn, cancel_btn
    
    @staticmethod
    def create_log_group() -> tuple:
        """
        创建日志输出组
        
        Returns:
            (group_widget, log_text) 元组
        """
        log_group = QGroupBox("初始化日志")
        log_layout = QVBoxLayout()
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setMaximumHeight(180)
        log_layout.addWidget(log_text)
        log_group.setLayout(log_layout)
        return log_group, log_text
    
    @staticmethod
    def create_title() -> QLabel:
        """创建标题标签"""
        title = QLabel("项目初始化配置")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        return title

