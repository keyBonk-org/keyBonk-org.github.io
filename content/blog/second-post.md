{
    "date": "2026-07-11 3:12:13",
    "author": "小狄同学呀",
    "avatar": "/imgs/xiaodi.jpg",
    "title": "Yumo Audio v0.0.1 正式发布",
    "summary": "Yumo Audio —— 基于 Win32 API 的 C++ 音频播放库，首个版本 v0.0.1 发布。聚焦音频混合等基础 API 无法满足的功能，服务于 KeyBonk 项目。",
    "tags": ["发布", "音频库", "Yumo Audio"]
}

## 发布说明

Yumo Audio v0.0.1 正式发布了！

Yumo Audio 是一个利用 Win32 API 实现的 C++ 音频播放库，它是 KeyBonk 项目的重要组成部分。

## 项目背景

在开发 KeyBonk 的过程中，我们发现Windows内置的PlaySound函数在播放音频时会阻塞前面的音频播放，导致按键反馈延迟。

为了解决这些问题，我们决定造一个自己的轮子——Yumo Audio 应运而生。

## 项目定位

Yumo Audio 属于**自用型库**，它的设计目标非常明确：**完全服务于 KeyBonk 项目**。

这意味着：
- 功能需求完全由 KeyBonk 的实际使用场景驱动
- API 设计优先考虑 KeyBonk 的调用方式
- 不追求大而全，只做 KeyBonk 需要的功能

当然，如果它恰好也能满足你的需求，欢迎使用。

## 核心特性

### 基于 Win32 API

完全基于 Windows 原生 API 构建，不依赖任何第三方音频库，部署简单，启动迅速。

### 音频混合

支持多音频同时播放，内部自动进行音频混合处理。对于键盘音效这种需要频繁触发、多音叠加的场景特别友好。

### C++ 接口

提供简洁的 C++ API，便于集成到各类桌面应用中。

## 适用场景

- 键盘音效软件（如 KeyBonk）
- 游戏音效播放
- 需要同时播放多个短音频的桌面应用
- 对播放延迟敏感的场景

## 获取方式

- **Release 页面**：[https://github.com/keyBonk-org/audio-player/releases/tag/v0.0.1](https://github.com/keyBonk-org/audio-player/releases/tag/v0.0.1)
- **源码仓库**：[https://github.com/keyBonk-org/audio-player](https://github.com/keyBonk-org/audio-player)

## 后续计划

v0.0.1 只是一个开始，后续将根据 KeyBonk 的开发进度持续迭代，包括但不限于：

- 更丰富的音频格式支持
- 性能进一步优化

## 写在最后

虽然 Yumo Audio 是一个自用型库，但如果你在使用过程中有任何问题或建议，欢迎在 GitHub 上提 Issue。

> 让每一次按键掷地有声！
