# EDP LibKit 使用指南

## 概述

EDP LibKit 是一个库配置生成工具，用于扫描库目录并生成 `lib_config.tcl` 配置文件。

**重要**：现在要求用户明确指定库路径和类型，不再进行自动识别。

## 基本用法

### 必需参数

所有命令都需要以下参数：

- `--foundry`: Foundry名称（必需），如 `Samsung`, `SMIC`
- `--lib-path` 或 `--lib-paths-file`: 库目录路径（必需，可以指定多个）
- `--lib-type`: 库类型（必需），可选值：`STD`, `IP`, `MEM`
- `--node`: 工艺节点（必需），如 `ln08lpu_gp`

### 基本命令格式

**单个库**：
```bash
edp-libkit gen-lib \
  --foundry <foundry_name> \
  --lib-path <library_directory> \
  --lib-type <STD|IP|MEM> \
  --node <node_name>
```

**多个库（批量处理）**：
```bash
edp-libkit gen-lib \
  --foundry <foundry_name> \
  --lib-path <lib1> <lib2> <lib3> \
  --lib-type <STD|IP|MEM> \
  --node <node_name>
```

**从文件读取库列表**：
```bash
edp-libkit gen-lib \
  --foundry <foundry_name> \
  --lib-paths-file <path_list_file> \
  --lib-type <STD|IP|MEM> \
  --node <node_name>
```

## 使用示例

### 示例1：处理STD库

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /tech_1/designkit/Samsung/LN08LPU_GP/ori/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp
```

**注意**：即使目录名不是 `v-logic_` 开头也可以，只要明确指定 `--lib-type STD` 即可。

### 示例2：处理IP库

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /tech_1/designkit/Samsung/LN08LPU_GP/ori/IP/ln08lpu_gpio_1p8v/v1.12 \
  --lib-type IP \
  --node ln08lpu_gp
```

### 示例3：处理MEM库

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /tech_1/designkit/Samsung/LN08LPU_GP/ori/mem_compiler/sram_xxx \
  --lib-type MEM \
  --node ln08lpu_gp
```

### 示例4：批量处理多个库

```bash
# 方式1：命令行指定多个路径
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path \
    /path/to/lib1 \
    /path/to/lib2 \
    /path/to/lib3 \
  --lib-type STD \
  --node ln08lpu_gp

# 方式2：从文件读取路径列表
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file /path/to/lib_paths.txt \
  --lib-type STD \
  --node ln08lpu_gp
```

### 示例5：指定特定版本

```bash
# 使用特定版本（如 1.00B）
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --version 1.00B \
  --output-dir /path/to/output
```

### 示例6：处理所有版本

```bash
# 处理库目录下的所有版本（每个版本生成一个配置文件）
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --all-versions \
  --output-dir /path/to/output
```

### 示例7：指定输出目录

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

### 示例5：指定数组变量名

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --array-name MEM_LIBRARY
```

## 参数说明

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `--foundry` | ✅ | Foundry名称 | `Samsung`, `SMIC` |
| `--lib-path` | ✅ | 库目录路径 | `/path/to/library` |
| `--lib-type` | ✅ | 库类型 | `STD`, `IP`, `MEM` |
| `--node` | ✅ | 工艺节点 | `ln08lpu_gp` |
| `--version` | ❌ | 指定版本号 | `2.00A`, `1.00B` |
| `--all-versions` | ❌ | 处理所有版本 | - |
| `--output-dir` | ✅ | 输出目录（必需） | `/path/to/output` |
| `--array-name` | ❌ | TCL数组变量名 | `LIBRARY`（默认） |
| `--verbose` / `-v` | ❌ | 显示详细日志 | - |

**版本选择说明**：
- 默认：自动选择最新版本
- `--version`：指定特定版本（如 `--version 1.00B`）
- `--all-versions`：处理所有版本（每个版本生成一个配置文件）
- `--version` 和 `--all-versions` 不能同时使用

## 为什么需要明确指定？

### 1. 目录命名不统一
- 不是所有STD库都以 `v-logic_` 开头
- 不同foundry的命名规则可能不同
- 用户自定义的目录名可能不符合标准

### 2. 更可靠
- 明确指定避免了误识别
- 用户可以完全控制处理哪些库
- 减少因自动识别失败导致的错误

### 3. 更灵活
- 支持任意目录结构
- 不依赖特定的命名约定
- 用户可以处理非标准目录

## 库类型说明

### STD（标准单元库）
- 通常包含：`gds/`, `lef/`, `liberty/ccs_lvf/` 等视图目录
- 适配器会递归查找这些目录

### IP（IP库）
- 通常包含：`FE-Common/` 和 `BE-Common/` 目录
- 适配器会在这些目录下查找视图

### MEM（内存库）
- 通常包含：`gds/`, `lef/`, `liberty/` 等视图目录
- 适配器会查找这些标准视图目录

## 输出格式

生成的 `lib_config.tcl` 文件会保存在：

**路径结构**：
```
{output_dir}/{lib_name}/lib_config.tcl
```

**注意**：
- `--output-dir` 是必需参数，必须指定
- 路径结构已简化，不包含版本目录层级
- 使用 `--all-versions` 时：
  - 最新版本生成：`lib_config.tcl`
  - 其他版本生成：`lib_config.{version}.tcl`（如 `lib_config.1.00B.tcl`，使用点分隔）
- 所有版本的文件都在同一目录下（`{output_dir}/{lib_name}/`）
- 不再自动包含 `{foundry}/{lib_type}` 层级
- 如果需要在输出目录中区分类型，可以在 `--output-dir` 中包含这些信息
  - 例如：`--output-dir /path/to/Samsung/STD` 会输出到 `/path/to/Samsung/STD/{lib_name}/lib_config.tcl`

## 常见问题

### Q: 为什么必须指定库类型？
A: 因为不同库类型的目录结构不同，适配器需要知道使用哪种查找逻辑。而且目录命名可能不统一，自动识别不可靠。

### Q: 如果目录名不是标准格式怎么办？
A: 没问题！只要明确指定 `--lib-type`，工具会根据库类型查找视图目录，不依赖目录名。

### Q: 可以批量处理多个库吗？
A: 是的！支持三种方式：
1. **安装目录方式（推荐）**：选择包含多个库的安装目录，工具会自动检测并展开
   ```bash
   edp-libkit gen-lib --foundry Samsung --lib-path /path/to/0711_install --lib-type STD --node ln03lpp --output-dir /path/to/output
   ```
2. **命令行方式**：使用多个 `--lib-path` 参数
   ```bash
   edp-libkit gen-lib --foundry Samsung --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 --lib-type STD --node ln08lpu_gp --output-dir /path/to/output
   ```
3. **文件列表方式**：使用 `--lib-paths-file` 从文件读取路径列表
   ```bash
   edp-libkit gen-lib --foundry Samsung --lib-paths-file lib_paths.txt --lib-type STD --node ln08lpu_gp --output-dir /path/to/output
   ```
   详细说明请参考 [批量处理文档](BATCH_PROCESSING.md) 和 [安装目录检测文档](INSTALLATION_DIRECTORY_DETECTION.md)。

### Q: 如何知道应该使用哪个节点？
A: 节点名称通常可以从库目录路径或库名称中推断，或者查看foundry的文档。如果不确定，可以尝试常见的节点名称。

### Q: 如何选择特定版本？
A: 使用 `--version` 参数指定版本号，例如 `--version 1.00B`。如果不指定，默认使用最新版本。

### Q: 如何处理所有版本？
A: 使用 `--all-versions` 参数，工具会为每个版本生成一个独立的 `lib_config.tcl` 文件。

## 完整示例

```bash
# 处理STD库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /tech_1/designkit/Samsung/LN08LPU_GP/ori/STD_Cell/0711_install/my_custom_lib \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output

# 处理IP库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /tech_1/designkit/Samsung/LN08LPU_GP/ori/IP/my_ip/v2.0 \
  --lib-type IP \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```
