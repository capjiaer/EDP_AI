# 统一错误处理指南

## 概述

EDP 框架提供了统一的错误处理机制，包括：
- 统一的异常类体系（`edp_common.exceptions`）
- 错误处理装饰器和上下文管理器（`edp_common.error_handler`）
- 日志记录辅助函数（`edp_common.logging_helpers`）

## 异常类体系

### EDPError（基础异常类）

所有框架特定的异常都继承自 `EDPError`，提供：
- **错误消息**：简要描述问题
- **上下文信息**：错误发生的上下文（字典）
- **解决建议**：具体的解决步骤

```python
from edp_common import EDPError

raise EDPError(
    message="配置加载失败",
    context={
        "config_file": "/path/to/config.yaml",
        "line": 10
    },
    suggestion="检查配置文件格式是否正确"
)
```

### 特定异常类

- **ConfigError**: 配置相关错误
- **EDPFileNotFoundError**: 文件未找到错误
- **ProjectNotFoundError**: 项目未找到错误
- **WorkflowError**: 工作流执行错误
- **ValidationError**: 验证错误

## 错误处理装饰器

### @handle_error

用于普通函数的错误处理：

```python
from edp_common import handle_error

@handle_error(error_message="处理文件失败", exit_code=1)
def process_file(file_path: str):
    # 如果这里抛出异常，会被统一处理
    with open(file_path) as f:
        return f.read()
```

### @handle_cli_error

专门用于 CLI 命令函数，自动返回退出码：

```python
from edp_common import handle_cli_error

@handle_cli_error(error_message="命令执行失败")
def handle_my_command(args):
    # CLI 命令逻辑
    # 如果抛出异常，会自动返回退出码 1
    do_something()
    return 0  # 成功返回 0
```

## 错误处理上下文管理器

### error_context

用于代码块的错误处理：

```python
from edp_common import error_context

with error_context(error_message="处理数据失败"):
    # 如果这里抛出异常，会被统一处理
    process_data()
```

## 安全调用函数

### safe_call

捕获异常并返回默认值：

```python
from edp_common import safe_call

# 如果 risky_function 抛出异常，返回 []
result = safe_call(
    risky_function,
    arg1, arg2,
    default_return=[],
    error_message="调用失败"
)
```

## 迁移指南

### 旧代码模式

```python
def my_command(args):
    try:
        do_something()
        return 0
    except Exception as e:
        print(f"[ERROR] 执行失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

### 新代码模式（推荐）

```python
from edp_common import handle_cli_error

@handle_cli_error(error_message="执行失败")
def my_command(args):
    do_something()
    return 0
```

### 使用 EDPError

```python
from edp_common import EDPFileNotFoundError, handle_cli_error

@handle_cli_error()
def my_command(args):
    file_path = args.file
    if not Path(file_path).exists():
        raise EDPFileNotFoundError(
            file_path=file_path,
            suggestion="请检查文件路径是否正确"
        )
    # ...
```

## 最佳实践

1. **使用 EDPError 子类**：对于框架特定的错误，使用 `EDPError` 的子类
2. **提供上下文**：在异常中包含足够的上下文信息
3. **提供建议**：给出具体的解决步骤
4. **使用装饰器**：对于 CLI 命令，使用 `@handle_cli_error`
5. **记录日志**：错误会自动记录到日志（如果配置了日志）

## 示例

### CLI 命令示例

```python
from edp_common import handle_cli_error, EDPFileNotFoundError

@handle_cli_error(error_message="加载配置失败")
def handle_load_config(manager, args):
    config_file = args.config
    if not Path(config_file).exists():
        raise EDPFileNotFoundError(
            file_path=config_file,
            suggestion="请检查配置文件路径是否正确"
        )
    
    config = load_config(config_file)
    print(f"配置已加载: {config}")
    return 0
```

### 普通函数示例

```python
from edp_common import handle_error, ConfigError

@handle_error(error_message="处理配置失败")
def process_config(config_path: str):
    if not Path(config_path).exists():
        raise ConfigError(
            message="配置文件不存在",
            config_file=config_path,
            suggestion="请检查配置文件路径"
        )
    
    # 处理配置...
    return config
```

### 上下文管理器示例

```python
from edp_common import error_context, WorkflowError

def execute_workflow(workflow_name: str):
    with error_context(error_message="执行工作流失败"):
        if not workflow_exists(workflow_name):
            raise WorkflowError(
                message="工作流不存在",
                flow_name=workflow_name,
                suggestion="请检查工作流名称是否正确"
            )
        
        # 执行工作流...
```

