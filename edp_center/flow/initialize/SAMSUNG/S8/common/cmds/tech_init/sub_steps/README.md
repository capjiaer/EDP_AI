# Sub_steps 目录说明

此目录用于存放 Sub_step proc 文件，这些文件通过 `dependency.yaml` 配置自动加载。

## 目录结构

```
flow/initialize/SAMSUNG/S8/common/cmds/tech_init/
├── steps/              # 主脚本目录
├── sub_steps/          # Sub_step proc 文件目录（当前目录）
│   └── ...             # Sub_step 文件
└── helpers/            # 辅助代码目录
```

## 使用方式

Sub steps 是封装成 proc 的子步骤，通过 `dependency.yaml` 配置自动加载。

**在 dependency.yaml 中声明（字典格式）**：
```yaml
tech_init:
  dependency:
    FP_MODE:
      - step1:
          sub_steps:
            tech_init_sub_step1.tcl: tech_init::sub_step1
            tech_init_sub_step2.tcl: tech_init::sub_step2
```

**格式说明**：
- Key：文件名（如 `tech_init_sub_step1.tcl`），可以是任意文件名
- Value：proc 名称（如 `tech_init::sub_step1`，使用 Tcl namespace 语法）

**重要说明**：
- 文件名和 proc 名称之间**没有强制对应关系**
- 只要该文件中定义了对应的 proc 即可

**Proc 定义格式**：
使用 `proc ::namespace::proc_name {} { ... }` 格式直接定义，例如：
```tcl
# tech_init_sub_step1.tcl
proc ::tech_init::sub_step1 {} {
    global edp project tech_init
    
    puts "Executing sub_step1..."
    # 具体逻辑
}
```

**自动展开内容**：
框架会自动在生成的 cmd 文件中展开 sub_steps 文件内容（包括处理其中的 `#import source` 指令），所有 sub_step proc 定义会放在最终脚本的开头。

**在主脚本中使用**：
```tcl
# 直接调用 proc（已经通过自动展开加载）
tech_init::sub_step1
tech_init::sub_step2
```

## 搜索路径优先级

Sub_steps 文件的搜索路径（从高到低）：
1. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/sub_steps/`
2. `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/sub_steps/`

项目特定的文件会覆盖 common 的文件。

## 注意事项

- Sub_steps 文件支持 `#import source` 指令，框架会自动递归处理
- 与 `helpers/` 的区别：`sub_steps/` 中的文件通过 `dependency.yaml` 自动加载，而 `helpers/` 中的文件需要手动通过 `#import source` 导入

