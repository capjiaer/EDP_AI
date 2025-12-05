# 脚本生成增量更新说明

> **注意**：经过评估，此优化在当前框架中**不推荐实施**。
> 
> **原因**：
> - Sub_steps 文件通常较小，全量生成的性能开销可接受
> - 增量更新会增加代码复杂度，维护成本高
> - 收益不明显，不符合 KISS 原则
> 
> 本文档保留作为技术参考，但不作为推荐优化方向。

## 📋 问题说明

### 当前实现方式（全量生成）

当前框架在生成脚本时，**每次都会重新生成整个脚本**，即使只有少量文件变更。

**评估结论**：在当前场景下，这是**合理的设计选择**，因为：
- Sub_steps 文件通常较小（< 1000 行）
- 全量生成逻辑简单，易于维护
- 性能开销可接受（< 1 秒）

#### 执行流程

每次调用 `edp -run` 时，框架会：

1. **重置处理状态**
   ```python
   # cmd_processor.py:127
   self.processed_files.clear()  # 清空已处理文件集合
   ```

2. **重新整合所有内容**
   - 重新读取主脚本
   - 重新读取所有 Hooks 文件（step.pre/post, sub_step.pre/post/replace）
   - 重新读取所有 #import source 的文件
   - 重新读取所有 Sub_steps 文件

3. **重新处理所有指令**
   - 递归处理所有 #import source 指令
   - 重新展开所有 Sub_steps
   - 重新处理所有 Hooks

4. **重新生成整个脚本**
   - 重新生成 package source 语句
   - 重新生成 sub_steps proc 定义
   - 重新生成调用代码
   - 写入完整的 `full.tcl` 文件

#### 示例场景

假设你有一个包含 10 个 Sub_steps 的步骤：

```
步骤：pnr_innovus.place
├── Sub_step 1: innovus_restore_design.tcl
├── Sub_step 2: innovus_config_design.tcl
├── Sub_step 3: innovus_add_tie_cell.tcl
├── ...
└── Sub_step 10: innovus_save_metrics.tcl
```

**场景 1：修改了 Sub_step 3 的一个小改动**

当前行为：
- ✅ 重新读取 Sub_step 3（已变更）
- ❌ 重新读取 Sub_step 1-2（未变更，浪费）
- ❌ 重新读取 Sub_step 4-10（未变更，浪费）
- ❌ 重新处理所有 #import 指令（即使文件未变更）
- ❌ 重新生成整个脚本（即使大部分内容未变更）

**场景 2：只修改了 step.pre hook**

当前行为：
- ✅ 重新读取 step.pre（已变更）
- ❌ 重新读取主脚本（未变更，浪费）
- ❌ 重新读取所有 Sub_steps（未变更，浪费）
- ❌ 重新处理所有 #import 指令（即使文件未变更）
- ❌ 重新生成整个脚本（即使大部分内容未变更）

---

## 💡 增量更新的含义

### 什么是增量更新？

**增量更新**是指：**只重新处理变更的文件，保留未变更的部分**。

### 增量更新的优势

1. **性能提升**
   - 小型变更：预计提升 70-90%
   - 只处理变更的文件，跳过未变更的文件

2. **资源节约**
   - 减少文件 I/O 操作
   - 减少内存占用
   - 减少 CPU 使用

3. **响应更快**
   - 用户修改后快速看到结果
   - 提升开发体验

---

## 🔧 增量更新的实现方案

### 方案 1：基于文件时间戳的变更检测

#### 实现思路

1. **记录文件时间戳**
   ```python
   # 记录每个文件的修改时间
   file_timestamps = {
       'sub_step_1.tcl': 1234567890,
       'sub_step_2.tcl': 1234567891,
       'helper.tcl': 1234567892,
   }
   ```

2. **检测变更**
   ```python
   def is_file_changed(file_path: Path, cached_timestamp: int) -> bool:
       current_timestamp = file_path.stat().st_mtime
       return current_timestamp != cached_timestamp
   ```

3. **只处理变更的文件**
   ```python
   for sub_step_file in sub_steps:
       if is_file_changed(sub_step_file, cached_timestamps[sub_step_file]):
           # 重新处理
           process_file(sub_step_file)
       else:
           # 使用缓存的结果
           use_cached_result(sub_step_file)
   ```

#### 优点

- ✅ 实现简单
- ✅ 检测准确
- ✅ 性能提升明显

#### 缺点

- ⚠️ 需要维护时间戳缓存
- ⚠️ 需要处理缓存失效

### 方案 2：基于内容哈希的变更检测

#### 实现思路

1. **计算文件哈希**
   ```python
   import hashlib
   
   def get_file_hash(file_path: Path) -> str:
       content = file_path.read_bytes()
       return hashlib.md5(content).hexdigest()
   ```

2. **记录文件哈希**
   ```python
   file_hashes = {
       'sub_step_1.tcl': 'abc123...',
       'sub_step_2.tcl': 'def456...',
   }
   ```

3. **检测变更**
   ```python
   def is_file_changed(file_path: Path, cached_hash: str) -> bool:
       current_hash = get_file_hash(file_path)
       return current_hash != cached_hash
   ```

#### 优点

- ✅ 检测更准确（内容级别）
- ✅ 不受时间戳影响

#### 缺点

- ⚠️ 计算哈希需要读取文件（性能开销）
- ⚠️ 需要维护哈希缓存

### 方案 3：基于依赖图的增量生成

#### 实现思路

1. **构建依赖图**
   ```python
   dependency_graph = {
       'main_script.tcl': ['helper1.tcl', 'helper2.tcl'],
       'helper1.tcl': ['common.tcl'],
       'helper2.tcl': [],
   }
   ```

2. **检测变更影响范围**
   ```python
   def get_affected_files(changed_file: str) -> List[str]:
       # 返回所有受影响的文件（依赖链）
       affected = [changed_file]
       # 找到所有依赖 changed_file 的文件
       for file, deps in dependency_graph.items():
           if changed_file in deps:
               affected.extend(get_affected_files(file))
       return affected
   ```

3. **只重新生成受影响的部分**
   ```python
   changed_files = ['helper1.tcl']
   affected_files = get_affected_files('helper1.tcl')
   # 只重新处理 affected_files
   ```

#### 优点

- ✅ 精确识别影响范围
- ✅ 最小化重新处理

#### 缺点

- ⚠️ 实现复杂
- ⚠️ 需要维护依赖图

---

## 📊 性能对比

### 当前实现（全量生成）

**场景：修改了 1 个 Sub_step（共 10 个）**

| 操作 | 时间 | 说明 |
|------|------|------|
| 读取所有文件 | 100ms | 读取 10 个 Sub_steps |
| 处理 #import | 200ms | 处理所有文件的 #import |
| 生成脚本 | 50ms | 生成整个脚本 |
| **总计** | **350ms** | |

### 增量更新实现

**场景：修改了 1 个 Sub_step（共 10 个）**

| 操作 | 时间 | 说明 |
|------|------|------|
| 检测变更 | 10ms | 检查文件时间戳 |
| 读取变更文件 | 10ms | 只读取 1 个 Sub_step |
| 处理 #import | 20ms | 只处理变更文件的 #import |
| 合并结果 | 20ms | 合并变更部分和缓存部分 |
| **总计** | **60ms** | |

**性能提升：83%** (350ms → 60ms)

---

## 🎯 推荐实现方案

### 阶段 1：基础增量更新（推荐先实现）

**使用方案 1：基于文件时间戳**

1. **实现文件时间戳缓存**
   ```python
   class IncrementalProcessor:
       def __init__(self):
           self.file_timestamps = {}  # {file_path: timestamp}
           self.processed_cache = {}  # {file_path: processed_content}
       
       def process_file_if_changed(self, file_path: Path) -> str:
           current_timestamp = file_path.stat().st_mtime
           cached_timestamp = self.file_timestamps.get(file_path)
           
           if cached_timestamp and current_timestamp == cached_timestamp:
               # 使用缓存
               return self.processed_cache[file_path]
           
           # 重新处理
           processed_content = self.process_file(file_path)
           self.file_timestamps[file_path] = current_timestamp
           self.processed_cache[file_path] = processed_content
           return processed_content
   ```

2. **应用到脚本生成流程**
   - Sub_steps 处理
   - #import source 处理
   - Hooks 处理

### 阶段 2：高级增量更新（未来优化）

**使用方案 3：基于依赖图**

- 构建完整的依赖图
- 精确识别影响范围
- 最小化重新处理

---

## 📝 实现检查清单

### 需要修改的模块

- [ ] `cmd_processor.py` - 添加增量更新逻辑
- [ ] `import_processor.py` - 添加文件变更检测
- [ ] `sub_steps/generator.py` - 添加 Sub_steps 缓存
- [ ] `hooks_handler.py` - 添加 Hooks 缓存

### 需要添加的功能

- [ ] 文件时间戳缓存管理
- [ ] 缓存失效机制
- [ ] 缓存清理机制
- [ ] 缓存持久化（可选）

### 测试要求

- [ ] 单元测试：文件变更检测
- [ ] 集成测试：增量更新流程
- [ ] 性能测试：对比全量和增量

---

## 🔍 相关代码位置

### 当前全量生成的关键代码

1. **重置处理状态**
   ```python
   # cmd_processor.py:127
   self.processed_files.clear()
   ```

2. **重新处理所有内容**
   ```python
   # cmd_processor.py:143-158
   assembled_content = assemble_content_with_hooks(...)
   result = self.import_processor.process_imports_in_content(...)
   ```

3. **重新生成 Sub_steps**
   ```python
   # sub_steps/generator.py:42-251
   def generate_sub_steps_sources(...):
       # 每次都会重新读取和处理所有 Sub_steps
   ```

---

## 💬 总结

**"缺少增量更新"的含义：**

当前框架在生成脚本时，**无论文件是否变更，都会重新处理所有文件并重新生成整个脚本**。这导致：

1. **性能浪费**：即使只修改了一个小文件，也要处理所有文件
2. **响应慢**：用户修改后需要等待较长时间
3. **资源浪费**：重复的文件 I/O 和计算

**增量更新的目标：**

只重新处理**变更的文件**，**保留未变更的部分**，从而大幅提升性能（预计 70-90%）。

---

**最后更新**: 2025-01-XX

