# Sub_steps 机制和 Debug 模式

[← 返回目录](../TUTORIAL.md)

本文档介绍 EDP_AI 框架的 Sub_steps 机制和 Debug 模式的使用方法。

## 1. Sub_steps 机制

Sub_steps 允许你将一个大的步骤拆分成多个可复用的小步骤，便于管理和调试。

**适用场景**：
- **使用 sub_steps 的 flow（如 `pnr_innovus`）**：使用 sub_steps 机制，将步骤拆分为多个子步骤，便于管理和调试
- **简单 flow（如 `pv_calibre`）**：不需要 sub_steps，直接在主脚本中写散装代码，使用 `#import source` 加载 proc 定义即可

**选择建议**：
- 如果步骤逻辑简单，直接在主脚本中写散装代码，使用 `#import source` 加载 proc 定义即可
- 如果步骤逻辑复杂，需要分步执行和调试，使用 sub_steps 机制

### 定义 Sub_steps

在 `dependency.yaml` 中使用字典格式定义 sub_steps：

```yaml
# dependency.yaml
pnr_innovus:
  dependency:
    FP_MODE:
      - place:
          out: place.pass
          cmd: place.tcl
          sub_steps:
            innovus_restore_design.tcl: pnr_innovus::restore_design
            innovus_config_design.tcl: pnr_innovus::config_design
            innovus_add_tie_cell.tcl: pnr_innovus::add_tie_cell
            innovus_save_design.tcl: pnr_innovus::save_design
            innovus_report_design.tcl: pnr_innovus::report_design
            innovus_check_pd.tcl: pnr_innovus::check_pd
            innovus_save_metrics.tcl: pnr_innovus::save_metrics
```

**格式说明**：
- Key：文件名（如 `innovus_restore_design.tcl`），可以是任意文件名
- Value：proc 名称（如 `pnr_innovus::restore_design`，使用 Tcl namespace 语法 `::`）

**重要说明**：
- 文件名和 proc 名称之间**没有强制对应关系**
- 只要该文件中定义了对应的 proc 即可，例如：
  - `a_b.tcl: a::b` ✓（文件 `a_b.tcl` 中定义了 `proc ::a::b {} { ... }`）
  - `aasdfas_fawef.tcl: a::b` ✓（文件 `aasdfas_fawef.tcl` 中定义了 `proc ::a::b {} { ... }`）
- 框架会根据文件名找到对应的 tcl 文件，然后调用文件中定义的 proc

### 创建 Sub_step 文件

Sub_step 文件应该放在 `sub_steps/` 目录下：

```
cmds/pnr_innovus/
├── sub_steps/               # Sub_step proc 文件目录
│   ├── innovus_restore_design.tcl
│   ├── innovus_config_design.tcl
│   ├── innovus_add_tie_cell.tcl
│   └── ...
├── helpers/                 # 辅助代码目录
│   └── helper.tcl
└── place.tcl                # 主脚本
```

每个文件定义一个 proc：

```tcl
# cmds/pnr_innovus/sub_steps/innovus_restore_design.tcl
# Sub Step: pnr_innovus::restore_design
# 恢复设计状态
# 文件位置：sub_steps/ 目录下

proc ::pnr_innovus::restore_design {} {
    # 声明全局变量（数组），以便在 namespace 中访问和修改
    global edp project
    
    puts "========== Sub Step: pnr_innovus::restore_design =========="
    
    # 从配置中获取 restore 文件路径
    if {[info exists project(work_path)]} {
        set restore_file [file join $project(work_path) restore.db]
        if {[file exists $restore_file]} {
            puts "Restoring design from: $restore_file"
            puts "INFO: Simulating restoreDesign command"
            puts "Design restored successfully."
        } else {
            puts "Warning: Restore file not found: $restore_file"
        }
    } else {
        puts "Warning: project(work_path) not defined, skipping restore."
    }
    
    puts "========== End of Sub Step: pnr_innovus::restore_design =========="
}
```

**Proc 定义格式说明**：
- 使用 `proc ::namespace::proc_name {} { ... }` 格式直接定义
- 在 proc 内部使用 `global` 声明全局变量（数组），以便访问和修改
- 使用 `global` 后，可以像外部脚本一样使用 `$edp(...)` 和 `$project(...)`
- **支持 `#import source`**：可以在 proc 内部使用 `#import source` 指令加载辅助文件
  - 例如：`#import source helper.tcl` 会被转换为 `source /path/to/helper.tcl`
  - 这些 `source` 语句会在运行时执行，加载对应的文件

### 主脚本结构

**重要**：主脚本只需要包含 pre_step 部分，sub_steps 会自动从 `dependency.yaml` 生成！

```tcl
# cmds/pnr_innovus/place.tcl
# 主脚本结构：
# 1. Pre_step 部分（本文件内容）：包含 #import source 和初始化代码
# 2. Sub_steps 部分（自动生成）：根据 dependency.yaml 自动生成调用
# 3. Post_step 部分（step.post hook）：在 hooks/pnr_innovus.place/step.post 中定义

# ========== Pre_step 部分 ==========
# 导入 util（推荐使用 #import source）
#import source helper.tcl

# 其他 pre_step 代码可以写在这里
# 例如：初始化变量、设置环境等

# ========== Sub_steps 部分（自动生成）==========
# 以下 sub_steps 调用会根据 dependency.yaml 自动生成：
# - pnr_innovus::restore_design
# - pnr_innovus::config_design
# - pnr_innovus::add_tie_cell
# - pnr_innovus::save_design
# - pnr_innovus::report_design
# - pnr_innovus::check_pd
# - pnr_innovus::save_metrics
# 不需要手动写这些调用！

# ========== Post_step 部分（在 step.post hook 中）==========
# Post_step 代码应该写在 hooks/pnr_innovus.place/step.post 中
```

**注意**：
- **主脚本中的所有逻辑都属于 pre_step 部分**
- sub_steps 的调用会根据 `dependency.yaml` 自动生成，不需要手动写
- 如果主脚本中还有手动写的 sub_step 调用，系统仍然会处理，但建议移除
- `#import` 指令应该放在 pre_step 部分（主脚本或 step.pre hook）或 post_step 部分（step.post hook）
- 不允许在 sub_steps 之间使用 `#import` 指令

**极限情况**：
- 即使主脚本是空的，hooks 也是空的，只要 `dependency.yaml` 中配置了 sub_steps
- 最终生成的脚本仍然会包含：
  1. **文件开头**：直接展开的 sub_step proc 定义（所有 proc 内容直接嵌入，不是 source 语句）
  2. **文件中间**：自动生成的 sub_steps 调用（按 `dependency.yaml` 中的顺序）
- 这是完全可行的，体现了"配置驱动"的设计理念
- 主脚本可以只包含注释，甚至完全为空，框架会根据配置自动生成完整的执行脚本

### 自动展开机制

框架会自动：
1. 从 `dependency.yaml` 读取 `sub_steps` 配置
2. 读取所有 sub_step 文件内容，处理其中的 `#import source` 指令
3. 将所有 sub_step proc 定义直接展开到生成的主脚本开头（不是生成 `source` 语句）
4. 按照配置的顺序生成 sub_step 调用代码

### 完整示例：从原始文件到最终生成脚本

下面通过一个完整的示例，展示框架如何处理主脚本、sub_steps 和 hooks，生成最终的执行脚本。

#### 1. 原始文件结构

假设我们有以下文件：

**主脚本** (`cmds/pnr_innovus/place.tcl`):
```tcl
# ========== Pre_step 部分 ==========
#import source helper.tcl

puts "开始执行 place 步骤"
set project(place_start_time) [clock seconds]
```

**Sub_step 文件** (`sub_steps/innovus_add_tie_cell.tcl`):
```tcl
proc ::pnr_innovus::add_tie_cell {} {
    global edp project pnr_innovus
    
    # 支持在 proc 内部使用 #import source
    #import source tie_cell_helper.tcl
    
    puts "========== Sub Step: pnr_innovus::add_tie_cell =========="
    puts "添加 Tie Cell..."
    puts "========== End of Sub Step: pnr_innovus::add_tie_cell =========="
}
```

**Hooks 文件**:

`hooks/pnr_innovus.place/step.pre`:
```tcl
puts "准备执行 place 步骤"
set start_time [clock seconds]
```

`hooks/pnr_innovus.place/step.post`:
```tcl
puts "place 步骤执行完成"
set end_time [clock seconds]
puts "总耗时: [expr $end_time - $start_time] 秒"
```

`hooks/pnr_innovus.place/add_tie_cell.tcl.pre`:
```tcl
puts "========== Pre-step: add_tie_cell =========="
set tie_cell_count 100
```

`hooks/pnr_innovus.place/add_tie_cell.tcl.post`:
```tcl
puts "========== Post-step: add_tie_cell =========="
puts "Tie cell 添加完成，数量: $tie_cell_count"
```

#### 2. 最终生成的脚本

框架处理后的最终脚本（`cmds/pnr_innovus/place.tcl`，实际执行的文件）:

```tcl
# ========== 文件头部：Packages ==========
# All packages from general common package default path
source /path/to/packages/common_default.tcl
source /path/to/packages/node_default.tcl
# ... 其他 packages

# ========== 文件头部：Sub_step proc 定义（直接展开）==========
# ========== Sub_step: innovus_add_tie_cell.tcl (proc: pnr_innovus::add_tie_cell) ==========
proc ::pnr_innovus::add_tie_cell {} {
    global edp project pnr_innovus
    
    # #import source 被转换为 source 语句
    source /path/to/tie_cell_helper.tcl
    
    puts "========== Sub Step: pnr_innovus::add_tie_cell =========="
    puts "添加 Tie Cell..."
    puts "========== End of Sub Step: pnr_innovus::add_tie_cell =========="
}
# ========== End of Sub_step: innovus_add_tie_cell.tcl ==========

# ... 其他 sub_step proc 定义（如果有）

# ========== 文件头部：Sub_step hooks proc 定义（自动封装）==========
# ========== Sub_step pre-step procs ==========
# ========== sub_step.pre hook: pnr_innovus::add_tie_cell ==========
proc ::pnr_innovus::add_tie_cell_pre {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus
    
    puts "========== Pre-step: add_tie_cell =========="
    set tie_cell_count 100
}
# ========== end of sub_step.pre hook: pnr_innovus::add_tie_cell ==========

# ========== Sub_step post-step procs ==========
# ========== sub_step.post hook: pnr_innovus::add_tie_cell ==========
proc ::pnr_innovus::add_tie_cell_post {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus
    
    puts "========== Post-step: add_tie_cell =========="
    puts "Tie cell 添加完成，数量: $tie_cell_count"
}
# ========== end of sub_step.post hook: pnr_innovus::add_tie_cell ==========

# ========== 文件头部：Step hooks proc 定义（自动封装）==========
# ========== Step pre hook ==========
proc ::pnr_innovus::place_pre {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus
    
    puts "准备执行 place 步骤"
    set start_time [clock seconds]
}

# ========== Step post hook ==========
proc ::pnr_innovus::place_post {} {
    # 声明全局变量（框架自动添加）
    global edp project pnr_innovus
    
    puts "place 步骤执行完成"
    set end_time [clock seconds]
    puts "总耗时: [expr $end_time - $start_time] 秒"
}

# ========== 主脚本内容（处理 #import source）==========
# ========== Pre_step 部分 ==========
source /path/to/helper.tcl

puts "开始执行 place 步骤"
set project(place_start_time) [clock seconds]

# ========== Auto-generated sub_steps calls ==========
# Sub_steps are automatically generated from dependency.yaml

# 调用 step.pre hook
pnr_innovus::place_pre

# 如果有 pre hook，先调用 pre-step
pnr_innovus::add_tie_cell_pre
# 调用 sub_step proc
pnr_innovus::add_tie_cell
# 如果有 post hook，在 sub_step 调用之后调用 post-step
pnr_innovus::add_tie_cell_post

# ... 其他 sub_steps 调用（按 dependency.yaml 中的顺序）

# ========== End of auto-generated sub_steps calls ==========

# 调用 step.post hook
pnr_innovus::place_post
```

#### 3. 关键点说明

1. **Sub_step proc 定义**：直接展开到文件头部，不是 `source` 语句
2. **Sub_step proc 中的 `#import source`**：被转换为 `source` 语句，在运行时执行
3. **Hooks 自动封装**：所有 hooks（step.pre/post, sub_step.pre/post）都被自动封装为 proc
4. **自动添加 global**：框架自动添加 `global edp project {flow_name}`
5. **执行顺序**：
   - Step.pre hook
   - Sub_step.pre hook → Sub_step proc → Sub_step.post hook（对每个 sub_step）
   - Step.post hook

#### 4. 执行流程

当运行 `edp -run pnr_innovus.place` 时，执行顺序为：

```
1. 加载所有 packages
2. 定义所有 sub_step procs（直接展开）
3. 定义所有 hooks procs（自动封装）
4. 执行主脚本内容（处理 #import source）
5. 调用 step.pre hook
6. 对每个 sub_step：
   - 调用 sub_step.pre hook
   - 调用 sub_step proc
   - 调用 sub_step.post hook
7. 调用 step.post hook
```

这样，框架将所有内容整合到一个完整的、可直接执行的脚本中。

### 跳过 Sub_steps（非 Debug 模式）

在非 debug 模式下，可以通过 `user_config.yaml` 配置跳过某些 sub_steps。

#### 配置方式

在 `user_config.yaml` 中配置 `skip_sub_step` 字段：

```yaml
# user_config.yaml
pnr_innovus:
  place:
    skip_sub_step: "pnr_innovus::check_pd pnr_innovus::report_design"
```

**格式说明**：
- `skip_sub_step` 的值是一个字符串，包含要跳过的 sub_step proc 名称，用空格分隔
- 多个 sub_step 名称之间用空格分隔
- proc 名称使用 Tcl namespace 语法（如 `pnr_innovus::check_pd`）

#### 工作原理

当配置了 `skip_sub_step` 后，框架会：

1. **在脚本开头添加初始化代码**：
   ```tcl
   # ========== Skip sub_steps configuration ==========
   set edp(skip,pnr_innovus::check_pd) 1
   set edp(skip,pnr_innovus::report_design) 1
   # ====================================================
   ```

2. **将 sub_step 调用包装在条件判断中**：
   ```tcl
   # 原始代码
   pnr_innovus::check_pd
   
   # 条件化后
   if {![info exists edp(skip,pnr_innovus::check_pd)]} {
       pnr_innovus::check_pd
   }
   ```

#### 使用场景

- **临时跳过某些检查步骤**：在快速迭代时跳过耗时的检查步骤
- **选择性执行**：只执行必要的 sub_steps，跳过可选的步骤
- **调试特定步骤**：跳过已知正常的步骤，专注于调试有问题的步骤

#### 动态控制

由于使用了 `edp(skip,proc_name)` 变量，你还可以在脚本中动态控制：

```tcl
# 在 step.pre hook 中动态设置
set edp(skip,pnr_innovus::check_pd) 1  # 跳过
unset edp(skip,pnr_innovus::check_pd)  # 取消跳过（恢复执行）
```

#### 注意事项

- **仅适用于非 debug 模式**：在 debug 模式下，应该使用 `edp_run -skip` 命令来跳过步骤
- **配置优先级**：`user_config.yaml` 中的配置会在脚本生成时应用，运行时可以通过 Tcl 变量动态修改
- **向后兼容**：如果没有配置 `skip_sub_step`，所有 sub_steps 都会正常执行

#### 示例

```yaml
# user_config.yaml
pnr_innovus:
  place:
    skip_sub_step: "pnr_innovus::check_pd pnr_innovus::report_design"
```

运行后，生成的脚本会跳过 `pnr_innovus::check_pd` 和 `pnr_innovus::report_design` 这两个步骤。

## 2. Debug 模式 - 交互式 Sub_steps 调试

Debug 模式允许你逐步执行和调试 sub_steps，非常适合开发和测试。

**适用场景**：
- **主要适用于**：`pnr_innovus` 等使用 sub_steps 机制的 flow
- **通常不需要**：`pv_calibre` 等不使用sub_steps的 flow（没有 sub_steps，直接执行脚本即可）
- **使用建议**：只有在需要逐步调试 sub_steps 时才启用 debug 模式

### 启用 Debug 模式

使用 `--debug` 参数进入交互式调试模式：

```bash
# 进入分支目录
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main

# 以 debug 模式运行
edp -run pnr_innovus.place --debug
```

### Debug 模式行为

在 debug 模式下：
1. 系统会 source 所有必要的文件和配置
2. 初始化 `edp_sub_steps_manager`
3. 进入交互式 Tcl shell
4. 你可以在 shell 中手动控制 sub_steps 的执行

### 交互式命令

在 debug 模式的 Tcl shell 中，可以使用以下命令：

#### 初始化和管理

```tcl
# 初始化管理器（通常在脚本开头自动完成）
edp_run -init edp(execution_plan,place)

# 查看所有 sub_steps 及其状态
edp_run -info
```

#### 执行 Sub_steps

```tcl
# 执行下一个步骤
edp_run -next

# 跳过下一个步骤
edp_run -next -skip

# 执行指定步骤（支持索引或 proc 名称）
edp_run 2
edp_run pnr_innovus::add_tie_cell

# 执行范围（从某个步骤到某个步骤）
edp_run -from 2 -to 5
edp_run -from pnr_innovus::config_design -to pnr_innovus::save_design

# 执行到指定步骤
edp_run -to 5
edp_run -to pnr_innovus::save_design

# 执行所有步骤
edp_run -all
```

#### 跳过步骤

```tcl
# 跳过下一个步骤
edp_run -next -skip

# 执行范围时跳过某些步骤（支持索引或 proc 名称）
edp_run -from 0 -to 6 -skip 3 4
edp_run -from 0 -to 6 -skip pnr_innovus::save_design pnr_innovus::report_design

# 执行到指定步骤时跳过某些步骤
edp_run -to 5 -skip 2 3
edp_run -to pnr_innovus::save_design -skip pnr_innovus::add_tie_cell

# 执行所有步骤时跳过某些步骤
edp_run -all -skip pnr_innovus::check_pd pnr_innovus::report_design
```

**注意**：
- `-skip` 参数可以接受多个步骤引用（索引或 proc 名称），用空格分隔
- 跳过的步骤会被标记为 `[SKIPPED]` 状态，不会执行
- 可以在 `-from/-to`、`-to`、`-all` 等命令中使用 `-skip` 参数

#### 安全保护

系统会自动检查并警告：

1. **跳过未执行的步骤**：
   ```tcl
   edp_run 2
   # WARNING: The following steps will be skipped:
   #   [0] pnr_innovus::restore_design
   #   [1] pnr_innovus::config_design
   # To execute anyway, use: edp_run 2 -force
   ```

2. **重新执行已完成的步骤**：
   ```tcl
   edp_run 2
   # WARNING: Step [2] pnr_innovus::add_tie_cell has already been executed (status: success)
   # To re-execute, use: edp_run 2 -force
   ```

使用 `-force` 参数可以强制执行：

```tcl
# 强制执行（跳过警告）
edp_run 2 -force
edp_run -from 2 -to 5 -force
```

### 状态显示

`edp_run -info` 会显示所有步骤的状态：

```
========== Available Sub Steps ==========
  [0] pnr_innovus::restore_design  [OK]      <-- next
  [1] pnr_innovus::config_design    [PENDING]
  [2] pnr_innovus::add_tie_cell     [PENDING]
  [3] pnr_innovus::save_design      [PENDING]
  [4] pnr_innovus::report_design    [PENDING]
  [5] pnr_innovus::check_pd         [PENDING]
  [6] pnr_innovus::save_metrics     [PENDING]
=========================================
Total: 7 sub_step(s)
  Success: 1
  Failed:  0
  Pending: 6
Last executed: [0] pnr_innovus::restore_design (success)
Next to execute: [1] pnr_innovus::config_design
=========================================
```

**状态标记**：
- `[OK]` - 成功完成
- `[FAILED]` - 执行失败
- `[SKIPPED]` - 已跳过
- `[PENDING]` - 未执行

### 使用场景

Debug 模式特别适合：

1. **开发新步骤**：逐步测试每个 sub_step（适用于 pnr_innovus 等使用 sub_steps 的 flow）
2. **调试问题**：在特定步骤停止，检查状态
3. **选择性执行**：只执行部分 sub_steps
4. **重新执行**：重新运行失败的步骤

**何时不需要 Debug 模式**：
- **简单 flow**（如 `pv_calibre`）：没有 sub_steps，直接执行脚本即可，不需要逐步调试
- **正常生产运行**：不需要逐步调试时，直接使用 `edp -run` 即可
- **没有 sub_steps 的 flow**：debug 模式主要是为了调试 sub_steps，如果没有 sub_steps 则不需要

### 示例工作流

```bash
# 1. 进入 debug 模式
cd /home/user/WORK_PATH/dongting/P85/block1/user1/main
edp -run pnr_innovus.place -debug 1

# 2. 在 Tcl shell 中
% edp_run -info                    # 查看所有步骤
% edp_run -next                    # 执行第一个步骤
% edp_run -next -skip              # 跳过第二个步骤
% edp_run -next                    # 执行第三个步骤
% edp_run -from 0 -to 6 -skip 3 4  # 执行范围，跳过步骤 3 和 4
% edp_run 5                        # 直接跳到第 5 个步骤（会警告）
% edp_run 5 -force                 # 强制执行（跳过警告）
% edp_run -from 0 -to 3            # 执行前 4 个步骤
% edp_run -info                    # 再次查看状态
```

---

## 下一步

- ⚙️ [掌握配置文件高级用法](06_configuration.md)
- 📚 [参考最佳实践](07_best_practices.md)
- ❓ [查看常见问题](08_faq.md)

[← 返回目录](../TUTORIAL.md)

