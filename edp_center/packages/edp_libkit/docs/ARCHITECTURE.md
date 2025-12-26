# EDP LibKit 架构和逻辑说明

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI 入口层                              │
│                   (cli.py)                                  │
│  - 解析命令行参数                                            │
│  - 调用生成器                                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   生成器协调层                                │
│              (LibConfigGenerator)                           │
│  - 协调适配器和生成器                                         │
│  - 管理整个工作流程                                           │
│  - 处理版本选择逻辑                                           │
└───────┬───────────────────────────────┬─────────────────────┘
        │                               │
        ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│   适配器层        │          │   TCL生成器层     │
│ (FoundryAdapter)  │          │  (LibGenerator)   │
│                  │          │                  │
│ - 查找视图目录    │          │ - 生成TCL格式     │
│ - 提取库信息      │          │ - 格式化输出      │
│ - PVT corner映射 │          │                  │
└──────────────────┘          └──────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   数据模型层                                  │
│                    (LibInfo)                                 │
│  - LibInfo: 库基本信息                                        │
│  - ViewInfo: 视图信息                                        │
│  - FileInfo: 文件信息                                        │
└─────────────────────────────────────────────────────────────┘
```

## 二、核心组件

### 1. CLI 层 (`cli.py`)
**职责**：命令行接口，解析用户输入

**主要功能**：
- 解析命令行参数（foundry, node, lib-path, lib-type等）
- 创建 `LibConfigGenerator` 实例
- 调用相应的生成方法
- 输出结果和错误信息

**必需参数**：
- `--foundry`: Foundry名称（Samsung, SMIC, TSMC）
- `--lib-path` 或 `--lib-paths-file`: 库目录路径（可指定多个）
- `--lib-type`: 库类型（STD, IP, MEM）
- `--node`: 工艺节点（如 ln08lpu_gp, n7, n5）
- `--output-dir`: 输出目录（必需）

**可选参数**：
- `--version`: 指定特定版本
- `--all-versions`: 处理所有版本
- `--array-name`: TCL数组变量名（默认：LIBRARY）

### 2. 生成器协调层 (`generator.py` - `LibConfigGenerator`)
**职责**：协调各个组件，管理整个工作流程

**核心方法**：
- `generate_from_directory()`: 从指定目录生成配置（指定库类型和版本）
- `generate_all_versions()`: 处理所有版本，生成多个配置文件

**工作流程**：
```
1. 创建适配器（根据foundry和node）
2. 提取库信息（从路径中提取名称、版本等）
3. 查找视图目录（根据库类型使用不同的查找逻辑）
4. 收集文件（使用适配器的文件模式匹配）
5. 确定输出路径（简化路径结构）
6. 生成lib_config.tcl（使用LibGenerator）
```

### 3. 适配器层 (`foundry_adapters/`)

#### 3.1 适配器架构（简化后）

```
FoundryAdapter (统一入口)
    │
    └── BaseNodeAdapter (通用节点适配器)
            │
            ├── Samsung节点（通过foundry参数区分）
            ├── SMIC节点
            └── TSMC节点
```

**关键变化**：
- ✅ **统一适配器**：所有 foundry 使用同一个 `BaseNodeAdapter`，通过 `foundry` 参数区分
- ✅ **YAML 配置**：每个节点的配置都在 `{node_key}.config.yaml` 文件中
- ✅ **自动发现**：支持的节点列表通过扫描 `*.config.yaml` 文件自动获取
- ❌ **不再需要**：`nodes.py`、`__init__.py`、foundry 特定的 `base_node_adapter.py`

#### 3.2 配置文件结构

每个节点的配置都在一个 YAML 文件中：`foundry_adapters/{foundry}/{node_key}.config.yaml`

**配置文件内容**：
```yaml
# 节点元数据
node_info:
  name: "LN08LPU_GP"
  description: "8nm Low Power Ultra General Purpose"
  supported_lib_types:
    - STD
    - IP
    - MEM

# PVT Corner 映射规则
pvt_corner_mapping:
  ff: sigcmin    # fast-fast → best case
  ss: sigcmax    # slow-slow → worst case
  tt: typical    # typical → typical

# 第一张表：定义每个库类型需要哪些视图类型
standard_view_types:
  STD:
    - gds
    - lef
    - ccs_lvf
    - ccs_power
    - logic_synth
    - cdl
    - verilog
  IP:
    - gds
    - lef
    - liberty
    - ibis
    - model
    - symbol
  MEM:
    - gds
    - lef
    - liberty
    - verilog
    - spice

# 第二张表：定义每个视图类型对应的文件匹配模式
view_file_patterns:
  gds:
    - "*.gds"
  lef:
    - "*.lef"
  ccs_lvf:
    - "*.db"
    - "*.db_ccs_tn_lvf_dths"
    - "*.lib_ccs_tn_lvf_dths.gz"
    - "*.lib_ccs_tn_lvf_dths"
  # ... 其他视图类型
```

#### 3.3 适配器核心方法

**`find_view_directories(lib_path, lib_type, version)`**
- 在库目录中查找视图类型目录
- 返回 `Dict[str, Path]`，例如：`{'gds': Path(...), 'lef': Path(...)}`
- STD库：递归查找 `gds/`, `lef/`, `liberty/ccs_lvf/` 等
- IP库：查找 `FE-Common/` 和 `BE-Common/` 下的视图目录
- MEM库：查找 `gds/`, `lef/`, `liberty/` 等
- 支持版本参数，可以只查找特定版本的目录

**`extract_lib_info(lib_path)`**
- 从路径提取库信息（名称、版本、类型等）
- 返回 `LibInfo` 对象
- 注意：库类型由用户通过命令行参数指定，不再自动判断

**`get_standard_view_types(lib_type)`**
- 从 YAML 配置中获取指定库类型的标准视图类型列表
- 返回视图类型列表，如 `['gds', 'lef', 'ccs_lvf', ...]`

**`get_view_file_pattern(view_type)`**
- 从 YAML 配置中获取视图类型的文件匹配模式
- 支持返回单个模式字符串或模式列表
- 例如：`'*.gds'` 或 `['*.db', '*.db_ccs_tn_lvf_dths', '*.lib_ccs_tn_lvf_dths.gz']`

**`extract_rc_corner(pvt_corner)`**
- 从PVT corner名称提取RC corner（sigcmin/sigcmax/typical）
- 使用 YAML 配置中的 `pvt_corner_mapping` 规则
- Samsung 使用 `startswith` 匹配（支持 'ff', 'ffgs' 等变体）
- SMIC/TSMC 使用精确匹配

### 4. TCL生成器层 (`lib_generator.py` - `LibGenerator`)
**职责**：生成标准化的 `lib_config.tcl` 文件

**核心方法**：
- `generate()`: 主生成方法，根据库信息和视图文件生成TCL配置

**支持的格式**：

**多文件格式**（如GDS, LEF）：
```tcl
set LIBRARY(cell_name,gds,gds) {/path/to/file1.gds /path/to/file2.gds}
```

**单文件格式**（如CCS_LVF, Liberty）：
```tcl
set LIBRARY(cell_name,ccs_lvf,rc_corner,pvt_corner,file_type) {/path/to/file.db}
```

**SMIC特殊格式**：
```tcl
set LIBRARY(cell_name,rc_corner,libcorner,file_type) {/path/to/file.lib}
```

### 5. 数据模型层 (`lib_info.py`)

**LibInfo**：库基本信息
- `lib_name`: 库名称
- `lib_path`: 库路径
- `lib_type`: 库类型（STD/IP/MEM）
- `version`: 版本信息
- `foundry`: Foundry名称
- `node`: 工艺节点
- `views`: 视图信息字典

**ViewInfo**：视图信息
- `view_type`: 视图类型（gds, lef, ccs_lvf等）
- `view_path`: 视图目录路径
- `files`: 文件列表
- `pvt_corners`: 支持的PVT corners

**FileInfo**：文件信息
- `file_path`: 文件路径
- `file_type`: 文件类型
- `pvt_corner`: PVT corner
- `rc_corner`: RC corner
- `checksum`: 文件校验和

## 三、完整工作流程

### 场景1：处理单个库（默认使用最新版本）

```
用户命令：
  edp-libkit gen-lib \
    --foundry Samsung \
    --lib-path /path/to/library_dir \
    --lib-type STD \
    --node ln08lpu_gp \
    --output-dir /path/to/output

执行流程：
1. CLI解析参数
   └─> 创建 LibConfigGenerator(foundry='Samsung', node='ln08lpu_gp', output_base_dir=...)

2. LibConfigGenerator.generate_from_directory(lib_path, lib_type='STD')
   ├─> 创建适配器：AdapterFactory.create_adapter('Samsung', 'ln08lpu_gp')
   │   └─> FoundryAdapter -> BaseNodeAdapter('samsung', 'ln08lpu_gp')
   │       └─> 加载配置：foundry_adapters/samsung/ln08lpu_gp.config.yaml
   │
   ├─> 提取库信息：adapter.extract_lib_info(lib_path)
   │   └─> 设置 lib_info.lib_type = 'STD'（覆盖）
   │   └─> 提取版本：自动选择最新版本（如 '2.00A'）
   │
   ├─> 查找视图目录：adapter.find_view_directories(lib_path, lib_type='STD', version='2.00A')
   │   ├─> 根据 lib_type 使用相应的查找逻辑
   │   ├─> STD库：递归查找 gds/, lef/, liberty/ccs_lvf/ 等
   │   └─> 返回 Dict[view_type, view_path]
   │
   ├─> 收集文件：_collect_files(view_dirs)
   │   ├─> 对每个视图类型，使用 adapter.get_view_file_pattern()
   │   ├─> 支持多个文件模式（如 ccs_lvf: ['*.db', '*.db_ccs_tn_lvf_dths', ...]）
   │   └─> 使用 glob 查找匹配的文件
   │   └─> 返回 Dict[view_type, List[Path]]
   │
   ├─> 确定输出路径：_determine_output_path(lib_info)
   │   └─> {output_dir}/{lib_name}/lib_config.tcl
   │   └─> 示例：/path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl
   │
   └─> 生成TCL：lib_generator.generate(lib_info, view_files, output_path, adapter)
       ├─> 根据视图类型选择格式（多文件/单文件）
       ├─> 提取PVT corner和RC corner（使用 adapter.extract_rc_corner()）
       └─> 生成TCL条目并写入文件
```

### 场景2：处理所有版本

```
用户命令：
  edp-libkit gen-lib \
    --foundry Samsung \
    --lib-path /path/to/library_dir \
    --lib-type STD \
    --node ln08lpu_gp \
    --all-versions \
    --output-dir /path/to/output

执行流程：
1. CLI解析参数
   └─> 创建 LibConfigGenerator

2. LibConfigGenerator.generate_all_versions(lib_path, lib_type='STD')
   ├─> 查找所有版本：adapter._node_adapter._find_all_versions(lib_path)
   │   └─> 返回版本列表：['2.00A', '1.01a', '1.0']
   │
   ├─> 确定最新版本：adapter._node_adapter._get_latest_version(versions)
   │   └─> 返回：'2.00A'
   │
   └─> 对每个版本：
       ├─> 提取库信息：adapter.extract_lib_info(lib_path)
       │   └─> 设置 lib_info.version = 当前版本
       │
       ├─> 查找视图目录：adapter.find_view_directories(lib_path, lib_type='STD', version=当前版本)
       │
       ├─> 收集文件：_collect_files(view_dirs)
       │
       ├─> 确定输出文件名：
       │   ├─> 最新版本：lib_config.tcl
       │   └─> 其他版本：lib_config.{version}.tcl（如 lib_config.1.00B.tcl）
       │
       └─> 生成TCL：lib_generator.generate(...)
           └─> 所有版本的文件都在 {output_dir}/{lib_name}/ 目录下
```

## 四、关键设计决策

### 1. 统一适配器架构
**原因**：不同 foundry 的适配器逻辑大部分相同，只有配置不同

**实现**：
- 使用通用的 `BaseNodeAdapter`，通过 `foundry` 参数区分
- 所有配置都在 YAML 文件中，易于维护和扩展
- 添加新节点只需创建一个 YAML 配置文件

### 2. YAML 配置驱动
**原因**：配置与代码分离，更易维护

**实现**：
- 每个节点的配置都在 `{node_key}.config.yaml` 文件中
- 包含：节点元数据、PVT corner映射、视图类型、文件模式
- 支持节点自动发现（通过扫描 YAML 文件）

### 3. 明确指定库类型
**原因**：不同库类型的目录结构不同，自动识别不可靠

**实现**：
- 要求用户通过 `--lib-type` 参数明确指定
- 适配器根据库类型使用相应的查找逻辑
- 不再依赖目录命名约定

### 4. 简化输出路径
**原因**：减少目录层级，便于使用

**实现**：
- 输出路径：`{output_dir}/{lib_name}/lib_config.tcl`
- 不再包含 `{foundry}/{lib_type}/{version}` 层级
- 使用 `--all-versions` 时，所有版本文件在同一目录下

### 5. 智能版本选择
**原因**：库目录可能包含多个版本，需要智能选择

**实现**：
- 默认：自动选择最新版本
- `--version`：指定特定版本
- `--all-versions`：处理所有版本
- 版本比较支持 `1.00A` vs `1.00B` 等格式

## 五、目录结构

```
edp_libkit/
├── __init__.py
├── cli.py                    # CLI接口
├── generator.py              # 主生成器（LibConfigGenerator）
├── lib_generator.py          # TCL文件生成器（LibGenerator）
├── lib_info.py              # 数据模型（LibInfo, ViewInfo, FileInfo）
├── foundry_adapters/         # Foundry适配器
│   ├── __init__.py
│   ├── interface.py          # 适配器接口定义（BaseFoundryAdapter）
│   ├── foundry_adapter.py    # Foundry适配器（FoundryAdapter, AdapterFactory）
│   ├── node_adapter.py       # 节点适配器实现（BaseNodeAdapter）
│   ├── samsung/              # Samsung 配置文件目录
│   │   ├── ln08lpu_gp.config.yaml
│   │   ├── ln08lpu_hp.config.yaml
│   │   ├── ln05lpe.config.yaml
│   │   ├── ln04lpp.config.yaml
│   │   └── ln03lpp.config.yaml
│   ├── smic/                 # SMIC 配置文件目录
│   │   ├── n7.config.yaml
│   │   ├── n12.config.yaml
│   │   ├── n14.config.yaml
│   │   └── n28.config.yaml
│   └── tsmc/                 # TSMC 配置文件目录
│       ├── n5.config.yaml
│       ├── n3.config.yaml
│       ├── n7.config.yaml
│       └── n16.config.yaml
└── docs/                     # 文档目录
    ├── ARCHITECTURE.md       # 架构文档（本文件）
    ├── USAGE.md              # 使用指南
    ├── BATCH_PROCESSING.md   # 批量处理说明
    ├── VERSION_SELECTION.md  # 版本选择说明
    └── ...
```

## 六、扩展点

### 添加新的 Foundry

1. 在 `foundry_adapters/` 下创建新的 foundry 目录（如 `umc/`）
2. 为每个节点创建 YAML 配置文件（如 `umc/28nm.config.yaml`）
3. 配置文件包含：
   - `node_info`: 节点元数据
   - `pvt_corner_mapping`: PVT corner 映射规则
   - `standard_view_types`: 视图类型配置
   - `view_file_patterns`: 文件模式配置
4. 系统会自动识别新 foundry（通过扫描 `*.config.yaml` 文件）

### 添加新的节点

1. 在 foundry 目录下创建 YAML 配置文件（如 `samsung/ln02lpp.config.yaml`）
2. 配置文件格式与其他节点相同
3. 系统会自动识别新节点（通过扫描 `*.config.yaml` 文件）

### 添加新的视图类型

1. 在节点的 YAML 配置文件中添加视图类型：
   ```yaml
   standard_view_types:
     STD:
       - gds
       - lef
       - new_view_type  # 新增视图类型
   ```
2. 添加文件模式：
   ```yaml
   view_file_patterns:
     new_view_type:
       - "*.new"
   ```
3. 在适配器的 `find_view_directories` 中添加识别逻辑（如果需要特殊处理）

## 七、关键文件说明

| 文件 | 职责 |
|------|------|
| `cli.py` | 命令行接口，参数解析 |
| `generator.py` | 主生成器，协调工作流程 |
| `lib_generator.py` | TCL文件生成器 |
| `lib_info.py` | 数据模型定义 |
| `foundry_adapters/interface.py` | 适配器接口定义 |
| `foundry_adapters/foundry_adapter.py` | Foundry适配器（统一入口和工厂） |
| `foundry_adapters/node_adapter.py` | 节点适配器实现（所有 foundry 共享） |
| `foundry_adapters/{foundry}/{node_key}.config.yaml` | 节点配置文件（YAML格式） |

## 八、总结

**核心思想**：
1. **统一适配器**：所有 foundry 使用同一个 `BaseNodeAdapter`，通过配置区分
2. **配置驱动**：所有节点配置都在 YAML 文件中，易于维护和扩展
3. **明确指定**：要求用户明确指定库类型，避免自动识别的不可靠性
4. **简化路径**：输出路径简洁，便于使用

**工作流程**：
提取库信息 → 查找视图目录 → 收集文件 → 生成TCL配置

**关键特性**：
- ✅ 支持多种库类型（STD/IP/MEM）
- ✅ 支持多种 foundry 和节点（Samsung, SMIC, TSMC）
- ✅ YAML 配置驱动，易于扩展
- ✅ 智能版本选择和比较
- ✅ 批量处理支持
- ✅ 生成标准化的TCL配置文件
