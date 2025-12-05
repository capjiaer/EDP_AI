#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial HTML Generator - 教程 HTML 生成器

负责生成教程的 HTML 页面（单页应用）。
"""

import sys
import re
from pathlib import Path
from typing import Optional, List, Dict

from .tutorial_path_manager import get_tutorial_output_dir
from .tutorial_styles import SPA_STYLE
from .tutorial_scripts import generate_spa_script
from .tutorial_html_templates import generate_spa_html


def extract_headings(md_content: str) -> List[Dict]:
    """
    从 Markdown 内容中提取标题（h2, h3）
    
    Args:
        md_content: Markdown 内容
        
    Returns:
        标题列表，每个标题包含 level, text, anchor
    """
    headings = []
    lines = md_content.split('\n')
    
    for line in lines:
        # 匹配 h2 (##) 和 h3 (###)
        h2_match = re.match(r'^##\s+(.+)$', line)
        h3_match = re.match(r'^###\s+(.+)$', line)
        
        if h2_match:
            text = h2_match.group(1).strip()
            # 移除返回链接
            text = text.replace('[← 返回目录]', '').strip()
            # 生成锚点 ID（移除特殊字符，转换为小写，空格替换为-）
            anchor = re.sub(r'[^\w\s-]', '', text.lower())
            anchor = re.sub(r'[-\s]+', '-', anchor)
            headings.append({
                'level': 2,
                'text': text,
                'anchor': anchor
            })
        elif h3_match:
            text = h3_match.group(1).strip()
            # 移除返回链接
            text = text.replace('[← 返回目录]', '').strip()
            # 生成锚点 ID
            anchor = re.sub(r'[^\w\s-]', '', text.lower())
            anchor = re.sub(r'[-\s]+', '-', anchor)
            headings.append({
                'level': 3,
                'text': text,
                'anchor': anchor
            })
    
    return headings


def collect_tutorial_files(tutorial_dir: Path) -> List[Dict]:
    """
    收集所有教程文件
    
    Args:
        tutorial_dir: 教程目录路径
        
    Returns:
        教程文件列表（包含 filename, title, path, file_path, headings）
    """
    tutorial_files = []
    file_order = [
        '00_introduction.md',
        '01_installation.md',
        '02_getting_started.md',
        '03_basic_usage.md',
        '04_hooks_and_imports.md',
        '05_sub_steps_and_debug.md',
        '06_configuration.md',
        '07_best_practices.md',
        '08_faq.md',
        '09_resources.md',
    ]
    
    for filename in file_order:
        file_path = tutorial_dir / filename
        if file_path.exists():
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取第一行作为主标题
            first_line = content.split('\n')[0].strip()
            title = first_line.lstrip('#').strip()
            # 移除返回链接
            title = title.replace('[← 返回目录]', '').strip()
            
            # 提取子标题
            headings = extract_headings(content)
            
            tutorial_files.append({
                'filename': filename,
                'title': title,
                'path': file_path.relative_to(tutorial_dir),
                'file_path': file_path,
                'headings': headings
            })
    
    return tutorial_files


def generate_tutorial_html(edp_center_path: Path, output_dir: Optional[Path] = None, force: bool = False) -> Path:
    """
    生成教程单页应用（SPA）：左侧目录，右侧内容
    
    Args:
        edp_center_path: edp_center 路径
        output_dir: 输出目录（如果为 None，自动选择用户可写位置）
        force: 是否强制重新生成
        
    Returns:
        生成的 HTML 文件路径
    """
    tutorial_dir = edp_center_path / 'tutorial'
    if not tutorial_dir.exists():
        print(f"错误: 教程目录不存在: {tutorial_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 确定输出目录
    if output_dir is None:
        output_dir = get_tutorial_output_dir(edp_center_path)
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'index.html'
    
    # 收集所有教程文件
    tutorial_files = collect_tutorial_files(tutorial_dir)
    
    # 检查是否需要重新生成
    need_update = force
    if not need_update and output_file.exists():
        # 文件存在，检查是否需要更新
        index_mtime = output_file.stat().st_mtime
        for tutorial in tutorial_files:
            md_mtime = tutorial['file_path'].stat().st_mtime
            if md_mtime > index_mtime:
                need_update = True
                break
    elif not need_update and not output_file.exists():
        # 文件不存在，需要生成
        need_update = True
    
    if not need_update:
        # 再次验证文件确实存在（防止文件在检查后被删除）
        if output_file.exists():
            print(f"ℹ️  教程已是最新: {output_file}")
            return output_file
        else:
            # 文件不存在，需要生成
            need_update = True
    
    # 读取所有教程内容
    tutorials_data = []
    for tutorial in tutorial_files:
        with open(tutorial['file_path'], 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 转义 Markdown 内容
        md_content_escaped = (md_content
                              .replace('\\', '\\\\')
                              .replace('`', '\\`')
                              .replace('${', '\\${')
                              .replace('\r\n', '\\n')
                              .replace('\r', '\\n')
                              .replace('\n', '\\n'))
        
        tutorials_data.append({
            'id': tutorial['filename'].replace('.md', ''),
            'title': tutorial['title'],
            'content': md_content_escaped,
            'headings': tutorial.get('headings', [])
        })
    
    # 生成单页应用 HTML（连续滚动模式）
    nav_items_html = ''
    content_sections_html = ''
    tutorials_js_data = []
    
    for i, tutorial in enumerate(tutorials_data):
        # 导航项（使用锚点链接）
        # 第一个章节默认展开
        expanded_class = ' expanded' if i == 0 and tutorial.get('headings') else ''
        nav_items_html += f'                <div class="nav-group{expanded_class}">\n'
        nav_items_html += f'                    <a href="#{tutorial["id"]}" class="nav-item nav-main" data-tutorial-id="{tutorial["id"]}">{i+1}. {tutorial["title"]}</a>\n'
        
        # 添加子目录（如果有标题）
        if tutorial.get('headings'):
            nav_items_html += f'                    <div class="nav-submenu">\n'
            for heading in tutorial['headings']:
                # 生成完整的锚点 ID（章节ID + 标题锚点）
                full_anchor = f"{tutorial['id']}-{heading['anchor']}"
                indent = '                        ' if heading['level'] == 3 else '                    '
                nav_items_html += f'{indent}<a href="#{full_anchor}" class="nav-item nav-sub" data-level="{heading["level"]}">{heading["text"]}</a>\n'
            nav_items_html += f'                    </div>\n'
        
        nav_items_html += f'                </div>\n'
        
        # 内容区域（所有内容都显示，连续排列）
        content_sections_html += f'            <section class="tutorial-section" id="{tutorial["id"]}">\n                <div class="content-wrapper">\n                    <div id="markdown-{tutorial["id"]}">加载中...</div>\n                </div>\n            </section>\n'
        
        # JavaScript 数据（包含标题信息）
        title_escaped = tutorial['title'].replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        headings_json = '[]'
        if tutorial.get('headings'):
            headings_list = []
            for heading in tutorial['headings']:
                text_escaped = heading['text'].replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
                headings_list.append(f'{{level: {heading["level"]}, text: "{text_escaped}", anchor: "{heading["anchor"]}"}}')
            headings_json = '[' + ', '.join(headings_list) + ']'
        
        tutorials_js_data.append(f'            {{ id: "{tutorial["id"]}", title: "{title_escaped}", content: `{tutorial["content"]}`, headings: {headings_json} }}')
    
    # 生成 JavaScript 代码
    script_code = generate_spa_script(tutorials_js_data)
    
    # 生成完整 HTML（传递 edp_center_path 以便使用本地 JS 库）
    html_content = generate_spa_html(nav_items_html, content_sections_html, script_code, edp_center_path)
    
    # 写入文件
    output_file.write_text(html_content, encoding='utf-8')
    print(f"✅ 已生成教程单页应用: {output_file}")
    print(f"📁 HTML 文件位置: {output_dir}")
    print(f"💡 提示: HTML 文件生成在用户可写目录，不会修改 edp_center 目录")
    
    return output_file

