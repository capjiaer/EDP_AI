# RELEASE 功能

[← 返回目录](../TUTORIAL.md)

本文档介绍 EDP_AI 框架的 RELEASE 功能，用于发布和共享运行结果。

## 什么是 RELEASE？

RELEASE 功能允许你将运行结果发布到共享目录，供团队成员使用。发布后的数据会被设置为只读，防止意外修改。

## RELEASE 目录结构

RELEASE 目录位于项目版本目录下，结构如下：

**单步骤结构**：
```
WORK_PATH/
└── {project}/              # 项目名称
    └── {version}/          # 项目版本
        ├── {block}/         # 块名称
        │   └── {user}/      # 用户名
        │       └── {branch}/# 分支名称（工作目录）
        └── RELEASE/        # RELEASE 目录（与 block 同级）
            └── {block}/     # 块名称
                └── {user}/  # 用户名（按用户分组）
                    └── {version}/  # RELEASE 版本（如 v09001）
                        ├── data/                   # 数据目录
                        │   └── {flow}.{step}/     # 每个 step 一个目录（统一结构）
                        │       ├── def/           # DEF 文件
                        │       ├── db/            # 数据库文件
                        │       ├── sdf/           # SDF 文件
                        │       ├── spef/          # SPEF 文件
                        │       ├── verilog/       # Verilog 网表
                        │       ├── config/        # 配置文件
                        │       ├── timing_csv/    # 时序数据（CSV 格式）
                        │       ├── lib_settings.tcl  # 该 step 的库设置文件（必须）
                        │       └── full.tcl       # 该 step 的完整脚本（可选）
                        ├── release_note.txt       # 发布说明（可选，所有 step 共享）
                        └── .readonly              # 只读标记文件（框架自动创建）
```

**多步骤结构**（如果一次 release 多个步骤）：
```
RELEASE/{block}/{user}/{version}/
├── data/
│   ├── pnr_innovus.place/      # place 步骤的数据
│   │   ├── def/
│   │   ├── db/
│   │   ├── timing_csv/
│   │   ├── lib_settings.tcl
│   │   └── full.tcl
│   └── pnr_innovus.postroute/  # postroute 步骤的数据
│       ├── def/
│       ├── db/
│       ├── timing_csv/
│       ├── lib_settings.tcl
│       └── full.tcl
├── release_note.txt
└── .readonly
```

**重要说明**：
- 统一使用 `data/{flow}.{step}/` 结构，即使是单步骤也这样
- 每个 step 的 `lib_settings.tcl` 和 `full.tcl` 独立存储在自己的 step 目录下
- `release_note.txt` 在根目录，所有 step 共享

## 基本用法

### 方式 A: 使用 GUI 图形界面（推荐）

启动统一 GUI 进行 RELEASE 管理：

```bash
# 启动统一 GUI
edp -gui
```

在 GUI 的 **RELEASE 版本管理** Tab 中：

1. **查看 Release 列表**：
   - 使用过滤器（项目、版本、Block、User）筛选 release 版本
   - 在版本列表中查看所有符合条件的 release
   - 点击版本查看详细信息

2. **创建新 Release**：
   - 点击"新建"按钮
   - 选择工作目录和分支
   - 输入 release 版本号
   - 勾选要发布的步骤（支持多选）
   - 可选：添加发布说明、选择追加/覆盖模式
   - 点击"创建"开始发布

3. **查看版本内容**：
   - 在"Version Overview"树中浏览版本目录结构
   - 点击文件可在右侧预览文件内容
   - 使用"折叠"/"展开"按钮控制树形结构

4. **Timing Compare**：
   - 勾选版本列表中的"Timing Compare"复选框选择要对比的版本
   - 点击"对比"按钮打开 Timing Compare 窗口
   - 在窗口中查看多个版本的时序数据对比

### 方式 B: 使用命令行

```bash
# 进入分支目录
cd /path/to/work/{project}/{version}/{block}/{user}/{branch}

# 基本用法：发布单个步骤的结果
edp -release --release-version v09001 --step pnr_innovus.postroute

# 添加发布说明
edp -release --release-version v09001 --step pnr_innovus.postroute --note "Initial release for postroute"

# Release 多个步骤
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute

# Release 整个 flow（从 dependency.yaml 读取所有步骤）
edp -release --release-version v09001 --step pnr_innovus

# 如果版本号已存在，自动添加时间戳创建新版本（默认行为）
edp -release --release-version v09001 --step pnr_innovus.postroute
# 如果 v09001 已存在，会自动创建 v09001_20240115_103045

# 追加到现有版本（需要明确指定 --append）
edp -release --release-version v09001 --step pnr_innovus.route --append
# 如果 v09001 已存在，会将新步骤追加到现有版本

# 覆盖已存在的步骤（需要配合 --append 使用）
edp -release --release-version v09001 --step pnr_innovus.postroute --append --overwrite

# 严格模式：如果版本号已存在则报错
edp -release --release-version v09001 --step pnr_innovus.postroute --strict
```

### 版本号规则

- **基础版本号**：用户指定的版本号（如 `v09001`）
- **默认行为**：如果版本号已存在，自动添加时间戳后缀创建新版本（格式：`YYYYMMDD_HHMMSS`）
- **追加模式**：使用 `--append` 选项时，如果版本号已存在但包含不同的步骤，允许追加到现有版本
- **覆盖模式**：使用 `--append --overwrite` 选项可以覆盖已存在的步骤
- **示例**：
  - `v09001` - 第一次创建，无冲突
  - `v09001_20240115_103045` - 如果 v09001 已存在，自动添加时间戳创建新版本（默认行为）
  - `v09001_20240115_143022` - 同一天多次发布，使用时间戳区分
  - 追加示例：`edp -release --release-version v09001 --step pnr_innovus.route --append` 会将新步骤追加到现有的 v09001

## 配置文件

### 在 flow 配置中定义文件映射

每个 flow 需要在 `config.yaml` 中定义 `release` 配置：

```yaml
# edp_center/config/{foundry}/{node}/{project}/pnr_innovus/config.yaml
pnr_innovus:
  default:
    lsf: 1
    tool_opt: "innovus -file"
    # ... 其他 LSF 配置

release:
  # 文件到目录的映射规则（通用规则，适用于所有 step）
  file_mappings:
    def: "**/*.def"              # 递归搜索所有 .def 文件
    db: "**/*.db"                # 数据库文件
    sdf: "**/*.sdf"              # 时序信息文件
    spef: "**/*.spef"            # 寄生参数文件
    verilog: "**/*.v **/*.vg"    # Verilog 网表文件
    config: "**/*.mmc.tcl **/*.sdc config/**/*.tcl"  # 配置文件
    timing: "timing/**/*.csv"    # 时序数据（CSV 格式）
  
  # 保持目录结构的目录
  keep_structure:
    - "timing"    # timing 目录保持结构
    - "config"    # config 目录保持结构
  
  # 按 step 的特定规则（可选，增量覆盖通用规则）
  step_rules:
    postroute:
      file_mappings:
        def: "*.def output/*.def"  # 覆盖通用规则中的 def 映射
        db: "output/*.db"          # 覆盖通用规则中的 db 映射
        # 其他未指定的映射会保留通用规则
    
    floorplan:
      file_mappings:
        def: "*.def"               # 覆盖通用规则
        db: "output/*.db"
        # 排除某些文件类型
        sdf: null                  # 排除 sdf 文件
        spef: null                 # 排除 spef 文件
```

### 文件路径模式

支持以下文件路径模式：

- `*.def` - 匹配根目录下的所有 .def 文件（不递归）
- `output/*.def` - 匹配 `output/` 目录下的所有 .def 文件（不递归）
- `**/*.def` - 递归匹配所有目录下的所有 .def 文件
- `a_dir/**/*.def` - 递归匹配 `a_dir/` 及其所有子目录下的所有 .def 文件
- `@libs` - 复制整个 `libs/` 目录（使用 `@` 前缀）

### 排除文件类型

有两种方式可以排除不需要 release 的文件类型：

**方式 1：设置为 null（推荐）**

```yaml
floorplan:
  file_mappings:
    sdf: null      # 排除 sdf 文件
    spef: null     # 排除 spef 文件
```

**方式 2：使用 exclude 列表**

```yaml
floorplan:
  file_mappings:
    def: "*.def"
  exclude:
    - "sdf"
    - "spef"
```

## 高级用法

### 覆盖配置

```bash
# 包含所有文件（忽略配置中的 file_mappings）
edp -release --release-version v09001 --step pnr_innovus.postroute --include-all

# 只包含指定的文件模式
edp -release --release-version v09001 --step pnr_innovus.postroute --include-patterns "*.def,*.sdf"

# 排除指定的文件模式
edp -release --release-version v09001 --step pnr_innovus.postroute --exclude-patterns "*.tmp,*.bak"
```

### 指定 block

```bash
# 如果不在 block 目录下，需要指定 block
edp -release --release-version v09001 --step pnr_innovus.postroute --release-block block1
```

## 工作流程示例

### 1. 运行流程

```bash
# 进入分支目录
cd /path/to/work/dongting/P85/block1/user1/main

# 运行 postroute 步骤
edp -run pnr_innovus.postroute
```

### 2. 创建 RELEASE

```bash
# 在同一个分支目录下
edp -release --release-version v09001 --step pnr_innovus.postroute --note "Postroute results for review"
```

### 3. 框架自动执行

框架会自动：
- 检查版本号是否已存在
- 如果存在，自动添加时间戳后缀（或报错，取决于选项）
- 如果版本已存在但包含不同的步骤，允许追加（追加模式）
- 从当前分支的 `data/pnr_innovus.postroute/` 目录复制数据
- 创建 RELEASE 目录结构：`RELEASE/block1/user1/v09001/data/pnr_innovus.postroute/`
- 复制文件到 `data/{flow}.{step}/` 目录下的各个子目录
- 复制 `lib_settings.tcl` 到 `data/{flow}.{step}/` 目录
- 创建 `release_note.txt`（如果提供，在根目录）
- 复制 `full.tcl` 到 `data/{flow}.{step}/` 目录（如果存在）
- **设置目录为只读**（chmod 555）
- **创建 .readonly 标记文件**

## 只读保护

RELEASE 目录一旦创建就会被设置为只读：

- **Unix 系统**：目录权限设置为 555，文件权限设置为 444
- **标记文件**：创建 `.readonly` 标记文件
- **防止修改**：防止用户意外修改已发布的数据

如果需要修改，需要管理员权限或手动修改权限。

## 最佳实践

1. **版本号命名**：使用有意义的版本号（如 `v09001` 表示版本 0.9.0.01）
2. **发布说明**：使用 `--note` 添加发布说明，方便后续查找
3. **配置文件**：在 flow 的 `config.yaml` 中定义完整的 `release` 配置
4. **Step 特定规则**：为不同 step 定义特定的文件映射规则
5. **排除不需要的文件**：明确排除不需要 release 的文件类型

## Timing Compare 功能

Timing Compare 功能允许你对比多个 release 版本的时序数据，帮助分析不同版本之间的性能差异。

### 使用 GUI 进行 Timing Compare

1. **选择版本**：
   - 在 RELEASE 版本管理 Tab 中，勾选要对比的版本的"Timing Compare"复选框
   - 可以同时选择多个版本（建议 2-4 个版本以便查看）

2. **打开对比窗口**：
   - 点击"对比"按钮
   - 会打开 Timing Compare 窗口

3. **查看对比结果**：
   - **SETUP/HOLD 数据**：按 PATH_TYPE（如 IN2REG, REG2REG）和 VIOLATION 类别分组显示
   - **DRV 数据**：按 DRV_TYPE 分组显示
   - **指标**：WNS（最差负时序）、TNS（总负时序）、VIO_PATHS（违规路径数）
   - **颜色编码**：绿色表示良好，黄色表示警告，红色表示严重违规
   - **缺失数据**：显示为 "NA"（灰色斜体）

4. **过滤和筛选**：
   - 使用左侧过滤器选择要显示的 Timing 类型（SETUP/HOLD/DRV）
   - 选择要显示的 Stage 和 Category
   - 调整字体大小以适应显示

### 数据来源

Timing Compare 会自动从每个 release 版本的 `data/{flow}.{step}/timing/` 目录中读取 CSV 文件：
- 同一 release 版本下的所有步骤（如 place, postroute）的数据会被合并
- 支持对比不同版本之间的数据
- 也支持对比同一版本内不同步骤的数据

## 常见问题

**Q: 如何查看已发布的 RELEASE？**

**方式 A: 使用 GUI（推荐）**

```bash
# 启动 GUI
edp -gui
```

在 RELEASE 版本管理 Tab 中，所有 release 版本会自动扫描并显示在版本列表中。

**方式 B: 使用命令行**

A: RELEASE 目录位于 `WORK_PATH/{project}/{version}/RELEASE/{block}/{user}/`，可以直接查看。

**Q: 可以修改已发布的 RELEASE 吗？**

A: 不建议修改。RELEASE 目录是只读的，如果需要修改，应该创建新的版本号。

**Q: 如何删除已发布的 RELEASE？**

A: 需要管理员权限或手动修改权限后删除。建议保留历史版本，除非确实需要删除。

**Q: RELEASE 会占用很多空间吗？**

A: RELEASE 只包含必要的文件，不会包含所有运行数据。可以通过配置文件控制哪些文件需要 release。

**Q: 可以发布多个 step 的结果到同一个版本吗？**

A: 可以！支持三种方式：
- **多次指定 `--step`**：`edp -release --release-version v09001 --step pnr_innovus.place --step pnr_innovus.postroute`
- **Release 整个 flow**：`edp -release --release-version v09001 --step pnr_innovus`（会从 `dependency.yaml` 读取所有步骤）
- **追加到现有版本**：如果版本已存在但包含不同的步骤，会自动追加到同一版本

多个步骤的数据会分别存储在 `data/{flow}.{step}/` 目录下，每个步骤的 `lib_settings.tcl` 和 `full.tcl` 独立存储。

---

**下一步**：
- 查看 [配置文件高级用法](06_configuration.md) 了解如何配置 release
- 查看 [最佳实践](07_best_practices.md) 了解更多使用技巧

[← 返回目录](../TUTORIAL.md)
