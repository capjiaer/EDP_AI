#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RELEASE 管理 Tab
用于查看和管理 RELEASE 版本，支持创建新 release
"""

from pathlib import Path
from typing import Optional, List, Dict

try:
    from PyQt5.QtWidgets import QWidget, QMessageBox
    from PyQt5.QtCore import QTimer
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from ...workflow_manager import WorkflowManager
from .release_tab_ui import ReleaseTabUIBuilder
from .release_tab_data import ReleaseTabDataLoader
from .release_tab_filters import ReleaseTabFilterManager
from .release_tab_table import ReleaseTabTableManager
from .release_tab_details import ReleaseTabDetailsManager


class ReleaseTab(QWidget):
    """RELEASE 管理 Tab"""
    
    def __init__(self, manager: Optional[WorkflowManager] = None,
                 edp_center_path: Optional[Path] = None):
        super().__init__()
        self.manager = manager
        self.edp_center_path = edp_center_path
        
        self.selected_release = None
        self.compare_versions = []  # List of release info dicts selected for timing compare
        
        # Initialize components
        self.ui_builder = ReleaseTabUIBuilder(self)
        self.data_loader = ReleaseTabDataLoader()
        self.filter_manager = None  # Will be initialized after UI
        self.table_manager = None  # Will be initialized after UI
        self.details_manager = None  # Will be initialized after UI
        
        # Build UI
        self.ui_builder.build_ui()
        
        # Initialize managers after UI is built
        self.filter_manager = ReleaseTabFilterManager(
            self.ui_builder.project_combo,
            self.ui_builder.version_combo,
            self.ui_builder.block_combo,
            self.ui_builder.user_combo
        )
        self.table_manager = ReleaseTabTableManager(
            self.ui_builder.versions_table,
            self.compare_versions
        )
        self.details_manager = ReleaseTabDetailsManager(
            self.ui_builder.detail_text,
            self.ui_builder.contents_tree,
            self.ui_builder.file_content_text
        )
        
        # Auto-detect and scan
        self.auto_detect_release_root()
    
    def auto_detect_release_root(self):
        """自动检测 RELEASE 根目录"""
        release_root = self.data_loader.auto_detect_release_root()
        if release_root:
            self.ui_builder.release_dir_label.setText(str(release_root))
            self.scan_releases()
    
    def browse_release_dir(self):
        """浏览选择 RELEASE 根目录"""
        from PyQt5.QtWidgets import QFileDialog
        
        current_dir = self.ui_builder.release_dir_label.text()
        if current_dir == "未选择":
            current_dir = str(Path.cwd())
        
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择 RELEASE 根目录", current_dir if current_dir != "未选择" else ""
        )
        
        if dir_path:
            self.data_loader.release_root = Path(dir_path)
            self.ui_builder.release_dir_label.setText(dir_path)
            self.scan_releases()
    
    def scan_releases(self):
        """扫描 RELEASE 目录，查找所有版本"""
        self.data_loader.release_root = Path(self.ui_builder.release_dir_label.text()) if self.ui_builder.release_dir_label.text() != "未选择" else None
        
        releases = self.data_loader.scan_releases()
        
        if not releases:
            self.ui_builder.versions_table.setRowCount(0)
            return
        
        # 更新过滤器选项
        self.filter_manager.update_filter_combos(releases, self.update_versions_table)
        
        # 应用过滤器并更新表格
        self.update_versions_table()
    
    def on_project_changed(self):
        """Project 过滤器改变时更新下级过滤器和表格"""
        self.filter_manager.update_filter_combos(self.data_loader.releases, self.update_versions_table)
        self.update_versions_table()
    
    def on_version_changed(self):
        """Version 过滤器改变时更新下级过滤器和表格"""
        self.filter_manager.update_filter_combos(self.data_loader.releases, self.update_versions_table)
        self.update_versions_table()
    
    def on_block_changed(self):
        """Block 过滤器改变时更新下级过滤器和表格"""
        self.filter_manager.update_filter_combos(self.data_loader.releases, self.update_versions_table)
        self.update_versions_table()
    
    def on_filter_changed(self):
        """User 过滤器改变时更新表格"""
        self.update_versions_table()
    
    def update_versions_table(self):
        """更新版本列表表格"""
        # 过滤 releases
        filtered_releases = self.filter_manager.filter_releases(self.data_loader.releases)
        
        # 更新表格
        self.table_manager.update_table(
            filtered_releases,
            self.details_manager.get_final_stage,
            self.on_compare_checkbox_changed,
            self.on_version_selected
        )
    
    def on_version_selected(self):
        """版本选择改变时更新详情"""
        release = self.table_manager.get_selected_release()
        if release:
            self.selected_release = release
            self.details_manager.update_detail_text(release)
            self.details_manager.update_version_overview(release)
        else:
            self.selected_release = None
            self.ui_builder.detail_text.clear()
            self.ui_builder.contents_tree.clear()
    
    def on_tree_item_clicked(self, item, column: int):
        """处理树项点击，加载文件内容"""
        self.details_manager.on_tree_item_clicked(item, column)
    
    def fold_all_items(self):
        """折叠所有树项"""
        self.details_manager.fold_all_items()
    
    def unfold_all_items(self):
        """展开所有树项"""
        self.details_manager.unfold_all_items()
    
    def expand_to_level2(self):
        """展开到 L2 级别"""
        self.details_manager.expand_to_level2()
    
    def on_compare_checkbox_changed(self, state: int, release: Dict):
        """处理 Timing Compare 复选框状态改变"""
        from PyQt5.QtCore import Qt
        if state == Qt.Checked:
            # 添加到对比列表
            if release not in self.compare_versions:
                self.compare_versions.append(release)
        else:
            # 从对比列表移除
            if release in self.compare_versions:
                self.compare_versions.remove(release)
    
    def on_compare_timing(self):
        """处理 Compare Timing 按钮点击"""
        if not self.compare_versions:
            QMessageBox.warning(self, "警告", "请至少选择一个版本进行对比（勾选 Timing Compare 列）")
            return
        
        # 打开 Timing Compare 窗口
        try:
            from .timing_compare_window import TimingCompareWindow
            # 转换 release 信息为 version_info 格式
            version_list = []
            for release in self.compare_versions:
                version_info = {
                    'release_dir': str(self.data_loader.release_root),
                    'block': release['block'],
                    'user': release['user'],
                    'version': release['release_version']
                }
                version_list.append(version_info)
            
            compare_window = TimingCompareWindow(version_list, self)
            compare_window.exec_()
        except ImportError as e:
            QMessageBox.critical(self, "错误", f"无法导入 TimingCompareWindow: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开对比窗口失败: {e}")
    
    def create_new_release(self):
        """创建新的 RELEASE"""
        # 打开创建 Release 对话框
        from .release_create_dialog import ReleaseCreateDialog
        
        dialog = ReleaseCreateDialog(self.manager, self.edp_center_path, self)
        if dialog.exec_() == dialog.Accepted:
            # 创建成功后刷新列表
            QTimer.singleShot(500, self.scan_releases)  # 延迟刷新，确保文件系统已更新
