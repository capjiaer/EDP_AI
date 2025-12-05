# .run_info 扩展方案设计

## 1. 扩展的 .run_info 格式

### 当前格式
```yaml
runs:
- timestamp: '2025-11-10 18:09:44'
  flow: pv_calibre
  step: ipmerge
  utils: []
  hooks:
    step: []
    utils: {}
```

### 扩展后格式
```yaml
runs:
- timestamp: '2025-11-10 18:09:44'
  flow: pv_calibre
  step: ipmerge
  utils: []
  hooks:
    step: []
    utils: {}
  # 新增字段
  status: success  # success, failed, running, cancelled
  duration: 3600  # 执行时间（秒）
  lsf_job_id: "12345"  # LSF 作业 ID（如果有）
  resources:
    cpu_used: 16
    peak_memory: 32000  # MB
    queue: "default"
  output_files:  # 关键输出文件列表
    - cmds/pv_calibre/ipmerge/ipmerge.tcl
    - logs/pv_calibre/ipmerge/ipmerge.log
  error: null  # 错误信息（如果失败）
  validation:  # 验证结果（可选）
    passed: true
    files_checked: []
    timing_compare: null  # timing compare 结果（如果有）
```

## 2. 数据收集点

### 2.1 执行前（在 `run_handler.py` 中）
- 记录开始时间
- 记录配置信息（CPU、内存等）
- 记录输出文件路径

### 2.2 执行中（在 `ICCommandExecutor.run_cmd` 中）
- 提取 LSF job ID（如果有）
- 监控资源使用（如果可能）

### 2.3 执行后（在 `ICCommandExecutor.run_cmd` 返回后）
- 记录执行状态（success/failed）
- 计算执行时间
- 记录错误信息（如果失败）
- 检查输出文件是否存在
- 收集性能数据（从 LSF 日志或系统监控）

## 3. 功能设计

### 3.1 历史查询功能 (`edp -history`)

```bash
# 查看当前分支的运行历史
edp -history

# 查看指定步骤的历史
edp -history pv_calibre.ipmerge

# 查看最近 N 条记录
edp -history --limit 10

# 查看失败的历史
edp -history --status failed

# 查看指定时间范围的历史
edp -history --from "2025-11-10" --to "2025-11-12"

# 查看性能统计
edp -history --stats
```

输出示例：
```
运行历史 (共 25 条记录):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] 2025-11-14 17:58:22 | pnr_innovus.place | ✅ success | 1h 23m | CPU: 16 | Mem: 32GB
[2] 2025-11-14 17:57:46 | pnr_innovus.place | ✅ success | 1h 25m | CPU: 16 | Mem: 32GB
[3] 2025-11-14 11:12:38 | pnr_innovus.place | ❌ failed  | 0h 05m | CPU: 16 | Mem: 32GB
...
```

### 3.2 回滚功能 (`edp -rollback`)

```bash
# 回滚到上一次成功的执行
edp -rollback

# 回滚到指定的历史记录（通过索引）
edp -rollback --index 5

# 回滚到指定的步骤（从历史中找到最后一次成功执行）
edp -rollback pv_calibre.ipmerge

# 回滚到指定时间点的状态
edp -rollback --to "2025-11-10 18:09:44"

# 预览回滚操作（不实际执行）
edp -rollback --dry-run
```

回滚操作：
1. 从 `.run_info` 中找到目标记录
2. 检查输出文件是否存在
3. 恢复输出文件（从备份或重新生成）
4. 更新 `.run_info` 标记回滚点

### 3.3 性能分析功能 (`edp -stats`)

```bash
# 查看当前分支的性能统计
edp -stats

# 查看指定步骤的性能统计
edp -stats pv_calibre.ipmerge

# 查看性能趋势
edp -stats --trend

# 导出性能报告
edp -stats --export report.html
```

输出示例：
```
性能统计 - pnr_innovus.place
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
执行次数: 25
成功率: 96% (24/25)
平均执行时间: 1h 28m
最短执行时间: 1h 15m
最长执行时间: 1h 45m

资源使用:
  平均 CPU: 16 核
  平均内存: 32 GB
  Peak 内存: 45 GB

最近趋势:
  [图表显示执行时间趋势]
```

### 3.4 结果验证功能 (`edp -validate`)

```bash
# 验证最后一次执行的结果
edp -validate

# 验证指定步骤的结果
edp -validate pv_calibre.ipmerge

# 验证并生成报告
edp -validate --report

# Timing compare（如果支持）
edp -validate --timing-compare branch1 branch2
```

验证内容：
1. 检查关键输出文件是否存在
2. 检查文件大小是否合理
3. 检查日志文件中是否有错误
4. Timing compare（如果配置了）

## 4. 实现计划

### 阶段 1: 扩展数据收集
1. 修改 `update_run_info` 函数，支持更多字段
2. 在 `ICCommandExecutor.run_cmd` 中收集执行信息
3. 添加性能数据收集（从 LSF 或系统监控）

### 阶段 2: 历史查询功能
1. 实现 `edp -history` 命令
2. 实现历史记录过滤和排序
3. 实现性能统计

### 阶段 3: 回滚功能
1. 实现文件快照机制
2. 实现回滚逻辑
3. 添加回滚验证

### 阶段 4: 结果验证
1. 实现文件验证逻辑
2. 实现 Timing compare 功能
3. 生成验证报告

## 5. 技术细节

### 5.1 性能数据收集

#### LSF 作业
- 从 `bjobs -l` 获取资源使用信息
- 从 `bhist -l` 获取历史作业信息
- 从日志文件中提取性能数据

#### 本地执行
- 使用 `psutil` 监控进程资源使用
- 记录进程启动和结束时间
- 计算峰值内存使用

### 5.2 文件快照

对于关键步骤，可以：
1. 在执行前创建文件快照（使用硬链接或复制）
2. 在 `.run_info` 中记录快照路径
3. 回滚时从快照恢复

### 5.3 数据存储

- `.run_info` 文件：存储运行历史（YAML 格式）
- `.run_snapshots/` 目录：存储文件快照（可选）
- `.run_stats/` 目录：存储性能统计数据（可选）

## 6. 向后兼容

- 旧的 `.run_info` 文件仍然可以读取
- 新字段都是可选的
- 如果字段不存在，使用默认值或跳过

## 7. 示例代码结构

```
edp_center/main/cli/commands/
├── run_helpers.py          # 扩展 update_run_info
├── history_handler.py      # edp -history 命令
├── rollback_handler.py     # edp -rollback 命令
├── stats_handler.py        # edp -stats 命令
└── validate_handler.py    # edp -validate 命令
```

