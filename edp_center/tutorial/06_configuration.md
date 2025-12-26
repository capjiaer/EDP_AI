# 配置文件高级用法

[← 返回目录](../TUTORIAL.md)

本文档介绍 EDP_AI 框架的配置文件高级用法，包括 YAML/Tcl 格式、变量保护、变量约束、自动生成的变量和 LSF 作业管理。

## 配置文件格式

### YAML 格式（推荐）

#### 简单方式（仅设置值）

```yaml
# user_config.yaml
pv_calibre:
  ipmerge:
    cpu_num: 16
```

#### 变量引用（Variable References）

YAML 配置文件支持变量引用功能，可以在配置文件中引用其他变量的值：

**简单变量引用**:
```yaml
base_cpu: 16
pv_calibre:
  ipmerge:
    cpu_num: $base_cpu        # 引用 base_cpu
  drc:
    cpu_num: ${base_cpu}      # 使用大括号（推荐）
```

**嵌套字典引用**:
```yaml
database:
  host: localhost
  port: 5432
db_url: "postgres://${database(host)}:${database(port)}/mydb"
```

**深层嵌套引用**:
```yaml
app:
  config:
    timeout: 30
timeout_value: $app(config,timeout)
```

**字符串中的变量引用**:
```yaml
prefix: "http://"
suffix: "/api"
api_url: "${prefix}example.com${suffix}"
```

**支持的变量引用格式**:
- `$var` - 简单变量引用
- `${var}` - 带大括号的变量引用（**推荐**，避免歧义）
- `$var(key)` - 嵌套字典引用（一层嵌套）
- `$var(key1,key2)` - 嵌套字典引用（多层嵌套）
- `"prefix_${var}_suffix"` - 字符串中的变量引用

**注意事项**:
- 变量展开后类型为字符串（即使原值是数字）
- 后面的变量可以引用前面定义的变量
- 多文件加载时，后面的文件可以引用前面文件定义的变量
- 推荐使用 `${var}` 格式，避免变量名歧义

#### 完整方式（带元数据：保护、约束、描述）

```yaml
# user_config.yaml
pv_calibre:
  ipmerge:
    cpu_num:
      value: 16
      protect: 1              # 布尔标志：启用保护，保护值为 16
      constraint: "8 16 32"    # 允许的值列表
      description: "CPU number for ipmerge step"
```

### Tcl 格式

#### 简单方式（仅设置值）

```tcl
# user_config.tcl
set pv_calibre(ipmerge,cpu_num) 16
```

#### 完整方式（带元数据：保护、约束、描述）

```tcl
# user_config.tcl
set pv_calibre(ipmerge,cpu_num) 16
set pv_calibre(ipmerge,cpu_num,protect) 1
set pv_calibre(ipmerge,cpu_num,constraint) "8 16 32"
set pv_calibre(ipmerge,cpu_num,description) "CPU number for ipmerge step"
```

**注意**：`protect` 字段只能是布尔值（`1`/`0`），表示是否启用保护。如果为 `1`，保护值为当前的 `value`。

### 变量名设计说明

**重要**：无论使用简单格式还是完整格式，变量名始终是 `pv_calibre(ipmerge,cpu_num)`，**不是** `pv_calibre(ipmerge,cpu_num,value)`。

**生成的 Tcl 代码**：
- 简单格式：`cpu_num: 16` → `set pv_calibre(ipmerge,cpu_num) 16`
- 完整格式：`cpu_num: {value: 16, protect: 1}` → 
  ```tcl
  set pv_calibre(ipmerge,cpu_num) 16              # 变量值在这里
  set pv_calibre(ipmerge,cpu_num,protect) 1       # 元数据（仅用于生成保护代码）
  ```

**用户使用**：
```tcl
# 在 Tcl 脚本中，始终使用 $pv_calibre(ipmerge,cpu_num) 访问变量
puts $pv_calibre(ipmerge,cpu_num)  # ✅ 输出 16
set result [expr $pv_calibre(ipmerge,cpu_num) * 2]  # ✅ 正确
```

### 格式混用规则

**简单格式和完整格式可以混用**（在不同配置文件中）：

**示例**：
```yaml
# common/config.yaml（Flow owner 使用简单格式）
pv_calibre:
  ipmerge:
    cpu_num: 16

# user_config.yaml（用户使用完整格式添加保护）
pv_calibre:
  ipmerge:
    cpu_num:
      value: 16      # 覆盖 common 的值（值相同）
      protect: 1     # 添加保护
```

**规则**：
- ✅ 不同配置文件可以混用两种格式
- ✅ 同一配置文件内，同一变量只能用一种格式
- ✅ 后加载的配置会覆盖先加载的配置
- ✅ 如果 `common/config.yaml` 用简单格式，`user_config.yaml` 想加保护，必须用完整格式（覆盖）

---

## 变量保护

使用 `protect` 字段可以保护变量不被修改：

```yaml
pv_calibre:
  ipmerge:
    cpu_num:
      value: 16
      protect: 1  # 布尔标志：启用保护，保护值为 16
```

**生成的保护代码**（在 `full.tcl` 最后）：
```tcl
edp_protect_var pv_calibre(ipmerge,cpu_num) 16
```

**运行时效果**：
```tcl
# 在 Tcl 脚本中
puts $pv_calibre(ipmerge,cpu_num)  # ✅ 输出 16
set pv_calibre(ipmerge,cpu_num) 32  # ❌ 被保护阻止，值仍为 16
```

---

## 变量约束

使用 `constraint` 字段可以限制变量的允许值：

```yaml
pv_calibre:
  ipmerge:
    cpu_num:
      value: 16
      constraint: "8 16 32"  # 只允许这三个值
```

**生成的约束代码**（在 `full.tcl` 最后）：
```tcl
edp_constraint_var pv_calibre(ipmerge,cpu_num) "8 16 32"
```

**运行时效果**：
```tcl
# 在 Tcl 脚本中
set pv_calibre(ipmerge,cpu_num) 8   # ✅ 允许（在约束列表中）
set pv_calibre(ipmerge,cpu_num) 16  # ✅ 允许（在约束列表中）
set pv_calibre(ipmerge,cpu_num) 32  # ✅ 允许（在约束列表中）
set pv_calibre(ipmerge,cpu_num) 4   # ❌ 报错：ERROR: Cannot set 'pv_calibre(ipmerge,cpu_num)' to '4'. Allowed values are: 8 16 32
```

**重要**：如果设置了不在约束列表中的值，会**直接报错并中断执行**，不会自动修正。这样可以及早发现配置错误，避免使用错误的值。

---

## 自动生成的变量

框架会自动生成一些变量，你可以在 Tcl 脚本中直接使用：

### 项目变量

```tcl
set project(project_name) "dongting"
set project(version) "P85"
set project(block_name) "block1"
set project(user_name) "user1"
set project(branch_name) "main"
set project(foundry) "SAMSUNG"
set project(node) "S8"
set project(init_path) "/home/user/WORK_PATH"
set project(work_path) "/home/user/WORK_PATH/dongting/P85/block1/user1/main/runs/pv_calibre/ipmerge"
set project(flow_name) "pv_calibre"
set project(step_name) "ipmerge"
```

### 平台变量

```tcl
set edp(edp_center_path) "/home/user/EDP_AI/edp_center"
set edp(config_path) "/home/user/EDP_AI/edp_center/config"
set edp(flow_path) "/home/user/EDP_AI/edp_center/flow"
```

**查看自动生成的变量**：

所有自动生成的变量都在 `runs/{flow_name}/{step_name}/full.tcl` 文件最后（确保不被配置文件覆盖）。

```bash
# 进入分支目录
cd /path/to/work/{project}/{version}/{block}/{user}/{branch}

# 查看 full.tcl 文件
cat runs/pv_calibre/ipmerge/full.tcl
```

---

## LSF 作业管理

### 基本配置

在配置文件中设置 LSF 相关参数：

```yaml
pv_calibre:
  ipmerge:
    lsf: 1                    # 启用 LSF 模式
    queue: "default"          # LSF 队列名称（注意：不是 lsf_queue）
    cpu_num: 16               # CPU 核心数（注意：不是 lsf_num_cores）
    memory: 4000              # 内存需求（MB）
    span: 1                   # 主机数量
    wait_lsf: 1               # 是否等待 LSF 作业完成（默认：1）
    lsf_opt: ""               # LSF 额外选项（可选，如 "-Ip"）
```

### 本地执行

```yaml
pv_calibre:
  ipmerge:
    lsf: 0  # 禁用 LSF，本地执行
```

### 命令执行模式

框架支持两种执行模式：

1. **本地执行**：直接在本地运行命令
2. **LSF 提交**：通过 `bsub` 提交到 LSF 集群

执行模式由 `lsf` 配置项决定：
- `lsf: 0` → 本地执行
- `lsf: 1` → LSF 提交

### 交互模式（-Ip）和日志记录

#### 自动交互模式选择

框架会根据作业类型自动选择是否使用交互模式（`-Ip`）：

1. **单个作业**（`wait_lsf: 1`，默认）：
   - 自动使用 `-Ip` 选项
   - 输出实时显示在终端，方便查看进度
   - 适合单个步骤的调试和监控

2. **多个作业并行**（`wait_lsf: 0`）：
   - 不使用 `-Ip` 选项，避免阻塞
   - 通过日志文件查看输出
   - 适合批量执行多个步骤

#### 手动配置交互模式

如果需要手动控制交互模式，可以在配置中设置 `lsf_opt`：

```yaml
pv_calibre:
  ipmerge:
    lsf: 1
    lsf_opt: "-Ip"  # 强制使用交互模式
    # 或
    lsf_opt: ""     # 强制不使用交互模式
```

**注意**：如果设置了 `lsf_opt`，框架会优先使用用户配置，而不是自动选择。

#### 自动加载模块和环境设置

框架提供了两种预处理机制，用于在不同阶段执行命令：

##### 1. `pre_cmd`：在执行节点执行（推荐用于模块加载）

`pre_cmd` 会在实际命令执行前运行，适用于加载模块、设置工具环境等：

```yaml
pnr_innovus:
  place:
    pre_cmd: "module load innovus/22.31"  # 在执行命令前自动加载模块
    # 或者多个命令
    pre_cmd: "module load innovus/22.31 && module load calibre/2023"
```

**执行位置**：
- **本地执行**：在当前 shell 中执行
- **LSF 执行**：在 LSF 作业内部执行（在执行节点）

**执行时机**：
- 在实际命令（如 `innovus -file place.tcl`）执行前
- 使用 `&&` 连接，如果 `pre_cmd` 失败，后续命令不会执行

**适用场景**：
- 加载模块（`module load`）
- 设置工具环境变量
- 执行命令前的准备工作

##### 2. `pre_lsf`：在提交节点执行

`pre_lsf` 会在 LSF 提交前执行，在提交节点运行：

```yaml
pnr_innovus:
  place:
    pre_lsf: "source /path/to/setup_env.sh"  # 在提交前设置环境
```

**执行位置**：
- **仅在 LSF 模式下有效**
- 在**提交节点**执行（运行 `bsub` 命令的节点）
- **不会**在执行节点执行

**执行时机**：
- 在 `bsub` 命令之前执行
- 命令顺序：`pre_lsf -> bsub -> ... -> command`

**适用场景**：
- 设置提交节点的环境变量（如 `export LSF_SERVERDIR=/path/to/lsf`）
- 在提交前做一些准备工作（如检查提交环境、设置 LSF 相关配置）
- 配置 LSF 提交环境（如设置 LSF 队列、资源限制等）
- 加载提交节点需要的工具（如 LSF 客户端工具）

**典型示例**：
```yaml
pnr_innovus:
  place:
    pre_lsf: "export LSF_SERVERDIR=/opt/lsf && export LSF_ENVDIR=/opt/lsf/conf"
    # 或者
    pre_lsf: "source /opt/lsf/conf/profile.lsf"  # 加载 LSF 环境
```

**注意**：
- `pre_lsf` 不会影响执行节点的环境
- 如果需要模块在执行节点加载，应该使用 `pre_cmd` 而不是 `pre_lsf`

##### 对比总结

| 配置项 | 执行位置 | 执行时机 | 适用场景 |
|--------|---------|---------|---------|
| `pre_cmd` | 执行节点（本地/LSF） | 命令执行前 | 加载模块、设置工具环境 |
| `pre_lsf` | 提交节点（仅LSF） | LSF 提交前 | 设置提交环境 |

**推荐用法**：
- 加载模块：使用 `pre_cmd`（在执行节点执行）
- 设置提交环境：使用 `pre_lsf`（在提交节点执行）

#### 日志记录

- 框架使用 `tee` 命令将输出同时写入日志文件和终端
- 不再使用 `bsub -o` 选项，避免重复记录
- 日志文件位置：`logs/{flow}.{step}/{flow}.{step}_YYYYMMDD_HHMMSS.log`
- 所有输出（包括标准输出和标准错误）都会记录到日志文件

#### 示例配置

```yaml
# 单个作业，使用交互模式（默认）
pnr_innovus:
  place:
    lsf: 1
    wait_lsf: 1        # 等待作业完成（默认）
    # 会自动使用 -Ip，输出实时显示

# 多个作业并行，不使用交互模式
pnr_innovus:
  place:
    lsf: 1
    wait_lsf: 0        # 不等待作业完成
    # 不会使用 -Ip，通过日志文件查看输出

# 手动控制交互模式
pnr_innovus:
  place:
    lsf: 1
    lsf_opt: "-Ip"     # 强制使用交互模式
    wait_lsf: 0        # 即使并行也使用交互模式

# 自动加载模块
pnr_innovus:
  place:
    pre_cmd: "module load innovus/22.31"  # 每次执行前自动加载模块
    lsf: 1  # 或 lsf: 0（本地执行也支持）
```

---

## 脚本文件类型支持

### Python 脚本支持

1. 在 `dependency.yaml` 中指定 `.py` 文件：

```yaml
- test_py:
    cmd: test_py.py
```

2. 在 `config.yaml` 中配置 `tool_opt`：

```yaml
pv_calibre:
  test_py:
    tool_opt: "python"
    lsf: 0
```

---

## RELEASE 配置

### 基本结构

在 flow 的 `config.yaml` 中添加 `release` 配置：

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
    timing: "timing/**/*.csv"    # 时序数据
  
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
    
    floorplan:
      file_mappings:
        def: "*.def"               # 覆盖通用规则
        sdf: null                  # 排除 sdf 文件
        spef: null                 # 排除 spef 文件
```

### 文件路径模式

- `*.def` - 匹配根目录下的所有 .def 文件（不递归）
- `output/*.def` - 匹配 `output/` 目录下的所有 .def 文件（不递归）
- `**/*.def` - 递归匹配所有目录下的所有 .def 文件
- `a_dir/**/*.def` - 递归匹配 `a_dir/` 及其所有子目录下的所有 .def 文件
- `@libs` - 复制整个 `libs/` 目录（使用 `@` 前缀）

### 排除文件类型

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

**详细说明**：请参考 [RELEASE 功能](10_release.md)

---

## 配置文件加载顺序

配置文件按以下顺序加载（后加载的覆盖先加载的）：

1. `common/main/init_project.yaml` - 通用项目初始化配置
2. `common/main/config.yaml` - 通用主配置
3. `common/{flow_name}/config.yaml` - 通用流程配置
4. `{project}/main/init_project.yaml` - 项目特定初始化配置
5. `{project}/main/config.yaml` - 项目特定主配置
6. `{project}/{flow_name}/config.yaml` - 项目特定流程配置
7. `user_config.yaml` 或 `user_config.tcl` - 用户配置（**最高优先级**）

**后加载的配置会覆盖先加载的配置。**

**变量引用规则**:
- ✅ 后面的配置文件可以引用前面配置文件定义的变量
- ✅ 同一配置文件内，后面的变量可以引用前面定义的变量
- ✅ 变量引用会在配置加载时自动展开

**示例**:
```yaml
# common/main/config.yaml
base_path: "/work/data"

# {project}/main/config.yaml
output_path: "${base_path}/output"  # ✅ 可以引用 common 中定义的 base_path
```

---

## 下一步

- 📚 [查看最佳实践](07_best_practices.md)
- 📦 [查看 RELEASE 功能](10_release.md)
- ❓ [查看常见问题](08_faq.md)

[← 返回目录](../TUTORIAL.md)

