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

