# lib_config.tcl 输出位置说明

## 概述

批量生成的 `lib_config.tcl` 文件会按照简化的目录结构组织，每个库生成独立的配置文件。

## 输出路径规则

### 路径结构

```
{output_dir}/{lib_name}/lib_config.tcl
```

**路径组成部分**：
- `{output_dir}`: 输出目录（必须通过 `--output-dir` 指定）
- `{lib_name}`: 库名称（从目录路径提取）
- `lib_config.tcl`: 文件名（固定）

**注意**：
- 不再包含版本目录层级，版本信息通过文件名区分
- 使用 `--all-versions` 时，其他版本生成 `lib_config_{version}.tcl`
- 不再包含 `{foundry}` 和 `{lib_type}` 层级
- 因为用户可能已经在 `output_dir` 中包含了这些信息（如 `/path/to/Samsung/STD/`）
- `--output-dir` 现在是必需参数

### 输出目录

**必须指定 `--output-dir`**：

**示例**：
```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/lib1 /path/to/lib2 \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

**输出位置**：
```
/path/to/output/
├── sa08nvghlogl20hdf068f/
│   └── lib_config.tcl
└── sa08nvghlogl20hsf068f/
    └── lib_config.tcl
```

**如果用户指定包含类型的目录**：
```bash
# 用户指定包含 STD 的目录
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/lib1 \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/Samsung/STD
```

**输出位置**：
```
/path/to/Samsung/STD/
└── sa08nvghlogl20hdf068f/
    └── lib_config.tcl
```

## 批量处理时的输出结构

### 示例：处理3个STD库

**命令**：
```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path \
    /path/to/v-logic_sa08nvghlogl20hdf068f \
    /path/to/v-logic_sa08nvghlogl20hsf068f \
    /path/to/v-logic_sa08nvghlogl22hsf068f \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

**输出目录结构**：
```
/path/to/output/
├── sa08nvghlogl20hdf068f/      # 库1
│   └── lib_config.tcl
├── sa08nvghlogl20hsf068f/      # 库2
│   └── lib_config.tcl
└── sa08nvghlogl22hsf068f/      # 库3
    └── lib_config.tcl
```

### 示例：处理不同类型的库（分别指定不同的输出目录）

**命令**：
```bash
# 处理STD库，输出到 STD 目录
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/std_lib \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/Samsung/STD

# 处理IP库，输出到 IP 目录
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/ip_lib \
  --lib-type IP \
  --node ln08lpu_gp \
  --output-dir /path/to/Samsung/IP
```

**输出目录结构**：
```
/path/to/Samsung/
├── STD/                              # STD库类型
│   └── sa08nvghlogl20hdf068f/
│       └── lib_config.tcl
└── IP/                                # IP库类型
    └── ln08lpu_gpio_1p8v/
        └── lib_config.tcl
```

## 版本号处理

### 有版本号的情况

如果库有版本号，会在库名目录下创建版本子目录：

```
Samsung/STD/sa08nvghlogl20hdf068f/2.00A/lib_config.tcl
```

### 无版本号的情况

如果库没有版本号，直接在库名目录下创建文件：

```
Samsung/STD/my_library/lib_config.tcl
```

## 实际路径示例

### Windows路径示例

**简化后的路径**：
```
C:\output\sa08nvghlogl20hdf068f\lib_config.tcl
```

**如果用户指定包含类型的目录**：
```
C:\output\Samsung\STD\sa08nvghlogl20hdf068f\lib_config.tcl
```

### Linux路径示例

**简化后的路径**：
```
/path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl
```

**如果用户指定包含类型的目录**：
```
/path/to/output/Samsung/STD/sa08nvghlogl20hdf068f/lib_config.tcl
```

## 查找生成的文件

### 方法1：查看命令行输出

批量处理完成后，命令行会显示所有生成的文件路径：

```
[SUMMARY] 处理完成:
  成功: 3/3
  共生成: 3 个lib_config.tcl文件

生成的文件列表:
  - /path/to/output/Samsung/STD/sa08nvghlogl20hdf068f/lib_config.tcl
  - /path/to/output/Samsung/STD/sa08nvghlogl20hsf068f/lib_config.tcl
  - /path/to/output/Samsung/STD/sa08nvghlogl22hsf068f/lib_config.tcl
```

### 方法2：使用文件系统查找

**Windows**：
```cmd
dir /s /b lib_config.tcl
```

**Linux/Mac**：
```bash
find /path/to/output -name "lib_config.tcl"
```

### 方法3：查看输出目录结构

```bash
# Windows
tree /F /path/to/output

# Linux/Mac
tree /path/to/output
```

## 注意事项

1. **必须指定输出目录**：`--output-dir` 现在是必需参数，不能省略
2. **目录自动创建**：如果输出目录不存在，工具会自动创建
3. **文件覆盖**：如果同一个库的配置文件已存在，会被覆盖
4. **路径分隔符**：Windows使用反斜杠 `\`，Linux/Mac使用正斜杠 `/`，工具会自动处理
5. **相对路径**：如果使用相对路径，会基于当前工作目录解析
6. **简化路径结构**：不再自动添加 `{foundry}/{lib_type}` 层级，用户可以在 `--output-dir` 中指定

## 最佳实践

1. **按类型组织**：如果需要在输出目录中区分类型，可以在 `--output-dir` 中包含类型信息
   ```bash
   # STD库输出到
   --output-dir /path/to/Samsung/STD
   
   # IP库输出到
   --output-dir /path/to/Samsung/IP
   ```

2. **统一管理**：可以将所有库输出到同一个目录，然后按库名和版本组织
   ```bash
   --output-dir /path/to/all_libs
   ```

3. **版本控制**：可以将输出目录纳入版本控制，但注意排除大文件
4. **定期清理**：如果输出目录很大，可以定期清理旧版本
5. **备份重要配置**：生成后可以备份重要的配置文件

## 总结

- ✅ **每个库独立文件**：每个库生成一个独立的 `lib_config.tcl` 文件
- ✅ **简化目录结构**：按照 `{lib_name}/lib_config.tcl` 组织（不包含版本目录）
- ✅ **版本信息在文件名**：使用 `--all-versions` 时，其他版本生成 `lib_config_{version}.tcl`
- ✅ **必须指定输出目录**：`--output-dir` 是必需参数
- ✅ **灵活的组织方式**：用户可以在 `--output-dir` 中包含 foundry 和 lib_type 信息

