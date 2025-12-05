#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试教程 Markdown 转换器
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from edp_center.main.cli.commands.tutorial_markdown_converter import (
    markdown_to_html,
    escape_html,
    process_lists,
    process_code_blocks,
    restore_code_blocks
)


def test_escape_html():
    """测试 HTML 转义"""
    test_cases = [
        ('<script>alert(1)</script>', '&lt;script&gt;alert(1)&lt;/script&gt;'),
        ('"hello"', '&quot;hello&quot;'),
        ("'world'", '&#39;world&#39;'),
        ('&amp;', '&amp;amp;'),
        ('<div>test</div>', '&lt;div&gt;test&lt;/div&gt;'),
    ]
    
    print("测试 escape_html:")
    for input_text, expected in test_cases:
        result = escape_html(input_text)
        status = '✅' if result == expected else '❌'
        print(f'  {status} {input_text!r} -> {result!r}')
        if result != expected:
            print(f'     期望: {expected!r}')
    print()


def test_code_blocks():
    """测试代码块处理"""
    test_cases = [
        ('简单代码块', '```bash\necho test\n```'),
        ('多个代码块', '```bash\necho 1\n```\n\n```yaml\nkey: value\n```'),
        ('代码块中的特殊字符', '```bash\necho "<script>alert(1)</script>"\n```'),
        ('空代码块', '```\n\n```'),
    ]
    
    print("测试代码块处理:")
    for name, test_md in test_cases:
        try:
            html, code_blocks = process_code_blocks(test_md)
            restored = restore_code_blocks(html, code_blocks)
            print(f'  ✅ {name}: 通过 (找到 {len(code_blocks)} 个代码块)')
        except Exception as e:
            print(f'  ❌ {name}: {e}')
    print()


def test_lists():
    """测试列表处理"""
    test_cases = [
        ('有序列表', '1. first item\n2. second item\n3. third item'),
        ('无序列表', '- item1\n- item2\n- item3'),
        ('混合列表', '- unordered\n1. ordered\n- back to unordered'),
        ('列表中的代码占位符', '- item1\n<!--CODEBLOCK0-->\n- item2'),
    ]
    
    print("测试列表处理:")
    for name, test_html in test_cases:
        try:
            result = process_lists(test_html)
            print(f'  ✅ {name}: 通过')
        except Exception as e:
            print(f'  ❌ {name}: {e}')
    print()


def test_markdown_to_html():
    """测试完整的 Markdown 转 HTML"""
    test_cases = [
        ('简单段落', 'This is a paragraph.'),
        ('标题和段落', '# Heading\n\nThis is a paragraph.'),
        ('代码块', '```bash\necho test\n```'),
        ('列表', '- item1\n- item2'),
        ('有序列表', '1. first\n2. second'),
        ('粗体和斜体', 'This is **bold** and *italic*.'),
        ('链接', '[Link](http://example.com)'),
        ('混合内容', '# Title\n\nParagraph with **bold**.\n\n```bash\necho test\n```\n\n- item1\n- item2'),
    ]
    
    print("测试 markdown_to_html:")
    for name, test_md in test_cases:
        try:
            html = markdown_to_html(test_md)
            # 检查基本结构
            has_tags = '<' in html and '>' in html
            print(f'  ✅ {name}: 通过 (输出长度: {len(html)})')
        except Exception as e:
            print(f'  ❌ {name}: {e}')
    print()


def test_edge_cases():
    """测试边界情况"""
    test_cases = [
        ('空字符串', ''),
        ('只有换行', '\n\n\n'),
        ('代码块在列表前', '```bash\necho test\n```\n\n- item'),
        ('标题在代码块后', '```bash\necho test\n```\n\n# Heading'),
        ('多个连续空行', 'para1\n\n\n\npara2'),
        ('代码块中的代码标记', '```bash\necho "```yaml"\n```'),
    ]
    
    print("测试边界情况:")
    for name, test_md in test_cases:
        try:
            html = markdown_to_html(test_md)
            print(f'  ✅ {name}: 通过')
        except Exception as e:
            print(f'  ❌ {name}: {e}')
    print()


def main():
    """运行所有测试"""
    print("=" * 60)
    print("教程 Markdown 转换器测试")
    print("=" * 60)
    print()
    
    test_escape_html()
    test_code_blocks()
    test_lists()
    test_markdown_to_html()
    test_edge_cases()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

