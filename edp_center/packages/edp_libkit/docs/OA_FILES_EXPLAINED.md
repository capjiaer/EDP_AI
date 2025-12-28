# OA 文件详解

本文档解释 OA（OpenAccess）文件在 IC 设计流程中的作用。

## OA 文件简介

**OA（OpenAccess）** 是 **EDA 工具**使用的**数据库格式**，用于存储**原理图（Schematic）**和**符号（Symbol）**信息。

### 基本概念

- **格式**：OpenAccess 数据库格式（二进制）
- **工具**：Cadence Virtuoso, Synopsys Custom Compiler 等
- **用途**：存储标准单元库的**原理图**和**符号**信息
- **特点**：EDA 工具内部使用的数据库格式

---

## OA 文件的作用

### 1. 在 IC 设计流程中的作用

**OA 文件主要用于**：

| 工具 | 使用的文件格式 | OA 的作用 |
|------|---------------|-----------|
| **Cadence Virtuoso** | OA | ✅ 存储原理图和符号 |
| **Synopsys Custom Compiler** | OA | ✅ 存储原理图和符号 |
| **Schematic Editor** | OA | ✅ 编辑和查看原理图 |

**关键理解：**
- **OA** = EDA 工具内部使用的数据库格式
- **用途**：存储**原理图**和**符号**信息
- **使用场景**：**前端设计**（Schematic Design），不是 PR 流程

### 2. OA 文件包含的信息

**OA 数据库包含：**

1. **原理图信息（Schematic）**：
   - `schematic/sch.oa` - 原理图数据
   - `schematic/master.tag` - 原理图主标签
   - 标准单元的电路连接关系
   - 器件（transistor）的连接关系

2. **符号信息（Symbol）**：
   - `symbol/symbol.oa` - 符号数据
   - `symbol/master.tag` - 符号主标签
   - 标准单元的符号表示（用于 Schematic Editor）

3. **技术信息（Technology）**：
   - `tech.db` - 技术数据库
   - 工艺参数、器件模型等

4. **数据管理（Data Management）**：
   - `data.dm` - 数据管理文件
   - 版本控制、元数据等

---

## OA 文件结构

### 目录结构示例

```
schematics/oa/
├── sa08nvgllogl22hdp068a/          # 库名称目录
│   ├── tech.db                     # 技术数据库
│   ├── HDPLVT22_FSB2DPRBQ_PNRBY2_2/  # 标准单元名称
│   │   ├── data.dm                 # 数据管理文件
│   │   ├── schematic/              # 原理图目录
│   │   │   ├── sch.oa              # 原理图数据
│   │   │   └── master.tag          # 原理图主标签
│   │   └── symbol/                 # 符号目录
│   │       ├── symbol.oa           # 符号数据
│   │       └── master.tag          # 符号主标签
│   ├── HDPLVT22_FSB2DPSBQ_PNRBY2_2/
│   │   └── ...
│   └── ...
```

### 文件类型说明

| 文件类型 | 文件名 | 用途 |
|---------|--------|------|
| **技术数据库** | `tech.db` | 工艺技术信息 |
| **数据管理** | `data.dm` | 版本控制、元数据 |
| **原理图** | `schematic/sch.oa` | 标准单元的电路连接关系 |
| **原理图标签** | `schematic/master.tag` | 原理图主标签 |
| **符号** | `symbol/symbol.oa` | 标准单元的符号表示 |
| **符号标签** | `symbol/master.tag` | 符号主标签 |

---

## OA vs 其他格式

### OA vs GDS/LEF

| 特性 | OA（OpenAccess） | GDS/LEF |
|------|----------------|---------|
| **格式** | 二进制数据库 | 文本/二进制格式 |
| **工具** | Cadence Virtuoso, Custom Compiler | PR 工具（ICC2, Innovus） |
| **用途** | **前端设计**（原理图、符号） | **后端设计**（版图、PR） |
| **包含信息** | 电路连接关系、符号 | 物理版图信息 |
| **使用阶段** | **前端**（Schematic Design） | **后端**（Place & Route） |

**关键理解：**
- **OA** = **前端设计**用的数据库（原理图、符号）
- **GDS/LEF** = **后端设计**用的格式（版图、PR）
- **两者用途不同**，OA 用于前端，GDS/LEF 用于后端

### OA vs Verilog

| 特性 | OA（OpenAccess） | Verilog |
|------|----------------|---------|
| **格式** | 二进制数据库 | 文本格式 |
| **工具** | Schematic Editor | Synthesis Tool |
| **用途** | **原理图设计** | **RTL 综合** |
| **包含信息** | 电路连接关系（图形化） | 电路连接关系（文本描述） |
| **使用阶段** | **前端**（Schematic Design） | **前端**（RTL Synthesis） |

**关键理解：**
- **OA** = **图形化**的原理图设计（Schematic Editor）
- **Verilog** = **文本化**的电路描述（RTL Synthesis）
- **两者功能相似**（都描述电路），但**格式不同**

---

## OA 文件的使用场景

### 1. 前端设计（Schematic Design）

**OA 文件用于：**
- ✅ **原理图编辑**：使用 Schematic Editor 编辑标准单元的原理图
- ✅ **符号编辑**：编辑标准单元的符号表示
- ✅ **电路验证**：检查电路连接关系
- ✅ **前端仿真**：使用原理图进行仿真

### 2. 标准单元库开发

**OA 文件用于：**
- ✅ **库开发**：开发标准单元库时，需要 OA 文件
- ✅ **库验证**：验证标准单元的原理图是否正确
- ✅ **库文档**：提供标准单元的符号和原理图信息

---

## ⚠️ 重要：OA 文件对 PR 流程的影响

### 对于库文件整理

**关键理解：**
- ✅ **OA 文件是前端设计用的**：用于 Schematic Editor，不是 PR 流程
- ✅ **PR 流程不需要 OA 文件**：PR 流程使用 GDS/LEF，不使用 OA
- ✅ **可以忽略 OA 文件**：如果只关注 PR 流程，可以忽略 OA 文件

**实际建议：**
- ❌ **PR 流程不需要**：OA 文件不用于 PR 流程
- ✅ **前端设计需要**：如果使用 Schematic Editor，需要 OA 文件
- ✅ **库开发需要**：开发标准单元库时，需要 OA 文件

**文件过滤：**
- ✅ **包含**：GDS, LEF, NDM（PR 流程需要）
- ❌ **排除**：`schematics/` 目录下的所有文件（PR 流程不需要）
- ❌ **排除**：OA 文件（PR 流程不需要）

**总结：**
> **`schematics` 目录下的所有文件都是前端设计用的，PR 流程不需要！**
> 
> **如果只关注 PR 流程，可以忽略整个 `schematics` 目录。**

---

## OA 文件的位置

### 目录结构

**OA 文件通常在库目录中：**

```
库目录/
├── schematics/              # 原理图目录
│   └── oa/                 # OpenAccess 数据库目录
│       └── sa08nvgllogl22hdp068a/  # 库名称
│           ├── tech.db     # 技术数据库
│           ├── cell1/      # 标准单元1
│           │   ├── data.dm
│           │   ├── schematic/
│           │   │   ├── sch.oa
│           │   │   └── master.tag
│           │   └── symbol/
│           │       ├── symbol.oa
│           │       └── master.tag
│           └── cell2/      # 标准单元2
│               └── ...
```

---

## 实际使用建议

### 对于库文件整理

**关键问题：**
- ❓ **PR 流程需要 OA 文件吗？** → ❌ **不需要**
- ❓ **前端设计需要 OA 文件吗？** → ✅ **需要**（如果使用 Schematic Editor）
- ❓ **库开发需要 OA 文件吗？** → ✅ **需要**

**实际建议：**
- ✅ **PR 流程**：可以忽略 OA 文件
- ✅ **前端设计**：如果需要 Schematic Editor，需要 OA 文件
- ✅ **库开发**：开发标准单元库时，需要 OA 文件

**文件过滤规则：**
- ✅ **PR 流程**：排除 OA 文件（`.oa`, `schematics/oa/`）
- ✅ **前端设计**：包含 OA 文件（`.oa`, `schematics/oa/`）
- ✅ **库开发**：包含 OA 文件（`.oa`, `schematics/oa/`）

---

## 总结

### OA 文件的核心理解

1. **OA = OpenAccess 数据库格式**
   - EDA 工具内部使用的数据库格式
   - 存储原理图和符号信息

2. **OA 用于前端设计**
   - Schematic Editor（原理图编辑）
   - Symbol Editor（符号编辑）
   - 不是 PR 流程用的

3. **PR 流程不需要 OA 文件**
   - PR 流程使用 GDS/LEF/NDM
   - OA 文件是前端设计用的

4. **文件过滤建议**
   - ✅ **PR 流程**：排除 OA 文件
   - ✅ **前端设计**：包含 OA 文件
   - ✅ **库开发**：包含 OA 文件

### 关键对比

| 文件格式 | 用途 | PR 流程需要？ |
|---------|------|-------------|
| **GDS** | 版图信息 | ✅ **需要** |
| **LEF** | 抽象版图 | ✅ **需要** |
| **NDM** | 物理+时序 | ✅ **需要** |
| **OA** | 原理图+符号 | ❌ **不需要**（前端设计用） |

---

## 参考

- **OpenAccess**：EDA 工具的标准数据库格式
- **Schematic Design**：前端设计阶段（原理图设计）
- **Place & Route**：后端设计阶段（版图设计）

