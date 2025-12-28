#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EDP 框架统一异常类体系

提供框架特定的异常类，包含错误上下文和解决建议。
"""

from typing import Optional, Dict, Any, List


class EDPError(Exception):
    """
    EDP 框架基础异常类
    
    所有框架特定的异常都应该继承此类。
    提供错误上下文和解决建议，改善用户体验。
    
    Attributes:
        message: 错误消息
        context: 错误上下文信息（字典）
        suggestion: 解决建议（字符串）
    """
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, 
                 suggestion: Optional[str] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            context: 错误上下文信息（可选）
            suggestion: 解决建议（可选）
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion
    
    def __str__(self) -> str:
        """返回格式化的错误信息"""
        parts = [self.message]
        
        # 添加上下文信息
        if self.context:
            context_str = self._format_context(self.context)
            if context_str:
                parts.append(f"\n[详细信息]\n{context_str}")
        
        # 添加解决建议
        if self.suggestion:
            parts.append(f"\n[建议]\n{self.suggestion}")
        
        return "\n".join(parts)
    
    def _format_context(self, context: Dict[str, Any], indent: str = "  ") -> str:
        """格式化上下文信息"""
        lines = []
        for key, value in context.items():
            if value is None:
                continue
            
            # 处理列表（如果太长则截断）
            if isinstance(value, list):
                if len(value) > 5:
                    value_str = f"{value[:5]} ... (共 {len(value)} 项)"
                else:
                    value_str = str(value)
            elif isinstance(value, dict):
                # 字典格式化为多行
                value_str = "\n".join([f"{indent}  {k}: {v}" for k, v in value.items()])
                lines.append(f"{indent}- {key}:")
                lines.append(value_str)
                continue
            else:
                value_str = str(value)
            
            lines.append(f"{indent}- {key}: {value_str}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典（用于日志记录）"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'context': self.context,
            'suggestion': self.suggestion
        }


class ConfigError(EDPError):
    """
    配置相关错误
    
    用于配置加载、解析、验证等配置相关的错误。
    """
    
    def __init__(self, message: str, config_file: Optional[str] = None,
                 config_path: Optional[str] = None, **kwargs):
        """
        初始化配置错误
        
        Args:
            message: 错误消息
            config_file: 配置文件路径（可选）
            config_path: 配置目录路径（可选）
            **kwargs: 其他上下文信息
        """
        context = kwargs.pop('context', {})
        if config_file:
            context['config_file'] = config_file
        if config_path:
            context['config_path'] = config_path
        context.update(kwargs)
        
        suggestion = kwargs.pop('suggestion', None)
        if not suggestion:
            suggestion = (
                "1. 检查配置文件格式是否正确（YAML/Tcl）\n"
                "2. 检查配置文件路径是否正确\n"
                "3. 检查配置文件权限是否可读"
            )
        
        super().__init__(message, context, suggestion)


class FileNotFoundError(EDPError):
    """
    文件未找到错误（框架特定）
    
    注意：为了避免与 Python 内置的 FileNotFoundError 冲突，
    使用时应该使用别名 EDPFileNotFoundError。
    """
    
    def __init__(self, file_path: str, search_paths: Optional[List[str]] = None,
                 current_file: Optional[str] = None, similar_files: Optional[List[str]] = None,
                 **kwargs):
        """
        初始化文件未找到错误
        
        Args:
            file_path: 未找到的文件路径
            search_paths: 搜索路径列表（可选）
            current_file: 当前正在处理的文件（可选）
            similar_files: 相似文件名列表（可选，用于拼写错误检测）
            **kwargs: 其他上下文信息
        """
        message = f"无法找到文件: {file_path}"
        
        context = kwargs.pop('context', {})
        context['file_path'] = file_path
        if current_file:
            context['current_file'] = current_file
        if search_paths:
            context['search_paths'] = search_paths
        if similar_files:
            context['similar_files'] = similar_files
        context.update(kwargs)
        
        suggestion = kwargs.pop('suggestion', None)
        if not suggestion:
            suggestion_parts = [
                "1. 检查文件名是否正确",
                "2. 检查文件是否在搜索路径中"
            ]
            if search_paths:
                suggestion_parts.append(f"3. 搜索路径: {', '.join(search_paths[:3])}")
            if similar_files:
                suggestion_parts.append(f"4. 相似文件: {', '.join(similar_files[:3])}")
            suggestion = "\n".join(suggestion_parts)
        
        super().__init__(message, context, suggestion)


class ProjectNotFoundError(EDPError):
    """项目未找到错误"""
    
    def __init__(self, project_name: str, available_projects: Optional[List[Dict[str, str]]] = None,
                 foundry: Optional[str] = None, node: Optional[str] = None,
                 config_path: Optional[str] = None, **kwargs):
        """
        初始化项目未找到错误
        
        Args:
            project_name: 项目名称
            available_projects: 可用项目列表（可选）
            foundry: 代工厂名称（可选）
            node: 工艺节点（可选）
            config_path: 配置目录路径（可选）
            **kwargs: 其他上下文信息
        """
        message = f"找不到项目: {project_name}"
        if foundry or node:
            message += f" (foundry={foundry}, node={node})"
        
        context = kwargs.pop('context', {})
        context['project_name'] = project_name
        if foundry:
            context['foundry'] = foundry
        if node:
            context['node'] = node
        if config_path:
            context['config_path'] = config_path
        if available_projects:
            # 格式化项目列表
            project_list = [f"{p.get('project', '')} ({p.get('foundry', '')}/{p.get('node', '')})" 
                          for p in available_projects[:10]]
            context['available_projects'] = project_list
        context.update(kwargs)
        
        suggestion = kwargs.pop('suggestion', None)
        if not suggestion:
            suggestion_parts = []
            if available_projects:
                project_names = [p.get('project', '') for p in available_projects[:5]]
                suggestion_parts.append(f"可用项目: {', '.join(project_names)}")
            else:
                suggestion_parts.append("未找到可用项目")
            suggestion_parts.append("使用 'edp -create_project PROJECT_NAME FOUNDRY NODE' 创建新项目")
            suggestion = "\n".join(suggestion_parts)
        
        super().__init__(message, context, suggestion)


class WorkflowError(EDPError):
    """工作流执行错误"""
    
    def __init__(self, message: str, step_name: Optional[str] = None,
                 flow_name: Optional[str] = None, **kwargs):
        """
        初始化工作流错误
        
        Args:
            message: 错误消息
            step_name: 步骤名称（可选）
            flow_name: 流程名称（可选）
            **kwargs: 其他上下文信息
        """
        context = kwargs.pop('context', {})
        if step_name:
            context['step_name'] = step_name
        if flow_name:
            context['flow_name'] = flow_name
        context.update(kwargs)
        
        suggestion = kwargs.pop('suggestion', None)
        if not suggestion:
            suggestion = (
                "1. 检查步骤配置是否正确\n"
                "2. 检查输入文件是否存在\n"
                "3. 查看日志文件获取详细信息"
            )
        
        super().__init__(message, context, suggestion)


class ValidationError(EDPError):
    """验证错误"""
    
    def __init__(self, message: str, field_name: Optional[str] = None,
                 field_value: Optional[Any] = None, expected: Optional[str] = None,
                 **kwargs):
        """
        初始化验证错误
        
        Args:
            message: 错误消息
            field_name: 字段名称（可选）
            field_value: 字段值（可选）
            expected: 期望值或格式（可选）
            **kwargs: 其他上下文信息
        """
        context = kwargs.pop('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = field_value
        if expected:
            context['expected'] = expected
        context.update(kwargs)
        
        suggestion = kwargs.pop('suggestion', None)
        if not suggestion and expected:
            suggestion = f"期望格式: {expected}"
        
        super().__init__(message, context, suggestion)

