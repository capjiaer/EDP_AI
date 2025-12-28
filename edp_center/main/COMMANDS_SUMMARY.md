# EDP 命令总结

## 📋 命令概览

EDP 框架提供统一的命令行接口，支持多种工作流管理功能。

### 主要命令（14个）

| 命令 | 别名 | 功能 | 状态 |
|------|------|------|------|
| `-b, -branch, --branch` | `-b` | 创建新的 branch（分支） | ✅ 推荐 |
| `-run, --run` | `-run` | 运行流程/步骤 | ✅ 推荐 |
| `-release, --release` | `-release` | 创建 RELEASE（发布运行结果） | ✅ 推荐 |
| `-lib, --lib` | `-lib` | 生成库配置文件（lib_config.tcl） | ✅ 推荐 |
| `-workflow, -workflow-web` | `-workflow` | 启动工作流 Web 服务器 | ✅ 推荐 |
| `-view, -dashboard` | `-view` | 启动 Metrics Dashboard | ✅ 推荐 |
| `-gui, --gui` | `-gui` | 启动统一图形界面 | ✅ 推荐 |
| `-graph, --graph` | `-graph` | 生成依赖关系可视化图 | ✅ 推荐 |
| `-tutorial, -tutor` | `-tutor` | 查看教程 | ✅ 推荐 |
| `-info, -i` | `-i` | 查看 flow 信息 | ✅ 推荐 |
| `-history` | - | 查看运行历史 | 🚧 开发中 |
| `-stats` | - | 性能统计 | 🚧 开发中 |
| `-rollback` | - | 回滚到历史状态 | 🚧 开发中 |
| `-validate` | - | 验证执行结果 | 🚧 开发中 |

### 旧版命令（已全部移除）

所有旧版命令已移除或整合到新的命令中。

---

## 🔧 详细命令说明

### 1. 创建分支 (`-b, -branch, --branch`)

**功能**：创建新的工作分支

**用法**：
```bash
# 自动推断参数（推荐，在 user 目录下运行）
edp -b branch1

# 显式指定参数
edp -b branch1 -prj dongting -v P85 --block block1 --user zhangsan

# 从已有分支创建新分支
edp -b branch2 --from-branch-step "branch1:pnr_innovus.init"
# 或使用别名
edp -b branch2 -from-step "branch1:pnr_innovus.init"
```

**参数**：
- `-b, -branch, --branch`: 分支名称（必需）
- `--from-branch-step, -from-step`: 从指定分支的步骤创建新分支
- 通用参数：`-prj, -v, --block, --user, --foundry, --node`

---

### 2. 运行流程 (`-run, --run`)

**功能**：执行流程步骤，生成 cmds 文件并运行

**用法**：
```bash
# 单个步骤（自动推断项目信息）
edp -run pv_calibre.ipmerge

# 单个步骤（显式指定项目信息）
edp -run pv_calibre.ipmerge -prj dongting --foundry SAMSUNG --node S8

# 单个步骤（指定完整路径信息）
edp -run pv_calibre.ipmerge -prj dongting -v P85 --block block1 --user zhangsan --branch branch1

# 执行多个步骤（从某个步骤到另一个步骤）
edp -run -fr pnr_innovus.place -to pv_calibre.drc

# 从某个步骤开始执行所有后续步骤
edp -run -fr pnr_innovus.place

# 执行到某个步骤（执行所有前置步骤）
edp -run -to pv_calibre.drc

# 演示模式（不实际执行）
edp -run pv_calibre.ipmerge --dry-run

# 调试模式（交互式调试）
edp -run pv_calibre.ipmerge --debug
```

**参数**：
- `-run, --run`: 要执行的步骤（格式：`<flow_name>.<step_name>`）
- `--from, -fr`: 起始步骤
- `--to, -to`: 结束步骤
- `--from-step, -fs`: 执行范围（`skip-upstream`, `skip-downstream`, `all`）
- `--work-path, -wpath`: 工作路径（默认：当前目录）
- `--config, -config, -cfg`: 配置文件路径
- `--dry-run, -dry_run`: 演示模式
- `-debug, --debug`: 调试模式
- 通用参数：`-prj, -v, --block, --user, --branch, --foundry, --node`

---

### 3. 创建 RELEASE (`-release, --release`)

**功能**：发布运行结果，创建版本化的发布包

**用法**：
```bash
# 发布单个步骤
edp -release --release-version v09001 --step pnr_innovus.postroute
# 或使用别名
edp -release -rver v09001 --step pnr_innovus.postroute

# 发布多个步骤
edp -release -rver v09001 --step pnr_innovus.place --step pnr_innovus.postroute

# 发布整个 flow
edp -release -rver v09001 --step pnr_innovus

# 添加发布说明
edp -release -rver v09001 --step pnr_innovus.postroute --note "Initial release"

# 严格模式（版本存在则报错）
edp -release -rver v09001 --step pnr_innovus.postroute --strict

# 追加到现有版本
edp -release -rver v09001 --step pnr_innovus.route --append

# 覆盖已存在的步骤
edp -release -rver v09001 --step pnr_innovus.postroute --append --overwrite

# 指定 block（使用别名）
edp -release -rver v09001 --step pnr_innovus.postroute -rblock block1
```

**参数**：
- `-release, --release`: 创建 RELEASE（标志）
- `--release-version, -rver`: RELEASE 版本号（如 `v09001`）
- `--step`: 要发布的步骤（可多次指定）
- `--release-block, -rblock`: 块名称（默认：从当前目录推断）
- `--note`: 发布说明
- `--strict`: 严格模式
- `--append`: 追加模式
- `--overwrite`: 覆盖模式
- `--include-all`: 包含所有文件
- `--include-patterns`: 包含的文件模式
- `--exclude-patterns`: 排除的文件模式

---

### 4. 生成库配置 (`-lib, --lib`)

**功能**：生成库配置文件（lib_config.tcl）

**用法**：
```bash
# 生成单个库的配置
edp -lib --foundry Samsung --node ln08lpu_gp --lib-path /path/to/lib --lib-type STD --lib-output-dir /path/to/output
# 或使用别名
edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD -odir /path/to/output

# 批量处理多个库
edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib1 /path/to/lib2 --lib-type STD -odir /path/to/output

# 指定版本号
edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD --lib-version 2.00A -odir /path/to/output

# 处理所有版本
edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD --lib-all-versions -odir /path/to/output

# 启动图形界面
edp -lib --lib-gui
```

**参数**：
- `-lib, --lib`: 生成库配置（标志）
- `--lib-path, -lpath`: 库目录路径（可指定多个）
- `--lib-paths-file`: 包含库路径列表的文件
- `--lib-type`: 库类型（`STD`, `IP`, `MEM`，必需）
- `--lib-version`: 指定版本号
- `--lib-all-versions`: 处理所有版本
- `--lib-output-dir, -odir`: 输出目录（必需）
- `--lib-array-name`: 数组变量名（默认：`LIBRARY`）
- `--lib-gui`: 启动图形界面
- `--lib-verbose, -lv`: 显示详细日志
- 通用参数：`--foundry, --node`

---

### 5. 工作流 Web 服务器 (`-workflow, -workflow-web`)

**功能**：启动工作流 Web 服务器，通过浏览器管理流程

**用法**：
```bash
# 启动 Web 服务器（默认端口 8888）
edp -workflow

# 指定端口
edp -workflow --web-port 9999
# 或使用别名
edp -workflow -port 9999

# 不自动打开浏览器
edp -workflow --no-open-browser
```

**参数**：
- `-workflow, -workflow-web, --workflow, --workflow-web`: 启动 Web 服务器（标志）
- `--web-port, -port`: Web 服务器端口（默认：`8888`）
- `--no-open-browser`: 不自动打开浏览器

---

### 6. Metrics Dashboard (`-view, -dashboard`)

**功能**：启动 Metrics Dashboard，查看运行数据分析

**用法**：
```bash
edp -view
```

**参数**：
- `-view, --view, -dashboard`: 启动 Dashboard（标志）

---

### 7. 统一图形界面 (`-gui, --gui`)

**功能**：启动统一图形界面，包含项目初始化、Timing Compare 等功能

**用法**：
```bash
edp -gui
```

**参数**：
- `-gui, --gui`: 启动 GUI（标志）

**依赖**：需要安装 `PyQt5`

---

### 8. 依赖关系可视化 (`-graph, --graph`)

**功能**：生成依赖关系可视化图

**用法**：
```bash
# 文本格式（默认）
edp -graph

# 图片格式
edp -graph --graph-format png --graph-output dependency.png
# 或使用别名
edp -graph -format png -output dependency.png

# Web 格式（交互式）
edp -graph -format web -output dependency.html --open-browser

# 聚焦特定步骤
edp -graph --graph-focus pnr_innovus.place

# 限制深度
edp -graph --graph-depth 3
```

**参数**：
- `-graph, --graph`: 生成依赖图（标志）
- `--graph-format, --format, -format`: 输出格式（`text`, `dot`, `png`, `svg`, `pdf`, `mermaid`, `web`，默认：`text`）
- `--graph-output, --output, -output`: 输出文件路径
- `--graph-focus, --focus-step`: 聚焦的步骤名称
- `--graph-depth, --depth`: 深度限制
- `--graph-layout, --layout`: Graphviz 布局引擎（`dot`, `neato`, `fdp`, `sfdp`, `twopi`, `circo`，默认：`dot`）
- `--graph-title, --title`: 图表标题（仅用于 web 格式）
- `--open-browser`: 自动打开浏览器（仅用于 web 格式）
- 通用参数：`-prj, --foundry, --node, --flow`

---

### 9. 查看教程 (`-tutorial, -tutor`)

**功能**：生成教程 HTML 索引并在浏览器中打开

**用法**：
```bash
# 打开已生成的教程（普通用户）
edp -tutor

# 更新教程 HTML（仅 PM 使用）
edp -tutor --update

# 强制重新生成所有 HTML
edp -tutor --update --force

# 指定浏览器
edp -tutor --browser firefox

# 打开教程目录
edp -tutor --open-dir
```

**参数**：
- `-tutorial, --tutorial, -tutor`: 查看教程（标志）
- `--open-dir`: 打开教程目录
- `--update, -update`: 更新教程 HTML 文件
- `--force`: 强制重新生成所有 HTML 文件
- `--browser`: 指定浏览器（如 `firefox`, `chrome`, `chromium`）

---

### 10. 查看 Flow 信息 (`-info, -i`)

**功能**：显示 flow 信息，查看步骤状态

**用法**：
```bash
# 查看所有可用的 flow
edp -info
# 或使用短别名
edp -i

# 查看指定 flow 下所有 step 的状态
edp -info pv_calibre
# 或使用短别名
edp -i pv_calibre
```

**参数**：
- `-i, -info, --info [FLOW]`: 显示 flow 信息（可选参数：不提供时显示所有 flow，提供 flow_name 时显示该 flow 下所有 step 的状态）
- 通用参数：`-prj, --foundry, --node`

---

### 11. 查看运行历史 (`-history`)

**功能**：查看运行历史记录

**状态**：🚧 开发中

**用法**：
```bash
# 查看所有历史
edp -history
# 或使用别名
edp -hist

# 查看指定步骤的历史
edp -hist pv_calibre.ipmerge

# 限制显示数量
edp -hist --limit 10

# 过滤状态
edp -hist --status failed

# 时间范围
edp -history --from-date 2024-01-01 --to-date 2024-12-31
```

**参数**：
- `-history, --history, -hist [FLOW.STEP]`: 查看运行历史（可选参数）
- `--limit`: 限制显示的历史记录数量
- `--status`: 过滤历史记录的状态（`success`, `failed`, `running`, `cancelled`）
- `--from-date`: 历史记录的起始时间（格式: YYYY-MM-DD）
- `--to-date`: 历史记录的结束时间（格式: YYYY-MM-DD）

---

### 12. 性能统计 (`-stats`)

**功能**：性能分析和统计

**状态**：🚧 开发中

**用法**：
```bash
# 查看所有步骤的统计
edp -stats

# 查看指定步骤的统计
edp -stats pv_calibre.ipmerge

# 显示性能趋势
edp -stats --trend

# 导出性能报告
edp -stats --export report.html
```

**参数**：
- `-stats, --stats [FLOW.STEP]`: 性能统计（可选参数）
- `--trend`: 显示性能趋势
- `--export`: 导出性能报告到文件

---

### 13. 回滚 (`-rollback`)

**功能**：回滚到历史状态

**状态**：🚧 开发中

**用法**：
```bash
# 回滚到上一次成功
edp -rollback

# 回滚到指定步骤的最后一次成功
edp -rollback pv_calibre.ipmerge

# 回滚到指定的历史记录索引
edp -rollback --index 5

# 回滚到指定时间点
edp -rollback --to-time "2024-01-01 12:00:00"

# 预览回滚操作（不实际执行）
edp -rollback --preview
```

**参数**：
- `-rollback, --rollback [FLOW.STEP]`: 回滚到历史状态（可选参数）
- `--index`: 回滚到指定的历史记录索引
- `--to-time`: 回滚到指定时间点（格式: YYYY-MM-DD HH:MM:SS）
- `--preview`: 预览回滚操作，不实际执行

---

### 14. 结果验证 (`-validate`)

**功能**：验证执行结果

**状态**：🚧 开发中

**用法**：
```bash
# 验证最后一次执行
edp -validate

# 验证指定步骤
edp -validate pv_calibre.ipmerge

# Timing compare：对比两个分支的结果
edp -validate --timing-compare branch1 branch2
# 或使用别名
edp -val -tcompare branch1 branch2

# 生成验证报告
edp -validate --report
```

**参数**：
- `-validate, --validate, -val [FLOW.STEP]`: 验证执行结果（可选参数）
- `--timing-compare, -tcompare BRANCH1 BRANCH2`: Timing compare：对比两个分支的结果
- `--report`: 生成验证报告

---

## 🔄 旧版命令（向后兼容）

**已移除的命令**：
- `load-workflow`: 已移除，请使用 `edp -info` 或 `edp -i` 查看流程信息

---

## 🆕 项目初始化命令（`edp_init`）

**注意**：项目初始化使用独立的 `edp_init` 命令，不是主 `edp` 命令。

### 创建新项目（两步流程）

#### 步骤 1: 在 EDP Center 中创建项目结构

**功能**：在 `edp_center` 中创建新项目的文件夹结构（flow 和 config 目录）

**命令**：`edp_init -create-project`

**用法**：
```bash
# 创建新项目的文件夹结构
edp_init -create-project PROJECT_NAME FOUNDRY NODE

# 示例：创建一个名为 new_prj 的项目
edp_init -create-project new_prj TSMC n8
```

**说明**：
- 会在 `edp_center/flow/initialize/{foundry}/{node}/{project}/` 创建项目目录
- 会在 `edp_center/config/{foundry}/{node}/{project}/` 创建配置目录
- 从模板 `prj_example` 复制结构
- 已存在的文件不会被覆盖（安全模式）

---

#### 步骤 2: 在 WORK_PATH 中初始化工作空间

**功能**：在 `WORK_PATH` 下创建项目目录结构（类似 `dongting` 这样的项目）

**命令**：`edp_init -init`

**用法**：

**方式 A: 使用 GUI（推荐新手）**
```bash
# 进入 WORK_PATH 目录
cd /path/to/WORK_PATH

# 启动 GUI 初始化界面
edp_init -init --gui
```

**方式 B: 使用命令行**
```bash
# 1. 进入 WORK_PATH 目录
cd /path/to/WORK_PATH

# 2. 创建 config.yaml 文件（可选，如果不存在）
cat > config.yaml << 'EOF'
project:
  name: dongting          # 项目名称
  version: P85            # 项目版本
  blocks:                 # 块和用户列表
    block1: user1 user2   # block1 包含 user1 和 user2
    block2: user3 user4   # block2 包含 user3 和 user4
EOF

# 3. 执行初始化
edp_init -init

# 或显式指定参数
edp_init -init -prj dongting -v P85 --block block1 --user user1
```

**初始化结果**：
```
WORK_PATH/
└── dongting/              # 项目名称
    └── P85/               # 项目版本
        ├── .edp_version   # 项目版本信息文件
        ├── block1/        # 块1
        │   ├── user1/     # 用户1
        │   │   └── main/  # 默认分支（自动创建，包含完整目录结构）
        │   │       ├── cmds/      # 命令脚本目录（生成的 Tcl 脚本）
        │   │       ├── data/      # 数据目录（数据文件，用于 RELEASE）
        │   │       ├── hooks/     # Hooks 目录（自定义 hooks）
        │   │       ├── runs/      # 运行目录（运行时临时文件）
        │   │       ├── user_config.tcl   # 用户配置文件（TCL格式）
        │   │       └── user_config.yaml  # 用户配置文件（YAML格式）
        │   │       # 注意：logs/ 和 rpts/ 会在运行时自动创建
        │   └── user2/     # 用户2
        │       └── main/  # 默认分支（自动创建）
        └── block2/        # 块2
            ├── user3/
            │   └── main/
            └── user4/
                └── main/
```

**参数**：
- `-init`: 初始化项目（标志）
- `--gui`: 使用图形界面
- `--work-path`: WORK_PATH 根目录路径（默认：当前目录）
- `--config, -config, -cfg`: 配置文件路径（默认：`work_path/config.yaml`）
- `-prj, --project`: 项目名称
- `-v, --version`: 项目版本
- `--block, -blk`: 块名称
- `--user, -u`: 用户名称
- `--foundry`: 代工厂名称（可选）
- `--node`: 工艺节点（可选）

---

### 完整流程示例

**创建新项目 "new_prj" 的完整流程**：

```bash
# 步骤 1: 在 EDP Center 中创建项目结构
edp_init -create-project new_prj TSMC n8

# 步骤 2: 在 WORK_PATH 中初始化工作空间
cd /path/to/WORK_PATH
edp_init -init -prj new_prj -v P90 --block block1 --user user1

# 步骤 3: 创建分支（可选，main 分支已自动创建）
cd /path/to/WORK_PATH/new_prj/P90/block1/user1
edp -b my_branch

# 步骤 4: 运行流程
cd /path/to/WORK_PATH/new_prj/P90/block1/user1/my_branch
edp -run pv_calibre.ipmerge
```

---

## 🌐 通用参数

以下参数适用于所有命令：

| 参数 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `-prj, --project` | `-prj` | 项目名称 | `-prj dongting` |
| `-v, --version` | `-v` | 项目版本 | `-v P85` |
| `--foundry` | - | 代工厂名称 | `--foundry SAMSUNG` |
| `--node` | - | 工艺节点 | `--node S8` |
| `--block` | - | 块名称 | `--block block1` |
| `--user` | - | 用户名称 | `--user zhangsan` |
| `--branch` | `-b` | 分支名称 | `--branch branch1` |

**注意**：
- 这些参数支持自动推断（从当前目录或 `.edp_version` 文件）
- 命令行参数优先级最高
- 如果无法推断，需要显式指定

---

## 📊 命令统计

- **主要命令**：14 个（9 个已实现，5 个开发中）
- **旧版命令**：已全部移除
- **通用参数**：7 个
- **命令处理器**：13+ 个文件/模块

**注意**：所有功能已统一到 `edp` 命令，包括：
- 运行相关：`-run`, `-b`
- 信息查询：`-info`, `-history`, `-stats`, `-rollback`, `-validate`
- 其他功能：`-release`, `-lib`, `-workflow`, `-gui`, `-graph`, `-tutorial`

独立的 `edp_info` 命令已移除，请使用 `edp -info` 等命令。

---

## 🎯 推荐使用方式

### 日常使用（推荐）

```bash
# 1. 创建分支
edp -b branch1

# 2. 运行流程
edp -run pv_calibre.ipmerge

# 3. 创建 RELEASE（使用别名）
edp -release -rver v09001 --step pnr_innovus.postroute
```

### 高级使用

```bash
# 批量处理库配置
edp -lib --lib-gui

# 可视化依赖关系
edp -graph --graph-format web --open-browser

# Web 界面管理
edp -workflow
```

---

## 📝 注意事项

1. **参数推断**：大多数命令支持自动推断参数，建议在正确的工作目录下运行
2. **GUI 依赖**：`-gui` 需要 `PyQt5`，`-workflow` 需要 `Flask`
3. **命令组合**：通用参数可以与任何命令组合使用

---

## 🔗 相关文档

- **快速开始**：`edp_center/tutorial/02_getting_started.md`
- **基本使用**：`edp_center/tutorial/03_basic_usage.md`
- **API 文档**：`edp_center/docs/api/`
- **完整示例**：`edp_center/main/usage_examples.md`

---

*最后更新：2024年*

