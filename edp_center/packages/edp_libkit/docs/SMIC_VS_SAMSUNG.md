# SMIC vs Samsung 处理区别

本文档详细说明 `edp_libkit` 处理 SMIC 和 Samsung 两种 foundry 时的区别。

## 1. 目录结构识别

### Samsung

**识别逻辑**：
- 扫描 `STD_Cell/0711_install/v-logic_*` 目录
- 或者 `STD_Cell/*/v-logic_*` 目录
- 支持 IP 库：`IP/{ip_name}/{version}/`

**目录结构示例**：
```
ori/
├── STD_Cell/
│   └── 0711_install/
│       └── v-logic_sa08nvghlogl20hsf068f/
│           └── DesignWare_logic_libs/
│               └── samsung08nvllg/
│                   └── 20hs/
│                       └── hsf/
│                           └── hvt/
│                               └── 1.01a/
│                                   ├── gds/
│                                   ├── lef/
│                                   ├── liberty/
│                                   │   ├── ccs_lvf/
│                                   │   ├── ccs_power/
│                                   │   └── logic_synth/
│                                   └── verilog/
└── IP/
    └── ln08lpu_gpio_1p8v/
        └── v1.12/
            ├── FE-Common/
            └── BE-Common/
```

### SMIC

**识别逻辑**：
- 递归扫描所有目录
- 每个目录如果包含 `{目录名}.log` 文件，则视为一个库目录
- 支持深层嵌套结构

**目录结构示例**：
```
lib/
├── cell_name/
│   ├── cell_name.log          # 版本信息在这里
│   ├── cell_name.plef          # 根目录文件
│   ├── cell_name.cir
│   ├── cell_name.gds
│   ├── tt0p8v25c/              # PVT 子目录
│   │   ├── cell_name.lib
│   │   └── cell_name.db
│   ├── ffgs_ccb0p88v125c/      # PVT 子目录
│   │   ├── cell_name.lib
│   │   └── cell_name.db
│   └── ssgs_ccw0p72vn40c/      # PVT 子目录
│       ├── cell_name.lib
│       └── cell_name.db
```

## 2. 版本提取方式

### Samsung

**方式**：从路径中提取版本信息

**版本格式**：
- 标准单元库：`1.01a`, `2.00A`（数字.数字字母）
- IP库：`v1.12`（v数字.数字）

**提取逻辑**：
- 递归查找符合版本格式的目录名

### SMIC

**方式**：从 `.log` 文件中提取版本信息

**版本格式**：`1.05`（版本号的前两部分）

**提取逻辑**：
- 查找 `.log` 文件中类似 `"*  Library Format     : Rev: 1.05.00"` 的行
- 提取 `Rev:` 后面的版本号前两部分

## 3. 视图目录结构

### Samsung

**结构**：递归查找视图目录

**视图类型**：
- `gds/` - GDS 文件
- `lef/` - LEF 文件
- `liberty/ccs_lvf/` - CCS LVF 时序库
- `liberty/ccs_power/` - CCS Power 功耗库
- `liberty/logic_synth/` - Logic Synthesis 综合库
- `cdl/` 或 `netlists/lvs/` - CDL 文件
- `verilog/` - Verilog 文件

**特点**：
- 视图文件在各自的子目录中
- Liberty 相关文件在 `liberty/` 下的子目录中

### SMIC

**结构**：根目录文件 + PVT 子目录

**视图类型**：
- **根目录**：
  - `.plef` → `lef`
  - `.cir` → `cdl`
  - `.gds` → `gds`
- **PVT 子目录**（如 `tt0p8v25c`, `ffgs_ccb0p88v125c`）：
  - `.lib` → `lib`
  - `.db` → `db`

**特点**：
- 根目录直接包含视图文件
- PVT corner 作为子目录名
- 每个 PVT 目录包含对应的 `.lib` 和 `.db` 文件

## 4. lib_config.tcl 格式

### Samsung

**格式**：`LIBRARY(cell_name,view_type,rc_corner,pvt_corner,file_type)`

**示例**：
```tcl
# 多文件格式（GDS、LEF等）
set LIBRARY(sa08nvghlogl20hsf068f,gds,gds) {
    /path/to/file1.gds /path/to/file2.gds
}

# 单文件格式（Liberty相关）
set LIBRARY(sa08nvghlogl20hsf068f,ccs_lvf,sigcmin,ffpg0p825vn40c,db) {
    /path/to/sa08nvghlogl20hsf068f_ffpg0p825vn40c.db
}

set LIBRARY(sa08nvghlogl20hsf068f,ccs_lvf,typical,tt0p75v125c,lib) {
    /path/to/sa08nvghlogl20hsf068f_tt0p75v125c.lib.gz
}
```

**特点**：
- 使用 `LIBRARY` 数组（可通过 `--array-name` 自定义）
- 包含 `view_type`（实际的目录名）
- PVT corner 直接从文件名提取

### SMIC

**格式**：`LIBRARY(cell_name,rc_corner,libcorner,file_type)`

**示例**：
```tcl
# 根目录文件
set LIBRARY(cell_name,lef) {/path/to/cell_name.plef}
set LIBRARY(cell_name,cdl) {/path/to/cell_name.cir}
set LIBRARY(cell_name,gds) {/path/to/cell_name.gds}

# PVT 子目录文件
set LIBRARY(cell_name,CMINccbest,ff0p88vn50c,lib) {
    /path/to/ffgs_ccb0p88vn40c/cell_name.lib
}

set LIBRARY(cell_name,CMAXccworst,ss0p72vn50c,db) {
    /path/to/ssgs_ccw0p72vn40c/cell_name.db
}

set LIBRARY(cell_name,typical,tt0p8v25c,lib) {
    /path/to/tt0p8v25c/cell_name.lib
}
```

**特点**：
- 使用 `LIBRARY` 数组（默认，可通过 `--array-name` 自定义）
- 不包含 `view_type`（文件类型通过扩展名区分）
- infoMap 映射在工具内部处理，不需要写入文件
- PVT corner 从子目录名提取，需要映射到 libCorner

## 5. RC_CORNER 映射规则

### Samsung

| PVT Corner 前缀 | rc_corner | 说明 |
|----------------|-----------|------|
| `ff*` | `sigcmin` | Fast-Fast, best case |
| `ss*` | `sigcmax` | Slow-Slow, worst case |
| `tt*` | `typical` | Typical case |

**示例**：
- `ffpg0p825vn40c` → `sigcmin`
- `sspg0p675v125c` → `sigcmax`
- `tt0p75v125c` → `typical`

**特点**：
- 直接从 PVT corner 名称前缀判断
- 支持 PVVT 格式（dual rail level shifter）

### SMIC

| PVT Corner 前缀 | rc_corner | 说明 |
|----------------|-----------|------|
| `ffgs*` | `CMINccbest` | Fast-Fast, best case |
| `ssgs*` | `CMAXccworst` | Slow-Slow, worst case |
| `tt*` | `typical` | Typical case |

**示例**：
- `ffgs_ccb0p88vn40c` → `CMINccbest`
- `ssgs_ccw0p72vn40c` → `CMAXccworst`
- `tt0p8v25c` → `typical`

**特点**：
- 需要检查更长的前缀（`ffgs`, `ssgs`）
- RC_CORNER 值使用大写（`CMINccbest`, `CMAXccworst`）

## 6. PVT Corner 处理

### Samsung

**提取方式**：从文件名中提取

**格式**：
- 普通库：`ffpg0p825vn40c`（PVT）
- Level Shifter：`ffpg0p8v0p9v125c`（PVVT，双电源轨）

**处理**：
- 直接从文件名提取完整的 PVT corner 字符串
- 不需要额外的映射

### SMIC

**提取方式**：从 PVT 子目录名提取

**格式**：
- `tt0p8v25c`
- `ffgs_ccb0p88v125c`
- `ssgs_ccw0p72vn40c`

**处理**：
- 从子目录名提取 PVT corner
- **需要映射到 libCorner**：
  - `ffgs_ccb0p88vn40c` → `ff0p88vn50c`（`vn40c` → `vn50c`）
  - `ssgs_ccw0p72vn40c` → `ss0p72vn50c`（`vn40c` → `vn50c`）
  - `tt0p8v25c` → `tt0p8v25c`（保持不变）

**infoMap 条目**：
- 生成 `set infoMap(view,PVT,libCorner) "libcorner"` 条目
- 用于工具查找 PVT corner 对应的 libCorner

## 7. 文件类型识别

### Samsung

**方式**：通过目录结构识别

- `gds/` → GDS 文件
- `lef/` → LEF 文件
- `ccs_lvf/` → CCS LVF 时序库
- `ccs_power/` → CCS Power 功耗库
- `logic_synth/` → Logic Synthesis 综合库
- `cdl/` 或 `netlists/lvs/` → CDL 文件

### SMIC

**方式**：通过文件扩展名识别

- `.plef` → `lef`
- `.cir` → `cdl`
- `.gds` → `gds`
- `.lib` → `lib`
- `.db` → `db`

## 8. 默认数组名

### Samsung

**默认**：`LIBRARY`

**示例**：
```tcl
set LIBRARY(cell_name,view_type,rc_corner,pvt_corner,file_type) {...}
```

### SMIC

**默认**：`MEM_LIBRARY`

**示例**：
```tcl
set LIBRARY(cell_name,rc_corner,libcorner,file_type) {...}
```

**注意**：两者都支持通过 `--array-name` 参数自定义数组名，默认都是 `LIBRARY`。

## 9. 使用示例

### Samsung

```bash
# 扫描整个 ori 目录
edp-libkit gen-lib --foundry Samsung -o /path/to/ori

# 处理单个库目录
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/v-logic_xxx

# 自定义数组名
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/v-logic_xxx --array-name MY_LIBRARY
```

### SMIC

```bash
# 处理单个库目录
edp-libkit gen-lib --foundry SMIC --lib-path /path/to/lib/cell_name

# 扫描包含多个库的目录（支持深层结构）
edp-libkit gen-lib --foundry SMIC -o /path/to/libs

# 自定义数组名
edp-libkit gen-lib --foundry SMIC --lib-path /path/to/lib/cell_name --array-name MY_LIBRARY
```

## 10. 总结对比表

| 特性 | Samsung | SMIC |
|------|---------|------|
| **目录结构** | 深层嵌套（`STD_Cell/*/v-logic_*`） | 扁平结构（根目录 + PVT 子目录） |
| **版本提取** | 从路径提取 | 从 `.log` 文件提取 |
| **视图目录** | 递归查找子目录 | 根目录文件 + PVT 子目录 |
| **lib_config.tcl 格式** | `LIBRARY(cell_name,view_type,rc_corner,pvt_corner,file_type)` | `LIBRARY(cell_name,rc_corner,libcorner,file_type)` |
| **数组名默认值** | `LIBRARY` | `LIBRARY`（统一） |
| **RC_CORNER 值** | `sigcmin`, `sigcmax`, `typical`（小写） | `CMINccbest`, `CMAXccworst`, `typical`（部分大写） |
| **PVT Corner 来源** | 文件名 | 子目录名 |
| **libCorner 映射** | 不需要 | 需要（`map_pvt_to_libcorner`，内部处理） |
| **infoMap 条目** | 不需要 | 不需要（内部处理） |
| **目录扫描** | 递归扫描深层结构 | 递归扫描深层结构 |
| **文件类型识别** | 通过目录结构 | 通过文件扩展名 |
| **支持 Level Shifter** | 是（PVVT 格式） | 否（当前实现） |

## 11. 代码实现位置

### Samsung

- **适配器**：`foundry_adapters/samsung_adapter.py`
- **格式生成**：`lib_generator.py` → `_generate_single_file_entries_samsung()`

### SMIC

- **适配器**：`foundry_adapters/smic_adapter.py`
- **格式生成**：`lib_generator.py` → `_generate_smic_format()`

