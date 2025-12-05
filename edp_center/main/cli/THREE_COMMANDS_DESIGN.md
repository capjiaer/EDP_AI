# 三个独立命令设计方案

## 设计理念

将 EDP 命令拆分成三个独立的命令，每个命令职责清晰：

1. **`edp`** - 运行相关（执行流程、创建分支等）
2. **`edp_init`** - 初始化相关（设置项目、创建项目等）
3. **`edp_info`** - 信息查询相关（查看信息、历史、统计等）

## 命令分配

### 1. `edp` - 运行相关

**职责**：执行流程、创建分支、运行步骤

**命令**：
```bash
# 运行流程/步骤
edp -run <flow.step>          # 运行指定的流程/步骤
edp -run --dry-run            # 演示模式
edp -run --debug              # 调试模式

# 创建分支
edp -b <name>                 # 创建分支（快捷方式）
edp -branch <name>            # 创建分支（完整形式）
edp -b <name> --from-branch-step "branch1:step"  # 从指定步骤创建分支
edp -b <name> --to <step>     # 创建分支并执行到指定步骤（如果支持）
```

**选项**：
- `-run, --run <flow.step>` - 运行单个流程/步骤
- `--from <flow.step>` - 从指定步骤开始执行（edp 级别，跨 step）
  - 例如：`edp -run --from pnr_innovus.place` 从 place 开始执行所有后续步骤
  - 例如：`edp -run --from pnr_innovus.place --to pv_calibre.drc` 从 place 执行到 drc
- `--to <flow.step>` - 执行到指定步骤（edp 级别，跨 step）
  - 例如：`edp -run --to pv_calibre.drc` 执行所有前置步骤直到 drc
  - 注意：`--from/--to` 使用依赖图自动找到需要执行的步骤路径
- `-b, -branch, --branch <name>` - 创建分支
- `--from-branch-step <step>` - 从指定步骤创建分支（从源分支复制数据）
  - 例如：`edp -b branch2 --from-branch-step "branch1:pnr_innovus.init"`
  - 这会从 branch1 的 pnr_innovus.init 步骤复制数据到新分支

**注意**：
- `edp -run --from/--to` 是 edp 级别的功能，用于跨 step 执行（如从 `pnr_innovus.place` 到 `pv_calibre.drc`）
- `edp_run -from/-to` 是在 Tcl 脚本内部使用的，用于执行单个 step 内部的 sub_steps 范围
- `--dry-run` - 演示模式
- `--debug <level>` - 调试模式
- `--work-path` - 工作路径
- `--config` - 配置文件
- `-prj, --project` - 项目名称
- `-v, --version` - 版本
- `--block` - 块名称
- `-u, --user` - 用户名
- `--foundry` - 代工厂
- `--node` - 工艺节点

### 2. `edp_init` - 初始化相关

**职责**：初始化工作空间、创建项目结构

**命令**：
```bash
# 初始化工作空间
edp_init -init                # 初始化项目环境到 user 级别
edp_init -init --gui          # 使用图形界面初始化

# 创建项目
edp_init -create-project <project> <foundry> <node>  # 创建新项目
```

**选项**：
- `-init` - 初始化工作空间
- `--gui` - 使用图形界面（仅用于 -init）
- `-create-project, --create-project <project> <foundry> <node>` - 创建项目
- `--work-path` - 工作路径
- `--config` - 配置文件
- `-prj, --project` - 项目名称
- `-v, --version` - 版本
- `--block` - 块名称
- `-u, --user` - 用户名
- `--foundry` - 代工厂
- `--node` - 工艺节点

**注意**：`--from-branch-step` 不在 `edp_init` 中，因为创建分支是运行相关的操作（准备运行环境），所以放在 `edp` 中。

### 3. `edp_info` - 信息查询相关

**职责**：查看信息、历史查询、性能分析、结果验证等

**命令**：
```bash
# 查看 flow 信息
edp_info                      # 查看所有 flow
edp_info <flow>               # 查看指定 flow 的步骤状态

# 历史查询
edp_info -history             # 查看运行历史
edp_info -history <flow.step> # 查看指定步骤的历史
edp_info -history --limit 10  # 查看最近 N 条记录
edp_info -history --status failed  # 查看失败的历史

# 性能分析
edp_info -stats               # 性能统计
edp_info -stats <flow.step>   # 指定步骤的性能统计
edp_info -stats --trend       # 性能趋势

# 回滚
edp_info -rollback            # 回滚到上一次成功
edp_info -rollback --index 5  # 回滚到指定历史记录
edp_info -rollback <flow.step> # 回滚到指定步骤

# 结果验证
edp_info -validate            # 验证最后一次执行
edp_info -validate <flow.step> # 验证指定步骤
edp_info -validate --timing-compare branch1 branch2  # Timing compare

# 教程
edp_info -tutorial            # 查看教程
edp_info -tutorial --force   # 强制重新生成教程
```

**选项**：
- `-i, -info, --info [flow]` - 查看 flow 信息
- `-history, --history [flow.step]` - 历史查询
- `-stats, --stats [flow.step]` - 性能分析
- `-rollback, --rollback` - 回滚
- `-validate, --validate [flow.step]` - 结果验证
- `-tutorial, --tutorial` - 教程
- `--work-path` - 工作路径
- `--config` - 配置文件
- `-prj, --project` - 项目名称
- `-v, --version` - 版本
- `--block` - 块名称
- `-u, --user` - 用户名
- `--foundry` - 代工厂
- `--node` - 工艺节点

## 文件结构

```
edp_center/bin/
├── edp              # 运行相关命令的入口脚本
├── edp_init         # 初始化相关命令的入口脚本
├── edp_info         # 信息查询相关命令的入口脚本
├── edp.py           # edp 的 Python 入口
├── edp_init.py      # edp_init 的 Python 入口
└── edp_info.py      # edp_info 的 Python 入口

edp_center/main/cli/
├── cli.py           # edp 的主 CLI（运行相关）
├── cli_init.py      # edp_init 的主 CLI（初始化相关）
├── cli_info.py     # edp_info 的主 CLI（信息查询相关）
├── arg_parser.py    # edp 的参数解析器
├── arg_parser_init.py  # edp_init 的参数解析器
├── arg_parser_info.py  # edp_info 的参数解析器
└── ...
```

## Tab 补全效果

用户输入 `edp` 然后按 Tab，会看到：

```bash
$ edp<TAB>
edp       edp_init  edp_info
```

然后可以继续：
```bash
$ edp <TAB>
-run  -b  -branch  --help
```

```bash
$ edp_init <TAB>
-init  -create-project  --help
```

```bash
$ edp_info <TAB>
-info  -history  -stats  -rollback  -validate  -tutorial  --help
```

## 帮助信息示例

### `edp --help`
```
EDP - 运行相关命令

用于执行流程、创建分支等操作。

主要命令：
  -run, --run <flow.step>    运行指定的流程/步骤
  -b, -branch, --branch      创建分支
  --dry-run                  演示模式：只显示命令，不实际执行
  --debug <level>            调试模式：0=正常，1=交互式调试

示例：
  edp -run pv_calibre.ipmerge
  edp -b branch1
  edp -run pv_calibre.ipmerge --dry-run

使用 'edp <command> --help' 查看详细帮助。
```

### `edp_init --help`
```
EDP Init - 初始化相关命令

用于初始化工作空间、创建项目结构等操作。

主要命令：
  -init                      初始化项目环境到 user 级别
  --gui                      使用图形界面进行初始化（仅用于 -init）
  -create-project            创建新项目的文件夹结构

示例：
  edp_init -init -prj dongting -v P85 --block block1 --user zhangsan
  edp_init -init --gui
  edp_init -create-project new_prj TSMC n8

使用 'edp_init <command> --help' 查看详细帮助。
```

### `edp_info --help`
```
EDP Info - 信息查询相关命令

用于查看信息、历史查询、性能分析、结果验证等操作。

主要命令：
  -info, -i [flow]           查看 flow 信息
  -history [flow.step]       查看运行历史
  -stats [flow.step]         性能分析
  -rollback                  回滚到历史状态
  -validate [flow.step]      结果验证
  -tutorial                  查看教程

示例：
  edp_info                    # 查看所有 flow
  edp_info pv_calibre         # 查看指定 flow 的步骤状态
  edp_info -history           # 查看运行历史
  edp_info -stats             # 性能统计
  edp_info -rollback          # 回滚到上一次成功
  edp_info -validate          # 验证最后一次执行

使用 'edp_info <command> --help' 查看详细帮助。
```

## 实现计划

### 阶段 1: 创建三个独立的入口点
1. 创建 `edp_center/bin/edp_init` 和 `edp_center/bin/edp_info` 脚本
2. 创建 `edp_center/bin/edp_init.py` 和 `edp_center/bin/edp_info.py`
3. 创建 `edp_center/main/cli/cli_init.py` 和 `edp_center/main/cli/cli_info.py`

### 阶段 2: 拆分参数解析器
1. 创建 `arg_parser_init.py` - 只包含初始化相关的参数
2. 创建 `arg_parser_info.py` - 只包含信息查询相关的参数
3. 修改 `arg_parser.py` - 只包含运行相关的参数

### 阶段 3: 拆分命令路由
1. 修改 `command_router.py`，将初始化相关的路由移到 `cli_init.py`
2. 将信息查询相关的路由移到 `cli_info.py`
3. 保持 `cli.py` 只处理运行相关的命令

### 阶段 4: 更新补全脚本
1. 更新 `edp_completion.bash` 和 `edp_completion.csh`
2. 添加 `edp_init` 和 `edp_info` 的补全支持

### 阶段 5: 更新安装脚本
1. 更新 `install.sh`，安装三个命令
2. 更新环境变量脚本，添加三个命令到 PATH

## 向后兼容性

- 现有的 `edp -init` 仍然可以通过 `edp_init -init` 使用
- 现有的 `edp -info` 仍然可以通过 `edp_info -info` 使用
- 可以保留 `edp -init` 和 `edp -info` 作为快捷方式，但会提示用户使用新命令

## 优势

1. **职责清晰**：每个命令只负责一类功能
2. **Tab 补全自然**：用户输入 `edp` 会看到三个命令
3. **帮助信息聚焦**：每个命令的帮助信息更简洁
4. **易于扩展**：新功能可以明确归属到某个命令
5. **降低复杂度**：每个命令的选项更少，更容易理解

## 迁移建议

1. 保持 `edp -init` 和 `edp -info` 作为快捷方式，但显示警告提示使用新命令
2. 在帮助信息中提示用户使用新命令
3. 逐步迁移文档和示例

