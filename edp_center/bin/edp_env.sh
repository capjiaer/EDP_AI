#!/bin/bash
# 
# EDP 环境设置脚本（Bash 版本）
# 功能：
#   1. 设置 PATH（添加 edp_center/bin 到 PATH）
#   2. 设置环境变量（EDP_CENTER_PATH 等）
#
# 使用方法：
#   source /path/to/EDP_AI/edp_center/bin/edp_env.sh
#   或者在 ~/.bashrc 中添加：
#   source /path/to/EDP_AI/edp_center/bin/edp_env.sh

# 获取脚本所在目录（edp_center/bin）
EDP_BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EDP_CENTER_DIR="$(cd "$EDP_BIN_DIR/.." && pwd)"

# 1. 设置 PATH（如果还没有添加）
if [[ ":$PATH:" != *":$EDP_BIN_DIR:"* ]]; then
    export PATH="$EDP_BIN_DIR:$PATH"
fi

# 2. 设置 PYTHONPATH（如果需要）
if [[ ":$PYTHONPATH:" != *":$EDP_CENTER_DIR:"* ]]; then
    export PYTHONPATH="$EDP_CENTER_DIR:${PYTHONPATH:-}"
fi

# 3. 设置环境变量
export EDP_CENTER_PATH="$EDP_CENTER_DIR"
export EDP_BIN_PATH="$EDP_BIN_DIR"

# 4. 自动检测并设置 Python 路径（Windows Git Bash 兼容）
# 如果用户没有手动设置 EDP_PYTHON_PATH，则自动检测
if [ -z "$EDP_PYTHON_PATH" ]; then
    # 方法1: 从 PATH 中查找 Python 安装路径（Windows）
    # PATH 中通常包含类似 /c/Users/username/AppData/Local/Programs/Python/Python313 的路径
    PYTHON_FROM_PATH=$(echo "$PATH" | tr ':' '\n' | grep -i "Programs/Python/Python" | head -1)
    if [ -n "$PYTHON_FROM_PATH" ] && [ -f "$PYTHON_FROM_PATH/python.exe" ]; then
        # 移除末尾的斜杠（如果有）并添加 python.exe
        PYTHON_FROM_PATH=$(echo "$PYTHON_FROM_PATH" | sed 's|/$||')
        export EDP_PYTHON_PATH="$PYTHON_FROM_PATH/python.exe"
    fi
    
    # 方法2: 使用 $HOME 或从 PATH 提取用户名，查找常见安装路径
    if [ -z "$EDP_PYTHON_PATH" ] && [ -n "$HOME" ]; then
        USER_HOME=$(echo "$HOME" | sed 's|^/c/|/c/|')
        if [ -d "$USER_HOME/AppData/Local/Programs/Python" ]; then
            PYTHON_DIR=$(ls -td "$USER_HOME/AppData/Local/Programs/Python/Python"* 2>/dev/null | head -1)
            if [ -n "$PYTHON_DIR" ] && [ -f "$PYTHON_DIR/python.exe" ]; then
                export EDP_PYTHON_PATH="$PYTHON_DIR/python.exe"
            fi
        fi
    fi
    
    # 方法3: 尝试使用 command -v（但排除 WindowsApps 启动器）
    if [ -z "$EDP_PYTHON_PATH" ]; then
        if command -v python3 >/dev/null 2>&1; then
            PYTHON3_PATH=$(command -v python3)
            # 排除 WindowsApps 中的启动器，测试是否真的可用
            if [[ "$PYTHON3_PATH" != *"WindowsApps"* ]]; then
                if "$PYTHON3_PATH" --version >/dev/null 2>&1; then
                    export EDP_PYTHON_PATH="$PYTHON3_PATH"
                fi
            fi
        elif command -v python >/dev/null 2>&1; then
            PYTHON_PATH=$(command -v python)
            if [[ "$PYTHON_PATH" != *"WindowsApps"* ]]; then
                if "$PYTHON_PATH" --version >/dev/null 2>&1; then
                    export EDP_PYTHON_PATH="$PYTHON_PATH"
                fi
            fi
        fi
    fi
fi

