# 安装指南

[← 返回目录](../TUTORIAL.md)

本指南将帮助你安装和配置 EDP_AI 框架。

## 前置要求

- **Python**: 3.7 或更高版本
- **操作系统**: Linux 或 Windows（支持 Git Bash）
- **Shell**: bash, zsh, csh 或 tcsh

## 安装步骤

### 1. 获取 EDP_AI 代码

假设你的 EDP_AI 框架路径为：
- **Linux**: `/home/user/EDP_AI/edp_center`
- **Windows**: `C:/Users/username/Desktop/EDP_AI/edp_center`

### 2. 运行安装脚本

```bash
# 1. 进入 EDP_AI 项目目录
cd /home/user/EDP_AI  # Linux
# 或
cd C:/Users/username/Desktop/EDP_AI  # Windows

# 2. 进入 edp_center/bin 目录
cd edp_center/bin

# 3. 运行安装脚本
./install.sh
```

### 3. 配置环境变量

根据你使用的 shell，选择对应的配置文件：

#### 对于 bash/zsh:

```bash
# Linux
source /home/user/EDP_AI/edp_center/bin/edp.sh

# Windows (Git Bash)
source C:/Users/username/Desktop/EDP_AI/edp_center/bin/edp.sh
```

**永久配置**（推荐）：

将以下内容添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
# EDP_AI 框架
source /home/user/EDP_AI/edp_center/bin/edp.sh
```

#### 对于 csh/tcsh:

```bash
# Linux
source /home/user/EDP_AI/edp_center/bin/edp.csh

# Windows (Git Bash)
source C:/Users/username/Desktop/EDP_AI/edp_center/bin/edp.csh
```

**永久配置**（推荐）：

将以下内容添加到 `~/.cshrc` 或 `~/.tcshrc`：

```csh
# EDP_AI 框架
source /home/user/EDP_AI/edp_center/bin/edp.csh
```

---

## 验证安装

安装完成后，验证 `edp` 命令是否可用：

```bash
# 检查 edp 命令是否可用
edp --help

# 查看可用命令
edp -h
```

如果看到帮助信息，说明安装成功！

---

## 常见安装问题

### Q: 提示 "command not found: edp"

**原因**：环境变量未正确配置

**解决方法**：
1. 检查是否正确执行了 `source edp.sh` 或 `source edp.csh`
2. 检查 `edp_center/bin` 目录是否存在
3. 检查 `edp_center/bin/edp.sh` 或 `edp_center/bin/edp.csh` 文件是否存在
4. 尝试重新打开终端窗口

### Q: Windows 下无法执行 install.sh

**原因**：Windows 默认不支持 shell 脚本

**解决方法**：
1. 使用 Git Bash 或 WSL（Windows Subsystem for Linux）
2. 或者在 Git Bash 中运行：
   ```bash
   bash edp_center/bin/install.sh
   ```

### Q: 权限错误 "Permission denied"

**解决方法**：
```bash
chmod +x edp_center/bin/install.sh
chmod +x edp_center/bin/edp.sh
chmod +x edp_center/bin/edp.csh
```

---

## 卸载

如果需要卸载 EDP_AI 框架：

1. 从 shell 配置文件中移除 `source` 语句
2. 删除 EDP_AI 项目目录（可选）

---

## 下一步

- 🚀 [快速开始你的第一个项目](02_getting_started.md)
- 📖 [了解基本使用方法](03_basic_usage.md)

[← 返回目录](../TUTORIAL.md)

