"""Initialization logic for Init Project GUI."""

from pathlib import Path
from typing import Optional, Dict, Tuple
from PyQt5.QtWidgets import QMessageBox

from ...workflow_manager import WorkflowManager
from ..utils import get_current_user
from .init_worker import InitWorker


class InitGUIInitManager:
    """Manager for initialization logic."""
    
    def __init__(self, main_window, ui_builder, data_manager, manager: Optional[WorkflowManager]):
        self.main_window = main_window
        self.ui_builder = ui_builder
        self.data_manager = data_manager
        self.manager = manager
        self.worker = None
    
    def validate_inputs(self) -> Tuple[bool, str]:
        """验证输入参数"""
        if not self.ui_builder.work_path_edit.text().strip():
            return False, "请选择 Work Path 路径"
        
        if not self.ui_builder.project_combo.currentText().strip():
            return False, "请选择项目"
        
        if not self.ui_builder.version_edit.text().strip():
            return False, "请输入项目版本"
        
        return True, ""
    
    def collect_blocks_config(self) -> Dict[str, list]:
        """从表格收集 block 和 user 配置"""
        blocks_config = {}
        for row in range(self.ui_builder.block_user_table.rowCount()):
            block_item = self.ui_builder.block_user_table.item(row, 0)
            user_item = self.ui_builder.block_user_table.item(row, 1)
            
            if block_item and block_item.text().strip():
                block_name = block_item.text().strip()
                if user_item and user_item.text().strip():
                    users_str = user_item.text().strip()
                    users = [u.strip() for u in users_str.split(',') if u.strip()]
                    if users:
                        blocks_config[block_name] = users
                else:
                    blocks_config[block_name] = [get_current_user()]
        
        return blocks_config
    
    def prepare_init_params(self) -> Optional[Dict]:
        """准备初始化参数"""
        # 验证输入
        is_valid, error_msg = self.validate_inputs()
        if not is_valid:
            QMessageBox.warning(self.main_window, "输入错误", error_msg)
            return None
        
        # 检查是否正在初始化
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self.main_window, "警告", "初始化正在进行中，请稍候...")
            return None
        
        # 更新或创建 manager
        edp_center_path = self.ui_builder.edp_center_edit.text().strip()
        if edp_center_path:
            edp_center_path_obj = Path(edp_center_path)
            if edp_center_path_obj.exists():
                try:
                    if not self.manager or (hasattr(self.manager, 'edp_center') and 
                                           self.manager.edp_center != edp_center_path_obj):
                        self.manager = WorkflowManager(edp_center_path_obj)
                        self.data_manager.data_loader.manager = self.manager
                except Exception as e:
                    QMessageBox.warning(self.main_window, "错误", f"无法初始化 WorkflowManager: {e}")
                    return None
            else:
                QMessageBox.warning(self.main_window, "错误", f"EDP Center 路径不存在: {edp_center_path}")
                return None
        else:
            if not self.manager:
                QMessageBox.warning(self.main_window, "错误", "请先指定 EDP Center 路径")
                return None
        
        # 从表格收集 block 和 user 配置
        blocks_config = self.collect_blocks_config()
        
        # 从项目下拉框解析 project、foundry、node
        project, foundry, node = self.data_manager.get_selected_project_info(
            self.ui_builder.project_combo
        )
        if not project:
            QMessageBox.warning(self.main_window, "错误", "请先选择项目")
            return None
        
        # 收集参数
        params = {
            'work_path': self.ui_builder.work_path_edit.text().strip(),
            'project': project,
            'version': self.ui_builder.version_edit.text().strip(),
            'blocks_config': blocks_config,
            'foundry': foundry,
            'node': node,
        }
        
        return params
    
    def show_confirm_dialog(self, params: Dict) -> bool:
        """显示确认对话框"""
        # 构建 blocks 信息字符串
        blocks_info = []
        for block_name, users in params['blocks_config'].items():
            users_str = ', '.join(users)
            blocks_info.append(f"  - {block_name}: {users_str}")
        blocks_str = '\n'.join(blocks_info) if blocks_info else "  (无)"
        
        # 显示确认对话框
        confirm_msg = f"""
确认初始化参数:
- Work Path: {params['work_path']}
- 项目: {params['project']} ({params['foundry']}/{params['node']})
- 版本: {params['version']}

Block 和 User 配置:
{blocks_str}

是否继续？
        """
        reply = QMessageBox.question(self.main_window, "确认", confirm_msg, 
                                     QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes
    
    def start_init(self):
        """开始初始化"""
        # 准备参数
        params = self.prepare_init_params()
        if not params:
            return
        
        # 显示确认对话框
        if not self.show_confirm_dialog(params):
            return
        
        # 清空日志
        self.ui_builder.log_text.clear()
        self.ui_builder.log_text.append("[INFO] 开始初始化...")
        
        # 禁用初始化按钮
        self.ui_builder.init_btn.setEnabled(False)
        self.ui_builder.init_btn.setText("初始化中...")
        
        # 创建工作线程
        self.worker = InitWorker(self.manager, params)
        self.worker.progress.connect(self.main_window.on_progress)
        self.worker.finished.connect(self.main_window.on_finished)
        self.worker.start()
    
    def on_progress(self, message: str):
        """处理进度消息"""
        self.ui_builder.log_text.append(f"[INFO] {message}")
    
    def on_finished(self, success: bool, message: str):
        """处理完成信号"""
        self.ui_builder.init_btn.setEnabled(True)
        self.ui_builder.init_btn.setText("开始初始化")
        
        if success:
            self.ui_builder.log_text.append(f"[OK] {message}")
            QMessageBox.information(self.main_window, "成功", message)
            # 初始化成功后，自动刷新项目列表
            self.ui_builder.log_text.append("[INFO] 正在刷新项目列表...")
            self.main_window.load_project_options()
        else:
            self.ui_builder.log_text.append(f"[ERROR] {message}")
            QMessageBox.critical(self.main_window, "失败", message)
    
    def cleanup_worker(self):
        """清理工作线程"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait(3000)  # 等待最多3秒

