#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial Markdown Converter - Markdown 转 HTML 转换器

负责将 Markdown 内容转换为 HTML，包括代码块、标题、列表、链接等。
"""

import re
from typing import List


def escape_html(text: str) -> str:
    """
    HTML 转义
    
    Args:
        text: 原始文本
        
    Returns:
        转义后的文本
    """
    return (text.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def convert_link(match: re.Match) -> str:
    """
    转换 Markdown 链接为 HTML 链接（将 .md 链接转换为 .html）
    
    Args:
        match: 正则匹配对象
        
    Returns:
        HTML 链接字符串
    """
    link_text = match.group(1)
    link_url = match.group(2)
    
    # 跳过外部链接和纯锚点链接
    if link_url.startswith('http://') or link_url.startswith('https://') or (link_url.startswith('#') and not '.md' in link_url):
        return f'<a href="{link_url}">{link_text}</a>'
    
    # 提取锚点（如果有）
    anchor = ''
    if '#' in link_url:
        anchor = '#' + link_url.split('#', 1)[1]
        link_url = link_url.split('#', 1)[0]
    
    # 处理 TUTORIAL.md 或 TUTORIAL.html 链接（无论路径如何）
    if 'TUTORIAL' in link_url.upper() and (link_url.endswith('.md') or link_url.endswith('.html')):
        link_url = 'index.html'
    # 处理其他 .md 文件链接
    elif link_url.endswith('.md'):
        # 转换为 .html
        link_url = link_url.replace('.md', '.html')
    # 处理相对路径（去掉 ../）
    elif link_url.startswith('../'):
        # 去掉 ../，因为所有 HTML 文件都在同一目录
        link_url = link_url.replace('../', '')
        # 如果去掉 ../ 后是 TUTORIAL.md 或 TUTORIAL.html，转换为 index.html
        if 'TUTORIAL' in link_url.upper() and (link_url.endswith('.md') or link_url.endswith('.html')):
            link_url = 'index.html'
        # 如果去掉 ../ 后还是 .md，转换为 .html
        elif link_url.endswith('.md'):
            link_url = link_url.replace('.md', '.html')
    
    # 组合最终链接
    final_url = link_url + anchor
    return f'<a href="{final_url}">{link_text}</a>'


def process_code_blocks(html: str) -> tuple[str, List[str]]:
    """
    处理代码块：提取代码块并替换为占位符
    
    Args:
        html: 原始 HTML 内容
        
    Returns:
        (处理后的 HTML, 代码块列表)
    """
    code_blocks: List[str] = []
    
    def replace_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f'<!--CODEBLOCK{len(code_blocks)-1}-->'
    
    # 使用更精确的正则表达式：匹配 ``` 开头，然后是可选的语言标识符，然后是换行，然后是内容（非贪婪），最后是 ```
    # 注意：需要确保匹配到正确的结束标记，避免匹配到代码块内的 ``` 或其他内容
    # 改进：使用更严格的匹配，确保 ``` 后面是换行或字符串结束
    html = re.sub(
        r'```(\w+)?\n(.*?)```(?=\n|$)',
        replace_code_block,
        html,
        flags=re.DOTALL | re.MULTILINE
    )
    
    return html, code_blocks


def restore_code_blocks(html: str, code_blocks: List[str]) -> str:
    """
    恢复代码块：将占位符替换为实际的 HTML 代码块
    
    Args:
        html: 处理后的 HTML 内容
        code_blocks: 代码块列表
        
    Returns:
        恢复后的 HTML 内容
    """
    for i, code_block in enumerate(code_blocks):
        # 重新解析代码块（与 process_code_blocks 中的正则保持一致）
        code_match = re.match(r'```(\w+)?\n(.*?)```', code_block, flags=re.DOTALL)
        if code_match:
            lang = code_match.group(1) or ''
            code_content = code_match.group(2)
            html_code = f'<pre><code class="language-{lang}">{escape_html(code_content)}</code></pre>'
            html = html.replace(f'<!--CODEBLOCK{i}-->', html_code)
        else:
            # 如果匹配失败，尝试直接使用原始代码块（去掉首尾的 ```）
            # 这种情况不应该发生，但作为容错处理
            cleaned = code_block.strip()
            if cleaned.startswith('```'):
                # 提取语言标识符
                first_line = cleaned.split('\n', 1)[0]
                lang = first_line[3:].strip() if len(first_line) > 3 else ''
                # 提取内容（去掉第一行和最后一行）
                lines = cleaned.split('\n')
                if len(lines) > 2:
                    code_content = '\n'.join(lines[1:-1])
                    html_code = f'<pre><code class="language-{lang}">{escape_html(code_content)}</code></pre>'
                    html = html.replace(f'<!--CODEBLOCK{i}-->', html_code)
    
    return html


def process_lists(html: str) -> str:
    """
    处理列表（有序和无序）
    
    注意：此函数处理的是已经经过代码块占位符替换的 HTML，
    所以不会误处理代码块中的列表标记。
    
    Args:
        html: HTML 内容（已处理代码块占位符）
        
    Returns:
        处理后的 HTML 内容
    """
    lines = html.split('\n')
    result_lines = []
    in_ul = False
    in_ol = False
    
    for line in lines:
        # 跳过代码块占位符行
        if '<!--CODEBLOCK' in line:
            # 非列表项，关闭当前列表
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            result_lines.append(line)
            continue
        
        # 检查是否是无序列表项（-、*、+ 开头，后跟空格）
        ul_match = re.match(r'^([-*+])\s+(.+)$', line)
        # 检查是否是有序列表项（数字. 开头，后跟空格）
        ol_match = re.match(r'^(\d+)\.\s+(.+)$', line)
        
        if ul_match:
            if not in_ul:
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                result_lines.append('<ul>')
                in_ul = True
            result_lines.append(f'<li>{ul_match.group(2)}</li>')
        elif ol_match:
            if not in_ol:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                result_lines.append('<ol>')
                in_ol = True
            result_lines.append(f'<li>{ol_match.group(2)}</li>')
        else:
            # 非列表项，关闭当前列表
            if in_ul:
                result_lines.append('</ul>')
                in_ul = False
            if in_ol:
                result_lines.append('</ol>')
                in_ol = False
            result_lines.append(line)
    
    # 关闭可能未关闭的列表
    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')
    
    return '\n'.join(result_lines)


def markdown_to_html(markdown_content: str) -> str:
    """
    将 Markdown 转换为 HTML（带样式）
    
    Args:
        markdown_content: Markdown 内容
        
    Returns:
        HTML 内容
    """
    html = markdown_content
    
    # 移除返回目录链接
    html = re.sub(r'\[←.*?\]\(.*?\)', '', html)
    
    # 先处理代码块（在标题处理之前，避免代码块中的 # 被误认为是标题）
    html, code_blocks = process_code_blocks(html)
    
    # 标题转换（现在代码块已经被占位符替换，不会影响）
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # 行内代码（在代码块处理之后，避免影响代码块）
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # 粗体（避免匹配代码块占位符）
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(?![A-Z]+BLOCK\d+)([^_]+)__', r'<strong>\1</strong>', html)
    
    # 斜体（避免匹配代码块占位符和下划线变量名）
    # 只匹配单词边界之间的单个下划线，避免匹配变量名如 edp_center
    html = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'<em>\1</em>', html)
    # 对于下划线斜体，更严格：前后必须是空格或标点，不能是字母数字
    html = re.sub(r'(?<![a-zA-Z0-9])_([^_]+)_(?![a-zA-Z0-9])', r'<em>\1</em>', html)
    
    # 链接（需要将 .md 链接转换为 .html）
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', convert_link, html)
    
    # 列表处理
    html = process_lists(html)
    
    # 恢复代码块（将占位符替换为实际的 HTML 代码块）
    # 必须在段落处理之前恢复，避免占位符被包裹在 <p> 标签中
    html = restore_code_blocks(html, code_blocks)
    
    # 段落（简单处理：空行分隔）
    # 但要避免在代码块、列表、标题前后添加段落标签
    # 先保护特殊元素（代码块、列表、标题）
    html = re.sub(r'(<pre><code.*?</code></pre>)', r'__PROTECT_CODE__\1__PROTECT_CODE__', html, flags=re.DOTALL)
    html = re.sub(r'(<[uo]l>.*?</[uo]l>)', r'__PROTECT_LIST__\1__PROTECT_LIST__', html, flags=re.DOTALL)
    html = re.sub(r'(<h[1-4]>.*?</h[1-4]>)', r'__PROTECT_HEADING__\1__PROTECT_HEADING__', html, flags=re.DOTALL)
    
    # 处理段落：将连续的空行转换为段落分隔
    html = re.sub(r'\n\n+', '</p><p>', html)
    
    # 移除首尾的空段落标签，只在有内容时添加
    html = html.strip()
    if html and not html.startswith('<'):
        html = '<p>' + html
    if html and not html.endswith('>'):
        html = html + '</p>'
    
    # 恢复保护的元素
    html = re.sub(r'__PROTECT_CODE__(<pre><code.*?</code></pre>)__PROTECT_CODE__', r'\1', html, flags=re.DOTALL)
    html = re.sub(r'__PROTECT_LIST__(<[uo]l>.*?</[uo]l>)__PROTECT_LIST__', r'\1', html, flags=re.DOTALL)
    html = re.sub(r'__PROTECT_HEADING__(<h[1-4]>.*?</h[1-4]>)__PROTECT_HEADING__', r'\1', html, flags=re.DOTALL)
    
    return html

