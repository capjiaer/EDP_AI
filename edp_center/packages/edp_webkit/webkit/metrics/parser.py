#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metrics Parser
解析 Metrics CSV 数据，转换为结构化格式供 Dashboard 使用
"""

import csv
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetricsParser:
    """
    Metrics 数据解析器
    负责读取 CSV 格式的 Metrics 数据，并将其转换为 JSON 友好的字典格式
    """
    
    def __init__(self):
        pass
        
    def parse_csv(self, file_path: str) -> Dict[str, Any]:
        """
        解析 Metrics CSV 文件
        
        Args:
            file_path: CSV 文件路径
            
        Returns:
            包含解析后数据的字典
        """
        if not os.path.exists(file_path):
            logger.warning(f"Metrics CSV file not found: {file_path}")
            return {}
            
        try:
            data = {
                'summary': {},
                'categories': {}
            }
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 移除 BOM（如果存在）
                if reader.fieldnames and reader.fieldnames[0].startswith('#'):
                    reader.fieldnames[0] = reader.fieldnames[0].lstrip('#')
                
                # 检查必要的列头
                required_fields = ['stage', 'check_type', 'value']
                if not reader.fieldnames or not all(field in reader.fieldnames for field in required_fields):
                    logger.error(f"Invalid CSV format in {file_path}. Missing required columns.")
                    return {}
                
                for row in reader:
                    self._process_row(row, data)
                    
            return data
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {e}")
            return {}
            
    def _process_row(self, row: Dict[str, str], data: Dict[str, Any]):
        """处理单行数据"""
        stage = row.get('stage', '')
        check_type = row.get('check_type', '')
        
        # 构建层级 key: sub_category_1 -> sub_category_2 -> ...
        # 过滤空值
        categories = [
            row.get(f'sub_category_{i}', '').strip() 
            for i in range(1, 5) 
            if row.get(f'sub_category_{i}', '').strip()
        ]
        
        value = row.get('value', '').strip()
        
        # 尝试转换数值
        parsed_value = self._parse_value(value)
        
        # 组织数据结构
        # 1. 按 check_type 分类
        if check_type not in data['categories']:
            data['categories'][check_type] = []
            
        item = {
            'stage': stage,
            'path': categories,
            'value': parsed_value,
            'raw_value': value
        }
        
        data['categories'][check_type].append(item)
        
        # 2. 如果是关键指标（没有 sub_categories 的），添加到 summary
        if not categories:
            if stage not in data['summary']:
                data['summary'][stage] = {}
            data['summary'][stage][check_type] = parsed_value

    def _parse_value(self, value_str: str) -> Any:
        """尝试解析数值"""
        if not value_str:
            return None
            
        # 处理百分比
        if value_str.endswith('%'):
            try:
                return float(value_str.rstrip('%'))
            except ValueError:
                pass
                
        # 处理整数
        try:
            if '.' not in value_str:
                return int(value_str)
        except ValueError:
            pass
            
        # 处理浮点数
        try:
            return float(value_str)
        except ValueError:
            pass
            
        # 返回原始字符串
        return value_str

