# VHDL、DFT 和文档文件详解

本文档解释 VHDL、DFT（Design For Test）和文档文件在 IC 设计流程中的作用。

## 文件类型总结

### 1. VHDL 文件（`.vhd`）

**VHDL（VHSIC Hardware Description Language）** 是硬件描述语言，类似于 Verilog。

**用途：**
- ✅ **前端设计**：RTL 设计和描述
- ✅ **功能仿真**：VHDL 仿真器使用
- ✅ **综合**：VHDL 综合工具使用（某些工具支持 VHDL）

**PR 流程需要？**
- ❌ **不需要**：PR 流程使用 Verilog 或门级网表，不需要 VHDL

**文件过滤：**
- ❌ **PR 流程**：排除 VHDL 文件（`.vhd`, `.vhdl`）
- ❌ **综合流程**：通常使用 Verilog，不需要 VHDL（除非工具支持）

---

### 2. DFT/ATPG 文件（`.atpg`）

**DFT（Design For Test）** 和 **ATPG（Automatic Test Pattern Generation）** 文件用于芯片测试。

**用途：**
- ✅ **测试向量生成**：ATPG 工具（如 TetraMAX）使用
- ✅ **扫描链测试**：用于扫描链（scan chain）测试
- ✅ **芯片测试**：生成测试向量用于芯片测试

**PR 流程需要？**
- ❌ **不需要**：PR 流程不涉及测试向量生成

**文件过滤：**
- ❌ **PR 流程**：排除 DFT/ATPG 文件（`.atpg`）
- ❌ **综合流程**：排除 DFT/ATPG 文件
- ✅ **测试流程**：需要 DFT/ATPG 文件（如果进行测试）

**相关目录：**
- `dft/` - DFT 相关文件目录
- `dft/fastscan/` - FastScan ATPG 工具相关文件

---

### 3. 文档文件

**文档文件包括：**
- `README_*` - 说明文档
- `release.txt` - 发布说明
- `details_of_changes.txt` - 变更详情
- `DOWNLOAD_ME_FIRST_FOR_INSTALL_STEPS.TXT` - 安装步骤说明
- `*.html` - HTML 文档

**用途：**
- ✅ **文档说明**：解释库的使用方法、版本信息、变更记录等
- ✅ **安装指导**：提供安装和使用说明

**PR 流程需要？**
- ❌ **不需要**：PR 流程不需要文档文件

**文件过滤：**
- ❌ **PR 流程**：排除文档文件（`.txt`, `.md`, `.html`, `.pdf`）
- ❌ **综合流程**：排除文档文件
- ✅ **人工阅读**：需要文档文件（了解库的使用方法）

---

## 文件过滤规则总结

### PR 流程不需要的文件

| 文件类型 | 扩展名 | 用途 | PR 流程需要？ |
|---------|--------|------|-------------|
| **VHDL** | `.vhd`, `.vhdl` | 硬件描述语言（前端设计） | ❌ **不需要** |
| **DFT/ATPG** | `.atpg` | 测试向量生成（芯片测试） | ❌ **不需要** |
| **文档** | `.txt`, `.md`, `.html`, `.pdf` | 文档说明 | ❌ **不需要** |

### 相关目录

| 目录名 | 用途 | PR 流程需要？ |
|--------|------|-------------|
| **`vhdl/`** | VHDL 文件目录 | ❌ **不需要** |
| **`dft/`** | DFT/ATPG 文件目录 | ❌ **不需要** |
| **`documentation/`**, **`docs/`** | 文档目录 | ❌ **不需要** |

---

## 总结

### 核心理解

1. **VHDL 文件** = 硬件描述语言（类似于 Verilog）
   - 用途：前端设计、功能仿真
   - PR 流程：**不需要**

2. **DFT/ATPG 文件** = 测试相关文件
   - 用途：测试向量生成、芯片测试
   - PR 流程：**不需要**

3. **文档文件** = 说明文档
   - 用途：文档说明、安装指导
   - PR 流程：**不需要**

### 文件过滤建议

- ✅ **PR 流程**：排除 VHDL、DFT、文档文件
- ✅ **综合流程**：排除 VHDL（除非工具支持）、DFT、文档文件
- ✅ **测试流程**：需要 DFT/ATPG 文件（如果进行测试）

**总结：**
> **VHDL、DFT 和文档文件都不是 PR 流程需要的文件！**
> 
> **这些文件已经被过滤脚本正确排除。**

---

## 参考

- **VHDL**：VHSIC Hardware Description Language，硬件描述语言
- **DFT**：Design For Test，可测试性设计
- **ATPG**：Automatic Test Pattern Generation，自动测试模式生成
- **FastScan**：Synopsys 的 ATPG 工具

