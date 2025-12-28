# 版本选择功能说明

## 功能概述

**自动选择最新版本**：当库目录下有多个版本时，工具会自动选择最新版本进行处理。

## 问题场景

在一个库目录下可能有多个版本，例如：
```
v-logic_sa08nvghlogl20hdf068f/
└── DesignWare_logic_libs/
    └── samsung08nvllg/
        └── 20hs/
            └── hdf/
                └── hvt/
                    ├── 2.00A/    # 最新版本
                    ├── 1.01a/    # 旧版本
                    └── 1.0/      # 更旧版本
```

**需求**：通常只需要最新的版本（如 `2.00A`）

## 实现方案

### ✅ 已实现：自动选择最新版本

**特点**：
- ✅ 自动扫描所有版本目录
- ✅ 智能比较版本号，选择最新的
- ✅ 只处理最新版本的视图文件
- ✅ 无需额外配置，默认行为

### 版本比较逻辑

**支持的版本格式**：
- `2.00A` - 数字.数字字母（如 `2.00A`, `1.01a`, `1.00B`）
- `v1.12` - v数字.数字（如 `v1.12`, `v2.0`）
- `1.0` - 数字.数字（如 `1.0`, `2.5`）

**比较规则**：
1. 提取主版本号和次版本号
2. 先比较主版本号，再比较次版本号
3. 如果有字母后缀，按字母顺序比较（A < B < C ...）
4. 返回版本号最大的版本

**示例**：
- `2.00A` > `1.01a` > `1.00B` > `1.00A` > `1.0`
- `v2.0` > `v1.12` > `v1.0`
- `1.00B` > `1.00A`（相同数字，字母B比A新）

**特殊情况**：
- 相同数字部分，不同字母：`1.00B` > `1.00A`
- 相同数字部分，有字母 vs 无字母：`1.00A` > `1.00`

## 工作流程

1. **扫描版本目录**
   - 使用 `_find_all_versions()` 扫描库目录
   - 找到所有符合版本格式的目录名

2. **选择最新版本**
   - 使用 `_get_latest_version()` 比较所有版本
   - 返回版本号最大的版本

3. **只处理最新版本**
   - `_find_std_view_directories()` 只查找最新版本的目录
   - 生成的 `lib_config.tcl` 只包含最新版本的文件路径

## 使用示例

### 方式1：自动选择最新版本（默认）

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

**结果**：
- 如果库目录下有 `2.00A`, `1.01a`, `1.0` 三个版本
- 工具会自动选择 `2.00A`（最新版本）
- 生成的 `lib_config.tcl` 只包含 `2.00A` 版本的文件

### 方式2：指定特定版本

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --version 1.00B \
  --output-dir /path/to/output
```

**结果**：
- 只处理 `1.00B` 版本
- 生成的 `lib_config.tcl` 只包含 `1.00B` 版本的文件
- 即使 `2.00A` 更新，也会使用指定的 `1.00B`

### 方式3：处理所有版本

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --all-versions \
  --output-dir /path/to/output
```

**结果**：
- 处理所有版本（`2.00A`, `1.01a`, `1.0` 等）
- **最新版本**：生成 `lib_config.tcl`（默认使用）
- **其他版本**：生成 `lib_config_{version}.tcl`（如 `lib_config_1.01a.tcl`）
- 所有文件都在最新版本的目录下
- 输出结构：
  ```
  /path/to/output/
  └── sa08nvghlogl20hdf068f/
      └── 2.00A/                    # 最新版本目录
          ├── lib_config.tcl         # 最新版本（默认）
          ├── lib_config_1.01a.tcl  # 旧版本1
          └── lib_config_1.0.tcl    # 旧版本2
  ```

**使用方式**：
- 默认使用最新版本：`source lib_config.tcl`
- 使用特定版本：`source lib_config.1.01a.tcl`（使用点分隔，格式统一）

### 验证版本选择

生成的 `lib_config.tcl` 文件中的路径会指向选定的版本：
```tcl
# Library: sa08nvghlogl20hdf068f
# Version: 2.00A  # 自动选择或指定的版本

set LIBRARY(sa08nvghlogl20hdf068f,gds,gds) {
  /path/to/.../2.00A/gds/file.gds  # 只包含选定版本的文件
}
```

## 技术实现

### 关键方法

1. **`_find_all_versions(lib_path)`**
   - 扫描库目录，找到所有版本目录
   - 返回版本字符串列表

2. **`_get_latest_version(versions)`**
   - 比较版本列表，返回最新版本
   - 使用 `_parse_version_for_sort()` 解析版本号

3. **`_parse_version_for_sort(version)`**
   - 解析版本字符串为可比较的元组
   - 格式：`(主版本号, 次版本号, 字母值)`

4. **`_find_std_view_directories(lib_path)`**
   - 只查找最新版本的视图目录
   - 使用 `_find_version_path()` 定位版本目录

## 注意事项

1. **版本格式要求**
   - 版本目录名必须符合标准格式
   - 如果版本格式无法识别，可能无法正确比较

2. **IP库处理**
   - IP库的版本通常在目录名中（如 `v1.12`）
   - 如果用户指定的是版本目录，直接使用该版本
   - 如果指定的是IP库根目录，会查找所有版本目录并选择最新的

3. **向后兼容**
   - 如果只有一个版本，行为不变
   - 如果没有找到版本，使用原来的逻辑（遍历所有目录）

## 版本选择选项

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| （无） | 默认行为，自动选择最新版本 | - |
| `--version` | 指定特定版本 | `--version 1.00B` |
| `--all-versions` | 处理所有版本 | `--all-versions` |

**注意**：
- `--version` 和 `--all-versions` 不能同时使用
- 如果都不指定，默认使用最新版本

## 总结

- ✅ **自动选择**：默认自动选择最新版本，无需配置
- ✅ **指定版本**：支持 `--version` 参数指定特定版本
- ✅ **所有版本**：支持 `--all-versions` 处理所有版本
- ✅ **智能比较**：支持多种版本格式（`2.00A`, `1.00B`, `v1.12` 等）
- ✅ **向后兼容**：不影响单版本库的处理

**默认行为**：工具会自动选择最新版本，无需额外配置。

**灵活选择**：如果需要使用特定版本或所有版本，可以使用相应的命令行参数。

