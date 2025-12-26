# 参数别名建议

## 📋 当前别名情况

### ✅ 已有别名（无需修改）

| 完整参数 | 别名 | 说明 |
|---------|------|------|
| `--branch` | `-b` | 创建分支 |
| `--info` | `-i` | 查看信息 |
| `--from` | `-fr` | 起始步骤 |
| `--to` | `-to` | 结束步骤 |
| `--from-step` | `-fs` | 执行范围 |
| `--tutorial` | `-tutor` | 查看教程 |
| `--project` | `-prj` | 项目名称 |
| `--version` | `-v` | 项目版本 |
| `--config` | `-cfg` | 配置文件 |
| `--graph-format` | `--format` | 输出格式 |
| `--graph-output` | `--output` | 输出文件 |
| `--graph-depth` | `--depth` | 深度限制 |
| `--graph-layout` | `--layout` | 布局引擎 |
| `--graph-title` | `--title` | 图表标题 |
| `--graph-focus` | `--focus-step` | 聚焦步骤 |

---

## 💡 建议添加的别名

**设计原则**：别名要有意义、易记忆，不要太短（避免记不住）

### 高优先级（常用且较长）

| 完整参数 | 建议别名 | 理由 | 冲突检查 |
|---------|---------|------|----------|
| `--release-version` | `-rver` | 有意义的缩写：release-version → rver | ✅ 无冲突 |
| `--release-block` | `-rblock` | 有意义的缩写：release-block → rblock | ✅ 无冲突 |
| `--from-branch-step` | `-from-step` | 保留关键部分，更易理解 | ✅ 无冲突 |
| `--work-path` | `-wpath` | 有意义的缩写：work-path → wpath | ✅ 无冲突 |
| `--lib-output-dir` | `-odir` | 有意义的缩写：output-dir → odir | ✅ 无冲突 |
| `--lib-path` | `-lpath` | 有意义的缩写：lib-path → lpath | ✅ 无冲突 |
| `--web-port` | `-port` | 简洁且有意义 | ✅ 无冲突 |
| `--graph-format` | `-format` | 已有 `--format`，再加短别名 | ✅ 无冲突 |
| `--graph-output` | `-output` | 已有 `--output`，再加短别名 | ✅ 无冲突 |

### 中优先级（信息查询相关）

| 完整参数 | 建议别名 | 理由 | 冲突检查 |
|---------|---------|------|----------|
| `--history` | `-hist` | 有意义的缩写，避免与 `-h/--help` 冲突 | ✅ 无冲突 |
| `--stats` | `-stats` | 保持完整，避免与 `--status` 混淆 | ✅ 无冲突 |
| `--rollback` | `-rollback` | 保持完整，避免混淆 | ✅ 无冲突 |
| `--validate` | `-val` | 有意义的缩写，避免与 `-v/--version` 冲突 | ✅ 无冲突 |
| `--timing-compare` | `-tcompare` | 有意义的缩写：timing-compare → tcompare | ✅ 无冲突 |

### 低优先级（较少使用）

| 完整参数 | 建议别名 | 理由 | 冲突检查 |
|---------|---------|------|----------|
| `--export` | `-export` | 保持完整，避免混淆 | ✅ 无冲突 |
| `--limit` | `-limit` | 保持完整，避免与 `-l/--lib` 冲突 | ✅ 无冲突 |
| `--status` | `-status` | 保持完整，避免与 `--stats` 混淆 | ✅ 无冲突 |
| `--index` | `-idx` | 简短但有意义 | ✅ 无冲突 |
| `--to-time` | `-totime` | 有意义的缩写 | ✅ 无冲突 |
| `--note` | `-note` | 保持完整，避免与 `-n/--node` 冲突 | ✅ 无冲突 |

---

## 🎯 推荐实现的别名（按优先级）

### 第一批（高优先级，强烈推荐）

```python
# Release 相关
'--release-version': '-rver'      # release-version → rver（有意义）
'--release-block': '-rblock'      # release-block → rblock（有意义）
'--from-branch-step': '-from-step'  # 保留关键部分，更易理解

# 路径相关
'--work-path': '-wpath'           # work-path → wpath（有意义）

# Lib 相关
'--lib-output-dir': '-odir'       # output-dir → odir（有意义）
'--lib-path': '-lpath'            # lib-path → lpath（有意义）

# Graph 相关
'--graph-format': '-format'       # 已有 --format，再加短别名
'--graph-output': '-output'       # 已有 --output，再加短别名

# Web 相关
'--web-port': '-port'             # 简洁且有意义
```

### 第二批（中优先级，推荐）

```python
# 信息查询相关
'--history': '-hist'              # history → hist（有意义）
'--stats': '-stats'               # 保持完整，避免混淆
'--rollback': '-rollback'         # 保持完整，避免混淆
'--validate': '-val'              # validate → val（有意义）
'--timing-compare': '-tcompare'   # timing-compare → tcompare（有意义）
```

### 第三批（低优先级，可选）

```python
'--export': '-export'             # 保持完整
'--limit': '-limit'              # 保持完整
'--status': '-status'            # 保持完整
'--index': '-idx'                # index → idx（常见缩写）
'--to-time': '-totime'           # to-time → totime（有意义）
'--note': '-note'                # 保持完整
```

---

## 📝 使用示例（添加别名后）

### Release 命令（更简洁且易记）

```bash
# 之前
edp -release --release-version v09001 --step pnr_innovus.postroute --release-block block1

# 之后（使用有意义的别名）
edp -release -rver v09001 --step pnr_innovus.postroute -rblock block1
```

### Lib 命令（更简洁且易记）

```bash
# 之前
edp -lib --foundry Samsung --node ln08lpu_gp --lib-path /path/to/lib --lib-type STD --lib-output-dir /path/to/output

# 之后（使用有意义的别名）
edp -lib --foundry Samsung --node ln08lpu_gp -lpath /path/to/lib --lib-type STD -odir /path/to/output
```

### Graph 命令（更简洁且易记）

```bash
# 之前
edp -graph --graph-format png --graph-output dependency.png

# 之后（使用有意义的别名）
edp -graph -format png -output dependency.png
```

### 信息查询（更简洁且易记）

```bash
# 之前
edp --history --limit 10 --status failed
edp --validate --timing-compare branch1 branch2

# 之后（使用有意义的别名）
edp -hist -limit 10 -status failed
edp -val -tcompare branch1 branch2
```

### 分支创建（更简洁且易记）

```bash
# 之前
edp -b branch1 --from-branch-step "branch1:pnr_innovus.init"

# 之后（使用有意义的别名）
edp -b branch1 -from-step "branch1:pnr_innovus.init"
```

---

## ⚠️ 注意事项

1. **避免冲突**：确保新别名不与现有参数冲突
2. **保持一致性**：同类参数使用相似的命名模式
3. **易于记忆**：别名应该直观易记，**不要太短**（避免记不住）
4. **向后兼容**：保留完整参数名，别名只是补充
5. **有意义**：别名应该是有意义的缩写，而不是随意的字母组合
   - ✅ 好：`-rver` (release-version), `-lpath` (lib-path), `-odir` (output-dir)
   - ❌ 不好：`-rv` (太短，记不住), `-lp` (太短，容易混淆), `-od` (太短，记不住)

## 📊 别名设计原则

1. **保留关键部分**：如 `-from-step` 保留 "from" 和 "step"
2. **有意义的缩写**：如 `-rver` 来自 "release-version"
3. **避免单字母**：除非是通用约定（如 `-v` 表示 version）
4. **保持可读性**：别名应该能让人联想到完整参数名

