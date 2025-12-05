# 错误处理基础设施总结

## 现有基础设施

### 1. 日志配置模块 (`logging_config.py`)

**功能**：
- `setup_logging()`: 统一配置日志系统
- `get_logger()`: 获取 logger 实例

**使用**：
```python
from edp_common import setup_logging, get_logger

# 配置日志（通常在 CLI 入口处调用）
setup_logging(level='INFO', log_file=Path('app.log'))

# 获取 logger
logger = get_logger(__name__)
```

### 2. 日志辅助函数 (`logging_helpers.py`)

**功能**：
- `log_exception()`: 记录 EDPError 异常到日志
- `log_error_with_context()`: 记录带上下文信息的错误

**使用**：
```python
from edp_common import log_exception, EDPError

try:
    do_something()
except EDPError as e:
    log_exception(logger, e)  # 自动记录结构化日志
```

### 3. 异常类体系 (`exceptions.py`)

**功能**：
- `EDPError`: 基础异常类（包含 context 和 suggestion）
- `ConfigError`: 配置错误
- `EDPFileNotFoundError`: 文件未找到
- `ProjectNotFoundError`: 项目未找到
- `WorkflowError`: 工作流错误
- `ValidationError`: 验证错误

**使用**：
```python
from edp_common import EDPFileNotFoundError

raise EDPFileNotFoundError(
    file_path="/path/to/file",
    suggestion="请检查文件路径"
)
```

### 4. 错误处理模块 (`error_handler.py`) ⭐ 新增

**功能**：
- `@handle_error`: 普通函数错误处理装饰器
- `@handle_cli_error`: CLI 命令错误处理装饰器
- `error_context`: 错误处理上下文管理器
- `safe_call`: 安全调用函数

**目的**：基于现有的日志基础设施，提供统一的错误处理模式，减少重复代码。

## 统一错误处理方案

### 方案架构

```
现有基础设施：
├── logging_config.py (日志配置)
├── logging_helpers.py (日志辅助函数)
└── exceptions.py (异常类体系)

新增封装层：
└── error_handler.py (统一错误处理装饰器/上下文管理器)
    └── 基于上述基础设施，提供便捷的错误处理接口
```

### 使用示例

#### 旧代码模式（需要改进）

```python
def handle_load_config(manager, args):
    try:
        config = manager.load_config(...)
        return 0
    except Exception as e:
        print(f"[ERROR] 加载配置失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

#### 新代码模式（使用统一错误处理）

```python
from edp_common import handle_cli_error, ConfigError

@handle_cli_error(error_message="加载配置失败")
def handle_load_config(manager, args):
    config = manager.load_config(...)
    # 如果抛出异常，会自动：
    # 1. 输出友好的错误信息
    # 2. 记录结构化日志（如果配置了日志）
    # 3. 返回退出码 1
    return 0
```

#### 使用 EDPError 提供更好的错误信息

```python
from edp_common import handle_cli_error, ConfigError

@handle_cli_error()
def handle_load_config(manager, args):
    config_file = args.config
    if not Path(config_file).exists():
        raise ConfigError(
            message="配置文件不存在",
            config_file=config_file,
            suggestion="请检查配置文件路径"
        )
    # ...
```

## 优势

1. **减少重复代码**：不需要在每个函数中写 try-except
2. **统一错误格式**：所有错误都使用相同的格式输出
3. **自动日志记录**：错误自动记录到日志（如果配置了）
4. **更好的错误信息**：使用 EDPError 提供上下文和建议
5. **易于维护**：错误处理逻辑集中管理

## 迁移建议

1. **新代码**：直接使用 `@handle_cli_error` 装饰器
2. **旧代码**：逐步迁移，优先迁移高频使用的命令
3. **错误类型**：尽量使用 `EDPError` 子类，提供更好的错误信息

## 总结

`error_handler.py` 是基于现有日志基础设施的**封装层**，不是全新的实现。它提供了：
- 统一的错误处理接口（装饰器/上下文管理器）
- 自动的错误输出和日志记录
- 更好的代码可读性和可维护性

现有的 `logging_config.py`、`logging_helpers.py` 和 `exceptions.py` 继续使用，`error_handler.py` 只是在此基础上提供了更便捷的使用方式。

