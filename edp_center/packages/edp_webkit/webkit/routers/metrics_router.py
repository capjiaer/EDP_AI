from typing import List, Optional, Dict
import os
import logging
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel
import yaml

# Lazy load metrics modules
try:
    from ..metrics.parser import MetricsParser
    from ..metrics.csv_reader import CSVReader
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

router = APIRouter(prefix="/metrics", tags=["metrics"])
logger = logging.getLogger(__name__)

class MetricsResponse(BaseModel):
    success: bool
    data: Dict
    error: Optional[str] = None

@router.get("/scan", response_model=MetricsResponse)
async def scan_metrics(run_path: str = Query(..., description="Step run directory path")):
    """
    扫描并解析指定 Run 目录下的 Metrics CSV
    """
    if not METRICS_AVAILABLE:
        return MetricsResponse(success=False, data={}, error="Metrics module not available")

    if not os.path.exists(run_path):
         return MetricsResponse(success=False, data={}, error=f"Path not found: {run_path}")

    csv_path = CSVReader.find_metrics_csv(run_path)
    if not csv_path:
        return MetricsResponse(success=False, data={}, error="No metrics CSV found in directory")

    try:
        parser = MetricsParser()
        result = parser.parse_csv(csv_path)
        return MetricsResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Failed to parse metrics for {run_path}: {e}")
        return MetricsResponse(success=False, data={}, error=str(e))

@router.get("/export/yaml")
async def export_yaml(run_path: str = Query(..., description="Step run directory path")):
    """
    将解析结果导出为 YAML 文件 (下载)
    """
    if not METRICS_AVAILABLE:
        raise HTTPException(status_code=500, detail="Metrics module not available")

    # 复用扫描逻辑
    # 实际项目中可以抽离为 service 层函数
    csv_path = CSVReader.find_metrics_csv(run_path)
    if not csv_path:
        raise HTTPException(status_code=404, detail="No metrics CSV found")
    
    try:
        parser = MetricsParser()
        result = parser.parse_csv(csv_path)
        
        # 转换为 YAML 字符串
        yaml_content = yaml.dump(result, allow_unicode=True, sort_keys=False)
        
        # 设置响应头，触发下载
        filename = f"metrics_{os.path.basename(run_path)}.yaml"
        return Response(content=yaml_content, media_type="application/x-yaml", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
