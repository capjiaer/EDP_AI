# Milkyway 文件详解

本文档解释 Milkyway 在 IC 设计流程中的作用。

## Milkyway 简介

**Milkyway** 是 **Synopsys 工具**（如 ICC, Astro）使用的**物理设计数据库格式**。

### 基本概念

- **格式**：二进制数据库格式
- **工具**：Synopsys ICC（ICC1）, Astro（已淘汰）
- **用途**：存储标准单元库的物理信息和设计数据
- **状态**：⚠️ **旧版格式**，已被 NDM 格式取代

---

## Milkyway vs NDM

### 历史演进

| 工具版本 | 数据库格式 | 状态 |
|---------|-----------|------|
| **ICC（ICC1）** | Milkyway | ⚠️ **旧版**（已淘汰） |
| **ICC2** | NDM | ✅ **当前标准** |
| **Fusion Compiler** | NDM | ✅ **当前标准** |

### 格式对比

| 特性 | Milkyway | NDM |
|------|----------|-----|
| **工具** | ICC（ICC1）, Astro | ICC2, Fusion Compiler |
| **格式** | 二进制数据库 | 二进制数据库 |
| **状态** | ⚠️ **旧版**（已淘汰） | ✅ **当前标准** |
| **信息组织** | 物理信息为主 | 物理+时序合并 |
| **兼容性** | 仅支持旧版工具 | 支持新版工具 |

---

## Milkyway 的作用

### 1. 在旧版 PR 流程中的作用

**Milkyway 主要用于旧版 Synopsys 工具（ICC, Astro）：**

| 工具 | 使用的文件格式 | Milkyway 的作用 |
|------|---------------|----------------|
| **ICC（ICC1）** | Milkyway | ✅ 主要使用 Milkyway 格式 |
| **Astro** | Milkyway | ✅ 主要使用 Milkyway 格式 |
| **ICC2** | NDM | ❌ 不使用 Milkyway（使用NDM） |
| **Fusion Compiler** | NDM | ❌ 不使用 Milkyway（使用NDM） |

### 2. 存储的信息

**Milkyway 数据库包含：**
- ✅ **物理信息**（版图、pin位置、金属层等）
- ✅ **设计数据**（标准单元库的物理视图）
- ⚠️ **时序信息**（通常需要配合 Liberty 文件）

---

## NDM 到 Milkyway 的转换

### `ndm2mw.tcl` 脚本

**作用：**
- 将 NDM 格式转换为 Milkyway 格式
- 用于兼容旧版工具（ICC, Astro）

**使用场景：**
- 如果需要使用旧版工具（ICC, Astro）
- 需要将 NDM 格式转换为 Milkyway 格式
- 工具内部转换用

**示例：**
```tcl
# 使用 ndm2mw.tcl 脚本将 NDM 转换为 Milkyway
source /path/to/ndm/scripts/ndm2mw.tcl
```

---

## 为什么 Milkyway 被 NDM 取代？

### NDM 的优势

1. ✅ **信息集中**：物理+时序合并在一起
2. ✅ **工具优化**：ICC2 对 NDM 格式有专门优化
3. ✅ **配置简单**：一个文件搞定，不需要读取多个文件
4. ✅ **性能更好**：读取速度更快，工具运行更高效

### Milkyway 的劣势

1. ⚠️ **信息分离**：物理和时序信息分离，需要分别读取
2. ⚠️ **工具限制**：仅支持旧版工具（ICC, Astro）
3. ⚠️ **配置复杂**：需要读取多个文件
4. ⚠️ **性能较差**：读取速度较慢

---

## 实际使用建议

### 对于新项目

**推荐使用 NDM：**
- ✅ ICC2/Fusion Compiler 使用 NDM 格式
- ✅ 配置简单，性能更好
- ✅ 当前标准格式

### 对于旧项目

**如果必须使用 Milkyway：**
- ⚠️ 仅适用于旧版工具（ICC, Astro）
- ⚠️ 可以使用 `ndm2mw.tcl` 脚本转换
- ⚠️ 建议迁移到 NDM 格式

---

## ⚠️ 重要：Milkyway 文件可以忽略

### 对于当前项目

**关键理解：**
- ✅ **Milkyway 文件可以直接忽略**
- ✅ **已经不用老工具了**（ICC, Astro）
- ✅ **当前使用 ICC2/Fusion Compiler**（使用 NDM 格式）

**实际建议：**
- ❌ **不需要处理 Milkyway 文件**
- ❌ **不需要读取 Milkyway 数据库**
- ❌ **不需要使用 `ndm2mw.tcl` 脚本**
- ✅ **只关注 NDM 格式文件**

**文件过滤：**
- ✅ **包含**：NDM 文件（`.ndm/`）
- ❌ **排除**：Milkyway 文件（`.mw/`, `FRAM/`, `CEL/` 等）
- ❌ **排除**：`ndm2mw.tcl` 脚本（不需要转换）

**总结：**
> **Milkyway 文件可以直接不看，因为已经不用老工具了！**
> 
> **当前标准：只使用 NDM 格式（ICC2/Fusion Compiler）**

---

## 文件格式对比

### Milkyway 格式

```
Milkyway 数据库结构：
├── lib/                    # 库目录
│   ├── FRAM/              # Frame 视图（物理信息）
│   ├── CEL/               # Cell 视图（单元信息）
│   └── LM/                # Library Manager 视图
└── tech/                  # 工艺信息
```

### NDM 格式

```
NDM 数据库结构：
├── xx.ndm/                # NDM 数据库目录
│   └── reflib.ndm         # NDM 数据库文件（物理+时序合并）
└── tf/                    # Technology File
```

---

## 关键理解

### Milkyway 的本质

**Milkyway = 旧版物理设计数据库格式**

**关键理解：**
- ✅ **Milkyway 是旧版格式**，用于 ICC（ICC1）和 Astro
- ✅ **已被 NDM 格式取代**，ICC2 和 Fusion Compiler 使用 NDM
- ✅ **功能相同**：都是存储物理设计信息
- ⚠️ **格式不同**：Milkyway 是旧版，NDM 是新版

### 格式演进

```
历史演进：
ICC（ICC1）+ Astro  →  Milkyway（旧版）
         ↓
ICC2 + Fusion Compiler  →  NDM（当前标准）
```

### 实际使用

**当前标准：**
- **ICC2**：使用 NDM（✅ 推荐）
- **Fusion Compiler**：使用 NDM（✅ 推荐）

**旧版工具：**
- **ICC（ICC1）**：使用 Milkyway（⚠️ 已淘汰）
- **Astro**：使用 Milkyway（⚠️ 已淘汰）

---

## 总结

1. **Milkyway** = Synopsys 旧版工具（ICC, Astro）的数据库格式
2. **功能** = 存储标准单元库的物理信息
3. **状态** = ⚠️ **旧版格式**，已被 NDM 格式取代
4. **使用场景** = 仅适用于旧版工具（ICC, Astro）
5. **对于新项目** = ✅ 使用 NDM 格式（ICC2, Fusion Compiler）

**关键理解：**
- Milkyway 是旧版格式，用于 ICC（ICC1）和 Astro
- NDM 是当前标准格式，用于 ICC2 和 Fusion Compiler
- 两者功能相同，只是格式和工具版本不同
- **推荐使用 NDM**（当前标准）

**格式演进：**
- Milkyway（旧版）→ NDM（当前标准）
- ICC（ICC1）→ ICC2
- Astro → Fusion Compiler

