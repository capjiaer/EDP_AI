# 按工具/用途过滤文件列表

本文档说明如何根据不同的工具和用途，生成不同的文件列表。

## 设计理念

**核心思想：** 根据不同的工具和用途，生成对应的文件列表，让用户可以根据需求选择。

## 文件列表分类

### List1: 综合用文件（Synthesis）

**用途：** Design Compiler 等综合工具

**包含文件：**
- ✅ `verilog/std_primitives.v` - 标准原语文件（必须）
- ✅ `verilog/3.0/xx.v` - 主库文件（推荐）或 `verilog/2.1/xx.v`（备选）

**排除文件：**
- ❌ `verilog/xx.vm` - 仿真用
- ❌ `verilog/xx.mv` - 工具特定格式
- ❌ `verilog/rtl_primitives.v` - RTL设计用
- ❌ `verilog/atpg_primitives.v` - 测试用

**生成命令：**
```bash
python get_dir_structure_filtered.py <ori_path> synthesis_files.txt --filter synthesis
```

---

### List2: PR ICC2用文件（PR for ICC2/Fusion Compiler）

**用途：** Synopsys ICC2, Fusion Compiler

**包含文件：**
- ✅ `ndm/xx_frame_only.ndm/` - NDM文件（物理信息）
- ✅ 或 `ndm_mixed/xx_frame_only.ndm/` - NDM文件（如果只有ndm_mixed）

**⚠️ 注意：TF文件应该在PDK级别提供，不在库级别处理！**
- ❌ 库级别的 `tf/xx_*.tf` 文件应该**排除**（冗余）
- ✅ TF文件应该从**PDK级别**获取（更高层级）

**排除文件：**
- ❌ LEF文件（ICC2不使用）
- ❌ Liberty文件（从NDM读取，或单独读取）
- ❌ `tf/xx_*.tf` - Technology File（应该在PDK级别，不在库级别）

**生成命令：**
```bash
python get_dir_structure_filtered.py <ori_path> pr_icc2_files.txt --filter pr_icc2
```

---

### List3: PR Innovus用文件（PR for Innovus）

**用途：** Cadence Innovus

**包含文件：**
- ✅ `lef/xx.lef` - LEF文件（物理信息）
- ✅ `ccs_lvf/xx_*.db` - Liberty/CCS_LVF文件（时序信息）
- ✅ `tf/xx_*.tf` - Technology File（工艺技术文件，可选）

**排除文件：**
- ❌ NDM文件（Innovus不使用）

**生成命令：**
```bash
python get_dir_structure_filtered.py <ori_path> pr_innovus_files.txt --filter pr_innovus
```

---

## 使用示例

### 生成所有文件列表

```bash
# 1. 综合用文件列表
python get_dir_structure_filtered.py \
    /tech_1/designkit/Samsung/LN08LPU_GP/ori/auto_std/v-logic_sa08nvmhlogl22hdf068a/ \
    synthesis_files.txt \
    --filter synthesis

# 2. PR ICC2用文件列表
python get_dir_structure_filtered.py \
    /tech_1/designkit/Samsung/LN08LPU_GP/ori/auto_std/v-logic_sa08nvmhlogl22hdf068a/ \
    pr_icc2_files.txt \
    --filter pr_icc2

# 3. PR Innovus用文件列表
python get_dir_structure_filtered.py \
    /tech_1/designkit/Samsung/LN08LPU_GP/ori/auto_std/v-logic_sa08nvmhlogl22hdf068a/ \
    pr_innovus_files.txt \
    --filter pr_innovus
```

### 输出文件示例

**synthesis_files.txt:**
```
verilog/std_primitives.v
verilog/3.0/sa08nvmhlogl22hdf068a.v
```

**pr_icc2_files.txt:**
```
ndm/sa08nvmhlogl22hdf068a_frame_only.ndm/reflib.ndm
# 注意：TF文件应该在PDK级别获取，不在库级别处理
```

**pr_innovus_files.txt:**
```
lef/sa08nvmhlogl22hdf068a.lef
ccs_lvf/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
ccs_lvf/sa08nvmhlogl22hdf068a_sspg0p585v125c.db
# 注意：TF文件（Tech LEF）应该在PDK级别获取，不在库级别处理
```

---

## 集成到 edp_libkit

### 未来扩展

可以将这个功能集成到 `edp_libkit` 的 `gen-lib` 命令中：

```bash
# 生成综合用的lib_config.tcl
edp-libkit gen-lib --foundry Samsung -o <path> --tool synthesis

# 生成ICC2用的lib_config.tcl
edp-libkit gen-lib --foundry Samsung -o <path> --tool pr_icc2

# 生成Innovus用的lib_config.tcl
edp-libkit gen-lib --foundry Samsung -o <path> --tool pr_innovus
```

### 优势

1. **清晰分离**：不同工具的文件列表分开，不会混淆
2. **按需选择**：用户可以根据使用的工具选择对应的文件列表
3. **易于维护**：每个工具的文件需求清晰明确
4. **灵活扩展**：未来可以轻松添加新的工具支持

---

## 总结

| 文件列表 | 用途 | 包含文件 |
|---------|------|---------|
| **List1 (synthesis)** | 综合 | `std_primitives.v` + `3.0/xx.v` |
| **List2 (pr_icc2)** | PR ICC2 | `ndm/xx_frame_only.ndm/`（TF文件在PDK级别） |
| **List3 (pr_innovus)** | PR Innovus | `lef/xx.lef` + `ccs_lvf/xx.db`（Tech LEF在PDK级别） |

**这样的设计让 `edp_libkit` 更加清晰和实用！**

