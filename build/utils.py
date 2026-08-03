import os
import re
import json
import yaml
import subprocess
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
    """
    获取文件的最后修改时间（优先使用 Git 提交时间，失败时回退到文件系统 mtime）
    返回格式：'%Y-%m-%d %H:%M' 或 None
    """
    try:
        abs_path = os.path.abspath(filepath)
        # 尝试获取 Git 仓库根目录
        git_root = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=os.path.dirname(abs_path),
            stderr=subprocess.DEVNULL
        ).decode().strip()
        # 计算文件相对于仓库根目录的路径
        rel_path = os.path.relpath(abs_path, git_root)
        # 获取该文件最后一次提交的 Unix 时间戳
        timestamp_str = subprocess.check_output(
            ['git', 'log', '-1', '--format=%at', '--', rel_path],
            cwd=git_root,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if timestamp_str:
            timestamp = int(timestamp_str)
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M')
        # 若文件从未提交（新文件），则回退到文件系统时间
    except (subprocess.CalledProcessError, FileNotFoundError, Exception):
        # git 命令失败或不在 git 仓库中，继续执行回退逻辑
        pass

    # 回退：使用操作系统的文件修改时间
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
