# edp_dirkit API 文档

## 📋 概述

`edp_dirkit` 提供目录管理和工作空间初始化功能。

**位置**: `edp_center.packages.edp_dirkit`

---

## 核心类

### ProjectInitializer

项目初始化器，用于创建项目目录结构。

**位置**: `edp_center.packages.edp_dirkit.ProjectInitializer`

#### `__init__(edp_center_path)`

初始化 ProjectInitializer。

**参数**:
- `edp_center_path` (Union[str, Path]): edp_center 资源库的路径

#### `init_project(project_dir, foundry, node, project, link_mode=False, flows=None)`

初始化项目环境。

**参数**:
- `project_dir` (Union[str, Path]): 项目目录路径
- `foundry` (str): 代工厂名称（如 `SAMSUNG`）
- `node` (str): 工艺节点（如 `S8`）
- `project` (str): 项目名称（如 `dongting`）
- `link_mode` (bool): 是否使用符号链接模式（默认 False，使用复制模式）
- `flows` (Optional[List[str]]): 要初始化的流程列表，如果为 None 则初始化所有流程

**返回**:
- `Dict[str, Path]`: 创建的目录路径字典

#### `get_config_files(foundry, node, project, flow)`

获取配置文件路径列表（按加载优先级排序）。

**参数**:
- `foundry` (str): 代工厂名称
- `node` (str): 工艺节点
- `project` (str): 项目名称
- `flow` (str): 流程名称

**返回**:
- `List[Path]`: 配置文件路径列表（按优先级从低到高）

---

### WorkPathInitializer

工作路径初始化器，用于初始化用户工作空间。

**位置**: `edp_center.packages.edp_dirkit.WorkPathInitializer`

#### `__init__(edp_center_path)`

初始化 WorkPathInitializer。

**参数**:
- `edp_center_path` (Union[str, Path]): edp_center 资源库的路径

#### `init_project(work_path, project_name, project_node, blocks=None, foundry=None, node=None)`

初始化项目环境。

**参数**:
- `work_path` (Union[str, Path]): WORK_PATH 根目录路径
- `project_name` (str): 项目名称
- `project_node` (str): 项目版本名称
- `blocks` (Optional[List[str]]): 块名称列表
- `foundry` (Optional[str]): 代工厂名称（可选）
- `node` (Optional[str]): 工艺节点（可选）

**返回**:
- `Dict[str, Path]`: 创建的目录路径字典

#### `init_user_workspace(work_path=None, project_name=None, project_node=None, block_name=None, user_name=None, branch_name=None, from_branch_step=None)`

初始化用户工作空间。

**参数**:
- `work_path` (Optional[Union[str, Path]]): WORK_PATH 根目录路径（可选，可从当前目录推断）
- `project_name` (Optional[str]): 项目名称（可选，可从路径推断）
- `project_node` (Optional[str]): 项目版本名称（可选，可从路径推断）
- `block_name` (Optional[str]): 块名称（可选，可从路径推断）
- `user_name` (Optional[str]): 用户名（可选，可从路径推断）
- `branch_name` (Optional[str]): 分支名称（可选，默认为 `main`）
- `from_branch_step` (Optional[str]): 从指定分支的步骤创建新分支（可选）

**返回**:
- `Dict[str, Path]`: 创建的目录路径字典

#### `get_project_info(project_name, foundry=None, node=None)`

获取项目信息。

**参数**:
- `project_name` (str): 项目名称
- `foundry` (Optional[str]): 代工厂名称（可选）
- `node` (Optional[str]): 工艺节点（可选）

**返回**:
- `Dict[str, str]`: 项目信息字典，包含 `foundry` 和 `node`

**异常**:
- `ProjectNotFoundError`: 如果项目未找到

---

### BranchManager

分支管理器，用于管理分支的创建和链接。

**位置**: `edp_center.packages.edp_dirkit.work_path.BranchManager`

#### `create_branch(branch_path, from_branch_step=None)`

创建新分支。

**参数**:
- `branch_path` (Union[str, Path]): 新分支路径
- `from_branch_step` (Optional[str]): 从指定分支的步骤创建（可选）

**返回**:
- `Dict[str, Path]`: 创建的目录路径字典

---

## 辅助函数

### `detect_project_path(path=None)`

检测项目路径信息。

**参数**:
- `path` (Optional[Union[str, Path]]): 路径（可选，默认为当前目录）

**返回**:
- `Optional[Dict[str, str]]`: 项目路径信息字典，包含 `project`, `version`, `block`, `user`, `branch`

---

## 使用示例

```python
from edp_center.packages.edp_dirkit import WorkPathInitializer

# 初始化
initializer = WorkPathInitializer('/path/to/edp_center')

# 初始化用户工作空间
paths = initializer.init_user_workspace(
    work_path='/work',
    project_name='dongting',
    project_node='P85',
    block_name='block1',
    user_name='user1',
    branch_name='main'
)

# 获取项目信息
project_info = initializer.get_project_info('dongting')
foundry = project_info['foundry']
node = project_info['node']
```

---

## 相关文档

- [架构设计文档](../architecture/architecture_overview.md)
- [WorkflowManager API](workflow_manager.md)

