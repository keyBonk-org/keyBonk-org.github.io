#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KeyBonk 网站构建器
用法: python build_site.py

本文件作为构建入口，具体实现请参见 build/ 目录下的模块化文件。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build.site_builder import build_site

if __name__ == '__main__':
    build_site()
