"""Main window for timing comparison."""

from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Dict, List

from .timing_compare_ui import TimingCompareUIBuilder
from .timing_compare_data import TimingCompareDataLoader
from .timing_compare_table import TimingCompareTableBuilder


class TimingCompareWindow(QtWidgets.QDialog):
    """Window to compare timing information from multiple versions."""
    
    def __init__(self, version_list: List[Dict], parent=None):
        super().__init__(parent)
        self.version_list = version_list
        self.setWindowTitle(f"Timing Comparison - {len(version_list)} versions")
        self.setMinimumSize(1400, 800)
        # Allow window to be maximized
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        
        # Font size
        self.font_size = 12  # Default font size
        
        # Store column width ratios for proportional resizing
        self.column_width_ratios = {}  # {col_idx: ratio}
        self.initial_column_widths = {}  # {col_idx: initial_width}
        
        # Initialize components
        self.ui_builder = TimingCompareUIBuilder(self, version_list, self.font_size)
        self.data_loader = TimingCompareDataLoader(version_list)
        self.table_builder = None  # Will be initialized after UI setup
        
        # Setup UI
        self.ui_builder.setup_ui()
        self.table_builder = TimingCompareTableBuilder(self.ui_builder.compare_tree, self.font_size)
        
        # Load data and populate
        self._load_comparison_data()
    
    def _load_comparison_data(self):
        """Load timing data for all versions and create comparison tree."""
        if not self.data_loader.load_all_data():
            root_item = QtWidgets.QTreeWidgetItem(self.ui_builder.compare_tree)
            root_item.setText(0, "No versions selected")
            return
        
        # Analyze data to extract stages and categories
        self.data_loader.analyze_data()
        
        # Populate UI checkboxes
        self.ui_builder.populate_stage_checkboxes(self.data_loader.all_stages)
        self.ui_builder.populate_category_checkboxes(
            self.data_loader.metric_categories,
            self.data_loader.drv_categories
        )
        
        # Apply filters and build tree
        self._apply_filters()
    
    def _on_filter_changed(self):
        """Handle filter checkbox state change."""
        self._apply_filters()
    
    def _on_font_size_changed(self, size: int):
        """Handle font size change."""
        self.font_size = size
        # Update tree font
        self.ui_builder.compare_tree.setFont(QtGui.QFont("Consolas", self.font_size))
        # Rebuild tree to update all item fonts
        self._apply_filters()
    
    def _on_column_resized(self, logical_index: int, old_size: int, new_size: int):
        """Handle column resize event."""
        # Update column width ratios when user manually resizes
        if self.ui_builder.compare_tree.columnCount() > 0:
            total_width = sum(self.ui_builder.compare_tree.columnWidth(i) 
                            for i in range(self.ui_builder.compare_tree.columnCount()))
            if total_width > 0:
                for i in range(self.ui_builder.compare_tree.columnCount()):
                    self.column_width_ratios[i] = (
                        self.ui_builder.compare_tree.columnWidth(i) / total_width
                    )
    
    def resizeEvent(self, event):
        """Handle window resize event."""
        super().resizeEvent(event)
        # Delay column adjustment to avoid recursive calls
        QtCore.QTimer.singleShot(50, self._adjust_columns_to_window_width)
    
    def _adjust_columns_to_window_width(self):
        """Adjust column widths proportionally to fill window width."""
        if (self.ui_builder.compare_tree.columnCount() > 0 and 
            self.column_width_ratios):
            # Get available width for columns (subtract margins)
            available_width = self.ui_builder.compare_tree.width() - 50
            
            # Keep VERSION and STAGE columns at their current width or minimum
            version_col_width = max(self.ui_builder.compare_tree.columnWidth(0), 100)
            stage_col_width = max(self.ui_builder.compare_tree.columnWidth(1), 100)
            available_width -= (version_col_width + stage_col_width)
            
            # Calculate total ratio for data columns (excluding VERSION and STAGE columns)
            data_ratio_total = sum(
                self.column_width_ratios.get(i, 0) 
                for i in range(2, self.ui_builder.compare_tree.columnCount())
            )
            
            if data_ratio_total > 0 and available_width > 0:
                # Distribute available width proportionally among data columns
                for i in range(2, self.ui_builder.compare_tree.columnCount()):
                    ratio = self.column_width_ratios.get(i, 0) / data_ratio_total
                    new_width = max(int(available_width * ratio), 80)  # Minimum 80px
                    self.ui_builder.compare_tree.setColumnWidth(i, new_width)
    
    def _apply_filters(self):
        """Apply filters and rebuild tree."""
        # Get selected timing types
        selected_timing_types = []
        for timing_type in ['setup', 'hold']:
            if (self.ui_builder.timing_type_checks.get(timing_type, None) and 
                self.ui_builder.timing_type_checks[timing_type].isChecked()):
                selected_timing_types.append(timing_type)
        
        selected_has_drv = (self.ui_builder.timing_type_checks.get('drv', None) and 
                           self.ui_builder.timing_type_checks['drv'].isChecked())
        
        # Get selected stages
        selected_stages = [
            stage for stage in self.data_loader.all_stages 
            if (self.ui_builder.stage_checks.get(stage, None) and 
                self.ui_builder.stage_checks[stage].isChecked())
        ]
        
        # Get selected categories (filter timing categories)
        selected_categories = {
            cat: self.data_loader.metric_categories[cat] 
            for cat in self.data_loader.metric_categories.keys()
            if (self.ui_builder.category_checks.get(cat, None) and 
                self.ui_builder.category_checks[cat].isChecked())
        }
        
        # Get selected DRV categories
        selected_drv_categories = {
            cat: self.data_loader.drv_categories[cat]
            for cat in self.data_loader.drv_categories.keys()
            if (self.ui_builder.drv_category_checks.get(cat, None) and 
                self.ui_builder.drv_category_checks[cat].isChecked())
        }
        
        # Validation
        if not selected_timing_types and not selected_has_drv:
            self.ui_builder.compare_tree.clear()
            self.ui_builder.compare_tree.setColumnCount(1)
            self.ui_builder.compare_tree.setHeaderLabels(["Message"])
            item = QtWidgets.QTreeWidgetItem(self.ui_builder.compare_tree)
            item.setText(0, "Please select at least one timing type")
            return
        
        if not selected_stages:
            self.ui_builder.compare_tree.clear()
            self.ui_builder.compare_tree.setColumnCount(1)
            self.ui_builder.compare_tree.setHeaderLabels(["Message"])
            item = QtWidgets.QTreeWidgetItem(self.ui_builder.compare_tree)
            item.setText(0, "Please select at least one stage")
            return
        
        # Check if at least one category is selected for timing types
        if selected_timing_types and not selected_categories:
            self.ui_builder.compare_tree.clear()
            self.ui_builder.compare_tree.setColumnCount(1)
            self.ui_builder.compare_tree.setHeaderLabels(["Message"])
            item = QtWidgets.QTreeWidgetItem(self.ui_builder.compare_tree)
            item.setText(0, "Please select at least one category for timing types")
            return
        
        # Check if at least one DRV category is selected if DRV is selected
        if selected_has_drv and not selected_drv_categories:
            self.ui_builder.compare_tree.clear()
            self.ui_builder.compare_tree.setColumnCount(1)
            self.ui_builder.compare_tree.setHeaderLabels(["Message"])
            item = QtWidgets.QTreeWidgetItem(self.ui_builder.compare_tree)
            item.setText(0, "Please select at least one DRV category")
            return
        
        # Calculate column count: VERSION | STAGE | (category * 3 metrics) for each selected category
        max_timing_cols = 2 + len(selected_categories) * 3 if selected_categories else 0
        max_drv_cols = 2 + len(selected_drv_categories) * 3 if selected_drv_categories else 0
        self.table_builder.num_columns = max(max_timing_cols, max_drv_cols, 2)
        
        # Set column count
        self.ui_builder.compare_tree.setColumnCount(self.table_builder.num_columns)
        self.ui_builder.compare_tree.setHeaderLabels([''] * self.table_builder.num_columns)
        
        # Clear tree
        self.ui_builder.compare_tree.clear()
        
        # Build tree by timing type (SETUP, HOLD, DRV)
        # Add SETUP section
        if 'setup' in selected_timing_types and selected_categories:
            self.table_builder.add_timing_type_section(
                'setup', selected_stages, selected_categories, self.data_loader.all_data
            )
        
        # Add HOLD section
        if 'hold' in selected_timing_types and selected_categories:
            self.table_builder.add_timing_type_section(
                'hold', selected_stages, selected_categories, self.data_loader.all_data
            )
        
        # Add DRV section
        if selected_has_drv and selected_drv_categories:
            self.table_builder.add_drv_section(
                selected_stages, selected_drv_categories, self.data_loader.all_data
            )
        
        # Expand all and adjust column widths
        self.table_builder.adjust_column_widths(
            self.column_width_ratios, self.initial_column_widths
        )
