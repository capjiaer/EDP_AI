# Logic_Synth 文件详解

本文档解释 `logic_synth` 目录下的 Liberty 文件在 IC 设计流程中的作用。

## Logic_Synth 文件简介

**Logic_Synth** 是包含 **NLDM/NLPM 模型**（Non-linear Delay Modeling 和 Non-linear Power Modeling）的 Liberty 文件目录。

### 基本概念

- **格式**：Liberty 格式（`.db`）
- **工具**：综合工具（Design Compiler）、PR 工具（ICC2, Innovus）、STA 工具（PrimeTime, Tempus）
- **用途**：提供基础的时序和功耗信息（NLDM/NLPM 模型）
- **特点**：查找表模型（Lookup table），基础的时序和功耗建模方法

### ⚠️ 重要说明

**根据实际使用情况：**
- ❌ **不使用 Logic_Synth 文件**：实际项目中不使用 `logic_synth` 目录下的文件
- ✅ **使用 CCS_LVF 文件**：实际项目中使用 `ccs_lvf` 目录下的文件
- ✅ **Logic_Synth 可以忽略**：如果只关注实际使用，可以忽略 `logic_synth` 目录

---

## Logic_Synth vs CCS_LVF

### 根据 Foundry 提供的 README

**Logic_Synth：**
> This view contains timing and power characterized data as NLDM (Non-linear Delay Modeling) and NLPM (Non-linear Power Modeling).
> 
> The NLDM/NLPM (NLM) model is based on lookup tables that express the relationship of the characterized values, e.g., cell delay to other parameters such as input slew and output load.

**CCS_LVF：**
> This view contains the CCST/CCSN model along with sigma/OCV tables which model the effect due to process variation.

### 对比分析

| 特性 | Logic_Synth | CCS_LVF |
|------|-------------|---------|
| **模型类型** | NLDM/NLPM（查找表模型） | CCST/CCSN（电流源模型） |
| **时序模型** | NLDM（Non-linear Delay Modeling） | CCST/CCSN（Composite Current Source） |
| **功耗模型** | NLPM（Non-linear Power Modeling） | NLPM（通常） |
| **工艺变化** | ❌ **不包含** OCV 表 | ✅ **包含** sigma/OCV 表 |
| **准确性** | ⚠️ **基础模型** | ✅ **更准确**（考虑工艺变化） |
| **使用场景** | 基础时序和功耗分析 | 高级时序分析（考虑工艺变化） |
| **PR 流程** | ✅ **可以使用** | ✅ **推荐使用** |

**关键理解：**
- **Logic_Synth** = 基础的 NLDM/NLPM 模型（查找表方法）
- **CCS_LVF** = 高级的 CCS 模型 + OCV 表（考虑工艺变化）
- **两者都是 Liberty 文件**，但模型类型不同

---

## Logic_Synth 文件的作用

### 1. 在综合中的作用

**Logic_Synth 文件用于：**
- ✅ **综合**：Design Compiler 等综合工具使用 NLDM 模型
- ✅ **时序分析**：基础的时序分析（不考虑工艺变化）
- ✅ **功耗分析**：基础的功耗分析（NLPM 模型）

### 2. 在 PR 流程中的作用

**Logic_Synth 文件用于：**
- ✅ **PR 流程**：ICC2, Innovus 可以使用 Logic_Synth 文件
- ⚠️ **推荐使用 CCS_LVF**：如果可用，推荐使用 CCS_LVF（更准确）
- ✅ **备选方案**：如果没有 CCS_LVF，可以使用 Logic_Synth

### 3. 在 STA 中的作用

**Logic_Synth 文件用于：**
- ✅ **基础时序分析**：PrimeTime, Tempus 可以使用 Logic_Synth 文件
- ⚠️ **推荐使用 CCS_LVF**：如果进行高级时序分析，推荐使用 CCS_LVF
- ✅ **备选方案**：如果没有 CCS_LVF，可以使用 Logic_Synth

---

## Logic_Synth vs CCS_LVF vs CCS

### 根据 Foundry 提供的 README

| 特性 | Logic_Synth | CCS_LVF | CCS (CCST/CCSN) |
|------|-------------|---------|----------------|
| **模型类型** | NLDM/NLPM（查找表） | CCST/CCSN + OCV | CCST/CCSN（无 OCV） |
| **时序模型** | NLDM（查找表） | CCST/CCSN（电流源） | CCST/CCSN（电流源） |
| **功耗模型** | NLPM（查找表） | NLPM（通常） | NLPM（通常） |
| **工艺变化** | ❌ **不包含** | ✅ **包含** sigma/OCV 表 | ❌ **不包含** |
| **准确性** | ⚠️ **基础** | ✅ **更准确** | ✅ **较准确** |
| **使用场景** | 基础分析 | 高级分析（推荐） | 高级分析（无 OCV） |
| **PR 流程** | ✅ **可以使用** | ✅ **推荐使用** | ✅ **可以使用** |

**关键理解：**
- **Logic_Synth** = 基础的 NLDM/NLPM 模型（查找表方法）
- **CCS (CCST/CCSN)** = 高级的 CCS 模型（电流源方法，无 OCV）
- **CCS_LVF** = 高级的 CCS 模型 + OCV 表（电流源方法，考虑工艺变化）
- **推荐顺序**：CCS_LVF > CCS > Logic_Synth

---

## Logic_Synth 文件的位置

### 目录结构

**Logic_Synth 文件通常在库目录中：**

```
库目录/
├── liberty/                    # Liberty 文件目录
│   ├── logic_synth/           # Logic_Synth 文件目录（NLDM/NLPM 模型）
│   │   ├── sa08nvgllogl22hdp068a_ffpg0p715v125c.db
│   │   ├── sa08nvgllogl22hdp068a_sspg0p585v125c.db
│   │   └── ...
│   ├── ccs_lvf/               # CCS_LVF 文件目录（CCS + OCV，推荐）
│   │   └── ...
│   └── ccs/                   # CCS 文件目录（CCS，无 OCV）
│       └── ...
└── ...
```

---

## ⚠️ 重要：Logic_Synth vs CCS_LVF 对 PR 流程的影响

### 对于库文件整理

**关键理解：**
- ❌ **不使用 Logic_Synth 文件**：实际项目中不使用 `logic_synth` 目录下的文件
- ✅ **使用 CCS_LVF 文件**：实际项目中使用 `ccs_lvf` 目录下的文件
- ✅ **Logic_Synth 可以忽略**：如果只关注实际使用，可以忽略 `logic_synth` 目录

**实际建议：**
- ❌ **PR 流程**：不使用 Logic_Synth 文件
- ✅ **PR 流程**：使用 CCS_LVF 文件
- ❌ **STA 流程**：不使用 Logic_Synth 文件
- ✅ **STA 流程**：使用 CCS_LVF 文件
- ✅ **综合流程**：可以使用 Logic_Synth（NLDM 模型），但实际项目中不使用

**文件过滤：**
- ✅ **包含**：CCS_LVF (.db)（实际使用）
- ❌ **排除**：Logic_Synth (.db)（实际不使用）
- ⚠️ **注意**：Logic_Synth 是基础模型，但实际项目中不使用

**总结：**
> **Logic_Synth 文件实际项目中不使用！**
> 
> **实际项目中使用 CCS_LVF 文件。**
> 
> **如果只关注实际使用，可以忽略 `logic_synth` 目录。**

---

## 实际使用建议

### 对于库文件整理

**关键问题：**
- ❓ **PR 流程需要 Logic_Synth 文件吗？** → ❌ **不使用**（实际项目中不使用）
- ❓ **PR 流程需要 CCS_LVF 文件吗？** → ✅ **使用**（实际项目中使用）
- ❓ **Logic_Synth 和 CCS_LVF 的区别？** → Logic_Synth 是基础模型，CCS_LVF 是高级模型，但实际项目中不使用 Logic_Synth

**实际建议：**
- ❌ **PR 流程**：不使用 Logic_Synth 文件
- ✅ **PR 流程**：使用 CCS_LVF 文件
- ❌ **STA 流程**：不使用 Logic_Synth 文件
- ✅ **STA 流程**：使用 CCS_LVF 文件
- ❌ **综合流程**：不使用 Logic_Synth 文件（实际项目中不使用）

**文件过滤规则：**
- ✅ **PR 流程**：包含 CCS_LVF (.db)（实际使用），排除 Logic_Synth (.db)
- ✅ **STA 流程**：包含 CCS_LVF (.db)（实际使用），排除 Logic_Synth (.db)
- ❌ **综合流程**：排除 Logic_Synth (.db)（实际项目中不使用）

---

## 总结

### Logic_Synth 文件的核心理解

1. **Logic_Synth = NLDM/NLPM 模型**
   - 基础的时序和功耗建模方法
   - 查找表模型（Lookup table）
   - 不包含 OCV 表（不考虑工艺变化）

2. **Logic_Synth 实际项目中不使用**
   - 虽然理论上可以用于 PR 流程，但实际项目中不使用
   - 实际项目中使用 CCS_LVF 文件

3. **Logic_Synth vs CCS_LVF**
   - **Logic_Synth** = 基础模型（NLDM/NLPM，无 OCV）- **实际不使用**
   - **CCS_LVF** = 高级模型（CCS + OCV，考虑工艺变化）- **实际使用**
   - **实际使用**：只使用 CCS_LVF，不使用 Logic_Synth

4. **文件过滤建议**
   - ❌ **PR 流程**：排除 Logic_Synth，使用 CCS_LVF
   - ❌ **STA 流程**：排除 Logic_Synth，使用 CCS_LVF
   - ❌ **综合流程**：排除 Logic_Synth（实际项目中不使用）

### 关键对比

| 文件格式 | 模型类型 | PR 流程需要？ | STA 需要？ | 实际使用 |
|---------|---------|-------------|-----------|---------|
| **CCS_LVF (.db)** | CCS + OCV | ✅ **需要**（实际使用） | ✅ **需要**（实际使用） | ✅ **使用** |
| **CCS (.db)** | CCS（无 OCV） | ✅ **需要** | ✅ **需要** | ✅ **使用** |
| **Logic_Synth (.db)** | NLDM/NLPM | ❌ **不使用** | ❌ **不使用** | ❌ **不使用** |

---

## 参考

- **Logic_Synth**：包含 NLDM/NLPM 模型的 Liberty 文件
- **NLDM**：Non-linear Delay Modeling，非线性延迟建模
- **NLPM**：Non-linear Power Modeling，非线性功耗建模
- **CCS_LVF**：Composite Current Source Low Voltage Functionality，复合电流源低电压功能（含 OCV）
- **CCS**：Composite Current Source Model，复合电流源模型（无 OCV）

