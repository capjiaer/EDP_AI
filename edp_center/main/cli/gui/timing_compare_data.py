"""Data loading and processing for Timing Compare Window."""

import os
from typing import Dict, List
from pathlib import Path

from .utils.timing_parser import find_all_timing_directories, parse_timing_csv_files
from .utils.timing_utils import (
    extract_categories_from_metrics,
    extract_drv_categories_from_metrics,
)


class TimingCompareDataLoader:
    """Data loader for Timing Compare Window."""
    
    def __init__(self, version_list: List[Dict]):
        self.version_list = version_list
        self.all_data = []  # List of (version_info, timing_data) tuples
        self.all_stages = []
        self.metric_categories = {}
        self.drv_categories = {}
    
    def load_all_data(self):
        """Load timing data for all versions."""
        self.all_data = []
        
        # Always include all versions, even if they have no data
        for version_info in self.version_list:
            data = self._load_version_timing_data(version_info)
            # Always append, even if data is empty
            self.all_data.append((version_info, data if data else {}))
        
        return len(self.all_data) > 0
    
    def _load_version_timing_data(self, version_info: Dict) -> Dict:
        """Load timing data for a single version (EDP structure).
        
        EDP structure: RELEASE/{block}/{user}/{version}/data/{flow}.{step}/timing/
        A version may have multiple flow.step directories, each with its own timing.
        We merge all timing data from all flow.step directories.
        """
        # Find all timing directories for this version (one per flow.step)
        timing_dirs = find_all_timing_directories(version_info)
        
        if not timing_dirs:
            return {}
        
        # Merge timing data from all flow.step directories
        merged_timing_data = {}
        
        for flow_step, timing_dir in timing_dirs.items():
            if not os.path.isdir(timing_dir):
                continue
            
            csv_files = [f for f in os.listdir(timing_dir) if f.endswith('.csv')]
            if not csv_files:
                continue
            
            # Parse CSV files for this flow.step
            step_timing_data = parse_timing_csv_files(timing_dir, csv_files)
            
            # Merge into merged_timing_data
            # Stage names come from CSV filenames (e.g., 'place.csv' -> 'place')
            for stage, stage_data in step_timing_data.items():
                if stage not in merged_timing_data:
                    merged_timing_data[stage] = {}
                
                # Merge timing types (setup, hold, drv)
                for timing_type, timing_type_data in stage_data.items():
                    if timing_type not in merged_timing_data[stage]:
                        merged_timing_data[stage][timing_type] = {}
                    
                    # Merge metrics
                    merged_timing_data[stage][timing_type].update(timing_type_data)
        
        return merged_timing_data
    
    def analyze_data(self):
        """Analyze loaded data to extract stages and categories."""
        # Collect all stages, timing types, and metrics
        all_stages = set()
        all_metrics = set()
        all_drv_metrics = set()
        
        for version_info, timing_data in self.all_data:
            all_stages.update(timing_data.keys())
            for stage_data in timing_data.values():
                for timing_type, timing_type_data in stage_data.items():
                    if timing_type.lower() == 'drv':
                        all_drv_metrics.update(timing_type_data.keys())
                    else:
                        all_metrics.update(timing_type_data.keys())
        
        self.all_stages = sorted(all_stages) if all_stages else ['place']
        
        # Organize metrics by category using utility functions
        self.metric_categories = extract_categories_from_metrics(all_metrics, return_list=False)
        self.drv_categories = extract_drv_categories_from_metrics(all_drv_metrics, return_list=False)

