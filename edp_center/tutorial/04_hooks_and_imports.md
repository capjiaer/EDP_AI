# Hooks 机制和 #import 指令

[← 返回目录](../TUTORIAL.md)

本文档介绍 EDP_AI 框架的 Hooks 机制和 `#import` 指令的使用方法。

## 0. 生成的脚本结构

当你运行 `edp -run` 命令时，框架会自动生成最终的可执行脚本（位于 `cmds/{flow_name}/{step_name}.tcl`）。生成的脚本结构如下：

```
# 1. Package Source 语句（自动生成）
#    从以下位置自动加载 Tcl 包：
#    - flow/common/packages/tcl/default/*
#    - flow/common/packages/tcl/{flow_name}/*
#    - flow/initialize/{FOUNDRY}/{NODE}/common/packages/tcl/default/*
#    - flow/initialize/{FOUNDRY}/{NODE}/common/packages/tcl/{flow_name}/*
#    - flow/initialize/{FOUNDRY}/{NODE}/{PROJECT}/packages/tcl/default/*
#    - flow/initialize/{FOUNDRY}/{NODE}/{PROJECT}/packages/tcl/{flow_name}/*
source /path/to/package1.tcl
source /path/to/package2.tcl
...

# 2. Full.tcl Source 语句（自动生成）
#    加载合并后的配置文件（包含所有配置变量）
source /path/to/runs/{flow_name}.{step_name}/full.tcl

# 3. Sub_steps Proc 定义（自动生成）
#    从 dependency.yaml 读取 sub_steps 配置，自动展开所有 sub_step proc 定义
namespace eval {flow_name} {}
proc ::{flow_name}::{sub_step_proc} {} {
    # sub_step 代码
}
...

# 4. Step.pre Hook（如果存在）
#    框架自动封装为 proc 并调用
proc ::{flow_name}::{step_name}_pre {} {
    # step.pre hook 代码
}
::{flow_name}::{step_name}_pre

# 5. 主脚本内容
#    你写在 steps/{flow_name}.{step_name}/ 目录下的主脚本
#    所有 #import source 指令会被展开

# 6. Sub_steps 调用（自动生成）
#    从 dependency.yaml 读取 sub_steps 顺序，自动生成调用语句
::{flow_name}::{sub_step1}
::{flow_name}::{sub_step2}
...

# 7. Step.post Hook（如果存在）
#    框架自动封装为 proc 并调用
proc ::{flow_name}::{step_name}_post {} {
    # step.post hook 代码
}
::{flow_name}::{step_name}_post
```

**重要说明**：
- Package source 语句是**自动生成**的，你不需要手动添加
- 框架会根据 `foundry`、`node`、`project`、`flow_name` 自动推断并添加相应的 package source 语句
- 如果无法推断这些参数，package source 可能不会被添加（会记录警告日志）

## 1. Hooks 机制

Hooks 允许你在脚本执行前后插入自定义代码，或修改现有的 proc 定义。

### Hooks 类型

#### Step Hooks
- `step.pre`: 在步骤脚本执行前插入
- `step.post`: 在步骤脚本执行后插入

#### Util Hooks（已废弃）
- 注意：已移除 `#import util` 机制，util hooks 不再使用
- 如果需要修改 proc 定义，可以直接在主脚本中使用 `#import source` 加载文件，然后重新定义 proc

#### Sub_step Hooks
- `{file_name}.pre`: 在 sub_step proc 调用之前执行的逻辑
- `{file_name}.post`: 在 sub_step proc 调用之后执行的逻辑
- `{file_name}.replace`: 完全重写 sub_step proc（包含完整的 proc 定义）

**注意**：
- 已移除 `#import util` 机制，util hooks 不再使用
- 如果需要修改 proc 定义，可以直接在主脚本中使用 `#import source` 加载文件，然后重新定义 proc

### 使用示例

```bash
# 1. 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 2. 运行一次（会自动创建 hooks 目录和文件）
edp -run pv_calibre.ipmerge

# 3. 编辑 hooks 文件
vim hooks/pv_calibre.ipmerge/step.pre
# 或使用完整路径：
# vim /home/user/WORK_PATH/dongting/P85/block1/user1/main/hooks/pv_calibre.ipmerge/step.pre
```

Hooks 文件示例：

**Step Pre Hook**（框架会自动封装为 proc）：
```tcl
# hooks/pnr_innovus.place/step.pre
# 框架会自动封装为 proc ::pnr_innovus::place_pre {}
# 框架会自动添加 global edp project pnr_innovus

puts "准备执行 place 步骤"
set start_time [clock seconds]

# 检查前置条件
if {![file exists design.db]} {
    puts "WARNING: Design file not found!"
}
```

框架会自动生成：

```tcl
proc ::pnr_innovus::place_pre {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus
    
    puts "准备执行 place 步骤"
    set start_time [clock seconds]
    
    if {![file exists design.db]} {
        puts "WARNING: Design file not found!"
    }
}

# 调用 step.pre hook
::pnr_innovus::place_pre
```

**Step Post Hook**（框架会自动封装为 proc）：
```tcl
# hooks/pnr_innovus.place/step.post
# 框架会自动封装为 proc ::pnr_innovus::place_post {}
# 框架会自动添加 global edp project pnr_innovus

puts "place 步骤执行完成"
set end_time [clock seconds]
puts "总耗时: [expr $end_time - $start_time] 秒"
```

**注意**：已移除 `#import util` 机制，util hooks 不再使用。如果需要修改 proc 定义，可以直接在主脚本中使用 `#import source` 加载文件，然后重新定义 proc。

**Sub_step Replace Hook**：
```tcl
# hooks/pnr_innovus.place/innovus_restore_design.replace
# 完全重写 sub_step proc：包含完整的 proc 定义
proc ::pnr_innovus::restore_design {} {
    global edp project
    puts "OVERRIDDEN: Better restore design implementation"
    restoreDesign design_hacked.db
    puts "Design restored (hacked version)"
}
```

**Sub_step Pre Hook**（推荐使用文件名，只需写散装代码）：
```tcl
# hooks/pnr_innovus.place/add_tie_cell.tcl.pre
# 或者：hooks/pnr_innovus.place/add_tie_cell.pre（去掉 .tcl 扩展名）

# 注意：框架会自动添加 global edp project {flow_name}，不需要手动声明
# 例如：对于 pnr_innovus，会自动添加 global edp project pnr_innovus
# 如果需要其他 global 变量，可以自己添加

puts "========== Pre-step: add_tie_cell =========="
set start_time [clock seconds]

# 检查前置条件
if {![file exists design.db]} {
    puts "WARNING: Design file not found!"
    return -code error "Design file missing"
}

puts "准备添加 tie cell，开始时间: $start_time"
```

**Sub_step Post Hook**（推荐使用文件名，只需写散装代码）：
```tcl
# hooks/pnr_innovus.place/add_tie_cell.tcl.post
# 或者：hooks/pnr_innovus.place/add_tie_cell.post（去掉 .tcl 扩展名）

# 注意：框架会自动添加 global edp project {flow_name}，不需要手动声明
# 例如：对于 pnr_innovus，会自动添加 global edp project pnr_innovus
# 如果需要其他 global 变量，可以自己添加

puts "========== Post-step: add_tie_cell =========="
set end_time [clock seconds]

# 验证结果
if {[file exists design.db]} {
    puts "Tie cell 添加完成，结束时间: $end_time"
} else {
    puts "ERROR: Design file still not found after add_tie_cell!"
}
```

**Sub_step Replace Hook**（推荐使用文件名）：
```tcl
# hooks/pnr_innovus.place/config_design.tcl.replace
# 或者：hooks/pnr_innovus.place/config_design.replace（去掉 .tcl 扩展名）
# 完全重写 sub_step proc：包含完整的 proc 定义
proc ::pnr_innovus::config_design {} {
    global edp project
    puts "OVERRIDDEN: Better config design implementation"
    # ... 你的实现
}
```

**文件命名规则（按优先级）**：

对于 sub_step：`config_design.tcl: pnr_innovus::config_design`

1. **推荐方式**：使用完整文件名（最直观）
   - `config_design.tcl.pre`
   - `config_design.tcl.post`
   - `config_design.tcl.replace`

2. **简化方式**：去掉扩展名
   - `config_design.pre`
   - `config_design.post`
   - `config_design.replace`

**框架自动封装和自动添加 global**：

框架会自动：
1. 将你的散装代码封装为 proc（适用于 step.pre/post 和 sub_step.pre/post）
2. 自动添加常用的 `global edp project {flow_name}` 声明（如果用户没有写）

例如，你写的 hook 内容：

```tcl
# 你写的 hook 内容（散装代码，不需要写 global）
puts "准备添加 tie cell"
set start_time [clock seconds]
```

框架会自动生成：

```tcl
proc ::pnr_innovus::add_tie_cell_pre {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus
    
    puts "准备添加 tie cell"
    set start_time [clock seconds]
}
```

**注意**：框架会自动添加 `flow_name`（如 `pnr_innovus`、`pv_calibre`）到 global 声明中，因为代码中经常会用到 `$pnr_innovus(...)` 或 `$pv_calibre(...)` 等变量。

**优势**：
1. **简单易用**：只需要写逻辑代码，不需要关心 proc 定义和 global 声明
2. **自动添加 global**：框架自动添加常用的 `global edp project`，减少重复工作
3. **Debug Mode 支持**：生成的 proc 可以在 debug mode 中直接调用 `pnr_innovus::add_tie_cell_pre`
4. **自动命名**：框架自动生成标准 proc 名称 `{proc_name}_pre` 或 `{proc_name}_post`

**注意**：
- **统一使用文件名方式**：在 `dependency.yaml` 中就能看到文件名，不需要记住 proc_name
- **只需写散装代码**：不需要写 `proc ... {}` 包装，框架会自动封装（适用于 step.pre/post 和 sub_step.pre/post）
- **框架自动添加 global edp project {flow_name}**：如果用户没有写，框架会自动添加；如果用户已经写了，框架不会重复添加
  - 例如：对于 `pnr_innovus`，会自动添加 `global edp project pnr_innovus`
  - 例如：对于 `pv_calibre`，会自动添加 `global edp project pv_calibre`
- **可以添加其他 global 变量**：如果需要其他变量，可以自己添加
- `step.pre` 在步骤执行之前执行（封装为 `{flow_name}::{step_name}_pre`）
- `step.post` 在步骤执行之后执行（封装为 `{flow_name}::{step_name}_post`）
- `sub_step.pre` 在 sub_step proc 调用之前执行
- `sub_step.post` 在 sub_step proc 调用之后执行
- 生成的 proc 可以在 debug mode 中直接调用（如 `pnr_innovus::place_pre`、`pnr_innovus::add_tie_cell_pre`）

## 2. #import 指令

框架支持 `#import source` 指令：

### #import source

生成 `source` 语句，在运行时加载文件：

```tcl
#import source helper.tcl
```

处理为：
```tcl
source /path/to/helper.tcl
```

**适用场景**：
- 需要加载 proc 定义文件
- 文件较大，不需要看到完整代码
- 适用于所有 flow

**智能路径查找**：
- 支持相对路径（相对于当前文件）
- 支持搜索路径列表（search_paths）
- 支持递归查找子目录
- 自动转换为绝对路径

**注意**：
- `#import source` 会递归处理文件内的 `#import` 指令
- 如果文件未找到，会提供详细的错误信息和相似文件名建议

---

## 下一步

- 🐛 [学习 Sub_steps 和 Debug 模式](05_sub_steps_and_debug.md)
- ⚙️ [掌握配置文件高级用法](06_configuration.md)
- 📚 [参考最佳实践](07_best_practices.md)

[← 返回目录](../TUTORIAL.md)

