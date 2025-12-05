# 向后兼容代码移除日志

本文档记录逐步移除向后兼容代码的过程。

---

## 已移除的向后兼容代码

### 1. 参数推断的旧逻辑 ✅ 已移除

**位置**：`edp_center/main/cli/init/params.py`

**移除内容**：
- 移除了 `infer_params_from_version_file()` 函数中 `manager=None` 时的旧推断逻辑
- `manager` 参数现在是必需的（不再是可选参数）

**原因**：
- 所有调用处都已传入 `manager` 参数
- 统一推断模块已稳定，不再需要旧逻辑作为回退

**影响**：
- ✅ 无影响：所有调用处都已传入 `manager`
- ✅ 代码更简洁：移除了约 30 行向后兼容代码

**日期**：2024-01-XX

---

### 2. Debug 模式中的 util_hooks_procs ✅ 已移除

**位置**：
- `edp_center/packages/edp_cmdkit/debug_execution_plan.py`
- `edp_center/packages/edp_cmdkit/debug_mode_handler.py`
- `edp_center/packages/edp_cmdkit/tests/test_debug_execution_plan.py`
- `edp_center/packages/edp_cmdkit/tests/test_debug_mode_handler.py`

**移除内容**：
- 移除了 `parse_main_script_for_execution_plan()` 函数的返回值中的 `util_hooks_procs`
- 函数现在只返回 `execution_plan`，不再返回 `(execution_plan, util_hooks_procs)`
- 更新了所有调用处和测试

**原因**：
- `util_hooks_procs` 仅用于向后兼容旧的 util 代码块
- 已移除 `#import util` 机制，不再需要此返回值
- 保留接口兼容性已无意义

**影响**：
- ✅ 无影响：`util_hooks_procs` 始终为空字典，从未被使用
- ✅ 代码更清晰：移除了无用的返回值

**日期**：2024-01-XX

---

### 3. CLI 参数名称兼容 ✅ 已移除

**位置**：`edp_center/packages/edp_cmdkit/cli.py`

**移除内容**：
- 将 `--dir-list` 参数改为 `--search-paths`（保留 `-d` 短选项）
- 更新了参数目标名称从 `dir_list` 到 `search_paths`

**原因**：
- 统一参数命名，与 `process_file()` 方法的参数名一致
- 移除混淆，避免新旧参数名混用

**影响**：
- ⚠️ **破坏性变更**：使用 `--dir-list` 的脚本需要改为 `--search-paths`
- ✅ 代码更清晰：参数名与内部实现一致

**日期**：2024-01-XX

---

### 4. Debug Util Processor 模块 ✅ 已废弃

**位置**：`edp_center/packages/edp_cmdkit/debug_util_processor.py`

**移除内容**：
- 将模块标记为已废弃
- 移除了所有实际功能代码
- 保留空文件避免导入错误

**原因**：
- 已移除 `#import util` 机制
- 不再需要处理 util 代码块

**影响**：
- ✅ 无影响：模块已不再被使用
- ✅ 代码更清晰：明确标记为废弃

**日期**：2024-01-XX

---

## 待移除的向后兼容代码

### 1. 目录名称向后兼容 ⚠️ 保留（高优先级）

**位置**：
- `edp_center/main/cli/utils/script_finders.py` - `scripts/` → `steps/`
- `edp_center/packages/edp_cmdkit/package_loader.py` - `util/` → `helpers/`

**状态**：⚠️ **保留**（影响太大）

**原因**：
- 大量现有项目仍使用旧目录结构
- 移除会导致现有项目无法运行

**建议**：
- 保留此兼容性，但明确标记为废弃
- 在文档中提供迁移指南
- 在未来大版本中计划移除

---

### 2. Debug 模式中的 util 代码块处理 ⚠️ 待评估

**位置**：`edp_center/packages/edp_cmdkit/debug_util_processor.py`

**状态**：⚠️ **待评估**

**原因**：
- 已移除 `#import util` 机制
- 但旧脚本可能仍包含 util 代码块

**建议**：
- 评估是否仍有旧脚本使用 util 代码块
- 如果确认不再需要，可以移除
- 如果移除，需要添加明确的错误提示

---

### 3. 参数名称向后兼容 ⚠️ 待移除

**位置**：
- `edp_center/packages/edp_cmdkit/cmd_processor.py` - `dir_list` → `search_paths`
- `edp_center/packages/edp_cmdkit/cli.py` - `-I` → `-d`

**状态**：⚠️ **待移除**

**建议**：
- 移除 `dir_list` 参数兼容，添加明确的错误提示
- 移除 `-I` 参数兼容，添加明确的错误提示
- 提供迁移指南

---

### 4. 函数接口重新导出 ⚠️ 保留（低优先级）

**位置**：多个 `__init__.py` 和 `handlers.py` 文件

**状态**：⚠️ **保留**（重构后的标准做法）

**原因**：
- 这是重构后的标准做法
- 保持导入路径兼容性

**建议**：
- 保留，这是良好的实践

---

### 5. 异常处理回退 ⚠️ 保留（防御性编程）

**位置**：多个文件中的 `try/except ImportError`

**状态**：⚠️ **保留**（防御性编程）

**原因**：
- 这是良好的防御性编程实践
- 避免因模块问题导致功能失效

**建议**：
- 保留，这是良好的实践

---

## 移除计划

### 第一阶段（已完成）✅
1. ✅ 移除参数推断的旧逻辑
2. ✅ 移除 debug 模式中的 `util_hooks_procs`

### 第二阶段（已完成）✅
1. ✅ 移除 CLI 参数名称兼容（`--dir-list` → `--search-paths`）
2. ✅ 废弃 `debug_util_processor.py` 模块

### 第三阶段（已完成）✅
1. ✅ 移除目录名称兼容（`scripts/` → `steps/`，`util/` → `helpers/`）

**移除内容**：
- 移除了所有对 `scripts/` 目录的支持
- 移除了所有对 `util/` 目录的支持
- 更新了文档，移除了向后兼容说明

**影响**：
- ⚠️ **破坏性变更**：使用旧目录名称的项目需要迁移到新名称
- ✅ 代码更清晰：统一使用新目录名称

**日期**：2024-01-XX

---

### 第四阶段（待执行）⚠️
1. ⚠️ 评估并完全移除 `debug_util_processor.py`（如果确认不再需要）

### 第三阶段（未来大版本）📅
1. 📅 移除目录名称兼容（`scripts/`, `util/`）
2. 📅 提供完整的迁移指南

---

## 注意事项

1. **测试覆盖**：移除向后兼容代码前，确保有足够的测试覆盖
2. **文档更新**：移除后更新相关文档
3. **用户通知**：如果移除影响用户，提前通知并提供迁移指南
4. **版本标记**：在版本号中标记为破坏性变更

