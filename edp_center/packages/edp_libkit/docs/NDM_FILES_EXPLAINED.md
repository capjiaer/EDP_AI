# NDM 文件详解

本文档解释 NDM（Native Design Model）文件在 IC 设计流程中的作用。

## NDM 文件简介

**NDM（Native Design Model）** 是 **Synopsys 工具**（如 ICC2, Fusion Compiler）使用的**二进制数据库格式**。

### 基本概念

- **格式**：二进制数据库格式（类似 Innovus 的 `.db` 文件）
- **工具**：Synopsys ICC2, Fusion Compiler
- **用途**：存储标准单元库的物理和时序信息
- **优势**：比文本格式（LEF, Liberty）更高效，工具读取更快

### ⚠️ 核心理解：NDM 的本质

**NDM = Liberty库的二进制格式版本**

**关键理解：**
- ✅ **NDM 本质上就是 Liberty 库**（`.db` 文件），只是**格式不同**
- ✅ **目的**：集中文件（物理+时序合并），配合工具更快
- ✅ **用途**：给 PR（Place & Route）流程提供时序信息

**格式对比：**

| 格式 | 文件类型 | 工具 | 用途 |
|------|---------|------|------|
| **Liberty** | `.db`（文本格式） | Innovus, ICC2 | PR时序信息 |
| **NDM** | `.ndm/`（二进制格式） | ICC2, Fusion Compiler | PR时序信息 + 物理信息 |

**本质相同性：**
```
Liberty (.db) = 文本格式的时序库
NDM (.ndm)    = 二进制格式的时序库（+ 物理信息）

两者功能相同，只是格式不同！
```

**NDM 的优势：**
1. ✅ **信息集中**：物理+时序合并在一起
2. ✅ **二进制格式**：比文本格式（Liberty）读取更快
3. ✅ **工具优化**：Synopsys 工具对 NDM 格式有专门优化
4. ✅ **配置简单**：一个文件搞定，不需要读取多个 `.db` 文件

**实际使用：**
- **Innovus**：使用 LEF + Liberty（文本格式）
- **ICC2**：使用 NDM（二进制格式，信息集中）
- **两者功能相同**，只是格式和工具不同

---

## NDM 文件结构

### 目录结构示例

#### `ndm` 目录结构

```
ndm/
├── sa08nvgllogl22hdp068a_frame_only.ndm/  # NDM 数据库目录
│   └── reflib.ndm                          # NDM 数据库文件
├── tf/                                     # Technology File 目录
│   ├── sa08nvgllogl22hdp068a_13M_3Mx_6Dx_2Hx_2Iz_LB.tf
│   ├── sa08nvgllogl22hdp068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
│   ├── sa08nvgllogl22hdp068a_11M_3Mx_6Dx_1Gx_1Iz_LB.tf
│   ├── sa08nvgllogl22hdp068a_small_die_13M_3Mx_6Dx_2Hx_2Iz_LB.tf
│   └── ...
├── scripts/                                # 脚本目录
│   ├── ndmgen_frame_only.tcl              # 生成frame_only NDM的脚本
│   ├── ndmgen_frame_timing.tcl            # 生成frame_timing NDM的脚本
│   ├── icc2_lm_setup.tcl                  # ICC2 Library Manager设置脚本
│   ├── library_global_lm_setting.tcl      # 库全局LM设置脚本
│   ├── PMJ.tcl                            # PMJ相关脚本
│   ├── ndm2mw.tcl                         # NDM转Milkyway脚本
│   ├── change_site.tcl                    # 修改site的脚本
│   ├── gds_in_layer_map.*                 # GDS输入层映射文件
│   ├── gds_out_layer_map.*                # GDS输出层映射文件
│   └── block.map                          # Block映射文件
├── README_ndm                             # NDM说明文档
├── Makefile                               # 构建脚本
└── sa08.clf                               # CLF文件（Cell Library Format）
```

#### `ndm_mixed` 目录结构

```
ndm_mixed/
├── sa08nvmhlogl22hdf068a_frame_only.ndm/
│   └── reflib.ndm                    # NDM 数据库文件
├── tf/                               # Technology File 目录
│   ├── sa08nvmhlogl22hdf068a_13M_3Mx_6Dx_2Hx_2Iz_LB.tf
│   ├── sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
│   └── sa08nvmhlogl22hdf068a_11M_3Mx_6Dx_1Gx_1Iz_LB.tf
├── scripts/                          # 脚本目录
│   ├── ndmgen_frame_only.tcl
│   ├── ndmgen_frame_timing.tcl
│   ├── icc2_lm_setup.tcl
│   └── ...
├── README_ndm_mixed                  # 说明文档
├── Makefile                          # 构建脚本
└── sa08.clf                          # CLF 文件
```

### 关键文件说明

| 文件类型 | 扩展名 | 用途 | 是否必需？ |
|---------|--------|------|-----------|
| **NDM 数据库** | `.ndm/` | 二进制数据库目录，包含库的物理和时序信息 | ✅ **必需** |
| **Technology File** | `.tf` | 工艺技术文件，定义金属层、via、设计规则等 | ✅ **必需** |
| **CLF 文件** | `.clf` | Cell Library Format，标准单元库格式 | ⚠️ 可选 |
| **TCL 脚本** | `.tcl` | 用于生成和管理 NDM 的脚本 | ⚠️ 可选（工具用） |
| **Layer Map 文件** | `.map` | GDS层映射文件，定义GDS层到工艺层的映射 | ⚠️ 可选 |
| **Makefile** | `Makefile` | 构建脚本，用于自动化生成NDM | ⚠️ 可选（工具用） |
| **README** | `README_ndm` | 说明文档，解释如何使用NDM文件 | ⚠️ 可选（文档） |

---

## NDM 目录下的文件详解

### 1. Technology File (.tf) - 工艺技术文件

**位置：** `ndm/tf/` 目录

**作用：**
- 定义**金属层**（Metal Layer）的物理特性
- 定义**Via**（通孔）的类型和尺寸
- 定义**设计规则**（DRC规则）
- 定义**Metal Stack**（金属堆叠）配置

**文件命名规则：**
```
sa08nvgllogl22hdp068a_13M_3Mx_6Dx_2Hx_2Iz_LB.tf
│                        │   │   │   │   │  │
│                        │   │   │   │   │  └─ LB (Low-k Backend)
│                        │   │   │   │   └─ 2Iz (2层 Interconnect)
│                        │   │   │   └─ 2Hx (2层 High)
│                        │   │   └─ 6Dx (6层 Dense)
│                        │   └─ 3Mx (3层 Metal)
│                        └─ 13M (13层 Metal)
```

**不同配置的TF文件：**
- `13M_3Mx_6Dx_2Hx_2Iz_LB.tf` - 13层金属，标准配置
- `12M_3Mx_6Dx_1Gx_2Iz_LB.tf` - 12层金属，1层Global
- `11M_3Mx_6Dx_1Gx_1Iz_LB.tf` - 11层金属，1层Interconnect
- `small_die_13M_3Mx_6Dx_2Hx_2Iz_LB.tf` - 小die配置

**使用场景：**
- 根据项目的**Metal Stack**选择对应的TF文件
- 不同Metal Stack需要不同的TF文件

**关键理解：**
> **Metal Stack 确定 → TF文件确定 → GDS层映射文件确定**
> 
> 三者是**一一对应**的关系！

**对应关系：**
```
Metal Stack: 12M_3Mx_6Dx_1Gx_2Iz_LB
    ↓
TF文件: sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
    ↓
GDS层映射: gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB
          gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB
```

---

### ⚠️ 重要：TF文件的位置问题

**你的观察是对的！**

**理论上：**
- ✅ TF文件应该是**工艺级别**的文件（PDK级别）
- ✅ 同一个工艺节点的**所有库**应该**共享**同一个TF文件
- ✅ 不应该每个标准单元库都有一份TF文件

**实际情况：**
- ⚠️ Foundry为了方便打包，可能在每个库目录下都放了一份TF文件
- ⚠️ 这是**冗余的**，但可能是为了库的**完整性**和**独立性**

**正确的组织方式应该是：**

```
PDK级别（更高层级）：
pdk/
├── tf/                                    # 工艺技术文件（共享）
│   ├── sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
│   ├── sa08nvmhlogl22hdf068a_13M_3Mx_6Dx_2Hx_2Iz_LB.tf
│   └── ...
└── techlef/                                # Tech LEF（Innovus用）
    └── sa08nvmhlogl22hdf068a_tech.lef

库级别（标准单元库）：
library/STD/sa08nvmhlogl22hdf068a/
├── ndm/                                   # NDM文件（库特定）
│   └── sa08nvmhlogl22hdf068a_frame_only.ndm/
├── lef/                                   # LEF文件（库特定）
│   └── sa08nvmhlogl22hdf068a.lef
└── ccs_lvf/                               # Liberty文件（库特定）
    └── sa08nvmhlogl22hdf068a_*.db
```

**实际Foundry的组织方式（你看到的）：**

```
ori/auto_std/v-logic_sa08nvmhlogl22hdf068a/
├── ndm/
│   ├── tf/                                # ⚠️ TF文件在这里（冗余）
│   │   └── sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
│   └── sa08nvmhlogl22hdf068a_frame_only.ndm/
├── lef/
└── ccs_lvf/
```

**为什么Foundry这样组织？**

1. **完整性**：每个库目录包含所有需要的文件，库是**自包含**的
2. **独立性**：库可以独立使用，不依赖其他目录
3. **方便打包**：库打包时包含所有文件，用户解压后直接可用
4. **版本管理**：不同版本的库可能对应不同版本的TF文件

**实际使用建议：**

1. **如果PDK级别有TF文件**：
   - ✅ 优先使用PDK级别的TF文件（更高层级）
   - ✅ 所有库共享同一个TF文件

2. **如果只有库级别的TF文件**：
   - ⚠️ 可以使用库目录下的TF文件
   - ⚠️ 注意：不同库的TF文件应该是**相同的**（如果Metal Stack相同）

3. **最佳实践**：
   - ✅ 在项目配置中，TF文件路径应该指向**PDK级别**
   - ✅ 库级别的TF文件作为**备选**或**验证用**

**关键理解：**
- ✅ **理论上**：TF文件应该在PDK级别，所有库共享
- ⚠️ **实际上**：Foundry可能在每个库目录下都放了一份（冗余但方便）
- ✅ **使用建议**：优先使用PDK级别的TF文件
- ✅ **`edp_libkit`处理**：**忽略库级别的TF文件**，因为应该在PDK级别提供

**实际应用：**
- ✅ 一旦Metal Stack确定，对应的TF文件就确定了
- ✅ 对应的GDS层映射文件也确定了
- ✅ 它们必须**匹配使用**，不能混用

---

### 2. TCL 脚本文件

**位置：** `ndm/scripts/` 目录

#### 2.1 `ndmgen_frame_only.tcl`

**作用：**
- 生成**frame_only** NDM的脚本
- 用于创建仅包含物理信息的NDM数据库

**使用场景：**
- 工具内部使用，用于生成NDM文件
- 用户通常不需要直接调用

---

#### 2.2 `ndmgen_frame_timing.tcl`

**作用：**
- 生成**frame_timing** NDM的脚本
- 用于创建仅包含时序信息的NDM数据库

**使用场景：**
- 工具内部使用，用于生成NDM文件
- 用户通常不需要直接调用

---

#### 2.3 `icc2_lm_setup.tcl`

**作用：**
- ICC2 Library Manager的设置脚本
- 配置ICC2工具读取NDM库的参数

**使用场景：**
- 在ICC2中设置库时使用
- 可以source这个脚本来配置库

**示例：**
```tcl
# 在ICC2中使用
source /path/to/ndm/scripts/icc2_lm_setup.tcl
```

---

#### 2.4 `library_global_lm_setting.tcl`

**作用：**
- 库的全局Library Manager设置
- 定义库的全局参数和配置

**使用场景：**
- 工具配置用
- 定义库的全局设置

---

#### 2.5 `ndm2mw.tcl`

**作用：**
- 将NDM格式转换为Milkyway格式的脚本
- Milkyway是Synopsys的另一种数据库格式（⚠️ **旧版格式，已淘汰**）

**使用场景：**
- ⚠️ **已不需要**：当前使用 ICC2/Fusion Compiler（使用 NDM 格式）
- ⚠️ **仅适用于旧版工具**：ICC（ICC1）, Astro（已淘汰）
- ❌ **可以忽略**：不需要使用 Milkyway 格式

**实际建议：**
- ✅ **直接忽略**：已经不用老工具了，不需要 Milkyway 格式
- ✅ **只关注 NDM**：当前标准格式

---

#### 2.6 `change_site.tcl`

**作用：**
- 修改site定义的脚本
- Site是标准单元放置的基本单位

**使用场景：**
- 需要修改site配置时使用
- 工具配置用

---

#### 2.7 `PMJ.tcl`

**作用：**
- PMJ（可能是Process Model Job）相关脚本
- 处理工艺模型相关的配置

**使用场景：**
- 工具内部使用
- 工艺模型配置

---

### 3. Layer Map 文件

**位置：** `ndm/scripts/` 目录

#### 3.1 `gds_in_layer_map.*`

**作用：**
- GDS输入层映射文件
- 定义**GDS层号**到**工艺层名**的映射关系

**使用场景：**
- 读取GDS文件时，将GDS层号映射到工艺层
- **必须与TF文件的Metal Stack匹配**

**示例文件名：**
- `gds_in_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB` ← 对应 `12M_3Mx_6Dx_1Gx_2Iz_LB.tf`
- `gds_in_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB` ← 对应 `13M_3Mx_6Dx_2Hx_2Iz_LB.tf`

**关键理解：**
- ✅ **Metal Stack确定 → GDS输入层映射确定**
- ✅ 必须与TF文件的Metal Stack**一一对应**

---

#### 3.2 `gds_out_layer_map.*`

**作用：**
- GDS输出层映射文件
- 定义**工艺层名**到**GDS层号**的映射关系

**使用场景：**
- 输出GDS文件时，将工艺层映射到GDS层号
- **必须与TF文件的Metal Stack匹配**

**示例文件名：**
- `gds_out_layer_map.12M_3Mx_6Dx_1Gx_2Iz_LB` ← 对应 `12M_3Mx_6Dx_1Gx_2Iz_LB.tf`
- `gds_out_layer_map.13M_3Mx_6Dx_2Hx_2Iz_LB` ← 对应 `13M_3Mx_6Dx_2Hx_2Iz_LB.tf`

**关键理解：**
- ✅ **Metal Stack确定 → GDS输出层映射确定**
- ✅ 必须与TF文件的Metal Stack**一一对应**

---

#### 3.3 `block.map`

**作用：**
- Block映射文件
- 定义block级别的映射关系

**使用场景：**
- Block级别的配置
- 工具内部使用

---

### 4. CLF 文件

**位置：** `ndm/sa08.clf`

**作用：**
- **CLF (Cell Library Format)** 文件
- 标准单元库的格式定义文件

**使用场景：**
- 定义标准单元库的格式
- 工具读取库时参考

**特点：**
- 通常每个库有一个CLF文件
- 定义了库的基本结构和格式

---

### 5. Makefile

**位置：** `ndm/Makefile`

**作用：**
- 构建脚本，用于自动化生成NDM
- 定义了生成NDM的规则和步骤

**使用场景：**
- 工具内部使用，用于构建NDM文件
- 用户通常不需要直接使用

---

### 6. README 文件

**位置：** `ndm/README_ndm`

**作用：**
- 说明文档，解释如何使用NDM文件
- 包含NDM的使用说明和注意事项

**使用场景：**
- 用户参考文档
- 了解NDM文件的使用方法

---

## 对于 PR 流程，哪些文件是必需的？

### ICC2/Fusion Compiler 必需文件

**必需文件：**
1. ✅ `ndm/xx_frame_only.ndm/` - NDM数据库（物理信息）
2. ✅ `tf/xx_*.tf` - Technology File（根据Metal Stack选择）

**可选但推荐的文件：**
3. ⚠️ `scripts/icc2_lm_setup.tcl` - ICC2设置脚本（方便配置）
4. ⚠️ `scripts/gds_in_layer_map.*` - GDS层映射（如果需要读取GDS）
5. ⚠️ `scripts/gds_out_layer_map.*` - GDS层映射（如果需要输出GDS）

**不需要的文件：**
- ❌ `scripts/ndmgen_*.tcl` - 生成脚本（工具内部用）
- ❌ `Makefile` - 构建脚本（工具内部用）
- ❌ `README_ndm` - 文档（参考用）

---

## 总结

### NDM目录下的文件分类

| 文件类型 | 用途 | PR必需？ |
|---------|------|---------|
| **NDM数据库** | 物理/时序信息 | ✅ **必需** |
| **Technology File** | 工艺技术定义 | ✅ **必需** |
| **ICC2设置脚本** | 工具配置 | ⚠️ 推荐 |
| **Layer Map** | GDS层映射 | ⚠️ 可选（需要GDS时） |
| **生成脚本** | 工具内部用 | ❌ 不需要 |
| **Makefile** | 构建脚本 | ❌ 不需要 |
| **README** | 文档 | ❌ 不需要 |

**关键理解：**
- **必需**：NDM数据库 + Technology File
- **推荐**：ICC2设置脚本（方便配置）
- **可选**：Layer Map文件（需要GDS时）
- **不需要**：生成脚本、Makefile（工具内部用）

---

## NDM 文件的作用

### 1. 在 PR 流程中的作用

**NDM 文件主要用于 Synopsys 工具（ICC2, Fusion Compiler）**：

| 工具 | 使用的文件格式 | NDM 的作用 |
|------|---------------|-----------|
| **ICC2** | NDM | ✅ 主要使用 NDM 格式 |
| **Fusion Compiler** | NDM | ✅ 主要使用 NDM 格式 |
| **Innovus** | LEF + Liberty | ❌ 不使用 NDM（使用 LEF + .db） |

**关键理解：**
- **NDM** = Synopsys 工具的格式（ICC2, Fusion Compiler）
- **LEF + Liberty** = Cadence 工具的格式（Innovus）
- 两者**功能相同**，只是**格式不同**

### 2. NDM vs LEF + Liberty

| 特性 | NDM | LEF + Liberty |
|------|-----|---------------|
| **格式** | 二进制数据库 | 文本格式 |
| **工具** | Synopsys ICC2, Fusion Compiler | Cadence Innovus |
| **读取速度** | 快（二进制） | 较慢（文本解析） |
| **可读性** | 低（二进制） | 高（文本） |
| **包含信息** | 物理 + 时序 | 物理（LEF）+ 时序（Liberty） |

**类比：**
- **NDM** = 压缩的二进制格式（工具专用）
- **LEF + Liberty** = 文本格式（人类可读）

---

## NDM 文件的内容

### NDM 数据库包含的信息

1. **物理信息**：
   - 标准单元的版图信息（类似 LEF）
   - 金属层、via、pin 位置
   - 单元尺寸、site 信息

2. **时序信息**：
   - 时序模型（类似 Liberty）
   - 延迟、功耗信息
   - PVT corner 信息

3. **其他信息**：
   - 设计规则（DRC）
   - 提取规则（RC extraction）

### Technology File (.tf) 的作用

**Technology File** 定义：
- **金属层**：层数、厚度、宽度规则
- **Via**：via 类型、尺寸
- **设计规则**：最小间距、最小宽度等
- **Metal Stack**：不同 metal stack 配置

**示例文件名解析：**
```
sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
│                        │   │   │   │   │  │
│                        │   │   │   │   │  └─ LB (Low-k Backend)
│                        │   │   │   │   └─ 2Iz (2层 Interconnect)
│                        │   │   │   └─ 1Gx (1层 Global)
│                        │   │   └─ 6Dx (6层 Dense)
│                        │   └─ 3Mx (3层 Metal)
│                        └─ 12M (12层 Metal)
```

---

### Technology File (.tf) vs Tech LEF

**重要理解：`.tf` 文件等效于 Innovus 的 `techlef`！**

| 特性 | Technology File (.tf) | Tech LEF |
|------|----------------------|----------|
| **工具** | Synopsys ICC2, Fusion Compiler | Cadence Innovus |
| **格式** | Synopsys格式（文本） | LEF格式（文本） |
| **功能** | ✅ **完全相同** | ✅ **完全相同** |
| **定义内容** | 金属层、via、设计规则 | 金属层、via、设计规则 |
| **使用场景** | PR流程（ICC2） | PR流程（Innovus） |

**类比：**
- **`.tf`** = Synopsys版本的"Tech LEF"
- **`techlef`** = Cadence版本的"Technology File"
- 两者**功能相同**，只是**格式和工具不同**

**实际使用对比：**

**ICC2 使用 Technology File：**
```tcl
# ICC2 读取 Technology File
set_app_options -name lib.setting.technology_file \
    {/path/to/ndm/tf/sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf}
```

**Innovus 使用 Tech LEF：**
```tcl
# Innovus 读取 Tech LEF
read_lef /path/to/techlef/sa08nvmhlogl22hdf068a_tech.lef
```

**关键理解：**
- ✅ **功能相同**：都定义工艺技术信息
- ✅ **内容相同**：都包含金属层、via、设计规则
- ⚠️ **格式不同**：一个是Synopsys格式，一个是LEF格式
- ⚠️ **工具不同**：一个用于ICC2，一个用于Innovus

**总结：**
> **`.tf` 文件 = Synopsys版本的 Tech LEF**
> 
> 两者功能完全相同，只是格式和工具不同！

---

## 在 PR 流程中的使用

### ICC2 / Fusion Compiler 流程

```tcl
# ICC2 使用 NDM 的示例
set_app_options -name lib.setting.technology_file \
    {/path/to/ndm_mixed/tf/sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf}

set_app_options -name lib.setting.ndm_lib \
    {/path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm}

# 读取 NDM 库
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm
```

### Innovus 流程（不使用 NDM）

```tcl
# Innovus 使用 LEF + Liberty
read_lef /path/to/lef/sa08nvmhlogl22hdf068a.lef
read_liberty /path/to/ccs_lvf/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
```

---

## 对于 lib_config.tcl 生成的影响

### 是否需要包含 NDM 文件？

**取决于使用的 PR 工具：**

| 工具 | 是否需要 NDM？ | 需要什么文件？ |
|------|---------------|---------------|
| **ICC2** | ✅ 需要 | NDM + Technology File |
| **Fusion Compiler** | ✅ 需要 | NDM + Technology File |
| **Innovus** | ❌ 不需要 | LEF + Liberty (.db) |

### 建议

1. **如果项目使用 Innovus**：
   - ❌ 不需要 NDM 文件
   - ✅ 需要 LEF + Liberty (.db) 文件

2. **如果项目使用 ICC2/Fusion Compiler**：
   - ✅ 需要 NDM 文件
   - ✅ 需要 Technology File (.tf)
   - ❌ 可能不需要 LEF + Liberty（取决于工具配置）

3. **通用方案**：
   - 如果库同时提供 NDM 和 LEF + Liberty，可以都包含在 `lib_config.tcl` 中
   - 让用户根据使用的工具选择

---

## NDM 目录类型区别

### 常见的 NDM 目录类型

在库目录中，你可能会看到多种 NDM 相关的目录：

| 目录名 | 用途 | 使用场景 |
|--------|------|---------|
| **`ndm`** | 标准 NDM 格式 | 常规 PR 流程 |
| **`ndm_mixed`** | 混合模式 NDM | 包含多种信息（物理+时序） |
| **`ndm_eval`** | 评估版 NDM | 评估/预览用途 |
| **`ndm_mixed_eval`** | 混合模式评估版 | 评估/预览用途（混合模式） |

### 详细说明

#### 1. `ndm` - 标准 NDM 格式

**特点：**
- 标准的 NDM 数据库格式
- 包含**完整的物理和时序信息**（合并在一起）
- 用于常规的 PR 流程

**使用场景：**
- ICC2/Fusion Compiler 的标准流程
- **生产环境使用**（推荐）

**内容：**
- **物理信息**（版图、pin位置、金属层等）
- **时序信息**（延迟、功耗、PVT corner等）
- **合并在一起**，工具一次性读取

**目录结构示例：**
```
ndm/
├── sa08nvmhlogl22hdf068a.ndm/       # 标准NDM（物理+时序合并）
│   └── reflib.ndm
├── tf/                              # Technology File（可选）
└── scripts/                         # 生成脚本（可选）
```

**ICC2 使用方式：**
```tcl
# 读取标准 NDM（物理+时序合并）
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm/sa08nvmhlogl22hdf068a.ndm
```

**优点：**
- ✅ **简单直接**：一个文件包含所有信息
- ✅ **读取快速**：工具一次性读取，效率高
- ✅ **标准格式**：兼容性最好

**缺点：**
- ⚠️ 文件较大（包含所有信息）
- ⚠️ 如果需要分离物理和时序信息，不够灵活

---

#### 2. `ndm_mixed` - 混合模式 NDM

**特点：**
- **混合模式**（Mixed Mode）
- **分离的物理和时序信息**
- 包含**frame_only**（仅物理）和 **frame_timing**（时序）的**分离文件**

**使用场景：**
- 需要**分别管理**物理和时序信息的场景
- 某些特殊的 PR 流程
- 需要**灵活组合**不同版本的物理和时序信息

**内容：**
- **`frame_only.ndm`** - 仅物理信息（版图、pin位置、金属层等）
- **`frame_timing.ndm`** - 时序信息（延迟、功耗、PVT corner等）
- **分离存储**，工具可以分别读取和组合

**目录结构示例：**
```
ndm_mixed/
├── sa08nvmhlogl22hdf068a_frame_only.ndm/    # 仅物理信息
│   └── reflib.ndm
├── sa08nvmhlogl22hdf068a_frame_timing.ndm/  # 仅时序信息（可选）
│   └── reflib.ndm
├── tf/                                      # Technology File
│   ├── sa08nvmhlogl22hdf068a_12M_3Mx_6Dx_1Gx_2Iz_LB.tf
│   └── ...
├── scripts/                                 # 生成脚本
│   ├── ndmgen_frame_only.tcl
│   ├── ndmgen_frame_timing.tcl
│   └── icc2_lm_setup.tcl
├── README_ndm_mixed                         # 说明文档
├── Makefile                                 # 构建脚本
└── sa08.clf                                 # CLF 文件
```

**ICC2 使用方式：**

**方式1：只使用 frame_only（物理信息）**
```tcl
# 只读取物理信息（frame_only）
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息从 Liberty 文件读取
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
```

**方式2：同时使用 frame_only 和 frame_timing**
```tcl
# 读取物理信息
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a_physical \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 读取时序信息
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a_timing \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_timing.ndm
```

**优点：**
- ✅ **灵活组合**：可以分别使用物理和时序信息
- ✅ **文件较小**：物理和时序分离，文件更小
- ✅ **版本管理**：可以独立更新物理或时序信息
- ✅ **混合使用**：物理用NDM，时序用Liberty，灵活组合

**缺点：**
- ⚠️ 配置较复杂（需要分别读取）
- ⚠️ 需要理解 frame_only 和 frame_timing 的区别

---

### `ndm` vs `ndm_mixed` 详细对比

| 特性 | `ndm` | `ndm_mixed` |
|------|-------|-------------|
| **信息组织** | 物理+时序**合并** | 物理+时序**分离** |
| **文件结构** | 单个NDM文件 | frame_only + frame_timing |
| **读取方式** | 一次性读取 | 可以分别读取 |
| **文件大小** | 较大（包含所有信息） | 较小（分离存储） |
| **灵活性** | 较低（固定组合） | 较高（灵活组合） |
| **配置复杂度** | 简单 | 较复杂 |
| **使用场景** | 标准流程 | 特殊需求 |
| **推荐度** | ✅ **生产推荐** | ⚠️ 特殊需求 |

---

### 实际使用建议

#### 场景1：标准 PR 流程（推荐使用 `ndm`）

```tcl
# 简单直接，推荐用于生产
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm/sa08nvmhlogl22hdf068a.ndm
```

**优点：**
- ✅ 配置简单
- ✅ 一次性读取所有信息
- ✅ 兼容性最好

---

#### 场景2：需要灵活组合（使用 `ndm_mixed`）

**情况A：物理用NDM，时序用Liberty**
```tcl
# 物理信息从NDM读取
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息从Liberty读取（可能更新更频繁）
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_sspg0p585v125c.db
```

**情况B：物理和时序都从NDM读取，但分别管理**
```tcl
# 物理信息
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a_physical \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a_timing \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_timing.ndm
```

**优点：**
- ✅ 可以独立更新物理或时序信息
- ✅ 可以混合使用不同来源的信息
- ✅ 更灵活的组合方式

---

### 关键理解

**`ndm`（标准格式）：**
- **"合并模式"**：物理+时序合并在一起
- **"一站式"**：一个文件包含所有信息
- **"简单直接"**：配置简单，推荐用于生产

**`ndm_mixed`（混合模式）：**
- **"分离模式"**：物理和时序分离存储
- **"灵活组合"**：可以分别读取和组合
- **"特殊需求"**：适用于需要灵活组合的场景

**选择原则：**
- ✅ **标准流程** → 使用 `ndm`（推荐）
- ⚠️ **需要灵活组合** → 使用 `ndm_mixed`
- ⚠️ **物理用NDM，时序用Liberty** → 使用 `ndm_mixed` 的 frame_only

---

### 关键理解：`ndm_mixed` vs `LEF + Liberty` 的本质相同性

**重要发现：`ndm_mixed` 和 `LEF + Liberty` 在信息组织上本质相同！**

| 信息组织方式 | `ndm_mixed` | `LEF + Liberty` |
|-------------|-------------|-----------------|
| **物理信息** | `frame_only.ndm` | `LEF` 文件 |
| **时序信息** | `frame_timing.ndm` | `Liberty/CCS_LVF .db` 文件 |
| **组织方式** | **分离存储** | **分离存储** |
| **读取方式** | 可以分别读取 | 可以分别读取 |
| **格式** | 二进制（NDM） | 文本（LEF + Liberty） |

**本质相同性：**

```
ndm_mixed 的组织方式：
├── frame_only.ndm    (物理信息)  ← 类似 LEF
└── frame_timing.ndm  (时序信息)  ← 类似 Liberty/CCS_LVF .db

LEF + Liberty 的组织方式：
├── *.lef             (物理信息)  ← 类似 frame_only.ndm
└── *.db              (时序信息)  ← 类似 frame_timing.ndm
```

**关键理解：**

1. **信息组织相同**：
   - 都是**物理信息和时序信息分离**
   - 都可以**分别读取和组合**
   - 都支持**灵活的组合方式**

2. **格式不同**：
   - `ndm_mixed` = 二进制格式（NDM）
   - `LEF + Liberty` = 文本格式

3. **工具不同**：
   - `ndm_mixed` = Synopsys 工具（ICC2, Fusion Compiler）
   - `LEF + Liberty` = Cadence 工具（Innovus）

**实际使用对比：**

**使用 `ndm_mixed`（Synopsys ICC2）：**
```tcl
# 物理信息从NDM读取
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息从Liberty读取（或从frame_timing.ndm）
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
```

**使用 `LEF + Liberty`（Cadence Innovus）：**
```tcl
# 物理信息从LEF读取
read_lef /path/to/lef/sa08nvmhlogl22hdf068a.lef

# 时序信息从Liberty读取
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
```

**对比总结：**

| 特性 | `ndm_mixed` | `LEF + Liberty` |
|------|-------------|-----------------|
| **信息组织** | ✅ 物理+时序分离 | ✅ 物理+时序分离 |
| **读取方式** | ✅ 可以分别读取 | ✅ 可以分别读取 |
| **格式** | 二进制（NDM） | 文本（LEF + Liberty） |
| **工具** | Synopsys ICC2/Fusion Compiler | Cadence Innovus |
| **本质** | ✅ **相同**（都是分离模式） | ✅ **相同**（都是分离模式） |

**结论：**

> **`ndm_mixed` 和 `LEF + Liberty` 在信息组织上本质相同！**
> 
> - 都是**物理信息和时序信息分离**
> - 都支持**灵活的组合方式**
> - 只是**格式不同**（二进制 vs 文本）
> - 只是**工具不同**（Synopsys vs Cadence）

**类比：**
- `ndm_mixed` = 二进制版本的"LEF + Liberty"
- `LEF + Liberty` = 文本版本的"ndm_mixed"
- 两者**功能相同**，只是**格式和工具不同**

---

### 实际使用场景：只有 `ndm_mixed` 的情况

**常见情况：**
- 有些库**只有 `ndm_mixed` 目录**，没有 `ndm` 目录
- 这种情况下，`ndm_mixed` 实际上就**相当于标准的 NDM 格式**

**原因：**
- Foundry 可能只提供 `ndm_mixed` 格式
- `ndm_mixed` 更灵活，可以满足不同需求
- 即使只有 `ndm_mixed`，也可以正常使用

**使用方法：**

**情况1：只有 `ndm_mixed`，使用 frame_only + Liberty（推荐）**

```tcl
# 物理信息从 frame_only.ndm 读取
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息从 Liberty 文件读取（标准做法）
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
read_liberty /path/to/liberty/sa08nvmhlogl22hdf068a_sspg0p585v125c.db
```

**情况2：只有 `ndm_mixed`，使用 frame_only + frame_timing**

```tcl
# 物理信息从 frame_only.ndm 读取
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a_physical \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息从 frame_timing.ndm 读取（如果有）
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a_timing \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_timing.ndm
```

**关键理解：**

1. **如果只有 `ndm_mixed`**：
   - ✅ 使用 `frame_only.ndm` 作为物理信息（形状）
   - ✅ 使用 `Liberty .db` 文件作为时序信息（推荐）
   - ✅ 或者使用 `frame_timing.ndm`（如果有，但不常见）

2. **`ndm_mixed` 可以替代 `ndm`**：
   - 如果库只有 `ndm_mixed`，就用 `ndm_mixed`
   - `frame_only.ndm` 的功能等同于标准 `ndm` 的物理部分
   - 配合 `Liberty .db` 文件，功能完全等价

3. **实际使用建议**：
   - ✅ **优先使用 `ndm`**（如果存在）
   - ✅ **如果没有 `ndm`，使用 `ndm_mixed`**（完全可行）
   - ✅ **推荐组合**：`frame_only.ndm` + `Liberty .db`

---

## ⚠️ 重要澄清：NDM使用的两种情况

### 情况1：有 `ndm` 目录（标准格式）

**特点：**
- ✅ **一个NDM文件包含所有信息**（物理+时序合并）
- ✅ **形状信息**（版图、pin位置、金属层等）
- ✅ **时序信息**（延迟、功耗、PVT corner等）
- ✅ **合并在一起**，工具一次性读取

**使用方式：**
```tcl
# 一次性读取所有信息（物理+时序）
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm/sa08nvmhlogl22hdf068a.ndm
```

**优点：**
- ✅ 简单直接，一个文件搞定
- ✅ 配置简单，推荐用于生产

---

### 情况2：没有 `ndm` 目录，只有 `ndm_mixed`（混合模式）

**特点：**
- ⚠️ **物理和时序信息分离**
- ✅ **`frame_only.ndm`** - 仅物理信息（形状）
- ⚠️ **`frame_timing.ndm`** - 仅时序信息（**可选，通常不存在**）

**实际使用方式（推荐）：**
```tcl
# 物理信息从 frame_only.ndm 读取（形状）
read_ndm_lib -lib_name sa08nvmhlogl22hdf068a \
    -ndm_path /path/to/ndm_mixed/sa08nvmhlogl22hdf068a_frame_only.ndm

# 时序信息从 Liberty 文件读取（不是从 frame_timing.ndm）
read_liberty /path/to/ccs_lvf/sa08nvmhlogl22hdf068a_ffpg0p715vn40c.db
read_liberty /path/to/ccs_lvf/sa08nvmhlogl22hdf068a_sspg0p585v125c.db
```

**关键理解：**
- ✅ **`ndm_mixed` 通常只有 `frame_only.ndm`**（形状文件）
- ✅ **时序信息从 `Liberty .db` 文件读取**（不是从 `frame_timing.ndm`）
- ⚠️ **`frame_timing.ndm` 通常不存在**，即使存在也不常用

**为什么时序用 Liberty 而不是 frame_timing.ndm？**
- ✅ `Liberty .db` 文件更常见，每个PVT corner都有
- ✅ `frame_timing.ndm` 通常不存在或很少使用
- ✅ 标准做法是：物理用NDM，时序用Liberty

---

### 总结对比

| 情况 | NDM文件 | 包含信息 | 时序信息来源 |
|------|---------|---------|-------------|
| **情况1：有 `ndm`** | `ndm/xx.ndm/` | ✅ 物理+时序**合并** | ✅ 从NDM文件读取 |
| **情况2：只有 `ndm_mixed`** | `ndm_mixed/xx_frame_only.ndm/` | ✅ 仅物理（形状） | ✅ 从 `Liberty .db` 读取 |

**关键理解：**
1. ✅ **有 `ndm`** → 一个文件包含形状+时序
2. ✅ **只有 `ndm_mixed`** → `frame_only.ndm` 只有形状，时序从 `Liberty .db` 读取
3. ⚠️ **`frame_timing.ndm` 通常不存在**，即使存在也不常用

**总结：**

| 库提供的格式 | 推荐使用方式 |
|-------------|-------------|
| **有 `ndm`** | ✅ 使用 `ndm`（最简单） |
| **只有 `ndm_mixed`** | ✅ 使用 `ndm_mixed` 的 `frame_only.ndm` + `Liberty .db` |
| **两者都有** | ✅ 优先使用 `ndm`，`ndm_mixed` 作为备选 |

**实际建议：**
- 如果库**只有 `ndm_mixed`**，完全没问题，正常使用即可
- 使用 `frame_only.ndm` 作为物理信息，配合 `Liberty .db` 作为时序信息
- 这是**标准做法**，功能完全等价于使用 `ndm`

---

## 📋 实际选择逻辑：如何选择 `reflib.ndm`？

### 选择原则

**优先级顺序：**

1. ✅ **优先使用 `ndm` 目录下的 `reflib.ndm`**
   - 如果 `ndm` 目录存在，优先使用
   - 路径：`ndm/xx.ndm/reflib.ndm` 或 `ndm/xx_frame_only.ndm/reflib.ndm`

2. ✅ **如果没有 `ndm`，使用 `ndm_mixed` 目录下的 `reflib.ndm`**
   - 如果只有 `ndm_mixed` 目录，使用它
   - 路径：`ndm_mixed/xx_frame_only.ndm/reflib.ndm`

### 实际示例（根据你的图片）

**情况1：有 `ndm` 目录**
```
ndm/sa08nvgllogl22hdp068a_frame_only.ndm/reflib.ndm
```
✅ **使用这个文件**

**情况2：没有 `ndm`，只有 `ndm_mixed`**
```
ndm_mixed/sa08nvgllogl22hdp068a_frame_only.ndm/reflib.ndm
```
✅ **使用这个文件**

### 使用方式

**情况1：使用 `ndm` 目录下的 `reflib.ndm`**
```tcl
# 如果 ndm 目录下有合并格式的NDM（包含物理+时序）
read_ndm_lib -lib_name sa08nvgllogl22hdp068a \
    -ndm_path /path/to/ndm/sa08nvgllogl22hdp068a.ndm

# 或者如果 ndm 目录下只有 frame_only（只有物理）
read_ndm_lib -lib_name sa08nvgllogl22hdp068a \
    -ndm_path /path/to/ndm/sa08nvgllogl22hdp068a_frame_only.ndm

# 时序信息从 Liberty 文件读取
read_liberty /path/to/ccs_lvf/sa08nvgllogl22hdp068a_ffpg0p715vn40c.db
```

**情况2：使用 `ndm_mixed` 目录下的 `reflib.ndm`**
```tcl
# 物理信息从 frame_only.ndm 读取
read_ndm_lib -lib_name sa08nvgllogl22hdp068a \
    -ndm_path /path/to/ndm_mixed/sa08nvgllogl22hdp068a_frame_only.ndm

# 时序信息从 Liberty 文件读取
read_liberty /path/to/ccs_lvf/sa08nvgllogl22hdp068a_ffpg0p715vn40c.db
```

### 关键理解

1. ✅ **优先使用 `ndm` 目录**（如果存在）
2. ✅ **如果没有 `ndm`，使用 `ndm_mixed` 目录**
3. ⚠️ **重要区别**：`ndm` 不需要读取 `.db` 文件，`ndm_mixed` 需要读取 `.db` 文件

**选择逻辑总结：**
```
if 存在 ndm 目录:
    使用 ndm/xx.ndm/reflib.ndm 或 ndm/xx_frame_only.ndm/reflib.ndm
elif 存在 ndm_mixed 目录:
    使用 ndm_mixed/xx_frame_only.ndm/reflib.ndm
else:
    报错：找不到NDM文件
```

---

## ⚠️ 重要区别：`ndm` vs `ndm_mixed` 的实际使用差异

### 关键问题：为什么 `ndm` 有优势？

**你的观察是对的！** 如果使用 `ndm_mixed`，确实还是要读取 `.db` 文件。那么 `ndm` 的优势在哪里？

### 对比分析

#### 情况1：使用 `ndm`（标准格式）

**文件需求：**
- ✅ **只需要 NDM 文件**（物理+时序合并）
- ❌ **不需要读取 `.db` 文件**

**使用方式：**
```tcl
# 只需要读取一个NDM文件，包含所有信息（物理+时序）
read_ndm_lib -lib_name sa08nvgllogl22hdp068a \
    -ndm_path /path/to/ndm/sa08nvgllogl22hdp068a.ndm

# ✅ 完成！不需要读取 .db 文件
```

**优势：**
- ✅ **配置简单**：只需要一个文件
- ✅ **读取快速**：一次性读取所有信息
- ✅ **不需要 `.db` 文件**：时序信息已经在NDM里了
- ✅ **二进制格式**：比文本格式（LEF + Liberty）更快

---

#### 情况2：使用 `ndm_mixed`（混合模式）

**文件需求：**
- ✅ **需要 `frame_only.ndm`**（物理信息）
- ✅ **还需要 `.db` 文件**（时序信息，每个PVT corner一个）

**使用方式：**
```tcl
# 1. 读取物理信息（NDM）
read_ndm_lib -lib_name sa08nvgllogl22hdp068a \
    -ndm_path /path/to/ndm_mixed/sa08nvgllogl22hdp068a_frame_only.ndm

# 2. 读取时序信息（Liberty .db 文件，每个PVT corner一个）
read_liberty /path/to/ccs_lvf/sa08nvgllogl22hdp068a_ffpg0p715vn40c.db
read_liberty /path/to/ccs_lvf/sa08nvgllogl22hdp068a_sspg0p585v125c.db
read_liberty /path/to/ccs_lvf/sa08nvgllogl22hdp068a_ttpg0p65v25c.db
# ... 可能需要读取多个 .db 文件
```

**劣势：**
- ⚠️ **配置复杂**：需要读取多个文件
- ⚠️ **需要 `.db` 文件**：必须配合 Liberty 文件使用
- ⚠️ **读取较慢**：需要分别读取多个文件

---

### `ndm` 的优势总结

| 特性 | `ndm`（标准格式） | `ndm_mixed`（混合模式） |
|------|------------------|----------------------|
| **文件数量** | ✅ **1个文件**（NDM） | ⚠️ **多个文件**（NDM + N个.db） |
| **需要 `.db` 文件？** | ❌ **不需要** | ✅ **需要**（每个PVT corner一个） |
| **配置复杂度** | ✅ **简单**（一个命令） | ⚠️ **复杂**（多个命令） |
| **读取速度** | ✅ **快**（一次性读取） | ⚠️ **较慢**（分别读取） |
| **格式** | ✅ **二进制** | ✅ **二进制**（NDM部分） |
| **时序信息来源** | ✅ **从NDM读取** | ⚠️ **从 `.db` 文件读取** |

### 关键理解

**`ndm` 的优势不仅仅是二进制格式！**

1. ✅ **不需要 `.db` 文件**：
   - `ndm`：时序信息已经在NDM里了，**不需要读取 `.db` 文件**
   - `ndm_mixed`：必须读取 `.db` 文件（每个PVT corner一个）

2. ✅ **配置更简单**：
   - `ndm`：一个命令搞定
   - `ndm_mixed`：需要多个命令（NDM + 多个 `.db`）

3. ✅ **读取更快**：
   - `ndm`：一次性读取所有信息
   - `ndm_mixed`：需要分别读取多个文件

4. ✅ **二进制格式**：
   - 两者都是二进制格式，但 `ndm` 的优势在于**信息集中**，不需要额外读取 `.db` 文件

### 实际使用建议

**优先使用 `ndm`（如果存在）：**
- ✅ 配置简单，一个文件搞定
- ✅ **不需要读取 `.db` 文件**
- ✅ 读取更快，一次性完成

**如果没有 `ndm`，使用 `ndm_mixed`：**
- ⚠️ 需要配合 `.db` 文件使用
- ⚠️ 配置较复杂，但功能完全等价

**总结：**
> **`ndm` 的最大优势：不需要读取 `.db` 文件，时序信息已经在NDM里了！**
> 
> 这不仅仅是二进制格式的优势，更是**信息集中**的优势。

---

#### 3. `ndm_eval` - 评估版 NDM

**特点：**
- **评估版**（Evaluation）
- 可能是**简化版本**或**预览版本**
- 用于**评估和预览**，不是完整版本

**使用场景：**
- 评估库的兼容性
- 预览库的内容
- 测试工具支持

**限制：**
- 可能不包含所有标准单元
- 可能不包含所有 PVT corner
- 仅用于评估，不建议用于生产

---

#### 4. `ndm_mixed_eval` - 混合模式评估版

**特点：**
- **混合模式** + **评估版**
- 结合了 `ndm_mixed` 和 `ndm_eval` 的特点
- 用于评估混合模式的功能

**使用场景：**
- 评估混合模式的功能
- 测试混合模式的兼容性
- 预览混合模式的内容

**限制：**
- 评估版本，不建议用于生产

---

### 选择建议

**对于生产环境：**

| 场景 | 推荐目录 | 说明 |
|------|---------|------|
| **标准 PR 流程** | `ndm` | 标准格式，最常用 |
| **需要混合模式** | `ndm_mixed` | 混合模式，包含更多信息 |
| **评估/测试** | `ndm_eval` 或 `ndm_mixed_eval` | 仅用于评估 |

**实际选择：**

1. **优先选择 `ndm`**：
   - 标准格式，兼容性最好
   - 生产环境推荐

2. **如果需要混合模式**：
   - 选择 `ndm_mixed`
   - 根据工具和流程需求

3. **评估/测试时**：
   - 可以使用 `ndm_eval` 或 `ndm_mixed_eval`
   - **不要用于生产**

---

### 目录结构对比

```
标准库目录/
├── ndm/                    # 标准 NDM（推荐用于生产）
│   └── sa08nvmhlogl22hdf068a.ndm/
│
├── ndm_mixed/              # 混合模式 NDM（特殊需求）
│   ├── sa08nvmhlogl22hdf068a_frame_only.ndm/
│   └── sa08nvmhlogl22hdf068a_frame_timing.ndm/
│
├── ndm_eval/               # 评估版 NDM（仅评估用）
│   └── sa08nvmhlogl22hdf068a.ndm/
│
└── ndm_mixed_eval/         # 混合模式评估版（仅评估用）
    └── sa08nvmhlogl22hdf068a_frame_only.ndm/
```

---

## 文件选择建议

### 对于 PR（Place & Route）流程

**Innovus 需要的文件：**
- ✅ LEF 文件（`.lef`）
- ✅ Liberty/CCS_LVF 文件（`.db`）
- ✅ Technology File（`.tf`，可选）
- ❌ NDM 文件（不需要）

**ICC2/Fusion Compiler 需要的文件：**
- ✅ NDM 文件（`.ndm/`）
- ✅ Technology File（`.tf`）
- ✅ LEF 文件（可选，用于兼容性）
- ✅ Liberty 文件（可选，用于兼容性）

---

## 总结

1. **NDM 文件** = Synopsys 工具（ICC2, Fusion Compiler）的数据库格式
2. **功能** = 包含标准单元库的物理和时序信息（类似 LEF + Liberty）
3. **格式** = 二进制数据库（比文本格式更高效）
4. **使用场景** = ICC2/Fusion Compiler PR 流程
5. **对于 lib_config.tcl** = 根据使用的工具决定是否包含

### 核心理解总结

**NDM 的本质：**
- ✅ **NDM = Liberty库的二进制格式版本**
- ✅ **目的**：集中文件（物理+时序合并），配合工具更快
- ✅ **用途**：给 PR（Place & Route）流程提供时序信息

**格式对比：**
- **Liberty (.db)** = 文本格式的时序库
- **NDM (.ndm)** = 二进制格式的时序库（+ 物理信息）
- **两者功能相同**，只是格式不同

**关键理解：**
- NDM 和 LEF + Liberty **功能相同**，只是**格式不同**
- NDM 和 Liberty **本质相同**（都是时序库），只是**格式不同**（二进制 vs 文本）
- 选择哪个取决于**使用的 PR 工具**
- Innovus → LEF + Liberty（文本格式）
- ICC2/Fusion Compiler → NDM（二进制格式，信息集中）

**NDM 的优势：**
1. ✅ **信息集中**：物理+时序合并在一起
2. ✅ **二进制格式**：比文本格式（Liberty）读取更快
3. ✅ **工具优化**：Synopsys 工具对 NDM 格式有专门优化
4. ✅ **配置简单**：一个文件搞定，不需要读取多个 `.db` 文件

