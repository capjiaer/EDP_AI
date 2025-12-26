# 简化路径结构说明

## 路径结构变化

### 之前的结构（包含版本目录）

```
{output_dir}/{lib_name}/{version}/lib_config.tcl
```

**示例**：
```
/path/to/output/sa08nvghlogl20hdf068f/2.00A/lib_config.tcl
```

### 现在的结构（简化后）

```
{output_dir}/{lib_name}/lib_config.tcl
```

**示例**：
```
/path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl
```

## 优势

1. **路径更简洁**：少了一级目录，使用更方便
2. **source更简单**：`source lib_config.tcl` 即可
3. **版本信息在文件名**：使用 `--all-versions` 时，其他版本通过文件名区分

## 使用方式

### 默认使用最新版本

```tcl
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl
```

### 使用特定版本（使用 --all-versions 时）

```tcl
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.1.00B.tcl
```

## 文件命名规则

### 默认情况（单个版本）

- 生成：`lib_config.tcl`
- 路径：`{output_dir}/{lib_name}/lib_config.tcl`

### 使用 --all-versions

- **最新版本**：`lib_config.tcl`
- **其他版本**：`lib_config.{version}.tcl`（如 `lib_config.1.00B.tcl`）
- 所有文件都在：`{output_dir}/{lib_name}/` 目录下
- **格式说明**：使用点分隔（`.`），因为版本号本身用点分隔，格式更统一

## 示例

### 命令

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/v-logic_sa08nvghlogl20hdf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --all-versions \
  --output-dir /path/to/output
```

### 生成的文件结构

假设库有3个版本：`2.00A`（最新）, `1.01a`, `1.00B`

```
/path/to/output/
└── sa08nvghlogl20hdf068f/
    ├── lib_config.tcl         # 最新版本（2.00A）
    ├── lib_config.1.01a.tcl   # 旧版本1
    └── lib_config.1.00B.tcl   # 旧版本2
```

### 使用示例

```tcl
# 默认使用最新版本
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl

# 使用特定版本
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.1.00B.tcl
```

## 总结

- ✅ **路径简化**：去掉版本目录层级
- ✅ **使用方便**：`source lib_config.tcl` 即可
- ✅ **版本区分**：通过文件名区分版本（`lib_config.{version}.tcl`）
- ✅ **格式统一**：使用点分隔，与版本号格式一致
- ✅ **集中管理**：所有版本文件在同一目录

