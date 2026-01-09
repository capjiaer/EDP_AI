# EDP_AI 框架 API 文档

## 📚 文档索引

本目录包含 EDP_AI 框架的详细 API 文档。

### 核心 API

1. **[WorkflowManager API](workflow_manager.md)**
   - 统一工作流管理接口
   - 整合七个核心模块的接口

2. **[edp_dirkit API](edp_dirkit.md)**
   - 目录管理和工作空间初始化
   - ProjectInitializer, WorkPathInitializer, BranchManager

3. **[edp_configkit API](edp_configkit.md)**
   - 配置加载和合并
   - YAML ↔ Tcl 转换

4. **[edp_cmdkit API](edp_cmdkit.md)**
   - 脚本处理和 #import 展开
   - Hooks 和 Sub_steps 处理

5. **[edp_flowkit API](edp_flowkit.md)**
   - 工作流执行和依赖管理
   - Graph, Step, ICCommandExecutor

6. **[edp_libkit API](../../packages/edp_libkit/README.md)**
   - 库配置生成工具
   - LibConfigGenerator, FoundryAdapter
   - 支持多种 foundry 和库类型

7. **[edp_common API](edp_common.md)**
   - 公共模块（异常、日志、错误处理）

---

## 🚀 快速导航

### 用户（使用框架）

- [WorkflowManager API](workflow_manager.md) - 主要使用接口

### 开发者（扩展框架）

- [edp_cmdkit API](edp_cmdkit.md) - 脚本处理扩展
- [edp_flowkit API](edp_flowkit.md) - 工作流扩展
- [edp_common API](edp_common.md) - 公共工具

### 维护者（维护框架）

- 所有 API 文档

---

## 📋 文档维护

- **更新频率**: 每次 API 变更后更新
- **维护者**: EDP 框架团队
- **版本**: 1.0

---

## 🔗 相关文档

- [架构设计文档](../architecture/architecture_overview.md)
- [设计决策文档](../architecture/design_decisions.md)
- [教程文档](../../tutorial/)

