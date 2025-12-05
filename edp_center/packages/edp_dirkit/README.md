# DirKit

DirKit 是一个用于文件和目录操作的工具库，主要用于从 `edp_center` 资源库初始化项目环境。

## 特性

- **目录操作**：创建、复制、链接目录
- **文件操作**：复制、链接文件
- **项目初始化**：从 edp_center 资源库初始化项目环境
- **配置和流程提取**：自动提取和合并配置文件和流程定义

## 安装

```bash
pip install -e .
```

## 使用示例

### 基本目录操作

```python
from dirkit import DirKit

# 创建 DirKit 实例
kit = DirKit()

# 确保目录存在
kit.ensure_dir("project/config")

# 复制文件
kit.copy_file("source/file.txt", "project/file.txt")

# 复制目录
kit.copy_dir("source/config", "project/config")

# 创建符号链接
kit.link_file("source/file.txt", "project/link.txt")
```

### 项目初始化

```python
from dirkit import ProjectInitializer

# 创建初始化器
initializer = ProjectInitializer("/path/to/edp_center")

# 初始化项目环境
initializer.init_project(
    project_dir="./my_project",
    foundry="SAMSUNG",
    node="S8",
    project="dongting",
    link_mode=False,  # 使用复制模式（True 表示使用符号链接）
    flows=["pv_calibre", "pnr_innovus"]  # 指定要初始化的流程
)

# 获取配置文件路径（按加载优先级排序）
config_files = initializer.get_config_files(
    foundry="SAMSUNG",
    node="S8",
    project="dongting",
    flow="pv_calibre"
)

print(config_files)
# 输出: [
#   Path(.../common/main/config.yaml),      # 1. common/main/*
#   Path(.../common/pv_calibre/config.yaml),# 2. common/{flow}/*
#   Path(.../common/pv_calibre/dependency.yaml),
#   Path(.../dongting/main/config.yaml),    # 3. {project}/main/*
#   Path(.../dongting/pv_calibre/config.yaml), # 4. {project}/{flow}/*
# ]

# 注意：配置文件按优先级从低到高排列，后面的配置会覆盖前面的
# 可以直接用 edp_configkit 的 files2dict 合并：
# from configkit import files2dict
# merged_config = files2dict(*config_files)
```

## API 参考

### DirKit

文件和目录操作工具类。

#### 方法

- `ensure_dir(path)` - 确保目录存在
- `copy_file(src, dst, overwrite=True)` - 复制文件
- `copy_dir(src, dst, overwrite=True, ignore=None)` - 复制目录
- `link_file(src, dst, overwrite=True)` - 创建文件符号链接
- `link_dir(src, dst, overwrite=True)` - 创建目录符号链接
- `remove(path, recursive=False)` - 删除文件或目录
- `find_files(pattern, root=None, recursive=True)` - 查找文件
- `find_dirs(pattern, root=None, recursive=True)` - 查找目录

### ProjectInitializer

项目环境初始化器。

#### 方法

- `init_project(project_dir, foundry, node, project, link_mode=False, flows=None)` - 初始化项目环境
- `get_config_files(foundry, node, project, flow=None)` - 获取配置文件路径列表（按优先级排序）

**配置加载优先级**（从低到高）：
1. `common/main/*` - 通用主配置
2. `common/{flow}/*` - 通用流程配置
3. `{project}/main/*` - 项目特定主配置
4. `{project}/{flow}/*` - 项目特定流程配置

## 工作原理

### 项目初始化流程

1. **创建基础目录结构**
   - `config/` - 项目配置目录
   - `flow/` - 项目流程目录
   - `flow/cmds/` - 流程命令脚本目录
   - `flow/packages/` - 流程包目录

2. **复制/链接项目配置**
   - 从 `edp_center/config/{foundry}/{node}/{project}/` 复制配置

3. **初始化流程**
   - 从 `edp_center/flow/initialize/{foundry}/{node}/common/cmds/` 复制基础流程
   - 从 `edp_center/flow/initialize/{foundry}/{node}/{project}/cmds/` 合并项目特定覆盖

4. **初始化 packages**
   - 按优先级顺序加载 packages：
     1. `flow/common/packages/tcl/default/`
     2. `flow/common/packages/tcl/{flow_name}/`
     3. `flow/initialize/{foundry}/{node}/common/packages/tcl/default/`
     4. `flow/initialize/{foundry}/{node}/common/packages/tcl/{flow_name}/`
     5. `flow/initialize/{foundry}/{node}/{project}/packages/tcl/default/`
     6. `flow/initialize/{foundry}/{node}/{project}/packages/tcl/{flow_name}/`

## 许可证

MIT

