"""Table management for Release Tab."""

from typing import List, Dict
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ReleaseTabTableManager:
    """Manager for release versions table."""
    
    def __init__(self, versions_table: QTableWidget, compare_versions: List[Dict]):
        self.versions_table = versions_table
        self.compare_versions = compare_versions
    
    def update_table(self, filtered_releases: List[Dict], get_final_stage_func, 
                    on_compare_checkbox_changed, on_version_selected):
        """更新版本列表表格"""
        # 按版本号排序（降序，最新的在前）
        filtered_releases = sorted(filtered_releases, 
                                  key=lambda x: (x['project'], x['version'], x['block'], x['user'], x['release_version']),
                                  reverse=True)
        
        # 更新表格
        self.versions_table.setRowCount(len(filtered_releases))
        
        for row, release in enumerate(filtered_releases):
            # Type (Release/可写)
            type_text = "Release" if release['readonly'] else "Beta"
            type_item = QTableWidgetItem(type_text)
            self.versions_table.setItem(row, 0, type_item)
            
            # Block
            self.versions_table.setItem(row, 1, QTableWidgetItem(release['block']))
            
            # User
            self.versions_table.setItem(row, 2, QTableWidgetItem(release['user']))
            
            # Release Version（release 版本号）
            version_item = QTableWidgetItem(release['release_version'])
            version_item.setData(Qt.UserRole, release)  # 存储完整信息
            self.versions_table.setItem(row, 3, version_item)
            
            # Created
            self.versions_table.setItem(row, 4, QTableWidgetItem(release['created']))
            
            # Final Stage（最后一个步骤）
            final_stage = get_final_stage_func(release)
            if final_stage:
                stage_item = QTableWidgetItem(final_stage)
                stage_item.setForeground(QColor(76, 175, 80))  # 绿色
                stage_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            else:
                stage_item = QTableWidgetItem("—")
                stage_item.setForeground(QColor(158, 158, 158))  # 灰色
                stage_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.versions_table.setItem(row, 5, stage_item)
            
            # Timing Compare 复选框
            compare_checkbox = QCheckBox()
            compare_checkbox.setChecked(release in self.compare_versions)
            compare_checkbox.stateChanged.connect(
                lambda state, r=release: on_compare_checkbox_changed(state, r)
            )
            # 居中显示复选框
            compare_widget = QWidget()
            compare_layout = QHBoxLayout(compare_widget)
            compare_layout.setContentsMargins(0, 0, 0, 0)
            compare_layout.addWidget(compare_checkbox)
            compare_layout.setAlignment(Qt.AlignCenter)
            self.versions_table.setCellWidget(row, 6, compare_widget)
        
        # 调整列宽
        self.versions_table.resizeColumnsToContents()
    
    def get_selected_release(self) -> Dict:
        """获取当前选中的 release"""
        selected_items = self.versions_table.selectedItems()
        if not selected_items:
            return None
        
        # 获取选中行的版本信息
        row = selected_items[0].row()
        version_item = self.versions_table.item(row, 3)  # Version 列
        if version_item:
            return version_item.data(Qt.UserRole)
        return None

