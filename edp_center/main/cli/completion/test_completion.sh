#!/bin/bash
# EDP 命令补全测试脚本

echo "=== EDP 命令补全测试 ==="
echo ""

# 1. 检查 argcomplete 是否安装
echo "1. 检查 argcomplete 是否安装:"
if python -c "import argcomplete" 2>/dev/null; then
    echo "   ✓ argcomplete 已安装"
    # 尝试获取版本号（某些版本可能没有 __version__ 属性）
    python -c "import argcomplete; print(f'   版本: {getattr(argcomplete, \"__version__\", \"未知\")}')" 2>/dev/null || echo "   版本: 已安装（版本号不可用）"
else
    echo "   ✗ argcomplete 未安装"
    echo "   请运行: pip install argcomplete"
    exit 1
fi
echo ""

# 2. 检查 register-python-argcomplete 命令是否存在
echo "2. 检查 register-python-argcomplete 命令:"
if command -v register-python-argcomplete >/dev/null 2>&1; then
    echo "   ✓ register-python-argcomplete 命令可用"
    which register-python-argcomplete
else
    echo "   ✗ register-python-argcomplete 命令不可用"
    echo "   请检查 PATH 环境变量"
fi
echo ""

# 3. 检查补全函数是否注册
echo "3. 检查补全函数是否注册:"
if type _python_argcomplete >/dev/null 2>&1; then
    echo "   ✓ _python_argcomplete 函数已注册"
else
    echo "   ✗ _python_argcomplete 函数未注册"
    echo "   请运行: eval \"\$(register-python-argcomplete edp)\""
fi
echo ""

# 4. 检查 edp 命令的补全设置
echo "4. 检查 edp 命令的补全设置:"
if complete -p edp >/dev/null 2>&1; then
    echo "   ✓ edp 命令已设置补全"
    complete -p edp
else
    echo "   ✗ edp 命令未设置补全"
    echo "   请运行: eval \"\$(register-python-argcomplete edp)\""
fi
echo ""

# 5. 测试补全功能（需要交互式测试）
echo "5. 补全功能测试:"
echo "   请在 bash 中运行以下命令测试补全:"
echo "   edp -i<Tab>"
echo "   edp -init --project <Tab>"
echo "   edp -info <Tab>"
echo "   edp -run pv_calibre.<Tab>"
echo ""

# 6. 检查环境变量
echo "6. 检查相关环境变量:"
if [ -n "$COMP_LINE" ] || [ -n "$COMP_POINT" ]; then
    echo "   ✓ 补全环境变量已设置"
    echo "   COMP_LINE: $COMP_LINE"
    echo "   COMP_POINT: $COMP_POINT"
else
    echo "   (补全环境变量仅在补全时设置)"
fi
echo ""

echo "=== 测试完成 ==="
echo ""
echo "提示:"
echo "  - 如果补全不工作，请确保已运行: eval \"\$(register-python-argcomplete edp)\""
echo "  - 可以将此命令添加到 ~/.bashrc 以永久启用"
echo "  - 在非交互式 shell 中，补全功能不会激活"

