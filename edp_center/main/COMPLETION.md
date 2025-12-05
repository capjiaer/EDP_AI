# EDP 命令补全功能

EDP 支持 bash 命令自动补全，可以大大提升使用体验。

## 新用户快速开始

**只需要一行命令：**

```bash
# 使用绝对路径，source 安装脚本
source /path/to/EDP_AI/edp_center/bin/install.sh
```

就这么简单！脚本会自动完成所有设置：
- ✅ 设置 PATH（添加到 ~/.bashrc）
- ✅ 设置命令补全（添加到 ~/.bashrc）
- ✅ 激活补全功能（当前 shell）
- ✅ 生成补全缓存

**安装完成后，直接使用：**

```bash
edp --help
edp -i<Tab>  # 测试补全
```

详细步骤请参考：`edp_center/bin/QUICK_START.md`

## 重要提示

**不要使用 `source edp_center/bin/edp` 来使用 edp 命令！**

正确的方式：
1. **将 `edp_center/bin` 添加到 PATH**（如果还没有）
   ```bash
   bash edp_center/bin/setup_path.sh
   source ~/.bashrc
   ```

2. **直接执行 `edp` 命令**（不需要 source）
   ```bash
   edp --help
   edp -init --project dongting
   ```

## 安装方法

### 方法 1: 使用自动设置脚本（最简单，推荐）

```bash
# 运行自动设置脚本
bash edp_center/bin/setup_completion.sh
```

这个脚本会自动：
- 检查 `argcomplete` 是否安装
- 找到 `edp.py` 的路径
- 生成正确的补全命令
- 添加到 `~/.bashrc` 或 `~/.zshrc`

### 方法 1.5: 修复补全（如果补全不工作）

如果之前使用了错误的补全设置（例如 `register-python-argcomplete edp`），可以使用修复脚本：

```bash
# 运行修复脚本
bash edp_center/bin/fix_completion.sh
```

这个脚本会：
- 检查并删除错误的补全设置
- 添加正确的补全设置（指向 `edp.py`）

### 方法 2: 手动设置（使用 argcomplete）

如果系统已安装 `argcomplete`，EDP 会自动使用它提供补全功能。

1. 安装 argcomplete:
   ```bash
   pip install argcomplete
   ```

2. 激活补全（选择一种方式）:
   
   **方式 A: 使用自动设置脚本（推荐）**
   ```bash
   bash edp_center/bin/setup_completion.sh
   ```
   
   **方式 B: 手动添加到配置文件**
   ```bash
   # 获取 edp.py 的完整路径
   EDP_PYTHON_SCRIPT="$(cd edp_center/bin && pwd)/edp.py"
   
   # 添加到 ~/.bashrc 或 ~/.bash_profile
   echo 'eval "$(register-python-argcomplete -s bash '"$EDP_PYTHON_SCRIPT"')"' >> ~/.bashrc
   ```
   
   或者，如果 `edp` 命令在 PATH 中：
   ```bash
   # 获取 edp.py 的完整路径
   EDP_PYTHON_SCRIPT="$(dirname $(which edp))/edp.py"
   echo 'eval "$(register-python-argcomplete -s bash '"$EDP_PYTHON_SCRIPT"')"' >> ~/.bashrc
   ```
   
   **方式 C: 使用补全脚本**
   ```bash
   # 生成并安装补全脚本
   python -m edp_center.main.cli.completion_installer
   
   # 然后添加到 ~/.bashrc
   source ~/.bash_completion.d/edp-completion.bash
   ```

3. 重新加载 shell:
   ```bash
   source ~/.bashrc
   # 或
   source ~/.bash_profile
   ```

### 方法 2: 手动安装补全脚本

如果没有 `argcomplete`，可以使用基本的补全脚本：

```bash
# 生成补全脚本
python -m edp_center.main.cli.completion_installer --generate-only > ~/.bash_completion.d/edp-completion.bash

# 添加到 ~/.bashrc
echo 'source ~/.bash_completion.d/edp-completion.bash' >> ~/.bashrc

# 重新加载
source ~/.bashrc
```

## 使用方法

安装完成后，在 bash 中输入 `edp` 后按 `Tab` 键即可自动补全。

### 示例

1. **补全命令选项**:
   ```bash
   edp -i<Tab>  # 自动补全为 edp -init 或 edp -info
   ```

2. **补全项目名称**:
   ```bash
   edp -init --project <Tab>  # 显示所有可用的项目名称
   ```

3. **补全 flow 名称**:
   ```bash
   edp -info <Tab>  # 显示所有可用的 flow 名称
   ```

4. **补全 flow.step 格式**:
   ```bash
   edp -run pv_calibre.<Tab>  # 显示 pv_calibre 下的所有 step
   ```

5. **补全 block 和 user**:
   ```bash
   edp -init --block <Tab>  # 显示所有可用的 block 名称
   edp -init --block block1 --user <Tab>  # 显示 block1 下的所有 user
   ```

## 支持的补全类型

- **项目名称** (`--project`, `-prj`): 从 `edp_center/config` 自动推断
- **Foundry** (`--foundry`): 从 `edp_center/config` 自动推断
- **Node** (`--node`): 根据 foundry 过滤
- **Version** (`--version`, `-v`): 从项目配置自动推断
- **Block** (`--block`, `-blk`): 从当前目录的 `config.yaml` 读取
- **User** (`--user`, `-u`): 从当前目录的 `config.yaml` 读取（可基于 block 过滤）
- **Branch** (`-b`, `--branch`): 从当前目录结构推断
- **Flow** (`-i`, `--info`): 从 `edp_center/config` 自动推断
- **Flow.Step** (`-run`, `--run`): 支持 `flow.step` 格式的智能补全

## 验证补全是否激活

### 快速验证方法

1. **检查 argcomplete 是否安装**:
   ```bash
   python -c "import argcomplete; print('argcomplete 已安装，版本:', argcomplete.__version__)"
   ```

2. **检查补全函数是否注册**:
   ```bash
   type _python_argcomplete
   ```
   如果显示函数定义，说明补全已激活。

3. **检查 edp 命令的补全设置**:
   ```bash
   complete -p edp
   ```
   如果显示补全设置，说明补全已激活。

4. **运行测试脚本**:
   ```bash
   bash edp_center/main/cli/test_completion.sh
   ```

5. **实际测试补全**:
   ```bash
   # 在 bash 中输入以下命令，然后按 Tab 键
   edp -i<Tab>        # 应该显示 -init 和 -info
   edp -init --project <Tab>  # 应该显示项目列表
   ```

### 判断补全是否工作的标志

- ✅ **成功标志**:
  - 输入 `edp -i` 后按 Tab，会显示 `-init` 和 `-info`
  - 输入 `edp -init --project ` 后按 Tab，会显示项目列表
  - 运行 `type _python_argcomplete` 显示函数定义
  - 运行 `complete -p edp` 显示补全设置

- ❌ **失败标志**:
  - 按 Tab 没有任何反应
  - 按 Tab 显示文件列表而不是命令选项
  - `type _python_argcomplete` 显示 "not found"
  - `complete -p edp` 显示 "no completion specification"

## 故障排除

### 补全不工作

1. **检查 argcomplete 是否安装**:
   ```bash
   pip list | grep argcomplete
   # 或
   python -c "import argcomplete"
   ```

2. **检查补全脚本是否加载**:
   ```bash
   type _python_argcomplete
   ```

3. **检查 edp 命令路径**:
   ```bash
   which edp
   ```

4. **手动测试补全**:
   ```bash
   register-python-argcomplete edp
   ```

5. **检查 ~/.bashrc 是否包含补全命令**:
   ```bash
   grep "register-python-argcomplete" ~/.bashrc
   ```

6. **重新加载 bash 配置**:
   ```bash
   source ~/.bashrc
   # 或
   exec bash
   ```

### 补全结果不正确

补全功能依赖于：
- `edp_center` 路径（自动从当前目录向上查找）
- `config.yaml` 文件（用于 block 和 user 补全）
- `.edp_version` 文件（用于 branch 补全）

确保在正确的工作目录下使用补全功能。

## 高级配置

### 自定义补全脚本位置

```bash
python -m edp_center.main.cli.completion_installer --dest /custom/path/
```

### 查看生成的补全脚本

```bash
python -m edp_center.main.cli.completion_installer --generate-only
```

