# Helpers 目录说明

此目录用于存放可复用的辅助代码文件，通过 `#import source` 指令在主脚本中按需导入。

## 目录结构

```
flow/initialize/SAMSUNG/S8/common/cmds/tech_init/
├── steps/              # 主脚本目录
├── sub_steps/          # Sub_step proc 文件目录
└── helpers/            # 辅助代码目录（当前目录）
    └── helper.tcl      # 普通辅助文件（通过 #import source 使用）
```

## 使用方式

通过 `#import source <file>` 在主脚本中按需导入，加载 proc 定义文件。

**示例**：
```tcl
# 在主脚本中
#import source helper.tcl
# 然后可以直接调用 helper.tcl 中定义的 proc
```

## 搜索路径优先级

Helpers 文件的搜索路径（从高到低）：
1. `flow/initialize/<FOUNDRY>/<NODE>/<PROJECT>/cmds/<flow_name>/helpers/`
2. `flow/initialize/<FOUNDRY>/<NODE>/common/cmds/<flow_name>/helpers/`

项目特定的文件会覆盖 common 的文件。

## 注意事项

- Helpers 文件中的 `#import source` 指令会被递归处理
- Helpers 文件应该包含可复用的 proc 定义或工具函数
- 与 `sub_steps/` 的区别：`helpers/` 中的文件需要手动通过 `#import source` 导入，而 `sub_steps/` 中的文件通过 `dependency.yaml` 自动加载

