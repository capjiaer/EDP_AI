# EDP_AI Agent 指南

此文档为在 EDP_AI 代码库上工作的 AI 编程助手提供必要信息。

## 构建/测试命令

### 测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python Example/tests/run_tests.py

# 运行单个测试
pytest tests/test_module.py::test_function -v

# 运行带覆盖率的测试
pytest --cov=edp_center --cov-report=html
```

### 代码质量
```bash
# 格式化代码
black edp_center/

# 检查格式化
black --check edp_center/

# 代码检查
flake8 edp_center/

# 类型检查
mypy edp_center/
```

### 安装
```bash
# 开发模式安装
pip install -e .

# 安装开发依赖
pip install -r requirements-dev.txt
```

## 代码风格指南

### Python 标准
- 遵循 PEP 8 规范，行长度限制为 100 字符
- 使用 Black 进行自动代码格式化
- 使用 Google 风格的文档字符串
- 所有公共函数和方法都需要类型提示

### 命名约定
- 函数/变量：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有成员：`_leading_underscore`
- 保护成员：`_leading_underscore`

### 导入组织
按以下顺序分组导入，各组之间用空行分隔：
```python
# 标准库导入
import os
import sys
from pathlib import Path

# 第三方导入
import yaml
from fastapi import FastAPI

# 本地导入
from edp_center.main.workflow_manager import WorkflowManager
from .utils import helper_function
```

### 代码结构
- 一个文件一个类（简单辅助类除外）
- 私有方法和属性应该以 `_` 开头
- 使用描述性的变量名 - 优先选择清晰度而非简洁性
- 保持函数专注于单一职责

## 错误处理

项目使用来自 `edp_common` 的统一错误处理系统：

- **异常**: 使用 `edp_common.exceptions.EDPError` 及其子类
- **装饰器**:
  - `@handle_cli_error` 用于 CLI 命令（自动退出码）
  - `@handle_error` 用于普通函数
  - `@error_context` 用于代码块
- **安全调用**: 使用 `safe_call()` 函数处理可能失败的操作

参考: `docs/UNIFIED_ERROR_HANDLING.md`

## 测试指南

### 测试结构
```
tests/
├── test_module_name.py
├── fixtures/
│   └── test_data.yaml
└── __init__.py
```

### 测试编写
- 测试文件命名 `test_*.py`
- 测试函数命名 `test_*`
- 使用 pytest 框架
- 测试应该独立且隔离
- 使用 fixtures 共享测试数据
- 目标覆盖率 80%+

### 示例测试
```python
import pytest
from edp_center.packages.edp_cmdkit import CmdProcessor

def test_process_file_success(tmp_path):
    """测试成功处理文件。"""
    # Arrange
    input_file = tmp_path / "input.tcl"
    input_file.write_text("#import source helper.tcl")

    # Act
    processor = CmdProcessor()
    result = processor.process_file(input_file)

    # Assert
    assert "helper.tcl" in result
```

## 文档标准

### 代码文档
- 所有公共函数/方法必须有文档字符串
- 使用 Google 文档字符串格式
- 包含 Args、Returns、Raises 部分
- 在行内记录复杂逻辑

### 文档字符串示例
```python
def process_file(file_path: Path, options: Optional[Dict] = None) -> List[str]:
    """
    处理文件并返回结果。

    Args:
        file_path: 要处理的文件路径
        options: 可选的配置字典

    Returns:
        处理后的结果列表

    Raises:
        FileNotFoundError: 如果文件不存在
        ValueError: 如果文件格式无效

    Example:
        >>> result = process_file(Path("test.txt"))
        >>> print(result)
        ['line1', 'line2']
    """
```

### 用户文档
- 新功能需要更新 README.md
- 接口变更需要更新 `docs/api/` 中的 API 文档
- 破坏性变更需要更新迁移指南
- 保持文档与代码同步

## 项目结构

### 核心模块（共7个）

- **edp_dirkit**: 目录管理和工作空间初始化
- **edp_configkit**: 配置加载和合并（YAML ↔ Tcl 转换）
- **edp_cmdkit**: 脚本处理和 #import 展开（Hooks 和 Sub_steps）
- **edp_flowkit**: 工作流执行和依赖管理（Graph、Step、ICCommandExecutor）
- **edp_libkit**: 库配置生成工具（LibConfigGenerator、FoundryAdapter）
- **edp_common**: 公共工具（异常、日志、错误处理）
- **edp_webkit**: Web 服务和界面（FastAPI + 指标，开发中）

### 关键目录

```
edp_center/
├── bin/                    # 可执行脚本
├── config/                 # 配置文件
├── flow/                   # 流程脚本和模板
├── main/                   # 主程序和 CLI
│   ├── cli/               # 命令行接口
│   ├── workflow_manager.py
│   └── tests/             # 单元测试
├── packages/              # 7 个核心模块
│   ├── edp_dirkit/
│   ├── edp_configkit/
│   ├── edp_cmdkit/
│   ├── edp_flowkit/
│   ├── edp_libkit/        # 关键：库配置生成
│   ├── edp_common/
│   └── edp_webkit/
├── docs/                  # 文档
└── tutorial/              # 教程和示例

Example/                   # 示例配置和测试数据
```

### 重要文件

- `edp_center/main/edp.py`: 主 CLI 入口点
- `edp_center/main/setup.py`: 包配置
- `Example/tests/run_tests.py`: 集成测试运行器
- `docs/UNIFIED_ERROR_HANDLING.md`: 错误处理参考
- `CONTRIBUTING.md`: 贡献指南

## 开发工作流

### Git 工作流
- 使用 Conventional Commits 格式
- 分支命名：`feature/`、`fix/`、`docs/`、`refactor/`
- 拉取请求需要审查
- 合并前所有测试必须通过

### 提交前检查
- [ ] 代码遵循风格指南
- [ ] 所有测试通过
- [ ] 代码有适当文档
- [ ] 未提交敏感数据或密钥
- [ ] 类型检查通过
- [ ] 代码检查通过

### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型: feat, fix, docs, style, refactor, perf, test, chore

## 安全考虑

- 永远不要提交密钥、API 密钥或敏感数据
- 使用环境变量进行配置
- 验证所有用户输入
- 遵循最小权限原则
- 记录错误时不暴露敏感信息

## 性能指南

- 在优化前先进行性能分析
- 使用合适的数据结构
- 避免不必要的 I/O 操作
- 缓存昂贵的计算结果
- 考虑大数据集的内存使用

---

*此文档应随着代码库的发展而更新。最后更新: 2025-01-XX*</content>
<parameter name="filePath">/home/capjiaer/git_resource/EDP_AI/AGENTS.md