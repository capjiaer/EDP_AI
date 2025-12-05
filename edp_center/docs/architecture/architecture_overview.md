# EDP_AI 框架架构设计文档

## 📋 文档信息

- **版本**: 1.0
- **最后更新**: 2025-01-XX
- **维护者**: EDP 框架团队

---

## 1. 架构概览

### 1.1 整体架构

EDP_AI 框架采用**四 KIT 架构**，通过 `WorkflowManager` 统一管理：

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI / GUI / API                          │
│              (edp, edp_init, edp_info, Web GUI)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │      WorkflowManager                   │
        │   (统一工作流管理接口)                  │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ edp_dirkit  │ │edp_configkit│ │ edp_cmdkit  │ │ edp_flowkit │
├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤
│ 目录管理     │ │ 配置加载     │ │ 脚本处理     │ │ 工作流执行   │
│ 工作空间初始化│ │ 配置合并     │ │ #import展开  │ │ 依赖管理     │
│ 分支管理     │ │ YAML↔Tcl    │ │ Hooks处理    │ │ 步骤执行     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 1.2 核心设计原则

1. **模块化**: 四个 KIT 职责清晰，相对独立
2. **统一接口**: `WorkflowManager` 提供统一的工作流管理接口
3. **可扩展性**: 通过 hooks 机制支持用户自定义扩展
4. **配置驱动**: 通过 YAML/Tcl 配置文件驱动工作流
5. **依赖管理**: 自动管理步骤之间的依赖关系

---

## 2. 四 KIT 架构详解

### 2.1 edp_dirkit - 目录管理工具

**职责**: 目录结构管理和工作空间初始化

**核心功能**:
- 项目目录结构创建
- 用户工作空间初始化
- 分支管理（创建、链接）
- 工作路径检测和验证

**主要类**:
- `ProjectInitializer`: 项目初始化
- `WorkPathInitializer`: 工作路径初始化
- `BranchManager`: 分支管理

**目录结构**:
```
WORK_PATH/
└── {project}/
    └── {version}/
        └── {block}/
            └── {user}/
                ├── main/          # 主分支
                │   ├── cmds/      # 命令脚本目录
                │   ├── hooks/     # Hooks 目录
                │   ├── runs/      # 运行目录
                │   └── user_config.yaml
                └── {branch}/      # 其他分支
```

**依赖关系**:
- 无其他 KIT 依赖
- 被 `WorkflowManager` 使用

---

### 2.2 edp_configkit - 配置管理工具

**职责**: 配置文件的加载、合并和转换

**核心功能**:
- YAML 配置文件加载
- Tcl 配置文件加载
- 多层级配置合并（common → project → user）
- YAML ↔ Tcl 双向转换
- 配置验证和约束检查

**配置加载顺序**（优先级从低到高）:
1. `common/main/init_project.yaml`
2. `common/main/config.yaml`
3. `common/{flow_name}/config.yaml`
4. `{project}/main/init_project.yaml`
5. `{project}/main/config.yaml`
6. `{project}/{flow_name}/config.yaml`
7. `user_config.yaml` 或 `user_config.tcl`（最高优先级）

**主要类**:
- `ConfigLoader`: 配置加载器
- `ConfigMerger`: 配置合并器
- `TclInterpreter`: Tcl 解释器（用于 Tcl 配置）

**输出**:
- `full.tcl`: 合并后的完整配置（Tcl 格式）
- 包含所有配置变量和自动生成的变量

**依赖关系**:
- 无其他 KIT 依赖
- 被 `WorkflowManager` 和 `edp_cmdkit` 使用

---

### 2.3 edp_cmdkit - 脚本处理工具

**职责**: Tcl 脚本处理和 `#import` 指令展开

**核心功能**:
- `#import source` 指令处理
- Hooks 机制（step.pre/post, sub_step.pre/post/replace）
- Sub_steps 处理
- Debug 模式脚本生成
- 文件搜索和缓存

**处理流程**:
```
输入脚本
    ↓
1. 整合 Hooks（step.pre + 主脚本 + step.post）
    ↓
2. 处理 #import source 指令（递归展开）
    ↓
3. 处理 Sub_steps（生成 proc 定义和调用）
    ↓
4. 添加默认 source 语句（packages, full.tcl）
    ↓
5. Debug 模式处理（可选）
    ↓
输出脚本
```

**主要类**:
- `CmdProcessor`: 脚本处理器（主入口）
- `ImportProcessor`: `#import` 指令处理器
- `HooksHandler`: Hooks 处理器
- `SubStepsGenerator`: Sub_steps 生成器
- `DebugModeHandler`: Debug 模式处理器

**Hooks 机制**:
- **Step Hooks**: `step.pre`, `step.post`
- **Sub_step Hooks**: `{file_name}.pre`, `{file_name}.post`, `{file_name}.replace`

**依赖关系**:
- 依赖 `edp_configkit`（用于加载配置）
- 被 `WorkflowManager` 使用

---

### 2.4 edp_flowkit - 工作流执行工具

**职责**: 工作流执行和依赖管理

**核心功能**:
- 依赖图构建（从 `dependency.yaml`）
- 步骤状态管理
- 步骤执行（本地/LSF）
- 并发执行支持
- 执行计划管理

**依赖图结构**:
```
Step A
  ├── Step B (依赖 A)
  ├── Step C (依赖 A)
  └── Step D (依赖 B, C)
```

**主要类**:
- `Graph`: 依赖图
- `Step`: 步骤节点
- `ICCommandExecutor`: 命令执行器
- `LSFExecutor`: LSF 作业执行器

**执行模式**:
- **顺序执行**: 按依赖顺序执行
- **并发执行**: 无依赖的步骤并发执行
- **失败策略**: stop（遇到失败停止）或 continue（继续执行）

**依赖关系**:
- 依赖 `edp_cmdkit`（用于处理脚本）
- 被 `WorkflowManager` 使用

---

## 3. WorkflowManager - 统一接口

### 3.1 设计目的

`WorkflowManager` 整合四个 KIT，提供统一的工作流管理接口，简化用户使用。

### 3.2 核心方法

#### 环境初始化
- `init_project()`: 初始化项目环境
- `init_user_workspace()`: 初始化用户工作空间

#### 配置管理
- `load_config()`: 加载配置
- `generate_full_tcl()`: 生成 full.tcl

#### 脚本处理
- `process_script()`: 处理脚本（展开 #import）

#### 工作流执行
- `load_workflow()`: 加载工作流（构建依赖图）
- `run_full_workflow()`: 执行完整工作流
- `run_single_step()`: 执行单个步骤

### 3.3 工作流执行流程

```
1. 初始化工作空间（edp_dirkit）
   ↓
2. 加载配置（edp_configkit）
   ↓
3. 构建依赖图（edp_flowkit）
   ↓
4. 处理脚本（edp_cmdkit）
   ↓
5. 执行步骤（edp_flowkit）
   ↓
6. 完成
```

---

## 4. 数据流

### 4.1 配置数据流

```
配置文件（YAML/Tcl）
    ↓
edp_configkit 加载和合并
    ↓
full.tcl（合并后的配置）
    ↓
edp_cmdkit 处理脚本时 source
    ↓
最终执行的 Tcl 脚本
```

### 4.2 脚本数据流

```
主脚本 + Hooks
    ↓
edp_cmdkit 处理
    ├── 展开 #import source
    ├── 处理 Sub_steps
    └── 添加默认 source
    ↓
最终脚本
    ↓
edp_flowkit 执行
```

### 4.3 依赖关系数据流

```
dependency.yaml（每个 flow）
    ↓
edp_flowkit 解析
    ↓
依赖图（Graph）
    ↓
执行计划
    ↓
步骤执行
```

---

## 5. 模块依赖关系

### 5.1 依赖图

```
WorkflowManager
    ├── edp_dirkit (无依赖)
    ├── edp_configkit (无依赖)
    ├── edp_cmdkit
    │   └── edp_configkit
    └── edp_flowkit
        └── edp_cmdkit
            └── edp_configkit
```

### 5.2 依赖说明

- **edp_dirkit**: 独立模块，无依赖
- **edp_configkit**: 独立模块，无依赖
- **edp_cmdkit**: 依赖 `edp_configkit`（用于加载配置）
- **edp_flowkit**: 依赖 `edp_cmdkit`（用于处理脚本）

---

## 6. 扩展机制

### 6.1 Hooks 机制

允许用户在特定位置插入自定义代码：

- **Step Hooks**: 在步骤执行前后插入代码
- **Sub_step Hooks**: 在子步骤执行前后插入代码，或替换子步骤

### 6.2 配置文件扩展

通过多层级配置，支持：
- 通用配置（common）
- 项目特定配置（project）
- 用户特定配置（user）

### 6.3 Flow 扩展

通过添加新的 flow 目录和 `dependency.yaml`，可以添加新的工作流。

---

## 7. 错误处理

### 7.1 异常体系

统一的异常类体系（`edp_common.exceptions`）:
- `EDPError`: 基础异常类
- `ConfigError`: 配置错误
- `EDPFileNotFoundError`: 文件未找到
- `ProjectNotFoundError`: 项目未找到
- `WorkflowError`: 工作流错误
- `ValidationError`: 验证错误

### 7.2 错误处理模式

- 统一的错误处理装饰器（`@handle_cli_error`）
- 统一的日志记录（`edp_common.logging_helpers`）
- 友好的错误提示（包含上下文和建议）

---

## 8. 性能优化

### 8.1 文件搜索缓存

- 缓存文件搜索结果
- 基于目录修改时间戳失效
- 预计性能提升 50-80%

### 8.2 配置合并优化

- 缓存已解析的配置文件
- 增量合并（只处理变更的文件）

---

## 9. 架构优势

1. **模块化**: 四个 KIT 职责清晰，便于维护和扩展
2. **统一接口**: `WorkflowManager` 简化用户使用
3. **可扩展性**: Hooks 机制支持用户自定义
4. **配置驱动**: 通过配置文件驱动，无需修改代码
5. **依赖管理**: 自动管理步骤依赖，支持并发执行

---

## 10. 架构改进方向

### 10.1 短期改进

1. **接口抽象**: 引入更抽象的接口层，便于未来替换实现
2. **依赖关系**: 更清晰地定义和文档化模块依赖关系
3. **错误处理**: 统一错误处理模式（已部分实现）

### 10.2 长期改进

1. **插件机制**: 支持插件化扩展
2. **异步执行**: 支持异步执行机制
3. **数据库存储**: 考虑使用数据库存储元数据

---

## 11. 相关文档

- [框架分析与未来方向](../FRAMEWORK_ANALYSIS_AND_FUTURE_DIRECTIONS.md)
- [统一错误处理指南](../UNIFIED_ERROR_HANDLING.md)
- [设计决策文档](design_decisions.md)（待创建）
- [API 文档](../api/)（待创建）

---

**文档维护**: 建议每次重大架构变更后更新此文档。

