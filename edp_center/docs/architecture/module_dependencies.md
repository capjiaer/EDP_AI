# EDP_AI 框架模块依赖关系文档

## 📋 文档信息

- **版本**: 1.0
- **最后更新**: 2025-01-XX
- **维护者**: EDP 框架团队

本文档详细说明 EDP_AI 框架各模块之间的依赖关系。

---

## 1. 依赖关系概览

### 1.1 顶层依赖图

```
CLI / GUI / API
    │
    ▼
WorkflowManager
    │
    ├── edp_dirkit (无依赖)
    ├── edp_configkit (无依赖)
    ├── edp_cmdkit
    │   └── edp_configkit
    └── edp_flowkit
        └── edp_cmdkit
            └── edp_configkit
```

### 1.2 依赖层次

- **第 0 层（无依赖）**: `edp_dirkit`, `edp_configkit`
- **第 1 层（依赖第 0 层）**: `edp_cmdkit`
- **第 2 层（依赖第 1 层）**: `edp_flowkit`
- **第 3 层（依赖所有层）**: `WorkflowManager`

---

## 2. 详细依赖关系

### 2.1 edp_dirkit

**依赖**: 无

**被依赖**:
- `WorkflowManager` - 用于工作空间初始化

**主要模块**:
- `ProjectInitializer` - 项目初始化
- `WorkPathInitializer` - 工作路径初始化
- `BranchManager` - 分支管理

**说明**: `edp_dirkit` 是完全独立的模块，只依赖 Python 标准库。

---

### 2.2 edp_configkit

**依赖**: 无

**被依赖**:
- `edp_cmdkit` - 用于加载配置生成 `full.tcl`
- `WorkflowManager` - 用于配置加载和合并

**主要模块**:
- `ConfigLoader` - 配置加载器
- `ConfigMerger` - 配置合并器
- `TclInterpreter` - Tcl 解释器

**说明**: `edp_configkit` 是完全独立的模块，只依赖 Python 标准库和 PyYAML。

---

### 2.3 edp_cmdkit

**依赖**:
- `edp_configkit` - 用于加载配置

**被依赖**:
- `edp_flowkit` - 用于处理脚本
- `WorkflowManager` - 用于脚本处理

**主要模块**:
- `CmdProcessor` - 脚本处理器（主入口）
- `ImportProcessor` - `#import` 指令处理器
- `HooksHandler` - Hooks 处理器
- `SubStepsGenerator` - Sub_steps 生成器
- `DebugModeHandler` - Debug 模式处理器
- `FileFinder` - 文件查找器（带缓存）

**依赖说明**:
- `CmdProcessor` 使用 `edp_configkit` 加载配置生成 `full.tcl`
- `SubStepsGenerator` 可能需要读取配置文件

---

### 2.4 edp_flowkit

**依赖**:
- `edp_cmdkit` - 用于处理脚本

**被依赖**:
- `WorkflowManager` - 用于工作流执行

**主要模块**:
- `Graph` - 依赖图
- `Step` - 步骤节点
- `ICCommandExecutor` - 命令执行器
- `LSFExecutor` - LSF 作业执行器

**依赖说明**:
- `ICCommandExecutor` 使用 `edp_cmdkit` 处理脚本
- `Graph` 从 `dependency.yaml` 构建依赖关系

---

### 2.5 WorkflowManager

**依赖**:
- `edp_dirkit` - 工作空间初始化
- `edp_configkit` - 配置加载
- `edp_cmdkit` - 脚本处理
- `edp_flowkit` - 工作流执行

**被依赖**:
- CLI 命令处理函数
- GUI 应用
- Web API

**说明**: `WorkflowManager` 整合四个 KIT，提供统一接口。

---

## 3. 依赖传递关系

### 3.1 完整依赖链

```
WorkflowManager
    ├── edp_dirkit (无依赖)
    ├── edp_configkit (无依赖)
    ├── edp_cmdkit
    │   └── edp_configkit (无依赖)
    └── edp_flowkit
        └── edp_cmdkit
            └── edp_configkit (无依赖)
```

### 3.2 依赖深度

- **edp_dirkit**: 深度 0（无依赖）
- **edp_configkit**: 深度 0（无依赖）
- **edp_cmdkit**: 深度 1（依赖 edp_configkit）
- **edp_flowkit**: 深度 2（依赖 edp_cmdkit，间接依赖 edp_configkit）
- **WorkflowManager**: 深度 3（依赖所有 KIT）

---

## 4. 循环依赖检查

### 4.1 当前状态

✅ **无循环依赖**: 所有依赖关系都是单向的，不存在循环依赖。

### 4.2 依赖方向

所有依赖关系都是**自上而下**的：
- `WorkflowManager` → KITs
- `edp_flowkit` → `edp_cmdkit` → `edp_configkit`
- `edp_dirkit` 和 `edp_configkit` 独立

---

## 5. 外部依赖

### 5.1 Python 标准库

所有模块都依赖 Python 标准库：
- `pathlib` - 路径处理
- `typing` - 类型提示
- `logging` - 日志记录
- `yaml` (PyYAML) - YAML 解析
- `subprocess` - 进程执行

### 5.2 第三方库

- **PyYAML**: `edp_configkit` 用于 YAML 解析
- **可选依赖**:
  - `graphviz` - 图形可视化（可选）
  - `mermaid` - Mermaid 图形（可选）
  - `PyQt5` - GUI（可选）
  - `Flask` - Web GUI（可选）

---

## 6. 模块接口

### 6.1 公共接口

每个 KIT 都通过**公共类和方法**对外提供接口：

- **edp_dirkit**: `ProjectInitializer`, `WorkPathInitializer`, `BranchManager`
- **edp_configkit**: `ConfigLoader`, `ConfigMerger`, `files2dict`
- **edp_cmdkit**: `CmdProcessor`
- **edp_flowkit**: `Graph`, `Step`, `ICCommandExecutor`

### 6.2 接口稳定性

- **稳定接口**: 公共类和方法保持稳定，向后兼容
- **内部实现**: 内部实现可以自由修改，不影响接口

---

## 7. 依赖管理建议

### 7.1 添加新依赖

1. **评估必要性**: 确认新依赖是否必要
2. **检查循环**: 确保不会引入循环依赖
3. **文档更新**: 更新依赖关系文档
4. **测试验证**: 充分测试依赖关系

### 7.2 减少依赖

1. **提取公共模块**: 将公共功能提取到 `edp_common`
2. **接口抽象**: 通过接口减少直接依赖
3. **依赖注入**: 使用依赖注入减少硬编码依赖

---

## 8. 依赖图可视化

### 8.1 ASCII 图

```
                    ┌─────────────┐
                    │   CLI/GUI   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │WorkflowMgr  │
                    └───┬───┬───┬─┘
                        │   │   │
        ┌───────────────┘   │   └───────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌─────▼──────┐
│ edp_dirkit   │   │ edp_configkit   │   │ edp_cmdkit │
│ (无依赖)     │   │ (无依赖)        │   │            │
└──────────────┘   └────────┬────────┘   └─────┬──────┘
                            │                  │
                            └──────────┬───────┘
                                       │
                              ┌────────▼────────┐
                              │  edp_flowkit    │
                              └─────────────────┘
```

### 8.2 依赖矩阵

| 模块 | edp_dirkit | edp_configkit | edp_cmdkit | edp_flowkit | WorkflowManager |
|------|------------|----------------|------------|-------------|-----------------|
| edp_dirkit | - | ❌ | ❌ | ❌ | ✅ |
| edp_configkit | ❌ | - | ✅ | ❌ | ✅ |
| edp_cmdkit | ❌ | ✅ | - | ❌ | ✅ |
| edp_flowkit | ❌ | ❌ | ✅ | - | ✅ |
| WorkflowManager | ✅ | ✅ | ✅ | ✅ | - |

**说明**:
- ✅ = 依赖
- ❌ = 不依赖
- - = 自身

---

## 9. 依赖最佳实践

### 9.1 原则

1. **最小依赖**: 只依赖必要的模块
2. **单向依赖**: 避免循环依赖
3. **接口依赖**: 依赖接口而不是实现
4. **文档化**: 明确记录所有依赖关系

### 9.2 检查清单

添加新依赖前检查：
- [ ] 是否必要？
- [ ] 是否引入循环依赖？
- [ ] 是否影响现有功能？
- [ ] 是否更新了文档？

---

## 10. 相关文档

- [架构设计文档](architecture_overview.md)
- [设计决策文档](design_decisions.md)
- [框架分析文档](../FRAMEWORK_ANALYSIS_AND_FUTURE_DIRECTIONS.md)

---

**文档维护**: 每次依赖关系变更后，应更新此文档。

