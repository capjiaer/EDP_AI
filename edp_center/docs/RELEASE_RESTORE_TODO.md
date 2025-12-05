# RELEASE 恢复功能 TODO

## 功能概述

实现从 RELEASE 恢复数据到工作分支的功能，用于复现之前 run 的状态。

**状态**: ⏸️ **暂缓实现** - 等待 RELEASE 创建功能稳定后，根据实际使用需求再实现

**原因**: 
- 需要为每个 run 准备映射文件（`restore_metadata.yaml`）
- 需要在实际使用中积累经验，了解真实需求
- 先完善 RELEASE 创建功能，确保稳定后再考虑恢复功能

**相关文档**:
- [RELEASE_RESTORE_DESIGN_PROPOSAL.md](RELEASE_RESTORE_DESIGN_PROPOSAL.md) - 设计提案
- [RELEASE_RESTORE_METADATA_EXAMPLE.md](RELEASE_RESTORE_METADATA_EXAMPLE.md) - 元数据示例

## 待确认的问题

### 1. 复现一个 run 需要哪些内容？

需要明确以下问题：

#### 1.1 必需的数据文件
- [ ] 哪些文件是必需的？（例如：DEF, DB, SDF, SPEF 等）
- [ ] 哪些文件是可选的？
- [ ] 不同 flow/step 的必需文件是否不同？

#### 1.2 配置信息
- [ ] `lib_settings.tcl` 是否足够？
- [ ] 是否需要 `full.tcl` 中的配置变量？
- [ ] 是否需要恢复 `user_config.yaml` 或 `user_config.tcl`？
- [ ] 是否需要恢复 flow 的配置文件？

#### 1.3 元数据信息
- [ ] 是否需要保存原始 run 的路径信息？
- [ ] 是否需要保存原始 run 的时间戳？
- [ ] 是否需要保存原始 run 的配置快照？

#### 1.4 依赖关系
- [ ] 如果恢复 postroute，是否需要前置步骤（place, cts, route）的数据？
- [ ] 如何验证依赖的完整性？

### 2. 数据完整性验证

- [ ] 如何验证 RELEASE 中的数据是否完整？
- [ ] 如何验证数据是否损坏？
- [ ] 如何验证配置是否匹配？

### 3. 文件映射反向

- [ ] RELEASE 中的 `data/def/design.def` 应该恢复到 `data/pnr_innovus.postroute/` 的哪个位置？
- [ ] 是否需要保存原始文件路径信息？
- [ ] 如何根据配置反向映射文件位置？

### 4. 实现方案

#### 4.1 方案 A：保存完整信息
- 在 RELEASE 中保存：
  - 数据文件
  - 配置文件
  - 元数据（原始路径、时间戳、配置快照）
- 恢复时：
  - 根据元数据恢复文件到原始位置
  - 恢复配置文件
  - 验证完整性

#### 4.2 方案 B：最小化保存
- 在 RELEASE 中只保存：
  - 数据文件
  - `lib_settings.tcl`
- 恢复时：
  - 根据配置反向映射文件位置
  - 用户需要手动恢复配置

#### 4.3 方案 C：混合方案
- 在 RELEASE 中保存：
  - 数据文件
  - `lib_settings.tcl`
  - `full.tcl`（包含配置快照）
  - 元数据文件（记录原始路径映射）
- 恢复时：
  - 根据元数据恢复文件位置
  - 从 `full.tcl` 提取配置信息（可选）

## 需要调研的内容

1. **现有 RELEASE 结构分析**
   - 检查现有 RELEASE 目录，看看包含了哪些内容
   - 分析哪些内容是必需的，哪些是可选的

2. **不同 flow 的需求**
   - 分析不同 flow（pnr_innovus, pv_calibre, sta_pt 等）的复现需求
   - 确定通用的复现规则

3. **工具依赖**
   - 分析不同工具（Innovus, Calibre, PrimeTime 等）需要哪些文件才能恢复状态
   - 确定最小复现集合

## 下一步行动

1. [ ] 调研现有 RELEASE 结构
2. [ ] 分析不同 flow 的复现需求
3. [ ] 确定必需文件列表
4. [ ] 设计元数据保存方案
5. [ ] 设计文件映射反向方案
6. [ ] 实现恢复功能

## 相关文档

- [RELEASE_RESTORE_SCENARIOS.md](RELEASE_RESTORE_SCENARIOS.md) - 应用场景分析
- [RELEASE_FRAMEWORK_DESIGN.md](RELEASE_FRAMEWORK_DESIGN.md) - RELEASE 框架设计

