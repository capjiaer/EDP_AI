#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Timing Compare Tab
用于对比多个 RELEASE 版本的时序数据
"""

from pathlib import Path
from typing import Optional, List, Dict
import os

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
        QListWidget, QListWidgetItem, QMessageBox, QFileDialog
    )
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from ...workflow_manager import WorkflowManager


class TimingCompareTab(QWidget):
    """Timing Compare Tab"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None,
                 edp_center_path: Optional[Path] = None):
        super().__init__()
        self.manager = manager
        self.edp_center_path = edp_center_path
        self.selected_versions = []  # List of version_info dicts
        
        self.init_ui()
        self.scan_release_versions()
    
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("Timing Compare - 时序数据对比")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # RELEASE 目录选择
        release_dir_layout = QHBoxLayout()
        release_dir_layout.addWidget(QLabel("RELEASE 目录:"))
        self.release_dir_label = QLabel("未选择")
        self.release_dir_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        release_dir_layout.addWidget(self.release_dir_label, 1)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_release_dir)
        release_dir_layout.addWidget(browse_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.scan_release_versions)
        release_dir_layout.addWidget(refresh_btn)
        
        layout.addLayout(release_dir_layout)
        
        # 版本列表（左侧）
        versions_layout = QHBoxLayout()
        
        # 可用版本列表
        versions_left = QVBoxLayout()
        versions_left.addWidget(QLabel("可用版本:"))
        self.available_versions_list = QListWidget()
        self.available_versions_list.setSelectionMode(QListWidget.MultiSelection)
        versions_left.addWidget(self.available_versions_list)
        
        add_btn = QPushButton("添加到对比 →")
        add_btn.clicked.connect(self.add_to_compare)
        versions_left.addWidget(add_btn)
        
        versions_layout.addLayout(versions_left, 1)
        
        # 已选版本列表（右侧）
        versions_right = QVBoxLayout()
        versions_right.addWidget(QLabel("已选版本（用于对比）:"))
        self.selected_versions_list = QListWidget()
        versions_right.addWidget(self.selected_versions_list)
        
        remove_btn = QPushButton("← 从对比中移除")
        remove_btn.clicked.connect(self.remove_from_compare)
        versions_right.addWidget(remove_btn)
        
        versions_layout.addLayout(versions_right, 1)
        
        layout.addLayout(versions_layout, 1)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        compare_btn = QPushButton("开始对比")
        compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        compare_btn.clicked.connect(self.start_compare)
        button_layout.addWidget(compare_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_selected)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
    
    def browse_release_dir(self):
        """浏览选择 RELEASE 目录"""
        current_dir = self.release_dir_label.text()
        if current_dir == "未选择":
            # 尝试从当前工作目录推断
            current = Path.cwd()
            # 查找 RELEASE 目录
            for parent in [current] + list(current.parents):
                release_dir = parent / 'RELEASE'
                if release_dir.exists():
                    current_dir = str(release_dir)
                    break
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择 RELEASE 目录", current_dir if current_dir != "未选择" else ""
        )
        
        if dir_path:
            self.release_dir_label.setText(dir_path)
            self.scan_release_versions()
    
    def scan_release_versions(self):
        """扫描 RELEASE 目录，查找所有版本"""
        release_dir = self.release_dir_label.text()
        if release_dir == "未选择":
            # 尝试自动检测
            current = Path.cwd()
            for parent in [current] + list(current.parents):
                potential_release = parent / 'RELEASE'
                if potential_release.exists():
                    release_dir = str(potential_release)
                    self.release_dir_label.setText(release_dir)
                    break
        
        if release_dir == "未选择" or not os.path.isdir(release_dir):
            self.available_versions_list.clear()
            return
        
        # 扫描 RELEASE 目录结构: RELEASE/{block}/{user}/{version}/
        self.available_versions_list.clear()
        release_path = Path(release_dir)
        
        versions = []
        for block_dir in release_path.iterdir():
            if not block_dir.is_dir() or block_dir.name.startswith('.'):
                continue
            
            for user_dir in block_dir.iterdir():
                if not user_dir.is_dir() or user_dir.name.startswith('.'):
                    continue
                
                for version_dir in user_dir.iterdir():
                    if not version_dir.is_dir() or version_dir.name.startswith('.'):
                        continue
                    
                    # 检查是否有 timing 数据
                    data_dir = version_dir / 'data'
                    if not data_dir.exists():
                        continue
                    
                    # 查找所有 flow.step 目录下的 timing
                    has_timing = False
                    for step_dir in data_dir.iterdir():
                        if step_dir.is_dir():
                            timing_dir = step_dir / 'timing'
                            if timing_dir.exists():
                                has_timing = True
                                break
                    
                    if has_timing:
                        version_info = {
                            'release_dir': str(release_path),
                            'block': block_dir.name,
                            'user': user_dir.name,
                            'version': version_dir.name
                        }
                        versions.append(version_info)
        
        # 显示版本列表
        for version_info in sorted(versions, key=lambda v: (v['block'], v['user'], v['version'])):
            display_text = f"{version_info['block']}/{version_info['user']}/{version_info['version']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, version_info)
            self.available_versions_list.addItem(item)
    
    def add_to_compare(self):
        """添加选中的版本到对比列表"""
        selected_items = self.available_versions_list.selectedItems()
        for item in selected_items:
            version_info = item.data(Qt.UserRole)
            if version_info and version_info not in self.selected_versions:
                self.selected_versions.append(version_info)
                display_text = f"{version_info['block']}/{version_info['user']}/{version_info['version']}"
                compare_item = QListWidgetItem(display_text)
                compare_item.setData(Qt.UserRole, version_info)
                self.selected_versions_list.addItem(compare_item)
    
    def remove_from_compare(self):
        """从对比列表中移除选中的版本"""
        selected_items = self.selected_versions_list.selectedItems()
        for item in selected_items:
            version_info = item.data(Qt.UserRole)
            if version_info in self.selected_versions:
                self.selected_versions.remove(version_info)
            row = self.selected_versions_list.row(item)
            self.selected_versions_list.takeItem(row)
    
    def clear_selected(self):
        """清空已选版本"""
        self.selected_versions.clear()
        self.selected_versions_list.clear()
    
    def start_compare(self):
        """开始对比"""
        if not self.selected_versions:
            QMessageBox.warning(self, "警告", "请至少选择一个版本进行对比")
            return
        
        # 导入并打开 TimingCompareWindow
        try:
            from .timing_compare_window import TimingCompareWindow
            compare_window = TimingCompareWindow(self.selected_versions, self)
            compare_window.exec_()
        except ImportError as e:
            QMessageBox.critical(self, "错误", f"无法导入 TimingCompareWindow: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开对比窗口失败: {e}")

