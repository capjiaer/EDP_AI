"""Filter management for Release Tab."""

from typing import List, Dict
from PyQt5.QtWidgets import QComboBox


class ReleaseTabFilterManager:
    """Manager for release filters."""
    
    def __init__(self, project_combo: QComboBox, version_combo: QComboBox,
                 block_combo: QComboBox, user_combo: QComboBox):
        self.project_combo = project_combo
        self.version_combo = version_combo
        self.block_combo = block_combo
        self.user_combo = user_combo
    
    def update_filter_combos(self, releases: List[Dict], on_update_table):
        """更新过滤器下拉框选项（级联更新）"""
        # 获取当前选中的值
        current_project = self.project_combo.currentText()
        current_version = self.version_combo.currentText()
        current_block = self.block_combo.currentText()
        
        # 过滤 releases
        filtered = releases
        if current_project and current_project != "全部":
            filtered = [r for r in filtered if r['project'] == current_project]
        if current_version and current_version != "全部":
            filtered = [r for r in filtered if r['version'] == current_version]
        if current_block and current_block != "全部":
            filtered = [r for r in filtered if r['block'] == current_block]
        
        # 更新 Project 下拉框
        projects = sorted(set(r['project'] for r in releases))
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItem("全部")
        self.project_combo.addItems(projects)
        if current_project and current_project in projects:
            self.project_combo.setCurrentText(current_project)
        self.project_combo.blockSignals(False)
        
        # 更新 Version 下拉框（基于选中的 project）
        if current_project and current_project != "全部":
            versions = sorted(set(r['version'] for r in releases if r['project'] == current_project))
        else:
            versions = sorted(set(r['version'] for r in releases))
        self.version_combo.blockSignals(True)
        self.version_combo.clear()
        self.version_combo.addItem("全部")
        self.version_combo.addItems(versions)
        if current_version and current_version in versions:
            self.version_combo.setCurrentText(current_version)
        self.version_combo.blockSignals(False)
        
        # 更新 Block 下拉框（基于选中的 project 和 version）
        if current_project and current_project != "全部":
            block_filtered = [r for r in releases if r['project'] == current_project]
        else:
            block_filtered = releases
        if current_version and current_version != "全部":
            block_filtered = [r for r in block_filtered if r['version'] == current_version]
        blocks = sorted(set(r['block'] for r in block_filtered))
        self.block_combo.blockSignals(True)
        self.block_combo.clear()
        self.block_combo.addItem("全部")
        self.block_combo.addItems(blocks)
        if current_block and current_block in blocks:
            self.block_combo.setCurrentText(current_block)
        self.block_combo.blockSignals(False)
        
        # 更新 User 下拉框（基于所有前面的过滤器）
        user_filtered = filtered
        users = sorted(set(r['user'] for r in user_filtered))
        self.user_combo.blockSignals(True)
        self.user_combo.clear()
        self.user_combo.addItem("全部")
        self.user_combo.addItems(users)
        self.user_combo.blockSignals(False)
    
    def get_selected_filters(self) -> Dict[str, str]:
        """获取当前选中的过滤器值"""
        return {
            'project': self.project_combo.currentText(),
            'version': self.version_combo.currentText(),
            'block': self.block_combo.currentText(),
            'user': self.user_combo.currentText()
        }
    
    def filter_releases(self, releases: List[Dict]) -> List[Dict]:
        """根据当前过滤器过滤 releases"""
        filters = self.get_selected_filters()
        filtered = releases
        
        if filters['project'] and filters['project'] != "全部":
            filtered = [r for r in filtered if r['project'] == filters['project']]
        if filters['version'] and filters['version'] != "全部":
            filtered = [r for r in filtered if r['version'] == filters['version']]
        if filters['block'] and filters['block'] != "全部":
            filtered = [r for r in filtered if r['block'] == filters['block']]
        if filters['user'] and filters['user'] != "全部":
            filtered = [r for r in filtered if r['user'] == filters['user']]
        
        return filtered

