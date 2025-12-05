# RELEASE 框架设计文档

## 1. 设计目标

RELEASE 目录用于用户发布和共享运行结果，需要：
- 与现有框架结构（WORK_PATH/{project}/{version}/{block}/{user}/{branch}）良好集成
- 支持版本管理和状态追踪
- 包含完整的元数据信息
- 便于查找和使用
- **防止版本覆盖和数据篡改**
- **支持同一用户一天内多次发布**

## 2. 核心设计原则

### 2.1 版本唯一性
- 每个 RELEASE 版本必须是唯一的，不能覆盖
- 版本号一旦创建就不可修改
- 使用时间戳确保唯一性

### 2.2 只读保护
- RELEASE 目录一旦创建就应该是只读的
- 防止用户篡改已发布的数据
- 只有管理员可以修改（如果需要）

### 2.3 版本号设计
- 支持用户自定义版本号（如 v09001）
- 如果版本号已存在，自动添加时间戳后缀
- 或者强制使用时间戳作为版本号的一部分

## 3. 推荐的目录结构

### 3.1 位置和层级

**方案 A：按用户分组（推荐）**

```
WORK_PATH/
└── {project}/              # 项目名称
    └── {version}/          # 项目版本
        ├── {block}/         # 块名称
        │   └── {user}/      # 用户名
        │       └── {branch}/# 分支名称
        │           ├── cmds/
        │           ├── runs/
        │           ├── logs/
        │           └── ...
        └── RELEASE/         # RELEASE 目录（与 block 同级）
            └── {block}/     # 块名称
                └── {user}/  # 用户名（按用户分组）
                    └── {version}/  # RELEASE 版本（如 v09001 或 v09001_20240115_1030）
                        ├── data/          # 数据目录（所有数据文件都在这里）
                        ├── lib_settings.tcl  # 库设置文件（必须）
                        ├── release_note.txt  # 发布说明（可选）
                        ├── full.tcl          # 完整脚本（可选）
                        └── .readonly        # 只读标记（框架自动创建）
```

**方案 B：扁平结构（备选）**

```
RELEASE/{block}/{version}_{timestamp}/
```

**推荐使用方案 A**，原因：
- 按用户分组，便于管理
- 同一用户的不同版本集中在一起
- 避免不同用户之间的版本号冲突
- 便于权限管理

### 3.2 版本号规则

版本号格式：`{base_version}[_{timestamp}]`

- `base_version`: 用户指定的版本号（如 `v09001`）
- `timestamp`: 时间戳（格式：`YYYYMMDD_HHMMSS`），仅在版本号冲突时自动添加

示例：
- `v09001` - 第一次创建，无冲突
- `v09001_20240115_103045` - 如果 v09001 已存在，自动添加时间戳
- `v09001_20240115_143022` - 同一天多次发布，使用时间戳区分

### 3.3 详细结构

**单步骤结构**：
```
RELEASE/{block}/{user}/{version}/
├── data/                   # 数据目录
│   └── {flow}.{step}/      # 每个 step 一个目录（统一结构）
│       ├── config/         # 配置文件
│       ├── db/             # 数据库文件
│       ├── def/            # Design Exchange Format
│       ├── hcell/          # Hard Cell
│       ├── ilm/            # Interface Logic Model
│       ├── layout_et/      # Layout Extraction
│       ├── lef/            # Library Exchange Format
│       ├── lib/            # 库文件
│       ├── oas/            # Open Artwork System
│       ├── sdf/            # Standard Delay Format
│       ├── spef/           # Standard Parasitic Exchange Format
│       ├── spice/          # SPICE netlist
│       ├── svf/            # Synopsys Verification Format
│       ├── twf/            # Timing Window Format
│       ├── upf/            # Unified Power Format
│       ├── verilog/        # Verilog netlist
│       ├── timing_csv/     # 时序数据（CSV 格式）
│       ├── reports/        # 报告文件（可选）
│       ├── lib_settings.tcl # 该 step 的库设置文件（必须）
│       └── full.tcl        # 该 step 的完整脚本（可选）
├── release_note.txt        # 发布说明（可选，所有 step 共享）
└── .readonly               # 只读标记文件（框架自动创建）
```

**多步骤结构**（如果一次 release 多个步骤）：
```
RELEASE/{block}/{user}/{version}/
├── data/
│   ├── pnr_innovus.place/      # place 步骤的数据
│   │   ├── def/
│   │   ├── db/
│   │   ├── timing_csv/
│   │   ├── lib_settings.tcl
│   │   └── full.tcl
│   └── pnr_innovus.postroute/  # postroute 步骤的数据
│       ├── def/
│       ├── db/
│       ├── timing_csv/
│       ├── lib_settings.tcl
│       └── full.tcl
├── release_note.txt
└── .readonly
```

**重要说明**：
- 统一使用 `data/{flow}.{step}/` 结构，即使是单步骤也这样
- 每个 step 的 `lib_settings.tcl` 和 `full.tcl` 独立存储在自己的 step 目录下
- `release_note.txt` 在根目录，所有 step 共享

### 3.4 版本号层级总结

**推荐结构：`RELEASE/{block}/{user}/{version}/`**

理由：
1. **{block}** - 按块分组，不同 block 的 RELEASE 分开
2. **{user}** - 按用户分组，避免版本号冲突，便于权限管理
3. **{version}** - 版本号，支持时间戳后缀避免覆盖

这样设计的好处：
- ✅ 同一用户一天内可以发布多个版本（通过时间戳区分）
- ✅ 不同用户的版本号不会冲突（按用户分组）
- ✅ 便于权限管理（每个用户只能管理自己的 RELEASE）
- ✅ 便于查找（按 block 和 user 组织）

## 6. RELEASE 文件说明

### 6.1 必需文件

**data/{flow}.{step}/**（必须）
- 每个 step 的数据都放在 `data/{flow}.{step}/` 目录下
- 子目录根据文件类型组织（def, db, sdf, spef 等，统一小写）
- 即使是单步骤，也使用 `data/{flow}.{step}/` 结构

**lib_settings.tcl**（必须）
- 库设置文件，包含库路径、版本等信息
- 格式：Tcl 脚本
- 位置：`data/{flow}.{step}/lib_settings.tcl`（每个 step 独立）

### 6.2 可选文件

**release_note.txt**（可选）
- 发布说明文件
- 格式：纯文本
- 位置：RELEASE 根目录

**full.tcl**（可选）
- 完整脚本文件
- 包含完整的运行脚本
- 位置：`data/{flow}.{step}/full.tcl`（每个 step 独立）

**其他文件**（可选）
- 根据项目需要，可以添加其他文件到根目录
- 例如：`bom.tcl`, `config.yaml` 等

### 6.3 自动生成文件

**.readonly**（框架自动创建）
- 只读标记文件
- 框架在创建 RELEASE 后自动生成
- 用于标记该 RELEASE 为只读状态
design_name: "sm3_top"         # 设计名称
version: "v09001"              # 版本号
target_frequency: 800          # 目标频率（可选）
target_area: 0.5               # 目标面积（可选）
power_budget: 1.2              # 功耗预算（可选）
```

## 4. 版本唯一性和只读保护

### 4.1 版本唯一性检查

创建 RELEASE 时，框架会：
1. 检查目标版本号是否已存在：`RELEASE/{block}/{user}/{version}/`
2. 如果已存在：
   - **选项 A（推荐）**：自动添加时间戳后缀
     - `v09001` → `v09001_20240115_103045`
   - **选项 B**：报错，要求用户指定新版本号
3. 如果不存在：直接使用用户指定的版本号

### 4.2 只读保护机制

RELEASE 目录创建后，框架会：
1. **设置目录权限为只读**（chmod 555 或 Windows 只读属性）
2. **创建 `.readonly` 标记文件**，标识这是一个只读的 RELEASE
3. **防止覆盖**：如果目录已存在，拒绝创建

### 4.3 权限管理

- **创建者（user）**：只能创建，不能修改已创建的 RELEASE
- **管理员**：可以修改或删除 RELEASE（需要特殊权限）
- **其他用户**：只能读取

## 5. 文件选择机制

### 5.1 问题：如何决定哪些文件需要 release？

在 `data/` 目录下可能有很多文件，但不是所有文件都需要 release。需要有一个机制来决定哪些文件应该被包含。

### 5.2 解决方案：文件到目录的映射配置

每个 flow 需要声明：
1. **哪些文件需要 release**
2. **这些文件应该放到 RELEASE 的哪个目录下**

#### 方案：在 Flow 配置中定义文件映射（推荐）

**重要：使用字典的字典格式，而不是列表的字典，以确保与 Tcl 转换兼容**

在每个 flow 的配置文件中定义文件到目录的映射规则：

```yaml
# edp_center/config/{foundry}/{node}/{project}/pnr_innovus/config.yaml
release:
  # 文件到目录的映射规则（简洁格式）
  # 格式：目标目录名 -> 源文件路径列表
  file_mappings:
    # def 目录：匹配 data/pnr_innovus.place/ 下的所有 .def 文件（递归）
    def: "**/*.def"
    
    # 或者只匹配根目录下的 .def（不递归）
    # def: "*.def"
    
    # 或者匹配特定目录下的 .def（不递归）
    # def: "output/*.def"
    
    # 或者匹配特定目录下的 .def（递归搜索子目录）
    # def: "a_dir/**/*.def"
    
    # 或者多个路径组合
    # def: "*.def output/*.def a_dir/**/*.def"
    
    # db 目录
    db: "output/*.db"
    
    # sdf 目录
    sdf: "results/*.sdf"
    
    # spef 目录
    spef: "results/*.spef"
    
    # config 目录：多个文件模式
    config: "**/*.mmc.tcl config/*.sdc"
    
    # verilog 目录：多个文件模式
    verilog: "netlist/*.v netlist/*.vg"
    
    # timing 目录：保持目录结构
    timing: "timing/*.csv"
    
    # lib 目录：整个目录（使用 @ 前缀表示目录）
    lib: "@libs"
    
    # 或者混合使用：文件和目录
    # lib: "@libs libs/*.lib"
  
  # 按 step 的特定规则（可选，会覆盖上面的通用规则）
  step_rules:
    postroute:
      file_mappings:
        DEF: "*.def a_dir/*.def"
        SDF: "results/*.sdf"
        SPEF: "results/*.spef"
        timing: "timing/postroute.csv"
    
    place:
      file_mappings:
        DEF: "*.def"
        timing: "timing/place.csv"
```

#### 配置说明

**为什么使用字典而不是列表？**

框架的 YAML 到 Tcl 转换机制：
- **字典的字典** → Tcl 数组：`release(file_mappings,def_files,pattern) = "*.def"`
  - ✅ 可以在 Tcl 中直接访问每个字段
  - ✅ `release` 会变成一个 Tcl 数组（这是正常的，框架的标准行为）
- **列表的字典** → Tcl list 中的字符串：`release(file_mappings) = {pattern *.def target_dir DEF} ...`
  - ❌ 字典被转换为字符串，难以在 Tcl 中解析和访问

因此使用字典格式，确保在 Tcl 中可以正确访问每个字段。

**关于 `release` 数组：**
- 是的，`release` 会变成一个 Tcl 数组（`array exists release` 返回 1）
- 这是框架的正常行为：所有嵌套字典都会被转换为 Tcl 数组
- 在 Tcl 中可以通过 `release(file_mappings,def_files,pattern)` 的方式访问
- 不会影响其他配置项的使用

**file_mappings 字段说明：**
- **格式**：`目标目录名: 源文件路径列表`
  - **key**：目标目录名（如 `def`, `db`, `sdf`, `lib` 等，统一小写）
  - **value**：源文件路径列表，支持两种格式：
    1. **字符串格式**（空格分隔）：`"a_dir/*.def xxx.def abc.def"`
    2. **列表格式**（YAML 列表）：`["a_dir/*.def", "xxx.def", "abc.def"]`

- **源文件路径规则**（相对于 `data/{flow}.{step}/`）：
  - **精确文件**：`a_dir/xx.def` - 复制指定文件
  - **根目录所有文件**：`*.def` - 匹配根目录下的所有 .def 文件（不递归）
  - **子目录所有文件**：`a_dir/*.def` - 匹配 `a_dir/` 目录下的所有 .def 文件（不递归）
  - **子目录递归搜索**：`a_dir/**/*.def` - 递归搜索 `a_dir/` 及其所有子目录下的所有 .def 文件
  - **递归搜索所有文件**：`**/*.def` - 递归搜索整个目录树下的所有 .def 文件
  - **整个目录**：`@libs` - 复制整个目录及其所有内容（使用 `@` 前缀）
  
**示例**：
  - 匹配 `data/pnr_innovus.place/` 根目录下的所有 .def：`*.def`
  - 匹配 `data/pnr_innovus.place/` 下所有目录的所有 .def：`**/*.def`
  - 匹配 `data/pnr_innovus.place/output/` 下的所有 .def：`output/*.def`（不递归）
  - 匹配 `data/pnr_innovus.place/output/` 及其子目录的所有 .def：`output/**/*.def`（递归）
  - 匹配 `data/pnr_innovus.place/a_dir/` 及其子目录的所有 .def：`a_dir/**/*.def`（递归）

- **特殊标记**：
  - `@目录名`：表示复制整个目录及其内容
  - 默认行为：文件扁平化到目标目录（不保持源目录结构）
  - 如需保持目录结构，使用 `keep_structure` 选项（见下方）

- **可选配置**（在 `release` 下单独配置）：
  ```yaml
  release:
    file_mappings:
      DEF: "a_dir/*.def"
      timing: "timing/*.csv"
    
    # 可选：目录结构保持规则
    keep_structure:
      - "timing"    # timing 目录保持结构
      - "LIB"       # LIB 目录保持结构
  ```

**路径匹配逻辑：**
1. **精确文件**：`a_dir/xx.def` → 直接复制
2. **通配符**：`a_dir/*.def` → 匹配 `a_dir/` 下的所有 .def 文件
3. **递归**：`**/*.def` → 在整个 `data/{flow}.{step}/` 下递归搜索
4. **目录**：`@libs` → 复制整个 `libs/` 目录
5. **根目录**：`xxx.def` → 匹配根目录下的文件

**Tcl 中的访问方式：**
```tcl
# 访问 DEF 目录的源文件路径列表
set release(file_mappings,DEF)  ;# 返回 "a_dir/*.def xxx.def abc.def"

# 如果是列表格式，在 Tcl 中会自动转换为 list
set def_paths $release(file_mappings,DEF)
foreach path $def_paths {
    puts "DEF source path: $path"
}

# 遍历所有目标目录
foreach target_dir [array names release "file_mappings,*"] {
    set source_paths $release($target_dir)
    puts "Target: $target_dir, Sources: $source_paths"
}
```

**匹配优先级：**
1. step_rules 中的规则（如果存在）
2. file_mappings 中的通用规则
3. 如果都不匹配，文件不会被包含（除非使用 `--include-all`）

#### 方案 B：在项目级配置中定义

```yaml
# edp_center/config/{foundry}/{node}/{project}/main/config.yaml
release:
  default_include_dirs:
    - DEF
    - LEF
    - SDF
    - SPEF
    - VERILOG
  
  flow_specific:
    pnr_innovus:
      include_dirs:
        - DEF
        - LEF
        - SDF
        - SPEF
        - DB
        - LIB
    pv_calibre:
      include_dirs:
        - OAS
        - GDS
```

#### 方案 C：命令行参数覆盖

```bash
# 使用配置文件中的规则（默认）
edp -release --version v09001 --step pnr_innovus.postroute

# 覆盖：只包含指定的目录
edp -release --version v09001 --step pnr_innovus.postroute --include-dirs DEF,LEF,SDF

# 覆盖：排除指定的目录
edp -release --version v09001 --step pnr_innovus.postroute --exclude-dirs TMP,BACKUP

# 覆盖：包含所有目录
edp -release --version v09001 --step pnr_innovus.postroute --include-all
```

### 5.3 文件映射优先级

1. **命令行参数**（最高优先级）
   - `--include-patterns` - 指定文件模式
   - `--exclude-patterns` - 排除文件模式
   - `--include-all` - 包含所有文件（使用默认映射）

2. **Step 特定规则**（如果存在）
   - `release.step_rules.{step_name}.file_mappings`

3. **Flow 配置规则**（默认）
   - `release.file_mappings`

4. **框架默认规则**（如果 flow 配置中没有）
   - 使用内置的默认文件映射规则

### 5.4 文件选择和映射逻辑

```python
def select_and_map_files_for_release(data_dir, config, flow_name, step_name, cli_args):
    """
    选择需要 release 的文件并映射到目标目录
    
    逻辑：
    1. 从配置中读取文件映射规则（flow -> step -> project -> default）
    2. 应用命令行参数覆盖
    3. 解析源文件路径列表，匹配文件
    4. 返回文件映射列表：[(source_path, target_dir, keep_structure), ...]
    """
    # 1. 获取配置规则（优先使用 step 特定规则）
    # config['release']['step_rules'][step_name]['file_mappings'] 或
    # config['release']['file_mappings']
    # 格式：{'DEF': 'a_dir/*.def xxx.def', 'DB': 'output/*.db', ...}
    file_mappings_config = get_release_mappings(config, flow_name, step_name)
    keep_structure_dirs = config.get('release', {}).get('keep_structure', [])
    
    # 2. 应用命令行参数覆盖
    if cli_args.include_all:
        file_mappings_config = get_default_mappings()
    elif cli_args.include_patterns:
        file_mappings_config = build_mappings_from_patterns(cli_args.include_patterns)
    
    # 3. 解析并匹配文件
    file_mappings = []
    
    for target_dir, source_paths_str in file_mappings_config.items():
        # 解析源文件路径列表（支持字符串和列表格式）
        if isinstance(source_paths_str, str):
            source_paths = source_paths_str.split()
        else:
            source_paths = source_paths_str
        
        keep_structure = target_dir in keep_structure_dirs
        
        # 处理每个源路径
        for source_path in source_paths:
            if source_path.startswith('@'):
                # 目录类型：@libs -> 复制整个 libs 目录
                dir_name = source_path[1:]
                full_dir_path = os.path.join(data_dir, dir_name)
                if os.path.isdir(full_dir_path):
                    file_mappings.append((full_dir_path, target_dir, keep_structure, 'directory'))
            else:
                # 文件类型：匹配文件
                matched_files = match_files_by_pattern(data_dir, source_path)
                for file_path in matched_files:
                    file_mappings.append((file_path, target_dir, keep_structure, 'file'))
    
    return file_mappings

def match_files_by_pattern(data_dir, pattern):
    """
    根据模式匹配文件
    
    Args:
        data_dir: data/{flow}.{step}/ 的绝对路径
        pattern: 文件路径模式（如 "a_dir/*.def", "**/*.def", "xxx.def"）
    
    Returns:
        匹配的文件路径列表
    """
    import fnmatch
    import os
    
    matched_files = []
    
    if '**' in pattern:
        # 递归搜索
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, data_dir)
                if fnmatch.fnmatch(rel_path, pattern) or \
                   fnmatch.fnmatch(rel_path, pattern.replace('**', '*')):
                    matched_files.append(file_path)
    elif '*' in pattern or '?' in pattern:
        # 通配符匹配
        pattern_dir = os.path.dirname(pattern) if os.path.dirname(pattern) else '.'
        pattern_file = os.path.basename(pattern)
        
        search_dir = os.path.join(data_dir, pattern_dir) if pattern_dir != '.' else data_dir
        
        if os.path.isdir(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if fnmatch.fnmatch(file, pattern_file):
                        file_path = os.path.join(root, file)
                        matched_files.append(file_path)
    else:
        # 精确文件路径
        file_path = os.path.join(data_dir, pattern)
        if os.path.isfile(file_path):
            matched_files.append(file_path)
    
    return matched_files

def match_path_to_target(path, is_directory, mappings_dict, data_base_dir):
    """
    匹配路径（文件或目录）到目标目录
    
    Args:
        path: 文件或目录的绝对路径
        is_directory: 是否为目录
        mappings_dict: 映射规则字典
        data_base_dir: data/{flow}.{step}/ 的绝对路径
    
    Returns:
        (target_dir, keep_structure, mapping_type) 或 None
    """
    import fnmatch
    import os
    
    # 计算相对于 data_base_dir 的相对路径
    rel_path = os.path.relpath(path, data_base_dir)
    
    # 遍历所有映射规则
    for mapping_name, mapping_config in mappings_dict.items():
        source_path = mapping_config.get('source_path', '')
        pattern = mapping_config.get('pattern')
        target_dir = mapping_config.get('target_dir')
        mapping_type = mapping_config.get('type', 'file')
        keep_structure = mapping_config.get('keep_structure', False)
        
        if not source_path or not target_dir:
            continue
        
        # 检查类型是否匹配
        if mapping_type == 'directory' and not is_directory:
            continue
        if mapping_type == 'file' and is_directory:
            continue
        
        # 处理 source_path（支持通配符）
        if '**' in source_path or '*' in source_path or '?' in source_path:
            # 通配符路径：使用 fnmatch 匹配
            if fnmatch.fnmatch(rel_path, source_path) or \
               fnmatch.fnmatch(rel_path, f"{source_path}/**"):
                return (target_dir, keep_structure, mapping_type)
        else:
            # 精确路径或目录路径
            if mapping_type == 'directory':
                # 目录：精确匹配或子目录
                if rel_path == source_path or rel_path.startswith(source_path + os.sep):
                    return (target_dir, keep_structure, mapping_type)
            else:
                # 文件：精确匹配或通配符匹配
                if rel_path == source_path:
                    return (target_dir, keep_structure, mapping_type)
                # 如果 source_path 是目录，检查文件是否在该目录下
                if source_path.endswith(os.sep) or os.path.isdir(os.path.join(data_base_dir, source_path)):
                    if rel_path.startswith(source_path + os.sep):
                        # 检查 pattern（如果提供）
                        if pattern:
                            file_name = os.path.basename(rel_path)
                            if fnmatch.fnmatch(file_name, pattern):
                                return (target_dir, keep_structure, mapping_type)
                        else:
                            return (target_dir, keep_structure, mapping_type)
    
    return None
```

### 5.5 实际示例

#### 示例 1：文件在子目录中

假设 `data/pnr_innovus.postroute/` 目录下有：
```
data/pnr_innovus.postroute/
├── a_dir/
│   └── design.def          # 文件在子目录中
├── output/
│   ├── design.db
│   └── design.sdf
├── results/
│   └── design.spef
└── timing/
    └── postroute.csv
```

配置：
```yaml
release:
  file_mappings:
    DEF: "a_dir/*.def"           # 匹配 a_dir/ 下的所有 .def 文件
    DB: "output/*.db"
    SDF: "output/*.sdf"
    SPEF: "results/*.spef"
    timing: "timing/*.csv"
  
  keep_structure:
    - "timing"                   # timing 目录保持结构
```

结果：
```
RELEASE/block1/user1/v09001/data/
├── def/
│   └── design.def          # 从 a_dir/design.def 复制
├── db/
│   └── design.db          # 从 output/design.db 复制
├── sdf/
│   └── design.sdf         # 从 output/design.sdf 复制
├── spef/
│   └── design.spef        # 从 results/design.spef 复制
└── timing/
    └── postroute.csv      # 从 timing/postroute.csv 复制（保持结构）
```

#### 示例 2：复制整个目录

假设 `data/pnr_innovus.postroute/` 目录下有：
```
data/pnr_innovus.postroute/
├── libs/
│   ├── std.lib
│   ├── io.lib
│   └── memory.lib
└── config/
    ├── design.mmc.tcl
    └── design.sdc
```

配置：
```yaml
release:
  file_mappings:
    lib: "@libs"                  # @ 前缀表示复制整个目录
    config: "@config"
  
  keep_structure:
    - "lib"                      # lib 目录保持结构
    - "config"                    # config 目录保持结构
```

结果：
```
RELEASE/block1/user1/v09001/data/
├── lib/
│   └── libs/              # 保持目录结构
│       ├── std.lib
│       ├── io.lib
│       └── memory.lib
└── config/
    └── config/             # 保持目录结构
        ├── design.mmc.tcl
        └── design.sdc
```

#### 示例 3：多个源文件路径

配置：
```yaml
release:
  file_mappings:
    # 多个源路径，空格分隔
    def: "a_dir/*.def xxx.def abc.def a_dir/xx.def"
    
    # 或者使用列表格式
    # def:
    #   - "a_dir/*.def"
    #   - "xxx.def"
    #   - "abc.def"
    #   - "a_dir/xx.def"
```

结果：所有匹配的文件都会复制到 `RELEASE/.../data/def/` 目录下

### 5.6 默认规则（如果没有配置）

如果配置文件中没有定义 release 规则，使用默认的文件映射：

```yaml
# 默认文件映射（框架内置）
default_file_mappings:
  def: "**/*.def"
  lef: "**/*.lef"
  sdf: "**/*.sdf"
  spef: "**/*.spef"
  db: "**/*.db"
  lib: "**/*.lib"
  verilog: "**/*.v **/*.vg"
  oas: "**/*.oas"
  gds: "**/*.gds"
  config: "**/*.tcl **/*.sdc"
  timing: "timing/*.csv"

# 默认保持结构的目录
default_keep_structure:
  - "timing"
```

### 5.7 完整配置示例

```yaml
# edp_center/config/SAMSUNG/S8/dongting/pnr_innovus/config.yaml
release:
  # 通用文件映射规则
  file_mappings:
    def: "a_dir/*.def *.def"
    db: "output/*.db"
    config: "**/*.mmc.tcl config/*.sdc"
    timing: "timing/*.csv"
    lib: "@libs"
  
  # 保持目录结构的目录列表
  keep_structure:
    - "timing"
    - "lib"
  
  # Step 特定规则（可选，会覆盖上面的通用规则）
  step_rules:
    postroute:
      file_mappings:
        def: "*.def a_dir/*.def"
        sdf: "results/*.sdf"
        spef: "results/*.spef"
        timing: "timing/postroute.csv"
    
    place:
      file_mappings:
        def: "*.def"
        timing: "timing/place.csv"
```

**在 Tcl 中的访问方式：**
```tcl
# 访问 def 目录的源文件路径列表
set release(file_mappings,def)      ;# "a_dir/*.def *.def"

# 访问 step 特定规则
set release(step_rules,postroute,file_mappings,sdf)  ;# "results/*.sdf"

# 遍历所有目标目录
foreach target_dir [array names release "file_mappings,*"] {
    set source_paths $release($target_dir)
    puts "Target: $target_dir, Sources: $source_paths"
}

# 访问保持结构的目录列表
set release(keep_structure)  ;# 如果是列表，会自动转换为 Tcl list
```

## 6. 与框架的集成

### 6.1 创建 RELEASE 的命令

建议添加一个命令来创建 RELEASE：

```bash
# 从当前分支创建 RELEASE（使用配置文件中的规则）
edp -release --version v09001 --step pnr_innovus.postroute

# 强制使用时间戳（即使版本号不存在也添加时间戳）
edp -release --version v09001 --step pnr_innovus.postroute --timestamp

# 如果版本号已存在，报错而不是自动添加时间戳
edp -release --version v09001 --step pnr_innovus.postroute --strict

# 指定目标 block（如果不在 block 目录下）
edp -release --version v09001 --step pnr_innovus.postroute --block block1

# 覆盖：包含所有数据（忽略配置）
edp -release --version v09001 --step pnr_innovus.postroute --include-all

# 覆盖：只包含指定的文件模式
edp -release --version v09001 --step pnr_innovus.postroute --include-patterns "*.def,*.sdf"

# 覆盖：排除指定的文件模式
edp -release --version v09001 --step pnr_innovus.postroute --exclude-patterns "*.tmp,*.bak"
```

### 6.2 RELEASE 工作流

1. **用户在工作分支中运行流程**
   ```
   WORK_PATH/dongting/P85/block1/user1/main/
   ```

2. **运行完成后，创建 RELEASE**
   ```bash
   cd WORK_PATH/dongting/P85/block1/user1/main
   edp -release --version v09001 --step pnr_innovus.postroute
   ```

3. **框架自动执行：**
   - 检查版本号是否已存在
   - 如果存在，自动添加时间戳后缀（或报错，取决于选项）
   - 从当前分支的 `runs/` 或 `data/` 目录复制数据
   - 创建 RELEASE 目录结构：`RELEASE/block1/user1/v09001/`（或带时间戳）
   - 复制文件到 `data/` 目录下的各个子目录
   - 复制 `lib_settings.tcl` 到根目录
   - 创建 `release_note.txt`（如果提供）
   - 创建 `full.tcl`（如果提供）
   - **设置目录为只读**（chmod 555）
   - **创建 .readonly 标记文件**

## 10. 统一命名建议

### 10.1 目录命名
- **数据目录**：统一使用 `data/`（所有数据文件都在这里）
- **时序数据**：使用 `data/timing/`（在 data 目录下）
- **报告文件**：使用 `data/reports/`（在 data 目录下，可选）

### 10.2 文件命名
- **库设置**：`lib_settings.tcl`（必须，在根目录）
- **发布说明**：`release_note.txt`（可选，在根目录）
- **完整脚本**：`full.tcl`（可选，在根目录）
- **其他文件**：根据项目需要，放在根目录

## 11. 版本管理

### 6.1 版本号格式
- 建议使用：`v{数字}` 格式，如 `v09001`, `v09002`
- 或者：`v{主版本}.{次版本}` 格式，如 `v1.0`, `v1.1`

### 11.2 版本关联
- 版本关系可以通过 `release_note.txt` 或其他文档记录
- 支持版本树结构（通过目录结构体现）

## 12. 迁移建议

### 12.1 从现有结构迁移
1. 将 `dbs/` 或 `datadir/` 重命名为 `data/`
2. 将 `timing_csv/` 重命名为 `data/timing/`
3. 将 `reports/` 移动到 `data/reports/`（如果存在）
4. 将 `lib_settings.tcl` 移动到根目录（如果原来在 metadata/ 下）
5. 移除 `metadata/` 和 `status.yaml`（如果存在）

### 8.2 向后兼容
- 框架可以同时支持新旧两种结构
- 优先使用新结构，如果不存在则回退到旧结构

## 14. 示例

### 13.1 完整的 RELEASE 目录示例

```
RELEASE/block1/user1/v09001/
├── metadata/
│   ├── release_info.yaml
│   ├── source_info.yaml
│   ├── bom.tcl
│   └── lib_settings.tcl
├── data/
│   ├── CONFIG/
│   ├── DB/
│   ├── DEF/
│   ├── LEF/
│   └── ...
├── reports/
│   └── summary.rpt
├── timing/
│   ├── place.csv
│   └── postroute.csv
├── status.yaml
└── release_note.txt
```

### 13.2 status.yaml 示例

```yaml
ready: true
note: "Production release - All checks passed"
created_date: "2024-01-15"
created_by: "user1"
design_name: "sm3_top"
version: "v09001"
target_frequency: 800
target_area: 0.5
power_budget: 1.2
```

### 13.3 metadata/source_info.yaml 示例

```yaml
source:
  work_path: "/home/user/WORK_PATH"
  project: "dongting"
  version: "P85"
  block: "block1"
  user: "user1"
  branch: "main"
  branch_step: "pnr_innovus.postroute"
  created_at: "2024-01-15T10:30:00"
  
related:
  parent: null
  based_on: "v09000"
```

## 15. 总结

推荐的 RELEASE 框架特点：
1. **统一结构**：使用 `data/` 而不是 `dbs/` 或 `datadir/`
2. **元数据集中**：使用 `metadata/` 目录管理所有元数据
3. **来源追踪**：通过 `source_info.yaml` 追踪 RELEASE 的来源
4. **状态管理**：通过 `status.yaml` 管理版本状态
5. **与框架集成**：通过命令创建 RELEASE，自动填充元数据
6. **版本唯一性**：按 `{block}/{user}/{version}` 组织，支持时间戳避免冲突
7. **只读保护**：RELEASE 创建后自动设置为只读，防止篡改
8. **多版本支持**：同一用户一天内可以发布多个版本（通过时间戳区分）

### 15.1 关键设计决策

| 问题 | 解决方案 |
|------|---------|
| 同一用户一天内多次发布 | 版本号冲突时自动添加时间戳后缀 |
| 防止用户覆盖版本 | 目录创建后设置为只读，拒绝覆盖已存在的版本 |
| release_version 层级 | `RELEASE/{block}/{user}/{version}/` - 按用户分组避免冲突 |

