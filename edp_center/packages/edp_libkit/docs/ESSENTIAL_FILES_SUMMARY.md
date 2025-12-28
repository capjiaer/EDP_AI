# 库文件必需文件总结

本文档总结在生成 `lib_config.tcl` 时，对于不同用途需要保留的**最小必需文件集**。

## 快速参考

### 对于综合（Synthesis）

**必需文件（2个）：**

1. ✅ `verilog/std_primitives.v` - 标准原语文件（必须）
2. ✅ `verilog/3.0/xx.v` - 主库文件（推荐）或 `verilog/2.1/xx.v`（备选）

**不需要的文件：**
- ❌ `verilog/xx.vm` - 仿真用
- ❌ `verilog/xx.mv` - 工具特定格式
- ❌ `verilog/rtl_primitives.v` - RTL设计用
- ❌ `verilog/atpg_primitives.v` - 测试用

---

### 对于 PR（Place & Route）

**⚠️ 核心理解：PR vs PV**

**PR 流程本身只需要：**
- ✅ 物理抽象信息（LEF 或 NDM）
- ✅ 时序信息（Liberty `.db`）

**PR 流程不需要：**
- ❌ GDS/OAS 文件（这些是 PV 流程用的）
- ❌ CDL/SPICE 文件（这些是 PV 流程用的）

---

**取决于使用的工具：**

#### 情况1：使用 Innovus（Cadence）

**PR 流程必需文件：**
1. ✅ `lef/xx.lef` - LEF文件（物理抽象信息）
2. ✅ `ccs_lvf/xx_*.db` - Liberty/CCS_LVF文件（时序信息，每个PVT corner一个）

**PR 流程不需要的文件：**
- ❌ NDM文件（Innovus不使用）
- ❌ GDS/OAS文件（PV流程用的）
- ❌ CDL/SPICE文件（PV流程用的）

---

#### 情况2：使用 ICC2/Fusion Compiler（Synopsys）

**PR 流程必需文件：**
1. ✅ `ndm/xx.ndm/` 或 `ndm_mixed/xx_frame_only.ndm/` - NDM文件（物理抽象信息）
2. ✅ `ccs_lvf/xx_*.db` - Liberty/CCS_LVF文件（时序信息，每个PVT corner一个）

**PR 流程不需要的文件：**
- ❌ LEF文件（ICC2不使用）
- ❌ GDS/OAS文件（PV流程用的）
- ❌ CDL/SPICE文件（PV流程用的）

**⚠️ 注意：TF文件（Technology File）应该在PDK级别提供，不在库级别处理！**
- ❌ 库级别的 `tf/xx_*.tf` 文件应该**忽略**（冗余）
- ✅ TF文件应该从**PDK级别**获取（更高层级）

**如果只有 `ndm_mixed`：**
- ✅ `ndm_mixed/xx_frame_only.ndm/` - 物理抽象信息
- ✅ `ccs_lvf/xx_*.db` - 时序信息（从Liberty文件读取）

---

## 你看到的三个文件分析

根据你提供的文件列表：

```
1. verilog/3.0/sa08nvgllogl22hdp068a.v        # ✅ 综合必需
2. verilog/std_primitives.v                    # ✅ 综合必需
3. ndm/sa08nvgllogl22hdp068a_frame_only.ndm/  # ✅ PR必需（物理信息）
```

### 对于综合：✅ 足够

- ✅ `verilog/std_primitives.v` - 原语定义
- ✅ `verilog/3.0/xx.v` - 主库文件

**这两个文件足够用于综合！**

---

### 对于 PR：⚠️ 还需要时序文件

**当前有：**
- ✅ `ndm/xx_frame_only.ndm/` - 物理信息（足够）

**还需要：**
- ⚠️ `ccs_lvf/xx_*.db` - 时序信息（Liberty文件，每个PVT corner一个）

**⚠️ 注意：TF文件应该在PDK级别提供，不在库级别处理！**

**示例：**
```
ccs_lvf/
├── sa08nvgllogl22hdp068a_ffpg0p715vn40c.db  # Fast-Fast corner
├── sa08nvgllogl22hdp068a_sspg0p585v125c.db  # Slow-Slow corner
└── sa08nvgllogl22hdp068a_ttpg0p65v25c.db    # Typical corner
```

---

## 完整的最小必需文件集

### 场景1：综合 + PR（Innovus）

**必需文件：**
1. ✅ `verilog/std_primitives.v`
2. ✅ `verilog/3.0/xx.v`
3. ✅ `lef/xx.lef`
4. ✅ `ccs_lvf/xx_*.db`（每个PVT corner）

**总计：** 2个Verilog文件 + 1个LEF文件 + N个Liberty文件（N = PVT corner数量）

---

### 场景2：综合 + PR（ICC2/Fusion Compiler）

**必需文件：**
1. ✅ `verilog/std_primitives.v`
2. ✅ `verilog/3.0/xx.v`
3. ✅ `ndm/xx.ndm/` 或 `ndm_mixed/xx_frame_only.ndm/`
4. ✅ `ccs_lvf/xx_*.db`（每个PVT corner）

**⚠️ 注意：TF文件应该在PDK级别提供，不在库级别处理！**

**总计：** 2个Verilog文件 + 1个NDM文件 + N个Liberty文件（N = PVT corner数量）

---

## 总结

### 你看到的三个文件

| 文件 | 用途 | 是否足够？ |
|------|------|-----------|
| `verilog/3.0/xx.v` | 综合 | ✅ 足够（配合std_primitives.v） |
| `verilog/std_primitives.v` | 综合 | ✅ 足够（配合3.0/xx.v） |
| `ndm/xx_frame_only.ndm/` | PR（物理） | ⚠️ **还需要时序文件** |

### 对于 PR，还需要：

- ✅ `ccs_lvf/xx_*.db` - Liberty文件（时序信息）

**⚠️ 注意：TF文件应该在PDK级别提供，不在库级别处理！**

### 最终答案

**对于综合：** ✅ 这两个 `.v` 文件足够

**对于 PR：** ⚠️ 还需要 `ccs_lvf/xx_*.db`

**完整的最小集：**
- 综合：`std_primitives.v` + `3.0/xx.v`
- PR：`ndm/xx_frame_only.ndm/` + `ccs_lvf/xx_*.db`
- **TF文件：从PDK级别获取（不在库级别处理）**

