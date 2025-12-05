#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV Reader Helper
辅助类，用于读取和验证 CSV 文件
"""

import os
import logging

logger = logging.getLogger(__name__)

class CSVReader:
    """CSV 读取辅助类"""
    
    @staticmethod
    def find_metrics_csv(run_dir: str) -> str:
        """
        在运行目录中查找 Metrics CSV 文件
        
        Args:
            run_dir: 运行目录路径 (e.g., .../data/pnr_innovus.place/)
            
        Returns:
            CSV 文件路径，如果未找到则返回 None
        """
        if not os.path.exists(run_dir):
            return None
            
        # 策略 1: 查找 *.csv (假设只有一个主要的 metrics csv)
        # 通常文件名与 step 名相关，例如 place.csv
        step_name = os.path.basename(run_dir)
        # step_name可能是 "pnr_innovus.place"
        # 尝试简单的名称匹配
        
        # 1. 精确匹配 step 后缀 (e.g. place.csv)
        if '.' in step_name:
            suffix = step_name.split('.')[-1]
            csv_path = os.path.join(run_dir, f"{suffix}.csv")
            if os.path.exists(csv_path):
                return csv_path
                
        # 2. 尝试匹配目录名 (e.g. pnr_innovus.place.csv)
        csv_path = os.path.join(run_dir, f"{step_name}.csv")
        if os.path.exists(csv_path):
            return csv_path
            
        # 3. 遍历目录查找任何 CSV
        # 排除 timing/ 目录下的详细时序报告
        for file in os.listdir(run_dir):
            if file.endswith('.csv') and os.path.isfile(os.path.join(run_dir, file)):
                return os.path.join(run_dir, file)
                
        return None

