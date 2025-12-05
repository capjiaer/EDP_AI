"""Data loading and processing for Init Project GUI."""

from pathlib import Path
from typing import Optional, Dict, List, Tuple

from .init_data_loader import InitDataLoader
from ...workflow_manager import WorkflowManager


class InitGUIDataManager:
    """Manager for data loading and processing."""
    
    def __init__(self, manager: Optional[WorkflowManager] = None):
        self.data_loader = InitDataLoader(manager)
        self.project_data = {}  # {display_text: (project, foundry, node)}
    
    def load_project_list(self, edp_center_path: Optional[Path], 
                         project_combo, log_text) -> bool:
        """加载项目列表并更新下拉框"""
        if not edp_center_path or not edp_center_path.exists():
            # 如果路径不存在，清空下拉框
            project_combo.clear()
            project_combo.addItem("")  # 空选项
            self.project_data = {}
            return False
        
        # 使用数据加载器加载项目列表
        project_items = self.data_loader.load_project_list(edp_center_path)
        
        # 更新下拉框
        project_combo.clear()
        project_combo.addItem("")  # 空选项
        
        # 存储项目信息
        self.project_data = {}
        for display_text, project, foundry, node in project_items:
            project_combo.addItem(display_text)
            self.project_data[display_text] = (project, foundry, node)
        
        # 调试信息：记录加载的项目数量
        if project_items:
            log_text.append(f"[INFO] 已加载 {len(project_items)} 个项目")
            # 列出所有加载的项目名称
            project_names = [item[1] for item in project_items]
            log_text.append(f"[INFO] 项目列表: {', '.join(project_names)}")
        else:
            log_text.append(f"[WARN] 未找到项目，请检查 EDP Center 路径: {edp_center_path}")
            log_text.append(f"[INFO] 提示: 项目需要存在于 EDP Center 的 config/ 目录下")
            log_text.append(f"[INFO] 路径格式: {edp_center_path}/config/{{foundry}}/{{node}}/{{project}}/")
        
        return len(project_items) > 0
    
    def get_selected_project_info(self, project_combo) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """获取当前选中的项目信息"""
        display_text = project_combo.currentText().strip()
        return self.data_loader.parse_project_display_text(display_text, self.project_data)
    
    def auto_detect_work_path(self, work_path_edit, log_text) -> Optional[Path]:
        """自动检测 Work Path（从当前目录向上查找 .edp_version 文件）"""
        from edp_center.main.cli.init.params import find_edp_version_file
        
        current_dir = Path.cwd()
        version_file, version_info = find_edp_version_file(current_dir)
        
        if version_file and version_info:
            # .edp_version 文件所在的目录是 version 目录
            version_dir = version_file.parent
            # version 的父目录是 project 目录
            project_dir = version_dir.parent
            # project 的父目录是 work_path 根目录
            work_path_root = project_dir.parent
            
            # 设置 Work Path
            work_path_edit.setText(str(work_path_root.resolve()))
            log_text.append(f"[INFO] 已自动检测 Work Path: {work_path_root}")
            return work_path_root
        else:
            # 如果找不到 .edp_version，使用当前目录
            work_path_edit.setText(str(current_dir))
            return current_dir
    
    def load_from_config_file(self, work_path: Path, project_combo, version_edit, 
                             block_user_table, project_data, log_text) -> bool:
        """从配置文件加载参数"""
        config = self.data_loader.load_from_config_file(work_path)
        
        if not config:
            return False
        
        # 加载项目配置
        project_config = config.get('project', {})
        if project_config:
            if 'name' in project_config:
                project = project_config['name']
                display_text = self.data_loader.find_matching_project(project, project_data)
                if display_text:
                    index = project_combo.findText(display_text)
                    if index >= 0:
                        project_combo.setCurrentIndex(index)
                else:
                    log_text.append(f"[WARN] 在项目列表中未找到项目: {project}")
            
            if 'version' in project_config:
                version_edit.setText(project_config['version'])
            
            # 加载 blocks 配置到表格
            blocks = project_config.get('blocks', {})
            if blocks:
                block_user_table.setRowCount(0)
                from PyQt5.QtWidgets import QTableWidgetItem
                for block_name, users in blocks.items():
                    row = block_user_table.rowCount()
                    block_user_table.insertRow(row)
                    
                    # Block 列
                    block_item = QTableWidgetItem(block_name)
                    block_user_table.setItem(row, 0, block_item)
                    
                    # User 列
                    if isinstance(users, list):
                        user_str = ', '.join(str(u) for u in users)
                    elif isinstance(users, str):
                        user_str = users
                    else:
                        user_str = str(users)
                    user_item = QTableWidgetItem(user_str)
                    block_user_table.setItem(row, 1, user_item)
        
        log_text.append(f"[INFO] 已从配置文件加载参数: {work_path / 'config.yaml'}")
        return True
    
    def auto_infer_params(self, work_path: Path, project_combo, version_edit, 
                         project_data, log_text) -> bool:
        """自动推断参数（从当前目录或 .edp_version 文件）"""
        # 尝试从 .edp_version 文件推断
        version_info = self.data_loader.infer_from_version_file(work_path)
        if version_info:
            if 'project' in version_info:
                project = version_info['project']
                display_text = self.data_loader.find_matching_project(project, project_data)
                if display_text:
                    index = project_combo.findText(display_text)
                    if index >= 0:
                        project_combo.setCurrentIndex(index)
                else:
                    log_text.append(f"[WARN] 在项目列表中未找到项目: {project}")
            
            if 'version' in version_info:
                version_edit.setText(version_info['version'])
            
            log_text.append(f"[INFO] 已从 .edp_version 文件推断参数")
            return True
        
        # 尝试从路径推断
        project_info = self.data_loader.infer_from_path(work_path)
        if project_info and not project_combo.currentText():
            project = project_info.get('project', '')
            if project:
                display_text = self.data_loader.find_matching_project(project, project_data)
                if display_text:
                    index = project_combo.findText(display_text)
                    if index >= 0:
                        project_combo.setCurrentIndex(index)
                else:
                    log_text.append(f"[WARN] 在项目列表中未找到项目: {project}")
            
            log_text.append(f"[INFO] 已从路径推断参数")
            return True
        
        return False

