# 版本文件命名策略

## 设计理念

**默认使用最新版本，可选使用其他版本**

## 文件命名规则

### 使用 `--all-versions` 时

当使用 `--all-versions` 参数处理所有版本时：

1. **最新版本**：生成 `lib_config.tcl`
   - 这是默认使用的配置文件
   - 用户可以直接 `source lib_config.tcl` 使用最新版本

2. **其他版本**：生成 `lib_config_{version}.tcl`
   - 例如：`lib_config_1.00B.tcl`, `lib_config_1.01a.tcl`
   - 用户需要特定版本时，可以 `source lib_config_1.00B.tcl`

### 输出目录结构

```
/path/to/output/
└── sa08nvghlogl20hdf068f/        # 库名目录（不包含版本子目录）
    ├── lib_config.tcl             # 最新版本（默认）
    ├── lib_config_1.01a.tcl      # 旧版本1
    └── lib_config_1.00B.tcl       # 旧版本2
```

**注意**：
- 所有版本的文件都在库名目录下，不创建版本子目录
- 路径更简洁，使用更方便

## 使用场景

### 场景1：默认使用最新版本

```tcl
# 在TCL脚本中
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl
# 自动使用最新版本（2.00A）
```

### 场景2：使用特定版本

```tcl
# 在TCL脚本中
source /path/to/output/sa08nvghlogl20hdf068f/lib_config_1.00B.tcl
# 使用1.00B版本
```

### 场景3：混合使用

```tcl
# 大部分cell使用最新版本
source /path/to/output/lib1/lib_config.tcl

# 某些特定cell需要使用旧版本
source /path/to/output/lib1/lib_config_1.00B.tcl
```

## 优势

1. **默认简单**：`lib_config.tcl` 就是最新版本，无需记忆版本号
2. **灵活选择**：需要特定版本时，文件名明确标识版本
3. **集中管理**：所有版本文件在同一目录，便于查找和管理
4. **向后兼容**：不影响现有的使用方式

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

### 生成的文件

假设库有3个版本：`2.00A`（最新）, `1.01a`, `1.00B`

```
/path/to/output/sa08nvghlogl20hdf068f/
├── lib_config.tcl         # 指向 2.00A 版本（最新）
├── lib_config_1.01a.tcl   # 指向 1.01a 版本
└── lib_config_1.00B.tcl   # 指向 1.00B 版本
```

### 文件内容

**lib_config.tcl**（最新版本）：
```tcl
# Library: sa08nvghlogl20hdf068f
# Version: 2.00A

set LIBRARY(sa08nvghlogl20hdf068f,gds,gds) {
  /path/to/.../2.00A/gds/file.gds
}
```

**lib_config.1.00B.tcl**（旧版本）：
```tcl
# Library: sa08nvghlogl20hdf068f
# Version: 1.00B

set LIBRARY(sa08nvghlogl20hdf068f,gds,gds) {
  /path/to/.../1.00B/gds/file.gds
}
```

## 总结

- ✅ **最新版本**：`lib_config.tcl` - 默认使用
- ✅ **其他版本**：`lib_config.{version}.tcl` - 按需使用（使用点分隔，格式统一）
- ✅ **简化路径**：不包含版本目录层级，路径更简洁
- ✅ **集中管理**：所有版本文件在同一目录
- ✅ **简单灵活**：默认简单，需要时灵活

**文件名格式说明**：
- 使用点分隔（`.`）而不是下划线（`_`）
- 原因：版本号本身用点分隔（如 `1.00b`），文件名也用点连接更统一自然
- 格式：`lib_config.{version}.tcl`，如 `lib_config.1.00b.tcl`

**路径对比**：

**之前**（包含版本目录）：
```
/path/to/output/lib_name/2.00A/lib_config.tcl
```

**现在**（简化后）：
```
/path/to/output/lib_name/lib_config.tcl          # 更简洁！
/path/to/output/lib_name/lib_config.1.00B.tcl   # 其他版本（点分隔）
```

