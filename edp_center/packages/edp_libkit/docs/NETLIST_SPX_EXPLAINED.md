# Netlist SPX 文件详解

本文档解释 `netlists/extracted/` 目录下的 `.spx` 文件在 IC 设计流程中的作用。

## SPX 文件简介

**SPX（SPICE Extracted）** 是从版图（GDS）**提取的 SPICE 网表文件**。

### 基本概念

- **格式**：SPICE 网表格式（文本）
- **来源**：从标准单元库的版图（GDS）提取
- **用途**：LVS（Layout Versus Schematic）验证
- **特点**：包含寄生参数（RC）的电路网表

---

## SPX 文件的作用

### 1. LVS 验证

**SPX 文件主要用于 LVS（Layout Versus Schematic）验证：**

| 工具 | 使用的文件格式 | SPX 的作用 |
|------|---------------|-----------|
| **Calibre LVS** | SPX | ✅ 从版图提取的网表，用于 LVS 验证 |
| **Assura LVS** | SPX | ✅ 从版图提取的网表，用于 LVS 验证 |

**LVS 验证流程：**
```
1. 设计网表（Verilog/CDL） → 参考网表
2. 版图（GDS） → 提取网表（SPX） → 提取的网表
3. 比较参考网表和提取的网表 → LVS 验证
```

### 2. 存储的信息

**SPX 文件包含：**
- ✅ **电路连接关系**（从版图提取）
- ✅ **寄生参数**（RC，电阻-电容）
- ✅ **器件信息**（晶体管、电阻、电容等）

---

## Netlist 目录结构

### 典型的 Netlist 目录

```
netlists/
├── extracted/                  # 提取的网表目录
│   ├── lpuff125c/              # PVT corner（如 lpuff125c）
│   │   ├── HDPLVT22_PGATBDRV_ONRBY4_187.spx
│   │   ├── HDPLVT22_CKGTPLT_PY2_32.spx
│   │   ├── HDPLVT22_FSB2DPRBQ_PNRBY2_2.spx
│   │   └── ...                 # 每个标准单元一个 SPX 文件
│   ├── ss125c/                 # 其他 PVT corner
│   └── ...
└── ...
```

### 文件命名规则

**SPX 文件命名：**
```
HDPLVT22_PGATBDRV_ONRBY4_187.spx
│        │              │   │
│        │              │   └─ 版本号或参数
│        │              └─ 单元变体
│        └─ 标准单元名称
└─ 库类型（HDPLVT22 = High Density, Low Vt, 22nm）
```

**示例：**
- `HDPLVT22_PGATBDRV_ONRBY4_187.spx` - PGATBDRV 单元的提取网表
- `HDPLVT22_CKGTPLT_PY2_32.spx` - CKGTPLT 单元的提取网表

---

## SPX vs CDL vs Verilog

### 网表格式对比

| 格式 | 文件类型 | 来源 | 用途 |
|------|---------|------|------|
| **SPX** | `.spx` | 从版图（GDS）提取 | LVS 验证 |
| **CDL** | `.cdl` | 设计网表 | LVS 验证（参考网表） |
| **Verilog** | `.v` | RTL 综合 | 前端设计、综合 |

### 关键区别

**SPX（提取网表）：**
- ✅ **从版图提取**：从 GDS 文件提取的电路网表
- ✅ **包含寄生参数**：包含 RC 寄生参数
- ✅ **用于 LVS**：与设计网表（CDL）比较

**CDL（设计网表）：**
- ✅ **设计生成**：从设计生成的电路网表
- ✅ **不包含寄生参数**：纯电路连接关系
- ✅ **用于 LVS**：作为参考网表

**Verilog（RTL 网表）：**
- ✅ **RTL 综合**：从 RTL 综合生成的网表
- ✅ **门级描述**：门级电路描述
- ✅ **用于综合**：前端设计用

---

## SPX 文件的实际使用

### 在 LVS 验证中

**LVS 验证流程：**

```tcl
# Calibre LVS 使用 SPX 文件
# 1. 读取设计网表（CDL）作为参考
lvs_netlist /path/to/design.cdl

# 2. 读取版图（GDS）
layout /path/to/design.gds

# 3. 使用库的 SPX 文件（从版图提取的网表）
# 工具会自动使用库目录下的 SPX 文件进行 LVS 验证
```

### 在库文件整理中

**SPX 文件的位置：**
- ✅ **库级别**：标准单元库的提取网表
- ✅ **Foundry 提供**：Foundry 从标准单元版图提取的网表
- ✅ **用于 LVS**：LVS 验证时使用

---

## 关键理解

### SPX 文件的本质

**SPX = 从版图提取的 SPICE 网表**

**关键理解：**
- ✅ **从版图提取**：从标准单元库的 GDS 文件提取
- ✅ **包含寄生参数**：包含 RC 寄生参数
- ✅ **用于 LVS**：LVS 验证时与设计网表比较
- ✅ **Foundry 提供**：Foundry 预先提取好的网表

### 使用场景

**LVS 验证：**
- ✅ **使用库的 SPX 文件**：标准单元库的提取网表
- ✅ **与设计网表比较**：验证版图与设计的一致性

**库文件整理：**
- ✅ **SPX 文件在库目录中**：Foundry 提供的标准单元提取网表
- ✅ **用于 LVS 验证**：LVS 工具会自动使用

---

## ⚠️ 重要：SPX 文件可以忽略

### 对于实际项目

**关键理解：**
- ✅ **SPX 文件可以直接忽略**
- ✅ **PV（Physical Verification）流程不使用这些文件**
- ✅ **实际 LVS 验证使用 CDL 文件**，不使用 SPX 文件

**实际建议：**
- ❌ **不需要处理 SPX 文件**
- ❌ **不需要读取 SPX 文件**
- ✅ **PV 流程使用 CDL 文件**（不是 SPX）

**文件过滤：**
- ✅ **包含**：CDL 文件（`.cdl`，用于 LVS）
- ❌ **排除**：SPX 文件（`.spx`，Foundry 提供但实际不使用）

**总结：**
> **SPX 文件可以直接不看，因为 PV 流程不使用这些文件！**
> 
> **实际 LVS 验证：使用 CDL 文件（不是 SPX）**

---

## 总结

1. **SPX 文件** = 从版图（GDS）提取的 SPICE 网表文件
2. **功能** = 包含寄生参数（RC）的电路网表
3. **用途** = LVS（Layout Versus Schematic）验证
4. **来源** = Foundry 从标准单元库版图提取
5. **位置** = `netlists/extracted/` 目录下

**关键理解：**
- SPX 是从版图提取的网表，包含寄生参数
- 用于 LVS 验证，与设计网表（CDL）比较
- Foundry 提供的标准单元库提取网表
- LVS 工具会自动使用库目录下的 SPX 文件

**实际使用建议：**
- ❌ **可以忽略 SPX 文件**：PV 流程不使用
- ✅ **PV 流程使用 CDL 文件**：实际 LVS 验证使用 CDL
- ✅ **库文件整理**：可以排除 SPX 文件

