# 向后兼容代码移除总结

本文档总结了所有已移除的向后兼容代码。

---

## ✅ 已完成的移除工作

### 1. 参数推断的旧逻辑 ✅

**位置**：`edp_center/main/cli/init/params.py`

**移除内容**：
- 移除了 `infer_params_from_version_file()` 函数中 `manager=None` 时的旧推断逻辑
- `manager` 参数现在是必需的（不再是可选参数）

**影响**：
- ✅ 无影响：所有调用处都已传入 `manager`
- ✅ 代码更简洁：移除了约 30 行向后兼容代码

---

### 2. Debug 模式中的 `util_hooks_procs` ✅

**位置**：
- `edp_center/packages/edp_cmdkit/debug_execution_plan.py`
- `edp_center/packages/edp_cmdkit/debug_mode_handler.py`
- 相关测试文件

**移除内容**：
- 移除了 `parse_main_script_for_execution_plan()` 函数的返回值中的 `util_hooks_procs`
- 函数现在只返回 `execution_plan`

**影响**：
- ✅ 无影响：`util_hooks_procs` 始终为空字典，从未被使用
- ✅ 代码更清晰：移除了无用的返回值

---

### 3. CLI 参数名称兼容 ✅

**位置**：`edp_center/packages/edp_cmdkit/cli.py`

**移除内容**：
- 将 `--dir-list` 参数改为 `--search-paths`（保留 `-d` 短选项）
- 更新了参数目标名称从 `dir_list` 到 `search_paths`

**影响**：
- ⚠️ **破坏性变更**：使用 `--dir-list` 的脚本需要改为 `--search-paths`
- ✅ 代码更清晰：参数名与内部实现一致

---

### 4. Debug Util Processor 模块 ✅

**位置**：`edp_center/packages/edp_cmdkit/debug_util_processor.py`

**移除内容**：
- 将模块标记为已废弃
- 移除了所有实际功能代码
- 保留空文件避免导入错误

**影响**：
- ✅ 无影响：模块已不再被使用
- ✅ 代码更清晰：明确标记为废弃

---

### 5. 目录名称向后兼容 ✅

**位置**：
- `edp_center/main/cli/utils/script_finders.py`
- `edp_center/packages/edp_cmdkit/package_loader.py`
- 相关文档

**移除内容**：
- 移除了所有对 `scripts/` 目录的支持（只支持 `steps/`）
- 移除了所有对 `util/` 目录的支持（只支持 `helpers/`）
- 更新了所有相关文档

**影响**：
- ⚠️ **破坏性变更**：使用旧目录名称的项目需要迁移到新名称
- ✅ 代码更清晰：统一使用新目录名称

**注意**：
- 代码中实际上已经只支持新目录名称了
- 主要是移除了文档中的向后兼容说明

---

## 📊 移除统计

### 代码行数减少
- 参数推断旧逻辑：约 30 行
- Debug util_hooks_procs：约 10 行
- Debug util processor：约 300 行（标记为废弃）
- **总计**：约 340 行代码被移除或标记为废弃

### 文档更新
- 更新了 5+ 个文档文件
- 移除了所有向后兼容说明
- 统一了目录结构说明

---

## 🎯 保留的向后兼容代码

### 1. 异常处理回退 ✅ 保留（防御性编程）

**位置**：多个文件中的 `try/except ImportError`

**原因**：
- 这是良好的防御性编程实践
- 避免因模块问题导致功能失效

**建议**：保留

---

### 2. 函数接口重新导出 ✅ 保留（重构后的标准做法）

**位置**：多个 `__init__.py` 和 `handlers.py` 文件

**原因**：
- 这是重构后的标准做法
- 保持导入路径兼容性

**建议**：保留

---

### 3. Shell 兼容性 ✅ 保留（跨平台支持）

**位置**：
- `command_builder.py` - 使用 `2>&1 |` 而不是 `|&`
- `terminal_executor.py` - 使用 `;` 而不是 `&&`

**原因**：
- 跨 Shell 兼容性（bash、csh、tcsh）
- 这是良好的跨平台实践

**建议**：保留

---

### 4. 配置默认行为 ✅ 保留（合理的默认值）

**位置**：
- `validators.py` - 空列表表示不限制
- Web UI - `flow_ready` 默认值

**原因**：
- 合理的默认行为
- 符合用户期望

**建议**：保留

---

## 📝 总结

### 已移除的向后兼容代码
1. ✅ 参数推断的旧逻辑
2. ✅ Debug 模式中的 `util_hooks_procs`
3. ✅ CLI 参数名称兼容（`dir_list` → `search_paths`）
4. ✅ Debug Util Processor 模块（已废弃）
5. ✅ 目录名称兼容（`scripts/` → `steps/`，`util/` → `helpers/`）

### 保留的向后兼容代码
1. ✅ 异常处理回退（防御性编程）
2. ✅ 函数接口重新导出（重构后的标准做法）
3. ✅ Shell 兼容性（跨平台支持）
4. ✅ 配置默认行为（合理的默认值）

### 影响
- **代码更简洁**：移除了约 340 行向后兼容代码
- **结构更清晰**：统一使用新命名和结构
- **维护更容易**：减少了需要维护的兼容代码

### 破坏性变更
- ⚠️ CLI 参数：`--dir-list` → `--search-paths`
- ⚠️ 目录名称：`scripts/` → `steps/`，`util/` → `helpers/`

**建议**：
- 在版本号中标记为破坏性变更
- 提供迁移指南
- 在发布说明中明确说明

---

**日期**：2024-01-XX
**环境**：try_run 环境（未进入生产环境）

