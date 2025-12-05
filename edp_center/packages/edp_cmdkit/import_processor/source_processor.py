#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Source Processor - Source 导入处理模块
"""

from pathlib import Path
from typing import List, Optional
import logging
from ..source_generator import generate_source_statement

logger = logging.getLogger(__name__)


class SourceProcessor:
    """Source 导入处理器"""
    
    def process_import_source(
        self,
        import_file: str,
        base_file: Path,
        search_paths: List[Path],
        hooks_dir: Optional[Path]
    ) -> str:
        """
        处理 #import source 指令
        
        Args:
            import_file: 要导入的文件名
            base_file: 基础文件路径（用于解析相对路径）
            search_paths: 搜索路径列表
            hooks_dir: hooks 目录路径（保留用于未来扩展）
        
        Returns:
            生成的 source 语句
        """
        # source 模式：生成 source 语句
        source_line = generate_source_statement(
            import_file, base_file, search_paths, recursive=True
        )
        
        return source_line

