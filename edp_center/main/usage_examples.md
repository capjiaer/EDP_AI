# EDP Main 使用示例

## 1. Python API 使用方式

### 基本使用流程

```python
from edp_center.main import WorkflowManager

# 创建 WorkflowManager
manager = WorkflowManager('edp_center')

# 方式 1: 初始化用户工作空间
manager.init_user_workspace(
    work_path='WORK_PATH',
    project='dongting',
    project_node='P85',
    block='block1',
    user='zhangsan',
    branch='branch1'
)

# 方式 2: 加载配置
config = manager.load_config(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow='pv_calibre'
)

# 方式 3: 处理脚本（展开 #import 指令）
manager.process_script(
    input_file='edp_center/flow/initialize/SAMSUNG/S8/dongting/cmds/pv_calibre/steps/ipmerge.tcl',
    output_file='WORK_PATH/dongting/P85/block1/zhangsan/branch1/cmds/pv_calibre/steps/ipmerge.tcl',
    prepend_default_sources=True
)

# 方式 4: 加载工作流（自动加载所有 flow 的 dependency.yaml）
graph = manager.load_workflow(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow=None  # None 表示加载所有 flow
)

# 方式 5: 执行完整工作流（推荐）
results = manager.run_full_workflow(
    work_path='WORK_PATH',
    project='dongting',
    project_node='P85',
    block='block1',
    user='zhangsan',
    branch='branch1',
    flow='pv_calibre'  # 主要执行的 flow
)
```

### 从已有分支创建新分支

```python
# 从 branch1 的 pnr_innovus.init 步骤创建 branch2
manager.init_user_workspace(
    work_path='WORK_PATH',
    project='dongting',
    project_node='P85',
    block='block1',
    user='zhangsan',
    branch='branch2',
    from_branch_step='branch1:pnr_innovus.init'  # 从指定分支的步骤创建
)
```

## 2. 命令行使用方式

### 初始化用户工作空间

```bash
# 基本初始化
edp-main init-workspace \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1

# 从已有分支创建新分支
edp-main init-workspace \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch2 \
  --from-branch-step "branch1:pnr_innovus.init"
```

### 加载配置

```bash
# 加载配置并输出到控制台
edp-main load-config \
  --project dongting \
  --project-node P85 \
  --flow pv_calibre

# 加载配置并保存到文件
edp-main load-config \
  --project dongting \
  --project-node P85 \
  --flow pv_calibre \
  --output config.yaml
```

### 处理脚本

```bash
# 处理脚本并输出到控制台
edp-main process-script \
  --input edp_center/flow/initialize/SAMSUNG/S8/dongting/cmds/pv_calibre/steps/ipmerge.tcl

# 处理脚本并保存到文件
edp-main process-script \
  --input edp_center/flow/initialize/SAMSUNG/S8/dongting/cmds/pv_calibre/steps/ipmerge.tcl \
  --output output/ipmerge_expanded.tcl
```

### 加载工作流

```bash
# 加载工作流定义（自动加载所有 flow）
edp-main load-workflow \
  --project dongting \
  --project-node P85 \
  --flow pv_calibre
```

### 执行完整工作流（推荐）

```bash
# 执行完整工作流
edp-main run \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1 \
  --flow pv_calibre
```

## 3. 完整工作流程示例

### 场景：运行 pv_calibre 流程

```bash
# 步骤 1: 初始化用户工作空间
edp-main init-workspace \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1

# 步骤 2: 执行完整工作流
# 这会自动：
# - 加载所有 flow 的 dependency.yaml
# - 通过文件匹配自动建立跨 flow 依赖
# - 处理脚本（展开 #import 指令）
# - 执行工作流
edp-main run \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1 \
  --flow pv_calibre
```

### 场景：从已有分支创建新分支并运行

```bash
# 步骤 1: 从 branch1 的 pnr_innovus.init 创建 branch2
edp-main init-workspace \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch2 \
  --from-branch-step "branch1:pnr_innovus.init"

# 步骤 2: 在 branch2 上运行 pv_calibre
edp-main run \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch2 \
  --flow pv_calibre
```

## 4. 自动检测 edp_center 路径

如果不指定 `--edp-center`，系统会自动从当前目录向上查找 `edp_center` 目录：

```bash
# 在项目根目录下运行，会自动检测 edp_center
cd /path/to/EDP_AI
edp-main run --work-path WORK_PATH --project dongting ...
```

## 5. 依赖关系说明

系统会自动：
1. 加载所有 flow 的 `dependency.yaml` 文件
2. 通过文件匹配自动建立依赖关系（包括跨 flow 依赖）
3. 例如：
   - `pnr_innovus.postroute` 输出 `postroute.pass`
   - `pv_calibre.ipmerge` 需要 `postroute.pass`
   - 系统自动建立依赖：`postroute -> ipmerge`

