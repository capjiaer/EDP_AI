"""Table building and rendering for Timing Compare Window."""

from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Dict, List

from .utils.timing_utils import (
    apply_color_coding_to_item,
    apply_visual_separator,
    STANDARD_METRICS,
)


class TimingCompareTableBuilder:
    """Builder for Timing Compare table structure."""
    
    def __init__(self, compare_tree: QtWidgets.QTreeWidget, font_size: int = 12):
        self.compare_tree = compare_tree
        self.font_size = font_size
        self.num_columns = 0
    
    def add_timing_type_section(self, timing_type: str, selected_stages: List[str], 
                                selected_categories: Dict, all_data: List):
        """Add timing type section (SETUP or HOLD) with all categories in one table."""
        timing_item = QtWidgets.QTreeWidgetItem(self.compare_tree)
        timing_item.setText(0, timing_type.upper())
        timing_item.setExpanded(True)
        timing_item.setBackground(0, QtGui.QColor(235, 245, 255))
        timing_item.setFont(0, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
        
        # Create header row with all categories
        self.create_table_header(timing_item, selected_categories)
        
        # For each stage and version combination, create a data row
        row_index = 0
        for stage in selected_stages:
            for version_info, timing_data in all_data:
                version_label = version_info.get('version', 'Unknown')
                
                # Create data row
                data_row_item = QtWidgets.QTreeWidgetItem(timing_item)
                data_row_item.setText(0, version_label)
                data_row_item.setText(1, stage.upper())
                
                # Apply zebra striping
                base_bg_color = QtGui.QColor(255, 255, 255) if row_index % 2 == 0 else QtGui.QColor(245, 245, 245)
                data_row_item.setBackground(0, base_bg_color)
                data_row_item.setBackground(1, base_bg_color)
                
                # Populate all categories' metrics in columns
                col_idx = 2
                categories_list = sorted(selected_categories.keys())
                for category in categories_list:
                    for metric in STANDARD_METRICS:
                        stage_data = timing_data.get(stage, {})
                        timing_type_data = stage_data.get(timing_type.lower(), {})
                        key = f"{category}_{metric}"
                        value = timing_type_data.get(key, '')
                        
                        self._populate_cell(data_row_item, col_idx, value, metric, base_bg_color, row_index == 0 and col_idx == 2)
                        col_idx += 1
                
                row_index += 1
    
    def add_drv_section(self, selected_stages: List[str], selected_drv_categories: Dict, all_data: List):
        """Add DRV section with all categories in one table."""
        drv_item = QtWidgets.QTreeWidgetItem(self.compare_tree)
        drv_item.setText(0, "DRV")
        drv_item.setExpanded(True)
        drv_item.setBackground(0, QtGui.QColor(235, 245, 255))
        drv_item.setFont(0, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
        
        # Create header row with all categories
        self.create_table_header(drv_item, selected_drv_categories, is_drv=True)
        
        # For each stage and version combination, create a data row
        row_index = 0
        for stage in selected_stages:
            for version_info, timing_data in all_data:
                version_label = version_info.get('version', 'Unknown')
                
                # Create data row
                data_row_item = QtWidgets.QTreeWidgetItem(drv_item)
                data_row_item.setText(0, version_label)
                data_row_item.setText(1, stage.upper())
                
                # Apply zebra striping
                base_bg_color = QtGui.QColor(255, 255, 255) if row_index % 2 == 0 else QtGui.QColor(245, 245, 245)
                data_row_item.setBackground(0, base_bg_color)
                data_row_item.setBackground(1, base_bg_color)
                
                # Populate all categories' metrics in columns
                col_idx = 2
                categories_list = sorted(selected_drv_categories.keys())
                for category in categories_list:
                    for metric in STANDARD_METRICS:
                        stage_data = timing_data.get(stage, {})
                        drv_data = stage_data.get('drv', {})
                        key = f"{category}_{metric}"
                        value = drv_data.get(key, '')
                        
                        self._populate_cell(data_row_item, col_idx, value, metric, base_bg_color, row_index == 0 and col_idx == 2)
                        col_idx += 1
                
                row_index += 1
    
    def _populate_cell(self, data_row_item: QtWidgets.QTreeWidgetItem, col_idx: int, 
                      value: str, metric: str, base_bg_color: QtGui.QColor, is_first: bool):
        """Populate a single cell with value or NA."""
        if value:
            data_row_item.setText(col_idx, str(value))
            data_row_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
            apply_color_coding_to_item(data_row_item, value, metric, col_idx)
            
            # If not color-coded, apply zebra striping
            brush = data_row_item.background(col_idx)
            if not brush or brush.style() == QtCore.Qt.NoBrush:
                data_row_item.setBackground(col_idx, base_bg_color)
        else:
            # Show "NA" for missing data, with grayed out style
            data_row_item.setText(col_idx, 'NA')
            data_row_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
            data_row_item.setBackground(col_idx, base_bg_color)
            data_row_item.setForeground(col_idx, QtGui.QColor(180, 180, 180))  # Gray color
            font = data_row_item.font(col_idx)
            font.setItalic(True)  # Italic for NA
            data_row_item.setFont(col_idx, font)
        
        # Add visual separator for first metric of first category
        if is_first:
            apply_visual_separator(data_row_item, col_idx, is_first=True)
    
    def create_table_header(self, parent_item: QtWidgets.QTreeWidgetItem, categories: Dict, is_drv: bool = False):
        """Create two-row header for a timing type section."""
        # First row: Category names (spanning 3 columns each)
        category_header_item = QtWidgets.QTreeWidgetItem(parent_item)
        # Use DRV_TYPE for DRV, PATH_TYPE for timing types
        header_label = "DRV_TYPE" if is_drv else "PATH_TYPE"
        category_header_item.setText(0, header_label)
        category_header_item.setText(1, "")  # Empty for first row
        category_header_item.setBackground(0, QtGui.QColor(245, 245, 245))
        category_header_item.setBackground(1, QtGui.QColor(245, 245, 245))
        category_header_item.setFont(0, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
        category_header_item.setFont(1, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
        
        # Second row: Metric names (WNS, TNS, VIO_NUM for each category)
        metric_header_item = QtWidgets.QTreeWidgetItem(category_header_item)
        metric_header_item.setText(0, "VIOLATION")
        metric_header_item.setText(1, "")  # Empty for second row
        metric_header_item.setBackground(0, QtGui.QColor(250, 250, 250))
        metric_header_item.setBackground(1, QtGui.QColor(250, 250, 250))
        metric_header_item.setFont(0, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
        metric_header_item.setFont(1, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
        
        # Add columns for each category
        col_idx = 2
        categories_list = sorted(categories.keys())
        for category_idx, category in enumerate(categories_list):
            # First row: Category name should be centered over the 3 metric columns
            # Put the category name in the middle column (TNS column) to visually center it
            # WNS column (col_idx): empty
            category_header_item.setText(col_idx, "")
            category_header_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
            category_header_item.setBackground(col_idx, QtGui.QColor(245, 245, 245))
            
            # TNS column (col_idx + 1): category name (centered)
            category_header_item.setText(col_idx + 1, category.upper())
            category_header_item.setTextAlignment(col_idx + 1, QtCore.Qt.AlignCenter)
            category_header_item.setBackground(col_idx + 1, QtGui.QColor(245, 245, 245))
            category_header_item.setFont(col_idx + 1, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
            
            # VIO_PATHS column (col_idx + 2): empty
            if col_idx + 2 < self.num_columns:
                category_header_item.setText(col_idx + 2, "")
                category_header_item.setTextAlignment(col_idx + 2, QtCore.Qt.AlignCenter)
                category_header_item.setBackground(col_idx + 2, QtGui.QColor(245, 245, 245))
            
            # Second row: Metrics (WNS, TNS, VIO_NUM)
            for metric_idx, metric in enumerate(STANDARD_METRICS):
                metric_header_item.setText(col_idx, metric.upper())
                metric_header_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
                metric_header_item.setBackground(col_idx, QtGui.QColor(250, 250, 250))
                metric_header_item.setFont(col_idx, QtGui.QFont("Consolas", self.font_size, QtGui.QFont.Bold))
                
                # Add visual separator for first metric of first category
                if col_idx == 2:
                    apply_visual_separator(metric_header_item, col_idx, is_first=True)
                
                col_idx += 1
    
    def adjust_column_widths(self, column_width_ratios: Dict, initial_column_widths: Dict):
        """Expand all items and adjust column widths."""
        self.compare_tree.expandAll()
        
        # Resize all columns to contents first
        for i in range(self.compare_tree.columnCount()):
            self.compare_tree.resizeColumnToContents(i)
        
        # Set minimum width for all columns
        for i in range(self.compare_tree.columnCount()):
            current_width = self.compare_tree.columnWidth(i)
            min_width = max(current_width, 80)
            self.compare_tree.setColumnWidth(i, min_width)
        
        # Calculate total width and store ratios
        total_width = sum(self.compare_tree.columnWidth(i) for i in range(self.compare_tree.columnCount()))
        if total_width > 0:
            for i in range(self.compare_tree.columnCount()):
                column_width_ratios[i] = self.compare_tree.columnWidth(i) / total_width
                initial_column_widths[i] = self.compare_tree.columnWidth(i)
        
        # Set resize modes for all columns - all are interactive
        for i in range(self.compare_tree.columnCount()):
            self.compare_tree.header().setSectionResizeMode(i, QtWidgets.QHeaderView.Interactive)
        
        # Calculate minimum width needed for all columns
        total_min_width = sum(self.compare_tree.columnWidth(i) for i in range(self.compare_tree.columnCount()))
        total_min_width += 50  # Add some padding for borders and scrollbar
        
        # Set minimum window width to prevent shrinking too much
        window = self.compare_tree.window()
        if window:
            window.setMinimumWidth(int(total_min_width))
            
            # Adjust window width to fit content initially (but allow manual resizing)
            current_width = window.width()
            if current_width < total_min_width:
                # Expand window if content is larger than current width
                app = QtWidgets.QApplication.instance()
                if app:
                    screen_width = app.desktop().screenGeometry().width()
                else:
                    screen_width = 1920  # Default fallback
                new_width = min(total_min_width, screen_width * 0.9)  # Max 90% of screen width
                window.resize(int(new_width), window.height())

