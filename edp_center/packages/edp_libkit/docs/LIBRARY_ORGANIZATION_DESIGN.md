# 库文件目录整理功能设计讨论

## 需求概述

除了生成 `lib_config.tcl` 配置文件外，还需要：
1. **创建规整的目录结构**：将分散的库文件组织到统一的目录结构中
2. **使用符号链接**：通过 symlink 将原始文件链接到新位置，避免复制
3. **更新路径引用**：`lib_config.tcl` 中的路径指向新的规整目录

## 当前情况

### 原始文件位置（复杂且分散）

```
STD_Cell/0711_install/v-logic_sa08nvgllogl22hsl068f/
└── DesignWare_logic_libs/
    └── samsung08nvllg/
        └── 22hs/
            └── hsl/
                └── lvt/
                    └── 2.00a/
                        ├── gds/
                        │   └── sa08nvgllogl22hsl068f.gds
                        ├── lef/
                        │   └── sa08nvgllogl22hsl068f.lef
                        └── liberty/
                            └── ccs_lvf/
                                └── sa08nvgllogl22hsl068f_ffpg0p715vn40c.db
```

### lib_config.tcl 中的路径

```tcl
set LIBRARY(sa08nvgllogl22hsl068f,gds,gds) {
  C:/.../STD_Cell/0711_install/v-logic_sa08nvgllogl22hsl068f/DesignWare_logic_libs/samsung08nvllg/22hs/hsl/lvt/2.00a/gds/sa08nvgllogl22hsl068f.gds
}
```

## 目标结构

### 规整的目录结构

```
library/
└── STD/
    └── JoinSilicon/
        └── samsung/
            └── samsung08nvllg/
                └── 2.00a/
                    ├── gds/
                    │   └── sa08nvgllogl22hsl068f.gds  (symlink)
                    ├── lef/
                    │   └── sa08nvgllogl22hsl068f.lef  (symlink)
                    └── liberty/
                        └── ccs_lvf/
                            └── sa08nvgllogl22hsl068f_ffpg0p715vn40c.db  (symlink)
```

### 更新后的 lib_config.tcl

```tcl
set LIBRARY(sa08nvgllogl22hsl068f,gds,gds) {
  C:/library/STD/JoinSilicon/samsung/samsung08nvllg/2.00a/gds/sa08nvgllogl22hsl068f.gds
}
```

## 需要讨论的问题

### 1. 目录结构规则

**问题**：如何确定目录结构的各个层级？

**示例结构**：
```
{library_base}/{lib_type}/{vendor}/{foundry}/{library_name}/{version}/{view_type}/{files}
```

**层级说明**：
- `{library_base}`: 基础目录（如 `library`）
- `{lib_type}`: 库类型（`STD`, `IP`, `MEM`）
- `{vendor}`: 供应商（如 `JoinSilicon`）- **如何提取？**
- `{foundry}`: Foundry名称（如 `samsung`）
- `{library_name}`: 库名称（如 `samsung08nvllg`）- **如何提取？**
- `{version}`: 版本号（如 `2.00a`）
- `{view_type}`: 视图类型（`gds`, `lef`, `liberty/ccs_lvf` 等）
- `{files}`: 实际文件（通过 symlink）

**问题**：
- `JoinSilicon` 这个信息从哪里来？是固定的还是需要从路径提取？
- `samsung08nvllg` 是从路径中的 `DesignWare_logic_libs/samsung08nvllg/` 提取的吗？
- 是否所有库都遵循这个结构？

### 2. 信息提取规则

**需要从原始路径提取的信息**：

| 信息 | 示例值 | 提取位置 | 问题 |
|------|--------|----------|------|
| vendor | JoinSilicon | ? | 如何确定？固定值还是从路径提取？ |
| library_name | samsung08nvllg | `DesignWare_logic_libs/samsung08nvllg/` | 是否总是这个位置？ |
| version | 2.00a | `.../lvt/2.00a/` | 版本号的位置是否固定？ |
| view_type | gds, lef, ccs_lvf | 目录名 | 这个应该可以自动识别 |

**问题**：
- 不同库类型的路径结构可能不同，如何统一处理？
- IP库和MEM库的路径结构可能完全不同，如何处理？

### 3. 符号链接策略

**Windows vs Linux**：
- **Linux/Mac**: 使用 `os.symlink()` 创建符号链接
- **Windows**: 
  - 需要管理员权限才能创建符号链接（或启用开发者模式）
  - 可以使用 `mklink` 命令
  - 或者使用 junction（目录链接）

**问题**：
- 是否需要检测系统类型？
- 如果无法创建符号链接，是否回退到复制文件？
- 是否需要提供选项让用户选择：symlink、copy、或两者都支持？

### 4. 路径更新策略

**问题**：
- 是否需要更新 `lib_config.tcl` 中的路径？
- 还是生成两个版本：一个指向原始路径，一个指向新路径？
- 或者提供一个选项让用户选择？

### 5. 目录结构配置

**问题**：
- 目录结构规则是硬编码还是可配置？
- 是否需要支持配置文件或命令行参数来指定结构？
- 是否需要支持不同的组织方式（如按foundry组织、按vendor组织等）？

## 建议的设计方案

### 方案1：固定结构 + 路径解析

**特点**：
- 定义固定的目录结构规则
- 从原始路径中解析关键信息
- 支持配置覆盖

**优点**：
- 实现简单
- 结构统一

**缺点**：
- 不够灵活
- 需要准确解析路径

### 方案2：可配置结构 + 模板

**特点**：
- 支持配置文件定义目录结构模板
- 使用占位符（如 `{vendor}`, `{library_name}`）
- 从路径或元数据中提取值填充

**优点**：
- 灵活可配置
- 适应不同场景

**缺点**：
- 实现复杂
- 需要定义提取规则

### 方案3：混合方案（推荐）

**特点**：
- 提供默认的目录结构规则
- 支持通过命令行参数或配置文件覆盖
- 智能提取路径信息
- 支持多种链接方式（symlink/copy）

**实现步骤**：
1. 定义默认目录结构模板
2. 从原始路径提取信息（vendor, library_name等）
3. 构建目标目录结构
4. 创建符号链接（或复制）
5. 更新 `lib_config.tcl` 中的路径

## 下一步讨论

请确认以下问题：

1. **目录结构**：`library/STD/JoinSilicon/samsung/samsung08nvllg/2.00a/` 这个结构是固定的吗？
2. **信息提取**：
   - `JoinSilicon` 是固定值还是需要从路径提取？
   - `samsung08nvllg` 是否总是从 `DesignWare_logic_libs/samsung08nvllg/` 提取？
3. **链接方式**：优先使用 symlink，如果失败是否回退到 copy？
4. **路径更新**：`lib_config.tcl` 中的路径是否需要更新为新路径？
5. **配置方式**：是否需要支持配置文件或命令行参数来定制目录结构？

