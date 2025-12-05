# 配置合并优化说明

## 📋 什么是配置合并？

在 EDP_AI 框架中，配置合并是指将多个层级的配置文件（YAML/Tcl）合并成一个统一的配置，最终生成 `full.tcl` 文件。

### 配置加载顺序（优先级从低到高）

1. `common/main/init_project.yaml` - 通用项目初始化配置
2. `common/main/config.yaml` - 通用主配置
3. `common/{flow_name}/config.yaml` - 通用流程配置
4. `{project}/main/init_project.yaml` - 项目特定初始化配置
5. `{project}/main/config.yaml` - 项目特定主配置
6. `{project}/{flow_name}/config.yaml` - 项目特定流程配置
7. `user_config.yaml` 或 `user_config.tcl` - 用户配置（最高优先级）

**后加载的配置会覆盖先加载的配置。**

---

## 🔍 当前实现的问题

### 1. 每次都要重新解析所有配置文件

**当前流程**：
```python
# 在 full_tcl_generator.py 中
for config_file in config_files:
    # 每次都要：
    # 1. 读取文件内容
    # 2. 解析 YAML/Tcl
    # 3. 转换为 Tcl 变量
    # 4. 验证变量格式
    process_yaml_file(config_file_path, shared_interp)
```

**问题**：
- 即使配置文件没有变化，每次执行都要重新解析
- 在大型项目中，可能有 5-10 个配置文件
- 每个文件都要读取、解析、验证，耗时较长

### 2. 重复的配置验证

**当前流程**：
```python
# 对每个文件都要验证
validate_file_variables_are_arrays(temp_interp, abs_path)

# 最后还要整体验证一次
validate_all_variables_are_arrays(shared_interp)
```

**问题**：
- 每个文件都要单独验证
- 最后还要整体验证一次
- 可能存在重复的验证逻辑

### 3. 没有缓存机制

**当前问题**：
- 没有缓存已解析的配置
- 即使文件内容完全相同，也要重新解析
- 在频繁执行的工作流中，浪费大量时间

---

## ⚠️ 重要约束：变量引用继承

### 配置文件之间的依赖关系

**关键特性**：后面的配置文件可以引用前面配置文件定义的变量！

**示例**：
```yaml
# config1.yaml (第一个文件)
pv_calibre:
  ipmerge:
    base_path: "/work/data"

# config2.yaml (第二个文件，可以引用 config1.yaml 的变量)
pv_calibre:
  ipmerge:
    output_path: "$pv_calibre(ipmerge,base_path)/output"  # ✅ 引用前面的变量
```

**当前实现**：
- 每个文件处理完后，立即调用 `expand_variable_references()` 展开变量引用
- 后面的文件可以引用前面文件已定义的变量
- 变量引用使用 Tcl 的 `subst` 机制展开

**影响**：
- ❌ **不能简单地缓存单个文件的解析结果**
- ✅ **需要缓存整个配置链的解析结果**
- ✅ **或者缓存单个文件，但确保变量引用展开正确**

---

## 💡 优化方案

### 方案 1：配置链缓存（推荐）

**核心思想**：缓存整个配置链的解析结果，基于所有文件的修改时间戳失效。

**实现方式**：
```python
# 伪代码示例
_config_chain_cache = {}  # {(file_list_tuple, mtime_tuple): merged_config}

def get_cached_config_chain(config_files):
    # 计算所有文件的修改时间戳
    file_list = tuple(sorted(config_files))
    mtime_tuple = tuple(f.stat().st_mtime for f in file_list)
    
    # 检查缓存
    cache_key = (file_list, mtime_tuple)
    if cache_key in _config_chain_cache:
        return _config_chain_cache[cache_key]  # 缓存命中
    
    # 缓存未命中，按顺序解析所有文件
    merged_config = parse_config_chain(config_files)
    _config_chain_cache[cache_key] = merged_config
    return merged_config
```

**优势**：
- ✅ 正确处理变量引用继承
- ✅ 文件未修改时，直接使用缓存
- ✅ 任何文件修改后，整个链自动失效
- ✅ 性能提升明显（特别是重复执行时）

**缺点**：
- 需要所有文件都未修改才能使用缓存
- 部分文件修改时，需要重新解析整个链

### 方案 1b：单文件缓存 + 增量合并（复杂但更高效）

**核心思想**：缓存单个文件的解析结果，但增量合并时正确处理变量引用。

**实现方式**：
```python
# 伪代码示例
_file_cache = {}  # {(file_path, mtime): parsed_config}
_chain_cache = {}  # {(file_list_tuple, mtime_tuple): merged_config}

def get_cached_config_chain_incremental(config_files):
    file_list = tuple(sorted(config_files))
    mtime_tuple = tuple(f.stat().st_mtime for f in file_list)
    
    # 检查整个链的缓存
    cache_key = (file_list, mtime_tuple)
    if cache_key in _chain_cache:
        return _chain_cache[cache_key]
    
    # 检查哪些文件已缓存
    changed_files = []
    cached_configs = {}
    
    for config_file in config_files:
        mtime = config_file.stat().st_mtime
        file_cache_key = (config_file, mtime)
        
        if file_cache_key in _file_cache:
            cached_configs[config_file] = _file_cache[file_cache_key]
        else:
            changed_files.append(config_file)
    
    # 如果有文件变更，需要重新解析整个链（因为变量引用）
    if changed_files:
        merged_config = parse_config_chain(config_files)
        # 更新单文件缓存
        for config_file in config_files:
            mtime = config_file.stat().st_mtime
            _file_cache[(config_file, mtime)] = get_file_config(config_file, merged_config)
    else:
        # 所有文件都未修改，使用缓存的链
        merged_config = _chain_cache.get(cache_key)
        if merged_config is None:
            # 重新合并缓存的单文件配置（确保变量引用正确）
            merged_config = merge_cached_configs(cached_configs, config_files)
    
    _chain_cache[cache_key] = merged_config
    return merged_config
```

**优势**：
- ✅ 正确处理变量引用继承
- ✅ 单文件缓存可以用于其他场景
- ✅ 所有文件未修改时，性能最优

**缺点**：
- 实现复杂
- 部分文件修改时，仍需要重新解析整个链（因为变量引用）

### 方案 2：增量合并（受限于变量引用）

**⚠️ 注意**：由于变量引用的存在，增量合并的实现更复杂。

**问题**：
- 如果前面的文件修改了，后面的文件可能引用了前面的变量
- 如果后面的文件修改了，它可能引用了前面的变量
- **不能简单地只处理变更的文件**

**可行的增量合并方式**：
```python
# 伪代码示例
def merge_configs_incremental(config_files, last_merge_time):
    # 找到第一个变更的文件位置
    first_changed_idx = None
    for i, config_file in enumerate(config_files):
        if config_file.stat().st_mtime > last_merge_time:
            first_changed_idx = i
            break
    
    if first_changed_idx is None:
        # 没有文件变更，使用缓存
        return load_cached_merged_config()
    
    # 从第一个变更的文件开始，重新解析后续所有文件
    # （因为后面的文件可能引用了前面的变量）
    merged_config = load_cached_config_up_to(first_changed_idx - 1)
    
    # 重新处理从第一个变更文件开始的所有文件
    for config_file in config_files[first_changed_idx:]:
        merged_config.update(parse_config_file(config_file))
        expand_variable_references(merged_config)  # 展开变量引用
    
    return merged_config
```

**优势**：
- 可以跳过未变更的前置文件
- 只处理从第一个变更文件开始的部分

**缺点**：
- 实现复杂
- 如果第一个文件变更，仍需要重新解析所有文件

### 方案 3：优化验证逻辑

**核心思想**：减少重复验证，优化验证流程。

**实现方式**：
```python
# 伪代码示例
def validate_configs_optimized(config_files, parsed_configs):
    # 一次性验证所有配置，而不是逐个验证
    all_variables = {}
    for parsed_config in parsed_configs:
        all_variables.update(parsed_config)
    
    # 只验证一次
    validate_all_variables_are_arrays(all_variables)
```

**优势**：
- 减少验证次数
- 提高验证效率

---

## 📊 性能提升预期

### 场景 1：首次执行（无缓存）

**当前**：
- 读取 7 个配置文件：~50ms
- 解析 YAML：~100ms
- 验证变量：~50ms
- **总计**：~200ms

**优化后**：
- 读取 7 个配置文件：~50ms
- 解析 YAML：~100ms
- 验证变量：~30ms（优化验证逻辑）
- **总计**：~180ms
- **提升**：~10%

### 场景 2：重复执行（配置文件未修改）

**当前**：
- 每次都要重新解析：~200ms

**优化后**：
- 使用缓存：~5ms（只读取缓存）
- **提升**：~97.5%（40倍提升）

### 场景 3：部分文件修改

**当前**：
- 重新解析所有文件：~200ms

**优化后**：
- 只解析修改的文件：~50ms（假设 2 个文件修改）
- **提升**：~75%

---

## 🎯 实施建议

### 阶段 1：配置解析缓存（简单，效果明显）

1. **实现文件缓存**
   - 基于文件路径和修改时间戳
   - 自动失效机制

2. **预期效果**
   - 重复执行：提升 90%+
   - 实现难度：低
   - 风险：低

### 阶段 2：增量合并（复杂，效果更好）

1. **实现增量合并**
   - 跟踪文件修改时间
   - 只处理变更的文件

2. **预期效果**
   - 部分修改：提升 70%+
   - 实现难度：中
   - 风险：中

### 阶段 3：优化验证逻辑（简单，效果中等）

1. **优化验证流程**
   - 减少重复验证
   - 批量验证

2. **预期效果**
   - 验证时间：提升 30-50%
   - 实现难度：低
   - 风险：低

---

## 📝 代码示例

### 当前实现（无缓存）

```python
# full_tcl_generator.py
def generate_full_tcl(...):
    config_files = build_config_file_paths(...)
    shared_interp = Tcl()
    
    for config_file in config_files:
        # 每次都重新解析
        temp_interp = process_yaml_file(config_file_path, shared_interp)
        validate_file_variables_are_arrays(temp_interp, abs_path)
        
        # 展开变量引用（后面的文件可以引用前面的变量）
        expand_variable_references(shared_interp)
```

### 优化后实现（配置链缓存）

```python
# config_cache.py
_config_chain_cache = {}
_cache_timestamps = {}

def get_cached_config_chain(config_files):
    """获取缓存的配置链，如果所有文件未修改则使用缓存"""
    # 计算所有文件的修改时间戳
    file_list = tuple(sorted(config_files))
    mtime_tuple = tuple(f.stat().st_mtime for f in file_list)
    
    # 检查缓存
    cache_key = (file_list, mtime_tuple)
    if cache_key in _config_chain_cache:
        return _config_chain_cache[cache_key]  # 缓存命中
    
    # 缓存未命中，按顺序解析所有文件
    shared_interp = Tcl()
    for config_file in config_files:
        temp_interp = process_yaml_file(config_file_path, shared_interp)
        validate_file_variables_are_arrays(temp_interp, abs_path)
        expand_variable_references(shared_interp)  # 展开变量引用
    
    # 缓存整个链的结果
    _config_chain_cache[cache_key] = shared_interp
    return shared_interp

# full_tcl_generator.py
def generate_full_tcl(...):
    config_files = build_config_file_paths(...)
    
    # 使用配置链缓存
    shared_interp = get_cached_config_chain(config_files)
    # ... 使用缓存的配置链
```

---

## ✅ 总结

**配置合并优化**主要是通过**缓存机制**来减少重复的配置文件解析和验证工作，从而提升性能。

**重要约束**：
- ⚠️ **配置文件支持变量引用继承**（后面的文件可以引用前面的变量）
- ⚠️ **必须缓存整个配置链**，不能简单地缓存单个文件
- ⚠️ **任何文件修改时，整个链都需要重新解析**（因为变量引用）

**核心优势**：
- ✅ 重复执行时性能提升明显（90%+）
- ✅ 所有文件未修改时，直接使用缓存
- ✅ 实现相对简单，风险低
- ✅ 对用户透明，不影响现有功能
- ✅ 正确处理变量引用继承

**适用场景**：
- 频繁执行相同的工作流
- 大型项目（多个配置文件）
- 配置文件很少修改的情况

**实施建议**：
- 优先实现**配置链缓存**（方案 1）
- 这是最简单且最安全的方案
- 正确处理变量引用继承
- 性能提升明显

