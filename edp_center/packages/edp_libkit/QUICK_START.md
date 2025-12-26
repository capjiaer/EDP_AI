# EDP LibKit 快速开始指南

## 🚀 最快方式：使用GUI（无需安装！）

**不想看文档？直接启动GUI：**

```bash
cd edp_center/packages/edp_libkit
python run_gui.py
```

界面直观，一看就会！详细说明请查看 [GUI使用指南](GUI_README.md)

---

## 命令行方式（5分钟快速上手）

### 1. 处理单个STD库

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/std_library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

**结果**：生成 `{output_dir}/{lib_name}/lib_config.tcl`

### 2. 批量处理多个库

**方式1：选择安装目录（推荐）** ⭐

```bash
# 自动检测并处理安装目录中的所有库
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/0711_install \
  --lib-type STD \
  --node ln03lpp \
  --output-dir /path/to/output
```

**方式2：手动指定多个路径**

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 \
  --lib-type STD \
  --node ln08lpu_gp \
  --output-dir /path/to/output
```

**说明**：安装目录自动展开功能会自动检测包含多个库的目录，无需手动指定每个库路径。详见 [安装目录检测文档](docs/INSTALLATION_DIRECTORY_DETECTION.md)。

### 3. 处理所有版本

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --all-versions \
  --output-dir /path/to/output
```

**结果**：
- 最新版本：`lib_config.tcl`
- 其他版本：`lib_config.{version}.tcl`

### 4. 使用特定版本

```bash
edp-libkit gen-lib \
  --foundry Samsung \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --node ln08lpu_gp \
  --version 1.00B \
  --output-dir /path/to/output
```

## 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--foundry` | Foundry名称 | `Samsung`, `SMIC` |
| `--lib-path` | 库目录路径（可多个） | `/path/to/lib1 /path/to/lib2` |
| `--lib-type` | 库类型 | `STD`, `IP`, `MEM` |
| `--node` | 工艺节点 | `ln08lpu_gp` |
| `--output-dir` | 输出目录（必需） | `/path/to/output` |

## 可选参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--version` | 指定版本号 | `1.00B`, `2.00A` |
| `--all-versions` | 处理所有版本 | - |
| `--lib-paths-file` | 从文件读取路径列表 | `lib_paths.txt` |
| `--verbose` / `-v` | 显示详细日志 | - |

## 输出结构

```
/path/to/output/
├── sa08nvghlogl20hdf068f/
│   ├── lib_config.tcl         # 最新版本（默认）
│   ├── lib_config.1.01a.tcl   # 其他版本（如果使用 --all-versions）
│   └── lib_config.1.00B.tcl
└── ln08lpu_gpio_1p8v/
    └── lib_config.tcl
```

## 使用生成的配置文件

```tcl
# 默认使用最新版本
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.tcl

# 使用特定版本
source /path/to/output/sa08nvghlogl20hdf068f/lib_config.1.00B.tcl
```

## 常见问题

### Q: 如何知道应该使用哪个节点？
A: 节点名称通常可以从库目录路径或库名称中推断，或者查看foundry的文档。

### Q: 如何选择特定版本？
A: 使用 `--version` 参数指定版本号，例如 `--version 1.00B`。

### Q: 如何处理所有版本？
A: 使用 `--all-versions` 参数，工具会为每个版本生成一个独立的配置文件。

### Q: 可以批量处理不同类型的库吗？
A: 可以，但需要分别处理（因为 `--lib-type` 是必需的）：
```bash
# 先处理STD库
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/std_libs --lib-type STD --node ln08lpu_gp --output-dir /path/to/output

# 再处理IP库
edp-libkit gen-lib --foundry Samsung --lib-path /path/to/ip_libs --lib-type IP --node ln08lpu_gp --output-dir /path/to/output
```

## 更多信息

- 详细使用说明：查看 [USAGE.md](docs/USAGE.md)
- 版本选择功能：查看 [VERSION_SELECTION.md](docs/VERSION_SELECTION.md)
- 批量处理功能：查看 [BATCH_PROCESSING.md](docs/BATCH_PROCESSING.md)
