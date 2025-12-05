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

## 下一步

- 查看 [常见问题](08_faq.md)
- 参考 [更多资源](07_resources.md)

[← 返回目录](../TUTORIAL.md)

