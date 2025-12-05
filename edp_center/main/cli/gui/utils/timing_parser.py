"""Timing CSV file parser utilities for EDP."""

import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import csv


def find_timing_directory(version_info: Dict) -> str:
    """Find timing directory for a version (EDP structure).
    
    Args:
        version_info: Dictionary containing release_dir, block, user, version
        
    Returns:
        Path to timing directory, or empty string if not found
        
    EDP structure:
        RELEASE/{block}/{user}/{version}/data/{flow}.{step}/timing/
    """
    release_dir = version_info.get('release_dir', '')
    block = version_info.get('block', '')
    user = version_info.get('user', '')
    version = version_info.get('version', '')
    
    if not all([release_dir, block, user, version]):
        return ""
    
    # EDP structure: RELEASE/{block}/{user}/{version}/data/
    version_dir = Path(release_dir) / block / user / version / 'data'
    
    if not version_dir.exists():
        return ""
    
    # 查找所有 flow.step 目录下的 timing
    # 返回第一个找到的 timing 目录（或者可以返回所有，这里先返回第一个）
    # 注意：一个版本可能有多个 flow.step，每个都有自己的 timing
    # 这里我们返回 data 目录，让调用者处理多个 flow.step 的情况
    return str(version_dir)


def find_all_timing_directories(version_info: Dict) -> Dict[str, str]:
    """Find all timing directories for a version (EDP structure).
    
    Args:
        version_info: Dictionary containing release_dir, block, user, version
        
    Returns:
        Dictionary mapping flow.step to timing directory path
        Example: {'pnr_innovus.place': '/path/to/timing', ...}
    """
    release_dir = version_info.get('release_dir', '')
    block = version_info.get('block', '')
    user = version_info.get('user', '')
    version = version_info.get('version', '')
    
    if not all([release_dir, block, user, version]):
        return {}
    
    version_dir = Path(release_dir) / block / user / version / 'data'
    
    if not version_dir.exists():
        return {}
    
    timing_dirs = {}
    for step_dir in version_dir.iterdir():
        if step_dir.is_dir():
            timing_dir = step_dir / 'timing'
            if timing_dir.exists():
                timing_dirs[step_dir.name] = str(timing_dir)
    
    return timing_dirs


def parse_timing_csv_files(timing_dir: str, csv_files: List[str] = None) -> Dict:
    """Parse CSV files and organize timing data.
    
    Args:
        timing_dir: Directory containing CSV files
        csv_files: List of CSV file names (if None, will scan directory)
        
    Returns:
        Dictionary with structure: {stage: {timing_type: {key: value}}}
        Example: {'place': {'setup': {'reg2reg_wns': '-0.3'}, 'drv': {'max_tran_wns': '-0.105'}}}
    """
    timing_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    
    timing_path = Path(timing_dir)
    if not timing_path.exists():
        return timing_data
    
    # 如果没有指定 csv_files，扫描目录
    if csv_files is None:
        csv_files = [f.name for f in timing_path.iterdir() if f.suffix == '.csv']
    
    for csv_file in csv_files:
        # Stage name is derived from filename (e.g., 'place.csv' -> 'place')
        stage = csv_file.replace('.csv', '')
        file_path = timing_path / csv_file
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    check_type = row.get('check_type', '')
                    sub1 = row.get('sub_category_1', '')
                    sub2 = row.get('sub_category_2', '')
                    sub3 = row.get('sub_category_3', '')
                    value = row.get('value', '')
                    
                    # Parse timing data (setup/hold)
                    if check_type == 'timing' and sub1.lower() in ['setup', 'hold']:
                        timing_type = sub1.lower()
                        category = sub2  # e.g., 'reg2reg'
                        metric = sub3  # e.g., 'wns', 'tns', 'vio_paths'
                        
                        if category and metric:
                            key = f"{category}_{metric}"
                            timing_data[stage][timing_type][key] = value
                    
                    # Parse DRV data
                    elif check_type == 'drv':
                        drv_type = sub1.lower()  # max_tran, max_cap, max_length
                        metric = sub2.lower()  # wns, vio_paths
                        
                        if drv_type and metric:
                            key = f"{drv_type}_{metric}"
                            timing_data[stage]['drv'][key] = value
        except Exception as e:
            print(f"Error parsing {csv_file}: {e}")
    
    return timing_data

