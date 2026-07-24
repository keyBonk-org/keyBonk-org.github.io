---
date: 2026-07-13
author: Yumo-sama
avatar: /imgs/yumo.jpg
title: 音频库的选择
summary: 快速判断Yumo audio库到底适不适合您的项目，以及其他库的情况
tags: ["Yumo audio","比较"]
weight: 300
---

一个很普遍的现象是：在目标相同的各种库中选择最适合自己项目的一个一直是一件困难的时期，本文提供了Yumo audio与Windows原生API及主流C/C++音频库进行的对比，以方便各位根据项目需求做出选择。

### 简单介绍

- **Yumo audio**：基于 Win32 的 C++17 音频库，目前只支持WAV与MP3播放，支持异步非阻塞播放、音频混合、暂停/静音和音量独立控制。
- **PlaySound / sndPlaySound**：Windows 最简单的音频播放 API，适合播放小型 WAV 文件。
- **MCI（mciSendString / mciSendCommand）**：Windows 多媒体控制接口，支持更多格式和播放控制，但不支持多线程混音。
- **waveOut**：Windows 底层波形音频 API，提供更细粒度的音频流控制。（实际上，本库就是封装过的waveOut）
- **DirectSound**：旧版 DirectX 音频 API，支持硬件加速和 3D 音效（已弃用，建议改用 XAudio2）。
- **XAudio2**：DirectX 的现代音频 API，支持混音、音效处理和低延迟播放。（需要Windows SDK）
- **WASAPI**：Windows 核心音频 API，低延迟、高精度，是微软推荐的新一代音频方案。
- **OpenAL**：跨平台 3D 音频 API，支持空间音频和多声道混音。
- **SDL_mixer**：SDL 的音频扩展库，跨平台，支持多种格式和混音。
- **FMOD**：专业级音频引擎，功能强大，支持复杂混音和 DSP 效果，但商业使用需付费。
- **PortAudio**：跨平台音频 I/O 库，专注于低延迟录音和播放。
- **SoLoud**：轻量级游戏音频引擎，API 简单易用。
- **miniaudio**：单文件 C 库，无依赖，支持播放、混音和 3D 音效。

### 功能对比表

| 功能 / 库 | Yumo Audio | PlaySound / sndPlaySound | MCI | waveOut* | XAudio2 | WASAPI | OpenAL | SDL_mixer | FMOD | PortAudio | SoLoud | miniaudio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **平台** | Windows | Windows | Windows | Windows | Windows | Windows | 跨平台 | 跨平台 | 跨平台 | 跨平台 | 跨平台 | 跨平台 |
| **音频格式** | WAV / MP3 | WAV | WAV / MP3 等 | PCM | 多种 | PCM | PCM | 12+ 种 | 几乎全部 | PCM | WAV/MP3/OGG/FLAC | 多种 |
| **异步播放** | ✅ | ✅（SND_ASYNC） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **音频混合** | ✅（重叠混合） | ❌ | ❌（不支持多线程） | 需自行实现 | ✅ | ✅（系统级） | ✅ | ✅ | ✅ | 需自行实现 | ✅ | ✅ |
| **暂停/恢复** | ✅（单个音频） | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **音量控制** | ✅（单个音频） | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **静音控制** | ✅（单个音频） | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **3D 空间音效** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅（可选） |
| **DSP/音效** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | 基础 | ✅ | ❌ | 基础 | ✅ |
| **文件大小限制** | 无 | ~100KB | 无 | 无 | 无 | 无 | 无 | 无 | 无 | 无 | 无 | 无 |
| **学习曲线** | 低 | 极低 | 中 | 高 | 中高 | 高 | 中 | 低 | 中 | 中 | 低 | 低 |
| **许可证** | WTFPL | 闭源（系统 API） | 闭源（系统 API） | 闭源（系统 API） | 闭源（系统 API） | 闭源（系统 API） | LGPL | zlib | 商业（免费供个人/小团队） | MIT | 公共领域 / zlib | 公共领域 |
| **适用场景** | 轻量级多音效管理 | 简单提示音 | 简单媒体播放 | 底层音频控制 | 游戏/高性能音频 | 专业音频应用 | 3D 游戏音效 | 跨平台游戏 | 专业游戏音频 | 实时音频采集 | 轻量级游戏 | 极简嵌入式项目 |