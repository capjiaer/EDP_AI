# PR 流程文件快速总结

## ✅ PR 流程必需文件（快速参考）

### 核心文件（必需）

1. **时序库文件**（`.lib` 和 `.db`）
   - ✅ 所有与这个 stdcell 相关的 `.lib` 文件（Liberty 文本格式）
   - ✅ 所有与这个 stdcell 相关的 `.db` 文件（Liberty 二进制格式）
   - ✅ 包括压缩的 `.lib_ccs_tn_lvf_dths.gz` 文件（工具可以直接读取）
   - 📍 位置：通常在 `ccs_lvf/` 或 `liberty/` 目录下
   - 📝 说明：`.lib` 和 `.db` 内容相同，只是格式不同（文本 vs 二进制）

2. **物理抽象文件**
   - ✅ **LEF 文件**（`.lef`）- 如果使用 **Innovus**（Cadence）
   - ✅ **NDM 文件**（`.ndm/`）- 如果使用 **ICC2/Fusion Compiler**（Synopsys）
   - 📍 位置：通常在 `lef/` 或 `ndm/` 目录下

### 可选文件（PV 流程用，但实际项目中可能一起处理）

3. **版图文件**（PV 流程用）
   - ⚠️ **GDS 文件**（`.gds`, `.gds2`）- 用于 LVS、DRC
   - ⚠️ **OASIS 文件**（`.oasis`, `.oas`）- 用于 LVS、DRC
   - 📝 说明：严格来说是 PV 流程用的，但实际项目中可能一起处理

4. **网表文件**（PV 流程用）
   - ⚠️ **CDL 文件**（`.cdl`）- 用于 LVS
   - ⚠️ **SPICE 文件**（`.sp`, `.spice`）- 用于 LVS
   - 📝 说明：严格来说是 PV 流程用的，但实际项目中可能一起处理

---

## 📋 文件清单总结

### 对于 Innovus（Cadence）

**必需文件：**
1. ✅ `.lib` 和 `.db` - 时序库（每个 PVT corner 一个）
2. ✅ `.lef` - 物理抽象信息

**可选文件（PV 流程用）：**
3. ⚠️ `.gds`, `.gds2`, `.oasis` - 版图信息
4. ⚠️ `.cdl`, `.sp`, `.spice` - 网表

---

### 对于 ICC2/Fusion Compiler（Synopsys）

**必需文件：**
1. ✅ `.lib` 和 `.db` - 时序库（每个 PVT corner 一个）
2. ✅ `.ndm/` - 物理抽象信息（NDM 数据库）

**可选文件（PV 流程用）：**
3. ⚠️ `.gds`, `.gds2`, `.oasis` - 版图信息
4. ⚠️ `.cdl`, `.sp`, `.spice` - 网表

---

## ⚠️ 重要说明

### `.lib` vs `.db` 文件

**关键理解：**
- ✅ **`.lib`** = Liberty 文本格式（人类可读）
- ✅ **`.db`** = Liberty 二进制格式（工具优化）
- ✅ **两者内容相同**，只是格式不同
- ✅ **工具都可以直接使用**，不需要手动转换
- ✅ **建议：两者都保留**（工具会自动选择）

### LEF vs NDM

**关键理解：**
- ✅ **LEF** = 用于 Innovus（Cadence）
- ✅ **NDM** = 用于 ICC2/Fusion Compiler（Synopsys）
- ✅ **两者都是物理抽象信息**，只是格式不同
- ✅ **根据使用的工具选择**

### GDS/OASIS/CDL 文件

**关键理解：**
- ⚠️ **严格来说**：这些是 PV 流程用的（LVS、DRC）
- ⚠️ **实际项目中**：可能一起处理，不太分家
- ✅ **建议：保留这些文件**（即使严格来说是 PV 流程用的）

---

## ✅ 最终答案

**PR 流程需要的文件：**

1. ✅ **所有与这个 stdcell 相关的 `.lib` 和 `.db`** - 时序库（必需）
2. ✅ **LEF 文件**（`.lef`）- 如果使用 Innovus（必需）
3. ✅ **NDM 文件**（`.ndm/`）- 如果使用 ICC2（必需）
4. ⚠️ **GDS/OASIS/CDL 文件** - PV 流程用，但实际项目中可能一起处理（可选）

**总结：**
> **PR 流程本身只需要：时序库（`.lib`/`.db`）+ 物理抽象（`.lef` 或 `.ndm`）**
> 
> **GDS/OASIS/CDL 虽然严格来说是 PV 流程用的，但实际项目中可能一起处理，所以保留也可以。**

---

## 参考

- **Liberty 文件**：`.lib`（文本格式）和 `.db`（二进制格式），内容相同
- **LEF**：Library Exchange Format，用于 Innovus
- **NDM**：Native Design Model，用于 ICC2/Fusion Compiler
- **GDS/OASIS**：版图信息，PV 流程用
- **CDL/SPICE**：网表，PV 流程用

