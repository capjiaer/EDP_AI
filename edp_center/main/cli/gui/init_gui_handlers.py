"""Event handlers for Init Project GUI."""

from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox

from ..utils import get_current_user


class InitGUIHandlers:
    """Event handlers for Init Project GUI."""
    
    def __init__(self, main_window, ui_builder, data_manager):
        self.main_window = main_window
        self.ui_builder = ui_builder
        self.data_manager = data_manager
    
    def browse_edp_center(self):
        """浏览 EDP Center 路径"""
        path = QFileDialog.getExistingDirectory(self.main_window, "选择 EDP Center 路径")
        if path:
            self.ui_builder.edp_center_edit.setText(path)
            # 重新加载项目列表
            self.main_window.load_project_options()
    
    def browse_work_path(self):
        """浏览 Work Path 路径"""
        current_path = self.ui_builder.work_path_edit.text().strip()
        if not current_path or not Path(current_path).exists():
            current_path = str(Path.cwd())
        
        path = QFileDialog.getExistingDirectory(self.main_window, "选择 Work Path 路径", current_path)
        if path:
            self.ui_builder.work_path_edit.setText(path)
    
    def add_block_user_row(self):
        """添加一行 block/user"""
        row = self.ui_builder.block_user_table.rowCount()
        self.ui_builder.block_user_table.insertRow(row)
        
        # Block 列
        block_item = QTableWidgetItem("")
        self.ui_builder.block_user_table.setItem(row, 0, block_item)
        
        # User 列（默认当前用户）
        current_user = get_current_user()
        user_item = QTableWidgetItem(current_user)
        self.ui_builder.block_user_table.setItem(row, 1, user_item)
    
    def remove_block_user_row(self):
        """删除选中的行"""
        current_row = self.ui_builder.block_user_table.currentRow()
        if current_row >= 0:
            self.ui_builder.block_user_table.removeRow(current_row)
    
    def load_from_config(self):
        """从配置文件加载参数"""
        work_path = self.ui_builder.work_path_edit.text().strip()
        if not work_path:
            QMessageBox.warning(self.main_window, "警告", "请先选择 Work Path 路径")
            return
        
        work_path_obj = Path(work_path)
        success = self.data_manager.load_from_config_file(
            work_path_obj,
            self.ui_builder.project_combo,
            self.ui_builder.version_edit,
            self.ui_builder.block_user_table,
            self.data_manager.project_data,
            self.ui_builder.log_text
        )
        
        if not success:
            QMessageBox.warning(self.main_window, "警告", 
                              f"配置文件不存在或加载失败: {work_path_obj / 'config.yaml'}")
    
    def auto_infer_params(self):
        """自动推断参数（从当前目录或 .edp_version 文件）"""
        work_path = self.ui_builder.work_path_edit.text().strip()
        if not work_path:
            work_path = str(Path.cwd())
            self.ui_builder.work_path_edit.setText(work_path)
        
        work_path_obj = Path(work_path)
        self.data_manager.auto_infer_params(
            work_path_obj,
            self.ui_builder.project_combo,
            self.ui_builder.version_edit,
            self.data_manager.project_data,
            self.ui_builder.log_text
        )

