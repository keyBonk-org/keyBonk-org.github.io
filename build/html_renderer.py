from .config import NAV_LINKS, FOOTER


def render_toc_sidebar(toc):
    if not toc:
        return ''
    
    items_html = ''
    for item in toc:
        indent = (item['level'] - 2) * 12
        items_html += f'''
                        <a href="#{item['id']}" class="toc-link toc-level-{item['level']}" style="padding-left: {indent}px;">
                            {item['title']}
                        </a>'''
    
    return f'''
                <div class="toc-sidebar">
                    <div class="toc-title">目录</div>
                    <div class="toc-list">
                        {items_html}
                    </div>
                </div>'''


def render_navbar(active_path=None):
    links_html = ''
    for link in NAV_LINKS:
        is_active = False
        if active_path:
            normalized_active = active_path.rstrip('/')
            normalized_link = link['path'].rstrip('/')
            if normalized_active == normalized_link:
                is_active = True
            elif normalized_link == '/index.html' and normalized_active == '':
                is_active = True
            elif normalized_link != '/index.html' and normalized_active.startswith(normalized_link):
                is_active = True
        
        active_class = ' class="active"' if is_active else ''
        links_html += f'''
                <li>
                    <a href="{link['path']}"{active_class}>
                        {link['label']}
                    </a>
                </li>'''
    
    navbar = f'''
        <nav id="navbar" style="display: block;">
            <div class="navbar-container">
                <div class="navbar-brand">
                    <a href="/index.html">
                        <img src="/imgs/icon.png" alt="KeyBonk Logo" class="navbar-logo">
                        KeyBonk
                    </a>
                </div>
                <ul class="navbar-links">
                    {links_html}
                </ul>
                <div class="navbar-right">
                    <div class="search-box">
                        <input type="text" placeholder="搜索...">
                        <img src="/imgs/UI/search.png" class="search-icon" alt="搜索">
                    </div>
                    <a href="https://github.com/keyBonk-org" target="_blank" class="github-link" title="GitHub">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                    </a>
                    <button class="theme-toggle" title="切换主题">
                        <img src="/imgs/UI/dark_mood.png" class="theme-toggle-icon" alt="切换主题">
                    </button>
                    <button class="menu-toggle" title="菜单">
                        <img src="/imgs/UI/menu.png" class="menu-icon" alt="菜单">
                    </button>
                </div>
            </div>
            <div class="mobile-menu">
                <div class="mobile-menu-overlay"></div>
            </div>
        </nav>'''
    return navbar


def render_sidebar(nav_items, base_path, current_path=None):
    def contains_current(item, cpath):
        if not cpath:
            return False
        if item.get('url_path') == cpath:
            return True
        if item.get('path') == cpath:
            return True
        for child in item.get('children', []):
            if contains_current(child, cpath):
                return True
        return False

    def render_items(items, base, cpath):
        html = ''
        for item in items:
            has_children = 'children' in item and item['children']
            is_active = cpath and (cpath == item.get('url_path') or cpath == item.get('path'))
            active_class = ' active' if is_active else ''
            
            if item.get('is_dir'):
                arrow = ''
                toggle_class = ''
                children_html = ''
                
                if has_children:
                    arrow = '<span class="sidebar-arrow" onclick="var item=this.closest(\'.sidebar-item\'); item.classList.toggle(\'collapsed\'); event.stopPropagation();">▶</span>'
                    should_expand = contains_current(item, cpath)
                    collapsed_class = '' if should_expand else ' collapsed'
                    toggle_class = f' has-children{collapsed_class}'
                    children_html = f'''
                        <div class="sidebar-children">
                            {render_items(item['children'], base, cpath)}
                        </div>'''
                
                href = f'/{base}/{item["url_path"]}/' if item.get('url_path') else '#'
                html += f'''
                        <div class="sidebar-item{toggle_class}{active_class}">
                            <div class="sidebar-item-header">
                                {arrow}
                                <a href="{href}" class="sidebar-item-title">{item["title"]}</a>
                            </div>
                            {children_html}
                        </div>'''
            else:
                href = f'/{base}/{item["url_path"]}/'
                html += f'''
                        <div class="sidebar-item{active_class}">
                            <div class="sidebar-item-header">
                                <a href="{href}" class="sidebar-item-title">{item["title"]}</a>
                            </div>
                        </div>'''
        return html
    
    return f'''
                <div class="content-sidebar" id="contentSidebar">
                    <div class="content-sidebar-inner-left"></div>
                    <div class="sidebar-tree" id="sidebarTree">
                        {render_items(nav_items, base_path, current_path)}
                    </div>
                </div>'''


def render_article_header(meta):
    if not meta:
        return ''
    
    tags_html = ''
    full_tags_html = ''
    if meta.get('tags'):
        tags_list = meta['tags']
        tags_html = '<div class="meta-tags">' + ''.join(
            f'<span class="tag">{tag}</span>' for tag in tags_list
        ) + '</div>'
        full_tags_html = '<div class="full-meta-tags">' + ''.join(
            f'<span class="tag">{tag}</span>' for tag in tags_list
        ) + '</div>'
    
    author_html = ''
    full_author_html = ''
    authors = meta.get('author')
    if authors:
        if isinstance(authors, list):
            author_items = []
            for author in authors:
                if isinstance(author, dict):
                    name = author.get('name', '')
                    avatar = author.get('avatar', '')
                else:
                    name = str(author)
                    avatar = ''
                avatar_html = f'<img src="{avatar}" alt="{name}" class="meta-avatar">' if avatar else ''
                author_items.append(f'<span class="meta-author">{avatar_html}{name}</span>')
            author_html = '<div class="meta-authors">' + ''.join(author_items) + '</div>'
            full_author_html = '<div class="full-meta-authors">' + ''.join(author_items) + '</div>'
        else:
            avatar_html = f'<img src="{meta["avatar"]}" alt="{authors}" class="meta-avatar">' if meta.get('avatar') else ''
            author_html = f'<span class="meta-author">{avatar_html}{authors}</span>'
            full_author_html = f'<span class="meta-author">{avatar_html}{authors}</span>'
    
    has_extra = (isinstance(authors, list) and len(authors) > 2) or (meta.get('tags') and len(meta['tags']) > 3)
    
    meta_content = f'''
                                {author_html}
                                {f'<span class="meta-date">{meta.get("date", "")}</span>' if meta.get('date') else ''}
                                {tags_html}'''
    
    expand_btn_html = ''
    if has_extra:
        expand_btn_html = f'''
                            <button class="meta-expand-btn" onclick="toggleMetaPopup(this)">...</button>'''
    
    popup_html = ''
    if has_extra:
        popup_html = f'''
                    <div class="meta-popup" id="metaPopup">
                        <div class="meta-popup-overlay" onclick="closeMetaPopup()"></div>
                        <div class="meta-popup-content">
                            <div class="meta-popup-header">
                                <h4>文章信息</h4>
                                <button class="meta-popup-close" onclick="closeMetaPopup()">×</button>
                            </div>
                            <div class="meta-popup-body">
                                {full_author_html}
                                {f'<div class="meta-popup-date">{meta.get("date", "")}</div>' if meta.get('date') else ''}
                                {full_tags_html}
                            </div>
                        </div>
                    </div>'''
    
    return f'''
                    <div class="article-header">
                        <h1>{meta.get('title', '未命名文章')}</h1>
                        <div class="article-meta">
                            <div class="meta-truncated">
                                {meta_content}
                            </div>
                            {expand_btn_html}
                        </div>
                        {popup_html}
                    </div>'''


def render_list_page(type, nav_items, active_path=None):
    from .utils import flatten_articles
    
    if type == 'docs':
        articles = [item for item in nav_items if item.get('path')]
    else:
        articles = flatten_articles(nav_items)
    
    if type == 'blog':
        def parse_date(s):
            from datetime import datetime
            if isinstance(s, datetime):
                return s
            if not s:
                return datetime.min
            if isinstance(s, str):
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', 
                            '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y/%m/%d'):
                    try:
                        return datetime.strptime(s, fmt)
                    except (ValueError, TypeError):
                        continue
            return datetime.min
        
        articles.sort(key=lambda x: (x.get('weight', 0) != 0, -x.get('weight', 0), parse_date(x.get('date', ''))), reverse=True)
    else:
        articles.sort(key=lambda x: (x.get('weight', 0), x['title']))
    
    title = '文档' if type == 'docs' else '博客'
    
    articles_html = '<div class="article-list">'
    for article in articles:
        url = article.get('url_path', article['path'])
        is_pinned = article.get('weight', 0) != 0 and type == 'blog'
        pinned_badge = '<span class="pinned-badge">置顶</span>' if is_pinned else ''
        
        authors = article.get('author')
        author_html = ''
        if authors:
            if isinstance(authors, list):
                author_names = []
                for author in authors:
                    if isinstance(author, dict):
                        author_names.append(author.get('name', ''))
                    else:
                        author_names.append(str(author))
                author_html = f'<span>{", ".join(author_names)}</span>'
            else:
                author_html = f'<span>{authors}</span>'
        
        articles_html += f'''
            <a href="/{type}/{url}/" target="_blank" class="article-card">
                <h3>{pinned_badge}{article['title']}</h3>
                <p>{article.get('summary', '')}</p>
                <div class="article-card-meta">
                    {f'<span>{article.get("date", "")}</span>' if article.get('date') else ''}
                    {author_html}
                </div>
            </a>'''
    articles_html += '</div>'
    
    content = f'<h2>{title}</h2>{articles_html}'
    
    if type == 'docs':
        return render_page(
            title=f'KeyBonk - {title}',
            content=content,
            has_sidebar=True,
            nav_items=nav_items,
            base_path=type,
            active_path=active_path,
            body_class='page-docs-index'
        )
    else:
        return render_page(
            title=f'KeyBonk - {title}',
            content=content,
            has_sidebar=False,
            active_path=active_path,
            body_class='page-blog-home'
        )


def render_page(title, content, has_sidebar=False, nav_items=None, base_path=None, active_path=None, toc=None, body_class=None):
    navbar = render_navbar(active_path)
    toc_html = render_toc_sidebar(toc) if toc else ''
    
    body_class_attr = f' class="{body_class}"' if body_class else ''
    
    if has_sidebar and nav_items and base_path:
        sidebar_html = render_sidebar(nav_items, base_path, active_path)
        layout_class = ' content-page-has-toc' if toc else ''
        main_content = f'''
            <div class="content-page{layout_class}">
                {sidebar_html}
                <div class="content-main">
                    {content}
                </div>
                {toc_html}
            </div>'''
    else:
        layout_class = ' content-page-has-toc' if toc else ''
        main_content = f'''
            <div class="content-page blog-page{layout_class}">
                <div class="content-main">
                    {content}
                </div>
                {toc_html}
            </div>'''
    
    meta_script = '''    <script>
        Navbar.init();
        hljs.highlightAll();

        function toggleMetaPopup(btn) {
            var popup = document.getElementById('metaPopup');
            if (popup) {
                popup.classList.toggle('active');
            }
        }

        function closeMetaPopup() {
            var popup = document.getElementById('metaPopup');
            if (popup) {
                popup.classList.remove('active');
            }
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeMetaPopup();
            }
        });
    </script>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="icon" href="/imgs/icon.ico" type="image/x-icon">
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/highlight.css" id="hljs-light">
    <link rel="stylesheet" href="/css/github-dark.min.css" id="hljs-dark" disabled>
</head>
<body{body_class_attr}>
    <div id="app">
        {navbar}
        <main id="main-content">
            {main_content}
        </main>
        {FOOTER}
    </div>

    <script src="/js/lib/highlight.min.js"></script>
    <script src="/js/lib/powershell.min.js"></script>
    <script src="/js/lib/diff.min.js"></script>
    <script src="/js/lib/rust.min.js"></script>
    <script src="/js/lib/vim.min.js"></script>
    <script src="/js/lib/cmake.min.js"></script>
    <script src="/js/lib/yaml.min.js"></script>
    <script src="/js/lib/dos.min.js"></script>
    <script src="/js/search.js"></script>
    <script src="/js/components/navbar.js"></script>
{meta_script}
</body>
</html>'''
    
    return html
