#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_sitemap.py - 生成 sitemap.xml（单参数版本）
用法:
    python generate_sitemap.py https://example.com
"""

import os
import sys
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# ========== 可调整的固定配置 ==========
ROOT_DIR = '.'               # 扫描的根目录（当前目录）
OUTPUT_FILE = 'sitemap.xml'  # 输出文件名
EXCLUDE_DIRS = {'.git', '.svn', '.hg', '.idea', '.vscode', '__pycache__'}
# =====================================

def get_lastmod(filepath):
    """获取文件的最后修改时间（W3C 格式）"""
    try:
        mtime = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    except OSError:
        return None

def build_urlset(base_url):
    """扫描目录，生成 <urlset> 元素"""
    urlset = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    base = base_url.rstrip('/')

    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # 过滤排除目录
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in EXCLUDE_DIRS]

        for filename in filenames:
            if not filename.lower().endswith('.html'):
                continue

            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, ROOT_DIR)
            url_path = rel_path.replace(os.sep, '/')
            url = f"{base}/{url_path}"

            url_elem = SubElement(urlset, 'url')
            loc = SubElement(url_elem, 'loc')
            loc.text = url

            lastmod_str = get_lastmod(full_path)
            if lastmod_str:
                lastmod = SubElement(url_elem, 'lastmod')
                lastmod.text = lastmod_str

    return urlset

def prettify(elem):
    """格式化 XML"""
    rough = tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent='  ')

def main():
    if len(sys.argv) != 2:
        print("用法: python generate_sitemap.py <base-url>")
        print("示例: python generate_sitemap.py https://example.com")
        sys.exit(1)

    base_url = sys.argv[1]
    print(f"扫描目录: {os.path.abspath(ROOT_DIR)}")
    print(f"基础 URL: {base_url}")
    print(f"输出文件: {OUTPUT_FILE}")

    urlset = build_urlset(base_url)
    pretty_xml = prettify(urlset)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    count = len(urlset.findall('url'))
    print(f"成功生成 {OUTPUT_FILE}，共 {count} 个 URL")

if __name__ == '__main__':
    main()