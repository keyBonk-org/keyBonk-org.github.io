import re
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
