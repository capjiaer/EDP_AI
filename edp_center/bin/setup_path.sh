#!/bin/bash
# 
# EDP Main PATH 设置脚本
# 将 edp_center/bin 目录添加到 PATH 环境变量

# 获取脚本所在目录（edp_center/bin 的绝对路径）
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$BIN_DIR/../.." && pwd)"

echo "EDP Main PATH 设置"
echo "=================="
echo ""
echo "当前 bin 目录: $BIN_DIR"
echo "项目根目录: $PROJECT_ROOT"
echo ""

# 检查 shell 类型
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
    SHELL_NAME="bash"
    PATH_LINE="export PATH=\"\$PATH:$BIN_DIR\""
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_NAME="zsh"
    PATH_LINE="export PATH=\"\$PATH:$BIN_DIR\""
elif [ -n "$CSH_VERSION" ] || [ -n "$TCSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.cshrc"
    SHELL_NAME="csh/tcsh"
    PATH_LINE="set path = (\$path $BIN_DIR)"
else
    echo "未识别的 shell 类型，请手动添加到配置文件"
    exit 1
fi

echo "检测到 shell: $SHELL_NAME"
echo "配置文件: $SHELL_CONFIG"
echo ""

# 检查是否已经添加
if grep -q "$BIN_DIR" "$SHELL_CONFIG" 2>/dev/null; then
    echo "⚠️  PATH 已经包含 $BIN_DIR"
    echo "   无需重复添加"
else
    echo "添加 PATH 配置到 $SHELL_CONFIG..."
    echo "" >> "$SHELL_CONFIG"
    echo "# EDP Main - Add bin directory to PATH" >> "$SHELL_CONFIG"
    echo "$PATH_LINE" >> "$SHELL_CONFIG"
    echo "✅ PATH 配置已添加"
    echo ""
    echo "请运行以下命令使配置生效："
    echo "  source $SHELL_CONFIG"
    echo ""
    echo "或者重新打开终端"
fi

echo ""
echo "设置完成后，可以在任何地方使用 'edp' 命令："
echo "  edp --help"
echo "  edp run --work-path WORK_PATH ..."

