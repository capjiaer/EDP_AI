# EDP AI GUI 模块

## 概述

本模块提供基于 PyQt5 的图形界面，用于项目初始化配置，无需手动编辑配置文件。

## 功能特性

- **图形化配置界面**：通过 GUI 配置所有初始化参数
- **路径选择**：支持浏览选择 EDP Center 路径和 Work Path 路径
- **自动推断**：支持从配置文件或 `.edp_version` 文件自动推断参数
- **实时日志**：显示初始化过程的实时日志
- **异步执行**：使用工作线程执行初始化，避免阻塞 GUI

## 使用方法

### 命令行启动

```bash
# 启动 GUI 进行初始化配置
edp -init --gui

# 指定 EDP Center 路径
edp -init --gui --edp-center /path/to/edp_center
```

### 直接运行

```python
from edp_center.main.cli.gui import run_gui

# 启动 GUI
run_gui()

# 或指定 EDP Center 路径
from pathlib import Path
run_gui(Path("/path/to/edp_center"))
```

## 界面说明

### 路径配置
- **EDP Center 路径**：EDP Center 资源库的路径
- **Work Path 路径**：工作路径，将在此路径下初始化项目

### 项目配置
- **项目名称**：项目名称（如 `dongting`）
- **项目版本**：项目版本（如 `P85`, `P90`）
- **代工厂**：代工厂名称（可选，留空将自动推断）
- **工艺节点**：工艺节点（可选，留空将自动推断）

### Block 和 User 配置
- **Block 名称**：块名称（如 `block1`, `block2`），多个用逗号分隔
- **User 名称**：用户名（如 `user1`, `user2`），多个用逗号分隔，留空使用当前用户

### 功能按钮
- **从配置文件加载**：从 `config.yaml` 文件加载配置参数
- **自动推断参数**：从当前目录或 `.edp_version` 文件自动推断参数
- **开始初始化**：开始执行初始化操作
- **取消**：关闭 GUI 窗口

## 依赖要求

```bash
pip install PyQt5
```

## 注意事项

1. GUI 模式需要安装 PyQt5，如果未安装会自动提示
2. 初始化过程在后台线程执行，不会阻塞界面
3. 所有初始化日志会实时显示在日志区域
4. 初始化完成后会显示成功或失败的消息框

