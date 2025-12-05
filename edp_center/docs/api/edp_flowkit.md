# edp_flowkit API 文档

## 📋 概述

`edp_flowkit` 提供工作流执行和依赖管理功能。

**位置**: `edp_center.packages.edp_flowkit.flowkit`

**已有文档**: `edp_center/packages/edp_flowkit/docs/api.md`

---

## 核心类

### Graph

工作流图，管理步骤之间的依赖关系。

**位置**: `edp_center.packages.edp_flowkit.flowkit.Graph`

详细 API 请参考：[edp_flowkit API 文档](../../packages/edp_flowkit/docs/api.md)

### Step

步骤节点，表示工作流中的一个步骤。

**位置**: `edp_center.packages.edp_flowkit.flowkit.Step`

详细 API 请参考：[edp_flowkit API 文档](../../packages/edp_flowkit/docs/api.md)

### ICCommandExecutor

命令执行器，用于执行步骤命令。

**位置**: `edp_center.packages.edp_flowkit.flowkit.ICCommandExecutor`

详细 API 请参考：[edp_flowkit API 文档](../../packages/edp_flowkit/docs/api.md)

---

## 执行函数

### `execute_all_steps(graph, execute_func=None, merged_var=None, continue_on_failure=False)`

按拓扑顺序执行所有步骤。

**位置**: `edp_center.packages.edp_flowkit.flowkit.execute_all_steps`

详细 API 请参考：[edp_flowkit API 文档](../../packages/edp_flowkit/docs/api.md)

---

## 相关文档

- [edp_flowkit 完整 API 文档](../../packages/edp_flowkit/docs/api.md)
- [架构设计文档](../architecture/architecture_overview.md)
- [WorkflowManager API](workflow_manager.md)

