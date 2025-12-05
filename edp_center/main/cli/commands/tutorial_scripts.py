#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tutorial Scripts - 教程 JavaScript 代码

存放所有 JavaScript 代码定义。
"""


def generate_spa_script(tutorials_js_data: list) -> str:
    """
    生成单页应用的 JavaScript 代码
    
    Args:
        tutorials_js_data: 教程数据列表（已转义的 JavaScript 字符串）
        
    Returns:
        JavaScript 代码字符串
    """
    tutorials_data_str = ',\n'.join(tutorials_js_data)
    
    return f"""        // 教程数据（全局变量，供搜索功能使用）
        const tutorials = [
{tutorials_data_str}
        ];
        
        // 等待页面和库加载完成
        function initTutorial() {{
            // 检查 marked 和 DOMPurify 是否已加载
            if (typeof marked === 'undefined') {{
                console.error('marked.js 未加载');
                document.querySelectorAll('[id^="markdown-"]').forEach(el => {{
                    el.innerHTML = '<p style="color: red;">❌ marked.js 加载失败，请检查网络连接。</p>';
                }});
                return;
            }}
            
            if (typeof DOMPurify === 'undefined') {{
                console.error('DOMPurify 未加载');
                document.querySelectorAll('[id^="markdown-"]').forEach(el => {{
                    el.innerHTML = '<p style="color: red;">❌ DOMPurify 加载失败，请检查网络连接。</p>';
                }});
                return;
            }}
            
            console.log('开始渲染教程内容，共', tutorials.length, '个教程');
            
            // 初始化：渲染所有教程内容
            tutorials.forEach(tutorial => {{
                try {{
                    let markdown = tutorial.content;
                    
                    // 移除返回目录链接
                    const backLinkPattern = '\\\\[←.*?\\\\]\\\\(.*?\\\\)';
                    const backLinkRegex = new RegExp(backLinkPattern, 'g');
                    markdown = markdown.replace(backLinkRegex, '');
                    
                    // 转换 .md 链接为锚点（在同一页面内跳转）
                    const mdLinkPattern = '\\\\[([^\\\\]]+)\\\\]\\\\(([^)]+\\\\.md)([^)]*)\\\\)';
                    const mdLinkRegex = new RegExp(mdLinkPattern, 'g');
                    markdown = markdown.replace(mdLinkRegex, (match, text, url, anchor) => {{
                        const mdPattern = '\\\\.md$';
                        const mdRegex = new RegExp(mdPattern);
                        const tutorialId = url.replace(mdRegex, '');
                        return '[' + text + '](#' + tutorialId + anchor + ')';
                    }});
                    
                    // 处理 TUTORIAL.md 链接
                    const tutorialLinkPattern = '\\\\[([^\\\\]]+)\\\\]\\\\(([^)]*TUTORIAL[^)]*\\\\.(md|html))([^)]*)\\\\)';
                    const tutorialLinkRegex = new RegExp(tutorialLinkPattern, 'gi');
                    markdown = markdown.replace(tutorialLinkRegex, (match, text, url, ext, anchor) => {{
                        return '[' + text + '](#01_quick_start' + anchor + ')';
                    }});
                    
                    // 使用 marked.js 渲染 Markdown
                    const html = marked.parse(markdown);
                    
                    // 使用 DOMPurify 清理 HTML
                    const cleanHtml = DOMPurify.sanitize(html);
                    
                    // 插入到页面
                    const contentEl = document.getElementById('markdown-' + tutorial.id);
                    if (contentEl) {{
                        contentEl.innerHTML = cleanHtml;
                        
                        // 为标题添加 ID 属性（用于锚点跳转）
                        if (tutorial.headings && tutorial.headings.length > 0) {{
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = cleanHtml;
                            
                            tutorial.headings.forEach(heading => {{
                                const fullAnchor = tutorial.id + '-' + heading.anchor;
                                // 查找对应的 h2 或 h3 元素
                                const headings = tempDiv.querySelectorAll('h' + heading.level);
                                headings.forEach(h => {{
                                    if (h.textContent.trim() === heading.text) {{
                                        h.id = fullAnchor;
                                    }}
                                }});
                            }});
                            
                            contentEl.innerHTML = tempDiv.innerHTML;
                        }}
                        
                        console.log('已渲染教程:', tutorial.id);
                    }} else {{
                        console.error('找不到元素: markdown-' + tutorial.id);
                    }}
                }} catch (error) {{
                    console.error('渲染教程失败:', tutorial.id, error);
                    const contentEl = document.getElementById('markdown-' + tutorial.id);
                    if (contentEl) {{
                        contentEl.innerHTML = '<p style="color: red;">❌ 渲染失败: ' + error.message + '</p>';
                    }}
                }}
            }});
            
            console.log('所有教程内容渲染完成');
        }}
        
        // 导航切换（使用锚点跳转，并监听滚动高亮当前章节）
        function initNavigation() {{
            const contentArea = document.querySelector('.content-area');
            const sections = document.querySelectorAll('.tutorial-section');
            const navItems = document.querySelectorAll('.nav-item');
            const navGroups = document.querySelectorAll('.nav-group');
            
            // 点击导航项时处理
            navItems.forEach(item => {{
                item.addEventListener('click', function(e) {{
                    const isMainItem = this.classList.contains('nav-main');
                    const navGroup = this.closest('.nav-group');
                    const hasSubmenu = navGroup && navGroup.querySelector('.nav-submenu');
                    
                    // 如果点击的是主目录项且有子目录，切换展开/折叠，不滚动
                    if (isMainItem && hasSubmenu) {{
                        navGroup.classList.toggle('expanded');
                        e.preventDefault();
                        e.stopPropagation();
                        return;
                    }}
                    
                    // 否则，执行滚动到对应章节
                    e.preventDefault();
                    const href = this.getAttribute('href');
                    if (href && href.startsWith('#')) {{
                        const targetId = href.substring(1);
                        const targetElement = document.getElementById(targetId);
                        
                        if (targetElement) {{
                            // 平滑滚动到目标元素
                            targetElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                            
                            // 更新 URL（不刷新页面）
                            history.pushState(null, '', '#' + targetId);
                            
                            // 如果是子目录，展开父目录
                            if (navGroup && !navGroup.classList.contains('expanded')) {{
                                navGroup.classList.add('expanded');
                            }}
                        }}
                    }}
                }});
            }});
            
            // 监听滚动，高亮当前可见的章节
            let scrollTimeout;
            function updateActiveNav() {{
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {{
                    const scrollTop = contentArea.scrollTop;
                    const viewportHeight = contentArea.clientHeight;
                    const scrollMiddle = scrollTop + viewportHeight / 2;
                    
                    // 找到当前最接近视口中心的章节
                    let activeSection = null;
                    let minDistance = Infinity;
                    
                    sections.forEach(section => {{
                        const sectionTop = section.offsetTop;
                        const sectionHeight = section.offsetHeight;
                        const sectionMiddle = sectionTop + sectionHeight / 2;
                        const distance = Math.abs(scrollMiddle - sectionMiddle);
                        
                        if (distance < minDistance && scrollTop + 100 >= sectionTop) {{
                            minDistance = distance;
                            activeSection = section;
                        }}
                    }});
                    
                    // 更新导航高亮
                    if (activeSection) {{
                        navItems.forEach(nav => nav.classList.remove('active'));
                        const activeNav = document.querySelector(`[data-tutorial-id="${{activeSection.id}}"]`);
                        if (activeNav) {{
                            activeNav.classList.add('active');
                        }}
                    }}
                }}, 100);
            }}
            
            // 监听滚动事件
            contentArea.addEventListener('scroll', updateActiveNav);
            
            // 初始更新一次
            updateActiveNav();
            
            // 默认展开第一个章节的子目录
            const firstNavGroup = document.querySelector('.nav-group');
            if (firstNavGroup) {{
                firstNavGroup.classList.add('expanded');
            }}
            
            // 处理浏览器前进/后退按钮
            window.addEventListener('popstate', function(e) {{
                const hash = window.location.hash.substring(1);
                if (hash) {{
                    const targetSection = document.getElementById(hash);
                    if (targetSection) {{
                        targetSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }}
            }});
            
            // 页面加载时如果有 hash，滚动到对应位置
            if (window.location.hash) {{
                const hash = window.location.hash.substring(1);
                const targetSection = document.getElementById(hash);
                if (targetSection) {{
                    setTimeout(() => {{
                        targetSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}, 500);
                }}
            }}
        }}
        
        // 页面加载完成后初始化
        function initAll() {{
            initTutorial();
            initNavigation();
        }}
        
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                // 等待 marked.js 和 DOMPurify 加载
                if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {{
                    initAll();
                }} else {{
                    window.addEventListener('load', initAll);
                }}
            }});
        }} else {{
            // 如果 DOM 已经加载完成
            if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {{
                initAll();
            }} else {{
                // 等待库加载
                window.addEventListener('load', initAll);
            }}
        }}"""

