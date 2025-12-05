#!/bin/bash
# 
# 下载教程 HTML 所需的 JavaScript 库文件
# 
# 使用方法：
#   cd /path/to/EDP_AI/edp_center/tutorial/libs
#   ./download_libs.sh
# 
# 或者：
#   bash /path/to/EDP_AI/edp_center/tutorial/libs/download_libs.sh

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 下载 JavaScript 库文件 ==="
echo ""
echo "目标目录: $SCRIPT_DIR"
echo ""

# 检查 wget 或 curl
if command -v wget >/dev/null 2>&1; then
    DOWNLOAD_CMD="wget"
elif command -v curl >/dev/null 2>&1; then
    DOWNLOAD_CMD="curl"
else
    echo "❌ 错误: 未找到 wget 或 curl 命令" >&2
    echo "   请安装 wget 或 curl，或手动下载库文件" >&2
    exit 1
fi

echo "使用下载工具: $DOWNLOAD_CMD"
echo ""

# 下载 marked.js
echo "[1/2] 下载 marked.js..."
if [ "$DOWNLOAD_CMD" = "wget" ]; then
    wget -q https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js -O marked.min.js
else
    curl -s -o marked.min.js https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js
fi

if [ -f "marked.min.js" ] && [ -s "marked.min.js" ]; then
    echo "   ✓ marked.min.js 下载成功"
else
    echo "   ❌ marked.min.js 下载失败"
    exit 1
fi

# 下载 DOMPurify
echo "[2/2] 下载 DOMPurify..."
if [ "$DOWNLOAD_CMD" = "wget" ]; then
    wget -q https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js -O purify.min.js
else
    curl -s -o purify.min.js https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js
fi

if [ -f "purify.min.js" ] && [ -s "purify.min.js" ]; then
    echo "   ✓ purify.min.js 下载成功"
else
    echo "   ❌ purify.min.js 下载失败"
    exit 1
fi

echo ""
echo "=== 下载完成 ==="
echo ""
echo "已下载的文件："
ls -lh marked.min.js purify.min.js 2>/dev/null
echo ""
echo "✅ 现在教程 HTML 可以在离线环境下正常工作了！"
echo ""

