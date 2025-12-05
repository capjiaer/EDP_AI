# RELEASE 恢复功能 - 复现需求分析

## 问题：复现一个 run 需要哪些内容？

### 核心问题

如果原始的 run 已经被删除或修改，如何确保从 RELEASE 能够完全复现之前的状态？

## 需要确认的内容

### 1. 数据文件需求

#### 1.1 必需文件（不同 flow/step 可能不同）

**pnr_innovus.postroute**：
- [ ] `*.def` - Design Exchange Format（必需？）
- [ ] `*.db` - 设计数据库（必需？）
- [ ] `*.sdf` - 时序信息（必需？）
- [ ] `*.spef` - 寄生参数（必需？）
- [ ] `*.v` / `*.vg` - Verilog 网表（必需？）
- [ ] `*.mmc.tcl` - 多模式约束（必需？）
- [ ] `*.sdc` - 时序约束（必需？）

**问题**：
- 哪些文件是工具恢复设计状态所必需的？
- 哪些文件是后续步骤所必需的？
- 哪些文件是可选的（用于分析、报告等）？

#### 1.2 文件位置映射

**当前 RELEASE 结构**：
```
RELEASE/block1/user1/v09001/data/
├── def/design.def
├── db/design.db
├── sdf/postroute.sdf
└── ...
```

**恢复目标位置**：
```
WORK_PATH/.../block1/user1/branch/data/pnr_innovus.postroute/
├── output/design.def  (?) 
├── output/design.db   (?)
├── results/postroute.sdf (?)
└── ...
```

**问题**：
- 如何知道文件应该恢复到哪个位置？
- 是否需要保存原始文件路径信息？
- 还是根据配置反向映射？

### 2. 配置信息需求

#### 2.1 库设置
- [ ] `lib_settings.tcl` - 是否足够？
- [ ] 是否包含所有必需的库路径？

#### 2.2 设计配置
- [ ] `full.tcl` 中的配置变量：
  - 设计名称
  - 工作路径
  - 工具版本
  - 其他配置参数
- [ ] 是否需要恢复 `user_config.yaml`？

#### 2.3 Flow 配置
- [ ] 是否需要恢复 flow 的配置文件？
- [ ] 配置是否会影响数据文件的路径？

### 3. 元数据需求

#### 3.1 原始路径信息
- [ ] 是否需要保存原始文件路径？
  - 例如：`data/pnr_innovus.postroute/output/design.def`
- [ ] 如何保存？（元数据文件？）

#### 3.2 时间戳和版本信息
- [ ] 是否需要保存原始 run 的时间戳？
- [ ] 是否需要保存工具版本信息？

#### 3.3 依赖关系
- [ ] 是否需要记录前置步骤的依赖？
- [ ] 如何验证依赖的完整性？

### 4. 工具恢复状态的需求

#### 4.1 Innovus
- 恢复设计状态需要：
  - [ ] `*.db` 文件（设计数据库）
  - [ ] `lib_settings.tcl`（库设置）
  - [ ] 其他？

#### 4.2 Calibre
- 恢复状态需要：
  - [ ] GDS 文件？
  - [ ] 规则文件？
  - [ ] 其他？

#### 4.3 PrimeTime
- 恢复状态需要：
  - [ ] 网表文件
  - [ ] 库文件
  - [ ] 约束文件
  - [ ] 其他？

## 调研建议

### 1. 检查现有 RELEASE

```bash
# 检查现有 RELEASE 目录结构
ls -R RELEASE/block1/user1/v09001/

# 检查包含的文件类型
find RELEASE/block1/user1/v09001/data -type f | head -20
```

### 2. 测试工具恢复

- 尝试只使用 RELEASE 中的数据恢复 Innovus 设计状态
- 记录哪些文件是必需的，哪些是可选的

### 3. 分析不同 flow 的需求

- 列出每个 flow 的必需文件
- 确定通用的复现规则

## 可能的解决方案

### 方案 1：保存元数据文件

在 RELEASE 中保存 `metadata/restore_info.yaml`：

```yaml
source_info:
  branch: "main"
  step: "pnr_innovus.postroute"
  timestamp: "2024-01-15 10:30:45"
  
file_mappings:
  # 记录原始路径 -> RELEASE 路径的映射
  "data/pnr_innovus.postroute/output/design.def": "data/def/design.def"
  "data/pnr_innovus.postroute/output/design.db": "data/db/design.db"
  "data/pnr_innovus.postroute/results/postroute.sdf": "data/sdf/postroute.sdf"

config_snapshot:
  lib_settings: "lib_settings.tcl"
  full_tcl: "full.tcl"
  user_config: null  # 如果存在，保存路径

dependencies:
  - step: "pnr_innovus.place"
    required: true
  - step: "pnr_innovus.cts"
    required: true
```

### 方案 2：从 full.tcl 提取信息

- `full.tcl` 包含所有配置变量
- 可以从中提取：
  - 工作路径
  - 设计名称
  - 工具版本
  - 其他配置

### 方案 3：配置驱动的反向映射

- 使用 flow 的 `release` 配置反向映射
- 根据配置规则将文件恢复到原始位置

## 待确认清单

- [ ] 确认每个 flow/step 的必需文件列表
- [ ] 确认文件路径映射方案
- [ ] 确认配置信息保存方案
- [ ] 确认元数据保存方案
- [ ] 确认依赖关系验证方案
- [ ] 测试工具恢复功能

## 下一步

1. 调研现有 RELEASE 结构
2. 测试工具恢复需求
3. 确定最小复现集合
4. 设计元数据方案
5. 实现恢复功能

