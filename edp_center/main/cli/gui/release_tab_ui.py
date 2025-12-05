"""UI components for Release Tab."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTextEdit, QGroupBox, QComboBox,
    QSplitter, QTreeWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Optional
from pathlib import Path


class ReleaseTabUIBuilder:
    """Builder for Release Tab UI components."""
    
    def __init__(self, tab_widget):
        self.tab = tab_widget
        
        # UI components (will be populated)
        self.release_dir_label = None
        self.project_combo = None
        self.version_combo = None
        self.block_combo = None
        self.user_combo = None
        self.versions_table = None
        self.detail_text = None
        self.contents_tree = None
        self.file_content_text = None
        self.compare_timing_btn = None
        self.fold_btn = None
        self.unfold_btn = None
    
    def build_ui(self):
        """Build the complete UI layout."""
        main_layout = QVBoxLayout(self.tab)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("RELEASE 版本管理")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # RELEASE 根目录选择
        release_dir_layout = QHBoxLayout()
        release_dir_layout.addWidget(QLabel("RELEASE 根目录:"))
        self.release_dir_label = QLabel("未选择")
        self.release_dir_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        release_dir_layout.addWidget(self.release_dir_label, 1)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.tab.browse_release_dir)
        release_dir_layout.addWidget(browse_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.tab.scan_releases)
        release_dir_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(release_dir_layout)
        
        # 过滤器组（一行显示）
        filter_group = self._create_filter_group()
        main_layout.addWidget(filter_group)
        
        # 第一行：版本列表和版本详情（左右布局）
        top_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：版本列表表格
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 版本列表标题和创建按钮（一行）
        versions_header_layout = QHBoxLayout()
        versions_label = QLabel("版本列表:")
        versions_header_layout.addWidget(versions_label)
        versions_header_layout.addStretch()
        
        # 创建 Release 按钮（小按钮）
        create_btn = QPushButton("新建")
        create_btn.setMaximumWidth(60)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        create_btn.clicked.connect(self.tab.create_new_release)
        versions_header_layout.addWidget(create_btn)
        
        left_layout.addLayout(versions_header_layout)
        
        self.versions_table = QTableWidget()
        self.versions_table.setColumnCount(7)
        self.versions_table.setHorizontalHeaderLabels([
            "Type", "Block", "User", "Version", "Created", "Final Stage", "Timing Compare"
        ])
        self.versions_table.horizontalHeader().setStretchLastSection(True)
        self.versions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.versions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.versions_table.itemSelectionChanged.connect(self.tab.on_version_selected)
        self.versions_table.setAlternatingRowColors(True)
        left_layout.addWidget(self.versions_table, 1)
        top_splitter.addWidget(left_widget)
        
        # 右侧：版本详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        detail_label = QLabel("版本详情:")
        right_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 8px;
                font-size: 9pt;
            }
        """)
        right_layout.addWidget(self.detail_text, 1)
        top_splitter.addWidget(right_widget)
        
        # 设置分割器比例（左侧列表和右侧详情各占 50%）
        # 版本列表的宽度将用于设置 Contents 的宽度
        top_splitter.setSizes([500, 500])
        main_layout.addWidget(top_splitter, 1)
        
        # 保存 top_splitter 的引用，以便后续同步宽度
        self.top_splitter = top_splitter
        
        # 第二行：Contents（内容树和文件预览，占整行）
        overview_header_layout = QHBoxLayout()
        overview_label = QLabel("Version Overview:")
        overview_header_layout.addWidget(overview_label)
        overview_header_layout.addStretch()
        
        # Compare Timing 按钮（小按钮）
        self.compare_timing_btn = QPushButton("对比")
        self.compare_timing_btn.setMaximumWidth(50)
        self.compare_timing_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.compare_timing_btn.clicked.connect(self.tab.on_compare_timing)
        overview_header_layout.addWidget(self.compare_timing_btn)
        
        # Fold/Unfold 按钮（小按钮）
        self.fold_btn = QPushButton("折叠")
        self.fold_btn.setMaximumWidth(50)
        self.fold_btn.clicked.connect(self.tab.fold_all_items)
        overview_header_layout.addWidget(self.fold_btn)
        
        self.unfold_btn = QPushButton("展开")
        self.unfold_btn.setMaximumWidth(50)
        self.unfold_btn.clicked.connect(self.tab.unfold_all_items)
        overview_header_layout.addWidget(self.unfold_btn)
        
        main_layout.addLayout(overview_header_layout)
        
        # 内容树和文件预览（使用分割器，占整行）
        contents_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：内容树
        self.contents_tree = QTreeWidget()
        self.contents_tree.setHeaderLabel("Contents")
        self.contents_tree.setFont(QFont("Consolas", 9))
        self.contents_tree.setRootIsDecorated(True)
        self.contents_tree.setItemsExpandable(True)
        self.contents_tree.setExpandsOnDoubleClick(True)
        self.contents_tree.itemClicked.connect(self.tab.on_tree_item_clicked)
        contents_splitter.addWidget(self.contents_tree)
        
        # 右侧：文件内容预览
        self.file_content_text = QTextEdit()
        self.file_content_text.setReadOnly(True)
        self.file_content_text.setFont(QFont("Consolas", 9))
        self.file_content_text.setPlaceholderText("Select a file to view its contents")
        contents_splitter.addWidget(self.file_content_text)
        
        contents_splitter.setStretchFactor(0, 1)
        contents_splitter.setStretchFactor(1, 1)
        # 设置 Contents 的宽度与版本列表一致（版本列表在 top_splitter 的左侧）
        # 使用相同的初始宽度值，确保视觉上对齐
        contents_splitter.setSizes([500, 500])
        
        main_layout.addWidget(contents_splitter, 1)
        
        # 保存 contents_splitter 的引用，以便后续同步宽度
        self.contents_splitter = contents_splitter
        
        # 连接信号，当 top_splitter 大小改变时，同步更新 contents_splitter 的左侧宽度
        def sync_contents_width():
            """同步 Contents 宽度以匹配版本列表宽度"""
            top_sizes = self.top_splitter.sizes()
            if top_sizes and len(top_sizes) > 0:
                version_list_width = top_sizes[0]  # 版本列表的宽度
                contents_sizes = self.contents_splitter.sizes()
                if contents_sizes and len(contents_sizes) >= 2:
                    # 保持 Contents 的宽度等于版本列表的宽度，文件预览宽度自动调整
                    total_width = sum(contents_sizes)
                    preview_width = total_width - version_list_width
                    if preview_width > 0:
                        self.contents_splitter.setSizes([version_list_width, preview_width])
        
        # 监听 top_splitter 的大小变化
        self.top_splitter.splitterMoved.connect(sync_contents_width)
    
    def _create_filter_group(self):
        """Create filter group with combo boxes."""
        filter_group = QGroupBox("过滤器")
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Project 过滤器
        filter_layout.addWidget(QLabel("项目:"))
        self.project_combo = QComboBox()
        self.project_combo.setEditable(True)
        self.project_combo.setMinimumWidth(100)
        self.project_combo.currentTextChanged.connect(self.tab.on_project_changed)
        filter_layout.addWidget(self.project_combo)
        
        # Version 过滤器
        filter_layout.addWidget(QLabel("版本:"))
        self.version_combo = QComboBox()
        self.version_combo.setEditable(True)
        self.version_combo.setMinimumWidth(100)
        self.version_combo.currentTextChanged.connect(self.tab.on_version_changed)
        filter_layout.addWidget(self.version_combo)
        
        # Block 过滤器
        filter_layout.addWidget(QLabel("Block:"))
        self.block_combo = QComboBox()
        self.block_combo.setEditable(True)
        self.block_combo.setMinimumWidth(100)
        self.block_combo.currentTextChanged.connect(self.tab.on_block_changed)
        filter_layout.addWidget(self.block_combo)
        
        # User 过滤器
        filter_layout.addWidget(QLabel("User:"))
        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        self.user_combo.setMinimumWidth(100)
        self.user_combo.currentTextChanged.connect(self.tab.on_filter_changed)
        filter_layout.addWidget(self.user_combo)
        
        filter_layout.addStretch()  # 右侧留空
        
        filter_group.setLayout(filter_layout)
        return filter_group

