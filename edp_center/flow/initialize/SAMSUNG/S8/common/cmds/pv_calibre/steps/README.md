# Steps 目录说明

此目录用于存放主脚本文件（每个 step 的主脚本）。

## 目录结构

```
flow/initialize/SAMSUNG/S8/common/cmds/pv_calibre/
├── steps/              # 主脚本目录（当前目录）
│   └── step.tcl        # 主脚本文件（示例）
├── sub_steps/          # Sub_step proc 文件目录
└── helpers/            # 辅助代码目录
```

## 使用方式

主脚本文件可以通过以下方式组织：

1. **扁平结构**：直接在 `steps/` 目录下放置脚本文件
   - `steps/step1.tcl`
   - `steps/step2.tcl`

2. **按 step 分目录**：为每个 step 创建子目录
   - `steps/pv_calibre.step1/step1.tcl`
   - `steps/pv_calibre.step2/step2.tcl`

3. **简化结构**：只使用 step_name 作为目录名
   - `steps/step1/step1.tcl`
   - `steps/step2/step2.tcl`

## 搜索路径优先级

主脚本文件的搜索路径（从高到低）：
1. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/steps/<flow_name>.<step_name>/<script_filename>`
2. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/steps/<step_name>/<script_filename>`
3. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/steps/<script_filename>`
4. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/<script_filename>`
5. `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/steps/<flow_name>.<step_name>/<script_filename>`
6. `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/steps/<step_name>/<script_filename>`
7. `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/steps/<script_filename>`
8. `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/<script_filename>`

项目特定的文件会覆盖 common 的文件。

