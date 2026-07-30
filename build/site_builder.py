import os
import re
import json
import shutil
from datetime import datetime

from .utils import (
    extract_text_from_markdown,
    generate_last_modified_html,
    parse_frontmatter,
    flatten_articles,
)
from .markdown_renderer import (
    render_markdown,
    extract_toc_and_add_ids,
)
from .html_renderer import (
    render_list_page,
    render_article_header,
    render_page,
)


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


def cleanup_temp_files():
    """清理临时文件"""
    temp_files = ['log.txt']
    for f in temp_files:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f'Cleaned up: {f}')
            except Exception:
                pass


def build_site():
    cleanup_temp_files()
    
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
                        
                        # 标记代码块内的行号
                        lines = body.split('\n')
                        code_block_lines = set()
                        in_code_block = False
                        for i, line in enumerate(lines):
                            stripped = line.strip()
                            if stripped.startswith('```'):          # 围栏代码块开始/结束
                                in_code_block = not in_code_block
                                continue
                            if in_code_block:
                                code_block_lines.add(i)             # 该行在代码块内部

                        # 遍历所有匹配，但只保留非代码块内的
                        heading_matches = []
                        for match in re.finditer(r'^(#{1,4})\s+(.+)$', body, re.MULTILINE):
                            line_num = body[:match.start()].count('\n')
                            if line_num not in code_block_lines:
                                heading_matches.append(match)

                        # 使用过滤后的heading_matches构建标题及内容
                        headings = []
                        heading_contents = {}
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
                        
                        last_modified_html = generate_last_modified_html(actual_md_path)
                        
                        full_content = header_html + f'''
                    <div class="article-content">
                        {article_html}
                    </div>
                    {last_modified_html}'''
                        
                        if type_name == 'docs':
                            page_html = render_page(
                                title=f'{meta.get("title", "未命名文章")} - KeyBonk',
                                content=full_content,
                                has_sidebar=True,
                                nav_items=nav_items,
                                base_path=type_name,
                                active_path=md_rel_path,
                                toc=toc,
                                body_class='page-docs'
                            )
                        else:
                            page_html = render_page(
                                title=f'{meta.get("title", "未命名文章")} - KeyBonk',
                                content=full_content,
                                has_sidebar=False,
                                active_path=f'/{type_name}/{url_path}',
                                toc=toc,
                                body_class='page-blog'
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
