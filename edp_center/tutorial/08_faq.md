# 常见问题

[← 返回目录](../TUTORIAL.md)

本文档回答 EDP_AI 框架的常见问题，帮助你快速解决遇到的问题。

## Q1: 如何在 EDP Center 中创建新项目的文件夹结构？

当你需要引入一个新的项目时，可以使用 `-create_project` 命令：

```bash
# 创建新项目的文件夹结构
edp_init -create-project PROJECT_NAME FOUNDRY NODE

# 示例
edp_init -create-project new_prj TSMC n8
```

**工作原理**：
1. 如果目标 node 下没有 `common` 目录，会先从模板 `foundry_name/node_name/common` 复制
2. 然后从模板 `foundry_name/node_name/prj_example` 复制到新项目目录
3. 已存在的文件不会被覆盖，只会补充缺失的目录和文件

**注意事项**：
- 模板目录 `foundry_name/node_name/common` 和 `foundry_name/node_name/prj_example` 必须存在
- 如果项目目录已存在，已存在的文件不会被覆盖，可以安全地运行此命令补充缺失的内容

更多详细信息请参考 [基本使用 - 创建项目结构](03_basic_usage.md#5-创建项目结构-edp--create_project)。

## Q2: 如何使用 GUI 图形界面初始化项目？

如果你不熟悉配置文件格式，可以使用图形界面进行初始化：

```bash
# 启动 GUI 初始化界面
edp_init -init --gui
```

GUI 界面会自动扫描并显示所有可用的项目，你只需要：
1. 选择 EDP Center 路径和 Work Path 路径
2. 从下拉列表选择项目（格式：`项目名 (foundry/node)`）
3. 输入项目版本
4. 在表格中配置 Block 和 User
5. 点击"开始初始化"

更多详细信息请参考 [快速开始 - 创建第一个项目](02_getting_started.md#方式-a-使用-gui-图形界面推荐新手)。

## Q3: 如何查看所有可用的流程和步骤？

```bash
# 查看所有流程
edp_info -info
# 或使用短别名
edp_info -i

# 查看指定流程的步骤
edp_info -info pv_calibre
# 或使用短别名
edp_info -i pv_calibre
```

## Q4: 如何修改配置？

假设你的分支目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1/main`

编辑 `user_config.yaml` 或 `user_config.tcl` 文件（在分支目录下），然后重新运行：

```bash
# 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 编辑配置文件
vim user_config.yaml  # 或 user_config.tcl

# 重新运行
edp -run pv_calibre.ipmerge
```

**配置文件位置**：
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/user_config.yaml`
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/user_config.tcl`

## Q5: 如何保护变量不被修改？

在配置中使用 `protect` 字段（布尔标志）：

```yaml
pv_calibre:
  ipmerge:
    cpu_num:
      value: 16
      protect: 1  # 布尔标志：1 表示启用保护，保护值为当前的 value（16）
```

**说明**：
- `protect: 1` 表示启用保护，保护值为当前的 `value`（16）
- `protect: 0` 表示不保护
- `protect` 只能是布尔值（1/0），不能直接指定保护值

更多详细信息请参考 [配置文件高级用法 - 变量保护](06_configuration.md#变量保护)。

## Q6: 遇到错误时如何理解错误信息？

EDP 框架提供了详细的错误信息，包含：

1. **错误消息**：简要描述问题
2. **[详细信息]**：包含错误发生的上下文（文件路径、行号、参数值等）
3. **[建议]**：提供具体的解决步骤和命令示例

### 错误消息格式

所有错误消息都遵循统一的格式：

```
错误消息简要描述

[详细信息]
  - key1: value1
  - key2: value2
  - ...

[建议]
具体的解决步骤和示例
```

### 示例 1：变量格式验证错误

```
在文件 /path/to/config.yaml 中发现简单变量（非数组格式），不符合要求。

[详细信息]
  - config_file: /path/to/config.yaml
  - invalid_variables: ['cpu_num', 'memory']
  - variable_count: 2
  - field_name: 变量格式
  - field_value: 2 个简单变量
  - expected: 数组格式（带命名空间）

[建议]
所有变量都必须是数组格式（带命名空间），请按以下方式修改：

YAML 格式示例：
  错误：
    cpu_num: 32
  正确：
    pnr_innovus:
      place:
        cpu_num: 32  # 生成 set pnr_innovus(place,cpu_num) 32

Tcl 格式示例：
  错误：
    set cpu_num 32
  正确：
    set pnr_innovus(place,cpu_num) 32
```

### 示例 2：YAML 文件解析错误

```
YAML 文件解析失败: while scanning for the next token

[详细信息]
  - line_number: 5
  - column_number: 10
  - error_type: YAMLError
  - config_file: /path/to/config.yaml

[建议]
请检查 YAML 文件格式是否正确：

错误位置：第 5 行
          第 10 列

常见问题：
1. 缩进错误：
   - YAML 使用空格缩进，不要使用 Tab
   - 确保缩进一致（通常使用 2 个空格）

2. 引号问题：
   - 确保所有引号（单引号 ' 或双引号 "）都已正确闭合
   - 如果字符串包含特殊字符，需要用引号括起来
```

### 示例 3：配置文件未找到错误

```
未找到任何配置文件，无法生成 full.tcl

[详细信息]
  - edp_center_path: /path/to/edp_center
  - foundry: SAMSUNG
  - node: S8
  - project: test_project
  - flow_name: pnr_innovus
  - step_name: place

[建议]
请检查配置文件路径是否正确，确保配置文件存在于正确的位置：

配置文件查找路径（按优先级顺序）：
1. user_config.yaml（当前目录或工作目录）
2. SAMSUNG/S8/test_project/pnr_innovus/place.yaml
3. SAMSUNG/S8/test_project/pnr_innovus/common.yaml
4. SAMSUNG/S8/test_project/common.yaml
5. SAMSUNG/S8/common/common.yaml
6. SAMSUNG/common/common.yaml

检查步骤：
1. 确认 edp_center 路径正确: /path/to/edp_center
2. 确认 foundry 和 node 正确: SAMSUNG/S8
3. 确认项目路径正确: test_project
4. 确认流程和步骤名称正确: pnr_innovus.place
```

### 示例 4：项目未找到错误

```
找不到项目: test_project

[详细信息]
  - project_name: test_project
  - available_projects: ['project1 (FOUNDRY1/NODE1)', 'project2 (FOUNDRY2/NODE2)']
  - config_path: /path/to/config

[建议]
可用项目: project1, project2
使用 'edp_init -create-project PROJECT_NAME FOUNDRY NODE' 创建新项目
```

**常见错误类型**：
- **变量格式错误**：检查变量是否使用数组格式（带命名空间）
- **配置文件解析错误**：检查 YAML/Tcl 文件格式、缩进、引号等
- **文件未找到**：检查文件路径、搜索路径是否正确
- **配置验证错误**：检查配置值是否在允许的约束列表中
- **项目未找到**：检查项目名称、foundry/node 是否正确，或使用 `edp_init -create-project` 创建
- **配置错误**：检查配置文件格式（YAML/Tcl）是否正确
- **工作流错误**：检查步骤配置、输入文件是否存在

**提示**：错误信息中的 💡 建议通常包含可以直接使用的命令，按照建议操作即可解决问题。

## Q7: 如何添加自定义代码？

假设你的分支目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1/main`

使用 hooks 机制：

```bash
# 1. 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 2. 编辑 hooks 文件（hooks 目录在 init 时已创建）
vim hooks/pv_calibre.ipmerge/step.pre
# 或使用完整路径：
# vim /home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pv_calibre.ipmerge/step.pre
```

**说明**：
- `hooks/` 目录在 `edp_init -init` 时已经创建（在 `main` 分支下）
- 第一次运行 `edp -run` 时会自动创建对应 flow 和 step 的子目录（如 `hooks/pv_calibre.ipmerge/`）
- 之后可以直接编辑 hooks 文件

**Hooks 文件位置**（统一使用 `flow_name.step_name` 格式）：
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pv_calibre.ipmerge/step.pre`
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pv_calibre.ipmerge/step.post`
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pnr_innovus.place/config_design.tcl.pre`（sub_step pre hook）
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pnr_innovus.place/config_design.tcl.post`（sub_step post hook）
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pnr_innovus.place/config_design.tcl.replace`（sub_step replace hook）

**注意**：已移除 `#import util` 机制，util hooks 不再使用。

## Q8: 如何从已有分支创建新分支？

假设你的用户目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1`

```bash
# 1. 进入用户目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1

# 2. 从已有分支创建新分支
edp -b new_branch --from-branch-step "main.pnr_innovus.init"
```

**说明**：
- `main.pnr_innovus.init` 表示从 `main` 分支的 `pnr_innovus.init` 步骤创建（使用点号分隔）
- 新分支会创建在：`/home/user/WORK_PATH/dongting/P85/block1/user1/new_branch/`

## Q9: 如何查看运行历史？

假设你的分支目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1/main`

查看 `.run_info` 文件：

```bash
# 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 查看运行历史
cat .run_info

# 或使用完整路径
cat /home/user/WORK_PATH/dongting/P85/block1/user1/main/.run_info
```

**文件位置**：
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/.run_info`

## Q10: 如何本地测试 LSF 命令？

假设你的分支目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1/main`

使用 `--dry-run` 模式：

```bash
# 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 只显示构建的命令，不实际执行
edp -run pv_calibre.ipmerge --dry-run
```

这会显示完整的 LSF 命令，包括工作目录、日志文件路径等，方便你验证配置是否正确。

## Q11: 如何支持 Python 脚本？

1. 在 `dependency.yaml` 中指定 `.py` 文件：
   ```yaml
   - test_py:
       cmd: test_py.py
   ```

2. 在 `config.yaml` 中配置 `tool_opt`：
   ```yaml
   pv_calibre:
     test_py:
       tool_opt: "python"
       lsf: 0
   ```

## Q12: 配置文件加载顺序是什么？

假设你的路径为：
- **edp_center**: `/home/user/EDP_AI/edp_center`
- **foundry**: `SAMSUNG`
- **node**: `S8`
- **project**: `dongting`
- **flow_name**: `pv_calibre`
- **分支目录**: `/home/user/WORK_PATH/dongting/P85/block1/user1/main`

配置文件按以下顺序加载（后加载的覆盖先加载的）：

1. `/home/user/EDP_AI/edp_center/config/SAMSUNG/S8/common/main/init_project.yaml`
2. `/home/user/EDP_AI/edp_center/config/SAMSUNG/S8/common/main/config.yaml`
3. `/home/user/EDP_AI/edp_center/config/SAMSUNG/S8/common/pv_calibre/config.yaml`
4. `/home/user/EDP_AI/edp_center/config/SAMSUNG/S8/dongting/main/init_project.yaml`
5. `/home/user/EDP_AI/edp_center/config/SAMSUNG/S8/dongting/main/config.yaml`
6. `/home/user/EDP_AI/edp_center/config/SAMSUNG/S8/dongting/pv_calibre/config.yaml`
7. `/home/user/WORK_PATH/dongting/P85/block1/user1/main/user_config.yaml` 或 `user_config.tcl`（最高优先级）

## Q13: 如何查看自动生成的变量？

假设你的分支目录为：`/home/user/WORK_PATH/dongting/P85/block1/user1/main`

查看 `runs/{flow_name}/{step_name}/full.tcl` 文件，所有自动生成的变量都在文件最后（确保不被配置文件覆盖）。

```bash
# 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 查看 full.tcl 文件
cat runs/pv_calibre/ipmerge/full.tcl

# 或使用完整路径
cat /home/user/WORK_PATH/dongting/P85/block1/user1/main/runs/pv_calibre/ipmerge/full.tcl
```

**文件位置**：
- `/home/user/WORK_PATH/dongting/P85/block1/user1/main/runs/pv_calibre/ipmerge/full.tcl`

**自动生成的变量示例**：
```tcl
# Generated by configkit
# ... (文件头注释) ...

# Auto-generated project variables
set project(project_name) "dongting"
set project(version) "P85"
set project(block_name) "block1"
set project(user_name) "user1"
set project(branch_name) "main"
set project(foundry) "SAMSUNG"
set project(node) "S8"
set project(init_path) "/home/user/WORK_PATH"
set project(work_path) "/home/user/WORK_PATH/dongting/P85/block1/user1/main/runs/pv_calibre/ipmerge"
set project(flow_name) "pv_calibre"
set project(step_name) "ipmerge"

# Auto-generated platform variables
set edp(edp_center_path) "/home/user/EDP_AI/edp_center"
set edp(config_path) "/home/user/EDP_AI/edp_center/config"
set edp(flow_path) "/home/user/EDP_AI/edp_center/flow"

# ... (其他配置变量) ...
```

## Q14: 如何使用日志系统进行调试？

EDP 框架提供了统一的日志系统，帮助你更好地追踪和调试问题。

### 日志级别控制

可以通过环境变量 `EDP_LOG_LEVEL` 控制日志级别：

```bash
# 开发环境：显示所有日志（包括 DEBUG）
export EDP_LOG_LEVEL=DEBUG

# 生产环境：只显示重要信息
export EDP_LOG_LEVEL=INFO
# 或
export EDP_LOG_LEVEL=WARNING
```

### 日志输出位置

- **控制台输出**：日志默认输出到 stderr，格式为 `时间戳 - 模块名 - 级别 - 消息`
- **日志文件**：如果指定了日志文件路径，日志会同时写入文件

### 错误信息格式

当遇到错误时，你会看到：

**用户输出**（友好格式）：
```
❌ 配置验证失败
  ERROR: Value '64' of variable 'pv_calibre(ipmerge,cpu_num)' is not in constraint list. Allowed values are: 1 2 4 8 16 32
  配置文件: /path/to/user_config.yaml

💡 建议: 请检查配置文件，将变量值改为允许的值
```

**日志记录**（结构化数据）：
```
2025-11-14 16:31:41 - edp_center.main.cli.utils.full_tcl_generator - ERROR - ❌ 配置验证失败
  ERROR: Value '64' of variable 'pv_calibre(ipmerge,cpu_num)' is not in constraint list. Allowed values are: 1 2 4 8 16 32
  配置文件: /path/to/user_config.yaml
Traceback (most recent call last):
  ...
```

### 查看日志

1. **控制台输出**：直接查看命令执行时的 stderr 输出
2. **日志文件**：如果指定了日志文件，查看文件中的完整记录
3. **结构化信息**：日志中包含上下文信息（如 flow_name, step_name, search_paths 等），便于问题定位

### 常见问题

**Q: 如何查看完整的错误堆栈？**
A: 日志记录中会自动包含完整的堆栈跟踪信息，查看日志文件即可。

**Q: 日志会影响性能吗？**
A: 日志记录是异步的，一般不会显著影响性能。但在高频操作中，建议使用 `INFO` 或 `WARNING` 级别。

**Q: 如何只查看错误日志？**
A: 设置 `EDP_LOG_LEVEL=ERROR`，只显示 ERROR 级别的日志。

更多详细信息请参考 [最佳实践 - 日志系统](07_best_practices.md#6-日志系统)。

## Q15: 如何查看和生成 HTML 教程？

EDP_AI 框架提供了完整的教程文档系统，支持生成美观的 HTML 格式教程。

### 基本用法

```bash
# 方式 A: 使用快捷命令（推荐）
edp -tutor                    # 生成 HTML 教程并在浏览器中打开
edp -tutor --force           # 强制重新生成所有 HTML 文件
edp -tutor --browser firefox # 指定浏览器（firefox, chrome, chromium）
edp -tutor --open-dir        # 只打开教程目录（不生成 HTML）

# 方式 B: 使用完整命令
edp_info -tutorial           # 生成 HTML 教程并在浏览器中打开
edp_info -tutorial --force   # 强制重新生成所有 HTML 文件
edp_info -tutorial --open-dir # 只打开教程目录（不生成 HTML）
```

### 常见问题

**Q: HTML 文件生成在哪里？**
A: HTML 文件统一生成在 `edp_center/tutorial/index.html`，由 PM 负责维护和更新。普通用户不需要生成 HTML，直接打开即可。

**Q: 为什么 HTML 文件生成在 `edp_center/tutorial/` 目录？**
A: 为了统一管理，避免每个用户都在本地生成 HTML 文件。PM 负责更新 HTML，所有用户共享同一个 HTML 文件。

**Q: 如何更新 HTML 文件？**
A: PM 使用 `edp -tutor --update` 更新 HTML 文件。系统会自动检测 Markdown 文件的修改时间，只更新已修改的文件。如果需要强制重新生成所有文件，使用 `edp -tutor --update --force`。

**Q: HTML 文件会占用很多空间吗？**
A: 不会。HTML 文件通常只有几 KB 到几十 KB，而且统一存放在 `edp_center/tutorial/` 目录下，不会在用户本地生成。

**Q: 可以离线查看 HTML 教程吗？**
A: 可以。生成的 HTML 文件是静态的，可以离线查看，也可以复制到其他位置分享。

**Q: 生成的 HTML 格式正确吗？**
A: 系统会自动处理代码块、列表、链接、标题等格式，生成的 HTML 包含完整的样式和导航。

更多详细信息请参考 [基本使用 - 查看教程](03_basic_usage.md#7-查看教程-edp--tutor-或-edp_info--tutorial)。

## Q16: 文件搜索缓存是什么？如何工作？

框架内置了**文件搜索缓存机制**，用于提升 `#import` 指令处理时的性能。

### 什么是文件搜索缓存？

**简单理解**：系统的"记忆本"，记住之前找过的文件在哪里，下次直接告诉你答案。

**类比**：
- 就像图书管理员记录"《Python编程》在第3排第5层"
- 下次有人借同一本书，直接看记录本，1秒就找到了
- 不用再从第一排开始，一排一排地找

### 工作原理

**第一次搜索**（无缓存）：
```
搜索 helper.tcl
  → 搜索整个目录（1000+ 文件）
  → 找了 3.37 毫秒，找到了！
  → 📝 记录：helper.tcl 在 /path/to/helper.tcl
```

**第二次搜索**（有缓存）：
```
搜索 helper.tcl（相同文件）
  → 📝 查看记录：哦，在 /path/to/helper.tcl
  → 直接使用，0.67 毫秒！
```

**性能提升**：从 3.37ms 降到 0.67ms，**快了 5 倍**！

### 实际效果

**场景**：处理包含多个 `#import` 的脚本

```tcl
#import source helper.tcl
#import source utils.tcl
#import source helper.tcl    # 重复了！
#import source common.tcl
#import source helper.tcl    # 又重复了！
```

**性能对比**：

| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 第1次搜索 helper.tcl | 3.37 ms | 3.37 ms | - |
| 第2次搜索 helper.tcl | 3.37 ms | **0.67 ms** | **5x** |
| 第3次搜索 helper.tcl | 3.37 ms | **0.67 ms** | **5x** |
| **总耗时** | **10.11 ms** | **4.71 ms** | **2.1x** |

### 缓存失效机制

框架会**自动检测**目录变化：

- ✅ **目录未修改** → 使用缓存（快速）
- ❌ **目录被修改** → 缓存失效，重新搜索（确保准确性）

**示例**：
```
1. 搜索 helper.tcl → 找到并缓存
2. 用户修改了目录（添加/删除文件）
3. 目录时间戳变化
4. 再次搜索 helper.tcl → 缓存失效，重新搜索
5. 更新缓存
```

### 常见问题

**Q: 缓存会占用很多内存吗？**

A: 不会。缓存只记录文件路径，不存储文件内容。
- 一个缓存项：几 KB
- 1000 个缓存项：几 MB
- 对现代计算机来说，很小

**Q: 缓存会出错吗？**

A: 不会。系统会检查：
- 文件还在不在
- 目录有没有被修改
- 如果不对，会自动重新搜索

**Q: 什么时候需要清除缓存？**

A: 很少需要。系统会自动检查：
- 如果文件被移动了 → 自动清除
- 如果目录被修改了 → 自动清除
- 只有在怀疑缓存有问题时，才需要手动清除

**Q: 如何手动清除缓存？**

A: 通常不需要，但如果需要：

```python
from edp_center.packages.edp_cmdkit.file_finder import clear_file_cache

clear_file_cache()  # 清除所有缓存
```

### 总结

- ✅ **自动工作**：框架自动管理缓存，无需手动干预
- ✅ **性能提升**：重复搜索快 5 倍
- ✅ **智能失效**：目录变化时自动失效
- ✅ **结果可靠**：缓存结果与直接搜索一致

更多技术细节请参考 [最佳实践 - 代码结构](07_best_practices.md#7-代码结构最佳实践)。

## Q17: 如何使用 edp_libkit 生成库配置文件？

`edp_libkit` 是一个库配置生成工具，用于从分散的库文件中收集配置信息，生成统一的 `lib_config.tcl` 配置文件。

### 基本用法

```bash
# 处理单个STD库（自动选择最新版本）
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/std_library_dir \
  --lib-type STD \
  --lib-output-dir /path/to/output

# 批量处理多个库
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/lib1 /path/to/lib2 /path/to/lib3 \
  --lib-type STD \
  --lib-output-dir /path/to/output

# 处理所有版本
edp -lib --foundry Samsung --node ln08lpu_gp \
  --lib-path /path/to/library_dir \
  --lib-type STD \
  --lib-all-versions \
  --lib-output-dir /path/to/output

# 启动图形界面（推荐新手）
edp -lib --lib-gui
```

### 常见问题

**Q: 支持哪些 foundry 和库类型？**  
A: 支持 Samsung、SMIC、TSMC 等 foundry，以及 STD（标准单元库）、IP（IP库）、MEM（内存库）三种库类型。

**Q: 如何指定特定版本？**  
A: 使用 `--lib-version` 参数指定版本号，如 `--lib-version 2.00A`。如果不指定，默认使用最新版本。

**Q: 输出文件在哪里？**  
A: 输出文件在 `{output_dir}/{lib_name}/lib_config.tcl`。如果使用 `--lib-all-versions`，最新版本生成 `lib_config.tcl`，其他版本生成 `lib_config.{version}.tcl`。

**Q: 可以批量处理吗？**  
A: 可以。可以指定多个 `--lib-path`，或使用 `--lib-paths-file` 从文件读取路径列表。如果指定的是安装目录，工具会自动检测并展开多个库。

**Q: 如何启动图形界面？**  
A: 使用 `edp -lib --lib-gui` 启动图形界面，界面直观易用，无需查看文档。

更多详细信息请参考 [基本使用 - 生成库配置文件](03_basic_usage.md#7-生成库配置文件-edp--lib) 和 `edp_center/packages/edp_libkit/README.md`。

---

## 下一步

- 📖 [查看更多资源](09_resources.md)
- 🏠 [返回目录](../TUTORIAL.md)

[← 返回目录](../TUTORIAL.md)

