---
date: 2026-07-13 17:36:34
author: Yumo-sama
avatar: /imgs/yumo.jpg
title: keyBonk V1.4.0.0 正式发布
summary: 本次更新优化了软件的音频播放，从原本的Windows原生API播放全面迁移到了Yumo Audio库，实现了多音频同时播放的音频混合效果
tags: ["发布", "keyBonk"]
---

KeyBonk 1.4.0.0版本正式发布！

!!! note
    考虑下载速度，本次之后将持续提供蓝奏云下载通道，下载链接[https://wwbvf.lanzouu.com/b00jfemoja](https://wwbvf.lanzouu.com/b00jfemoja)，密码:KEYBONK

本次更新优化了软件的音频播放，从原本的Windows原生API播放全面迁移到了[Yumo Audio](https://github.com/keyBonk-org/audio-player)库，实现了多音频同时播放的音频混合效果

本版本的音频寻找逻辑有所变更，原本的版本是根据按键推测音频文件名，寻找后播放；当前版本是运行时预读取音频库下所有音频文件，在按键时从预读取列表寻找。这导致了本版本相对前几个版本失去了一定的运行时灵活性，但相应的播放效率有所提高。

另外，考虑到项目已经拥有了独立的[官网](https://keyBonk-org.github.io/)，本版本修缮了“关于”页面

<img width="596" height="398" alt="image" src="https://github.com/user-attachments/assets/11a113a4-2cc0-4e76-90da-0f4ebefce05d" />

下载链接：

[Release [V1.4.0.0] 音频播放优化 · keyBonk-org/KeyBonk](https://github.com/keyBonk-org/KeyBonk/releases/tag/V1.4.0.0)