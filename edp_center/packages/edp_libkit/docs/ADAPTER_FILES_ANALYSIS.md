# Adapter 相关文件分析

## 文件列表

在 `foundry_adapters/` 目录下有以下 adapter 相关文件：

1. **interface.py** - 适配器接口定义
2. **foundry_adapter.py** - Foundry适配器（代理层）
3. **node_adapter.py** - 节点适配器实现
4. **enhanced_base_adapter.py** - 增强适配器（旧实现，已删除）

## 文件关系图

```
当前架构（正在使用）：
┌─────────────────────────────────────────┐
│  base_adapter.py                        │
│  BaseFoundryAdapter (抽象基类)          │
│  - 定义接口                             │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────────────┐
│ adapter.py   │  │ base_node_adapter.py │
│              │  │                      │
│ FoundryAdapter│  │ BaseNodeAdapter      │
│ (主适配器)    │  │ (节点适配器)         │
│              │  │                      │
│ - 统一入口   │  │ - 通用实现            │
│ - 动态加载   │  │ - YAML配置驱动        │
│              │  │ - 所有foundry共享     │
└──────────────┘  └──────────────────────┘

旧架构（未使用）：
┌─────────────────────────────────────────┐
│  enhanced_base_adapter.py              │
│  - Foundry → Node → LibraryType         │
│  - 只在 cli_enhanced.py 中使用         │
│  - 测试文件中使用                        │
└─────────────────────────────────────────┘
```

## 详细说明

### 1. interface.py ✅ **正在使用**

**职责**：定义适配器接口

**内容**：
- `BaseFoundryAdapter` - 抽象基类
- 定义核心方法：
  - `find_view_directories()` - 查找视图目录
  - `extract_lib_info()` - 提取库信息
  - `get_view_file_pattern()` - 获取文件模式（默认实现）

**使用情况**：
- ✅ 被 `foundry_adapter.py` 中的 `FoundryAdapter` 继承
- ✅ 被 `node_adapter.py` 中的 `BaseNodeAdapter` 继承

### 2. foundry_adapter.py ✅ **正在使用**

**职责**：Foundry适配器（代理层）

**内容**：
- `FoundryAdapter` - 统一适配器入口
  - 根据 foundry 和 node 动态加载节点适配器
  - 对于 Samsung/SMIC/TSMC，使用 `BaseNodeAdapter`
  - 对于其他 foundry，尝试从节点目录加载（向后兼容）
- `AdapterFactory` - 适配器工厂
  - `create_adapter()` - 创建适配器实例
  - `get_supported_foundries()` - 获取支持的 foundry 列表
  - `get_supported_nodes()` - 获取支持的节点列表

**使用情况**：
- ✅ 被 `generator.py` 使用
- ✅ 被 `cli.py` 使用
- ✅ 被 `__init__.py` 导出

### 3. node_adapter.py ✅ **正在使用**

**职责**：节点适配器实现

**内容**：
- `BaseNodeAdapter` - 节点适配器实现类
  - 所有 foundry 共享同一个实现
  - 通过 `foundry` 参数区分不同 foundry 的特殊处理
  - 从 YAML 配置文件加载节点配置
  - 实现所有核心方法：
    - `find_view_directories()` - 查找视图目录（STD/IP/MEM）
    - `extract_lib_info()` - 提取库信息
    - `get_standard_view_types()` - 获取视图类型列表
    - `get_view_file_pattern()` - 获取文件模式（支持多个模式）
    - `extract_rc_corner()` - 提取RC corner
    - `_find_all_versions()` - 查找所有版本
    - `_get_latest_version()` - 获取最新版本

**使用情况**：
- ✅ 被 `foundry_adapter.py` 中的 `FoundryAdapter` 动态加载
- ✅ 所有 Samsung/SMIC/TSMC 节点都使用这个实现

### 4. enhanced_base_adapter.py ❌ **未使用（旧实现）**

**职责**：增强适配器（旧架构）

**内容**：
- `BaseFoundryAdapter` - Foundry适配器基类（与 `base_adapter.py` 中的不同）
- `BaseNodeAdapter` - 节点适配器基类（与 `base_node_adapter.py` 中的不同）
- `BaseLibTypeAdapter` - 库类型适配器基类
- `AdapterFactory` - 适配器工厂（与 `adapter.py` 中的不同）
- `LibraryType` - 库类型枚举

**架构**：
- Foundry → Node → LibraryType → Adapter（三层架构）
- 更复杂，但未被实际使用

**使用情况**：
- ❌ 只在 `cli_enhanced.py` 中使用（`cli_enhanced.py` 未被使用）
- ❌ 只在 `tests/test_enhanced_adapters_properties.py` 中使用（测试文件）

## 优化结果

### ✅ 已删除的文件

1. **enhanced_base_adapter.py** ✅ **已删除**
   - **原因**：未被实际使用，只在未使用的 `cli_enhanced.py` 和测试文件中使用
   - **状态**：已删除

2. **cli_enhanced.py** ✅ **已删除**
   - **原因**：未被实际使用，当前使用的是 `cli.py`
   - **状态**：已删除

3. **tests/test_enhanced_adapters_properties.py** ✅ **已删除**
   - **原因**：测试的是未使用的 `enhanced_base_adapter.py`
   - **状态**：已删除

### ✅ 保留的文件（当前架构）

1. **base_adapter.py** ✅
   - 定义接口，必需

2. **adapter.py** ✅
   - 主适配器实现，必需

3. **base_node_adapter.py** ✅
   - 通用节点适配器，必需

## 优化后的文件结构

```
foundry_adapters/
├── __init__.py              # 导出当前使用的适配器
├── interface.py             # 适配器接口定义 ✅
├── foundry_adapter.py       # Foundry适配器（代理层）✅
├── node_adapter.py          # 节点适配器实现 ✅
├── samsung/                 # Samsung 配置文件目录
│   └── *.config.yaml
├── smic/                    # SMIC 配置文件目录
│   └── *.config.yaml
└── tsmc/                    # TSMC 配置文件目录
    └── *.config.yaml
```

## 总结

**当前架构**：
- ✅ 简洁清晰：3个核心文件
- ✅ 统一实现：所有 foundry 共享 `BaseNodeAdapter`
- ✅ 配置驱动：YAML 配置文件

**旧架构**：
- ❌ 复杂：Foundry → Node → LibraryType 三层架构
- ❌ 未使用：只在未使用的文件中引用
- ❌ 冗余：可以安全删除

**建议**：删除 `enhanced_base_adapter.py`、`cli_enhanced.py` 和相关的测试文件，保持代码库简洁。

