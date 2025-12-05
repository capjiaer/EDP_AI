# edp_common API 文档

## 📋 概述

`edp_common` 提供框架通用的功能，包括异常类、日志配置、错误处理等。

**位置**: `edp_center.packages.edp_common`

---

## 异常类

### EDPError

EDP 框架基础异常类。

**位置**: `edp_center.packages.edp_common.exceptions.EDPError`

#### `__init__(message, context=None, suggestion=None)`

初始化异常。

**参数**:
- `message` (str): 错误消息
- `context` (Optional[Dict[str, Any]]): 错误上下文信息（可选）
- `suggestion` (Optional[str]): 解决建议（可选）

#### `to_dict()`

将异常转换为字典（用于日志记录）。

**返回**:
- `Dict[str, Any]`: 异常信息字典

---

### ConfigError

配置相关错误。

**位置**: `edp_center.packages.edp_common.exceptions.ConfigError`

#### `__init__(message, config_file=None, config_path=None, **kwargs)`

初始化配置错误。

**参数**:
- `message` (str): 错误消息
- `config_file` (Optional[str]): 配置文件路径（可选）
- `config_path` (Optional[str]): 配置目录路径（可选）
- `**kwargs`: 其他上下文信息

---

### EDPFileNotFoundError

文件未找到错误（框架特定）。

**位置**: `edp_center.packages.edp_common.exceptions.FileNotFoundError`

**导入方式**:
```python
from edp_center.packages.edp_common import EDPFileNotFoundError
```

**注意**: 
- 类定义在 `exceptions.py` 中名为 `FileNotFoundError`
- 从 `edp_common` 导入时使用别名 `EDPFileNotFoundError` 以避免与 Python 内置的 `FileNotFoundError` 冲突
- 推荐始终使用 `EDPFileNotFoundError` 而不是直接导入 `FileNotFoundError`

#### `__init__(file_path, search_paths=None, current_file=None, similar_files=None, **kwargs)`

初始化文件未找到错误。

**参数**:
- `file_path` (str): 未找到的文件路径
- `search_paths` (Optional[List[str]]): 搜索路径列表（可选）
- `current_file` (Optional[str]): 当前正在处理的文件（可选）
- `similar_files` (Optional[List[str]]): 相似文件名列表（可选）
- `**kwargs`: 其他上下文信息

---

### ProjectNotFoundError

项目未找到错误。

**位置**: `edp_center.packages.edp_common.exceptions.ProjectNotFoundError`

### WorkflowError

工作流执行错误。

**位置**: `edp_center.packages.edp_common.exceptions.WorkflowError`

### ValidationError

验证错误。

**位置**: `edp_center.packages.edp_common.exceptions.ValidationError`

---

## 日志配置

### `setup_logging(level=None, log_file=None, format_string=None)`

统一配置 EDP 框架的日志系统。

**位置**: `edp_center.packages.edp_common.logging_config.setup_logging`

**参数**:
- `level` (Optional[str]): 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL），如果为 None，从环境变量 `EDP_LOG_LEVEL` 读取，默认为 INFO
- `log_file` (Optional[Path]): 日志文件路径（可选）
- `format_string` (Optional[str]): 日志格式字符串（可选）

**返回**:
- `logging.Logger`: 配置好的根 logger

### `get_logger(name)`

获取指定名称的 logger。

**位置**: `edp_center.packages.edp_common.logging_config.get_logger`

**参数**:
- `name` (str): logger 名称（通常是 `__name__`）

**返回**:
- `logging.Logger`: Logger 对象

---

## 日志辅助函数

### `log_exception(logger, error, message=None, include_traceback=True)`

记录 EDP 异常到日志。

**位置**: `edp_center.packages.edp_common.logging_helpers.log_exception`

**参数**:
- `logger` (logging.Logger): Logger 对象
- `error` (EDPError): EDP 异常对象
- `message` (Optional[str]): 自定义消息（可选，默认使用 error.message）
- `include_traceback` (bool): 是否包含堆栈跟踪（默认 True）

### `log_error_with_context(logger, message, context=None, suggestion=None, level=logging.ERROR)`

记录带上下文信息的错误日志。

**位置**: `edp_center.packages.edp_common.logging_helpers.log_error_with_context`

**参数**:
- `logger` (logging.Logger): Logger 对象
- `message` (str): 错误消息
- `context` (Optional[dict]): 错误上下文（可选）
- `suggestion` (Optional[str]): 解决建议（可选）
- `level` (int): 日志级别（默认 ERROR）

---

## 错误处理

### `@handle_cli_error(error_message=None, exit_code=1, log_error=True)`

CLI 命令错误处理装饰器。

**位置**: `edp_center.packages.edp_common.error_handler.handle_cli_error`

**参数**:
- `error_message` (Optional[str]): 自定义错误消息（可选）
- `exit_code` (int): 退出码（默认 1）
- `log_error` (bool): 是否记录日志（默认 True）

**示例**:
```python
from edp_center.packages.edp_common import handle_cli_error

@handle_cli_error(error_message="命令执行失败")
def my_command(args):
    # CLI 命令逻辑
    return 0
```

### `@handle_error(error_message=None, exit_code=1, log_error=True, reraise=False, error_type=None)`

普通函数错误处理装饰器。

**位置**: `edp_center.packages.edp_common.error_handler.handle_error`

### `error_context(error_message=None, log_error=True, reraise=False, error_type=None)`

错误处理上下文管理器。

**位置**: `edp_center.packages.edp_common.error_handler.error_context`

### `safe_call(func, *args, error_message=None, default_return=None, log_error=True, **kwargs)`

安全调用函数。

**位置**: `edp_center.packages.edp_common.error_handler.safe_call`

---

## 使用示例

```python
from edp_center.packages.edp_common import (
    EDPError,
    ConfigError,
    EDPFileNotFoundError,
    setup_logging,
    get_logger,
    handle_cli_error
)

# 配置日志
setup_logging(level='INFO', log_file='app.log')
logger = get_logger(__name__)

# 使用异常
raise ConfigError(
    message="配置文件格式错误",
    config_file="/path/to/config.yaml",
    suggestion="请检查配置文件格式"
)

# 使用错误处理装饰器
@handle_cli_error(error_message="处理失败")
def my_command(args):
    # 命令逻辑
    return 0
```

---

## 相关文档

- [统一错误处理指南](../UNIFIED_ERROR_HANDLING.md)
- [架构设计文档](../architecture/architecture_overview.md)

