# EDP 命令分类设计方案

## 当前命令结构

### 现有命令
- `-init` - 初始化项目环境
- `-branch` / `-b` - 创建分支
- `-create-project` - 创建项目
- `-run` - 运行流程/步骤
- `-info` / `-i` - 查看信息
- `-tutorial` - 教程
- `--dry-run` - 演示模式
- `--debug` - 调试模式

## 分类方案

### 方案 1: 使用子命令（推荐）

将命令组织成三个主要类别，使用子命令结构：

```bash
# Init 相关 - 设置项目
edp init <workspace>          # 初始化工作空间
edp init branch <name>        # 创建分支
edp init project <name>       # 创建项目

# Run 相关 - 执行流程
edp run <flow.step>           # 运行流程/步骤
edp run --dry-run             # 演示模式
edp run --debug               # 调试模式

# 辅助相关 - 查询和分析
edp info                      # 查看 flow 信息
edp history                   # 查看运行历史
edp stats                     # 性能分析
edp rollback                  # 回滚
edp validate                  # 结果验证
edp tutorial                  # 教程
```

### 方案 2: 保持快捷方式，添加分类帮助

保持现有的快捷方式，但添加分类帮助信息：

```bash
# 保持现有快捷方式
edp -init                     # 初始化
edp -b branch1               # 创建分支
edp -run flow.step           # 运行
edp -info                    # 查看信息

# 新增辅助命令
edp -history                 # 历史查询
edp -stats                   # 性能分析
edp -rollback                # 回滚
edp -validate                # 结果验证

# 分类帮助
edp --help-init              # 显示 init 相关命令
edp --help-run               # 显示 run 相关命令
edp --help-utils             # 显示辅助相关命令
```

### 方案 3: 混合方案（推荐用于过渡）

保持现有快捷方式，同时支持子命令：

```bash
# 快捷方式（向后兼容）
edp -init                    # 初始化
edp -b branch1              # 创建分支
edp -run flow.step          # 运行
edp -info                   # 查看信息

# 子命令（新方式，更清晰）
edp init workspace          # 等同于 edp -init
edp init branch branch1     # 等同于 edp -b branch1
edp run flow.step           # 等同于 edp -run flow.step
edp info                    # 等同于 edp -info

# 辅助命令（新功能）
edp history                 # 历史查询
edp stats                   # 性能分析
edp rollback                # 回滚
edp validate                # 结果验证
edp tutorial                # 教程
```

## 推荐方案：方案 3（混合方案）

### 优势
1. **向后兼容**：保持现有快捷方式，不影响现有脚本
2. **清晰分类**：新功能使用子命令，结构更清晰
3. **渐进迁移**：用户可以逐步从快捷方式迁移到子命令
4. **帮助系统**：可以按类别显示帮助信息

### 命令结构

```
edp
├── init                    # Init 相关
│   ├── workspace          # 初始化工作空间（等同于 -init）
│   ├── branch <name>      # 创建分支（等同于 -b/-branch）
│   └── project <name>     # 创建项目（等同于 -create-project）
│
├── run                     # Run 相关
│   ├── <flow.step>        # 运行流程/步骤（等同于 -run）
│   ├── --dry-run          # 演示模式
│   └── --debug            # 调试模式
│
└── [辅助命令]              # 辅助相关
    ├── info                # 查看信息（等同于 -info）
    ├── history             # 历史查询（新增）
    ├── stats               # 性能分析（新增）
    ├── rollback            # 回滚（新增）
    ├── validate            # 结果验证（新增）
    └── tutorial            # 教程（等同于 -tutorial）
```

### 帮助信息示例

```bash
$ edp --help

EDP Main - 统一的工作流管理工具

主要命令类别：
  init      - 初始化相关（设置项目、创建分支等）
  run       - 执行相关（运行流程、步骤等）
  info      - 查看 flow 信息
  history   - 查看运行历史
  stats     - 性能分析
  rollback  - 回滚到历史状态
  validate  - 结果验证
  tutorial  - 查看教程

快捷方式（向后兼容）：
  -init, -b, -run, -info 等仍然支持

使用 'edp <command> --help' 查看具体命令的帮助信息。

$ edp init --help

Init 相关命令 - 设置项目环境

命令：
  workspace             初始化工作空间（等同于 -init）
  branch <name>         创建分支（等同于 -b/-branch）
  project <name>        创建项目（等同于 -create-project）

示例：
  edp init workspace -prj dongting -v P85 --block block1 --user zhangsan
  edp init branch branch1
  edp init project new_prj TSMC n8

$ edp run --help

Run 相关命令 - 执行流程和步骤

用法：
  edp run <flow.step>   运行指定的流程/步骤（等同于 -run）

选项：
  --dry-run             演示模式：只显示构建的命令，不实际执行
  --debug <level>       调试模式：0=正常执行，1=交互式调试

示例：
  edp run pv_calibre.ipmerge
  edp run pv_calibre.ipmerge --dry-run
  edp run pv_calibre.ipmerge --debug 1
```

## 实现计划

### 阶段 1: 添加子命令支持（保持快捷方式）
1. 修改 `arg_parser.py`，添加子命令解析器
2. 修改 `command_router.py`，支持子命令路由
3. 保持现有快捷方式的处理逻辑

### 阶段 2: 实现新的辅助命令
1. 实现 `edp history` 命令
2. 实现 `edp stats` 命令
3. 实现 `edp rollback` 命令
4. 实现 `edp validate` 命令

### 阶段 3: 优化帮助系统
1. 添加分类帮助（`edp --help-init`, `edp --help-run`, `edp --help-utils`）
2. 优化帮助信息显示
3. 添加命令补全支持

## 命令映射表

| 快捷方式 | 子命令 | 说明 |
|---------|--------|------|
| `edp -init` | `edp init workspace` | 初始化工作空间 |
| `edp -b <name>` | `edp init branch <name>` | 创建分支 |
| `edp -create-project` | `edp init project <name>` | 创建项目 |
| `edp -run <flow.step>` | `edp run <flow.step>` | 运行流程/步骤 |
| `edp -info` | `edp info` | 查看信息 |
| `edp -tutorial` | `edp tutorial` | 查看教程 |
| - | `edp history` | 历史查询（新增） |
| - | `edp stats` | 性能分析（新增） |
| - | `edp rollback` | 回滚（新增） |
| - | `edp validate` | 结果验证（新增） |

## 向后兼容性

- 所有现有的快捷方式（`-init`, `-b`, `-run`, `-info` 等）继续支持
- 现有的脚本和文档不需要修改
- 新功能使用子命令，结构更清晰
- 用户可以逐步迁移到子命令方式

