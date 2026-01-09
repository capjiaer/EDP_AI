# 开发指南

本文档为框架开发者提供开发环境设置、调试技巧和开发最佳实践。

## 📋 目录

- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [调试技巧](#调试技巧)
- [测试开发](#测试开发)
- [代码审查](#代码审查)
- [常见问题](#常见问题)

---

## 开发环境设置

### 前置要求

- **Python**: 3.6+
- **Git**: 2.0+
- **文本编辑器**: VS Code / PyCharm / Vim
- **操作系统**: Linux / macOS / Windows

### 环境设置步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-org/EDP_AI.git
   cd EDP_AI
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

4. **安装开发工具**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

5. **验证安装**
   ```bash
   python -m pytest tests/
   ```

### IDE 配置

#### VS Code

**推荐扩展：**
- Python
- Pylance
- Python Docstring Generator
- Markdown Preview Enhanced

**设置 (`.vscode/settings.json`):**
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true
}
```

#### PyCharm

**推荐设置：**
- 启用类型检查
- 配置代码格式化（Black）
- 配置代码检查（Flake8）
- 配置测试运行器（pytest）

---

## 项目结构

### 目录结构

```
edp_center/
├── bin/                    # 可执行脚本
├── config/                 # 配置文件
├── flow/                   # 流程脚本
├── main/                   # 主程序
│   ├── cli/               # 命令行接口
│   ├── workflow_manager.py
│   └── tests/
├── packages/              # 七个核心模块
│   ├── edp_dirkit/
│   ├── edp_configkit/
│   ├── edp_cmdkit/
│   ├── edp_flowkit/
│   ├── edp_libkit/        # 库配置生成工具
│   ├── edp_common/        # 公共工具模块
│   └── edp_webkit/        # Web服务和界面
├── tutorial/              # 教程文档
└── docs/                  # 详细文档
```

### 模块职责

- **edp_dirkit**: 目录管理和工作空间初始化
- **edp_configkit**: 配置加载和合并（YAML ↔ Tcl转换）
- **edp_cmdkit**: 脚本处理和 #import 展开（Hooks 和 Sub_steps）
- **edp_flowkit**: 工作流执行和依赖管理（Graph、Step、ICCommandExecutor）
- **edp_libkit**: 库配置生成工具（LibConfigGenerator、FoundryAdapter）
- **edp_common**: 公共工具模块（异常、日志、错误处理）
- **edp_webkit**: Web服务和界面模块（FastAPI + 指标，开发中）

---

## 调试技巧

### 1. 使用日志

**设置日志级别：**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**使用日志：**
```python
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 2. 使用调试器

**pdb 调试器：**
```python
import pdb

def my_function():
    pdb.set_trace()  # 设置断点
    # 代码执行会在这里暂停
```

**VS Code 调试：**
1. 创建 `.vscode/launch.json`
2. 设置断点
3. 按 F5 开始调试

**PyCharm 调试：**
1. 设置断点
2. 右键选择 "Debug"
3. 使用调试工具栏

### 3. 打印调试

**使用 print：**
```python
print(f"Variable value: {variable}")
print(f"Function called with: {args}")
```

**使用 repr：**
```python
print(repr(object))  # 显示对象的详细信息
```

### 4. 单元测试调试

**运行单个测试：**
```bash
pytest tests/test_module.py::test_function -v
```

**使用 pytest 调试：**
```bash
pytest --pdb  # 失败时进入调试器
pytest -s     # 显示 print 输出
```

### 5. 性能分析

**使用 cProfile：**
```python
import cProfile
cProfile.run('my_function()')
```

**使用 timeit：**
```python
import timeit
timeit.timeit('my_function()', number=1000)
```

---

## 测试开发

### 测试结构

```
tests/
├── test_module_name.py
├── test_another_module.py
└── fixtures/
    └── test_data.yaml
```

### 编写测试

**基本测试：**
```python
import pytest
from edp_center.packages.edp_cmdkit import CmdProcessor

def test_process_file_success(tmp_path):
    """测试成功处理文件"""
    # 准备测试数据
    input_file = tmp_path / "input.tcl"
    input_file.write_text("#import source helper.tcl")
    
    # 执行测试
    processor = CmdProcessor()
    result = processor.process_file(input_file)
    
    # 验证结果
    assert "helper.tcl" in result
```

**使用 Fixtures：**
```python
@pytest.fixture
def sample_config():
    return {
        "project": {
            "name": "test_project",
            "version": "P85"
        }
    }

def test_config_loading(sample_config):
    # 使用 fixture
    assert sample_config["project"]["name"] == "test_project"
```

**参数化测试：**
```python
@pytest.mark.parametrize("input,expected", [
    ("file1.tcl", True),
    ("file2.tcl", False),
])
def test_file_validation(input, expected):
    assert validate_file(input) == expected
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_module.py

# 运行特定测试函数
pytest tests/test_module.py::test_function

# 生成覆盖率报告
pytest --cov=edp_center --cov-report=html
```

---

## 代码审查

### 提交前检查

- [ ] 代码遵循代码风格规范
- [ ] 所有测试通过
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息遵循规范

### 代码审查清单

**功能：**
- [ ] 功能实现正确
- [ ] 边界情况已处理
- [ ] 错误处理完善

**代码质量：**
- [ ] 代码清晰易读
- [ ] 命名规范
- [ ] 注释充分

**测试：**
- [ ] 测试覆盖充分
- [ ] 测试独立
- [ ] 测试可维护

**文档：**
- [ ] 文档字符串完整
- [ ] 用户文档已更新
- [ ] API 文档已更新

---

## 常见问题

### Q1: 导入错误

**问题：**
```python
ImportError: No module named 'edp_center'
```

**解决方案：**
```bash
# 安装开发模式
pip install -e .

# 或添加到 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/EDP_AI"
```

### Q2: 测试失败

**问题：**
```
AssertionError: ...
```

**解决方案：**
1. 检查测试数据
2. 检查测试环境
3. 使用调试器定位问题

### Q3: 类型检查错误

**问题：**
```
mypy: error: ...
```

**解决方案：**
1. 添加类型提示
2. 使用 `# type: ignore` 注释（谨慎使用）
3. 更新类型定义

### Q4: 代码格式化问题

**问题：**
```
black: would reformat ...
```

**解决方案：**
```bash
# 自动格式化
black edp_center/

# 检查格式
black --check edp_center/
```

---

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/new-feature
```

### 2. 开发功能

- 编写代码
- 编写测试
- 更新文档

### 3. 提交更改

```bash
git add .
git commit -m "feat: add new feature"
```

### 4. 推送分支

```bash
git push origin feature/new-feature
```

### 5. 创建 Pull Request

- 填写 PR 描述
- 链接相关 issue
- 等待代码审查

### 6. 响应审查反馈

- 及时响应
- 根据反馈修改
- 重新提交

---

## 最佳实践

### 1. 代码组织

- **单一职责**：每个函数/类只做一件事
- **DRY 原则**：不要重复代码
- **KISS 原则**：保持简单

### 2. 错误处理

- **使用异常**：不要返回错误码
- **提供上下文**：错误消息要清晰
- **记录日志**：记录错误信息

### 3. 文档

- **文档字符串**：所有公共函数都要有
- **类型提示**：使用类型注解
- **注释**：解释"为什么"而不是"是什么"

### 4. 测试

- **测试驱动**：先写测试再写代码
- **测试覆盖**：目标覆盖率 80%+
- **测试独立**：每个测试应该独立

---

## 获取帮助

### 文档资源

- [贡献指南](../../CONTRIBUTING.md)
- [API 文档](../api/)
- [架构文档](../architecture/)

### 社区支持

- GitHub Issues
- GitHub Discussions

---

**最后更新**: 2025-01-XX

