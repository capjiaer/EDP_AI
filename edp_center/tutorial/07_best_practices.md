# 最佳实践

[← 返回目录](../TUTORIAL.md)

本文档介绍使用 EDP_AI 框架的最佳实践，帮助你更高效地使用框架。

## 1. 项目组织

- **使用有意义的命名**: 项目名、版本、块名、用户名都应该清晰明确
- **保持目录结构一致**: 遵循标准的目录结构
- **使用分支管理**: 为不同的实验创建不同的分支

## 2. 配置管理

- **优先使用 YAML**: YAML 格式更易读易维护
- **合理使用变量保护**: 对关键变量使用 `protect` 防止误修改
- **使用变量约束**: 对有限选项的变量使用 `constraint`
- **添加变量描述**: 使用 `description` 字段记录变量用途

## 3. 脚本开发

- **使用 #import 指令**: 将通用代码提取为辅助文件
  - `#import source`: 生成 source 语句，适合 proc 定义文件（推荐用于所有 flow）
  - 直接在主脚本中写散装代码：适合简单 flow（如 pv_calibre）
- **利用 hooks**: 使用 hooks 进行调试和扩展
  - `step.pre`/`step.post`: 步骤级别的 hooks（框架自动封装为 proc）
  - 如果需要修改 proc 定义，可以直接在主脚本中使用 `#import source` 加载文件，然后重新定义 proc
  - `sub_step.replace`/`sub_step.pre`/`sub_step.post`: Sub_step 级别的 hooks（框架自动封装为 proc）
- **保持脚本简洁**: 将复杂逻辑拆分为多个步骤
- **使用 Sub_steps**: 将大步骤拆分为可复用的小步骤（sub_steps/ 目录）
- **组织辅助代码**: 将辅助 proc 放在 helpers/ 目录

**注意**：
- 已移除 `#import util` 机制，不再使用 util hooks
- 所有 hooks（step.pre/post, sub_step.pre/post）只需写散装代码，框架会自动封装为 proc
- 框架会自动添加 `global edp project {flow_name}` 声明

## 4. 工作流管理

- **使用依赖关系**: 让框架自动处理步骤依赖
- **记录运行信息**: 查看 `.run_info` 了解执行历史
- **使用演示模式**: 在执行前使用 `--dry-run` 检查命令

## 5. 调试技巧

假设你的分支目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1/main`

- **查看生成的脚本**: 检查 `/home/user/WORK_PATH/dongting/P85/block1/user1/main/cmds/{flow_name}/` 目录下的生成脚本
- **查看 full.tcl**: 检查 `/home/user/WORK_PATH/dongting/P85/block1/user1/main/runs/{flow}.{step}/full.tcl` 了解最终配置
- **查看日志文件**: 检查 `/home/user/WORK_PATH/dongting/P85/block1/user1/main/logs/{flow}.{step}/` 目录下的日志文件
- **使用 hooks 调试**: 在 `/home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/{flow}.{step}/` 中添加调试输出
- **查看 RELEASE**: 检查 `/home/user/WORK_PATH/dongting/P85/RELEASE/{block}/{user}/{version}/` 目录下的发布结果

## 6. 日志系统

EDP 框架提供了统一的日志系统，帮助你更好地追踪和调试问题。

### 日志输出

框架采用**双重输出**机制：
- **用户输出**：友好格式，直接显示给用户（通过 `print()` 输出到 stderr）
- **日志记录**：结构化数据，记录到日志文件（通过 `logging` 模块）

### 日志级别

可以通过环境变量 `EDP_LOG_LEVEL` 控制日志级别：

```bash
# 开发环境：显示所有日志
export EDP_LOG_LEVEL=DEBUG

# 生产环境：只显示重要信息
export EDP_LOG_LEVEL=INFO
# 或
export EDP_LOG_LEVEL=WARNING
```

### 日志格式

日志格式统一为：
```
时间戳 - 模块名 - 级别 - 消息
```

示例：
```
2025-11-14 16:31:41 - edp_center.main.cli.utils.full_tcl_generator - ERROR - 配置验证失败
```

### 错误信息

当遇到错误时，你会看到：
1. **用户输出**：友好的错误信息，包含详细说明和建议
2. **日志记录**：完整的错误信息、堆栈跟踪和结构化上下文

**错误消息格式**：

所有错误消息都遵循统一格式，包含：
- **错误消息**：简要描述问题
- **[详细信息]**：包含错误发生的上下文（文件路径、行号、参数值等）
- **[建议]**：提供具体的解决步骤和示例

**示例**：

```
YAML 文件解析失败: while scanning for the next token

[详细信息]
  - line_number: 5
  - column_number: 10
  - error_type: YAMLError
  - config_file: /path/to/config.yaml

[建议]
请检查 YAML 文件格式是否正确：

错误位置：第 5 行
          第 10 列

常见问题：
1. 缩进错误：
   - YAML 使用空格缩进，不要使用 Tab
   - 确保缩进一致（通常使用 2 个空格）

2. 引号问题：
   - 确保所有引号（单引号 ' 或双引号 "）都已正确闭合
   - 如果字符串包含特殊字符，需要用引号括起来
```

**如何利用错误信息**：

1. **阅读错误消息**：了解问题的基本描述
2. **查看详细信息**：了解错误发生的具体位置和上下文
3. **遵循建议**：按照建议的步骤解决问题
4. **查看日志文件**：如果需要更多信息，查看日志文件获取完整的堆栈跟踪

### 查看日志

- **控制台输出**：日志默认输出到 stderr
- **日志文件**：如果指定了日志文件路径，日志会同时写入文件
- **结构化信息**：日志中包含 `extra` 参数传递的上下文信息（如 flow_name, step_name, search_paths 等），便于问题定位

### 最佳实践

- **开发调试**：使用 `DEBUG` 级别查看所有日志
- **生产环境**：使用 `INFO` 或 `WARNING` 级别，减少日志量
- **问题排查**：查看日志文件中的完整错误信息和堆栈跟踪
- **性能考虑**：日志记录是异步的，一般不影响性能

---

## 7. 代码结构最佳实践

EDP_AI 框架采用模块化设计，遵循统一的代码组织原则，确保代码的可维护性和可扩展性。

### 7.1 模块化设计

框架采用**模块化设计**，将功能拆分为独立的模块：

```
edp_center/
├── main/cli/
│   ├── commands/          # 命令处理模块
│   │   ├── history_handler.py    # 历史查询
│   │   ├── stats_handler.py      # 性能统计
│   │   ├── rollback_handler.py   # 配置回滚
│   │   └── ...
│   └── utils/             # 工具函数模块
│       ├── command_helpers.py    # 命令处理辅助函数
│       ├── unified_inference.py  # 统一推断逻辑
│       └── ...
└── packages/
    ├── edp_common/        # 公共模块
    │   ├── error_handler.py      # 统一错误处理
    │   ├── exceptions.py          # 异常定义
    │   └── ...
    └── ...
```

### 7.2 公共逻辑提取

框架通过**公共逻辑提取**减少代码重复，提高一致性：

#### 项目信息推断

所有命令处理函数使用统一的推断逻辑：

```python
# 使用公共函数（推荐）
from edp_center.main.cli.utils import infer_all_info

project_info, work_path_info, branch_dir = infer_all_info(manager, args)
if not project_info or not work_path_info or not branch_dir:
    return 1
```

**优势**：
- ✅ 代码简洁：从 ~30 行减少到 ~3 行
- ✅ 行为一致：所有命令使用相同的推断逻辑
- ✅ 易于维护：修改推断逻辑只需在一个地方修改

#### 错误处理

框架使用统一的错误处理机制：

```python
from edp_center.packages.edp_common.error_handler import handle_cli_error

@handle_cli_error(error_message="执行命令失败")
def handle_command(manager, args) -> int:
    # 业务逻辑
    # 错误会自动被装饰器捕获和处理
    pass
```

**优势**：
- ✅ 统一格式：所有错误消息格式一致
- ✅ 自动记录：错误自动记录到日志文件
- ✅ 用户友好：提供详细的错误信息和解决建议

### 7.3 代码组织原则

#### 单一职责原则

每个模块和函数只负责一个功能：

- `history_handler.py` - 只处理历史查询
- `stats_handler.py` - 只处理性能统计
- `command_helpers.py` - 只提供命令处理辅助函数

#### DRY 原则（Don't Repeat Yourself）

避免代码重复，提取公共逻辑：

- **推断逻辑**：统一使用 `infer_all_info()` 或 `infer_and_validate_project_info()`
- **路径构建**：统一使用 `build_branch_dir()`
- **错误处理**：统一使用 `@handle_cli_error` 装饰器

#### 关注点分离

将不同关注点分离到不同模块：

- **业务逻辑**：放在 `commands/` 目录下的各个 handler
- **工具函数**：放在 `utils/` 目录下
- **错误处理**：放在 `edp_common/error_handler.py`
- **异常定义**：放在 `edp_common/exceptions.py`

### 7.4 扩展框架

如果你需要扩展框架功能，遵循以下原则：

#### 1. 使用公共函数

优先使用框架提供的公共函数：

```python
# ✅ 推荐：使用公共函数
from edp_center.main.cli.utils import infer_all_info, build_branch_dir

project_info, work_path_info, branch_dir = infer_all_info(manager, args)
```

```python
# ❌ 不推荐：重复实现
current_dir = Path.cwd().resolve()
project_info = infer_project_info(manager, current_dir, args)
if not project_info:
    print(f"[ERROR] ...", file=sys.stderr)
    return 1
# ... 更多重复代码
```

#### 2. 统一错误处理

使用统一的错误处理装饰器：

```python
# ✅ 推荐：使用装饰器
@handle_cli_error(error_message="执行命令失败")
def handle_command(manager, args) -> int:
    # 业务逻辑
    pass
```

```python
# ❌ 不推荐：手动处理错误
def handle_command(manager, args) -> int:
    try:
        # 业务逻辑
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
```

#### 3. 提取公共逻辑

如果发现重复代码，提取为公共函数：

```python
# ✅ 推荐：提取公共函数
def build_branch_dir(work_path_info: Dict) -> Path:
    """构建 branch 目录路径"""
    work_path = Path(work_path_info['work_path']).resolve()
    project = work_path_info['project']
    version = work_path_info['version']
    block = work_path_info['block']
    user = work_path_info['user']
    branch = work_path_info['branch']
    return work_path / project / version / block / user / branch
```

```python
# ❌ 不推荐：在每个函数中重复实现
def handle_command1(manager, args):
    work_path = Path(work_path_info['work_path']).resolve()
    project = work_path_info['project']
    # ... 重复代码

def handle_command2(manager, args):
    work_path = Path(work_path_info['work_path']).resolve()
    project = work_path_info['project']
    # ... 重复代码
```

### 7.5 代码重构

框架持续进行代码重构，提高代码质量：

#### 已完成的重构

1. **参数解析模块化**：将 `arg_parser.py` (800行) 拆分为多个模块
2. **大文件拆分**：将 `generator.py` (703行) 拆分为多个功能模块
3. **公共逻辑提取**：提取命令处理中的重复逻辑到 `command_helpers.py`

#### 重构原则

- **保持向后兼容**：重构不破坏现有功能
- **逐步重构**：分阶段进行，确保每个阶段都可以正常工作
- **测试验证**：重构后进行充分测试

---

## 下一步

- 查看 [常见问题](08_faq.md)
- 参考 [更多资源](09_resources.md)

[← 返回目录](../TUTORIAL.md)

