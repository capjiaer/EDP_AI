# EDP LibKit 核心功能说明

## 核心价值

**本质**：从分散的库文件中收集和整理配置信息，生成统一的 `lib_config.tcl` 配置文件。

## 工作流程

### 场景：从Foundry拿到库文件后

1. **库文件分散在不同位置**
   ```
   STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f/...
   STD_Cell/0711_install/v-logic_sa08nvghlogl20hsf068f/...
   IP/ln08lpu_gpio_1p8v/v1.12/...
   MEM/sram_xxx/...
   ```

2. **执行工具收集配置**
   ```bash
   # 收集STD库
   edp-libkit gen-lib \
     --foundry Samsung \
     --lib-path /path/to/v-logic_sa08nvghlogl20hdf068f \
     --lib-type STD \
     --node ln08lpu_gp \
     --output-dir /path/to/configs
   
   # 收集IP库
   edp-libkit gen-lib \
     --foundry Samsung \
     --lib-path /path/to/ln08lpu_gpio_1p8v/v1.12 \
     --lib-type IP \
     --node ln08lpu_gp \
     --output-dir /path/to/configs
   
   # 收集MEM库
   edp-libkit gen-lib \
     --foundry Samsung \
     --lib-path /path/to/sram_xxx \
     --lib-type MEM \
     --node ln08lpu_gp \
     --output-dir /path/to/configs
   ```

3. **生成统一的配置文件**
   ```
   /path/to/configs/
   ├── sa08nvghlogl20hdf068f/lib_config.tcl
   ├── sa08nvghlogl20hsf068f/lib_config.tcl
   ├── ln08lpu_gpio_1p8v/lib_config.tcl
   └── sram_xxx/lib_config.tcl
   ```
   
   **注意**：路径结构已简化，不包含版本目录层级。使用 `--all-versions` 时，其他版本生成 `lib_config.{version}.tcl`（如 `lib_config.1.00B.tcl`），所有版本文件都在同一目录下。

4. **lib_config.tcl 包含所有必要信息**
   ```tcl
   # 每个库的配置文件包含：
   # - 库名称
   # - 版本信息
   # - 所有视图文件的完整路径（GDS, LEF, Liberty等）
   # - PVT corner信息
   # - RC corner信息
   
   set LIBRARY(sa08nvghlogl20hdf068f,gds,gds) {
     /original/path/to/file1.gds
     /original/path/to/file2.gds
   }
   set LIBRARY(sa08nvghlogl20hdf068f,lef,lef) {
     /original/path/to/file.lef
   }
   set LIBRARY(sa08nvghlogl20hdf068f,ccs_lvf,sigcmin,ffpg0p715vn40c,db) {
     /original/path/to/file.db
   }
   ```

## 核心功能

### ✅ 已实现的功能

1. **自动扫描库文件**
   - 识别库目录结构
   - 查找各种视图文件（GDS, LEF, Liberty等）
   - 提取PVT corner和RC corner信息

2. **生成统一配置**
   - 生成标准化的 `lib_config.tcl` 文件
   - 包含所有文件的完整路径
   - 包含库的元数据信息

3. **批量处理**
   - 支持一次处理多个库
   - 支持从文件列表读取库路径

4. **多库类型支持**
   - STD（标准单元库）
   - IP（IP库）
   - MEM（内存库）

### ❌ 不需要的功能（当前）

1. **文件链接（Link）**
   - 不需要创建符号链接
   - 不需要复制文件
   - 配置文件中的路径直接指向原始文件位置

2. **文件整理**
   - 不需要重新组织文件目录
   - 保持原始文件位置不变

## 为什么不需要 Link？

### 1. 核心需求已满足

**需求**：收集分散库的配置信息
**实现**：生成 `lib_config.tcl` 包含所有文件路径
**结果**：✅ 已完成

### 2. 工具自动读取配置

- EDA工具读取 `lib_config.tcl`
- 根据路径自动找到文件
- 不需要人工查看文件位置

### 3. 保持原始结构

- 原始文件位置不变
- 不影响其他工具使用
- 避免维护两套路径

### 4. 简单可靠

- 无平台兼容性问题
- 无链接失效风险
- 实现和维护简单

## 使用示例

### 完整工作流

```bash
# 1. 从Foundry拿到库文件（分散在不同位置）
# STD库在：/foundry/STD_Cell/0711_install/v-logic_xxx/
# IP库在：/foundry/IP/xxx/v1.12/
# MEM库在：/foundry/MEM/xxx/

# 2. 批量收集STD库配置
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path \
    /foundry/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f \
    /foundry/STD_Cell/0711_install/v-logic_sa08nvghlogl20hsf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /project/configs

# 3. 收集IP库配置
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /foundry/IP/ln08lpu_gpio_1p8v/v1.12 \
  --lib-type IP \
  --node ln08lpu_gp \
  --output-dir /project/configs

# 4. 收集MEM库配置
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /foundry/MEM/sram_xxx \
  --lib-type MEM \
  --node ln08lpu_gp \
  --output-dir /project/configs

# 5. 结果：所有库的配置都收集到 /project/configs/ 目录下
# 每个库一个 lib_config.tcl 文件，包含该库的所有文件路径
```

## 总结

**核心价值**：
- ✅ **收集配置信息**：从分散的库文件中收集配置
- ✅ **生成统一配置**：生成标准化的 `lib_config.tcl`
- ✅ **批量处理**：支持一次处理多个库
- ✅ **多类型支持**：支持 STD/IP/MEM

**不需要的功能**：
- ❌ 文件链接（Link）
- ❌ 文件复制
- ❌ 目录重组

**结论**：当前工具已经完美满足核心需求，不需要额外的 Link 功能。

