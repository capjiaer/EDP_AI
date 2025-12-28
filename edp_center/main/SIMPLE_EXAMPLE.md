# EDP Main 简单使用示例

## 快速开始

### 方式 1: Python API（推荐）

```python
from edp_center.main import WorkflowManager

# 创建管理器
manager = WorkflowManager('edp_center')

# 1. 初始化用户工作空间
manager.init_user_workspace(
    work_path='WORK_PATH',
    project='dongting',
    project_node='P85',
    block='block1',
    user='zhangsan',
    branch='branch1'
)

# 2. 加载配置
config = manager.load_config(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow='pv_calibre'
)

# 3. 加载工作流（自动加载所有 flow，自动发现跨 flow 依赖）
graph = manager.load_workflow(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow=None  # None 表示加载所有 flow
)

# 4. 执行完整工作流（推荐，一步完成所有操作）
results = manager.run_full_workflow(
    work_path='WORK_PATH',
    project='dongting',
    project_node='P85',
    block='block1',
    user='zhangsan',
    branch='branch1',
    flow='pv_calibre'
)
```

### 方式 2: 命令行（CLI）

```bash
# 1. 创建分支
edp -b branch1 -prj dongting -v P85 --block block1 --user zhangsan

# 2. 执行流程/步骤（推荐）
edp -run pv_calibre.ipmerge
# 或执行多个步骤
edp -run -fr pnr_innovus.place -to pv_calibre.drc
```

## 完整工作流程

### 场景：运行 pv_calibre 流程

```bash
# 执行流程/步骤（自动推断项目信息）
edp -run pv_calibre.ipmerge
# 或执行多个步骤
edp -run -fr pnr_innovus.place -to pv_calibre.drc
```

这会自动：
1. 初始化用户工作空间（如果不存在）
2. 加载所有 flow 的 dependency.yaml
3. 通过文件匹配自动建立跨 flow 依赖关系
4. 加载配置
5. 处理脚本（展开 #import 指令）
6. 执行工作流

## 从已有分支创建新分支

```bash
# 从 branch1 的 pnr_innovus.init 步骤创建 branch2
edp -b branch2 --from-branch-step "branch1:pnr_innovus.init"

# 然后在 branch2 上运行流程
edp -run pv_calibre.ipmerge
# 或执行多个步骤
edp -run -fr pnr_innovus.place -to pv_calibre.drc
```

## 跨 flow 依赖自动发现

系统会自动：
- 加载所有 flow 的 `dependency.yaml` 文件
- 通过文件匹配自动建立依赖关系
- 例如：
  - `pnr_innovus.postroute` 输出 `postroute.pass`
  - `pv_calibre.ipmerge` 需要 `postroute.pass`
  - 系统自动建立依赖：`postroute -> ipmerge`

无需手动声明 flow 之间的依赖关系！

