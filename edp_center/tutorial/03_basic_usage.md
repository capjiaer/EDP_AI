# 基本使用

[← 返回目录](../TUTORIAL.md)

本文档介绍 EDP_AI 框架的基本使用方法，包括目录结构、基本命令和配置文件基础。

## 目录结构

EDP_AI 框架使用标准的目录结构来组织项目。简化版结构如下：

```
WORK_PATH/
└── {project}/              # 项目名称
    └── {version}/          # 项目版本
        └── {block}/         # 块名称
            └── {user}/      # 用户名
                └── {branch}/# 分支名称
                    ├── cmds/      # 命令脚本目录（生成的 Tcl 脚本）
                    ├── hooks/     # Hooks 目录（自定义 hooks）
                    ├── runs/      # 运行目录（运行时临时文件）
                    ├── logs/      # 日志目录（运行日志）
                    ├── rpts/      # 报告目录（报告文件）
                    ├── data/      # 数据目录（数据文件）
                    ├── user_config.yaml  # 用户配置文件（可选）
                    └── .run_info  # 运行信息文件（执行状态）
```

**关键目录说明**：
- `cmds/`: 存放处理后的最终脚本（展开 #import 后）
  - 格式：`cmds/{flow_name}/` - 每个 flow 一个目录
- `hooks/`: 存放自定义 hooks（step.pre, step.post 等）
  - 格式：`hooks/{flow_name}.{step_name}/` - 统一使用点号分隔
- `runs/`: 存放运行时生成的 full.tcl 和临时文件
  - 格式：`runs/{flow_name}.{step_name}/` - 统一使用点号分隔
- `logs/`: 存放运行日志
  - 格式：`logs/{flow_name}.{step_name}/` - 统一使用点号分隔
- `rpts/`: 存放报告文件
  - 格式：`rpts/{flow_name}.{step_name}/` - 统一使用点号分隔
- `data/`: 存放数据文件
  - 格式：`data/{flow_name}.{step_name}/` - 统一使用点号分隔

**目录命名规则**：
- 除 `cmds/` 外，所有目录统一使用 `{flow_name}.{step_name}` 格式（点号分隔）
- `cmds/` 使用 `{flow_name}` 格式，因为每个 flow 只有一个 cmds 目录

---

## 基本命令

### 1. 项目初始化 (`edp_init -init`)

初始化项目工作空间：

```bash
# 方式 A: GUI 图形界面（推荐新手）
edp_init -init --gui

# 方式 B: 命令行（需要先创建 config.yaml）
edp_init -init
```

### 2. 创建分支 (`edp -b` / `edp -branch`)

创建新的工作分支：

```bash
# 进入 user 目录
cd /path/to/work/{project}/{version}/{block}/{user}

# 创建新分支
edp -b my_branch

# 从已有分支创建
edp -b new_branch --from-branch-step "main:pnr_innovus.init"
```

### 3. 统一图形界面 (`edp -gui`)

启动统一的图形界面，包含项目初始化、RELEASE 管理等功能：

```bash
# 启动统一 GUI
edp -gui
```

**GUI 功能**：

1. **项目初始化 Tab**：
   - 图形化配置项目初始化参数
   - 选择 EDP Center 路径和 Work Path 路径
   - **自动检测 Work Path**：如果当前目录在已初始化的项目下，GUI 会自动从 `.edp_version` 文件推断并设置正确的 WORK_PATH 根目录
   - 从下拉列表选择项目（支持刷新按钮手动刷新项目列表）
   - 配置 Block 和 User（支持添加/删除行）
   - 支持从配置文件加载参数
   - 支持自动推断参数（从 `.edp_version` 文件或路径）
   - 实时显示初始化日志

2. **RELEASE 版本管理 Tab**：
   - 扫描并显示所有 release 版本
   - 查看 release 状态和详细信息
   - 创建新的 release（支持多步骤选择）
   - 版本内容树形浏览和文件预览
   - Timing Compare 功能（对比多个版本的时序数据）

**界面布局**：

- **过滤器**：按项目、版本、Block、User 筛选 release 列表
- **版本列表**：显示所有符合条件的 release 版本，支持选择进行 Timing Compare
- **版本详情**：显示选中版本的详细信息
- **Version Overview**：树形结构显示版本目录内容，点击文件可预览内容

**依赖要求**：

```bash
pip install PyQt5
```

### 4. 运行流程 (`edp -run`)

运行指定的流程步骤：

```bash
# 进入分支目录
cd /path/to/work/{project}/{version}/{block}/{user}/{branch}

# 运行单个步骤（自动推断项目信息）
edp -run pv_calibre.ipmerge

# 运行单个步骤（显式指定项目信息）
edp -run pv_calibre.ipmerge -prj dongting --foundry SAMSUNG --node S8

# 运行单个步骤（指定完整路径信息）
edp -run pv_calibre.ipmerge -prj dongting -v P85 --block block1 --user zhangsan --branch branch1

# 演示模式（不实际执行）
edp -run pv_calibre.ipmerge --dry-run

# Debug 模式（交互式调试，适用于 sub_steps）
edp -run pnr_innovus.place --debug

# 执行多个步骤（从某个步骤到另一个步骤）
edp -run --from pnr_innovus.place --to pv_calibre.drc
# 或使用短别名
edp -run -fr pnr_innovus.place -to pv_calibre.drc

# 从某个步骤开始执行所有后续步骤
edp -run --from pnr_innovus.place
# 或使用短别名
edp -run -fr pnr_innovus.place

# 执行到某个步骤（执行所有前置步骤）
edp -run --to pv_calibre.drc
# 或使用短别名
edp -run -to pv_calibre.drc
```

#### 失败处理策略 (`--failure-strategy`)

当执行多个步骤时，可以指定失败处理策略：

```bash
# strict（默认）：前置步骤失败，后续步骤不执行
edp -run --from SA --to S3 --failure-strategy strict
# 或使用短别名
edp -run -fr SA -to S3 -fs strict

# skip-downstream：跳过失败步骤的下游，其他独立路径继续执行
edp -run --from SA --to S3 --failure-strategy skip-downstream
# 或使用短别名
edp -run -fr SA -to S3 -fs skip-downstream

# stop：遇到第一个失败就立即停止所有步骤
edp -run --from SA --to S3 --failure-strategy stop
# 或使用短别名
edp -run -fr SA -to S3 -fs stop

# continue：即使前置步骤失败也继续执行（不推荐，可能产生错误结果）
edp -run --from SA --to S3 --failure-strategy continue
# 或使用短别名
edp -run -fr SA -to S3 -fs continue
```

**策略说明**：

- **strict**（默认）：最安全的策略，确保数据完整性。如果前置步骤失败，后续步骤不会执行。
- **skip-downstream**：智能策略，适合多路径并行流程。只跳过失败步骤的直接下游，其他独立路径继续执行。
- **stop**：快速失败策略，遇到第一个失败就停止，节省时间和资源。
- **continue**：继续执行策略，即使前置步骤失败也继续。**注意**：这可能导致错误的结果，请谨慎使用。

**示例场景**：

假设有以下依赖关系：
```
SA -> S2.1 -> S3
SB -> S2.2 -> S3
SC -> S2.3 -> S4
```

如果 `S2.2` 失败：

- **strict**：`S3` 不执行（因为需要 `S2.2`），`S4` 继续执行（不依赖 `S2.2`）
- **skip-downstream**：`S3` 跳过（因为所有前置路径中 `S2.2` 失败），`S4` 继续执行
- **stop**：立即停止，`S3` 和 `S4` 都不执行
- **continue**：`S3` 和 `S4` 都继续执行（可能产生错误结果）

#### 日志文件

每次执行步骤时，EDP_AI 会在 `logs/{flow_name}.{step_name}/` 目录下生成两类日志文件：

1. **EDP 运行日志** (`edp_run_YYYYMMDD_HHMMSS.log`)
   - 记录框架执行过程，包括脚本处理、命令执行、状态更新等
   - 包含所有终端输出，便于调试和追踪问题
   - 文件名包含时间戳，格式：`edp_run_20251119_133549.log`

2. **工具输出日志** (`{flow_name}.{step_name}_YYYYMMDD_HHMMSS.log`)
   - 记录工具（如 `innovus`、`calibre` 等）的标准输出和错误输出
   - 文件名保持与步骤名称格式一致（使用点号分隔），格式：`pnr_innovus.place_20251119_133549.log`

**日志文件位置**：
```
{branch_dir}/logs/{flow_name}.{step_name}/
├── edp_run_20251119_150000.log           # 最新的 EDP 框架运行日志
├── pnr_innovus.place_20251119_150000.log # 最新的工具输出日志
└── old_logs/                              # 历史日志目录
    ├── edp_run_20251119_140000.log
    ├── edp_run_20251119_130000.log
    ├── pnr_innovus.place_20251119_140000.log
    └── pnr_innovus.place_20251119_130000.log
```

**自动日志管理**：
- 每次运行新步骤时，系统会自动将旧的日志文件移动到 `old_logs/` 目录
- `logs/{flow_name}.{step_name}/` 目录下只保留最新的日志文件，便于快速查找
- 历史日志文件保存在 `old_logs/` 目录中，不会丢失，方便历史回溯

**查看日志**：
```bash
# 查看最新的 EDP 运行日志（当前目录）
ls -lt logs/pnr_innovus.place/edp_run_*.log | head -1

# 查看最新的工具输出日志（当前目录）
ls -lt logs/pnr_innovus.place/pnr_innovus.place_*.log | head -1

# 查看日志内容
tail -f logs/pnr_innovus.place/edp_run_20251119_150000.log

# 查看历史日志（old_logs 目录）
ls -lt logs/pnr_innovus.place/old_logs/edp_run_*.log | head -5
```

**时间戳的作用**：
- 每次运行都会生成新的日志文件，不会覆盖之前的日志
- 便于对比多次运行的结果，追踪问题变化
- 历史日志自动归档到 `old_logs/` 目录，保持主目录整洁

### 4. 查看信息 (`edp -info` / `edp_info -info`)

查看可用的流程和步骤：

```bash
# 查看所有流程（统一使用 edp 命令）
edp -info
# 或使用短别名
edp -i

# 查看指定流程的步骤
edp -info pv_calibre
# 或使用短别名
edp -i pv_calibre

# 也可以使用 edp_info 命令（功能相同）
edp_info -info
edp_info -i pv_calibre
```

### 4.1. 查看历史记录 (`edp -history`)

查看运行历史记录：

```bash
# 查看所有历史记录
edp -history

# 查看指定步骤的历史记录
edp -history pnr_innovus.place

# 限制显示数量
edp -history --limit 10

# 过滤状态
edp -history --status success    # 只显示成功的记录
edp -history --status failed     # 只显示失败的记录

# 按时间范围过滤
edp -history --from-date 2025-01-01 --to-date 2025-01-31
```

**说明**：
- 历史记录存储在 `.run_info` 文件中
- 显示每次运行的详细信息：时间戳、状态、持续时间、资源使用等
- 支持按步骤、状态、时间范围过滤

### 4.2. 性能统计 (`edp -stats`)

查看性能统计信息：

```bash
# 查看所有步骤的统计
edp -stats

# 查看指定步骤的统计
edp -stats pnr_innovus.place

# 显示性能趋势
edp -stats --trend

# 导出统计报告
edp -stats --export report.html
```

**说明**：
- 统计信息包括：平均执行时间、CPU 使用率、内存使用、成功率等
- 支持按步骤分组统计
- 可以显示性能趋势，帮助识别性能问题

### 4.3. 配置对比和回滚 (`edp -rollback`)

对比不同运行的配置差异，帮助定位问题：

```bash
# 对比最后一次成功和最后一次失败（默认）
edp -rollback

# 对比指定步骤的最后一次成功和最后一次失败
edp -rollback pnr_innovus.place

# 对比指定索引的运行
edp -rollback --compare-index 1 3

# 预览模式（不实际回滚）
edp -rollback --preview
# 或
edp -rollback --rollback-dry-run

# 对比不同分支的配置
edp -rollback --compare-branch main
```

**说明**：
- 对比两次运行的 `full.tcl` 配置差异
- 显示新增、删除、修改的配置变量
- 帮助快速定位配置变化导致的问题
- 每次运行都会自动备份 `full.tcl` 到 `runs/{flow}.{step}/backups/` 目录

### 4.4. 验证执行结果 (`edp -validate`)

验证执行结果和生成验证报告：

```bash
# 验证最后一次执行
edp -validate

# 验证指定步骤的执行
edp -validate pnr_innovus.place

# Timing Compare（对比两个分支的结果）
edp -validate --timing-compare branch1 branch2

# 生成验证报告
edp -validate --report
```

**说明**：
- 验证执行结果的完整性和正确性
- 支持 Timing Compare 功能，对比不同分支的结果
- 可以生成详细的验证报告

### 5. 创建项目结构 (`edp_init -create-project`)

在 EDP Center 中创建新项目的文件夹结构：

```bash
# 创建新项目的文件夹结构
edp_init -create-project PROJECT_NAME FOUNDRY NODE

# 示例
edp_init -create-project new_prj TSMC n8
```

### 6. 创建 RELEASE (`edp -release`)

发布运行结果到共享目录：

```bash
# 进入分支目录
cd /path/to/work/{project}/{version}/{block}/{user}/{branch}

# 基本用法：发布单个步骤的结果
edp -release --release-version v09001 --step pnr_innovus.postroute

# 添加发布说明
edp -release --release-version v09001 --step pnr_innovus.postroute --note "Initial release"

# Release 多个步骤
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute

# Release 整个 flow（从 dependency.yaml 读取所有步骤）
edp -release --release-version v09001 --step pnr_innovus

# 如果版本号已存在，自动添加时间戳创建新版本（默认行为）
# 如果 v09001 已存在，会自动创建 v09001_20240115_103045

# 追加到现有版本（需要明确指定 --append）
edp -release --release-version v09001 --step pnr_innovus.route --append

# 覆盖已存在的步骤（需要配合 --append 使用）
edp -release --release-version v09001 --step pnr_innovus.postroute --append --overwrite

# 严格模式：如果版本号已存在则报错
edp -release --release-version v09001 --step pnr_innovus.postroute --strict
```

**说明**：
- RELEASE 目录位于 `WORK_PATH/{project}/{version}/RELEASE/{block}/{user}/{version}/`
- 统一使用 `data/{flow}.{step}/` 结构，每个步骤的数据独立存储
- 每个步骤的 `lib_settings.tcl` 和 `full.tcl` 存储在各自的 step 目录下
- 发布后的数据会被设置为只读，防止意外修改
- 详细用法请参考 [RELEASE 功能](10_release.md)

### 7. 生成库配置文件 (`edp -lib`)

生成库配置文件（lib_config.tcl）：

```bash
# 基本用法：处理单个STD库
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/std_library_dir \
  --lib-type STD \
  --lib-output-dir /path/to/output

# 批量处理多个库
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 \
  --lib-type STD \
  --lib-output-dir /path/to/output

# 从文件读取库路径列表
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-paths-file lib_paths.txt \
  --lib-type STD \
  --lib-output-dir /path/to/output

# 指定特定版本
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --lib-version 2.00A \
  --lib-output-dir /path/to/output

# 处理所有版本（最新版本生成 lib_config.tcl，其他版本生成 lib_config.{version}.tcl）
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --lib-all-versions \
  --lib-output-dir /path/to/output

# 处理IP库
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/ip_library_dir \
  --lib-type IP \
  --lib-output-dir /path/to/output

# 启动图形界面
edp -lib --lib-gui
```

**说明**：
- `--lib-type`: 库类型，必须指定（STD: 标准单元库, IP: IP库, MEM: 内存库）
- `--foundry`: Foundry名称（如 Samsung, SMIC, TSMC）
- `--node`: 工艺节点（如 ln08lpu_gp）
- `--lib-path`: 库目录路径（可指定多个，或使用 `--lib-paths-file`）
- `--lib-output-dir`: 输出目录（必须指定）
- `--lib-version`: 指定版本号（可选，默认使用最新版本）
- `--lib-all-versions`: 处理所有版本（与 `--lib-version` 互斥）
- `--lib-gui`: 启动图形界面（推荐新手使用）

**输出结构**：
```
{output_dir}/{lib_name}/
├── lib_config.tcl         # 最新版本（默认）
├── lib_config.1.01a.tcl   # 其他版本（如果使用 --lib-all-versions）
└── lib_config.1.00B.tcl
```

**详细用法**：请参考 `edp_center/packages/edp_libkit/README.md`

### 8. 查看教程 (`edp -tutor` 或 `edp_info -tutorial`)

查看 HTML 教程（普通用户）：

```bash
# 方式 A: 使用快捷命令
edp -tutor                    # 打开已生成的教程 HTML（普通用户）
edp -tutor --browser firefox # 指定浏览器（firefox, chrome, chromium）
edp -tutor --open-dir        # 只打开教程目录

# 方式 B: 使用完整命令
edp_info -tutorial           # 打开已生成的教程 HTML
edp_info -tutorial --browser firefox
edp_info -tutorial --open-dir
```

**更新教程 HTML（仅 PM 使用）**：

```bash
# 更新教程 HTML（需要 edp_center 写入权限）
edp -tutor --update          # 更新教程 HTML（自动检测修改）
edp -tutor --update --force  # 强制重新生成所有 HTML 文件
edp_info -tutorial --update
edp_info -tutorial --update --force
```

**说明**：

- **普通用户**：直接使用 `edp -tutor` 打开已生成的教程 HTML（位于 `edp_center/tutorial/index.html`）
- **PM（项目管理员）**：使用 `edp -tutor --update` 更新教程 HTML
- HTML 文件统一生成在 `edp_center/tutorial/` 目录下，由 PM 负责维护
- 如果 HTML 文件不存在，系统会提示联系 PM 更新
- `edp -tutor` 是 `edp_info -tutorial` 的快捷方式，功能完全相同

---

## 配置文件基础

### 配置文件位置

配置文件按优先级从低到高加载：

1. `common/main/config.yaml` - 通用主配置
2. `common/{flow}/config.yaml` - 通用流程配置
3. `{project}/main/config.yaml` - 项目特定主配置
4. `{project}/{flow}/config.yaml` - 项目特定流程配置
5. `user_config.yaml` 或 `user_config.tcl` - 用户配置（**最高优先级**）

**后加载的配置会覆盖先加载的配置。**

### 基本格式

#### YAML 格式（推荐）

```yaml
pv_calibre:
  ipmerge:
    cpu_num:
      value: 16
      description: "CPU 数量"
    design_file:
      value: "design.gds"
      description: "设计文件路径"
```

#### Tcl 格式

```tcl
set pv_calibre(ipmerge,cpu_num) 16
set pv_calibre(ipmerge,design_file) "design.gds"
```

### 用户配置文件

在分支目录下创建 `user_config.yaml` 或 `user_config.tcl` 来覆盖默认配置：

```bash
# 进入分支目录
cd /path/to/work/{project}/{version}/{block}/{user}/{branch}

# 创建用户配置文件
vim user_config.yaml
```

---

## 基本工作流

典型的 EDP_AI 工作流程：

```
1. 初始化项目
   ↓
   edp_init -init
   
2. 创建分支（可选）
   ↓
   edp -b my_branch
   
3. 配置参数（可选）
   ↓
   编辑 user_config.yaml
   
4. 运行流程
   ↓
   edp -run {flow}.{step}
   
5. 查看结果
   ↓
   查看 logs/, rpts/, data/ 目录
   或使用 edp_info -info 查看流程信息
```

---

## 执行记录和资源信息 (`.run_info`)

每次执行步骤时，EDP_AI 会自动在分支目录下创建或更新 `.run_info` 文件，记录详细的执行信息。

### `.run_info` 文件位置

```
{branch_dir}/.run_info
```

### 记录的内容

`.run_info` 文件以 YAML 格式记录每次执行的详细信息：

```yaml
runs:
  - timestamp: '2025-11-10 18:09:44'
    flow: pv_calibre
    step: ipmerge
    utils: ['test', 'helper']
    hooks:
      step: ['step.pre', 'step.post']
      utils:
        helper: ['helper.pre', 'helper.post']
    # 执行状态和时长
    status: success  # success 或 failed
    duration: 3600.5  # 执行时长（秒）
    
    # LSF 作业信息（如果使用 LSF）
    lsf_job_id: "12345"
    
    # 资源使用信息（如果使用 LSF）
    resources:
      cpu_used: 16  # 使用的 CPU 总数
      cpu_time_per_cpu: 225.5  # 每个 CPU 的使用时间（秒）
      peak_memory: 32000  # 峰值内存（MB）
      hosts:  # 使用的机器列表（包含每台主机的 CPU 数量）
        - host: host1
          cpus: 8
        - host: host2
          cpus: 8
      queue: "normal"  # LSF 队列名称
      start_time: "2025-11-10 18:09:44"
      end_time: "2025-11-10 19:09:44"
    
    # 错误信息（如果执行失败）
    error: null
```

### 记录的信息说明

1. **基本信息**
   - `timestamp`: 执行时间戳
   - `flow`: 流程名称
   - `step`: 步骤名称
   - `hooks`: 使用的 hooks 信息（step hooks 和 sub_step hooks）

**注意**：`utils` 字段已废弃（已移除 `#import util` 机制），不再记录。

2. **执行状态**
   - `status`: 执行状态（`success` 或 `failed`）
   - `duration`: 执行时长（秒）

3. **LSF 信息**（如果使用 LSF）
   - `lsf_job_id`: LSF 作业 ID
   - `resources`: 资源使用信息
     - `cpu_used`: 使用的 CPU 总数
     - `cpu_time_per_cpu`: 每个 CPU 的使用时间（秒）
     - `peak_memory`: 峰值内存（MB）
     - `hosts`: 使用的机器列表，每台机器包含：
       - `host`: 主机名
       - `cpus`: 该主机使用的 CPU 数量
     - `queue`: LSF 队列名称
     - `start_time` / `end_time`: 开始和结束时间

4. **错误信息**
   - `error`: 错误信息（如果执行失败）

### 用途

`.run_info` 文件可以用于：

- **历史查询**：查看某个步骤的执行历史
- **性能分析**：分析执行时间和资源使用趋势
- **问题排查**：查看失败步骤的错误信息
- **资源统计**：统计 CPU、内存使用情况
- **审计追踪**：记录每次执行的详细信息

### 实际示例

以下是一个完整的 `.run_info` 文件示例，包含多个执行记录：

```yaml
runs:
  # 第一次执行：LSF 作业，成功
  - timestamp: '2025-11-10 18:09:44'
    flow: pv_calibre
    step: ipmerge
    hooks:
      step: ['step.pre', 'step.post']
    status: success
    duration: 3600.5
    lsf_job_id: "12345"
    resources:
      cpu_used: 16
      cpu_time_per_cpu: 225.5
      peak_memory: 32000
      hosts:
        - host: host1
          cpus: 8
        - host: host2
          cpus: 8
      queue: "normal"
      start_time: "2025-11-10 18:09:44"
      end_time: "2025-11-10 19:09:44"
    error: null

  # 第二次执行：本地执行，成功
  - timestamp: '2025-11-10 20:15:30'
    flow: pnr_innovus
    step: init
    hooks:
      step: []
    status: success
    duration: 120.3
    # 本地执行没有 lsf_job_id 和 resources

  # 第三次执行：LSF 作业，失败
  - timestamp: '2025-11-10 21:30:15'
    flow: pv_calibre
    step: drc
    hooks:
      step: ['step.pre']
    status: failed
    duration: 1800.2
    lsf_job_id: "12346"
    resources:
      cpu_used: 8
      cpu_time_per_cpu: 225.0
      peak_memory: 16000
      hosts:
        - host: host3
          cpus: 8
      queue: "normal"
      start_time: "2025-11-10 21:30:15"
      end_time: "2025-11-10 22:00:15"
    error: "DRC violations found: 125 errors"

  # 第四次执行：LSF 作业，多主机
  - timestamp: '2025-11-11 09:00:00'
    flow: pnr_innovus
    step: place
    hooks:
      step: ['step.pre', 'step.post']
      sub_steps:
        config_design: ['config_design.tcl.pre', 'config_design.tcl.post']
    status: success
    duration: 7200.0
    lsf_job_id: "12347"
    resources:
      cpu_used: 32
      cpu_time_per_cpu: 225.0
      peak_memory: 64000
      hosts:
        - host: host1
          cpus: 16
        - host: host2
          cpus: 16
      queue: "high_mem"
      start_time: "2025-11-11 09:00:00"
      end_time: "2025-11-11 11:00:00"
    error: null
```

### 查看执行记录

```bash
# 查看 .run_info 文件内容
cat .run_info

# 或使用 YAML 查看工具（如果安装了 yq）
cat .run_info | yq

# 或使用 Python 查看（格式化输出）
python -c "import yaml; import sys; print(yaml.dump(yaml.safe_load(open('.run_info')), allow_unicode=True, default_flow_style=False))"
```

### 注意事项

- **自动更新**：`.run_info` 文件会自动更新，每次执行步骤时都会追加新的记录
- **文件大小**：随着执行次数增加，文件会逐渐变大，建议定期备份或清理旧记录
- **LSF vs 本地**：LSF 执行会记录详细的资源信息，本地执行只记录基本信息和执行时长
- **失败记录**：失败的执行会记录 `error` 字段，包含错误信息，便于问题排查

---

## 下一步

- 🔧 [了解 Hooks 机制和 #import 指令](04_hooks_and_imports.md)
- 🐛 [学习 Sub_steps 和 Debug 模式](05_sub_steps_and_debug.md)
- ⚙️ [掌握配置文件高级用法](06_configuration.md)

[← 返回目录](../TUTORIAL.md)

