#!/bin/bash
# 快速检查 EDP 命令补全是否激活

echo "=== EDP 命令补全状态检查 ==="
echo ""

# 检查 1: argcomplete 是否安装
echo "1. 检查 argcomplete 是否安装:"
if python -c "import argcomplete" 2>/dev/null; then
    echo "   ✓ argcomplete 已安装"
else
    echo "   ✗ argcomplete 未安装"
    echo "   请运行: pip install argcomplete"
fi
echo ""

# 检查 2: 补全函数是否注册
echo "2. 检查补全函数是否注册:"
if type _python_argcomplete >/dev/null 2>&1; then
    echo "   ✓ _python_argcomplete 函数已注册"
    echo "   (补全已激活)"
else
    echo "   ✗ _python_argcomplete 函数未注册"
    echo "   请运行: eval \"\$(register-python-argcomplete edp)\""
    echo "   或添加到 ~/.bashrc:"
    echo "   echo 'eval \"\$(register-python-argcomplete edp)\"' >> ~/.bashrc"
fi
echo ""

# 检查 3: edp 命令的补全设置
echo "3. 检查 edp 命令的补全设置:"
if complete -p edp >/dev/null 2>&1; then
    echo "   ✓ edp 命令已设置补全"
    complete -p edp
else
    echo "   ✗ edp 命令未设置补全"
    echo "   请运行: eval \"\$(register-python-argcomplete edp)\""
fi
echo ""

# 总结
echo "=== 总结 ==="
if type _python_argcomplete >/dev/null 2>&1 && complete -p edp >/dev/null 2>&1; then
    echo "✓ 补全功能已激活！"
    echo ""
    echo "测试方法:"
    echo "  1. 输入: edp -i<Tab>"
    echo "     应该显示: -init 和 -info"
    echo ""
    echo "  2. 输入: edp -init --project <Tab>"
    echo "     应该显示项目列表"
    echo ""
    echo "  3. 输入: edp -info <Tab>"
    echo "     应该显示 flow 列表"
else
    echo "✗ 补全功能未激活"
    echo ""
    echo "激活步骤:"
    echo "  1. 安装 argcomplete: pip install argcomplete"
    echo "  2. 激活补全: eval \"\$(register-python-argcomplete edp)\""
    echo "  3. 永久激活: 将上述命令添加到 ~/.bashrc"
fi

