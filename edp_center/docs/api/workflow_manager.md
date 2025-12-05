# WorkflowManager API 文档

## 📋 概述

`WorkflowManager` 是 EDP_AI 框架的统一工作流管理接口，整合四个 KIT，提供简洁易用的 API。

**位置**: `edp_center.main.workflow_manager.WorkflowManager`

---

## 类定义

```python
from edp_center.main import WorkflowManager

manager = WorkflowManager(edp_center_path)
```

---

## 初始化

### `__init__(edp_center_path)`

初始化 WorkflowManager。

**参数**:
- `edp_center_path` (Union[str, Path]): edp_center 资源库的路径

**异常**:
- `FileNotFoundError`: 如果 edp_center_path 不存在

**示例**:
```python
from edp_center.main import WorkflowManager

manager = WorkflowManager('/path/to/edp_center')
```

---

## 环境初始化方法

### `init_project(work_path, project_name, version, blocks=None, foundry=None, node=None)`

初始化项目环境。

**参数**:
- `work_path` (Union[str, Path]): WORK_PATH 根目录路径
- `project_name` (str): 项目名称（如 `dongting`）
- `version` (str): 项目版本名称（如 `P85`）
- `blocks` (Optional[List[str]]): 块名称列表，如果为 None 则从配置文件读取
- `foundry` (Optional[str]): 可选，如果项目在多个 foundry 下存在，需要指定
- `node` (Optional[str]): 可选，如果项目在多个 node 下存在，需要指定

**返回**:
- `Dict[str, Path]`: 包含创建的目录路径的字典

**示例**:
```python
paths = manager.init_project(
    work_path='/work',
    project_name='dongting',
    version='P85',
    blocks=['block1', 'block2']
)
```

---

### `init_user_workspace(work_path, project, version, block, user, branch, foundry=None, node=None, from_branch_step=None)`

初始化用户工作空间。

**参数**:
- `work_path` (Union[str, Path]): WORK_PATH 根目录路径
- `project` (str): 项目名称（如 `dongting`）
- `version` (str): 项目版本名称（如 `P85`）
- `block` (str): 块名称（如 `block1`）
- `user` (str): 用户名（如 `user1`）
- `branch` (str): 分支名称（如 `main`）
- `foundry` (Optional[str]): 可选，如果项目在多个 foundry 下存在，需要指定
- `node` (Optional[str]): 可选，如果项目在多个 node 下存在，需要指定
- `from_branch_step` (Optional[str]): 可选，从指定分支的步骤创建新分支（如 `"branch1:pnr_innovus.init"`）

**返回**:
- `Dict[str, Path]`: 包含创建的目录路径的字典

**示例**:
```python
paths = manager.init_user_workspace(
    work_path='/work',
    project='dongting',
    version='P85',
    block='block1',
    user='user1',
    branch='main'
)
```

---

## 配置管理方法

### `load_config(foundry, node, project, flow, config_files=None)`

加载配置文件。

**参数**:
- `foundry` (str): 代工厂名称（如 `SAMSUNG`）
- `node` (str): 工艺节点（如 `S8`）
- `project` (str): 项目名称（如 `dongting`）
- `flow` (str): 流程名称（如 `pv_calibre`）
- `config_files` (Optional[List[Union[str, Path]]]): 可选的配置文件列表，如果为 None，则自动从 edp_center 获取

**返回**:
- `Dict[str, Any]`: 合并后的配置字典

**示例**:
```python
config = manager.load_config(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow='pv_calibre'
)
```

---

## 脚本处理方法

### `process_script(input_file, output_file=None, search_paths=None, prepend_default_sources=True, full_tcl_path=None, hooks_dir=None, step_name=None, debug_mode=0, skip_sub_steps=None)`

处理 Tcl 脚本。

**参数**:
- `input_file` (Union[str, Path]): 输入的 Tcl 文件路径
- `output_file` (Optional[Union[str, Path]]): 输出文件路径，如果为 None，返回处理后的内容字符串
- `search_paths` (Optional[List[Union[str, Path]]]): 搜索路径列表，用于查找被导入的文件
- `prepend_default_sources` (bool): 是否在文件头部添加默认的 source 语句（默认 True）
- `full_tcl_path` (Optional[Union[str, Path]]): full.tcl 文件路径，如果提供，会在文件头添加 source full.tcl
- `hooks_dir` (Optional[Union[str, Path]]): hooks 目录路径（如 `hooks/pv_calibre/ipmerge`），用于插入 hooks 文件
- `step_name` (Optional[str]): 步骤名称（如 `ipmerge`），用于查找 step.pre 和 step.post
- `debug_mode` (int): Debug 模式：0=正常执行，1=交互式调试（默认 0）
- `skip_sub_steps` (Optional[List[str]]): 要跳过的 sub_steps 列表（从 user_config.yaml 读取）

**返回**:
- `Optional[str]`: 如果 output_file 为 None，返回处理后的内容字符串；否则返回 None（内容已写入文件）

**示例**:
```python
# 处理脚本并保存到文件
manager.process_script(
    input_file='place.tcl',
    output_file='place_processed.tcl',
    hooks_dir='hooks/pnr_innovus.place',
    step_name='place'
)

# 处理脚本并返回内容
content = manager.process_script(
    input_file='place.tcl',
    hooks_dir='hooks/pnr_innovus.place',
    step_name='place'
)
```

---

## 工作流执行方法

### `load_workflow(foundry, node, project, flow=None, dependency_files=None)`

加载工作流定义。

**参数**:
- `foundry` (str): 代工厂名称（如 `SAMSUNG`）
- `node` (str): 工艺节点（如 `S8`）
- `project` (str): 项目名称（如 `dongting`）
- `flow` (Optional[str]): 流程名称（可选，如果为 None，则加载所有 flow）
- `dependency_files` (Optional[List[Union[str, Path]]]): 可选的 dependency.yaml 文件列表，如果为 None，则自动从 edp_center 获取

**返回**:
- `Graph`: Graph 对象（包含所有 flow 的步骤，依赖关系通过文件匹配自动建立）

**示例**:
```python
graph = manager.load_workflow(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow='pv_calibre'
)
```

---

### `execute_workflow(graph, work_path, project, version, block, user, branch, config=None)`

执行工作流。

**参数**:
- `graph` (Graph): 工作流图对象
- `work_path` (Union[str, Path]): WORK_PATH 根目录路径
- `project` (str): 项目名称（如 `dongting`）
- `version` (str): 项目版本名称（如 `P85`）
- `block` (str): 块名称（如 `block1`）
- `user` (str): 用户名（如 `user1`）
- `branch` (str): 分支名称（如 `main`）
- `config` (Optional[Dict[str, Any]]): 可选的配置字典，用于执行器

**返回**:
- `Dict[str, Any]`: 执行结果字典

**示例**:
```python
results = manager.execute_workflow(
    graph=graph,
    work_path='/work',
    project='dongting',
    version='P85',
    block='block1',
    user='user1',
    branch='main',
    config=config
)
```

---

### `run_full_workflow(work_path, project, version, block, user, branch, flow, foundry=None, node=None, from_branch_step=None, prepend_default_sources=True)`

运行完整工作流（整合四个 KIT）。

**流程**:
1. 初始化用户工作空间（edp_dirkit）
2. 加载配置（edp_configkit）
3. 加载工作流定义（edp_flowkit）
4. 处理脚本（edp_cmdkit）- 在工作流执行时自动调用
5. 执行工作流（edp_flowkit）

**参数**:
- `work_path` (Union[str, Path]): WORK_PATH 根目录路径
- `project` (str): 项目名称（如 `dongting`）
- `version` (str): 项目版本名称（如 `P85`）
- `block` (str): 块名称（如 `block1`）
- `user` (str): 用户名（如 `user1`）
- `branch` (str): 分支名称（如 `main`）
- `flow` (str): 流程名称（如 `pv_calibre`）
- `foundry` (Optional[str]): 可选，如果项目在多个 foundry 下存在，需要指定
- `node` (Optional[str]): 可选，如果项目在多个 node 下存在，需要指定
- `from_branch_step` (Optional[str]): 可选，从指定分支的步骤创建新分支
- `prepend_default_sources` (bool): 是否在脚本处理时添加默认 source 语句（默认 True）

**返回**:
- `Dict[str, Any]`: 执行结果字典

**示例**:
```python
results = manager.run_full_workflow(
    work_path='/work',
    project='dongting',
    version='P85',
    block='block1',
    user='user1',
    branch='main',
    flow='pv_calibre'
)
```

---

## 属性

### `edp_center`

edp_center 资源库的路径（Path 对象）。

### `project_initializer`

`ProjectInitializer` 实例（edp_dirkit）。

### `work_path_initializer`

`WorkPathInitializer` 实例（edp_dirkit）。

### `cmd_processor`

`CmdProcessor` 实例（edp_cmdkit）。

---

## 完整示例

```python
from edp_center.main import WorkflowManager

# 初始化
manager = WorkflowManager('/path/to/edp_center')

# 运行完整工作流
results = manager.run_full_workflow(
    work_path='/work',
    project='dongting',
    version='P85',
    block='block1',
    user='user1',
    branch='main',
    flow='pv_calibre'
)

# 或者分步执行
# 1. 初始化工作空间
paths = manager.init_user_workspace(
    work_path='/work',
    project='dongting',
    version='P85',
    block='block1',
    user='user1',
    branch='main'
)

# 2. 加载配置
config = manager.load_config(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow='pv_calibre'
)

# 3. 加载工作流
graph = manager.load_workflow(
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow='pv_calibre'
)

# 4. 执行工作流
results = manager.execute_workflow(
    graph=graph,
    work_path='/work',
    project='dongting',
    version='P85',
    block='block1',
    user='user1',
    branch='main',
    config=config
)
```

---

## 相关文档

- [架构设计文档](../architecture/architecture_overview.md)
- [edp_dirkit API](edp_dirkit.md)
- [edp_configkit API](edp_configkit.md)
- [edp_cmdkit API](edp_cmdkit.md)
- [edp_flowkit API](edp_flowkit.md)

