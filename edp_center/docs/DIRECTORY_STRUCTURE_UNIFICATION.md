# 目录结构统一方案

## 问题分析

当前框架的目录结构存在不一致：

| 目录 | 当前格式 | 问题 |
|------|---------|------|
| `cmds/` | `cmds/flow_name/` | 只有 flow 层，没有 step 层 |
| `hooks/` | `hooks/flow_name/step_name/` | 使用斜杠分隔，两层结构 |
| `runs/` | `runs/flow_name.step_name/` | ✅ 已统一（点号分隔） |
| `logs/` | `logs/flow_name.step_name/` | ✅ 已统一（点号分隔） |
| `rpts/` | `rpts/flow_name.step_name/` | ✅ 已统一（点号分隔） |
| `data/` | `data/flow_name.step_name/` | ✅ 已统一（点号分隔） |
| `dbs/` | `dbs/` | 空目录，可能废弃 |

## 统一方案

### 方案：统一使用 `flow_name.step_name` 格式（点号分隔）

**理由**：
1. `runs/`, `logs/`, `rpts/`, `data/` 已经在使用这个格式
2. 更简洁，一层目录结构
3. 与代码中的 `step_dir_name` 格式一致
4. 便于路径管理和查找

### 统一后的目录结构

```
{branch}/
├── cmds/
│   └── flow_name/               # 保持：flow_name 格式（每个 flow 一个目录）
│       └── step_name.tcl
├── hooks/
│   └── flow_name.step_name/    # 改为：flow_name.step_name 格式（一层）
│       ├── step.pre
│       └── step.post
├── runs/
│   └── flow_name.step_name/    # ✅ 已统一
│       └── full.tcl
├── logs/
│   └── flow_name.step_name/    # ✅ 已统一
│       └── flow_name_step_name.log
├── rpts/
│   └── flow_name.step_name/    # ✅ 已统一
│       └── ...
├── data/
│   └── flow_name.step_name/    # ✅ 已统一
│       └── ...
└── dbs/                         # 建议移除或废弃
```

## 需要修改的地方

### 1. `cmds/` 目录

**当前**：`cmds/flow_name/`
**改为**：`cmds/flow_name.step_name/`

**影响**：
- 每个 step 有自己的 cmds 目录
- 文件路径：`cmds/pnr_innovus.place/place.tcl`

### 2. `hooks/` 目录

**当前**：`hooks/flow_name/step_name/`
**改为**：`hooks/flow_name.step_name/`

**影响**：
- 从两层结构改为一层结构
- 文件路径：`hooks/pnr_innovus.place/step.pre`

### 3. `dbs/` 目录

**建议**：移除或废弃，统一使用 `data/`

## 代码修改

### `edp_center/packages/edp_flowkit/flowkit/command_utils.py`

```python
# 当前代码
dirs = {
    "runs": os.path.join(base_dir, "runs", step_dir_name),
    "logs": os.path.join(base_dir, "logs", step_dir_name),
    "rpts": os.path.join(base_dir, "rpts", step_dir_name),
    "data": os.path.join(base_dir, "data", step_dir_name),
    "hooks": os.path.join(base_dir, "hooks", flow_name, sub_step_name if sub_step_name else flow_name),
    "cmds": os.path.join(base_dir, "cmds", flow_name)
}

# 修改为
dirs = {
    "runs": os.path.join(base_dir, "runs", step_dir_name),
    "logs": os.path.join(base_dir, "logs", step_dir_name),
    "rpts": os.path.join(base_dir, "rpts", step_dir_name),
    "data": os.path.join(base_dir, "data", step_dir_name),
    "hooks": os.path.join(base_dir, "hooks", step_dir_name),  # 改为 step_dir_name
    "cmds": os.path.join(base_dir, "cmds", step_dir_name)    # 改为 step_dir_name
}
```

## 迁移计划

### 阶段 1：代码修改
1. 修改 `command_utils.py` 中的目录生成逻辑
2. 更新所有使用这些目录路径的代码

### 阶段 2：目录迁移（可选）
1. 提供迁移脚本，将旧目录结构迁移到新结构
2. 或者保持向后兼容，同时支持新旧两种格式

### 阶段 3：清理
1. 移除 `dbs/` 目录的创建逻辑
2. 更新文档

## 向后兼容性

如果需要保持向后兼容，可以：
1. 先检查新格式是否存在，如果不存在再检查旧格式
2. 提供迁移工具，自动将旧格式迁移到新格式

## 总结

统一后的优势：
- ✅ 所有目录使用相同的命名格式
- ✅ 更简洁，一层目录结构
- ✅ 便于路径管理和查找
- ✅ 与代码逻辑一致

