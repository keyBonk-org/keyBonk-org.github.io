import os
import re
import json
import yaml
from datetime import datetime


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


def get_file_last_modified(filepath):
    try:
        mtime = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return None


def generate_last_modified_html(filepath):
    last_modified = get_file_last_modified(filepath)
    if last_modified:
        return f'<div class="article-last-modified">最后一次修改时间：{last_modified}</div>'
    return ''


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
