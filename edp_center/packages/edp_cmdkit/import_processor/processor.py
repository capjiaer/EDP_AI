#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Import Processor - 主处理器类

处理 #import source 指令
"""

import re
from pathlib import Path
from typing import List, Optional
import logging
from .source_processor import SourceProcessor
from ..source_generator import generate_source_statement

# 导入框架异常类
from edp_center.packages.edp_common import EDPError, EDPFileNotFoundError, ConfigError

logger = logging.getLogger(__name__)

# #import 指令的正则表达式（只支持 source）
IMPORT_PATTERN = re.compile(
    r'^\s*#\s*import\s+source\s+(.+?)\s*$',
    re.IGNORECASE
)


class ImportProcessor:
    """Import 指令处理器"""
    
    def __init__(self, processed_files: set):
        """
        初始化 ImportProcessor
        
        Args:
            processed_files: 已处理文件集合（用于防止循环引用）
        """
        self.processed_files = processed_files
        self.import_pattern = IMPORT_PATTERN
        self.source_processor = SourceProcessor()
    
    def process_import_source(
        self,
        import_file: str,
        base_file: Path,
        search_paths: List[Path],
        hooks_dir: Optional[Path]
    ) -> str:
        """处理 #import source 指令（委托给 SourceProcessor）"""
        return self.source_processor.process_import_source(
            import_file, base_file, search_paths, hooks_dir
        )
    
    def is_critical_import(self, import_file: str) -> bool:
        """
        判断是否是关键的 import 文件
        
        关键文件：如果缺失会导致后续处理失败
        非关键文件：如果缺失可以继续处理（如可选的工具文件）
        
        Args:
            import_file: 导入文件名
        
        Returns:
            True 如果是关键文件，False 如果是非关键文件
        """
        # 默认所有文件都是关键的
        critical_patterns = [
            'full.tcl',
            'init.tcl',
            'config.tcl'
        ]
        
        import_lower = import_file.lower()
        for pattern in critical_patterns:
            if pattern in import_lower:
                return True
        
        return True  # 默认都是关键的，确保安全
    
    def process_imports_in_content(
        self,
        content: str,
        base_file: Path,
        search_paths: List[Path],
        hooks_dir: Optional[Path] = None,
        step_name: Optional[str] = None
    ) -> str:
        """
        处理字符串内容中的所有 #import 指令（递归）

        这是"先整合后处理"策略的第二阶段：处理整合后的内容中的所有 #import 指令

        处理范围：
        - 主脚本中的 #import 指令
        - step hooks 中的 #import 指令
        - source 文件内部的 #import 指令（递归处理）

        支持的 #import 指令：
        - #import source <file>: 生成 source 语句
        
        注意：
        - 此阶段不处理 hooks（hooks 已经在整合阶段处理了）
        - 只处理 #import 指令的展开和递归处理

        Args:
            content: 要处理的字符串内容（已经整合了所有 hooks）
            base_file: 基础文件路径（用于解析相对路径）
            search_paths: 搜索路径列表
            hooks_dir: hooks 目录路径（用于查找 hooks，但此阶段不处理 hooks）
            step_name: 步骤名称（用于查找 hooks，但此阶段不处理 hooks）

        Returns:
            处理后的内容（所有 #import 指令已展开）
        """
        lines = content.splitlines(keepends=True)
        result_lines = []
        
        for line in lines:
            # 检查是否是 #import 指令
            match = self.import_pattern.match(line.rstrip())
            
            if match:
                import_file = match.group(1).strip()
                
                try:
                    source_line = self.process_import_source(
                        import_file, base_file, search_paths, hooks_dir
                    )
                    result_lines.append(source_line)
                except (EDPFileNotFoundError, FileNotFoundError) as e:
                    # 文件未找到：记录详细错误信息
                    logger.error(f"处理 #import 指令失败: {line.strip()}")
                    logger.error(f"错误详情: {e}")
                    # 根据文件重要性决定是否继续
                    if self.is_critical_import(import_file):
                        # 关键文件，必须失败
                        raise
                    else:
                        # 非关键文件，记录错误但继续
                        result_lines.append(f"{line.rstrip()}  # 错误: 文件未找到 - {import_file}\n")
                except (ConfigError, ValueError) as e:
                    # 配置错误或验证错误：必须失败
                    logger.error(f"配置错误: {line.strip()} - {e}")
                    raise
                except KeyboardInterrupt:
                    # 用户中断：直接抛出
                    raise
                except Exception as e:
                    # 其他未预期的错误：记录详细信息并抛出框架异常
                    logger.error(f"处理 #import 指令时发生未预期的错误: {line.strip()}", exc_info=True)
                    raise EDPError(
                        f"处理 #import 指令失败: {e}",
                        context={
                            'line': line.strip(),
                            'import_file': import_file,
                            'import_type': import_type
                        },
                        suggestion="请检查文件格式和内容是否正确"
                    )
            else:
                # 普通行，直接保留
                result_lines.append(line)
        
        return ''.join(result_lines)
    
    def process_content(
        self,
        tcl_file: Path,
        search_paths: List[Path],
        hooks_dir: Optional[Path] = None,
        step_name: Optional[str] = None
    ) -> str:
        """
        递归处理文件内容
        
        Args:
            tcl_file: 要处理的文件路径
            search_paths: 搜索路径列表
        
        Returns:
            处理后的内容
        """
        # 防止循环引用
        if tcl_file in self.processed_files:
            logger.warning(f"检测到循环引用，跳过: {tcl_file}")
            return f"# 循环引用已跳过: {tcl_file}\n"
        
        self.processed_files.add(tcl_file)
        
        try:
            content = tcl_file.read_text(encoding='utf-8')
        except Exception as e:
            raise IOError(f"无法读取文件 {tcl_file}: {e}")
        
        lines = content.splitlines(keepends=True)
        result_lines = []
        
        for line in lines:
            # 检查是否是 #import 指令
            match = self.import_pattern.match(line.rstrip())
            
            if match:
                import_file = match.group(1).strip()
                
                try:
                    # 处理 #import source 指令：生成 source 语句
                    source_line = generate_source_statement(
                        import_file, tcl_file, search_paths, recursive=True
                    )
                    result_lines.append(source_line)
                except (EDPFileNotFoundError, FileNotFoundError) as e:
                    # 文件未找到：记录详细错误信息
                    logger.error(f"处理 #import source 指令失败: {line.strip()}")
                    logger.error(f"错误详情: {e}")
                    # 根据文件重要性决定是否继续
                    if self.is_critical_import(import_file):
                        # 关键文件，必须失败
                        raise
                    else:
                        # 非关键文件，记录错误但继续
                        result_lines.append(f"{line.rstrip()}  # 错误: 文件未找到 - {import_file}\n")
                except (ConfigError, ValueError) as e:
                    # 配置错误或验证错误：必须失败
                    logger.error(f"配置错误: {line.strip()} - {e}")
                    raise
                except KeyboardInterrupt:
                    # 用户中断：直接抛出
                    raise
                except Exception as e:
                    # 其他未预期的错误：记录详细信息并抛出框架异常
                    logger.error(f"处理 #import source 指令时发生未预期的错误: {line.strip()}", exc_info=True)
                    raise EDPError(
                        f"处理 #import source 指令失败: {e}",
                        context={
                            'line': line.strip(),
                            'import_file': import_file
                        },
                        suggestion="请检查文件格式和内容是否正确"
                    )
            else:
                # 普通行，直接保留
                result_lines.append(line)
        
        # 移除已处理的文件标记（允许在不同上下文中重新处理）
        self.processed_files.discard(tcl_file)
        
        return ''.join(result_lines)

