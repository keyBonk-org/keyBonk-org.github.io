---
date: 2026-07-13
author: Yumo-sama
avatar: /imgs/yumo.jpg
title: 获取Yumo audio
summary: 介绍如何获取Yumo audio库
tags: ["Yumo audio", "开发", "下载"]
weight: 2
---

使用Yumo Audio的第一步是下载，在本篇中，你将了解到：

- 从源码构建Yumo Audio静态库文件
- 从GitHub的release下载Yumo Audio静态库文件以及头文件
- 从其他渠道下载Yumo Audio静态库文件以及头文件

!!! note
	当前版本，只发布适用于MinGW的`.a`文件，对于MSVC等编译器，需要自行编译。  
	当前编译系统默认编译器名为g++，编译器不同请自行修改makefile

## 从源码构建

可以选择从源码构建Yumo audio，适合直接以源码形式接入项目或用于获取适合本地架构的静态库文件

### 先决条件

从源码构建Yumo audio需要确保拥有以下软件：

- make
- powershell
- g++
- i686-w64-mingw32-g++（如果需要32位版本）
- git（推荐用于源码获取）

### 获取源码

选择一个合适的文件夹，在此路径下打开控制台，输入：

```powershell
git clone https://github.io/keybonk-org/audio-player/
```

等待指令运行完毕。

### 编译

使用`cd audio-player`进入下载到的源码文件夹。

执行如下命令以获取本地`g++`编译的版本

```powershell
make
```

执行如下命令以获取32位版本（如有`i686-w64-mingw32-g++`）

```powershell
make 32
```

执行结束后，`build`路径下会多出：

- 一个`.o`对象文件，编译的过程文件
- 一个`.a`静态库文件，最终产物
- 两个`.hpp`头文件，复制自`src`目录
- 一个`.zip`压缩包，包含上述除`.o`以外的三个文件

至此，构建结束，成功获取Yumo audio库的二进制文件（`.a`文件）

## 从GitHub下载

打开Yumo audio的[Release](https://github.com/keybonk-org/audio-player/release/latest/)，选择需要的版本，点击下载即可获取携带静态库文件、头文件的`.zip`压缩包。

## 其他渠道下载

（暂未上传）