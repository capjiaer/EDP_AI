# RELEASE 恢复元数据示例

## 实际场景示例

假设用户执行了：
```bash
cd WORK_PATH/dongting/P85/block1/user1/main
edp -release --version v09001 --step pnr_innovus.postroute
```

### 原始工作分支结构

```
WORK_PATH/dongting/P85/block1/user1/main/
├── data/
│   └── pnr_innovus.postroute/
│       ├── a_dir/
│       │   └── design.def          # 源文件1
│       ├── output/
│       │   ├── design.db           # 源文件2
│       │   └── design.sdf          # 源文件3
│       ├── results/
│       │   └── postroute.spef      # 源文件4
│       └── timing/
│           └── postroute.csv       # 源文件5（需要保持目录结构）
├── runs/
│   └── pnr_innovus.postroute/
│       ├── full.tcl                # 完整配置脚本
│       └── lib_settings.tcl        # 库设置文件
└── ...
```

### 配置文件（config.yaml）

```yaml
# edp_center/config/SAMSUNG/S8/dongting/pnr_innovus/config.yaml
release:
  file_mappings:
    def: "a_dir/*.def *.def"
    db: "output/*.db"
    sdf: "output/*.sdf"
    spef: "results/*.spef"
    timing: "timing/*.csv"
  
  keep_structure:
    - "timing"
```

### RELEASE 目录结构（创建后）

```
WORK_PATH/dongting/P85/RELEASE/block1/user1/v09001/
├── data/
│   └── pnr_innovus.postroute/
│       ├── def/
│       │   └── design.def          # 从 a_dir/design.def 复制
│       ├── db/
│       │   └── design.db           # 从 output/design.db 复制
│       ├── sdf/
│       │   └── design.sdf          # 从 output/design.sdf 复制
│       ├── spef/
│       │   └── postroute.spef      # 从 results/postroute.spef 复制
│       ├── timing/
│       │   └── postroute.csv       # 从 timing/postroute.csv 复制（保持结构）
│       ├── lib_settings.tcl        # 从 runs/.../lib_settings.tcl 复制
│       ├── full.tcl                # 从 runs/.../full.tcl 复制
│       └── restore_metadata.yaml   # 元数据文件（新增）
├── release_note.txt                 # 发布说明
└── .readonly                        # 只读标记
```

---

## restore_metadata.yaml 完整示例

```yaml
# RELEASE/{block}/{user}/{version}/data/{flow}.{step}/restore_metadata.yaml

# 元数据版本（用于兼容性检查）
metadata_version: "1.0"

# 源信息（RELEASE 创建时的信息）
source:
  work_path: "/home/user/WORK_PATH"
  project: "dongting"
  version: "P85"
  block: "block1"
  user: "user1"
  branch: "main"
  flow: "pnr_innovus"
  step: "postroute"
  created_at: "2024-01-15T10:30:45"
  created_by: "user1"  # 当前用户名

# 文件映射信息（用于反向映射）
file_mappings:
  # DEF 文件映射
  def:
    # 源文件路径模式（相对于 data/{flow}.{step}/）
    source_patterns:
      - "a_dir/*.def"
      - "*.def"
    # 目标目录（RELEASE 中的目录）
    target_dir: "def"
    # 是否保持目录结构
    keep_structure: false
    # 实际复制的文件列表（用于验证和反向映射）
    files:
      - source: "a_dir/design.def"           # 源文件路径（相对于 data/{flow}.{step}/）
        target: "def/design.def"              # 目标文件路径（相对于 data/{flow}.{step}/）
        size: 1234567                          # 文件大小（字节）
        md5: "a1b2c3d4e5f6..."                # MD5 校验和（可选，用于完整性验证）
  
  # DB 文件映射
  db:
    source_patterns:
      - "output/*.db"
    target_dir: "db"
    keep_structure: false
    files:
      - source: "output/design.db"
        target: "db/design.db"
        size: 2345678
        md5: "b2c3d4e5f6a7..."
  
  # SDF 文件映射
  sdf:
    source_patterns:
      - "output/*.sdf"
    target_dir: "sdf"
    keep_structure: false
    files:
      - source: "output/design.sdf"
        target: "sdf/design.sdf"
        size: 3456789
        md5: "c3d4e5f6a7b8..."
  
  # SPEF 文件映射
  spef:
    source_patterns:
      - "results/*.spef"
    target_dir: "spef"
    keep_structure: false
    files:
      - source: "results/postroute.spef"
        target: "spef/postroute.spef"
        size: 4567890
        md5: "d4e5f6a7b8c9..."
  
  # Timing CSV 文件映射（保持结构）
  timing:
    source_patterns:
      - "timing/*.csv"
    target_dir: "timing"
    keep_structure: true  # 保持目录结构
    files:
      - source: "timing/postroute.csv"
        target: "timing/postroute.csv"  # 保持结构，所以路径相同
        size: 5678901
        md5: "e5f6a7b8c9d0..."

# 配置信息
config:
  # lib_settings.tcl 的位置（相对于 RELEASE 根目录）
  lib_settings_path: "data/pnr_innovus.postroute/lib_settings.tcl"
  # full.tcl 的位置（相对于 RELEASE 根目录）
  full_tcl_path: "data/pnr_innovus.postroute/full.tcl"
  
  # 可选：关键配置变量（从 full.tcl 提取，用于恢复时参考）
  key_variables:
    design_name: "sm3_top"
    tool_version: "innovus 22.31"
    # 其他关键变量...

# 依赖关系（可选，用于提示）
dependencies:
  - flow: "pnr_innovus"
    step: "place"
    required: false  # 是否必需（如果恢复 postroute，place 不是必需的，因为 postroute 包含完整设计）
    note: "前置步骤，可选"
  - flow: "pnr_innovus"
    step: "cts"
    required: false
    note: "前置步骤，可选"
  - flow: "pnr_innovus"
    step: "route"
    required: false
    note: "前置步骤，可选"

# 恢复提示信息
restore_hints:
  # 建议的恢复位置
  suggested_target_dir: "data/pnr_innovus.postroute"
  # 建议的恢复操作
  suggested_actions:
    - "恢复数据文件到 data/pnr_innovus.postroute/"
    - "恢复 lib_settings.tcl 到 runs/pnr_innovus.postroute/"
    - "可选：从 full.tcl 提取关键配置变量"
  # 注意事项
  notes:
    - "full.tcl 包含运行时路径，不建议直接复制到工作分支"
    - "建议从 full.tcl 提取关键配置变量，而不是直接复制文件"
    - "lib_settings.tcl 应该恢复到 runs/{flow}.{step}/ 目录"
```

---

## 恢复时的使用方式

### 场景 1：使用元数据恢复（推荐）

```python
# 1. 加载元数据
metadata = load_restore_metadata(release_dir, "pnr_innovus", "postroute")

# 2. 对于每个 file_mapping，反向映射文件
for target_dir, mapping_info in metadata['file_mappings'].items():
    for file_info in mapping_info['files']:
        # 源文件（在 RELEASE 中）
        release_file = release_dir / 'data' / 'pnr_innovus.postroute' / file_info['target']
        
        # 目标文件（在工作分支中）
        target_file = target_data_dir / file_info['source']  # 使用 source 路径
        
        # 复制文件
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(release_file, target_file)
```

### 场景 2：恢复配置

```python
# 1. 恢复 lib_settings.tcl
lib_settings_source = release_dir / metadata['config']['lib_settings_path']
lib_settings_target = branch_dir / 'runs' / 'pnr_innovus.postroute' / 'lib_settings.tcl'
shutil.copy2(lib_settings_source, lib_settings_target)

# 2. 可选：从 full.tcl 提取关键配置变量（不直接复制 full.tcl）
full_tcl_source = release_dir / metadata['config']['full_tcl_path']
# 解析 full.tcl，提取关键变量，更新到 user_config.yaml 或 user_config.tcl
```

---

## 关键点说明

### 1. `source` vs `target`

- **`source`**: 工作分支中的原始路径（如 `a_dir/design.def`）
- **`target`**: RELEASE 中的路径（如 `def/design.def`）

恢复时，使用 `source` 路径确定文件应该恢复到工作分支的哪个位置。

### 2. `full.tcl` 的处理

**为什么需要 `full.tcl`？**
- `full.tcl` 包含了完整的配置变量（设计名称、工具版本、路径等）
- 恢复时可能需要参考这些配置

**为什么不直接复制？**
- `full.tcl` 包含运行时路径（如 `work_path`），这些路径在工作分支中可能不同
- 直接复制可能导致路径错误

**建议的处理方式**：
- 保存 `full.tcl` 到 RELEASE（用于参考）
- 恢复时：从 `full.tcl` 提取关键配置变量，更新到 `user_config.yaml` 或 `user_config.tcl`
- 不直接复制 `full.tcl` 到工作分支

### 3. `keep_structure` 的处理

如果 `keep_structure: true`：
- 恢复时保持目录结构
- 例如：`timing/postroute.csv` -> `data/pnr_innovus.postroute/timing/postroute.csv`

如果 `keep_structure: false`：
- 恢复时只复制文件名
- 例如：`def/design.def` -> `data/pnr_innovus.postroute/a_dir/design.def`（根据 source 路径）

### 4. MD5 校验（可选）

MD5 校验和用于：
- 验证文件完整性
- 检测文件是否损坏
- 检测文件是否被修改

如果文件很大，计算 MD5 可能较慢，可以设为可选。

---

## 简化版本（如果文件很多）

如果文件很多，可以简化元数据，只保存关键信息：

```yaml
metadata_version: "1.0"

source:
  work_path: "/home/user/WORK_PATH"
  project: "dongting"
  version: "P85"
  block: "block1"
  user: "user1"
  branch: "main"
  flow: "pnr_innovus"
  step: "postroute"
  created_at: "2024-01-15T10:30:45"

file_mappings:
  def:
    source_patterns: ["a_dir/*.def", "*.def"]
    target_dir: "def"
    keep_structure: false
    # 只保存文件数量，不保存每个文件的详细信息
    file_count: 1
  
  db:
    source_patterns: ["output/*.db"]
    target_dir: "db"
    keep_structure: false
    file_count: 1

config:
  lib_settings_path: "data/pnr_innovus.postroute/lib_settings.tcl"
  full_tcl_path: "data/pnr_innovus.postroute/full.tcl"
```

恢复时：
- 使用 `source_patterns` 反向映射
- 不依赖详细的 `files` 列表

---

## 总结

`restore_metadata.yaml` 应该包含：

1. ✅ **源信息**：RELEASE 创建时的上下文（project, version, block, user, branch 等）
2. ✅ **文件映射**：每个文件的源路径和目标路径（用于反向映射）
3. ✅ **配置路径**：`lib_settings.tcl` 和 `full.tcl` 的位置
4. ✅ **依赖关系**：前置步骤的提示（可选）
5. ✅ **恢复提示**：建议的恢复操作和注意事项

最关键的是 **`file_mappings` 中的 `source` 路径**，这是恢复时确定文件位置的关键。

