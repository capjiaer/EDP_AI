# generator.py 重构计划

## 📋 重构目标

将 `generator.py` (703行) 拆分为多个模块，提高可维护性和可测试性。

---

## 🔍 当前结构分析

### 文件位置
`edp_center/packages/edp_cmdkit/sub_steps/generator.py` (703行)

### 当前函数列表

1. **`_ensure_global_declarations_in_proc()`** (~193行)
   - 确保 proc 中有基础的 global 声明
   - 自动添加 `global edp project {flow_name}`
   - 移除注释掉的 global 声明行

2. **`generate_step_hook_proc()`** (~49行)
   - 生成 step.pre 或 step.post hook 的 proc 定义
   - 自动封装散装代码为 proc

3. **`generate_sub_step_pre_proc()`** (~51行)
   - 生成 sub_step pre-step proc 定义
   - 自动封装散装代码为 proc

4. **`generate_sub_step_post_proc()`** (~51行)
   - 生成 sub_step post-step proc 定义
   - 自动封装散装代码为 proc

5. **`generate_sub_steps_sources()`** (~257行)
   - 从 dependency.yaml 读取 sub_steps
   - 生成对应的 source 语句
   - 处理 hooks（pre/post/replace）
   - 处理 #import source 指令

6. **`generate_sub_steps_calls()`** (~74行)
   - 从 dependency.yaml 读取 sub_steps
   - 生成对应的 proc 调用代码
   - 处理 pre/post hooks 调用

### 使用情况

**被以下模块使用**：
- `sub_steps/__init__.py` - 导出函数
- `sub_steps/handler.py` - 调用生成函数
- `content_assembler.py` - 调用 `generate_step_hook_proc`

---

## 📦 重构方案

### 方案：拆分为 3 个模块

#### 1. `proc_processor.py` (~250行)
**职责**：Proc 内容处理

**包含函数**：
- `_ensure_global_declarations_in_proc()` - 确保 global 声明
- `generate_step_hook_proc()` - 生成 step hook proc
- `generate_sub_step_pre_proc()` - 生成 sub_step pre proc
- `generate_sub_step_post_proc()` - 生成 sub_step post proc

**理由**：
- 这些函数都处理 proc 定义和内容
- 都涉及 global 声明处理
- 逻辑相关，可以放在一起

#### 2. `hooks_integration.py` (~200行)
**职责**：Hooks 集成和处理

**包含函数**：
- `integrate_sub_step_hooks()` - 集成 sub_step hooks（pre/post/replace）
- `collect_hooks()` - 收集所有 hooks 信息
- `apply_replace_hooks()` - 应用 replace hooks
- `generate_hook_procs()` - 生成 hook procs（调用 proc_processor）

**理由**：
- 专门处理 hooks 的集成逻辑
- 从 `generate_sub_steps_sources()` 中提取 hooks 相关逻辑

#### 3. `generator.py` (~250行)
**职责**：主入口，协调各个模块

**包含函数**：
- `generate_sub_steps_sources()` - 主函数，协调各个模块
- `generate_sub_steps_calls()` - 生成调用代码

**理由**：
- 保持向后兼容（函数名不变）
- 作为主入口，协调其他模块

---

## 🔧 重构步骤

### 步骤 1：创建 `proc_processor.py`

1. 创建新文件 `edp_center/packages/edp_cmdkit/sub_steps/proc_processor.py`
2. 移动以下函数：
   - `_ensure_global_declarations_in_proc()`
   - `generate_step_hook_proc()`
   - `generate_sub_step_pre_proc()`
   - `generate_sub_step_post_proc()`
3. 更新导入（如果需要）

### 步骤 2：创建 `hooks_integration.py`

1. 创建新文件 `edp_center/packages/edp_cmdkit/sub_steps/hooks_integration.py`
2. 从 `generate_sub_steps_sources()` 中提取 hooks 相关逻辑
3. 创建新的辅助函数：
   - `collect_sub_step_hooks()` - 收集所有 hooks
   - `integrate_replace_hooks()` - 集成 replace hooks
   - `generate_hook_procs()` - 生成 hook procs

### 步骤 3：重构 `generator.py`

1. 更新 `generator.py`，移除已迁移的函数
2. 更新 `generate_sub_steps_sources()`，使用新的模块
3. 保持函数签名不变（向后兼容）

### 步骤 4：更新导入

1. 更新 `sub_steps/__init__.py`，导出新模块的函数
2. 更新 `sub_steps/handler.py`，使用新的导入
3. 更新 `content_assembler.py`，使用新的导入

### 步骤 5：测试

1. 运行现有测试，确保功能正常
2. 添加新模块的单元测试
3. 端到端测试，确保生成结果一致

---

## 📝 文件结构

### 重构前
```
sub_steps/
├── generator.py (703行)
├── handler.py
├── hooks.py
├── reader.py
└── __init__.py
```

### 重构后
```
sub_steps/
├── generator.py (~250行) - 主入口
├── proc_processor.py (~250行) - Proc 处理
├── hooks_integration.py (~200行) - Hooks 集成
├── handler.py
├── hooks.py
├── reader.py
└── __init__.py
```

---

## ✅ 重构检查清单

- [ ] 创建 `proc_processor.py`
- [ ] 移动 proc 相关函数
- [ ] 创建 `hooks_integration.py`
- [ ] 提取 hooks 集成逻辑
- [ ] 重构 `generator.py`
- [ ] 更新所有导入
- [ ] 运行现有测试
- [ ] 添加新测试
- [ ] 更新文档

---

## 🎯 预期效果

1. **可维护性提升**：每个模块职责单一，易于理解和修改
2. **可测试性提升**：可以单独测试每个模块
3. **代码复用**：proc 处理逻辑可以在其他地方复用
4. **向后兼容**：保持函数签名不变，不影响现有代码

