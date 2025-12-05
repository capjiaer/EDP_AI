# CSV Compare 功能分析

## 功能概述

CSV Compare 是一个用于对比多个 RELEASE 版本的时序（timing）数据的 GUI 工具。它从 RELEASE 目录中读取 CSV 格式的时序报告，并以表格形式展示对比结果。

## 数据源

### CSV 文件位置

**当前 GUI_EXAMPLE 结构**：
```
RELEASE/P85/PR/sm3_top/release/v09001/timing/
├── place.csv
└── postroute.csv
```

**未来 EDP 结构**：
```
RELEASE/{block}/{user}/{version}/data/timing_csv/
├── place.csv
├── postroute.csv
└── ...
```

### CSV 文件格式

CSV 文件使用以下列结构：
```csv
stage,check_type,sub_category_1,sub_category_2,sub_category_3,sub_category_4,value
```

**示例数据**：
```csv
place,timing,setup,reg2reg,wns,,,-0.3
place,timing,setup,reg2reg,tns,,-3.300
place,timing,setup,reg2reg,vio_paths,,10024
place,drv,max_tran,wns,,,-0.105
place,drv,max_tran,vio_paths,,,-0.105
```

### 数据类型

1. **Timing 数据** (`check_type=timing`):
   - `sub_category_1`: `setup` 或 `hold`
   - `sub_category_2`: 类别（如 `reg2reg`, `in2reg`, `reg2out`, `mem2reg`, `reg2mem`, `reg2macro`, `macro2reg`, `reg2icg`）
   - `sub_category_3`: 指标（`wns`, `tns`, `vio_paths`）
   - `value`: 数值

2. **DRV 数据** (`check_type=drv`):
   - `sub_category_1`: DRV 类型（`max_tran`, `max_cap`, `max_length`）
   - `sub_category_2`: 指标（`wns`, `vio_paths`）
   - `value`: 数值

3. **其他数据** (`check_type=utilization`, `congestion`, `power`, `drc`, `vt_ratio` 等):
   - 这些数据在当前的 compare 功能中**不显示**，只关注 timing 和 DRV

## 核心组件

### 1. `timing_parser.py` - CSV 解析器

**功能**：
- `find_timing_directory(version_info)`: 查找版本的 timing 目录
- `parse_timing_csv_files(timing_dir, csv_files)`: 解析 CSV 文件并组织数据

**数据结构**：
```python
{
    'place': {
        'setup': {
            'reg2reg_wns': '-0.3',
            'reg2reg_tns': '-3.300',
            'reg2reg_vio_paths': '10024',
            ...
        },
        'hold': {...},
        'drv': {
            'max_tran_wns': '-0.105',
            'max_tran_vio_paths': '-0.105',
            ...
        }
    },
    'postroute': {...}
}
```

### 2. `timing_utils.py` - 工具函数

**主要函数**：
- `extract_categories_from_metrics()`: 从指标键中提取类别（如 `reg2reg`, `in2reg`）
- `extract_drv_categories_from_metrics()`: 从 DRV 指标键中提取类别（如 `max_tran`, `max_cap`）
- `apply_color_coding_to_item()`: 应用颜色编码（绿色=好，黄色=警告，红色=差）
- `apply_visual_separator()`: 添加视觉分隔符
- `create_category_header_row()`: 创建类别表头行
- `create_metric_header_row()`: 创建指标表头行
- `populate_stage_data_row()`: 填充阶段数据行

**颜色编码规则**：
- **绿色** (200, 255, 200): WNS/TNS >= 0（好）
- **黄色** (255, 255, 200): WNS/TNS >= -0.1（警告）
- **红色** (255, 200, 200): WNS/TNS < -0.1（差）

### 3. `timing_compare_window.py` - 主窗口

**功能**：
- 显示多个版本的时序对比表格
- 支持过滤（timing type, stage, category）
- 支持字体大小调整
- 支持列宽调整

**UI 结构**：
```
TimingCompareWindow
├── Header: "Comparing N versions"
├── Filter Panel
│   ├── Timing Types (SETUP, HOLD, DRV)
│   ├── Stages (place, postroute, ...)
│   ├── Categories (IN2REG, REG2REG, REG2OUT, ...)
│   └── DRV Categories (MAX_TRAN, MAX_CAP, MAX_LENGTH)
├── Font Size Control
├── Comparison Tree Widget
│   ├── SETUP
│   │   ├── Header Rows (Category + Metric headers)
│   │   ├── PLACE V1
│   │   ├── PLACE V2
│   │   ├── POSTROUTE V1
│   │   └── POSTROUTE V2
│   ├── HOLD
│   └── DRV
└── Close Button
```

**表格结构**：
- **列结构**: `STAGE` + `[Category] * 3 metrics (WNS, TNS, VIO_PATHS)`
- **行结构**: 每个版本每个阶段一行（如 `PLACE V1`, `PLACE V2`）

### 4. `release_tab.py` - RELEASE Tab 集成

**功能**：
- 在 RELEASE tab 中添加 "Compare Timing" 按钮
- 收集选中的版本信息
- 打开 `TimingCompareWindow`

**版本信息结构**：
```python
version_info = {
    'release_dir': '/path/to/RELEASE',
    'tag': 'P85',
    'sub_tag': 'PR',
    'block': 'sm3_top',
    'version': 'v09001'
}
```

## 数据流程

1. **用户操作**：
   - 在 RELEASE tab 中选择多个版本
   - 点击 "Compare Timing" 按钮

2. **数据收集**：
   - 从选中的版本中收集 `version_info`
   - 对每个版本调用 `find_timing_directory()` 查找 timing 目录

3. **数据解析**：
   - 对每个版本调用 `parse_timing_csv_files()` 解析 CSV 文件
   - 组织数据为 `{stage: {timing_type: {key: value}}}` 结构

4. **数据展示**：
   - 构建对比表格
   - 应用过滤和颜色编码
   - 显示在 `TimingCompareWindow` 中

## 需要迁移的内容

### 1. 核心功能（必需）

- [x] `timing_parser.py` - CSV 解析逻辑
- [x] `timing_utils.py` - 工具函数
- [x] `timing_compare_window.py` - 主窗口

### 2. 路径适配（需要修改）

- [ ] `find_timing_directory()`: 适配新的 EDP RELEASE 结构
  - 旧路径: `{release_dir}/{tag}/{sub_tag}/{block}/release/{version}/timing`
  - 新路径: `{release_dir}/{block}/{user}/{version}/data/timing_csv`

### 3. 集成点（需要实现）

- [ ] 在 EDP_GUI 中添加 "Compare Timing" 功能入口
- [ ] 实现版本选择机制（从 EDP RELEASE 结构中选择版本）
- [ ] 连接按钮到 `TimingCompareWindow`

## 适配 EDP 框架的修改点

### 1. 路径结构变化

**旧结构**（GUI_EXAMPLE）：
```
RELEASE/{tag}/{sub_tag}/{block}/release/{version}/timing/
```

**新结构**（EDP）：
```
RELEASE/{block}/{user}/{version}/data/timing_csv/
```

**需要修改**：
- `find_timing_directory()` 函数需要适配新路径
- 版本信息结构可能不同（没有 `tag`/`sub_tag`，有 `block`/`user`）

### 2. 版本信息结构

**旧结构**：
```python
{
    'release_dir': str,
    'tag': str,
    'sub_tag': str,
    'block': str,
    'version': str
}
```

**新结构**（推测）：
```python
{
    'release_dir': str,  # 或从 EDP 配置获取
    'block': str,
    'user': str,
    'version': str
}
```

### 3. GUI 集成

- 需要在 EDP_GUI 中创建新的功能入口
- 可能需要创建新的 tab 或菜单项
- 需要实现版本选择 UI（从 RELEASE 目录中选择版本）

## 实现计划

### Phase 1: 核心功能迁移
1. 复制 `timing_parser.py` 到 EDP 框架
2. 复制 `timing_utils.py` 到 EDP 框架
3. 复制 `timing_compare_window.py` 到 EDP 框架
4. 修改路径查找逻辑以适配 EDP 结构

### Phase 2: 路径适配
1. 修改 `find_timing_directory()` 以支持新路径结构
2. 更新版本信息结构
3. 测试路径查找功能

### Phase 3: GUI 集成
1. 在 EDP_GUI 中添加功能入口
2. 实现版本选择 UI
3. 连接按钮到 `TimingCompareWindow`
4. 测试完整流程

## 注意事项

1. **CSV 格式一致性**: 确保 EDP 生成的 CSV 格式与 GUI_EXAMPLE 中的格式一致
2. **路径兼容性**: 可能需要同时支持旧路径和新路径（向后兼容）
3. **性能**: 如果版本数量很多，需要考虑性能优化
4. **错误处理**: 需要处理缺失 CSV 文件、格式错误等情况

## 相关文件

- `GUI_EXAMPLE/ui/timing_compare_window.py` - 主窗口
- `GUI_EXAMPLE/ui/utils/timing_parser.py` - CSV 解析器
- `GUI_EXAMPLE/ui/utils/timing_utils.py` - 工具函数
- `GUI_EXAMPLE/ui/tabs/release_tab.py` - RELEASE tab 集成
- `GUI_EXAMPLE/samples/RELEASE/P85/PR/sm3_top/release/v09001/timing/` - 示例数据

