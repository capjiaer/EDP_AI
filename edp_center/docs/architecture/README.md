# EDP_AI 框架架构文档

## 📚 文档索引

本目录包含 EDP_AI 框架的架构设计文档。

### 核心文档

1. **[架构概览](architecture_overview.md)**
   - 整体架构设计
   - 四 KIT 架构详解
   - WorkflowManager 设计
   - 扩展机制
   - 性能优化

2. **[设计决策](design_decisions.md)**
   - 重要设计决策记录
   - 决策原因和权衡
   - 替代方案分析
   - 设计原则总结

3. **[模块依赖关系](module_dependencies.md)**
   - 详细的依赖关系图
   - 依赖层次说明
   - 循环依赖检查
   - 依赖管理建议

4. **[数据流](data_flow.md)**
   - 配置数据流
   - 脚本数据流
   - 依赖关系数据流
   - Hooks 数据流
   - 执行数据流

---

## 🚀 快速导航

### 新开发者

1. 先阅读 [架构概览](architecture_overview.md) 了解整体架构
2. 查看 [模块依赖关系](module_dependencies.md) 理解模块关系
3. 阅读 [数据流](data_flow.md) 了解数据流转
4. 参考 [设计决策](design_decisions.md) 理解设计原因

### 架构师/维护者

1. [设计决策](design_decisions.md) - 了解历史决策和权衡
2. [架构概览](architecture_overview.md) - 查看当前架构状态
3. [模块依赖关系](module_dependencies.md) - 规划依赖关系变更
4. [数据流](data_flow.md) - 分析数据流优化点

---

## 📋 文档维护

- **更新频率**: 每次重大架构变更后更新
- **维护者**: EDP 框架团队
- **版本**: 1.0

---

## 🔗 相关文档

- [框架分析与未来方向](../FRAMEWORK_ANALYSIS_AND_FUTURE_DIRECTIONS.md)
- [统一错误处理指南](../UNIFIED_ERROR_HANDLING.md)
- [文档问题分析](../DOCUMENTATION_ANALYSIS.md)
- [故障排查指南](../troubleshooting/troubleshooting_guide.md)
- [性能调优指南](../performance/performance_tuning.md)
- [开发指南](../development/development_guide.md)
- [迁移指南](../migration/migration_guide.md)

