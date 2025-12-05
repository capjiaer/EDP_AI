"""Timing utility functions for UI display and data processing."""

from typing import Dict, List, Set
from collections import defaultdict
from PyQt5 import QtWidgets, QtGui, QtCore


# Standard metrics
STANDARD_METRICS = ['wns', 'tns', 'vio_paths']
DRV_STANDARD_METRICS = ['wns', 'vio_paths']


def extract_categories_from_metrics(all_metrics: Set[str], return_list: bool = False) -> Dict:
    """Extract categories from metric keys.
    
    Args:
        all_metrics: Set of metric keys like {'reg2reg_wns', 'reg2reg_tns', 'macro2reg_vio_paths'}
        return_list: If True, return Dict[str, List[str]], else Dict[str, Set[str]]
        
    Returns:
        Dictionary mapping category to list/set of metrics: {'reg2reg': ['wns', 'tns'], ...}
    """
    if return_list:
        metric_categories = defaultdict(list)
    else:
        metric_categories = defaultdict(set)
    
    for metric_key in sorted(all_metrics):
        # Try to match against standard metrics (from longest to shortest)
        # This handles 'vio_paths' correctly before trying 'paths'
        matched = False
        for std_metric in sorted(STANDARD_METRICS, key=len, reverse=True):
            if metric_key.endswith(f"_{std_metric}"):
                category = metric_key[:-len(f"_{std_metric}")]
                if return_list:
                    metric_categories[category].append(std_metric)
                else:
                    metric_categories[category].add(std_metric)
                matched = True
                break
        
        # Fallback: if no match, use rsplit (for any non-standard metrics)
        if not matched:
            parts = metric_key.rsplit('_', 1)
            if len(parts) == 2:
                category, metric_name = parts
                if return_list:
                    metric_categories[category].append(metric_name)
                else:
                    metric_categories[category].add(metric_name)
    
    return metric_categories


def extract_drv_categories_from_metrics(all_drv_metrics: Set[str], return_list: bool = False) -> Dict:
    """Extract DRV categories from metric keys.
    
    Args:
        all_drv_metrics: Set of DRV metric keys like {'max_tran_wns', 'max_tran_vio_paths', ...}
        return_list: If True, return Dict[str, List[str]], else Dict[str, Set[str]]
        
    Returns:
        Dictionary mapping DRV category to list/set of metrics: {'max_tran': ['wns', 'vio_paths'], ...}
    """
    if return_list:
        drv_categories = defaultdict(list)
    else:
        drv_categories = defaultdict(set)
    
    for drv_metric_key in sorted(all_drv_metrics):
        # Try to match against standard DRV metrics (from longest to shortest)
        # This handles 'vio_paths' correctly before trying 'paths'
        matched = False
        for std_metric in sorted(DRV_STANDARD_METRICS, key=len, reverse=True):
            if drv_metric_key.endswith(f"_{std_metric}"):
                drv_category = drv_metric_key[:-len(f"_{std_metric}")]
                if return_list:
                    drv_categories[drv_category].append(std_metric)
                else:
                    drv_categories[drv_category].add(std_metric)
                matched = True
                break
        
        # Fallback: if no match, use rsplit (shouldn't happen for DRV)
        if not matched:
            parts = drv_metric_key.rsplit('_', 1)
            if len(parts) == 2:
                drv_category, drv_metric = parts
                if drv_metric in DRV_STANDARD_METRICS:
                    if return_list:
                        drv_categories[drv_category].append(drv_metric)
                    else:
                        drv_categories[drv_category].add(drv_metric)
    
    return drv_categories


def apply_color_coding_to_item(item: QtWidgets.QTreeWidgetItem, value: str, metric: str, col_idx: int):
    """Apply color coding to tree item cells based on value.
    
    Color scheme:
    - Green (200, 255, 200): WNS/TNS >= 0 (good)
    - Yellow (255, 255, 200): WNS/TNS >= -0.1 (warning)
    - Red (255, 200, 200): WNS/TNS < -0.1 (bad)
    
    Args:
        item: QTreeWidgetItem to apply color to
        value: Value string to evaluate
        metric: Metric name (wns, tns, vio_paths, etc.)
        col_idx: Column index to apply color to
    """
    try:
        num_value = float(value)
        if metric in ['wns', 'tns']:
            if num_value >= 0:
                item.setBackground(col_idx, QtGui.QColor(200, 255, 200))  # Light green
            elif num_value >= -0.1:
                item.setBackground(col_idx, QtGui.QColor(255, 255, 200))  # Light yellow
            else:
                item.setBackground(col_idx, QtGui.QColor(255, 200, 200))  # Light red
    except (ValueError, TypeError):
        pass


def apply_visual_separator(item: QtWidgets.QTreeWidgetItem, col_idx: int, is_first: bool = False):
    """Apply visual separator (darker background) to item column.
    
    Only applies separator if the background is not color-coded (not red/yellow/green).
    
    Args:
        item: QTreeWidgetItem to apply separator to
        col_idx: Column index to apply separator to
        is_first: If True, use lighter separator color (for first category)
    """
    if col_idx <= 0:  # Don't apply to STAGE column
        return
    
    brush = item.background(col_idx)
    if brush and brush.style() != QtCore.Qt.NoBrush:
        current_bg = brush.color()
        # Only apply separator if background is light (not color-coded for violations)
        if current_bg.red() > 200 and current_bg.green() > 200:
            # Make it darker for separator
            border_color = QtGui.QColor(max(0, current_bg.red() - 15), 
                                       max(0, current_bg.green() - 15), 
                                       max(0, current_bg.blue() - 15))
            item.setBackground(col_idx, border_color)
    else:
        # Default background, make it darker for separator
        border_color = QtGui.QColor(235, 235, 235) if is_first else QtGui.QColor(220, 220, 220)
        item.setBackground(col_idx, border_color)


def calculate_total_value(timing_data: Dict, key: str, metric: str) -> str:
    """Calculate total value for a metric across all stages.
    
    Args:
        timing_data: Dictionary with structure {stage: {timing_type: {key: value}}}
        key: Metric key to calculate total for
        metric: Metric name (wns, tns, vio_paths, etc.)
        
    Returns:
        Total value as string, or empty string if no values found
    """
    values = []
    for stage_data in timing_data.values():
        val = stage_data.get(key, '')
        if val:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                pass
    
    if not values:
        return ''
    
    if metric in ['wns', 'tns']:
        return f"{min(values):.3f}"
    elif 'paths' in metric.lower():
        return f"{sum(values):.0f}"
    else:
        return f"{sum(values):.3f}"


def create_category_header_row(parent_item: QtWidgets.QTreeWidgetItem, 
                                categories: Dict, 
                                num_columns: int,
                                is_drv: bool = False) -> QtWidgets.QTreeWidgetItem:
    """Create category header row with category names spanning 3 columns each.
    
    Args:
        parent_item: Parent tree item
        categories: Dictionary of categories to display
        num_columns: Total number of columns
        is_drv: If True, this is for DRV data
        
    Returns:
        Header item (for adding metric sub-header as child)
    """
    header_item = QtWidgets.QTreeWidgetItem(parent_item)
    header_item.setText(0, "")  # Empty for STAGE column
    header_item.setExpanded(False)
    header_item.setBackground(0, QtGui.QColor(220, 220, 220))
    header_item.setFont(0, QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
    
    # Set category names in header row (each category spans 3 columns)
    col_idx = 1
    categories_list = sorted(categories.keys())
    for cat_idx, category in enumerate(categories_list):
        category_name = category.upper()
        separator_color = QtGui.QColor(200, 200, 200) if cat_idx > 0 else QtGui.QColor(220, 220, 220)
        
        # Set empty text for first column, category name in middle column, empty for third
        header_item.setText(col_idx, "")
        header_item.setBackground(col_idx, separator_color)
        header_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
        
        header_item.setText(col_idx + 1, category_name)
        header_item.setBackground(col_idx + 1, QtGui.QColor(220, 220, 220))
        header_item.setTextAlignment(col_idx + 1, QtCore.Qt.AlignCenter)
        
        header_item.setText(col_idx + 2, "")
        header_item.setBackground(col_idx + 2, QtGui.QColor(220, 220, 220))
        header_item.setTextAlignment(col_idx + 2, QtCore.Qt.AlignCenter)
        col_idx += 3
    
    return header_item


def create_metric_header_row(header_item: QtWidgets.QTreeWidgetItem, 
                             categories: Dict,
                             standard_metrics: List[str]) -> QtWidgets.QTreeWidgetItem:
    """Create metric sub-header row with WNS, TNS, VIO_PATHS for each category.
    
    Args:
        header_item: Parent header item (category header row)
        categories: Dictionary of categories
        standard_metrics: List of standard metrics (e.g., ['wns', 'tns', 'vio_paths'])
        
    Returns:
        Metric header item
    """
    metric_header_item = QtWidgets.QTreeWidgetItem(header_item)
    metric_header_item.setText(0, "")
    metric_header_item.setExpanded(False)
    metric_header_item.setBackground(0, QtGui.QColor(210, 210, 210))
    metric_header_item.setFont(0, QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
    
    col_idx = 1
    categories_list = sorted(categories.keys())
    for cat_idx, category in enumerate(categories_list):
        for metric_idx, std_metric in enumerate(standard_metrics):
            metric_header_item.setText(col_idx, std_metric.upper())
            separator_color = QtGui.QColor(195, 195, 195) if (cat_idx > 0 and metric_idx == 0) else QtGui.QColor(210, 210, 210)
            metric_header_item.setBackground(col_idx, separator_color)
            metric_header_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
            col_idx += 1
    
    return metric_header_item


def populate_stage_data_row(stage_item: QtWidgets.QTreeWidgetItem,
                            stage_data: Dict,
                            timing_type: str,
                            categories: Dict,
                            standard_metrics: List[str]):
    """Populate stage data row with timing values.
    
    Args:
        stage_item: Tree item for the stage row
        stage_data: Data for the stage
        timing_type: Timing type (setup, hold, or drv)
        categories: Dictionary of categories
        standard_metrics: List of standard metrics
    """
    stage_item.setBackground(0, QtGui.QColor(240, 240, 240))
    
    timing_type_data = stage_data.get(timing_type, {})
    
    col_idx = 1
    categories_list = sorted(categories.keys())
    for cat_idx, category in enumerate(categories_list):
        metrics = sorted(categories[category])
        metric_values = {}
        for metric in metrics:
            key = f"{category}_{metric}"
            value = timing_type_data.get(key, '')
            if value:
                metric_values[metric] = value
        
        # Add standard metrics (WNS, TNS, VIO_PATHS) to columns (3 columns per category)
        for metric_idx, std_metric in enumerate(standard_metrics):
            if std_metric in metric_values:
                value = metric_values[std_metric]
                stage_item.setText(col_idx, str(value))
                stage_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
                apply_color_coding_to_item(stage_item, value, std_metric, col_idx)
            else:
                stage_item.setText(col_idx, '')
                stage_item.setTextAlignment(col_idx, QtCore.Qt.AlignCenter)
            
            # Add visual separator for WNS column (first metric) of each category
            if metric_idx == 0:
                apply_visual_separator(stage_item, col_idx, is_first=(cat_idx == 0))
            
            col_idx += 1
    
    # Ensure STAGE column (col 0) always has normal background color
    stage_item.setBackground(0, QtGui.QColor(240, 240, 240))