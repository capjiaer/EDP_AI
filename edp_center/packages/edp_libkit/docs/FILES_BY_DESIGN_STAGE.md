# 不同设计阶段需要的文件总结

本文档总结不同设计阶段（SYN、PR_INNOVUS、PR_FC、STA、DFT、IREM_REDHAWK、IREM_VOLTUS、PV、PA、RC）需要的文件类型。

## ⚠️ 核心理解

**不同的设计阶段需要不同的文件！**

每个阶段都有其特定的文件需求，不能混用。

---

## 📋 各阶段文件需求总结

### 1. SYN（Synthesis）- 综合

**必需文件：**
1. ✅ **Verilog 文件**（`.v`）
   - `verilog/std_primitives.v` - 标准原语文件（必须）
   - `verilog/3.0/xx.v` - 主库文件（推荐）或 `verilog/2.1/xx.v`（备选）

**不需要的文件：**
- ❌ `.lib`, `.db` - 时序库（综合不需要）
- ❌ `.lef`, `.ndm` - 物理抽象（综合不需要）
- ❌ `.gds`, `.oasis` - 版图（综合不需要）

**工具：** Design Compiler, Genus

---

### 2a. PR_INNOVUS（Place & Route - Innovus）- 布局布线（Cadence Innovus）

**必需文件：**
1. ✅ **LEF 文件**（`.lef`）
   - Library Exchange Format，物理抽象信息
2. ✅ **时序库文件**（`.lib`, `.db`）
   - Liberty 文件（每个 PVT corner 一个）
   - `ccs_lvf/xx_*.db` 或 `liberty/xx_*.db`

**可选文件（优化）：**
3. ⚠️ **CDB 文件**（`.cdb/`）- **可选优化**
   - Cell Database，Cadence 二进制数据库格式
   - 本质上是 LEF + Liberty 的二进制格式版本
   - 如果已有 LEF + Liberty，CDB 是可选的优化（读取更快）
   - 位置：`cdb/`，包含 `*_gencdb.tcl` 生成脚本

**不需要的文件：**
- ❌ Verilog 文件（`.v`）- 综合用的
- ❌ AOCV 文件（`.aocv`）- STA 用的
- ❌ CCS Power 文件 - IREM/PA 用的
- ❌ NDM 文件 - PR_FC 用的
- ❌ GDS/OASIS 文件 - PV 用的（严格来说）

**工具：** Innovus（Cadence）

---

### 2b. PR_FC（Place & Route - Fusion Compiler）- 布局布线（Synopsys Fusion Compiler/ICC2）

**必需文件：**
1. ✅ **NDM 文件**（`.ndm/`）
   - Native Design Model，物理抽象信息（Synopsys 格式）
   - `ndm/xx_frame_only.ndm/` 或 `ndm_mixed/xx_frame_only.ndm/`
2. ✅ **时序库文件**（`.lib`, `.db`）
   - Liberty 文件（每个 PVT corner 一个）
   - `ccs_lvf/xx_*.db` 或 `liberty/xx_*.db`

**可选文件（旧版工具）：**
3. ⚠️ **Milkyway 文件**（`.mw/`）- **旧版格式，已淘汰**
   - ICC1/Astro（旧版工具）使用
   - ⚠️ **旧版格式，已淘汰**，已被 NDM 格式取代

**不需要的文件：**
- ❌ Verilog 文件（`.v`）- 综合用的
- ❌ AOCV 文件（`.aocv`）- STA 用的
- ❌ CCS Power 文件 - IREM/PA 用的
- ❌ LEF 文件 - PR_INNOVUS 用的
- ❌ CDB 文件 - PR_INNOVUS 用的
- ❌ GDS/OASIS 文件 - PV 用的（严格来说）

**工具：** Fusion Compiler, ICC2（Synopsys）

---

### 3. STA（Static Timing Analysis）- 静态时序分析

**必需文件：**
1. ✅ **时序库文件**（`.lib`, `.db`）
   - Liberty 文件（每个 PVT corner 一个）
   - `ccs_lvf/xx_*.db` 或 `liberty/xx_*.db`
2. ✅ **AOCV 文件**（`.aocv`）- **高级时序分析**（推荐）
   - Advanced On-Chip Variation
   - 考虑片上工艺变化对时序的影响
   - 每个 PVT corner 一个
   - 位置：`aocv/xx_*.aocv`
3. ⚠️ **POCV 文件**（`.pocv`）- **路径基础时序分析**（备选）
   - Path-Based On-Chip Variation
   - 传统的路径基础片上变化方法
   - 如果 AOCV 不可用，可以使用 POCV
   - 每个 PVT corner 一个
   - 位置：`pocv/xx_*.pocv`
4. ⚠️ **MIS 文件**（`.mis.tcl`）- **互连延迟计算**
   - 用于 RC 提取和互连延迟计算
   - 通常在项目级别提供，不在库级别

**不需要的文件：**
- ❌ LEF/NDM 文件 - PR 用的
- ❌ GDS/OASIS 文件 - PV 用的
- ❌ CCS Power 文件 - IREM/PA 用的

**工具：** PrimeTime, Tempus

**注意：**
- **AOCV** 是更先进的方法（推荐）
- **POCV** 是传统方法（备选）
- 两者都是用于 STA 的 OCV 方法，通常只需要其中一种

---

### 4a. IREM_REDHAWK（IR Drop/EM Analysis - RedHawk）- IR 压降和电迁移分析（Cadence RedHawk）

**必需文件：**
1. ✅ **CCS Power 文件**（`.lib_ccs_p.gz`, `.db_ccs_p`）
   - Composite Current Source Power
   - 电流基础的功耗模型
   - 每个 PVT corner 一个
   - 位置：`ccs_power/` 或 `liberty/ccs_power/`
2. ✅ **RedHawk 文件**（`.cdev`, `.pwcdev`）
   - RedHawk 特定格式文件
   - `.cdev` - Current Device Model（电流设备模型）
   - `.pwcdev` - Power Current Device Model（功耗电流设备模型）
   - 用于 RedHawk IR Drop/EM 分析
   - 位置：`redhawk/apl_models/`，包含 `*_*.cdev` 和 `*_*.pwcdev` 文件

**不需要的文件：**
- ❌ Liberty 时序库（`.db`）- STA/PR 用的
- ❌ LEF/NDM 文件 - PR 用的
- ❌ GDS/OASIS 文件 - PV 用的

**工具：** RedHawk（Cadence）

---

### 4b. IREM_VOLTUS（IR Drop/EM Analysis - Voltus）- IR 压降和电迁移分析（Cadence Voltus）

**必需文件：**
1. ✅ **CCS Power 文件**（`.lib_ccs_p.gz`, `.db_ccs_p`）
   - Composite Current Source Power
   - 电流基础的功耗模型
   - 每个 PVT corner 一个
   - 位置：`ccs_power/` 或 `liberty/ccs_power/`

**可选文件：**
2. ⚠️ **Voltus 生成脚本**（`voltus_gen_scripts/`）
   - Voltus 工具特定脚本和配置文件
   - 位置：`voltus/voltus_gen_scripts/`，包含脚本和配置文件

**不需要的文件：**
- ❌ Liberty 时序库（`.db`）- STA/PR 用的
- ❌ LEF/NDM 文件 - PR 用的
- ❌ GDS/OASIS 文件 - PV 用的
- ❌ RedHawk 文件（`.cdev`, `.pwcdev`）- IREM_REDHAWK 用的

**工具：** Voltus（Cadence）

---

### 5. PA（Power Analysis）- 功耗分析

**必需文件：**
1. ✅ **CCS Power 文件**（`.lib_ccs_p.gz`, `.db_ccs_p`）
   - Composite Current Source Power
   - 电流基础的功耗模型
   - 每个 PVT corner 一个
   - 位置：`ccs_power/` 或 `liberty/ccs_power/`

**可选文件：**
2. ⚠️ **Liberty 时序库**（`.db`）- 基本功耗信息（如果 CCS Power 不可用）

**不需要的文件：**
- ❌ LEF/NDM 文件 - PR 用的
- ❌ GDS/OASIS 文件 - PV 用的
- ❌ AOCV 文件 - STA 用的

**工具：** PrimeTime PX, Voltus

---

### 6. PV（Physical Verification）- 物理验证

**必需文件：**
1. ✅ **版图文件**
   - GDS 文件（`.gds`, `.gds2`）
   - OASIS 文件（`.oasis`, `.oas`）
2. ✅ **网表文件**（用于 LVS）
   - CDL 文件（`.cdl`）
   - SPICE 文件（`.sp`, `.spice`）

**不需要的文件：**
- ❌ LEF/NDM 文件 - PR 用的（PV 不需要抽象版图）
- ❌ Liberty 文件（`.db`）- STA/PR 用的
- ❌ Verilog 文件（`.v`）- 综合用的

**工具：** Calibre, ICV, Pegasus

---

### 7. RC（RC Extraction）- RC 提取

**必需文件：**
1. ✅ **Technology File**（`.tf`）
   - 定义金属层、通孔和设计规则
   - **通常在 PDK 级别提供**，不在库级别
2. ✅ **LEF 文件**（`.lef`）
   - 物理抽象信息（用于 RC 提取）
3. ⚠️ **MIS 文件**（`.mis.tcl`）- **互连 RC 参数**
   - 定义互连的 RC 参数
   - 每个 PVT corner 一个
   - **通常在项目级别提供**，不在库级别

**可选文件（早期设计阶段）：**
4. ⚠️ **FXM 文件**（`.fxm`）- **快速寄生参数提取**
   - Fast Extraction Model，快速提取模型
   - 用于快速 RC 提取（比完整提取更快，但精度略低）
   - 适用于早期设计阶段，快速迭代
   - ⚠️ **Sign-off 阶段不使用**（使用完整提取，高精度）
   - 位置：`fxm/xx.fxm`

**不需要的文件：**
- ❌ Liberty 文件（`.db`）- STA/PR 用的
- ❌ GDS/OASIS 文件 - PV 用的（RC 提取不需要完整版图）

**工具：** StarRC, Quantus, Calibre xRC

---

### 8. DFT（Design for Test）- 可测试性设计

**必需文件：**
1. ✅ **Verilog 文件**（`.v`）
   - `verilog/atpg_primitives.v` - ATPG 原语文件（必须）
   - `verilog/std_primitives.v` - 标准原语文件（可选）
   - `verilog/3.0/xx.v` - 主库文件（可选）
2. ✅ **ATPG 文件**（`.atpg`）
   - ATPG 特定格式文件
   - 用于测试向量生成
   - 位置：`dft/` 或 `dft/fastscan/`

**不需要的文件：**
- ❌ LEF/NDM 文件 - PR 用的
- ❌ Liberty 文件（`.db`）- STA/PR 用的
- ❌ GDS/OASIS 文件 - PV 用的

**工具：** TetraMAX, FastScan, TestMAX

---

## 📊 文件类型与阶段对应表

| File Type                | SYN | PR_INNOVUS | PR_FC | STA | DFT | IREM_REDHAWK | IREM_VOLTUS | PA | PV | RC |
|--------------------------|-----|------------|-------|-----|-----|--------------|-------------|----|----|----|
| Verilog (.v)             | 1   | 0          | 0     | 0   | 1   | 0            | 0           | 0  | 0  | 0  |
| LEF (.lef)               | 0   | 1          | 0     | 0   | 0   | 0            | 0           | 0  | 0  | 1  |
| NDM (.ndm/)              | 0   | 0          | 1     | 0   | 0   | 0            | 0           | 0  | 0  | 0  |
| Milkyway (.mw/)          | 0   | 0          | 1     | 0   | 0   | 0            | 0           | 0  | 0  | 0  |
| CDB (.cdb/)              | 0   | 1          | 0     | 0   | 0   | 0            | 0           | 0  | 0  | 0  |
| Liberty (.lib, .db)      | 0   | 1          | 1     | 1   | 0   | 0            | 0           | 0  | 0  | 0  |
| AOCV (.aocv)             | 0   | 0          | 0     | 1   | 0   | 0            | 0           | 0  | 0  | 0  |
| POCV (.pocv)             | 0   | 0          | 0     | 1   | 0   | 0            | 0           | 0  | 0  | 0  |
| ATPG (.atpg)             | 0   | 0          | 0     | 0   | 1   | 0            | 0           | 0  | 0  | 0  |
| CCS Power (.lib_ccs_p)   | 0   | 0          | 0     | 0   | 0   | 1            | 1           | 1  | 0  | 0  |
| RedHawk (.cdev/.pwcdev)  | 0   | 0          | 0     | 0   | 0   | 1            | 0           | 0  | 0  | 0  |
| Voltus (scripts)         | 0   | 0          | 0     | 0   | 0   | 0            | 1           | 0  | 0  | 0  |
| GDS/OASIS (.gds/.oas)    | 0   | 0          | 0     | 0   | 0   | 0            | 0           | 0  | 1  | 0  |
| CDL/SPICE (.cdl/.sp)     | 0   | 0          | 0     | 0   | 0   | 0            | 0           | 0  | 1  | 0  |
| Technology File (.tf)    | 0   | 0          | 0     | 0   | 0   | 0            | 0           | 0  | 0  | 1  |
| MIS (.mis.tcl)           | 0   | 0          | 0     | 1   | 0   | 0            | 0           | 0  | 0  | 1  |
| FXM (.fxm)               | 0   | 0          | 0     | 0   | 0   | 0            | 0           | 0  | 0  | 1  |

**Note:** 
- Milkyway (.mw/) is legacy format for ICC1/Astro, replaced by NDM for ICC2/Fusion Compiler
- CDB (.cdb/) is optional optimization for Innovus, equivalent to LEF + Liberty in binary format
- FXM (.fxm) is for fast RC extraction in early design stages, not used in sign-off (full extraction preferred)
- PR_INNOVUS: Cadence Innovus (LEF + Liberty, optional CDB)
- PR_FC: Synopsys Fusion Compiler/ICC2 (NDM + Liberty, optional Milkyway for legacy tools)
- IREM_REDHAWK: Cadence RedHawk (CCS Power + RedHawk .cdev/.pwcdev)
- IREM_VOLTUS: Cadence Voltus (CCS Power + Voltus scripts)

**Legend:**
- 1 = Required
- 0 = Not Required

---

## 🔍 详细说明

### 文件类型说明

#### 1. Verilog 文件（`.v`）
- **用途**：综合（SYN）
- **内容**：标准单元库的 Verilog 定义
- **位置**：`verilog/3.0/xx.v`, `verilog/std_primitives.v`

#### 2. LEF 文件（`.lef`）
- **用途**：PR_INNOVUS（Innovus）、RC 提取
- **内容**：物理抽象信息
- **位置**：`lef/xx.lef`

#### 3. NDM 文件（`.ndm/`）
- **用途**：PR_FC（ICC2/Fusion Compiler）
- **内容**：物理抽象信息（Synopsys 格式）
- **位置**：`ndm/xx_frame_only.ndm/` 或 `ndm_mixed/xx_frame_only.ndm/`

#### 3a. Milkyway 文件（`.mw/`）
- **用途**：PR_FC（ICC1/Astro，旧版工具）
- **内容**：物理抽象信息（Synopsys 旧版格式）
- **位置**：`milkyway/` 或 `mw/`，包含 `FRAM/`, `CEL/`, `LM/` 等子目录
- **说明**：⚠️ **旧版格式，已淘汰**，已被 NDM 格式取代

#### 3b. CDB 文件（`.cdb/`）
- **用途**：PR_INNOVUS（Innovus，可选优化）
- **内容**：Cell Database，Cadence 二进制数据库格式，本质上是 LEF + Liberty 的二进制版本
- **位置**：`cdb/`，包含 `*_gencdb.tcl` 生成脚本
- **说明**：⚠️ **可选优化**，如果已有 LEF + Liberty，CDB 不是必需的，但可以提供更快的读取速度

#### 4. Liberty 文件（`.lib`, `.db`）
- **用途**：PR_INNOVUS、PR_FC、STA、PA（可选）
- **内容**：时序信息、功耗信息（基本）
- **位置**：`ccs_lvf/xx_*.db` 或 `liberty/xx_*.db`

#### 5. AOCV 文件（`.aocv`）
- **用途**：STA（高级时序分析，推荐）
- **内容**：Advanced On-Chip Variation，片上工艺变化对时序的影响
- **位置**：`aocv/xx_*.aocv`
- **说明**：更先进的 OCV 方法，推荐使用

#### 5a. POCV 文件（`.pocv`）
- **用途**：STA（路径基础时序分析，备选）
- **内容**：Path-Based On-Chip Variation，路径基础片上变化
- **位置**：`pocv/xx_*.pocv`
- **说明**：传统的 OCV 方法，如果 AOCV 不可用可以使用 POCV

#### 6. CCS Power 文件（`.lib_ccs_p.gz`, `.db_ccs_p`）
- **用途**：IREM_REDHAWK、IREM_VOLTUS、PA
- **内容**：电流基础的功耗模型
- **位置**：`ccs_power/` 或 `liberty/ccs_power/`

#### 6a. RedHawk 文件（`.cdev`, `.pwcdev`）
- **用途**：IREM_REDHAWK（RedHawk IR Drop/EM 分析）
- **内容**：RedHawk 特定格式文件
  - `.cdev` - Current Device Model（电流设备模型）
  - `.pwcdev` - Power Current Device Model（功耗电流设备模型）
- **位置**：`redhawk/apl_models/`，包含 `*_*.cdev` 和 `*_*.pwcdev` 文件
- **说明**：RedHawk 工具特定格式，用于 IR Drop/EM 分析

#### 6b. Voltus 文件（`voltus_gen_scripts/`）
- **用途**：IREM_VOLTUS（Voltus IR Drop/EM 分析）
- **内容**：Voltus 工具特定脚本和配置文件
  - `voltus_gen_scripts/` - Voltus 生成脚本目录
  - 包含脚本、配置文件和输入文件
- **位置**：`voltus/voltus_gen_scripts/`
- **说明**：Voltus 工具特定格式，用于 IR Drop/EM 分析

#### 7. GDS/OASIS 文件（`.gds`, `.oasis`）
- **用途**：PV（物理验证）
- **内容**：完整版图信息
- **位置**：`gds/xx.gds`, `gds/xx.oasis`

#### 8. CDL/SPICE 文件（`.cdl`, `.sp`）
- **用途**：PV（LVS）
- **内容**：电路网表
- **位置**：`cdl/xx.cdl`, `spice/xx.sp`

#### 9. Technology File（`.tf`）
- **用途**：RC 提取、PR（可选）
- **内容**：金属层、通孔、设计规则定义
- **位置**：**通常在 PDK 级别提供**，不在库级别

#### 10. MIS 文件（`.mis.tcl`）
- **用途**：STA、RC 提取
- **内容**：互连 RC 参数
- **位置**：**通常在项目级别提供**，不在库级别

#### 11. POCV 文件（`.pocv`）
- **用途**：STA（路径基础时序分析）
- **内容**：Path-Based On-Chip Variation，路径基础片上变化
- **位置**：`pocv/xx_*.pocv`
- **说明**：传统的 OCV 方法，如果 AOCV 不可用可以使用 POCV

#### 12. ATPG 文件（`.atpg`）
- **用途**：DFT（可测试性设计）
- **内容**：ATPG 特定格式文件，用于测试向量生成
- **位置**：`dft/` 或 `dft/fastscan/`
- **说明**：用于 ATPG 工具生成测试向量

#### 13. FXM 文件（`.fxm`）
- **用途**：RC 提取（快速寄生参数提取，早期设计阶段）
- **内容**：Fast Extraction Model，快速提取模型，用于快速 RC 提取
- **位置**：`fxm/xx.fxm`
- **说明**：⚠️ **早期设计阶段使用**（快速迭代），Sign-off 阶段不使用（使用完整提取，高精度）

---

## ✅ 总结

### 核心理解

1. **不同阶段需要不同的文件**
   - SYN：Verilog
   - PR_INNOVUS：LEF + Liberty（可选 CDB）
   - PR_FC：NDM + Liberty（可选 Milkyway，旧版格式）
   - STA：Liberty + AOCV（或 POCV）+ MIS
   - DFT：Verilog（atpg_primitives.v）+ ATPG
   - IREM_REDHAWK：CCS Power + RedHawk（.cdev/.pwcdev）
   - IREM_VOLTUS：CCS Power + Voltus scripts
   - PA：CCS Power
   - PV：GDS/OASIS + CDL/SPICE
   - RC：Technology File + LEF + MIS + FXM（可选，早期设计阶段）

2. **文件不能混用**
   - 每个阶段都有其特定的文件需求
   - 不能用一个阶段的文件替代另一个阶段的文件

3. **文件位置**
   - 库级别：Verilog, LEF, NDM, Milkyway, CDB, Liberty, AOCV, POCV, ATPG, CCS Power, RedHawk (.cdev/.pwcdev), Voltus (voltus_gen_scripts), GDS/OASIS, CDL/SPICE, FXM
   - PDK 级别：Technology File
   - 项目级别：MIS 文件

---

## 参考

- **SYN**：Synthesis，综合
- **PR_INNOVUS**：Place & Route - Innovus，布局布线（Cadence Innovus）
- **PR_FC**：Place & Route - Fusion Compiler，布局布线（Synopsys Fusion Compiler/ICC2）
- **STA**：Static Timing Analysis，静态时序分析
- **DFT**：Design for Test，可测试性设计
- **IREM_REDHAWK**：IR Drop/EM Analysis - RedHawk，IR 压降和电迁移分析（Cadence RedHawk）
- **IREM_VOLTUS**：IR Drop/EM Analysis - Voltus，IR 压降和电迁移分析（Cadence Voltus）
- **PA**：Power Analysis，功耗分析
- **PV**：Physical Verification，物理验证
- **RC**：RC Extraction，RC 提取
- **AOCV**：Advanced On-Chip Variation，高级片上变化
- **POCV**：Path-Based On-Chip Variation，路径基础片上变化
- **ATPG**：Automatic Test Pattern Generation，自动测试模式生成
- **Milkyway**：Synopsys 旧版物理设计数据库格式（ICC1/Astro），已被 NDM 取代
- **CDB**：Cell Database，Cadence 二进制数据库格式（Innovus 可选优化），等价于 LEF + Liberty 的二进制版本
- **FXM**：Fast Extraction Model，快速寄生参数提取模型（早期设计阶段使用，Sign-off 不使用）
- **RedHawk**：Cadence IR Drop/EM 分析工具
- **Voltus**：Cadence IR Drop/EM 分析工具
- **CDEV**：Current Device Model，电流设备模型（RedHawk 格式）
- **PWCDEV**：Power Current Device Model，功耗电流设备模型（RedHawk 格式）

