# 多步骤 RELEASE 设计

## 1. 设计目标

支持一次 release 多个步骤的数据，提高效率，同时保持数据独立性和清晰的组织结构。

## 2. 命令行参数设计

### 方案 A：`--step` 可多次指定（推荐）

```bash
# Release 多个步骤
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute

# Release 单个步骤（向后兼容）
edp -release --release-version v09001 --step pnr_innovus.postroute
```

**优点**：
- 清晰明确，每个 step 独立指定
- 支持不同 flow 的步骤混合
- 易于扩展和解析

**实现**：使用 `argparse` 的 `action='append'`

### 方案 B：`--step` 接受逗号分隔列表

```bash
edp -release --release-version v09001 \
    --step "pnr_innovus.place,pnr_innovus.postroute"
```

**优点**：
- 简洁，一行命令
- 适合脚本自动化

**缺点**：
- 需要解析字符串
- 如果 step 名称包含逗号会有问题（虽然不太可能）

### 方案 C：支持 release 整个 flow

```bash
# Release 整个 flow 的所有步骤
edp -release --release-version v09001 --step pnr_innovus

# 需要从 dependency.yaml 读取所有步骤
```

**优点**：
- 方便，一次 release 整个 flow
- 适合完整流程的发布

**缺点**：
- 需要读取 dependency.yaml
- 可能包含不需要的步骤

## 3. 推荐方案：方案 A + 方案 C（组合）

**实现优先级**：
1. **Phase 1**：实现方案 A（`--step` 可多次指定）
2. **Phase 2**：实现方案 C（支持 release 整个 flow）

## 4. 实现细节

### 4.1 参数解析

```python
parser.add_argument(
    '--step',
    dest='release_step',
    action='append',  # 支持多次指定
    help='要发布的步骤（格式: flow_name.step_name，如 pnr_innovus.postroute）。可多次指定以 release 多个步骤'
)
```

### 4.2 处理逻辑

```python
def handle_release_cmd(manager, args) -> int:
    # 1. 解析步骤列表
    if not args.release_step:
        print("错误: 必须指定至少一个 --step 参数", file=sys.stderr)
        return 1
    
    steps = args.release_step  # 列表：['pnr_innovus.place', 'pnr_innovus.postroute']
    
    # 2. 验证步骤格式
    parsed_steps = []
    for step_str in steps:
        if '.' not in step_str:
            # 可能是 flow 名称（方案 C）
            if is_flow_name(step_str):
                # 从 dependency.yaml 读取所有步骤
                flow_steps = get_flow_steps(step_str, manager)
                parsed_steps.extend(flow_steps)
            else:
                print(f"错误: --step 格式错误: {step_str}", file=sys.stderr)
                return 1
        else:
            flow_name, step_name = step_str.split('.', 1)
            parsed_steps.append((flow_name, step_name))
    
    # 3. 去重
    parsed_steps = list(set(parsed_steps))
    
    # 4. 创建 RELEASE 目录
    release_dir = create_release_directory(...)
    
    # 5. 循环处理每个步骤
    for flow_name, step_name in parsed_steps:
        release_single_step(manager, args, release_dir, flow_name, step_name)
    
    # 6. 创建共享的 release_note.txt
    if args.release_note:
        create_release_note(release_dir, args.release_note)
    
    # 7. 设置只读权限
    set_readonly(release_dir)
```

### 4.3 单步骤处理函数

```python
def release_single_step(manager, args, release_dir, flow_name, step_name):
    """Release 单个步骤的数据"""
    # 1. 确定数据源目录
    step_dir_name = f"{flow_name}.{step_name}"
    data_dir = branch_dir / 'data' / step_dir_name
    runs_dir = branch_dir / 'runs' / step_dir_name
    
    # 2. 检查数据是否存在
    if not data_dir.exists() and not runs_dir.exists():
        print(f"[WARN] 步骤 {step_dir_name} 的数据目录不存在，跳过")
        return
    
    # 3. 加载配置
    config = manager.load_config(foundry, node, project, flow_name)
    
    # 4. 创建 step 目录
    step_target_dir = release_dir / 'data' / step_dir_name
    step_target_dir.mkdir(parents=True, exist_ok=True)
    
    # 5. 获取文件映射并复制文件
    file_mappings = get_file_mappings(config, flow_name, step_name, data_dir, args)
    copy_files_to_release(file_mappings, data_dir, step_target_dir)
    
    # 6. 复制 lib_settings.tcl 和 full.tcl
    copy_step_files(branch_dir, runs_dir, step_target_dir)
```

### 4.4 版本冲突处理

**场景 1**：版本不存在
- 直接创建新版本

**场景 2**：版本已存在，但包含不同的步骤
- **选项 A（推荐）**：允许追加，但检查步骤是否已存在
  - 如果步骤已存在：报错（或使用 `--overwrite` 覆盖）
  - 如果步骤不存在：追加到现有版本
- **选项 B**：严格模式，版本存在就报错（使用 `--strict`）

**场景 3**：版本已存在，且包含相同的步骤
- 报错（或使用 `--overwrite` 覆盖）

**实现**：
```python
def ensure_version_unique(release_root: Path, base_version: str, 
                         steps: List[Tuple], strict: bool, overwrite: bool) -> str:
    """确保版本号唯一性，支持多步骤"""
    release_dir = release_root / base_version
    
    if not release_dir.exists():
        return base_version
    
    if strict:
        raise ValueError(f"版本号 {base_version} 已存在")
    
    # 检查已存在的步骤
    existing_steps = get_existing_steps(release_dir)
    new_steps = [f"{f}.{s}" for f, s in steps]
    
    # 检查冲突
    conflicts = set(existing_steps) & set(new_steps)
    if conflicts:
        if overwrite:
            print(f"[WARN] 步骤 {conflicts} 已存在，将覆盖")
        else:
            raise ValueError(f"步骤 {conflicts} 已存在于版本 {base_version}，使用 --overwrite 覆盖")
    
    # 如果没有冲突，使用原版本号（追加模式）
    return base_version
```

## 5. 目录结构示例

### 5.1 单步骤（向后兼容）

```
RELEASE/{block}/{user}/{version}/
├── data/
│   └── pnr_innovus.postroute/
│       ├── def/
│       ├── db/
│       ├── timing_csv/
│       ├── lib_settings.tcl
│       └── full.tcl
├── release_note.txt
└── .readonly
```

### 5.2 多步骤（同一 flow）

```
RELEASE/{block}/{user}/{version}/
├── data/
│   ├── pnr_innovus.place/
│   │   ├── def/
│   │   ├── db/
│   │   ├── timing_csv/
│   │   ├── lib_settings.tcl
│   │   └── full.tcl
│   └── pnr_innovus.postroute/
│       ├── def/
│       ├── db/
│       ├── timing_csv/
│       ├── lib_settings.tcl
│       └── full.tcl
├── release_note.txt
└── .readonly
```

### 5.3 多步骤（不同 flow）

```
RELEASE/{block}/{user}/{version}/
├── data/
│   ├── pnr_innovus.postroute/
│   │   ├── def/
│   │   ├── db/
│   │   ├── lib_settings.tcl
│   │   └── full.tcl
│   └── pv_calibre.drc/
│       ├── reports/
│       ├── lib_settings.tcl
│       └── full.tcl
├── release_note.txt
└── .readonly
```

## 6. 错误处理

### 6.1 数据不存在

```python
# 如果某个步骤的数据不存在
if not data_dir.exists() and not runs_dir.exists():
    print(f"[WARN] 步骤 {step_dir_name} 的数据目录不存在，跳过")
    # 选项 A：跳过，继续处理其他步骤
    # 选项 B：报错，停止处理（使用 --strict）
```

### 6.2 配置加载失败

```python
# 如果某个步骤的配置加载失败
try:
    config = manager.load_config(...)
except Exception as e:
    print(f"[WARN] 无法加载步骤 {step_dir_name} 的配置: {e}，使用默认设置")
    config = {}
```

### 6.3 文件复制失败

```python
# 如果文件复制失败，记录错误但继续处理其他步骤
try:
    copy_files_to_release(...)
except Exception as e:
    print(f"[ERROR] 复制步骤 {step_dir_name} 的文件失败: {e}")
    # 继续处理下一个步骤
```

## 7. 性能考虑

### 7.1 并行处理

如果步骤数量很多，可以考虑并行处理：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for flow_name, step_name in parsed_steps:
        future = executor.submit(release_single_step, ...)
        futures.append(future)
    
    for future in futures:
        future.result()  # 等待完成并检查错误
```

### 7.2 进度显示

```python
total_steps = len(parsed_steps)
for idx, (flow_name, step_name) in enumerate(parsed_steps, 1):
    print(f"[INFO] 处理步骤 {idx}/{total_steps}: {flow_name}.{step_name}")
    release_single_step(...)
```

## 8. 使用示例

### 8.1 基本用法

```bash
# Release 单个步骤（向后兼容）
edp -release --release-version v09001 --step pnr_innovus.postroute

# Release 多个步骤
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute

# Release 整个 flow（Phase 2）
edp -release --release-version v09001 --step pnr_innovus
```

### 8.2 高级用法

```bash
# Release 多个步骤，包含说明
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute \
    --note "Complete PnR flow release"

# Release 多个步骤，覆盖已存在的步骤
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute \
    --overwrite

# Release 多个步骤，严格模式（版本存在则报错）
edp -release --release-version v09001 \
    --step pnr_innovus.place \
    --step pnr_innovus.postroute \
    --strict
```

## 9. 实现计划

### Phase 1：基础多步骤支持
- [x] 统一使用 `data/{step}/` 结构
- [ ] 修改 `--step` 参数支持 `action='append'`
- [ ] 实现多步骤循环处理逻辑
- [ ] 实现版本冲突检查（支持追加模式）
- [ ] 测试单步骤（向后兼容）
- [ ] 测试多步骤（同一 flow）
- [ ] 测试多步骤（不同 flow）

### Phase 2：增强功能
- [ ] 支持 release 整个 flow（从 dependency.yaml 读取）
- [ ] 实现 `--overwrite` 选项
- [ ] 实现并行处理（可选）
- [ ] 实现进度显示
- [ ] 优化错误处理

## 10. 注意事项

1. **向后兼容**：单步骤 release 必须保持向后兼容
2. **数据独立性**：每个步骤的数据必须独立存储
3. **配置共享**：同一 flow 的多个步骤可以共享配置加载
4. **错误恢复**：某个步骤失败不应该影响其他步骤
5. **性能优化**：如果步骤很多，考虑并行处理

