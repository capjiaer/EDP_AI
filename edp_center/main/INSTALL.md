# EDP Main 安装和使用说明

## 安装方式

### 方式 1: 创建 bin 目录（推荐，适用于 Linux 用户）

#### Bash 用户

```bash
# 1. 创建用户 bin 目录（如果不存在）
mkdir -p ~/bin

# 2. 创建符号链接到 edp.sh 和 edp.py（bash 版本）
ln -s /path/to/EDP_AI/edp_center/main/edp.sh ~/bin/edp
ln -s /path/to/EDP_AI/edp_center/main/edp.py ~/bin/edp.py

# 3. 确保 ~/bin 在 PATH 中（添加到 ~/.bashrc 或 ~/.bash_profile）
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
# 或者
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bash_profile

# 4. 重新加载配置
source ~/.bashrc
# 或者
source ~/.bash_profile
```

#### Csh/Tcsh 用户

```bash
# 1. 创建用户 bin 目录（如果不存在）
mkdir -p ~/bin

# 2. 创建符号链接到 edp.csh 和 edp.py（csh 版本）
ln -s /path/to/EDP_AI/edp_center/main/edp.csh ~/bin/edp
ln -s /path/to/EDP_AI/edp_center/main/edp.py ~/bin/edp.py

# 3. 确保 ~/bin 在 PATH 中（添加到 ~/.cshrc 或 ~/.tcshrc）
echo 'set path = ($path ~/bin)' >> ~/.cshrc
# 或者
echo 'set path = ($path ~/bin)' >> ~/.tcshrc

# 4. 重新加载配置
source ~/.cshrc
# 或者
source ~/.tcshrc
```

### 方式 2: 直接使用 Python CLI

如果已经安装了 `edp-main` CLI，可以直接使用：

```bash
edp -run pv_calibre.ipmerge
```

### 方式 3: 使用 Python 直接调用

```bash
python -m edp_center.main.cli.cli -run pv_calibre.ipmerge
```

## 使用方式

### 使用 edp.csh（csh/tcsh 用户）

```bash
# 初始化工作空间
edp -b branch1 -prj dongting -v P85 --block block1 --user zhangsan

# 执行流程/步骤
edp -run pv_calibre.ipmerge
# 或执行多个步骤
edp -run -fr pnr_innovus.place -to pv_calibre.drc
```

### 使用 edp-main（如果已安装）

```bash
edp -run pv_calibre.ipmerge
```

## 自定义 Python 路径

如果需要使用特定的 Python 解释器，可以修改 `edp.csh` 文件：

```tcsh
# 在 edp.csh 中修改这一行
set python_path=/path/to/your/python3
```

或者设置环境变量：

```bash
# 在 ~/.cshrc 或 ~/.tcshrc 中设置
setenv EDP_PYTHON_PATH /path/to/your/python3
```

然后在 `edp.csh` 中检查这个环境变量：

```tcsh
if ( $?EDP_PYTHON_PATH ) then
    set python_path=$EDP_PYTHON_PATH
else
    # 使用默认路径
    ...
endif
```

## 验证安装

```bash
# 检查 edp 命令是否可用
which edp

# 查看帮助
edp --help

# 或者
edp-main --help
```

