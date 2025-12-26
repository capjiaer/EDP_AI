# PR 流程必需文件总结

本文档总结 PR（Place & Route）流程需要的文件。

## ⚠️ 核心理解：PR vs PV

**PR（Place & Route）流程本身只需要：**
- ✅ **时序库**（`.db`）- 每个 PVT corner 一个
- ✅ **物理抽象**（`.lef` 或 `.ndm`）

**PR 流程不需要：**
- ❌ **GDS/OAS 文件** - 这些是 **PV 流程用的**（LVS、DRC）
- ❌ **CDL/SPICE 文件** - 这些是 **PV 流程用的**（LVS）

**关键理解：**
- **PR 流程** = 布局布线（Place & Route）
- **PV 流程** = 物理验证（Physical Verification，LVS、DRC 等）
- **两者是不同的流程**，需要的文件也不同

---

## PR 流程必需文件（完整列表）

### 根据使用的工具分类

#### 情况1：使用 Innovus（Cadence）

**PR 流程必需文件：**
1. ✅ **LEF 文件**（`.lef`）- **物理抽象信息**（必需）
2. ✅ **Liberty 文件**（`.db`）- **时序信息**（必需，每个 PVT corner 一个）

**PR 流程不需要的文件：**
- ❌ NDM 文件（Innovus 不使用）
- ❌ Verilog 文件（PR 流程不需要）
- ❌ GDS 文件（PV 流程用的）
- ❌ OAS 文件（PV 流程用的）

---

#### 情况2：使用 ICC2/Fusion Compiler（Synopsys）

**PR 流程必需文件：**
1. ✅ **NDM 文件**（`.ndm/`）- **物理抽象信息**（必需）
   - `ndm/xx_frame_only.ndm/` 或
   - `ndm_mixed/xx_frame_only.ndm/`
2. ✅ **Liberty 文件**（`.db`）- **时序信息**（必需，每个 PVT corner 一个）

**PR 流程不需要的文件：**
- ❌ LEF 文件（ICC2 不使用）
- ❌ Verilog 文件（PR 流程不需要）
- ❌ GDS 文件（PV 流程用的）
- ❌ OAS 文件（PV 流程用的）

**⚠️ 注意：TF 文件应该在 PDK 级别提供，不在库级别处理！**

---

### PV 流程需要的文件（与 PR 流程分开）

**PV（Physical Verification）流程需要的文件：**
1. ✅ **GDS 文件**（`.gds`, `.gds2`）- **版图信息**（用于 LVS、DRC）
2. ✅ **OAS 文件**（`.oasis`, `.oas`）- **版图信息**（用于 LVS、DRC）
3. ✅ **CDL/SPICE 文件**（`.cdl`, `.sp`, `.spice`）- **网表**（用于 LVS）

**关键理解：**
- **GDS/OAS** = PV 流程用的（LVS、DRC 等）
- **不是 PR 流程需要的**

---

## PR 流程完整文件列表

### 最小必需文件集（PR 流程本身）

**对于 ICC2：**
1. ✅ `ndm/xx_frame_only.ndm/` 或 `ndm_mixed/xx_frame_only.ndm/` - 物理抽象信息
2. ✅ `ccs_lvf/xx_*.db` - 时序信息（每个 PVT corner 一个）

**对于 Innovus：**
1. ✅ `lef/xx.lef` - 物理抽象信息
2. ✅ `ccs_lvf/xx_*.db` - 时序信息（每个 PVT corner 一个）

**总计：** 1个物理抽象文件 + N个时序文件（N = PVT corner数量）

### ⚠️ 注意：GDS/OAS 不是 PR 流程需要的

**GDS/OAS 文件属于 PV 流程：**
- ❌ `gds/xx.gds` - **PV 流程用的**（LVS、DRC）
- ❌ `gds/xx.oasis` - **PV 流程用的**（LVS、DRC）
- ❌ `cdl/xx.cdl` - **PV 流程用的**（LVS）

**关键理解：**
- **PR 流程** = 布局布线，只需要物理抽象（LEF/NDM）+ 时序（Liberty）
- **PV 流程** = 物理验证，需要版图（GDS/OAS）+ 网表（CDL/SPICE）

---

## 总结

### 核心理解

**PR 流程需要的文件（严格来说）：**

1. **物理抽象信息**（必需）：
   - Innovus：LEF 文件（`.lef`）
   - ICC2：NDM 文件（`.ndm/`）

2. **时序信息**（必需）：
   - Liberty 文件（`.db`）- 每个 PVT corner 一个

**总计：** 1个物理抽象文件 + N个时序文件（N = PVT corner数量）

**PR 流程不需要的文件：**
- ❌ GDS 文件（`.gds`, `.gds2`, `.oasis`）- **PV 流程用的**
- ❌ CDL/SPICE 文件（`.cdl`, `.sp`, `.spice`）- **PV 流程用的**
- ❌ Verilog 文件（`.v`）- **综合用的**

---

## 最终答案

### PR 流程必需文件（严格来说）

**PR 流程本身只需要：**
1. ✅ **时序库**（`.db`）- 每个 PVT corner 一个
2. ✅ **物理抽象**：
   - Innovus：LEF 文件（`.lef`）
   - ICC2：NDM 文件（`.ndm/`）

**总计：** 1个物理抽象文件 + N个时序文件（N = PVT corner数量）

**PR 流程不需要：**
- ❌ GDS/OAS 文件（PV 流程用的）
- ❌ CDL/SPICE 文件（PV 流程用的）
- ❌ Verilog 文件（综合用的）

---

## 参考

- **LEF**：Library Exchange Format，库交换格式（物理抽象信息）
- **NDM**：Native Design Model，原生设计模型（物理抽象信息，ICC2）
- **Liberty**：Liberty 格式（时序信息）
- **GDS**：GDSII 格式（版图信息，PV 流程用）
- **OASIS**：Open Artwork System Interchange Standard（版图信息，PV 流程用）
- **PR**：Place & Route（布局布线）
- **PV**：Physical Verification（物理验证，LVS、DRC 等）
