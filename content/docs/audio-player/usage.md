---
date: 2026-07-11
author:
  - name: 小狄同学呀
    avatar: /imgs/xiaodi.jpg
  - name: Yumo-sama
    avatar: /imgs/yumo.jpg
title: 开始使用
summary: 介绍Yumo audio库的使用方法
tags: ["Yumo audio", "开发"]
weight: 1
---

Yumo audio是一个基于win32 API的C++音频混合库，用于混合播放多个音频流，是KeyBonk项目的一个重要组件，详细的介绍请见[项目简介](http://localhost:8000/docs/audio-player/)。

本文档包括以下几个章节：

- [获取Yumo audio](../download)
- [为make管理的项目引入Yumo audio](../make_get)
- [预处理与播放](../add-preload)
- [原子类与其typedef](../atomic)
- [音频播放状态管理](../status)
- [全局状态管理](../global)
- [错误处理](../exception)

另外，考虑到可能有的用户会考虑是否选用Yumo audio，我们提供了Yumo audio和win32 API以及主流API的数据对比，用于辅助参考，参见[音频库的选择](../choice)