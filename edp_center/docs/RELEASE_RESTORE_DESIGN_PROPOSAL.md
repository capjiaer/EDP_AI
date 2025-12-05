# RELEASE 恢复功能设计提案

## 📋 执行摘要

本文档提出 RELEASE 恢复功能的实现方案，基于现有的 RELEASE 创建机制，采用**元数据驱动的反向映射**方案。

**核心思路**：在创建 RELEASE 时保存文件路径映射元数据，恢复时根据元数据反向映射。

---

## 1. 设计原则

### 1.1 核心原则

1. **最小侵入**：尽量复用现有的 RELEASE 创建机制
2. **元数据驱动**：保存必要的元数据，支持反向映射
3. **配置优先**：优先使用配置文件中的映射规则
4. **向后兼容**：支持没有元数据的旧 RELEASE（使用默认规则）

### 1.2 关键决策

| 问题 | 决策 | 理由 |
|------|------|------|
| 文件映射反向 | 保存元数据 + 配置反向映射 | 既保证准确性，又支持灵活性 |
| 元数据格式 | YAML 文件（`restore_metadata.yaml`） | 易读易维护 |
| 配置恢复 | 只恢复 `lib_settings.tcl`，不恢复 `full.tcl` | `full.tcl` 包含运行时路径，不适合恢复 |
| 依赖关系 | 不自动恢复依赖，用户手动指定 | 简化实现，避免复杂依赖分析 |

---

## 2. 元数据设计

### 2.1 元数据文件结构

在 RELEASE 中保存 `restore_metadata.yaml`：

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
  created_at: "2024-01-15T10:30:00"
  
# 文件映射信息（用于反向映射）
file_mappings:
  # 每个目标目录的映射规则
  def:
    # 源文件路径（相对于 data/{flow}.{step}/）
    source_patterns: ["a_dir/*.def", "*.def"]
    # 目标目录（RELEASE 中的目录）
    target_dir: "def"
    # 是否保持结构
    keep_structure: false
    # 实际复制的文件列表（用于验证）
    files:
      - source: "a_dir/design.def"
        target: "def/design.def"
        size: 1234567
        md5: "abc123..."  # 可选，用于完整性验证
  
  db:
    source_patterns: ["output/*.db"]
    target_dir: "db"
    keep_structure: false
    files:
      - source: "output/design.db"
        target: "db/design.db"
        size: 2345678

# 配置信息
config:
  # lib_settings.tcl 的位置（相对于 RELEASE 根目录）
  lib_settings_path: "data/pnr_innovus.postroute/lib_settings.tcl"
  # full.tcl 的位置（可选）
  full_tcl_path: "data/pnr_innovus.postroute/full.tcl"
  
# 依赖关系（可选，用于提示）
dependencies:
  - flow: "pnr_innovus"
    step: "place"
    required: false  # 是否必需
  - flow: "pnr_innovus"
    step: "cts"
    required: false
```

### 2.2 元数据生成时机

**在创建 RELEASE 时自动生成**：

```python
# release_step_processor.py
def release_single_step(...):
    # ... 现有的文件复制逻辑 ...
    
    # 生成元数据
    metadata = {
        'metadata_version': '1.0',
        'source': {
            'work_path': str(work_path),
            'project': project,
            'version': version,
            'block': block,
            'user': user,
            'branch': branch,
            'flow': flow_name,
            'step': step_name,
            'created_at': datetime.now().isoformat()
        },
        'file_mappings': build_file_mappings_metadata(file_mappings, data_dir, step_target_dir),
        'config': {
            'lib_settings_path': str(lib_settings_path.relative_to(release_dir)),
            'full_tcl_path': str(full_tcl_path.relative_to(release_dir)) if full_tcl_path else None
        }
    }
    
    # 保存元数据
    metadata_path = step_target_dir / 'restore_metadata.yaml'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
```

---

## 3. 恢复功能设计

### 3.1 命令格式

```bash
# 基本用法：从 RELEASE 恢复数据到当前分支
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute

# 指定目标分支
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --branch target_branch

# 覆盖模式（覆盖已存在的文件）
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --overwrite

# 选择性恢复（只恢复指定的文件类型）
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute --include-types def db

# 创建新分支时从 RELEASE 恢复
edp -b new_branch --from-release block1/user1/v09001:pnr_innovus.postroute
```

### 3.2 恢复流程

```
1. 验证 RELEASE 存在性和完整性
   ├── 检查 RELEASE 目录是否存在
   ├── 检查 restore_metadata.yaml 是否存在（如果有，使用元数据）
   └── 验证文件完整性（可选：MD5 校验）

2. 确定恢复目标位置
   ├── 目标分支目录：WORK_PATH/{project}/{version}/{block}/{user}/{branch}/
   └── 目标数据目录：data/{flow}.{step}/

3. 反向映射文件
   ├── 如果有元数据：使用元数据中的 source_patterns 反向映射
   ├── 如果没有元数据：使用配置文件中的 file_mappings 反向映射
   └── 如果都没有：使用默认映射规则

4. 复制文件
   ├── 根据映射规则复制文件到目标位置
   ├── 处理目录结构（keep_structure）
   └── 处理冲突（--overwrite 或跳过）

5. 恢复配置
   ├── 复制 lib_settings.tcl 到 runs/{flow}.{step}/
   └── 可选：从 full.tcl 提取配置信息（不直接复制 full.tcl）

6. 验证和报告
   ├── 验证必需文件是否存在
   ├── 验证文件大小是否合理
   └── 生成恢复报告
```

### 3.3 反向映射逻辑

#### 方案 A：使用元数据中的 source_patterns（推荐）

```python
def restore_files_from_release(release_dir: Path, target_data_dir: Path, 
                               metadata: Dict, config: Dict) -> List[Tuple]:
    """
    从 RELEASE 恢复文件到工作分支
    
    逻辑：
    1. 读取元数据中的 file_mappings
    2. 对于每个 target_dir（如 def, db），找到对应的 source_patterns
    3. 将 RELEASE 中的文件反向映射到工作分支的原始位置
    """
    file_restore_mappings = []
    
    for target_dir, mapping_info in metadata['file_mappings'].items():
        source_patterns = mapping_info['source_patterns']
        keep_structure = mapping_info.get('keep_structure', False)
        
        # RELEASE 中的源目录
        release_source_dir = release_dir / 'data' / f"{metadata['source']['flow']}.{metadata['source']['step']}" / target_dir
        
        # 对于每个 source_pattern，反向映射文件
        for pattern in source_patterns:
            # 解析 pattern，确定目标位置
            target_location = reverse_map_pattern(pattern, target_data_dir, keep_structure)
            
            # 找到 RELEASE 中匹配的文件
            release_files = list(release_source_dir.glob('*'))
            for release_file in release_files:
                # 确定目标文件路径
                if keep_structure:
                    # 保持结构：需要从元数据中的 files 列表获取原始路径
                    target_file = find_original_path(release_file, mapping_info['files'])
                else:
                    # 扁平化：直接使用文件名
                    target_file = target_location / release_file.name
                
                file_restore_mappings.append((release_file, target_file))
    
    return file_restore_mappings
```

#### 方案 B：使用配置文件反向映射（向后兼容）

如果没有元数据，使用配置文件中的 `file_mappings` 反向映射：

```python
def restore_files_using_config(release_dir: Path, target_data_dir: Path,
                               config: Dict, flow_name: str, step_name: str) -> List[Tuple]:
    """
    使用配置文件反向映射（向后兼容）
    
    逻辑：
    1. 读取配置中的 file_mappings
    2. 对于每个 target_dir，找到对应的 source_patterns
    3. 将 RELEASE 中的文件反向映射到工作分支
    """
    # 获取配置中的映射规则（与 release 创建时相同）
    file_mappings_config = get_file_mappings(config, flow_name, step_name, target_data_dir, args)
    
    # 反向映射：target_dir -> source_patterns
    file_restore_mappings = []
    
    for target_dir, source_patterns_str in file_mappings_config.items():
        # RELEASE 中的源目录
        release_source_dir = release_dir / 'data' / f"{flow_name}.{step_name}" / target_dir
        
        # 解析 source_patterns
        source_patterns = source_patterns_str.split() if isinstance(source_patterns_str, str) else source_patterns_str
        
        # 对于每个 pattern，确定目标位置
        for pattern in source_patterns:
            target_location = reverse_map_pattern(pattern, target_data_dir, keep_structure)
            
            # 复制文件
            for release_file in release_source_dir.glob('*'):
                target_file = target_location / release_file.name
                file_restore_mappings.append((release_file, target_file))
    
    return file_restore_mappings
```

---

## 4. 实现建议

### 4.1 文件结构

```
edp_center/main/cli/commands/release/
├── __init__.py
├── release_handler.py          # RELEASE 创建（已有）
├── release_restore_handler.py  # RELEASE 恢复（新增）
├── release_file_mapper.py      # 文件映射（已有，可复用）
├── release_file_operations.py  # 文件操作（已有，可复用）
├── release_metadata.py         # 元数据管理（新增）
└── release_version_manager.py  # 版本管理（已有）
```

### 4.2 核心模块

#### `release_metadata.py`（新增）

```python
def build_file_mappings_metadata(file_mappings: List[Tuple], 
                                 data_dir: Path, 
                                 step_target_dir: Path) -> Dict:
    """构建文件映射元数据"""
    metadata = {}
    
    for source_path, target_dir, keep_structure, file_type in file_mappings:
        if target_dir not in metadata:
            metadata[target_dir] = {
                'source_patterns': [],
                'target_dir': target_dir,
                'keep_structure': keep_structure,
                'files': []
            }
        
        # 计算相对路径和 pattern
        rel_path = source_path.relative_to(data_dir)
        pattern = build_pattern_from_path(rel_path, data_dir)
        
        if pattern not in metadata[target_dir]['source_patterns']:
            metadata[target_dir]['source_patterns'].append(pattern)
        
        # 记录实际文件信息
        target_path = step_target_dir / target_dir / source_path.name
        metadata[target_dir]['files'].append({
            'source': str(rel_path),
            'target': str(target_path.relative_to(step_target_dir)),
            'size': source_path.stat().st_size
        })
    
    return metadata

def load_restore_metadata(release_dir: Path, flow_name: str, step_name: str) -> Optional[Dict]:
    """加载恢复元数据"""
    metadata_path = release_dir / 'data' / f"{flow_name}.{step_name}" / 'restore_metadata.yaml'
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return None
```

#### `release_restore_handler.py`（新增）

```python
def handle_release_restore_cmd(manager, args) -> int:
    """处理 -release-restore 命令"""
    # 1. 解析参数
    # 2. 验证 RELEASE 存在性
    # 3. 加载元数据（如果有）
    # 4. 确定恢复目标位置
    # 5. 反向映射文件
    # 6. 复制文件
    # 7. 恢复配置
    # 8. 验证和报告
    pass
```

---

## 5. 关键问题处理

### 5.1 文件映射反向

**问题**：RELEASE 中的 `data/def/design.def` 应该恢复到工作分支的哪个位置？

**解决方案**：
1. **优先使用元数据**：元数据中保存了 `source: "a_dir/design.def"`，直接恢复到 `data/{flow}.{step}/a_dir/design.def`
2. **使用配置反向映射**：如果没有元数据，使用配置中的 `file_mappings` 反向映射
3. **默认规则**：如果都没有，恢复到 `data/{flow}.{step}/output/`（默认位置）

### 5.2 目录结构保持

**问题**：如果 `keep_structure: true`，如何恢复目录结构？

**解决方案**：
- 元数据中保存了 `files` 列表，包含每个文件的 `source` 路径
- 恢复时根据 `source` 路径重建目录结构

### 5.3 配置恢复

**问题**：需要恢复哪些配置？

**解决方案**：
- **必须恢复**：`lib_settings.tcl`（库设置）
- **可选恢复**：从 `full.tcl` 提取关键配置变量（不直接复制 `full.tcl`，因为包含运行时路径）
- **不恢复**：`user_config.yaml`（用户配置应该由用户自己管理）

### 5.4 向后兼容

**问题**：如何处理没有元数据的旧 RELEASE？

**解决方案**：
1. 检查 `restore_metadata.yaml` 是否存在
2. 如果不存在，使用配置文件中的 `file_mappings` 反向映射
3. 如果配置也没有，使用默认映射规则

---

## 6. 实现优先级

### 🔴 阶段 1：核心功能（MVP）

1. **元数据生成**（在 RELEASE 创建时）
   - 保存 `restore_metadata.yaml`
   - 包含基本的文件映射信息

2. **基本恢复功能**
   - 从 RELEASE 恢复文件到工作分支
   - 使用元数据反向映射
   - 恢复 `lib_settings.tcl`

3. **冲突处理**
   - `--overwrite` 选项
   - 默认跳过已存在的文件

### 🟡 阶段 2：增强功能

4. **向后兼容**
   - 支持没有元数据的旧 RELEASE
   - 使用配置反向映射

5. **选择性恢复**
   - `--include-types` 选项
   - `--exclude-types` 选项

6. **验证和报告**
   - 文件完整性验证
   - 恢复报告生成

### 🟢 阶段 3：高级功能

7. **依赖关系提示**
   - 检查依赖步骤是否已恢复
   - 提供恢复建议

8. **批量恢复**
   - 恢复多个步骤
   - 恢复整个 flow

---

## 7. 使用示例

### 7.1 基本恢复

```bash
# 从 RELEASE 恢复数据到当前分支
cd WORK_PATH/dongting/P85/block1/user1/main
edp -release-restore --from-release block1/user1/v09001 --step pnr_innovus.postroute

# 输出：
# [INFO] 正在从 RELEASE 恢复数据...
# [INFO] RELEASE 版本: block1/user1/v09001
# [INFO] 恢复步骤: pnr_innovus.postroute
# [INFO] 使用元数据反向映射文件...
# [INFO] 已恢复文件: data/pnr_innovus.postroute/a_dir/design.def
# [INFO] 已恢复文件: data/pnr_innovus.postroute/output/design.db
# [INFO] 已恢复配置: runs/pnr_innovus.postroute/lib_settings.tcl
# [INFO] 恢复完成！
```

### 7.2 创建新分支时恢复

```bash
# 创建新分支时从 RELEASE 恢复
cd WORK_PATH/dongting/P85/block1/user1
edp -b eco_branch --from-release block1/user1/v09001:pnr_innovus.postroute

# 新分支已经包含了 RELEASE 的数据
cd eco_branch
edp -run pnr_innovus.eco
```

---

## 8. 总结

### 8.1 推荐方案

**采用"元数据驱动的反向映射"方案**：

1. **创建 RELEASE 时**：自动生成 `restore_metadata.yaml`，保存文件映射信息
2. **恢复时**：
   - 优先使用元数据反向映射（最准确）
   - 如果没有元数据，使用配置反向映射（向后兼容）
   - 如果都没有，使用默认规则（兜底）

### 8.2 优势

✅ **准确性高**：元数据保存了原始路径信息，恢复准确  
✅ **向后兼容**：支持没有元数据的旧 RELEASE  
✅ **灵活性好**：支持选择性恢复、覆盖等选项  
✅ **实现简单**：复用现有的文件映射逻辑

### 8.3 注意事项

⚠️ **元数据文件大小**：如果文件很多，元数据文件可能较大（可以考虑只保存关键信息）  
⚠️ **配置变更**：如果配置中的 `file_mappings` 变更，可能影响向后兼容的恢复  
⚠️ **依赖关系**：不自动处理依赖关系，用户需要手动恢复依赖步骤

---

## 9. 下一步行动

1. [ ] 实现元数据生成（在 `release_step_processor.py` 中）
2. [ ] 实现基本恢复功能（`release_restore_handler.py`）
3. [ ] 实现反向映射逻辑（`release_metadata.py`）
4. [ ] 添加命令行参数（`arg_parser.py`）
5. [ ] 编写测试用例
6. [ ] 更新文档

---

**文档版本**: 1.0  
**最后更新**: 2025-01-XX

