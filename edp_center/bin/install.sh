#!/bin/bash
# 
# EDP 一键安装脚本（Bash 版本）
# 用户只需要 source 这个脚本，就能完成所有设置
# 
# 使用方法：
#   source /path/to/EDP_AI/edp_center/bin/install.sh
# 
# 或者：
#   . /path/to/EDP_AI/edp_center/bin/install.sh
#
# 注意：
#   - 此脚本仅支持 Bash/Zsh
#   - Csh/Tcsh 用户请使用：source /path/to/EDP_AI/edp_center/bin/install.csh

# 检测 shell 类型
if [ -n "$CSH_VERSION" ] || [ -n "$TCSH_VERSION" ]; then
    echo "⚠️  检测到 Csh/Tcsh 环境" >&2
    echo "   请使用 install.csh 脚本：" >&2
    echo "   source /path/to/EDP_AI/edp_center/bin/install.csh" >&2
    exit 1
fi

# 获取脚本所在目录（edp_center/bin 的绝对路径）
# 支持通过 source 或 bash 执行
if [ -n "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

BIN_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$BIN_DIR/../.." && pwd)"

echo "=== EDP 一键安装 ==="
echo ""
echo "项目根目录: $PROJECT_ROOT"
echo "bin 目录: $BIN_DIR"
echo ""

# 步骤 0: 设置可执行权限
echo "[0/3] 设置可执行权限..."
if [ -d "$BIN_DIR" ]; then
    # 设置所有脚本文件的可执行权限
    chmod +x "$BIN_DIR"/edp "$BIN_DIR"/edp_init "$BIN_DIR"/edp_info 2>/dev/null
    chmod +x "$BIN_DIR"/edp.py "$BIN_DIR"/edp_init.py "$BIN_DIR"/edp_info.py 2>/dev/null
    chmod +x "$BIN_DIR"/*.sh "$BIN_DIR"/*.csh 2>/dev/null
    echo "   ✓ 可执行权限已设置"
else
    echo "   ⚠️  bin 目录不存在: $BIN_DIR"
fi
echo ""

# 步骤 1: 设置 PATH
echo "[1/3] 设置 PATH..."
if [ -f "$BIN_DIR/setup_path.sh" ]; then
    # 直接调用 setup_path.sh 的逻辑，避免重复 source
    SHELL_CONFIG="$HOME/.bashrc"
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    fi
    
    # 检查是否已经添加
    if grep -q "$BIN_DIR" "$SHELL_CONFIG" 2>/dev/null; then
        echo "   ✓ PATH 已经包含 $BIN_DIR"
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# EDP Main - Add bin directory to PATH" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$SHELL_CONFIG"
        echo "   ✓ PATH 配置已添加"
    fi
    
    # 立即添加到当前 shell 的 PATH
    export PATH="$PATH:$BIN_DIR"
    echo "   ✓ PATH 已添加到当前 shell"
else
    echo "   ⚠️  setup_path.sh 不存在，跳过 PATH 设置"
fi
echo ""

# 步骤 2: 检查命令是否可用
echo "[2/3] 检查命令..."
if command -v edp >/dev/null 2>&1; then
    echo "   ✓ edp 命令可用: $(which edp)"
else
    echo "   ❌ edp 命令不可用"
    echo "   请检查 PATH 设置"
fi
if command -v edp_init >/dev/null 2>&1; then
    echo "   ✓ edp_init 命令可用: $(which edp_init)"
else
    echo "   ❌ edp_init 命令不可用"
    echo "   请检查 PATH 设置"
fi
if command -v edp_info >/dev/null 2>&1; then
    echo "   ✓ edp_info 命令可用: $(which edp_info)"
else
    echo "   ❌ edp_info 命令不可用"
    echo "   请检查 PATH 设置"
fi
echo ""

# 总结
echo "=== 安装完成 ==="
echo ""
echo "✅ 所有设置已完成！"
echo ""
echo "现在可以使用："
echo "  edp --help        # 运行相关命令"
echo "  edp_init --help   # 初始化相关命令"
echo "  edp_info --help   # 信息查询相关命令"
echo ""
echo "注意："
echo "  - PATH 配置已添加到 $SHELL_CONFIG"
echo "  - 当前 shell 已激活 PATH"
echo "  - 新开的 shell 会自动加载配置（无需再次 source）"
echo ""
