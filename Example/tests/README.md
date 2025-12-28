# 集成测试和端到端测试

## 测试结构

```
Example/tests/
├── test_integration.py          # 核心功能集成测试
├── test_e2e_commands.py         # 端到端命令测试（history, stats 等）
├── test_init_commands.py        # 初始化相关命令测试（init, create_project, branch）
├── test_run_commands.py         # 运行相关命令测试（run, run_range）
├── test_info_commands.py        # 信息查询命令测试（info, history, stats, rollback）
├── test_other_commands.py       # 其他命令测试（tutorial, graph, release）
├── test_full_workflow.py        # 完整工作流测试（init -> branch -> run）
├── run_tests.py                 # 测试运行脚本
└── README.md                    # 本文件
```

## 测试分类

### 1. 初始化命令测试 (`test_init_commands.py`)
测试基础初始化功能：
- `edp_init -init` - 初始化项目环境
- `edp_init -create-project` - 创建新项目
- `edp -b/-branch` - 创建分支

### 2. 运行命令测试 (`test_run_commands.py`)
测试运行相关功能：
- `edp -run <flow.step>` - 运行单个步骤
- `edp -run --from/--to` - 运行步骤范围
- `--dry-run` 模式测试

### 3. 信息查询命令测试 (`test_info_commands.py`)
测试查询相关功能：
- `edp_info` / `edp_info <flow>` - 查看 flow 信息
- `edp_info -history` - 查看运行历史
- `edp_info -stats` - 性能统计
- `edp_info -rollback` - 回滚功能

### 4. 其他命令测试 (`test_other_commands.py`)
测试其他功能：
- `edp_info -tutorial` - 教程查看
- `edp_info -graph` - 流程图生成
- `edp_info -release` - Release 管理

### 5. 集成测试 (`test_integration.py`)
测试核心功能的集成：
- WorkflowManager 创建和管理
- 项目路径查找
- 运行历史加载
- 统计计算

### 6. 端到端测试 (`test_e2e_commands.py`)
测试完整的命令执行流程：
- `-history` 命令的完整流程
- `-stats` 命令的完整流程
- 导出功能（JSON/CSV）
- 错误处理场景

### 7. 完整工作流测试 (`test_full_workflow.py`)
测试完整的工作流流程：
- `init` - 初始化项目
- `branch` - 创建分支
- 创建假的 flow（pv_calibre.drc）
- `run` - 运行 flow（本地模式，非 LSF）
- 验证本地执行模式（lsf: 0）

## 运行测试

### 使用测试脚本（推荐）

```bash
# 运行所有测试
cd EDP_AI
python Example/tests/run_tests.py

# 运行特定测试文件
python Example/tests/run_tests.py test_init_commands
```

### 使用 unittest

```bash
# 运行所有测试
cd EDP_AI
python -m unittest discover Example/tests/ -v

# 运行特定测试文件
python -m unittest Example.tests.test_init_commands -v
python -m unittest Example.tests.test_run_commands -v
python -m unittest Example.tests.test_info_commands -v
```

### 使用 pytest（如果已安装）

```bash
# 运行所有测试
cd EDP_AI
pytest Example/tests/ -v

# 运行特定测试文件
pytest Example/tests/test_init_commands.py -v
```

## 测试数据

测试使用 `Example/WORK_PATH/` 目录下的真实项目数据：
- `dongting/P85/block1/user1/main/` - 主项目路径
- `dongting/P85/block1/user1/main/runs/` - 运行历史数据
- `dongting/P85/block1/user1/main/user_config.yaml` - 配置文件

## 测试覆盖范围

### ✅ 已覆盖的功能

1. **初始化命令**
   - ✅ 项目初始化
   - ✅ 创建项目
   - ✅ 创建分支
   - ✅ 错误处理

2. **运行命令**
   - ✅ 单步运行
   - ✅ 范围运行
   - ✅ Dry-run 模式
   - ✅ 错误处理

3. **信息查询命令**
   - ✅ Flow 信息查看
   - ✅ 运行历史查询
   - ✅ 性能统计
   - ✅ 回滚功能

4. **其他命令**
   - ✅ 教程查看
   - ✅ 流程图生成
   - ✅ Release 管理

5. **集成测试**
   - ✅ Manager 创建
   - ✅ 路径查找
   - ✅ 历史加载
   - ✅ 统计计算

6. **端到端测试**
   - ✅ History 命令完整流程
   - ✅ Stats 命令完整流程
   - ✅ 导出功能（JSON/CSV）
   - ✅ 错误场景处理

### 🔄 待扩展的测试

1. **边界条件测试**
   - 大量数据的性能测试
   - 异常数据格式处理
   - 并发执行测试

2. **更多端到端场景**
   - `-run` 命令的完整执行流程
   - `-rollback` 命令的实际回滚操作
   - `-info` 命令的各种参数组合

3. **性能测试**
   - 大型项目的文件搜索性能
   - 缓存机制的有效性验证
   - 内存使用情况

## 注意事项

1. **不修改真实数据**：测试应该只读取数据，不修改 Example 目录下的文件
2. **使用临时目录**：需要修改数据的测试应该使用临时目录
3. **清理资源**：测试后清理临时文件和目录
4. **跳过不存在的路径**：如果测试数据不存在，测试会优雅地跳过（skipTest）

## 测试统计

当前测试状态：
- **总测试数**: 31（包括完整工作流测试）
- **通过**: 30
- **跳过**: 1（当测试数据不存在时）
- **失败**: 0

运行 `python Example/tests/run_tests.py` 查看详细测试结果。

## 本地执行模式（非 LSF）

框架支持两种执行模式：

1. **本地执行**（`lsf: 0`）：直接在本地运行命令
2. **LSF 提交**（`lsf: 1`）：通过 `bsub` 提交到 LSF 集群

### 配置本地执行模式

在配置文件中设置：

```yaml
pv_calibre:
  drc:
    lsf: 0  # 本地执行，非 LSF
    tool_opt: "bash"
```

### 测试本地执行模式

`test_full_workflow.py` 中的 `test_local_execution_mode` 测试验证了本地执行模式的配置。
