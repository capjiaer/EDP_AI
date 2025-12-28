# Adapter 文件重命名提案

## 当前命名问题

当前三个文件的名字确实容易混淆：

1. `base_adapter.py` - 接口定义
2. `adapter.py` - 代理层
3. `base_node_adapter.py` - 实现层

**问题**：
- ❌ 都有 "adapter" 字样，难以区分
- ❌ "base" 出现在两个文件名中，含义不同
- ❌ `adapter.py` 名字太通用，看不出是代理层

## 重命名方案

### 方案1：按职责命名（推荐）⭐

```
base_adapter.py          →  interface.py
adapter.py               →  foundry_adapter.py
base_node_adapter.py     →  node_adapter.py
```

**优点**：
- ✅ `interface.py`：清晰表示这是接口定义
- ✅ `foundry_adapter.py`：明确表示这是 foundry 适配器（代理层）
- ✅ `node_adapter.py`：明确表示这是节点适配器（实现层）
- ✅ 名字简洁，职责清晰

**缺点**：
- ⚠️ `interface.py` 可能与 Python 的 `interface` 概念混淆（但在这个上下文中很清晰）

### 方案2：更详细的命名

```
base_adapter.py          →  adapter_interface.py
adapter.py               →  foundry_adapter_proxy.py
base_node_adapter.py     →  node_adapter_impl.py
```

**优点**：
- ✅ 非常明确，一看就知道是什么
- ✅ `proxy` 和 `impl` 明确表示设计模式

**缺点**：
- ❌ 名字较长
- ❌ 可能过于详细

### 方案3：保持 base，但更清晰

```
base_adapter.py          →  adapter_base.py
adapter.py               →  foundry_adapter.py
base_node_adapter.py     →  node_adapter.py
```

**优点**：
- ✅ 保留 "base" 但放在后面
- ✅ `foundry_adapter.py` 明确表示代理层

**缺点**：
- ⚠️ `adapter_base.py` 仍然不够清晰

## 推荐方案

### 🏆 推荐：方案1（按职责命名）

```
base_adapter.py          →  interface.py
adapter.py               →  foundry_adapter.py
base_node_adapter.py     →  node_adapter.py
```

**理由**：
1. **简洁明了**：名字短，易读
2. **职责清晰**：一看名字就知道作用
3. **符合惯例**：`interface.py` 常用于定义接口

## 重命名后的文件结构

```
foundry_adapters/
├── __init__.py              # 导出接口
├── interface.py             # 接口定义（原 base_adapter.py）
├── foundry_adapter.py       # Foundry适配器代理（原 adapter.py）
├── node_adapter.py          # 节点适配器实现（原 base_node_adapter.py）
├── samsung/
│   └── *.config.yaml
├── smic/
│   └── *.config.yaml
└── tsmc/
    └── *.config.yaml
```

## 需要修改的地方

1. **文件重命名**
   - `base_adapter.py` → `interface.py`
   - `adapter.py` → `foundry_adapter.py`
   - `base_node_adapter.py` → `node_adapter.py`

2. **导入语句更新**
   - `foundry_adapters/__init__.py`
   - `foundry_adapters/foundry_adapter.py`
   - `foundry_adapters/node_adapter.py`
   - `generator.py`
   - `cli.py`
   - 测试文件

3. **类名保持不变**
   - `BaseFoundryAdapter` 类名不变（在 `interface.py` 中）
   - `FoundryAdapter` 类名不变（在 `foundry_adapter.py` 中）
   - `BaseNodeAdapter` 类名不变（在 `node_adapter.py` 中）

## 重命名后的关系

```
interface.py
    └── BaseFoundryAdapter (接口定义)
    
foundry_adapter.py
    └── FoundryAdapter (代理层)
        └── 导入 interface.py
        └── 导入 node_adapter.py
        
node_adapter.py
    └── BaseNodeAdapter (实现层)
        └── 导入 interface.py
```

## 实施步骤

1. 重命名文件
2. 更新所有导入语句
3. 运行测试确保功能正常
4. 更新文档

