# EDP LibKit - 库配置生成工具

## 概述

EDP LibKit 是一个强大的库配置生成工具，用于从分散的库文件中收集配置信息，生成统一的 `lib_config.tcl` 配置文件。支持多种 foundry 和库类型。

## 核心功能

- ✅ **明确指定库类型**：要求用户明确指定库类型（STD/IP/MEM），确保准确性
- ✅ **批量处理**：支持一次处理多个库，提高效率
- ✅ **安装目录自动展开**：自动检测安装目录中的多个库，无需手动指定每个库
- ✅ **智能库检测**：通过检测视图目录识别库目录，不依赖命名规则
- ✅ **版本选择**：自动选择最新版本，或指定特定版本，或处理所有版本
- ✅ **简化路径**：输出路径简洁，不包含版本目录层级
- ✅ **多库类型支持**：完整支持标准单元库（STD）、IP库、内存库（MEM）
- ✅ **插件化架构**：支持不同 foundry 的适配器（Samsung、SMIC等）
- ✅ **智能版本比较**：正确处理版本号比较（如 `1.00A` vs `1.00B`）
- ✅ **容错处理**：支持不完整的库（缺少部分视图目录），版本提取错误时自动回退

## 安装

```bash
cd edp_center/packages/edp_libkit
pip install -e .
```

## 快速开始

### 基本用法

```bash
# 处理单个STD库（自动选择最新版本）
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/std_library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output

# 批量处理多个库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output

# 处理所有版本（最新版本生成 lib_config.tcl，其他版本生成 lib_config.{version}.tcl）
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --all-versions \
  --output-dir /path/to/output
```

### 版本选择

```bash
# 自动选择最新版本（默认）
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/lib --lib-type STD --node ln08lpu_gp --output-dir /path/to/output

# 指定特定版本
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/lib --lib-type STD --node ln08lpu_gp --version 1.00B --output-dir /path/to/output

# 处理所有版本
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/lib --lib-type STD --node ln08lpu_gp --all-versions --output-dir /path/to/output
```

## 主要特性

### 1. 明确指定库类型

不再进行自动识别，要求用户明确指定库类型，确保准确性：

```bash
--lib-type STD   # 标准单元库
--lib-type IP    # IP库
--lib-type MEM   # 内存库
```

### 2. 批量处理

支持一次处理多个库：

```bash
# 方式1：命令行指定多个路径
--lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3

# 方式2：从文件读取路径列表
--lib-paths-file lib_paths.txt

# 方式3：选择安装目录（自动展开多个库）⭐ 推荐
--lib-path /path/to/0711_install  # 自动检测并处理所有子库
```

**安装目录自动展开**：如果选择的路径包含多个库目录，工具会自动检测并展开为多个库进行处理。详见 [安装目录检测文档](docs/INSTALLATION_DIRECTORY_DETECTION.md)。

### 3. 版本选择

- **默认**：自动选择最新版本
- **指定版本**：`--version 1.00B`
- **所有版本**：`--all-versions`（最新版本生成 `lib_config.tcl`，其他版本生成 `lib_config.{version}.tcl`）

### 4. 简化路径结构

输出路径：`{output_dir}/{lib_name}/lib_config.tcl`

不再包含版本目录层级，路径更简洁。

## 架构设计

### 统一适配器架构

不同 foundry 的目录结构可能不同，但适配器逻辑大部分相同，因此采用统一适配器架构：

- `BaseFoundryAdapter` - 适配器基类，定义接口
- `BaseNodeAdapter` - 通用节点适配器（所有 foundry 共享）
- `FoundryAdapter` - 主适配器，根据 foundry 和 node 创建 `BaseNodeAdapter` 实例
- 配置驱动：每个节点的配置都在 YAML 文件中（`{foundry}/{node_key}.config.yaml`）
- 自动发现：支持的节点列表通过扫描 `*.config.yaml` 文件自动获取

### 工作流程

1. **用户指定库路径和类型**：通过命令行参数明确指定
2. **提取库信息**：从路径中提取库名称、版本等信息
3. **查找视图目录**：根据库类型使用不同的查找逻辑
   - STD库：递归查找 `gds/`, `lef/`, `ccs_lvf/` 等
   - IP库：查找 `FE-Common/` 和 `BE-Common/` 下的视图目录
   - MEM库：查找标准视图目录
4. **版本选择**：自动选择最新版本或使用指定版本
5. **收集文件**：收集各个视图目录中的文件
6. **生成lib_config.tcl**：生成标准化的 lib_config.tcl 文件

## 输出格式

### 输出路径

```
{output_dir}/{lib_name}/lib_config.tcl
```

**示例**：
```
/path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl
```

### 文件内容

生成的 `lib_config.tcl` 文件包含：

- **GDS视图**（多文件格式）：
  ```tcl
  set LIBRARY(cell_name,gds,gds) {/path/to/file1.gds /path/to/file2.gds}
  ```

- **CCS_LVF视图**（单文件格式，包含PVT corner）：
  ```tcl
  set LIBRARY(cell_name,ccs_lvf,sigcmin,ffpg0p715vn40c,db) {/path/to/file.db}
  ```

### 版本文件命名（使用 --all-versions 时）

- **最新版本**：`lib_config.tcl`
- **其他版本**：`lib_config.{version}.tcl`（如 `lib_config.1.00B.tcl`）

所有文件都在同一目录下，便于管理。

## 目录结构

```
edp_libkit/
├── __init__.py
├── cli.py                    # CLI接口
├── generator.py              # 主生成器（LibConfigGenerator）
├── lib_generator.py          # TCL文件生成器（LibGenerator）
├── lib_info.py              # 数据模型（LibInfo, ViewInfo, FileInfo）
├── foundry_adapters/         # Foundry适配器
│   ├── __init__.py
│   ├── base_adapter.py       # 适配器基类接口（BaseFoundryAdapter）
│   ├── base_node_adapter.py  # 通用节点适配器（BaseNodeAdapter）
│   ├── adapter.py            # 主适配器（FoundryAdapter, AdapterFactory）
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
    ├── ARCHITECTURE.md       # 架构文档
    ├── USAGE.md              # 使用指南
    └── ...
```

## 开发

### 添加新的 Foundry

1. 在 `foundry_adapters/` 目录下创建新的 foundry 目录（如 `umc/`）
2. 为每个节点创建 YAML 配置文件（如 `umc/28nm.config.yaml`）
3. 配置文件包含：
   - `node_info`: 节点元数据（name, description, supported_lib_types）
   - `pvt_corner_mapping`: PVT corner 映射规则
   - `standard_view_types`: 视图类型配置（每个库类型需要哪些视图）
   - `view_file_patterns`: 文件模式配置（每个视图类型对应的文件模式）
4. 系统会自动识别新 foundry（通过扫描 `*.config.yaml` 文件）

### 添加新的节点

1. 在 foundry 目录下创建 YAML 配置文件（如 `samsung/ln02lpp.config.yaml`）
2. 配置文件格式与其他节点相同
3. 系统会自动识别新节点（通过扫描 `*.config.yaml` 文件）

**示例配置文件**：
```yaml
# 节点元数据
node_info:
  name: "LN02LPP"
  description: "2nm Low Power Plus"
  supported_lib_types:
    - STD
    - IP
    - MEM

# PVT Corner 映射规则
pvt_corner_mapping:
  ff: sigcmin
  ss: sigcmax
  tt: typical

# 视图类型配置
standard_view_types:
  STD:
    - gds
    - lef
    - ccs_lvf
    # ...

# 文件模式配置
view_file_patterns:
  gds:
    - "*.gds"
  # ...
```

## 完整示例

### 处理STD库

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

### 处理IP库

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/IP/ln08lpu_gpio_1p8v/v1.12 \
  --lib-type IP \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

### 批量处理

```bash
# 从文件读取库路径列表
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file lib_paths.txt \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

## 图形界面（GUI）

不想看文档？使用图形界面！**无需安装，直接运行**：

```bash
cd edp_center/packages/edp_libkit
python run_gui.py
```

或者：

```bash
cd edp_center
python -m packages.edp_libkit.gui
```

GUI特点：
- ✅ 直观易用，无需查看文档
- ✅ 实时显示执行日志
- ✅ 支持批量处理
- ✅ 友好的错误提示

详细说明请查看 [GUI使用指南](GUI_README.md)

## 相关文档

- [GUI使用指南](GUI_README.md) - 图形界面使用说明
- [使用指南](docs/USAGE.md) - 详细的使用说明
- [版本选择](docs/VERSION_SELECTION.md) - 版本选择功能说明
- [批量处理](docs/BATCH_PROCESSING.md) - 批量处理功能说明
- [输出位置](docs/OUTPUT_LOCATION.md) - 输出路径说明
- [架构设计](docs/ARCHITECTURE.md) - 架构设计文档

