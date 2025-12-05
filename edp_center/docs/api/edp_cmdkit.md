# edp_cmdkit API 文档

## 📋 概述

`edp_cmdkit` 提供 Tcl 脚本处理功能，包括 `#import` 指令展开、Hooks 处理、Sub_steps 处理等。

**位置**: `edp_center.packages.edp_cmdkit`

---

## 核心类

### CmdProcessor

Tcl 脚本处理器，主入口类。

**位置**: `edp_center.packages.edp_cmdkit.CmdProcessor`

#### `__init__(base_dir=None, default_search_paths=None, default_recursive=True)`

初始化 CmdProcessor。

**参数**:
- `base_dir` (Optional[Path]): 基础目录（可选）
- `default_search_paths` (Optional[List[Union[str, Path]]]): 默认搜索路径列表（可选）
- `default_recursive` (bool): 默认是否递归搜索（默认 True）

#### `process_file(input_file, output_file=None, search_paths=None, recursive=None, edp_center_path=None, foundry=None, node=None, project=None, flow_name=None, prepend_default_sources=False, full_tcl_path=None, hooks_dir=None, step_name=None, debug_mode=0, skip_sub_steps=None)`

处理 Tcl 文件。

**参数**:
- `input_file` (Union[str, Path]): 输入的 Tcl 文件路径
- `output_file` (Optional[Union[str, Path]]): 输出文件路径，如果为 None，返回处理后的内容字符串
- `search_paths` (Optional[List[Union[str, Path]]]): 搜索路径列表
- `recursive` (Optional[bool]): 是否递归查找子目录
- `edp_center_path` (Optional[Union[str, Path]]): edp_center 资源库的路径
- `foundry` (Optional[str]): 代工厂名称
- `node` (Optional[str]): 工艺节点
- `project` (Optional[str]): 项目名称
- `flow_name` (Optional[str]): 流程名称
- `prepend_default_sources` (bool): 是否在文件头部添加默认的 source 语句
- `full_tcl_path` (Optional[Union[str, Path]]): full.tcl 文件路径
- `hooks_dir` (Optional[Union[str, Path]]): hooks 目录路径
- `step_name` (Optional[str]): 步骤名称
- `debug_mode` (int): Debug 模式：0=正常执行，1=交互式调试
- `skip_sub_steps` (Optional[List[str]]): 要跳过的 sub_steps 列表

**返回**:
- `Optional[str]`: 如果 output_file 为 None，返回处理后的内容字符串；否则返回 None

**异常**:
- `EDPFileNotFoundError`: 如果输入文件不存在

---

## 辅助函数

### `find_file(import_file, current_file, search_paths, recursive=True)`

在搜索路径中查找文件（带缓存）。

**位置**: `edp_center.packages.edp_cmdkit.file_finder.find_file`

**参数**:
- `import_file` (str): 要查找的文件名或路径
- `current_file` (Path): 当前文件（用于解析相对路径）
- `search_paths` (List[Path]): 搜索路径列表
- `recursive` (bool): 是否递归查找子目录（默认 True）

**返回**:
- `Optional[Path]`: 找到的文件路径，如果未找到返回 None

**特性**:
- 支持文件搜索缓存
- 基于目录修改时间戳的缓存失效

### `clear_file_cache()`

清除文件搜索缓存。

**位置**: `edp_center.packages.edp_cmdkit.file_finder.clear_file_cache`

---

## Sub_steps 处理

### `generate_sub_steps_sources(edp_center_path, foundry, node, project, flow_name, step_name, current_file, search_paths, hooks_dir=None)`

生成 Sub_steps 的 source 语句和调用代码。

**位置**: `edp_center.packages.edp_cmdkit.sub_steps.generator.generate_sub_steps_sources`

**参数**:
- `edp_center_path` (Path): edp_center 资源库的路径
- `foundry` (str): 代工厂名称
- `node` (str): 工艺节点
- `project` (Optional[str]): 项目名称
- `flow_name` (str): 流程名称
- `step_name` (str): 步骤名称
- `current_file` (Path): 当前文件
- `search_paths` (List[Path]): 搜索路径列表
- `hooks_dir` (Optional[Path]): hooks 目录路径（可选）

**返回**:
- `str`: 生成的 source 语句和调用代码

---

## Hooks 处理

### `get_sub_step_pre(hooks_dir, file_name)`

获取 Sub_step 的 pre hook。

**位置**: `edp_center.packages.edp_cmdkit.sub_steps.hooks.get_sub_step_pre`

**参数**:
- `hooks_dir` (Path): hooks 目录路径
- `file_name` (str): 文件名（不含扩展名）

**返回**:
- `Optional[str]`: Hook 内容，如果不存在返回 None

### `get_sub_step_post(hooks_dir, file_name)`

获取 Sub_step 的 post hook。

**位置**: `edp_center.packages.edp_cmdkit.sub_steps.hooks.get_sub_step_post`

### `get_sub_step_replace(hooks_dir, file_name)`

获取 Sub_step 的 replace hook。

**位置**: `edp_center.packages.edp_cmdkit.sub_steps.hooks.get_sub_step_replace`

---

## 使用示例

```python
from edp_center.packages.edp_cmdkit import CmdProcessor

# 创建处理器
processor = CmdProcessor()

# 处理脚本
content = processor.process_file(
    input_file='place.tcl',
    output_file='place_processed.tcl',
    search_paths=['sub_steps', 'helpers'],
    edp_center_path='/path/to/edp_center',
    foundry='SAMSUNG',
    node='S8',
    project='dongting',
    flow_name='pnr_innovus',
    prepend_default_sources=True,
    full_tcl_path='runs/pnr_innovus.place/full.tcl',
    hooks_dir='hooks/pnr_innovus.place',
    step_name='place'
)
```

---

## 相关文档

- [架构设计文档](../architecture/architecture_overview.md)
- [WorkflowManager API](workflow_manager.md)
- [Hooks 机制文档](../../tutorial/04_hooks_and_imports.md)

