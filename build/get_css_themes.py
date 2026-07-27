#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Highlight.js CSS 主题下载工具

功能：
  - 列出所有可用主题
  - 按关键词搜索主题（支持部分匹配）
  - 交互式搜索 → 显示匹配列表 → 用户选择序号下载
  - 命令行直接搜索并下载全部匹配（带 -y 参数）
  - 精确指定主题名称下载

依赖：
  - Python 3.6+（仅使用标准库）

使用示例：
  1. 交互式搜索（推荐）
     python get_css_themes.py
     然后输入关键词（如 "dark"），选择序号下载。

  2. 列出所有可用主题
     python get_css_themes.py --list

  3. 命令行搜索并下载所有匹配的主题（跳过交互，直接下载全部）
     python get_css_themes.py -s dark -y
     或
     python get_css_themes.py -s dark github -y   # 多个关键词（或关系）

  4. 精确下载指定的主题
     python get_css_themes.py -l github-dark atom-one-dark

  5. 指定版本和输出目录
     python get_css_themes.py -l github-dark -v 11.11.1 -o ./my_themes

交互式流程说明：
  1. 运行脚本无参数，提示输入搜索关键词。
  2. 输入关键词（支持空格分隔多个），显示匹配的主题列表。
  3. 输入序号（如 1 2 3）或 'all'，选择要下载的主题。
  4. 确认下载后，开始下载选中的主题文件。

其他参数：
  -h, --help          显示帮助信息
  -l, --theme         精确指定要下载的主题名称（多个用空格分隔）
  -s, --search        搜索关键词，下载所有匹配的主题（需配合 -y 跳过确认）
  -y, --yes           跳过确认，直接下载（仅与 -s 配合使用）
  -v, --version       指定版本号（默认自动获取最新稳定版）
  -o, --output        输出目录（默认为当前目录）
  --list              列出所有可用主题（不下载）

注意：
  - 网络请求需要连接 GitHub 和 cdnjs，请确保网络畅通。
  - 下载的文件为 .min.css，可直接用于 highlight.js 样式引用。
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import List, Optional

# ---------- 内置备用主题列表（基于 Highlight.js v11.x 官方主题） ----------
DEFAULT_THEMES = [
    "a11y-dark", "a11y-light", "agate", "an-old-hope", "androidstudio",
    "arduino-light", "arta", "ascetic", "atom-one-dark", "atom-one-dark-reasonable",
    "atom-one-light", "brown-paper", "codepen-embed", "color-brewer", "dark",
    "default", "devibeans", "docco", "far", "felipec", "foundation", "github",
    "github-dark", "github-dark-dimmed", "gml", "googlecode", "gradient-dark",
    "gradient-light", "grayscale", "hybrid", "idea", "ir-black", "isbl-editor-dark",
    "isbl-editor-light", "kimbie-dark", "kimbie-light", "lightfair", "lioshi",
    "magula", "mono-blue", "monokai", "monokai-sublime", "night-owl", "nnfx-dark",
    "nnfx-light", "nord", "obsidian", "ocean", "paraiso-dark", "paraiso-light",
    "pojoaque", "purebasic", "qtcreator-dark", "qtcreator-light", "rainbow",
    "routeros", "school-book", "shades-of-purple", "srcery", "stackoverflow-dark",
    "stackoverflow-light", "sunburst", "tokyo-night-dark", "tokyo-night-light",
    "tomorrow", "tomorrow-night", "tomorrow-night-blue", "tomorrow-night-bright",
    "tomorrow-night-eighties", "vs", "vs2015", "xcode", "xt256"
]


def get_latest_version() -> Optional[str]:
    """从 cdnjs API 获取 Highlight.js 最新版本号"""
    try:
        url = "https://api.cdnjs.com/libraries/highlight.js"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("version")
    except Exception as e:
        print(f"[警告] 无法获取最新版本: {e}", file=sys.stderr)
        return None


def fetch_theme_list_from_github() -> Optional[List[str]]:
    """从 GitHub 仓库获取官方主题列表，失败返回 None"""
    try:
        url = "https://api.github.com/repos/highlightjs/highlight.js/contents/src/styles"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            themes = []
            for item in data:
                if item.get("type") == "file" and item["name"].endswith(".css"):
                    name = item["name"].replace(".css", "")
                    # 排除 common 等非主题文件（如果有）
                    if name not in ("common", "default"):
                        themes.append(name)
            return sorted(themes)
    except Exception as e:
        print(f"[警告] 从 GitHub 获取主题列表失败: {e}", file=sys.stderr)
        return None


def get_available_themes() -> List[str]:
    """获取可用主题列表（优先 GitHub，失败则用内置列表）"""
    themes = fetch_theme_list_from_github()
    if themes:
        print(f"[信息] 从 GitHub 获取到 {len(themes)} 个主题", file=sys.stderr)
        return themes
    else:
        print(f"[信息] 使用内置备用列表 ({len(DEFAULT_THEMES)} 个主题)", file=sys.stderr)
        return DEFAULT_THEMES.copy()


def download_theme(theme: str, version: str, output_dir: str) -> bool:
    """下载指定主题的 .min.css，返回是否成功"""
    # CDN 上的主题文件通常为 .min.css
    url = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{version}/styles/{theme}.min.css"
    output_path = os.path.join(output_dir, f"{theme}.min.css")

    try:
        print(f"正在下载 {theme} ...", end=" ", flush=True)
        with urllib.request.urlopen(url, timeout=30) as resp:
            content = resp.read()
        with open(output_path, "wb") as f:
            f.write(content)
        print(f"✓ 已保存到 {output_path}")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # 有些主题可能没有 .min.css，尝试不带 .min 的版本
            try:
                alt_url = f"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{version}/styles/{theme}.css"
                print(f"重试标准版 ...", end=" ", flush=True)
                with urllib.request.urlopen(alt_url, timeout=30) as resp:
                    content = resp.read()
                with open(output_path, "wb") as f:
                    f.write(content)
                print(f"✓ 已保存到 {output_path}")
                return True
            except Exception:
                print(f"✗ 主题 '{theme}' 不存在 (404)")
                return False
        else:
            print(f"✗ HTTP 错误 {e.code}")
            return False
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False


def search_themes(themes: List[str], keyword: str) -> List[str]:
    """根据关键词搜索主题（不区分大小写，包含匹配）"""
    if not keyword:
        return themes
    keywords = keyword.lower().split()
    matched = []
    for t in themes:
        t_lower = t.lower()
        if any(k in t_lower for k in keywords):
            matched.append(t)
    return sorted(matched)


def interactive_search_and_download(themes: List[str], version: str, output_dir: str):
    """交互式搜索 → 显示匹配列表 → 用户选择序号 → 下载"""
    print("\n请输入搜索关键词（支持部分匹配，多个关键词用空格分隔，直接回车显示全部）：")
    keyword = input("> ").strip()
    matched = search_themes(themes, keyword)

    if not matched:
        print("没有匹配的主题。")
        return

    print(f"\n找到 {len(matched)} 个匹配的主题：")
    for i, t in enumerate(matched, 1):
        print(f"  {i:3}. {t}")

    print("\n请输入要下载的序号（多个用空格/逗号分隔），或输入 'all' 全部下载，或直接回车取消：")
    choice = input("> ").strip()
    if not choice:
        print("取消下载。")
        return

    # 解析选择
    if choice.lower() == 'all':
        selected = matched
    elif choice == "0":
        return
    else:
        indices = []
        for part in choice.replace(',', ' ').split():
            try:
                idx = int(part)
                if 1 <= idx <= len(matched):
                    indices.append(idx)
                else:
                    print(f"跳过无效序号: {idx}")
            except ValueError:
                print(f"忽略无效输入: {part}")
        if not indices:
            print("没有有效的选择。")
            return
        selected = [matched[i-1] for i in sorted(set(indices))]

    if not selected:
        print("没有选择任何主题。")
        return

    print(f"\n将下载 {len(selected)} 个主题：")
    for t in selected:
        print(f"  - {t}")
    print("\n确认下载？(y/n)")
    confirm = input("> ").strip().lower()
    if confirm not in ('y', 'yes'):
        print("取消下载。")
        return

    # 下载
    success = 0
    for t in selected:
        if download_theme(t, version, output_dir):
            success += 1
    print(f"\n[完成] 成功下载 {success} 个主题文件。")


def main():
    while True:
        parser = argparse.ArgumentParser(
            description="Highlight.js CSS 主题下载工具",
            epilog="示例：\n  %(prog)s -s dark\n  %(prog)s -l github-dark -o ./themes"
        )
        parser.add_argument(
            "-l", "--theme",
            nargs="+",
            help="精确指定要下载的主题名称（多个用空格分隔）"
        )
        parser.add_argument(
            "-s", "--search",
            nargs="+",
            help="搜索关键词并下载所有匹配的主题（非交互，搭配 -y 可跳过确认）"
        )
        parser.add_argument(
            "-v", "--version",
            help="Highlight.js 版本号（默认自动获取最新版）"
        )
        parser.add_argument(
            "-o", "--output",
            default=".",
            help="输出目录（默认当前目录）"
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="列出所有可用主题（不下载）"
        )
        parser.add_argument(
            "-y", "--yes",
            action="store_true",
            help="对搜索匹配的主题直接下载，无需确认（仅与 -s 配合使用）"
        )
        args = parser.parse_args()

        # 1. 确定版本
        if args.version:
            version = args.version
        else:
            version = get_latest_version()
            if not version:
                print("[错误] 无法获取最新版本，请手动指定 --version", file=sys.stderr)
                sys.exit(1)
        print(f"[信息] 使用版本: {version}")

        # 2. 获取主题列表
        all_themes = get_available_themes()

        # 3. 列出所有主题
        if args.list:
            print(f"\n所有可用主题（共 {len(all_themes)} 个）：")
            for i in range(0, len(all_themes), 8):
                print("  " + "  ".join(all_themes[i:i+8]))
            return

        # 4. 命令行搜索模式（非交互，直接下载所有匹配）
        if args.search:
            keyword = " ".join(args.search)
            matched = search_themes(all_themes, keyword)
            if not matched:
                print(f"没有匹配 '{keyword}' 的主题。")
                return
            print(f"\n搜索到 {len(matched)} 个匹配的主题：")
            for i in range(0, len(matched), 8):
                print("  " + "  ".join(matched[i:i+8]))
            if not args.yes:
                print("\n确认要下载这些主题吗？(y/n)")
                confirm = input("> ").strip().lower()
                if confirm not in ('y', 'yes'):
                    print("取消下载。")
                    return
            # 下载
            success = 0
            for t in matched:
                if download_theme(t, version, args.output):
                    success += 1
            print(f"\n[完成] 成功下载 {success} 个主题文件。")
            return

        # 5. 精确指定主题
        if args.theme:
            if not os.path.exists(args.output):
                os.makedirs(args.output, exist_ok=True)
            success = 0
            for theme in args.theme:
                # 支持精确匹配或前缀匹配（如 "github" 匹配 "github" 和 "github-dark"）
                matched = [t for t in all_themes if t == theme or t.startswith(theme)]
                if not matched:
                    print(f"[警告] 未找到匹配的主题: {theme}")
                    continue
                for m in matched:
                    if download_theme(m, version, args.output):
                        success += 1
            print(f"\n[完成] 成功下载 {success} 个主题文件。")
            return

        # 6. 无参数 → 交互式搜索 + 选择下载
        interactive_search_and_download(all_themes, version, args.output)

        input("输入任意内容以结束本轮下载")
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()