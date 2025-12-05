"""UI components for Timing Compare Window."""

from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Dict, List


class TimingCompareUIBuilder:
    """Builder for Timing Compare Window UI components."""
    
    def __init__(self, window, version_list: List[Dict], font_size: int = 12):
        self.window = window
        self.version_list = version_list
        self.font_size = font_size
        
        # Filter checkboxes (will be populated)
        self.timing_type_checks = {}
        self.stage_checks = {}
        self.category_checks = {}
        self.drv_category_checks = {}
        
        # Layout references (will be populated)
        self.stages_layout = None
        self.categories_layout = None
        self.drv_categories_layout = None
        
        # UI components
        self.font_size_spinbox = None
        self.compare_tree = None
    
    def setup_ui(self):
        """Setup the UI layout."""
        layout = QtWidgets.QVBoxLayout(self.window)
        
        # Header with version info
        header = QtWidgets.QLabel(f"Comparing {len(self.version_list)} versions:")
        header.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        layout.addWidget(header)
        
        # Filter panel
        filter_panel = self.create_filter_panel()
        layout.addWidget(filter_panel)
        
        # Font size control
        font_control_layout = QtWidgets.QHBoxLayout()
        font_control_layout.addWidget(QtWidgets.QLabel("Font Size:"))
        self.font_size_spinbox = QtWidgets.QSpinBox()
        self.font_size_spinbox.setMinimum(6)
        self.font_size_spinbox.setMaximum(20)
        self.font_size_spinbox.setValue(self.font_size)
        self.font_size_spinbox.valueChanged.connect(self.window._on_font_size_changed)
        font_control_layout.addWidget(self.font_size_spinbox)
        font_control_layout.addStretch()
        layout.addLayout(font_control_layout)
        
        # Comparison tree widget
        self.compare_tree = QtWidgets.QTreeWidget()
        self.compare_tree.setAlternatingRowColors(True)
        self.compare_tree.setRootIsDecorated(True)
        self.compare_tree.setItemsExpandable(True)
        self.compare_tree.setExpandsOnDoubleClick(True)
        self.compare_tree.setFont(QtGui.QFont("Consolas", self.font_size))
        self.compare_tree.header().setStretchLastSection(False)
        layout.addWidget(self.compare_tree)
        
        # Connect resize event
        self.compare_tree.header().sectionResized.connect(self.window._on_column_resized)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.window.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def create_filter_panel(self):
        """Create filter panel with checkboxes for timing types and stages."""
        panel = QtWidgets.QGroupBox("Filters")
        panel_layout = QtWidgets.QHBoxLayout()
        panel_layout.setContentsMargins(5, 5, 5, 5)
        
        # Timing types filter
        timing_types_group = QtWidgets.QGroupBox("Timing Types")
        timing_types_group.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        timing_types_layout = QtWidgets.QHBoxLayout()
        timing_types_layout.setContentsMargins(5, 5, 5, 5)
        
        self.timing_type_checks['setup'] = QtWidgets.QCheckBox("SETUP")
        self.timing_type_checks['setup'].setChecked(True)
        self.timing_type_checks['setup'].stateChanged.connect(self.window._on_filter_changed)
        
        self.timing_type_checks['hold'] = QtWidgets.QCheckBox("HOLD")
        self.timing_type_checks['hold'].setChecked(True)
        self.timing_type_checks['hold'].stateChanged.connect(self.window._on_filter_changed)
        
        self.timing_type_checks['drv'] = QtWidgets.QCheckBox("DRV")
        self.timing_type_checks['drv'].setChecked(True)
        self.timing_type_checks['drv'].stateChanged.connect(self.window._on_filter_changed)
        
        timing_types_layout.addWidget(self.timing_type_checks['setup'])
        timing_types_layout.addWidget(self.timing_type_checks['hold'])
        timing_types_layout.addWidget(self.timing_type_checks['drv'])
        timing_types_group.setLayout(timing_types_layout)
        
        # Stages filter
        stages_group = QtWidgets.QGroupBox("Stages")
        stages_group.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        stages_layout = QtWidgets.QHBoxLayout()
        stages_layout.setContentsMargins(5, 5, 5, 5)
        self.stages_layout = stages_layout
        stages_group.setLayout(stages_layout)
        
        # Categories filter
        categories_group = QtWidgets.QGroupBox("Categories")
        categories_group.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        categories_layout = QtWidgets.QHBoxLayout()
        categories_layout.setContentsMargins(5, 5, 5, 5)
        self.categories_layout = categories_layout
        categories_group.setLayout(categories_layout)
        
        # DRV Categories filter
        drv_categories_group = QtWidgets.QGroupBox("DRV Categories")
        drv_categories_group.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        drv_categories_layout = QtWidgets.QHBoxLayout()
        drv_categories_layout.setContentsMargins(5, 5, 5, 5)
        self.drv_categories_layout = drv_categories_layout
        drv_categories_group.setLayout(drv_categories_layout)
        
        panel_layout.addWidget(timing_types_group)
        panel_layout.addWidget(stages_group)
        panel_layout.addWidget(categories_group)
        panel_layout.addWidget(drv_categories_group)
        panel_layout.addStretch()
        panel.setLayout(panel_layout)
        
        return panel
    
    def populate_stage_checkboxes(self, all_stages: List[str]):
        """Populate stage checkboxes based on available stages."""
        while self.stages_layout.count():
            item = self.stages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.stage_checks.clear()
        
        for stage in all_stages:
            checkbox = QtWidgets.QCheckBox(stage.upper())
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.window._on_filter_changed)
            self.stage_checks[stage] = checkbox
            self.stages_layout.addWidget(checkbox)
        
        self.stages_layout.addStretch()
    
    def populate_category_checkboxes(self, metric_categories: Dict, drv_categories: Dict):
        """Populate category checkboxes based on available categories."""
        # Clear timing categories
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.category_checks.clear()
        
        # Create checkboxes for timing categories
        categories_list = sorted(metric_categories.keys())
        default_categories = {'in2reg', 'reg2reg', 'reg2out'}
        
        for category in categories_list:
            checkbox = QtWidgets.QCheckBox(category.upper())
            checkbox.setChecked(category.lower() in default_categories)
            checkbox.stateChanged.connect(self.window._on_filter_changed)
            self.category_checks[category] = checkbox
            self.categories_layout.addWidget(checkbox)
        
        self.categories_layout.addStretch()
        
        # Clear DRV categories
        while self.drv_categories_layout.count():
            item = self.drv_categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.drv_category_checks.clear()
        
        # Create checkboxes for DRV categories
        drv_categories_list = sorted(drv_categories.keys())
        for category in drv_categories_list:
            checkbox = QtWidgets.QCheckBox(category.upper())
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.window._on_filter_changed)
            self.drv_category_checks[category] = checkbox
            self.drv_categories_layout.addWidget(checkbox)
        
        self.drv_categories_layout.addStretch()

