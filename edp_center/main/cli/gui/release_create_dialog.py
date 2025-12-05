#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建 RELEASE 对话框
用于通过 GUI 创建新的 RELEASE 版本
"""

from pathlib import Path
from typing import Optional, List
import subprocess
import sys

try:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
        QLineEdit, QTextEdit, QGroupBox, QMessageBox, QComboBox,
        QCheckBox, QFormLayout, QProgressBar, QScrollArea, QWidget,
        QListWidget, QListWidgetItem
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from ...workflow_manager import WorkflowManager


class ReleaseCreateWorker(QThread):
    """后台执行 release 命令的工作线程"""
    
    finished = pyqtSignal(bool, str)  # (success, message)
    
    def __init__(self, manager, args_dict: dict, work_dir: Path):
        super().__init__()
        self.manager = manager
        self.args_dict = args_dict
        self.work_dir = work_dir
    
    def run(self):
        """执行 release 命令"""
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        try:
            # 切换到工作目录
            import os
            old_cwd = os.getcwd()
            os.chdir(self.work_dir)
            
            try:
                # 创建参数对象
                class Args:
                    def __init__(self, **kwargs):
                        for key, value in kwargs.items():
                            setattr(self, key, value)
                
                args = Args(**self.args_dict)
                
                # 直接调用 release 处理函数
                from edp_center.main.cli.commands.release import handle_release_cmd
                
                # 捕获输出
                output_buffer = io.StringIO()
                error_buffer = io.StringIO()
                
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    result_code = handle_release_cmd(self.manager, args)
                
                output = output_buffer.getvalue()
                error = error_buffer.getvalue()
                
                if result_code == 0:
                    self.finished.emit(True, output or "RELEASE 创建成功")
                else:
                    error_msg = error or output or "Unknown error"
                    self.finished.emit(False, error_msg)
            finally:
                os.chdir(old_cwd)
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.finished.emit(False, error_msg)


class ReleaseCreateDialog(QDialog):
    """创建 RELEASE 对话框"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None,
                 edp_center_path: Optional[Path] = None,
                 parent=None):
        super().__init__(parent)
        self.manager = manager
        self.edp_center_path = edp_center_path
        self.worker = None
        self.work_dir = Path.cwd()  # 当前工作目录
        self.selected_branch = None  # 选中的 branch
        self.work_path_info = None  # 工作路径信息
        
        self.init_ui()
        self.load_available_branches()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("创建新 RELEASE")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 版本信息组
        version_group = QGroupBox("版本信息")
        version_layout = QFormLayout()
        
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("例如: V001, v09001")
        version_layout.addRow("版本号:", self.version_edit)
        
        self.append_check = QCheckBox("追加模式（追加到现有版本）")
        version_layout.addRow("", self.append_check)
        
        self.overwrite_check = QCheckBox("覆盖模式（覆盖已存在的步骤）")
        version_layout.addRow("", self.overwrite_check)
        
        version_group.setLayout(version_layout)
        layout.addWidget(version_group)
        
        # 步骤选择组
        steps_group = QGroupBox("选择步骤")
        steps_layout = QVBoxLayout()
        
        # 工作目录选择
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("工作目录:"))
        self.work_dir_label = QLabel(str(Path.cwd()))
        self.work_dir_label.setStyleSheet("border: 1px solid #ccc; padding: 4px; background-color: #f5f5f5;")
        self.work_dir_label.setWordWrap(True)
        dir_layout.addWidget(self.work_dir_label, 1)
        
        browse_dir_btn = QPushButton("浏览...")
        browse_dir_btn.setMaximumWidth(60)
        browse_dir_btn.clicked.connect(self.browse_work_dir)
        dir_layout.addWidget(browse_dir_btn)
        
        steps_layout.addLayout(dir_layout)
        
        # Branch 选择
        branch_layout = QHBoxLayout()
        branch_layout.addWidget(QLabel("Branch:"))
        self.branch_combo = QComboBox()
        self.branch_combo.setEditable(False)
        self.branch_combo.currentTextChanged.connect(self.on_branch_changed)
        branch_layout.addWidget(self.branch_combo, 1)
        
        refresh_branches_btn = QPushButton("刷新")
        refresh_branches_btn.setMaximumWidth(60)
        refresh_branches_btn.clicked.connect(self.load_available_branches)
        branch_layout.addWidget(refresh_branches_btn)
        
        steps_layout.addLayout(branch_layout)
        
        steps_layout.addWidget(QLabel("选择要 release 的步骤（可多选）:"))
        
        # 使用 QListWidget 显示可勾选的步骤列表
        self.steps_list = QListWidget()
        self.steps_list.setMaximumHeight(200)
        self.steps_list.setSelectionMode(QListWidget.MultiSelection)
        steps_layout.addWidget(self.steps_list)
        
        # 全选/全不选按钮
        select_buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_all_btn.setMaximumWidth(60)
        select_all_btn.clicked.connect(self.select_all_steps)
        select_buttons_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("全不选")
        deselect_all_btn.setMaximumWidth(60)
        deselect_all_btn.clicked.connect(self.deselect_all_steps)
        select_buttons_layout.addWidget(deselect_all_btn)
        
        select_buttons_layout.addStretch()
        steps_layout.addLayout(select_buttons_layout)
        
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)
        
        # 备注
        note_group = QGroupBox("备注（可选）")
        note_layout = QVBoxLayout()
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("输入 release 备注信息...")
        self.note_edit.setMaximumHeight(80)
        note_layout.addWidget(self.note_edit)
        note_group.setLayout(note_layout)
        layout.addWidget(note_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.create_btn = QPushButton("创建 RELEASE")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.create_btn.clicked.connect(self.create_release)
        button_layout.addWidget(self.create_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def browse_work_dir(self):
        """浏览选择工作目录"""
        from PyQt5.QtWidgets import QFileDialog
        
        current_dir = str(self.work_dir) if self.work_dir else str(Path.cwd())
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择工作目录", current_dir
        )
        
        if dir_path:
            self.work_dir = Path(dir_path)
            self.work_dir_label.setText(str(self.work_dir))
            # 自动刷新 branch 列表
            self.load_available_branches()
    
    def load_available_branches(self):
        """加载可用的 branch 列表"""
        self.branch_combo.clear()
        
        try:
            # 尝试从工作目录推断项目信息
            from edp_center.main.cli.utils.inference.path_inference import infer_work_path_info as infer_work_path_info_func
            class SimpleArgs:
                pass
            args = SimpleArgs()
            self.work_path_info = infer_work_path_info_func(self.work_dir, args, None)
            
            if not self.work_path_info:
                self.branch_combo.addItem("无法推断项目信息")
                self.branch_combo.setEnabled(False)
                return
            
            # 获取 user 目录
            work_path = self.work_path_info.get('work_path')
            project = self.work_path_info.get('project')
            version = self.work_path_info.get('version')
            block = self.work_path_info.get('block')
            user = self.work_path_info.get('user')
            
            if not all([work_path, project, version, block, user]):
                self.branch_combo.addItem("无法获取完整路径信息")
                self.branch_combo.setEnabled(False)
                return
            
            # 扫描 user 目录下的所有 branch
            user_dir = Path(work_path) / project / version / block / user
            if not user_dir.exists():
                self.branch_combo.addItem("用户目录不存在")
                self.branch_combo.setEnabled(False)
                return
            
            branches = []
            for branch_dir in user_dir.iterdir():
                if branch_dir.is_dir() and not branch_dir.name.startswith('.'):
                    branches.append(branch_dir.name)
            
            if branches:
                self.branch_combo.addItems(sorted(branches))
                self.branch_combo.setEnabled(True)
                # 如果当前目录在某个 branch 下，自动选择
                current_branch = self.work_path_info.get('branch')
                if current_branch and current_branch in branches:
                    self.branch_combo.setCurrentText(current_branch)
                    self.on_branch_changed(current_branch)
            else:
                self.branch_combo.addItem("未找到 branch")
                self.branch_combo.setEnabled(False)
        except Exception as e:
            self.branch_combo.addItem(f"加载失败: {e}")
            self.branch_combo.setEnabled(False)
    
    def on_branch_changed(self, branch_name: str):
        """Branch 选择改变时，加载该 branch 下的步骤"""
        if not branch_name or branch_name.startswith("无法") or branch_name.startswith("未找到") or branch_name.startswith("加载失败"):
            self.steps_list.clear()
            return
        
        self.selected_branch = branch_name
        self.load_available_steps()
    
    def load_available_steps(self):
        """加载选中 branch 下可用的步骤列表"""
        self.steps_list.clear()
        
        if not self.selected_branch or not self.work_path_info:
            item = QListWidgetItem("请先选择 branch")
            item.setFlags(Qt.NoItemFlags)  # 禁用选择
            self.steps_list.addItem(item)
            return
        
        try:
            # 获取 branch 目录
            work_path = self.work_path_info.get('work_path')
            project = self.work_path_info.get('project')
            version = self.work_path_info.get('version')
            block = self.work_path_info.get('block')
            user = self.work_path_info.get('user')
            
            branch_dir = Path(work_path) / project / version / block / user / self.selected_branch
            
            if not branch_dir.exists():
                item = QListWidgetItem(f"Branch 目录不存在: {branch_dir}")
                item.setFlags(Qt.NoItemFlags)
                self.steps_list.addItem(item)
                return
            
            # 从 branch 目录下的 data/ 和 runs/ 目录查找实际存在的步骤
            steps_set = set()
            
            # 检查 data/ 目录
            data_dir = branch_dir / 'data'
            if data_dir.exists():
                for step_dir in data_dir.iterdir():
                    if step_dir.is_dir():
                        steps_set.add(step_dir.name)
            
            # 检查 runs/ 目录
            runs_dir = branch_dir / 'runs'
            if runs_dir.exists():
                for step_dir in runs_dir.iterdir():
                    if step_dir.is_dir():
                        steps_set.add(step_dir.name)
            
            if steps_set:
                # 显示找到的步骤（可勾选）
                for step in sorted(steps_set):
                    item = QListWidgetItem(step)
                    item.setCheckState(Qt.Unchecked)  # 默认未选中
                    self.steps_list.addItem(item)
            else:
                item = QListWidgetItem(f"Branch '{self.selected_branch}' 下未找到可用步骤")
                item.setFlags(Qt.NoItemFlags)  # 禁用选择
                self.steps_list.addItem(item)
        except Exception as e:
            import traceback
            error_msg = f"加载步骤失败: {e}"
            item = QListWidgetItem(error_msg)
            item.setFlags(Qt.NoItemFlags)  # 禁用选择
            self.steps_list.addItem(item)
    
    def select_all_steps(self):
        """全选所有步骤"""
        for i in range(self.steps_list.count()):
            item = self.steps_list.item(i)
            if item.flags() & Qt.ItemIsEnabled:  # 只选择可用的项
                item.setCheckState(Qt.Checked)
    
    def deselect_all_steps(self):
        """全不选所有步骤"""
        for i in range(self.steps_list.count()):
            item = self.steps_list.item(i)
            if item.flags() & Qt.ItemIsEnabled:  # 只取消选择可用的项
                item.setCheckState(Qt.Unchecked)
    
    def create_release(self):
        """创建 RELEASE"""
        # 验证输入
        release_version = self.version_edit.text().strip()  # 用户输入的 release 版本号
        if not release_version:
            QMessageBox.warning(self, "警告", "请输入版本号")
            return
        
        # 获取步骤列表（从勾选的列表项）
        selected_steps = []
        
        # 从勾选的列表项获取
        for i in range(self.steps_list.count()):
            item = self.steps_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_steps.append(item.text().strip())
        
        if not selected_steps:
            QMessageBox.warning(self, "警告", "请至少选择一个步骤")
            return
        
        steps = selected_steps
        
        # 使用选中的 branch 目录作为工作目录
        if not self.selected_branch or not self.work_path_info:
            QMessageBox.warning(self, "警告", "请先选择 branch")
            return
        
        work_path = self.work_path_info.get('work_path')
        project = self.work_path_info.get('project')
        project_version = self.work_path_info.get('version')  # 项目版本（如 P85）
        block = self.work_path_info.get('block')
        user = self.work_path_info.get('user')
        
        work_dir = Path(work_path) / project / project_version / block / user / self.selected_branch
        
        # 构建参数字典（参数名称必须与 arg_parser.py 中的 dest 一致）
        # 需要包含所有 release_handler.py 中可能访问的参数
        args_dict = {
            'release': True,
            'release_version': release_version,  # 使用用户输入的 release 版本号
            'release_step': steps,  # 列表（对应 --step，dest='release_step'）
            'release_block': None,  # 可选，从工作路径推断
            'release_note': None,  # 可选
            'append': self.append_check.isChecked(),
            'overwrite': self.overwrite_check.isChecked(),
            'strict': False,  # 默认非严格模式
            'include_all': False,
            'include_patterns': None,
            'exclude_patterns': None,
            # 其他可能需要的参数
            'project': None,
            'version': None,
            'block': None,
            'user': None,
            'foundry': None,
            'node': None,
            'edp_center': None,
        }
        
        note = self.note_edit.toPlainText().strip()
        if note:
            args_dict['release_note'] = note  # 对应 --note，dest='release_note'
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("正在创建 RELEASE...")
        self.create_btn.setEnabled(False)
        
        # 在后台执行命令（直接调用函数）
        self.worker = ReleaseCreateWorker(self.manager, args_dict, work_dir)
        self.worker.finished.connect(self.on_release_finished)
        self.worker.start()
    
    def on_release_finished(self, success: bool, message: str):
        """RELEASE 创建完成"""
        self.progress_bar.setVisible(False)
        self.create_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("RELEASE 创建成功！")
            QMessageBox.information(self, "成功", f"RELEASE 创建成功！\n\n{message}")
            self.accept()
        else:
            self.status_label.setText("RELEASE 创建失败")
            QMessageBox.critical(self, "失败", f"RELEASE 创建失败：\n\n{message}")

