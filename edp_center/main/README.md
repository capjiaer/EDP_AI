# EDP Main - 统一的工作流管理工具

EDP Main 整合了五个核心 KIT，提供统一的工作流管理接口。

## 📚 文档

- **[完整教程 (TUTORIAL.md)](../TUTORIAL.md)** - 从入门到精通的完整指南，包含快速开始、核心概念、基本操作、高级功能和最佳实践
- [快速开始 (QUICK_START.md)](../bin/QUICK_START.md) - 快速上手指南
- [安装指南 (INSTALL.md)](INSTALL.md) - 详细的安装和配置说明
- [使用示例 (usage_examples.md)](usage_examples.md) - Python API 使用示例

## 快速开始

### 最简单的使用方式

```bash
# 执行完整工作流（一步完成所有操作）
edp-main run \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1 \
  --flow pv_calibre
```

这会自动：
1. 初始化用户工作空间（如果不存在）
2. 加载所有 flow 的 dependency.yaml
3. 通过文件匹配自动建立跨 flow 依赖关系
4. 加载配置
5. 处理脚本（展开 #import 指令）
6. 执行工作流

### Python API 使用

```python
from edp_center.main import WorkflowManager

# 创建管理器
manager = WorkflowManager('edp_center')

# 执行完整工作流（推荐）
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

## 功能特性

- **环境初始化**：使用 `edp_dirkit` 初始化项目和工作空间
- **配置加载**：使用 `edp_configkit` 加载和合并配置
- **脚本处理**：使用 `edp_cmdkit` 处理 Tcl 脚本（展开 #import 指令）
- **工作流执行**：使用 `edp_flowkit` 执行工作流
- **库配置生成**：使用 `edp_libkit` 生成库配置文件（lib_config.tcl）
- **跨 flow 依赖自动发现**：通过文件匹配自动建立依赖关系

## 跨 flow 依赖自动发现

系统会自动：
- 加载所有 flow 的 `dependency.yaml` 文件
- 通过文件匹配自动建立依赖关系（包括跨 flow 依赖）
- 例如：
  - `pnr_innovus.postroute` 输出 `postroute.pass`
  - `pv_calibre.ipmerge` 需要 `postroute.pass`
  - 系统自动建立依赖：`postroute -> ipmerge`

**无需手动声明 flow 之间的依赖关系！**

## 命令行接口

### 初始化用户工作空间

```bash
edp-main init-workspace \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1
```

### 从已有分支创建新分支

```bash
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
edp-main load-config \
  --project dongting \
  --project-node P85 \
  --flow pv_calibre
```

### 处理脚本

```bash
edp-main process-script \
  --input script.tcl \
  --output output.tcl
```

### 加载工作流

```bash
edp-main load-workflow \
  --project dongting \
  --project-node P85 \
  --flow pv_calibre
```

### 执行完整工作流

```bash
edp-main run \
  --work-path WORK_PATH \
  --project dongting \
  --project-node P85 \
  --block block1 \
  --user zhangsan \
  --branch branch1 \
  --flow pv_calibre
```

## 更多示例

详细使用示例请查看：
- `SIMPLE_EXAMPLE.md` - 简单使用示例
- `usage_examples.md` - 详细使用示例
