# EDP Bin 目录

这个目录用于存放可执行脚本的符号链接。

## 📚 文档

- **[完整教程 (TUTORIAL.md)](../TUTORIAL.md)** - 从入门到精通的完整指南（**推荐新用户阅读**）
- [快速开始 (QUICK_START.md)](QUICK_START.md) - 快速上手指南
- [安装指南 (../main/INSTALL.md)](../main/INSTALL.md) - 详细的安装和配置说明

## 快速开始：让用户直接使用 `edp` 命令

### 方式 1: 将当前 bin 目录添加到 PATH（推荐）

```bash
# 1. 进入 bin 目录
cd /path/to/EDP_AI/edp_center/bin

# 2. 运行自动设置脚本
./setup_path.sh

# 3. 重新加载配置
source ~/.bashrc
# 或者重新打开终端

# 4. 现在可以在任何地方使用 edp 命令
edp --help
edp run --work-path WORK_PATH ...
```

### 方式 2: 手动添加到 PATH

#### Bash 用户

```bash
# 1. 获取 bin 目录的绝对路径
cd /path/to/EDP_AI/edp_center/bin
BIN_DIR=$(pwd)

# 2. 添加到 ~/.bashrc
echo "" >> ~/.bashrc
echo "# EDP Main - Add bin directory to PATH" >> ~/.bashrc
echo "export PATH=\"\$PATH:$BIN_DIR\"" >> ~/.bashrc

# 3. 重新加载配置
source ~/.bashrc

# 4. 现在可以在任何地方使用
edp --help
```

#### Csh/Tcsh 用户

**方式 A: 使用 edp_env.csh（推荐）**

```tcsh
# 1. 进入 bin 目录
cd /path/to/EDP_AI/edp_center/bin

# 2. source 环境设置脚本（会自动设置 PATH 和补全）
source ./edp_env.csh

# 3. 现在可以使用 edp 命令
edp --help

# 4. 永久设置：添加到 ~/.cshrc 或 ~/.tcshrc
echo "" >> ~/.cshrc
echo "# EDP Main - Environment setup" >> ~/.cshrc
echo "source /path/to/EDP_AI/edp_center/bin/edp_env.csh" >> ~/.cshrc
source ~/.cshrc
```

**方式 B: 手动设置 PATH**

```tcsh
# 1. 获取 bin 目录的绝对路径
cd /path/to/EDP_AI/edp_center/bin
set BIN_DIR = `pwd`

# 2. 添加到 ~/.cshrc
echo "" >> ~/.cshrc
echo "# EDP Main - Add bin directory to PATH" >> ~/.cshrc
echo "set path = (\$path $BIN_DIR)" >> ~/.cshrc

# 3. 重新加载配置
source ~/.cshrc

# 4. 现在可以在任何地方使用
edp --help
```

### 方式 3: 使用完整路径（临时）

如果不想修改 PATH，可以使用完整路径：

```bash
/path/to/EDP_AI/edp_center/bin/edp run --work-path WORK_PATH ...
```

### 方式 2: 使用用户主目录的 bin（推荐）

推荐在用户主目录创建 `~/bin` 目录，这样可以在任何地方使用 `edp` 命令：

#### Bash 用户

```bash
# 创建用户 bin 目录
mkdir -p ~/bin

# 创建符号链接（bash 版本）
ln -s /path/to/EDP_AI/edp_center/main/edp.sh ~/bin/edp
ln -s /path/to/EDP_AI/edp_center/main/edp.py ~/bin/edp.py

# 确保 ~/bin 在 PATH 中（添加到 ~/.bashrc 或 ~/.bash_profile）
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 现在可以在任何地方使用
edp run --work-path WORK_PATH ...
```

#### Csh/Tcsh 用户

```bash
# 创建用户 bin 目录
mkdir -p ~/bin

# 创建符号链接（csh 版本）
ln -s /path/to/EDP_AI/edp_center/main/edp.csh ~/bin/edp
ln -s /path/to/EDP_AI/edp_center/main/edp.py ~/bin/edp.py

# 确保 ~/bin 在 PATH 中（添加到 ~/.cshrc 或 ~/.tcshrc）
echo 'set path = ($path ~/bin)' >> ~/.cshrc
source ~/.cshrc

# 现在可以在任何地方使用
edp run --work-path WORK_PATH ...
```

## 符号链接创建

### 自动安装（推荐）

```bash
# 运行安装脚本
cd /path/to/EDP_AI/edp_center/bin

# Bash/Zsh 用户
source ./install.sh
# 或
./install.sh

# Csh/Tcsh 用户
source ./install.csh
```

**注意**：如果没有 `install.csh`，csh/tcsh 用户可以直接使用 `edp_env.csh`：

```tcsh
# 方式 1: 临时使用（当前 shell）
cd /path/to/EDP_AI/edp_center/bin
source ./edp_env.csh
edp --help

# 方式 2: 永久设置（添加到 ~/.cshrc）
echo "" >> ~/.cshrc
echo "# EDP Main - Environment setup" >> ~/.cshrc
echo "source /path/to/EDP_AI/edp_center/bin/edp_env.csh" >> ~/.cshrc
source ~/.cshrc
```

### 手动创建

#### Bash 用户

```bash
# 在项目 bin 目录中创建符号链接
cd /path/to/EDP_AI/edp_center/bin
ln -s ../main/edp.sh edp
ln -s ../main/edp.py edp.py
```

#### Csh/Tcsh 用户

```bash
# 在项目 bin 目录中创建符号链接
cd /path/to/EDP_AI/edp_center/bin
ln -s ../main/edp.csh edp
ln -s ../main/edp.py edp.py
```

