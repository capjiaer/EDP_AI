"""Details and tree view for Release Tab."""

from pathlib import Path
from typing import Dict, List
from PyQt5.QtWidgets import QTreeWidgetItem, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ReleaseTabDetailsManager:
    """Manager for release details and tree view."""
    
    def __init__(self, detail_text: QTextEdit, contents_tree, file_content_text):
        self.detail_text = detail_text
        self.contents_tree = contents_tree
        self.file_content_text = file_content_text
    
    def update_detail_text(self, release: Dict):
        """更新版本详情文本"""
        detail_lines = []
        detail_lines.append(f"项目: {release.get('project', 'unknown')}")
        detail_lines.append(f"版本: {release.get('version', 'unknown')}")
        detail_lines.append(f"Block: {release['block']}")
        detail_lines.append(f"User: {release['user']}")
        detail_lines.append(f"Release 版本: {release['release_version']}")
        detail_lines.append(f"状态: {'只读' if release['readonly'] else '可写'}")
        detail_lines.append(f"创建时间: {release['created']}")
        detail_lines.append(f"路径: {release['path']}")
        detail_lines.append("")
        
        # Steps
        detail_lines.append(f"包含步骤 ({len(release['steps'])}):")
        if release['steps']:
            for step in release['steps']:
                detail_lines.append(f"  - {step}")
        else:
            detail_lines.append("  (无)")
        
        # 目录结构
        detail_lines.append("")
        detail_lines.append("目录结构:")
        data_dir = release['path'] / 'data'
        if data_dir.exists():
            for step_dir in sorted(data_dir.iterdir()):
                if step_dir.is_dir():
                    detail_lines.append(f"  data/{step_dir.name}/")
                    # 列出子目录
                    for subdir in sorted(step_dir.iterdir()):
                        if subdir.is_dir():
                            detail_lines.append(f"    - {subdir.name}/")
        
        self.detail_text.setText("\n".join(detail_lines))
    
    def get_final_stage(self, release: Dict) -> str:
        """获取最后一个步骤（Final Stage）"""
        steps = release.get('steps', [])
        if not steps:
            return ""
        
        # 标准步骤顺序
        STAGE_ORDER = ['init', 'floorplan', 'place', 'cts', 'postcts', 'route', 'postroute']
        
        # 分离已知和未知步骤
        known_steps = []
        unknown_steps = []
        
        for step in steps:
            # 从 flow.step 格式中提取 step 名称
            step_name = step.split('.')[-1] if '.' in step else step
            step_lower = step_name.lower()
            if step_lower in STAGE_ORDER:
                known_steps.append(step_name)
            else:
                unknown_steps.append(step_name)
        
        # 按顺序排序已知步骤
        known_steps.sort(key=lambda s: STAGE_ORDER.index(s.lower()) if s.lower() in STAGE_ORDER else len(STAGE_ORDER))
        unknown_steps.sort()
        
        # 返回最后一个步骤
        all_steps = known_steps + unknown_steps
        return all_steps[-1] if all_steps else ""
    
    def update_version_overview(self, release: Dict):
        """更新 Version Overview 树形结构"""
        self.contents_tree.clear()
        
        if not release:
            return
        
        # 创建根节点
        root_item = QTreeWidgetItem(self.contents_tree)
        root_text = (f"Version: {release['release_version']} | "
                    f"Project: {release.get('project', 'unknown')} | "
                    f"Version: {release.get('version', 'unknown')} | "
                    f"Block: {release['block']} | User: {release['user']}")
        root_item.setText(0, root_text)
        root_item.setExpanded(True)
        
        # 添加版本信息
        status_icon = "✓" if release['readonly'] else "⚠"
        status_text = "Ready" if release['readonly'] else "Not Ready"
        
        info_item = QTreeWidgetItem(root_item)
        info_item.setText(0, f"Status: {status_icon} {status_text}")
        
        created_item = QTreeWidgetItem(root_item)
        created_item.setText(0, f"Created: {release['created']}")
        
        # 添加步骤信息
        steps_item = QTreeWidgetItem(root_item)
        steps_str = ", ".join(release['steps']) if release['steps'] else "无"
        steps_item.setText(0, f"Steps: {steps_str}")
        
        # 添加分隔线
        sep_item = QTreeWidgetItem(root_item)
        sep_item.setText(0, "─" * 60)
        
        # 添加 Contents
        contents_item = QTreeWidgetItem(root_item)
        contents_item.setText(0, "Contents")
        contents_item.setExpanded(True)
        
        # 递归填充目录结构
        self.populate_contents_tree(contents_item, release['path'])
        
        # 默认展开到 L2
        self.expand_to_level2()
    
    def populate_contents_tree(self, parent_item: QTreeWidgetItem, version_path: Path):
        """递归填充目录树"""
        try:
            data_dir = version_path / 'data'
            if not data_dir.exists():
                no_content_item = QTreeWidgetItem(parent_item)
                no_content_item.setText(0, "(No contents found)")
                return
            
            # 遍历 data 目录
            for step_dir in sorted(data_dir.iterdir()):
                if not step_dir.is_dir():
                    continue
                
                step_item = QTreeWidgetItem(parent_item)
                step_item.setText(0, f"{step_dir.name}/")
                # 使用绝对路径存储
                step_item.setData(0, Qt.UserRole, str(step_dir.resolve()))
                step_item.setExpanded(False)
                
                # 递归填充子目录
                self._populate_directory_recursive(step_item, step_dir)
        except Exception as e:
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, f"(Error: {str(e)})")
    
    def _populate_directory_recursive(self, parent_item: QTreeWidgetItem, dir_path: Path):
        """递归填充目录和文件"""
        try:
            items = sorted(dir_path.iterdir())
            items = [item for item in items if not item.name.startswith('.')]
            
            # 分离目录和文件
            dirs = []
            files = []
            for item in items:
                if item.is_dir():
                    dirs.append(item)
                elif item.is_file():
                    files.append(item)
            
            # 先添加目录
            for dir_item in dirs:
                dir_tree_item = QTreeWidgetItem(parent_item)
                
                # 检查是否为空
                try:
                    sub_items = [i for i in dir_item.iterdir() if not i.name.startswith('.')]
                    is_empty = len(sub_items) == 0
                except Exception:
                    is_empty = False
                
                if is_empty:
                    dir_tree_item.setText(0, f"{dir_item.name}/ (empty)")
                    dir_tree_item.setForeground(0, QColor(128, 128, 128))
                else:
                    dir_tree_item.setText(0, f"{dir_item.name}/")
                
                # 使用绝对路径存储
                dir_tree_item.setData(0, Qt.UserRole, str(dir_item.resolve()))
                dir_tree_item.setExpanded(False)
                
                if not is_empty:
                    self._populate_directory_recursive(dir_tree_item, dir_item)
            
            # 再添加文件
            for file_item in files:
                file_tree_item = QTreeWidgetItem(parent_item)
                file_tree_item.setText(0, file_item.name)
                # 使用绝对路径存储
                file_tree_item.setData(0, Qt.UserRole, str(file_item.resolve()))
        except PermissionError:
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, "(permission denied)")
            error_item.setForeground(0, QColor(200, 0, 0))
        except Exception as e:
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, f"(error: {str(e)})")
            error_item.setForeground(0, QColor(200, 0, 0))
    
    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """处理树项点击，加载文件内容"""
        file_path = None
        try:
            file_path = item.data(0, Qt.UserRole)
            if not file_path:
                # 如果没有文件路径，清空预览
                self.file_content_text.setPlainText("(未选择文件)")
                return
            
            # 确保 file_path 是字符串
            if not isinstance(file_path, str):
                file_path = str(file_path)
            
            file_path_obj = Path(file_path)
            
            # 检查是否是文件
            if not file_path_obj.exists():
                self.file_content_text.setPlainText(f"文件不存在: {file_path}")
                return
            
            if not file_path_obj.is_file():
                # 如果是目录，清空预览（点击目录时不显示内容）
                self.file_content_text.setPlainText("(选择文件以查看内容)")
                return
            
            # 加载文件内容
            file_size = file_path_obj.stat().st_size
            max_size = 100 * 1024 * 1024  # 100MB
            
            if file_size > max_size:
                self.file_content_text.setPlainText(
                    f"File too large to display ({file_size / 1024 / 1024:.2f} MB).\n"
                    f"Maximum display size: 100 MB\n"
                    f"File path: {file_path}\n"
                    f"File size: {file_size:,} bytes"
                )
                return
            
            # 尝试不同编码
            encodings = ['utf-8', 'latin-1', 'cp1252', 'gbk', 'gb2312']
            content = None
            
            for encoding in encodings:
                try:
                    content = file_path_obj.read_text(encoding=encoding)
                    break
                except (UnicodeDecodeError, Exception):
                    continue
            
            if content is None:
                # 尝试二进制读取
                try:
                    binary_content = file_path_obj.read_bytes()
                    self.file_content_text.setPlainText(
                        f"Binary file (cannot display as text)\n"
                        f"File path: {file_path}\n"
                        f"File size: {len(binary_content)} bytes"
                    )
                except Exception as e:
                    self.file_content_text.setPlainText(f"Error reading file: {str(e)}\nFile path: {file_path}")
            else:
                file_name = file_path_obj.name
                self.file_content_text.setPlainText(
                    f"File: {file_name}\nPath: {file_path}\n{'=' * 60}\n\n{content}"
                )
        except Exception as e:
            import traceback
            file_path_str = str(file_path) if file_path else "(unknown)"
            error_msg = f"Error loading file: {str(e)}\nFile path: {file_path_str}\n\n{traceback.format_exc()}"
            self.file_content_text.setPlainText(error_msg)
    
    def fold_all_items(self):
        """折叠所有树项"""
        def collapse_item(item):
            item.setExpanded(False)
            for i in range(item.childCount()):
                collapse_item(item.child(i))
        
        root = self.contents_tree.invisibleRootItem()
        for i in range(root.childCount()):
            collapse_item(root.child(i))
    
    def unfold_all_items(self):
        """展开所有树项"""
        def expand_item(item):
            item.setExpanded(True)
            for i in range(item.childCount()):
                expand_item(item.child(i))
        
        root = self.contents_tree.invisibleRootItem()
        for i in range(root.childCount()):
            expand_item(root.child(i))
    
    def expand_to_level2(self):
        """展开到 L2 级别"""
        def expand_item_level2(item, level=0):
            if level < 2:
                item.setExpanded(True)
                for i in range(item.childCount()):
                    expand_item_level2(item.child(i), level + 1)
            else:
                item.setExpanded(False)
        
        root = self.contents_tree.invisibleRootItem()
        for i in range(root.childCount()):
            expand_item_level2(root.child(i), 0)

