#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial HTML Templates - 教程 HTML 模板生成

负责生成 HTML 模板结构。
"""

from typing import List, Optional
from pathlib import Path


def generate_spa_html(nav_items_html: str, content_sections_html: str, script_code: str, edp_center_path: Optional[Path] = None) -> str:
    """
    生成单页应用的 HTML 结构
    
    Args:
        nav_items_html: 导航项 HTML
        content_sections_html: 内容区域 HTML
        script_code: JavaScript 代码
        edp_center_path: edp_center 路径（用于查找本地 JS 库文件）
        
    Returns:
        完整的 HTML 内容
    """
    from .tutorial_styles import SPA_STYLE
    
    # 确定 JS 库的加载方式（优先使用本地文件）
    marked_js_src = "https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js"
    dompurify_js_src = "https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.min.js"
    
    if edp_center_path:
        # 检查本地库文件是否存在（HTML 文件在 edp_center/tutorial/，libs 也在同一目录下）
        libs_dir = edp_center_path / 'tutorial' / 'libs'
        marked_local = libs_dir / 'marked.min.js'
        dompurify_local = libs_dir / 'purify.min.js'
        
        # 调试信息
        import sys
        print(f"🔍 检查本地库文件:", file=sys.stderr)
        print(f"   edp_center_path: {edp_center_path}", file=sys.stderr)
        print(f"   libs_dir: {libs_dir}", file=sys.stderr)
        print(f"   marked_local: {marked_local} (exists: {marked_local.exists()})", file=sys.stderr)
        print(f"   dompurify_local: {dompurify_local} (exists: {dompurify_local.exists()})", file=sys.stderr)
        
        if marked_local.exists():
            # 使用相对路径（HTML 文件在 tutorial/，libs 在 tutorial/libs/）
            marked_js_src = "./libs/marked.min.js"
            print(f"   ✓ 使用本地 marked.js", file=sys.stderr)
        else:
            print(f"   ⚠️  使用 CDN marked.js（本地文件不存在）", file=sys.stderr)
        
        if dompurify_local.exists():
            dompurify_js_src = "./libs/purify.min.js"
            print(f"   ✓ 使用本地 DOMPurify", file=sys.stderr)
        else:
            print(f"   ⚠️  使用 CDN DOMPurify（本地文件不存在）", file=sys.stderr)
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDP AI 教程</title>
    <script src="{marked_js_src}"></script>
    <script src="{dompurify_js_src}"></script>
    <style>
{SPA_STYLE}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- 左侧目录 -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>📚 EDP AI 教程</h1>
                <p>欢迎使用 EDP_AI 框架</p>
            </div>
            <nav class="sidebar-nav">
{nav_items_html}            </nav>
        </div>
        
        <!-- 右侧内容 -->
        <div class="content-area">
{content_sections_html}        </div>
    </div>
    
    <script>
{script_code}
    </script>
</body>
</html>
"""

