import os
import re
import json
import shutil
import yaml
from datetime import datetime
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.subscript import sub_plugin
from mdit_py_plugins.superscript import superscript_plugin
from mdit_py_plugins.admon import admon_plugin
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.colon_fence import colon_fence_plugin

NAV_LINKS = [
    {'path': '/index.html', 'label': '首页'},
    {'path': '/about/', 'label': '关于'},
    {'path': '/projects/', 'label': '项目表'},
    {'path': '/blog/', 'label': '博客'},
    {'path': '/docs/', 'label': '文档'},
]

FOOTER = '''
        <footer class="site-footer">
            <div class="footer-container">
                <div class="footer-brand">
                    <img src="/imgs/icon.png" alt="KeyBonk Logo" class="footer-logo">
                    <span class="footer-brand-text">KeyBonk</span>
                    <p class="footer-tagline">让每一次按键掷地有声</p>
                </div>
                <div class="footer-links">
                    <h4 class="footer-heading">导航</h4>
                    <a href="/index.html">首页</a>
                    <a href="/about/">关于</a>
                    <a href="/projects/">项目表</a>
                    <a href="/blog/">博客</a>
                    <a href="/docs/">文档</a>
                </div>
                <div class="footer-community">
                    <h4 class="footer-heading">社区</h4>
                    <a href="https://github.com/keyBonk-org" target="_blank" rel="noopener noreferrer">GitHub</a>
                    <a href="https://github.com/keyBonk-org/KeyBonk/releases/latest" target="_blank" rel="noopener noreferrer">最新发布</a>
                </div>
                <div class="footer-friends">
                    <h4 class="footer-heading">友链</h4>
                    <a href="https://xiaoditx.github.io" target="_blank" rel="noopener noreferrer">小狄の站</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 KeyBonk. WTFPL 协议开源。</p>
            </div>
        </footer>
'''

def extract_text_from_markdown(md_content):
    text = md_content
    
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', text)
    
    text = re.sub(r'<[^>]+>', '', text)
    
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'~~([^~]+)~~', r'\1', text)
    
    text = re.sub(r'^(\s*[-*+]\s+)+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^\s*!!!\s*\w+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*:::\s*\w*\s*$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'\$\$[\s\S]*?\$\$', '', text)
    text = re.sub(r'\$[^$]+\$', '', text)
    
    text = re.sub(r'\[\^[\w]+\]', '', text)
    text = re.sub(r'^\[\^[\w]+\]:', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^\s*-{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\*{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*_{3,}\s*$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'\|\s*---\s*\|', ' ', text)
    
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def parse_frontmatter(content):
    trimmed = content.strip()
    meta = {}
    body = content
    
    if trimmed.startswith('---'):
        end_match = re.search(r'^\s*---\s*$', trimmed[3:], re.MULTILINE)
        if end_match:
            yaml_content = trimmed[3:3 + end_match.start()].strip()
            try:
                meta = yaml.safe_load(yaml_content) or {}
                body = trimmed[3 + end_match.end():].strip()
            except:
                pass
    elif trimmed.startswith('{'):
        brace_count = 0
        json_end_index = -1
        for i, char in enumerate(trimmed):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end_index = i
                    break
        
        if json_end_index > 0:
            try:
                meta = json.loads(trimmed[:json_end_index + 1])
                body = trimmed[json_end_index + 1:].strip()
            except:
                pass
    
    return meta, body

def render_markdown(content):
    md = MarkdownIt('commonmark', {
        'html': True,
        'linkify': True,
        'typographer': True,
    }).enable('table')
    
    md.use(tasklists_plugin)
    md.use(footnote_plugin)
    md.use(deflist_plugin)
    md.use(sub_plugin)
    md.use(superscript_plugin)
    md.use(admon_plugin)
    md.use(container_plugin, name="note")
    md.use(container_plugin, name="tip")
    md.use(container_plugin, name="warning")
    md.use(container_plugin, name="danger")
    md.use(container_plugin, name="info")
    md.use(dollarmath_plugin)
    md.use(colon_fence_plugin)
    
    html = md.render(content)
    return html

def slugify(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

def extract_toc_and_add_ids(html):
    toc = []
    id_map = {}
    
    def add_id(match):
        level = int(match.group(1))
        title_html = match.group(2)
        title_text = re.sub(r'<[^>]+>', '', title_html).strip()
        
        slug = slugify(title_text)
        base_slug = slug
        count = 1
        while slug in id_map:
            count += 1
            slug = f'{base_slug}-{count}'
        id_map[slug] = True
        
        toc.append({'level': level, 'title': title_text, 'id': slug})
        return f'<h{level} id="{slug}">{title_html}</h{level}>'
    
    processed = re.sub(r'<h([2-4])>(.*?)</h\1>', add_id, html, flags=re.DOTALL)
    return processed, toc

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
                    <div class="sidebar-tree" id="sidebarTree">
                        {render_items(nav_items, base_path, current_path)}
                    </div>
                </div>'''

def render_article_header(meta):
    if not meta:
        return ''
    
    tags_html = ''
    if meta.get('tags'):
        tags_html = '<div class="meta-tags">' + ''.join(
            f'<span class="tag">{tag}</span>' for tag in meta['tags']
        ) + '</div>'
    
    author_html = ''
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
        else:
            avatar_html = f'<img src="{meta["avatar"]}" alt="{authors}" class="meta-avatar">' if meta.get('avatar') else ''
            author_html = f'<span class="meta-author">{avatar_html}{authors}</span>'
    
    return f'''
                    <div class="article-header">
                        <h1>{meta.get('title', '未命名文章')}</h1>
                        <div class="article-meta">
                            {author_html}
                            {f'<span class="meta-date">{meta.get("date", "")}</span>' if meta.get('date') else ''}
                            {tags_html}
                        </div>
                    </div>'''

def scan_directory(base_path, current_path=""):
    result = []
    
    full_path = os.path.join(base_path, current_path)
    if not os.path.isdir(full_path):
        return result
    
    for entry in sorted(os.listdir(full_path)):
        entry_path = os.path.join(current_path, entry)
        full_entry_path = os.path.join(base_path, entry_path)
        
        if entry.startswith('_') or entry.startswith('.'):
            continue
        
        if os.path.isdir(full_entry_path):
            children = scan_directory(base_path, entry_path)
            
            index_path = os.path.join(full_entry_path, 'index.md')
            has_index = os.path.exists(index_path)
            
            title = entry
            date = None
            author = None
            summary = None
            weight = 0
            id_val = None
            
            if has_index:
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    meta, _ = parse_frontmatter(content)
                    if meta:
                        title = meta.get('title', entry)
                        date = meta.get('date')
                        author = meta.get('author')
                        summary = meta.get('summary')
                        weight = meta.get('weight', 0)
                        id_val = meta.get('id')
            
            nav_path = entry_path.replace('\\', '/') if has_index else None
            url_path = id_val if id_val else nav_path
            
            if not has_index and children:
                first = children[0]
                if first.get('path'):
                    nav_path = first['path']
                    url_path = first.get('url_path', first['path'])
            
            item = {
                'title': title,
                'path': nav_path,
                'url_path': url_path,
                'date': date,
                'author': author,
                'summary': summary,
                'weight': weight,
                'is_dir': True
            }
            
            if children:
                item['children'] = children
            
            result.append(item)
        
        elif entry.endswith('.md') and entry != 'index.md':
            name = os.path.splitext(entry)[0]
            title = name
            date = None
            author = None
            summary = None
            weight = 0
            id_val = None
            
            with open(full_entry_path, 'r', encoding='utf-8') as f:
                content = f.read()
                meta, _ = parse_frontmatter(content)
                if meta:
                    title = meta.get('title', name)
                    date = meta.get('date')
                    author = meta.get('author')
                    summary = meta.get('summary')
                    weight = meta.get('weight', 0)
                    id_val = meta.get('id')
            
            nav_path = entry_path.replace('.md', '').replace('\\', '/')
            url_path = id_val if id_val else nav_path
            
            result.append({
                'title': title,
                'path': nav_path,
                'url_path': url_path,
                'date': date,
                'author': author,
                'summary': summary,
                'weight': weight,
                'is_dir': False
            })
    
    result.sort(key=lambda x: (x.get('weight', 0), x['title']))
    return result

def flatten_articles(items):
    result = []
    def traverse(arr):
        for item in arr:
            if 'children' in item:
                traverse(item['children'])
            elif item.get('path'):
                result.append(item)
    traverse(items)
    return result

def render_list_page(type, nav_items, active_path=None):
    if type == 'docs':
        articles = [item for item in nav_items if item.get('path')]
    else:
        articles = flatten_articles(nav_items)
    
    if type == 'blog':
        def parse_date(s):
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
            active_path=active_path
        )
    else:
        return render_page(
            title=f'KeyBonk - {title}',
            content=content,
            has_sidebar=False,
            active_path=active_path
        )

def render_page(title, content, has_sidebar=False, nav_items=None, base_path=None, active_path=None, toc=None):
    navbar = render_navbar(active_path)
    toc_html = render_toc_sidebar(toc) if toc else ''
    
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
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="icon" href="/imgs/icon.ico" type="image/x-icon">
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/highlight.css">
</head>
<body>
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
    <script>
        Navbar.init();
        hljs.highlightAll();
    </script>
</body>
</html>'''
    
    return html

def build_site():
    content_dir = 'content'
    output_dirs = {
        'docs': 'docs',
        'blog': 'blog'
    }
    
    search_index = []
    
    for type_name, output_dir in output_dirs.items():
        content_type_dir = os.path.join(content_dir, type_name)
        if not os.path.exists(content_type_dir):
            print(f'Skipping {type_name}: content directory not found')
            continue
        
        nav_items = scan_directory(content_type_dir)
        
        if os.path.exists(output_dir):
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                if os.path.isdir(item_path) and item != 'content':
                    shutil.rmtree(item_path)
                elif item.endswith('.html'):
                    os.remove(item_path)
        
        list_html = render_list_page(type_name, nav_items, f'/{type_name}/')
        index_path = os.path.join(output_dir, 'index.html')
        os.makedirs(output_dir, exist_ok=True)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(list_html)
        print(f'Generated {type_name} index: {index_path}')
        
        def build_pages(items, current_path=""):
            for item in items:
                if 'children' in item and item['children']:
                    build_pages(item['children'], os.path.join(current_path, item.get('url_path', item['path'])) if item.get('path') else current_path)
                
                if item.get('path'):
                    md_rel_path = item['path']
                    url_path = item.get('url_path', md_rel_path)
                    md_path = os.path.join(content_type_dir, md_rel_path + '.md')
                    index_md_path = os.path.join(content_type_dir, md_rel_path, 'index.md')
                    
                    actual_md_path = None
                    if os.path.exists(md_path):
                        actual_md_path = md_path
                    elif os.path.exists(index_md_path):
                        actual_md_path = index_md_path
                    
                    if actual_md_path:
                        with open(actual_md_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        meta, body = parse_frontmatter(content)
                        
                        plain_text = extract_text_from_markdown(body)
                        
                        headings = []
                        heading_contents = {}
                        heading_matches = list(re.finditer(r'^(#{1,4})\s+(.+)$', body, re.MULTILINE))
                        
                        for i, match in enumerate(heading_matches):
                            level = len(match.group(1))
                            text = match.group(2).strip()
                            headings.append({
                                'level': level,
                                'text': text
                            })
                            
                            if i < len(heading_matches) - 1:
                                next_match = heading_matches[i + 1]
                                content_between = body[match.end():next_match.start()].strip()
                            else:
                                content_between = body[match.end():].strip()
                            
                            heading_contents[text] = extract_text_from_markdown(content_between)
                        
                        search_index.append({
                            'title': meta.get('title', ''),
                            'url': f'/{type_name}/{url_path}/',
                            'content': body,
                            'plain_text': plain_text,
                            'type': type_name,
                            'headings': headings,
                            'heading_contents': heading_contents,
                            'full_path': url_path
                        })
                        
                        article_html = render_markdown(body)
                        article_html, toc = extract_toc_and_add_ids(article_html)
                        header_html = render_article_header(meta)
                        
                        full_content = header_html + f'''
                    <div class="article-content">
                        {article_html}
                    </div>'''
                        
                        if type_name == 'docs':
                            page_html = render_page(
                                title=f'{meta.get("title", "未命名文章")} - KeyBonk',
                                content=full_content,
                                has_sidebar=True,
                                nav_items=nav_items,
                                base_path=type_name,
                                active_path=md_rel_path,
                                toc=toc
                            )
                        else:
                            page_html = render_page(
                                title=f'{meta.get("title", "未命名文章")} - KeyBonk',
                                content=full_content,
                                has_sidebar=False,
                                active_path=f'/{type_name}/{url_path}',
                                toc=toc
                            )
                        
                        dir_path = os.path.join(output_dir, url_path, 'index.html')
                        os.makedirs(os.path.dirname(dir_path), exist_ok=True)
                        with open(dir_path, 'w', encoding='utf-8') as f:
                            f.write(page_html)
                        print(f'Generated {type_name}/{url_path}/ (index.html)')
        
        build_pages(nav_items)
    
    search_index_path = os.path.join('js', 'search_index.json')
    os.makedirs(os.path.dirname(search_index_path), exist_ok=True)
    with open(search_index_path, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False)
    print(f'Generated search index: {search_index_path}')
    
    print('\nBuild complete!')

if __name__ == '__main__':
    build_site()