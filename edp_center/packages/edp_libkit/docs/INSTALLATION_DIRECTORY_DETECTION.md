# 安装目录自动检测和展开

## 概述

EDP LibKit 现在支持自动检测安装目录（包含多个库目录的父目录），并自动展开为多个库进行处理。这大大简化了批量处理多个库的操作。

## 工作原理

### 检测逻辑

工具会通过以下方式检测库目录：

1. **检查父目录是否直接包含视图目录**
   - 如果父目录直接包含视图目录（如 `gds/`, `lef/`, `liberty/` 等），则认为父目录本身就是一个库目录

2. **检查子目录是否包含视图目录**
   - 如果父目录不直接包含视图目录，则检查所有子目录
   - 使用适配器的 `find_view_directories` 方法检测每个子目录
   - 如果子目录包含至少 2 个视图目录，则认为它是一个有效的库目录

3. **自动展开**
   - 如果检测到多个库目录，自动展开为多个库路径
   - 为每个库目录分别生成配置文件

## 使用示例

### 场景：安装目录包含多个库

假设你有以下目录结构：

```
0711_install/
├── v-logic_sa08nvghlogl20hdf068f/
│   └── DesignWare_logic_libs/.../gds/.../lef/...
├── v-logic_sa08nvghlogl20hsf068f/
│   └── DesignWare_logic_libs/.../gds/.../lef/.../liberty/...
└── v-logic_sa08nvghlogl22hsf068f/
    └── DesignWare_logic_libs/.../gds/.../lef/...
```

### 方式1：选择安装目录（推荐）

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/0711_install \
  --lib-type STD \
  --node ln03lpp \
  --output-dir /path/to/output
```

**结果**：
- 自动检测到 3 个子库
- 为每个库生成配置文件：
  - `{output_dir}/sa08nvghlogl20hdf068f/lib_config.tcl`
  - `{output_dir}/sa08nvghlogl20hsf068f/lib_config.tcl`
  - `{output_dir}/sa08nvghlogl22hsf068f/lib_config.tcl`

### 方式2：选择单个库目录

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/0711_install/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln03lpp \
  --output-dir /path/to/output
```

**结果**：
- 只处理指定的库
- 生成：`{output_dir}/sa08nvghlogl20hdf068f/lib_config.tcl`

## 检测标准

### 有效的库目录

一个目录被认为是有效的库目录，需要满足：

1. **包含足够的视图目录**：至少 2 个视图目录
   - 视图目录包括：`gds`, `lef`, `liberty`, `ccs_lvf`, `ccs_power`, `logic_synth`, `cdl`, `verilog` 等
   - 视图目录可能在深层目录中（如 `DesignWare_logic_libs/.../hvt/1.01a/gds/`）

2. **视图目录检测**
   - 使用适配器的 `find_view_directories` 方法
   - 该方法会递归查找视图目录，支持深层目录结构

### 不完整的库

即使某些库缺少部分视图目录（如缺 `gds` 或 `lef`），只要满足以下条件，仍然会被识别为有效的库目录：

- 包含至少 2 个视图目录
- 视图目录中包含有效的文件

**示例**：
- ✅ 有效：包含 `gds`, `lef`, `ccs_lvf`（3个视图目录）
- ✅ 有效：包含 `gds`, `liberty/ccs_lvf`（2个视图目录）
- ❌ 无效：只包含 `gds`（1个视图目录，不足2个）

## 优势

### 1. 无需手动指定每个库

**之前**：需要手动指定每个库路径
```bash
edp-libkit gen-lib --lib-path /path/to/lib1 --lib-type STD ...
edp-libkit gen-lib --lib-path /path/to/lib2 --lib-type STD ...
edp-libkit gen-lib --lib-path /path/to/lib3 --lib-type STD ...
```

**现在**：只需指定安装目录
```bash
edp-libkit gen-lib --lib-path /path/to/0711_install --lib-type STD ...
```

### 2. 自动识别库目录

- 不依赖特定的命名规则（如 `v-logic_*`）
- 通过检测视图目录来识别库目录
- 支持任意目录结构

### 3. 容错性强

- 支持不完整的库（缺少部分视图目录）
- 版本提取错误时自动回退到全目录搜索
- 跳过视图目录的子目录（避免误识别）

## 技术细节

### 检测流程

1. **创建适配器**：根据 `foundry` 和 `node` 创建适配器
2. **检查父目录**：检查父目录是否直接包含视图目录
3. **检查子目录**：遍历所有子目录，使用 `find_view_directories` 检测
4. **展开库路径**：将检测到的库目录添加到处理列表
5. **批量处理**：为每个库目录生成配置文件

### 版本处理

- 如果版本提取失败或版本目录不存在，自动回退到全目录搜索
- 这样可以处理版本提取错误的情况（如将 `lef/5.8` 误识别为版本）

## 注意事项

1. **性能**：检测过程需要遍历目录，对于包含大量子目录的安装目录，可能需要一些时间

2. **误识别**：如果子目录中包含非库目录但恰好有视图目录，可能会被误识别为库目录

3. **输出路径**：每个库都会生成独立的配置文件，库名从目录名提取（去掉 `v-logic_` 前缀等）

## 相关文档

- [使用指南](USAGE.md) - 详细的使用说明
- [批量处理](BATCH_PROCESSING.md) - 批量处理多个库的说明
- [快速开始](../QUICK_START.md) - 快速开始指南

