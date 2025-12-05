#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial Styles - 教程样式定义

存放所有 CSS 样式定义。
"""

# 单页应用样式（左侧目录，右侧内容）
SPA_STYLE = """        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            overflow: hidden;
        }
        .app-container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .sidebar-header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .sidebar-header h1 {
            font-size: 1.5em;
            margin-bottom: 5px;
            border: none;
            padding: 0;
        }
        .sidebar-header p {
            font-size: 0.9em;
            opacity: 0.9;
            margin: 0;
        }
        .sidebar-nav {
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
        }
        .nav-group {
            margin-bottom: 5px;
        }
        .nav-item {
            display: block;
            padding: 12px 20px;
            color: #333;
            text-decoration: none;
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }
        .nav-item.nav-main {
            font-weight: 600;
            font-size: 1em;
        }
        .nav-item.nav-sub {
            font-weight: 400;
            font-size: 0.9em;
            padding-left: 35px;
            color: #666;
        }
        .nav-item.nav-sub[data-level="3"] {
            padding-left: 50px;
            font-size: 0.85em;
            color: #888;
        }
        .nav-item:hover {
            background: #f8f9fa;
            border-left-color: #667eea;
        }
        .nav-item.active {
            background: #e8f0fe;
            border-left-color: #667eea;
            color: #667eea;
            font-weight: 600;
        }
        .nav-submenu {
            display: block;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }
        .nav-submenu.expanded,
        .nav-group.expanded .nav-submenu {
            max-height: 2000px;
            transition: max-height 0.5s ease-in;
        }
        .content-area {
            flex: 1;
            overflow-y: auto;
            background: white;
        }
        .content-wrapper {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px;
        }
        .content-wrapper h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        .content-wrapper h2 {
            color: #34495e;
            font-size: 2em;
            margin-top: 40px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #ecf0f1;
        }
        .content-wrapper h3 {
            color: #7f8c8d;
            font-size: 1.5em;
            margin-top: 30px;
            margin-bottom: 12px;
        }
        .content-wrapper h4 {
            color: #95a5a6;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .content-wrapper p {
            margin: 15px 0;
            text-align: justify;
        }
        .content-wrapper code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }
        .content-wrapper pre {
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .content-wrapper pre code {
            background-color: transparent;
            padding: 0;
            color: inherit;
            font-size: 0.9em;
            line-height: 1.5;
        }
        .content-wrapper ul, .content-wrapper ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        .content-wrapper li {
            margin: 8px 0;
        }
        .content-wrapper a {
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.3s;
        }
        .content-wrapper a:hover {
            border-bottom-color: #667eea;
        }
        .content-wrapper strong {
            color: #2c3e50;
            font-weight: 600;
        }
        .content-wrapper em {
            color: #7f8c8d;
            font-style: italic;
        }
        .content-wrapper blockquote {
            border-left: 4px solid #667eea;
            margin: 20px 0;
            padding-left: 20px;
            color: #7f8c8d;
            font-style: italic;
        }
        .search-highlight {
            background: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 600;
        }
        .tutorial-section {
            min-height: 100vh;
            padding: 40px 0;
            border-bottom: 2px solid #e0e0e0;
        }
        .tutorial-section:last-child {
            border-bottom: none;
        }
        .tutorial-section:target {
            scroll-margin-top: 20px;
        }"""

