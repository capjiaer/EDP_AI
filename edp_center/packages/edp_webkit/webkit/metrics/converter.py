import csv
import os
import yaml
import json
import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

class DataConverter:
    """
    数据转换工具类
    用于在 CSV, YAML, Dict, JSON 之间进行格式转换
    """
    
    @staticmethod
    def csv_to_dict(csv_path: str) -> Dict[str, Any]:
        """
        读取 CSV 并转换为 Dict (基于 MetricsParser 的逻辑)
        """
        # 延迟导入以避免循环依赖
        from .parser import MetricsParser
        
        parser = MetricsParser()
        return parser.parse_csv(csv_path)

    @staticmethod
    def dict_to_yaml(data: Dict[str, Any], yaml_path: str = None) -> Union[str, None]:
        """
        将 Dict 转换为 YAML 字符串或保存为文件
        """
        try:
            yaml_str = yaml.dump(data, sort_keys=False, allow_unicode=True)
            
            if yaml_path:
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_str)
                return None
            return yaml_str
        except Exception as e:
            logger.error(f"Error converting dict to yaml: {e}")
            return None

    @staticmethod
    def csv_to_yaml(csv_path: str, yaml_path: str = None) -> Union[str, None]:
        """
        直接将 CSV 转换为 YAML
        """
        data = DataConverter.csv_to_dict(csv_path)
        if not data:
            return None
        return DataConverter.dict_to_yaml(data, yaml_path)

    @staticmethod
    def dict_to_json(data: Dict[str, Any], json_path: str = None) -> Union[str, None]:
        """
        将 Dict 转换为 JSON 字符串或保存为文件
        """
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            
            if json_path:
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                return None
            return json_str
        except Exception as e:
            logger.error(f"Error converting dict to json: {e}")
            return None

