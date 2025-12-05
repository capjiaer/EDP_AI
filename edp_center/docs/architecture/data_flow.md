# EDP_AI 框架数据流文档

## 📋 文档信息

- **版本**: 1.0
- **最后更新**: 2025-01-XX
- **维护者**: EDP 框架团队

本文档详细说明 EDP_AI 框架中的数据流，包括配置、脚本、依赖关系等数据的流转过程。

---

## 1. 整体数据流

### 1.1 工作流执行数据流

```
用户输入（CLI/GUI）
    ↓
参数推断（project, version, block, user, branch, flow, step）
    ↓
工作空间初始化（edp_dirkit）
    ├── 创建目录结构
    └── 初始化分支
    ↓
配置加载（edp_configkit）
    ├── 加载多层级配置（common → project → user）
    ├── 合并配置
    └── 生成 full.tcl
    ↓
依赖图构建（edp_flowkit）
    ├── 读取 dependency.yaml
    └── 构建依赖图（Graph）
    ↓
脚本处理（edp_cmdkit）
    ├── 整合 Hooks
    ├── 处理 #import source
    ├── 处理 Sub_steps
    └── 生成最终脚本
    ↓
步骤执行（edp_flowkit）
    ├── 按依赖顺序执行
    ├── 更新步骤状态
    └── 记录执行结果
    ↓
完成
```

---

## 2. 配置数据流

### 2.1 配置加载流程

```
配置文件（YAML/Tcl）
    ├── common/main/init_project.yaml
    ├── common/main/config.yaml
    ├── common/{flow_name}/config.yaml
    ├── {project}/main/init_project.yaml
    ├── {project}/main/config.yaml
    ├── {project}/{flow_name}/config.yaml
    └── user_config.yaml 或 user_config.tcl
    ↓
edp_configkit 加载
    ├── 按优先级顺序加载
    ├── YAML → Tcl 转换（如需要）
    └── 合并配置（后加载覆盖先加载）
    ↓
full.tcl（合并后的配置）
    ├── 配置文件变量
    └── 自动生成的变量（project, edp）
    ↓
edp_cmdkit 处理脚本时 source
    ↓
最终执行的 Tcl 脚本（包含所有配置）
```

### 2.2 配置变量生成

```
项目信息（project, version, block, user, branch）
    ↓
自动生成 project 变量
    ├── project(project_name)
    ├── project(version)
    ├── project(block_name)
    ├── project(user_name)
    ├── project(branch_name)
    ├── project(foundry)
    ├── project(node)
    ├── project(init_path)
    ├── project(work_path)
    ├── project(flow_name)
    └── project(step_name)
    ↓
自动生成 edp 变量
    ├── edp(edp_center_path)
    ├── edp(config_path)
    ├── edp(flow_path)
    └── edp(execution_plan,{step_name})
    ↓
写入 full.tcl
```

---

## 3. 脚本数据流

### 3.1 脚本处理流程

```
主脚本（steps/{flow_name}/{step_name}.tcl）
    ↓
整合 Hooks
    ├── step.pre（如果存在）
    ├── 主脚本内容
    └── step.post（如果存在）
    ↓
处理 #import source 指令
    ├── 查找文件（使用 file_finder，带缓存）
    ├── 递归处理嵌套的 #import
    └── 转换为 source 语句
    ↓
处理 Sub_steps
    ├── 读取 dependency.yaml
    ├── 查找 sub_step 文件
    ├── 处理 sub_step 中的 #import source
    ├── 处理 sub_step hooks（pre/post/replace）
    ├── 生成 proc 定义（添加到脚本开头）
    └── 生成 proc 调用（添加到主脚本后）
    ↓
添加默认 source 语句
    ├── source packages（edp_center 包）
    ├── source full.tcl（配置）
    └── namespace eval（如需要）
    ↓
Debug 模式处理（可选）
    ├── 移除直接调用
    ├── 添加 edp_run 初始化
    └── 添加执行计划
    ↓
最终脚本（runs/{flow_name}/{step_name}/{step_name}.tcl）
```

### 3.2 Sub_steps 处理详细流程

```
dependency.yaml
    ├── 读取 sub_steps 定义
    └── 解析文件映射（file_name → proc_name）
    ↓
对每个 sub_step:
    ├── 查找文件（sub_steps/{file_name}.tcl）
    ├── 读取文件内容
    ├── 处理文件中的 #import source
    ├── 处理 hooks（{file_name}.pre/post/replace）
    ├── 确保 global 声明
    ├── 添加文件路径注释
    └── 生成 proc 定义
    ↓
所有 proc 定义（添加到脚本开头）
    ↓
所有 proc 调用（添加到主脚本后）
```

---

## 4. 依赖关系数据流

### 4.1 依赖图构建流程

```
dependency.yaml（每个 flow）
    ├── 定义 steps
    ├── 定义 sub_steps（每个 step）
    └── 定义依赖关系（depends_on）
    ↓
edp_flowkit 解析
    ├── 解析 steps
    ├── 解析 sub_steps
    └── 解析依赖关系
    ↓
构建依赖图（Graph）
    ├── 节点（Step）
    ├── 边（依赖关系）
    └── 拓扑排序
    ↓
执行计划
    ├── 步骤执行顺序
    └── 并发执行组
    ↓
步骤执行
    ├── 检查依赖是否完成
    ├── 执行步骤
    └── 更新状态
```

### 4.2 跨 Flow 依赖

```
多个 dependency.yaml（不同 flow）
    ├── pnr_innovus/dependency.yaml
    ├── pv_calibre/dependency.yaml
    └── sta_pt/dependency.yaml
    ↓
edp_flowkit 加载所有
    ├── 解析每个 flow 的依赖
    └── 通过文件匹配建立跨 flow 依赖
    ↓
统一依赖图
    ├── 包含所有 flow 的步骤
    └── 包含跨 flow 依赖关系
    ↓
执行计划（考虑跨 flow 依赖）
```

---

## 5. Hooks 数据流

### 5.1 Step Hooks 流程

```
hooks/{flow_name}.{step_name}/
    ├── step.pre（可选）
    └── step.post（可选）
    ↓
edp_cmdkit 读取
    ├── 检查文件是否存在且非空
    └── 读取文件内容
    ↓
自动封装为 proc
    ├── step.pre → proc step_pre_hook
    └── step.post → proc step_post_hook
    ↓
插入到主脚本
    ├── step.pre 在主脚本前
    └── step.post 在主脚本后
```

### 5.2 Sub_step Hooks 流程

```
hooks/{flow_name}.{step_name}/
    ├── {file_name}.pre（可选）
    ├── {file_name}.post（可选）
    └── {file_name}.replace（可选）
    ↓
edp_cmdkit 读取
    ├── 检查文件是否存在且非空
    └── 读取文件内容
    ↓
处理方式
    ├── .pre → 在 sub_step proc 开头插入
    ├── .post → 在 sub_step proc 结尾插入
    └── .replace → 替换整个 sub_step proc
    ↓
生成最终的 sub_step proc
```

---

## 6. 执行数据流

### 6.1 步骤执行流程

```
执行计划（edp_flowkit）
    ├── 步骤列表（按依赖顺序）
    └── 并发执行组
    ↓
对每个步骤:
    ├── 检查依赖是否完成
    ├── 检查步骤是否 ready（源脚本存在）
    ├── 生成脚本（edp_cmdkit）
    ├── 执行脚本（ICCommandExecutor）
    │   ├── 本地执行（subprocess）
    │   └── LSF 执行（bsub）
    ├── 更新步骤状态
    └── 记录执行结果
    ↓
完成或失败
```

### 6.2 Debug 模式执行流程

```
Debug 模式脚本
    ├── 所有 proc 定义（在开头）
    ├── source full.tcl
    └── edp_run 初始化
    ↓
tclsh 交互式执行
    ├── 用户输入 edp_run -next
    ├── 执行下一个步骤（step.pre → sub_steps → step.post）
    ├── 显示执行结果
    └── 等待下一个命令
    ↓
用户可以:
    ├── 跳过步骤（edp_run -skip）
    ├── 重试步骤（edp_run -retry）
    └── 查看状态（edp_run -status）
```

---

## 7. 文件搜索数据流

### 7.1 文件查找流程（带缓存）

```
#import source {file_name}
    ↓
file_finder.find_file()
    ├── 检查缓存
    │   ├── 缓存命中 → 返回缓存结果
    │   └── 缓存失效 → 继续搜索
    ├── 检查绝对路径
    ├── 检查相对当前文件的路径
    └── 在搜索路径中查找
        ├── 直接查找
        └── 递归查找（rglob，性能瓶颈）
    ↓
找到文件 → 缓存结果
    ├── 记录文件路径
    └── 记录目录时间戳
    ↓
返回文件路径
```

### 7.2 缓存失效机制

```
目录修改
    ↓
目录时间戳变化
    ↓
缓存检查
    ├── 比较当前时间戳和缓存时间戳
    └── 不一致 → 缓存失效
    ↓
重新搜索
    ↓
更新缓存
```

---

## 8. 日志数据流

### 8.1 日志记录流程

```
执行步骤
    ↓
ICCommandExecutor
    ├── 创建日志文件（logs/{flow_name}.{step_name}/{step_name}.log）
    ├── 重定向 stdout/stderr
    └── 记录执行信息
    ↓
步骤完成/失败
    ├── 记录执行结果
    ├── 记录执行时间
    └── 更新 .run_info
    ↓
日志文件
    ├── 包含完整执行输出
    └── 可用于问题排查
```

### 8.2 结构化日志

```
异常发生
    ↓
EDPError（包含 context 和 suggestion）
    ↓
log_exception()
    ├── 提取异常信息
    ├── 转换为字典格式
    └── 记录到日志
    ↓
日志文件
    ├── 错误消息
    ├── 上下文信息
    ├── 解决建议
    └── 堆栈跟踪
```

---

## 9. 状态管理数据流

### 9.1 步骤状态流转

```
INIT（初始状态）
    ↓
检查依赖和 ready 状态
    ├── 依赖未完成 → PENDING（等待）
    └── 依赖完成且 ready → READY（就绪）
    ↓
READY
    ↓
开始执行
    ↓
RUNNING（执行中）
    ↓
执行完成
    ├── 成功 → SUCCESS（成功）
    └── 失败 → FAILED（失败）
    ↓
状态更新
    ├── 更新 Graph 中的 Step 状态
    └── 触发依赖步骤的状态检查
```

### 9.2 状态持久化

```
步骤状态变更
    ↓
更新 Graph 中的 Step 对象
    ↓
（可选）持久化到文件
    ├── .run_info（运行信息）
    └── 状态文件（如需要）
    ↓
Web GUI 查询
    ├── 读取当前状态
    └── 更新 UI 显示
```

---

## 10. 数据流图总结

### 10.1 关键数据流

1. **配置流**: 配置文件 → 合并 → full.tcl → 脚本
2. **脚本流**: 主脚本 + Hooks → 处理 → 最终脚本
3. **依赖流**: dependency.yaml → 依赖图 → 执行计划
4. **执行流**: 执行计划 → 步骤执行 → 状态更新
5. **日志流**: 执行输出 → 日志文件 → 问题排查

### 10.2 数据流特点

- **单向流动**: 数据流基本是单向的，减少复杂性
- **阶段明确**: 每个阶段处理特定的数据
- **可追踪**: 每个数据转换都可以追踪
- **可调试**: 中间结果可以保存和检查

---

## 11. 相关文档

- [架构设计文档](architecture_overview.md)
- [设计决策文档](design_decisions.md)
- [模块依赖关系文档](module_dependencies.md)

---

**文档维护**: 每次数据流变更后，应更新此文档。

