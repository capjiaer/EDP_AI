# 批量处理多个库

## 概述

EDP LibKit 支持批量处理多个库，无需手动循环执行多次命令。有两种方式：

1. **命令行参数方式**：直接在命令行指定多个 `--lib-path`
2. **文件列表方式**：从文件读取库路径列表

## 方式1：命令行参数（推荐用于少量库）

### 基本用法

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 \
  --lib-type STD \
  --node ln08lpu_gp
```

### 示例

```bash
# 批量处理3个STD库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path \
    /path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f \
    /path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hsf068f \
    /path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl22hsf068f \
  --lib-type STD \
  --node ln08lpu_gp
```

**输出示例**：
```
[INFO] Foundry: Samsung
[INFO] Node: ln08lpu_gp
[INFO] Library Type: STD
[INFO] 待处理库数量: 3

[1/3] 处理库: v-logic_sa08nvghlogl20hdf068f
  ✓ 已生成: lib_config.tcl
[2/3] 处理库: v-logic_sa08nvghlogl20hsf068f
  ✓ 已生成: lib_config.tcl
[3/3] 处理库: v-logic_sa08nvghlogl22hsf068f
  ✓ 已生成: lib_config.tcl

============================================================
[SUMMARY] 处理完成:
  成功: 3/3
  共生成: 3 个lib_config.tcl文件
============================================================
```

## 方式2：文件列表（推荐用于大量库）

### 创建库路径列表文件

创建一个文本文件，每行一个库路径：

**`lib_paths.txt`**：
```
# STD库路径列表
/path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f
/path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hsf068f
/path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl22hsf068f

# IP库路径列表
/path/to/IP/ln08lpu_gpio_1p8v/v1.12
/path/to/IP/another_ip/v2.0
```

**注意**：
- 空行会被忽略
- 以 `#` 开头的行会被视为注释
- 路径可以是绝对路径或相对路径

### 使用文件列表

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file lib_paths.txt \
  --lib-type STD \
  --node ln08lpu_gp
```

### 动态生成路径列表

#### Bash脚本示例

```bash
#!/bin/bash
# 生成所有v-logic_开头的库路径列表

lib_base="/path/to/STD_Cell/0711_install"
lib_list_file="/tmp/lib_paths.txt"

# 生成路径列表
find "$lib_base" -maxdepth 1 -type d -name "v-logic_*" > "$lib_list_file"

# 批量处理
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file "$lib_list_file" \
  --lib-type STD \
  --node ln08lpu_gp

# 清理临时文件
rm "$lib_list_file"
```

#### Python脚本示例

```python
from pathlib import Path
import subprocess

# 查找所有库目录
lib_base = Path('/path/to/STD_Cell/0711_install')
lib_paths = list(lib_base.glob('v-logic_*'))

# 生成路径列表文件
lib_list_file = Path('/tmp/lib_paths.txt')
with open(lib_list_file, 'w') as f:
    for lib_path in lib_paths:
        f.write(f"{lib_path}\n")

# 批量处理
subprocess.run([
    'edp-libkit', 'gen-lib',
    '--foundry', 'Samsung',
    '--lib-paths-file', str(lib_list_file),
    '--lib-type', 'STD',
    '--node', 'ln08lpu_gp'
])

# 清理临时文件
lib_list_file.unlink()
```

## 混合不同库类型

如果需要处理不同类型的库，需要分别处理：

```bash
# 先处理所有STD库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file std_libs.txt \
  --lib-type STD \
  --node ln08lpu_gp

# 再处理所有IP库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file ip_libs.txt \
  --lib-type IP \
  --node ln08lpu_gp
```

## 错误处理

批量处理时，如果某个库处理失败，工具会：
- 继续处理剩余的库
- 在最后显示成功/失败统计
- 返回非零退出码（如果有失败）

**示例输出**：
```
[1/3] 处理库: lib1
  ✓ 已生成: lib_config.tcl
[2/3] 处理库: lib2
  ✗ 失败: 目录不存在
[3/3] 处理库: lib3
  ✓ 已生成: lib_config.tcl

============================================================
[SUMMARY] 处理完成:
  成功: 2/3
  失败: 1/3
  共生成: 2 个lib_config.tcl文件
============================================================
```

## 性能考虑

- **并行处理**：当前版本是串行处理，按顺序处理每个库
- **大量库**：如果库数量很大（>100），建议使用文件列表方式
- **输出目录**：所有库的输出会放在同一个基础目录下，按库名和版本组织

## 最佳实践

1. **少量库（<10）**：使用命令行参数方式
2. **中等数量（10-50）**：使用文件列表方式
3. **大量库（>50）**：考虑分批处理，或编写脚本动态生成列表

## 完整示例

```bash
# 1. 创建路径列表文件
cat > lib_paths.txt << EOF
/path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hdf068f
/path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl20hsf068f
/path/to/STD_Cell/0711_install/v-logic_sa08nvghlogl22hsf068f
EOF

# 2. 批量处理
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-paths-file lib_paths.txt \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output

# 3. 查看结果
ls -R /path/to/output/Samsung/STD/
```

