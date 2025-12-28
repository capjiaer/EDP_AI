# CLI 命令测试

## 测试结构

```
tests/
├── test_helpers.py          # 测试辅助函数和工具
├── test_cli_integration.py  # CLI 集成测试（参数解析等）
├── test_cli_commands.py    # CLI 命令功能测试
├── test_file_cache.py      # 文件搜索缓存测试
└── README.md               # 本文件
```

## 测试覆盖

### ✅ 已实现的测试

1. **test_cli_integration.py** - CLI 集成测试
   - ✅ 参数解析器创建
   - ✅ edp_center 路径查找
   - ✅ WorkflowManager 创建
   - ✅ 通用参数解析（-prj, -v, --foundry, --node）
   - ✅ 命令参数解析（-run, -history, -stats, -rollback）
   - ✅ 错误处理

2. **test_cli_commands.py** - CLI 命令功能测试
   - ✅ history 命令功能（加载历史、过滤历史）
   - ✅ stats 命令功能（计算统计信息）
   - ✅ 命令辅助函数测试

3. **test_file_cache.py** - 文件搜索缓存测试
   - ✅ 缓存命中测试
   - ✅ 缓存清除测试
   - ✅ 缓存失效测试（文件变化）
   - ✅ 缓存未找到结果测试
   - ✅ 多次搜索性能测试

4. **test_helpers.py** - 测试辅助工具
   - ✅ TestArgs 类（测试参数对象）
   - ✅ TestFixture 类（测试环境 Fixture）
   - ✅ 项目结构创建函数
   - ✅ 运行信息创建函数

## 运行测试

### 使用 unittest

```bash
# 运行所有测试
python -m unittest discover edp_center/main/cli/commands/tests/ -v

# 运行特定测试文件
python -m unittest edp_center.main.cli.commands.tests.test_file_cache -v
python -m unittest edp_center.main.cli.commands.tests.test_cli_commands -v
python -m unittest edp_center.main.cli.commands.tests.test_cli_integration -v

# 运行特定测试类
python -m unittest edp_center.main.cli.commands.tests.test_file_cache.TestFileCache -v

# 运行特定测试方法
python -m unittest edp_center.main.cli.commands.tests.test_file_cache.TestFileCache.test_cache_hit -v
```

### 使用 pytest（如果已安装）

```bash
# 运行所有测试
pytest edp_center/main/cli/commands/tests/ -v

# 运行特定测试文件
pytest edp_center/main/cli/commands/tests/test_file_cache.py -v

# 运行特定测试方法
pytest edp_center/main/cli/commands/tests/test_file_cache.py::TestFileCache::test_cache_hit -v
```

## 测试工具

### TestFixture

`TestFixture` 类提供了完整的测试环境：

```python
from test_helpers import TestFixture

# 使用上下文管理器（推荐）
with TestFixture() as fixture:
    args = fixture.create_args(run='pv_calibre.ipmerge')
    manager = fixture.manager
    branch_dir = fixture.branch_dir
    # 执行测试...
    # 自动清理

# 或手动管理
fixture = TestFixture()
try:
    args = fixture.create_args()
    # 执行测试...
finally:
    fixture.cleanup()
```

### TestArgs

`TestArgs` 类用于创建测试参数对象：

```python
from test_helpers import create_test_args

args = create_test_args(
    run='pv_calibre.ipmerge',
    project='test_project',
    branch='test_branch'
)
```

## 测试最佳实践

1. **使用临时目录**：每个测试使用 `TestFixture` 创建独立的临时目录
2. **清理资源**：使用 `tearDown` 或上下文管理器清理临时文件
3. **测试独立性**：每个测试应该独立，不依赖其他测试
4. **测试边界情况**：包括路径不存在、配置缺失等情况
5. **测试错误处理**：验证异常和错误信息

## 待补充的测试

- [ ] `-run` 命令的端到端测试（需要真实的项目结构）
- [ ] `-info` 命令的端到端测试
- [ ] `-rollback` 命令的端到端测试（需要真实的运行历史）
- [ ] `-validate` 命令的端到端测试
- [ ] 错误场景的完整测试

## 测试覆盖率

当前测试覆盖率：**~30%**

目标覆盖率：**80%+**

