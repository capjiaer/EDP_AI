# RELEASE 恢复数据应用场景分析

## 应用场景

### 场景 1：从稳定版本恢复继续工作

**场景描述**：
- 用户 A 发布了 `v09001` 版本的 `pnr_innovus.postroute` 结果
- 用户 B 需要在这个稳定版本的基础上继续优化（例如做 ECO）
- 用户 B 创建新分支，从 RELEASE 恢复数据作为起点

**工作流**：
```bash
# 用户 B 创建新分支
cd WORK_PATH/dongting/P85/block1/userB
edp -b eco_branch

# 从 RELEASE 恢复数据
cd eco_branch
edp -release-restore --from-release block1/userA/v09001 --step pnr_innovus.postroute

# 继续工作
edp -run pnr_innovus.eco
```

### 场景 2：回滚到之前的稳定版本

**场景描述**：
- 用户当前工作分支的实验结果不理想
- 需要回滚到之前发布的稳定版本 `v09001`
- 在当前分支恢复 RELEASE 数据，覆盖当前结果

**工作流**：
```bash
# 在当前分支恢复 RELEASE 数据
cd WORK_PATH/dongting/P85/block1/user1/main
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --overwrite

# 继续从稳定版本开始工作
edp -run pnr_innovus.eco
```

### 场景 3：从其他用户的 RELEASE 恢复（团队协作）

**场景描述**：
- 用户 A 发布了 `v09001` 版本的 `pnr_innovus.postroute` 结果
- 用户 B 需要基于用户 A 的结果继续工作
- 用户 B 创建新分支，从用户 A 的 RELEASE 恢复数据

**工作流**：
```bash
# 用户 B 创建新分支
cd WORK_PATH/dongting/P85/block1/userB
edp -b continue_from_userA

# 从用户 A 的 RELEASE 恢复数据
cd continue_from_userA
edp -release-restore --from-release block1/userA/v09001 --step pnr_innovus.postroute

# 继续工作
edp -run pnr_innovus.eco
```

### 场景 4：创建新分支时从 RELEASE 恢复（替代 from-branch-step）

**场景描述**：
- 用户想要创建新分支，但不想从其他分支恢复，而是从已发布的 RELEASE 恢复
- 这样可以确保起点是一个稳定、已验证的版本

**工作流**：
```bash
# 创建新分支时从 RELEASE 恢复
cd WORK_PATH/dongting/P85/block1/user1
edp -b new_branch --from-release block1/user1/v09001:pnr_innovus.postroute

# 新分支已经包含了 RELEASE 的数据
cd new_branch
edp -run pnr_innovus.eco
```

### 场景 5：恢复多个步骤的数据

**场景描述**：
- 用户需要恢复多个步骤的数据（例如 place 和 postroute）
- 从同一个 RELEASE 版本恢复多个步骤

**工作流**：
```bash
# 恢复多个步骤
edp -release-restore --from-release block1/user1/v09001 \
    --step pnr_innovus.place pnr_innovus.postroute
```

### 场景 6：选择性恢复（只恢复部分文件类型）

**场景描述**：
- 用户只需要恢复某些文件类型（例如只需要 DEF 和 DB，不需要 SDF）
- 可以指定要恢复的文件类型

**工作流**：
```bash
# 只恢复 DEF 和 DB 文件
edp -release-restore --from-release block1/user1/v09001 \
    --step pnr_innovus.postroute \
    --include-types def db
```

## 功能设计建议

### 命令格式

```bash
# 基本用法
edp -release-restore --from-release {block}/{user}/{version} --step {flow}.{step}

# 指定目标分支（默认当前分支）
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --branch target_branch

# 覆盖模式（覆盖已存在的文件）
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --overwrite

# 选择性恢复
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --include-types def db

# 创建新分支时从 RELEASE 恢复
edp -b new_branch --from-release block1/user1/v09001:pnr_innovus.postroute
```

### 实现要点

1. **数据恢复位置**：
   - 恢复到 `data/{flow}.{step}/` 目录
   - 恢复 `lib_settings.tcl` 到 `runs/{flow}.{step}/` 目录
   - 可选：恢复 `full.tcl` 到 `runs/{flow}.{step}/` 目录

2. **文件映射反向**：
   - RELEASE 中的 `data/def/design.def` -> 恢复到 `data/pnr_innovus.postroute/output/design.def`（根据配置）
   - 或者恢复到原始位置（如果 RELEASE 中保存了路径信息）

3. **冲突处理**：
   - 默认：如果文件已存在，跳过（不覆盖）
   - `--overwrite`：覆盖已存在的文件
   - `--backup`：覆盖前备份原文件

4. **验证**：
   - 验证 RELEASE 目录是否存在
   - 验证 RELEASE 版本是否有效
   - 验证目标分支是否存在

## 与现有功能的对比

### 与 `--from-branch-step` 的区别

| 特性 | `--from-branch-step` | `--from-release` |
|------|---------------------|------------------|
| 数据来源 | 其他工作分支 | RELEASE 目录 |
| 数据状态 | 可能正在修改 | 已发布、只读、稳定 |
| 适用场景 | 从其他分支继续工作 | 从稳定版本恢复 |
| 数据完整性 | 可能不完整 | 完整、已验证 |
| 版本管理 | 无版本概念 | 有版本号管理 |

### 使用建议

- **使用 `--from-branch-step`**：当需要从其他用户的工作分支继续工作时
- **使用 `--from-release`**：当需要从稳定、已验证的版本恢复时

## 总结

从 RELEASE 恢复数据的主要价值：
1. **稳定性**：从已验证的稳定版本恢复
2. **可追溯性**：有明确的版本号，便于追溯
3. **团队协作**：方便团队成员共享和复用稳定版本
4. **回滚能力**：可以快速回滚到之前的稳定版本

