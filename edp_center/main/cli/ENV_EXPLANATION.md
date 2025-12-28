# EDP 环境问题说明

## 问题描述

在测试过程中，直接运行 `python -m edp_center.main.cli.cli` 时出现以下错误：

```
ModuleNotFoundError: No module named 'edp_center'
```

## 原因分析

### 1. Python 模块搜索路径（sys.path）

Python 在导入模块时，会按照以下顺序搜索：
1. 当前脚本所在目录
2. `PYTHONPATH` 环境变量中的路径
3. Python 标准库路径
4. site-packages 目录

### 2. 问题场景

当我们在 `edp_center` 目录下运行：
```bash
cd edp_center
python -m edp_center.main.cli.cli --help
```

Python 会：
1. 将 `edp_center` 目录作为当前工作目录添加到 `sys.path`
2. 尝试导入 `edp_center.main.cli.cli`
3. 但是 `edp_center` 目录本身**不是** `edp_center` 模块，真正的 `edp_center` 模块在**项目根目录**下

### 3. 正确的路径结构

```
EDP_AI/                    # 项目根目录（需要添加到 sys.path）
├── edp_center/            # edp_center 模块
│   ├── __init__.py
│   ├── main/
│   │   └── cli/
│   │       └── cli.py
│   └── bin/
│       └── edp.py         # 入口脚本，会设置正确的路径
```

## 解决方案

### 方案 1：使用正确的入口脚本（推荐）

使用项目提供的入口脚本，它会自动设置正确的路径：

```bash
# 从项目根目录运行
cd /path/to/EDP_AI
python edp_center/bin/edp.py --help

# 或者如果已经设置了 PATH
edp --help
```

`edp_center/bin/edp.py` 中的关键代码：
```python
# Add project root to path
project_root = Path(__file__).parent.parent.parent  # 从 bin/edp.py 向上三级到项目根目录
sys.path.insert(0, str(project_root))  # 将项目根目录添加到 Python 路径
```

### 方案 2：手动设置 PYTHONPATH

```bash
# Linux/Mac
export PYTHONPATH=/path/to/EDP_AI:$PYTHONPATH
python -m edp_center.main.cli.cli --help

# Windows
set PYTHONPATH=C:\path\to\EDP_AI;%PYTHONPATH%
python -m edp_center.main.cli.cli --help
```

### 方案 3：从项目根目录运行

```bash
# 从项目根目录运行
cd /path/to/EDP_AI
python -m edp_center.main.cli.cli --help
```

### 方案 4：在代码中动态添加路径

```python
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent  # 根据实际位置调整
sys.path.insert(0, str(project_root))

from edp_center.main.cli.cli import main
```

## 为什么测试脚本能工作？

在测试脚本 `test_aliases.py` 中，我们使用了方案 4：

```python
# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from edp_center.main.cli.arg_parser import create_parser
```

这样就能正确导入 `edp_center` 模块了。

## 实际使用建议

1. **开发环境**：使用 `edp_center/bin/edp.py` 或设置 `PYTHONPATH`
2. **生产环境**：使用安装后的 `edp` 命令（通过 `edp_env.sh` 或 `edp_env.csh` 设置环境）
3. **测试**：在测试脚本中动态添加路径，或使用 pytest 的 `PYTHONPATH` 配置

## 相关文件

- `edp_center/bin/edp.py`：主入口脚本，包含路径设置逻辑
- `edp_center/bin/edp_env.sh`：Bash 环境设置脚本
- `edp_center/bin/edp_env.csh`：Csh 环境设置脚本

