---
date: 2026-07-21
author:
  - name: Yumo-sama
    avatar: /imgs/yumo.jpg
  - name: 小狄同学呀
    avatar: /imgs/xiaodi.jpg
title: 预处理与播放
summary: 介绍如何使用Yumo audio预处理一段音频并播放它
tags: ["Yumo audio", "开发","播放","预处理","接口"]
weight: 4
---

下面是与音频库播放功能直接相关的几个核心接口，我们先来粗略的看一遍：

```cpp
namespace yumo{
	size_t preloadAudio(const wchar_t *filename, readySign *ready = nullptr);
	size_t addAudio(size_t preloadedId, float volume = 1.0f);
	void addAudio(const wchar_t *filename, float volume = 1.0f, size_t *instanceId = nullptr, readySign *ready = nullptr);
}
```

!!! note
	库内所有内容都在`yumo`命名空间下，虽然很少，但仍不推荐`using namespace yumo;`，因为如果你还用了我们开发的其他库（虽然只是计划中的所以你现在肯定没用过）就会发现这些库的命名空间全部都是`yumo`，很有可能会有冲突发生

下面我们将对它们逐一讲解。

## 预处理音频

首先是预处理函数`preloadAudio`，函数会启动一个读取线程并返回该音频在队列中的ID，读取线程读取并解析指定音频，将其加入到已预处理音频队列。

### 原型

```cpp
size_t preloadAudio(
	const wchar_t *filename,
	readySign     *ready = nullptr
);
```

### 参数

`[in] filename`

类型：**wchar_t\***

宽字符字符串，指定需要预处理的音频文件名。

`[out,optional] ready`

类型：**readySign\***

函数会将其指向的对象赋为`false`然后启动后台线程并返回；后台读取线程在完成解析后，会将其更新为`true`。调用方可通过检查该值来确认对应音频是否已就绪。有关`readySign`，请参考[原子类typedef](../atomic/typedef)。

### 返回值

类型：**size_t**

预处理后的音频在队列中的ID。

### 示例

```cpp
yumo::readySign ready(false);
size_t preloadId = yumo::preloadAudio(L"./test.wav", &ready);
```

## 播放预处理后的音频

预处理后音频会得到一个ID，这是预处理ID，根据预处理ID，我们就可以将其对应的已经经过预处理的音频加入到播放队列。

### 原型

```cpp
size_t addAudio(
	size_t preloadedId,
	float  volume = 1.0f
);
```

### 参数

`[in] preloadedId`

类型：**size_t**

欲加入到播放队列的音频对应的预处理ID。

`[in,optional] volume`

类型：**float**

音频开始播放时的初始音量，最大为1，最小为0，默认为1。

### 返回值

类型：**size_t**

音频加入队列后创建的播放实例的ID。

### 示例

```cpp
yumo::readySign ready(false);
size_t preloadId = yumo::preloadAudio(L"./test.wav", &ready);
size_t instanceId = yumo::addAudio(preloadId, 0.7f);
```

## 无预处理播放

当音频较小或在一定时间内只需播放较少的次数时，可以直接忽略预处理，使用`addAudio`的一个字符串重载来直接从文件添加音频到播放队列而非预处理ID。

该重载会激活一个读取线程，自动完成预处理与播放，播放完毕后会将预处理音频从预处理队列移除，因此此方式只适用于一次性播放

### 原型

```cpp
void addAudio(
	const wchar_t *filename,
	float         volume = 1.0f,
	size_t        *instanceId = nullptr,
	readySign     *ready = nullptr);
```

### 参数

`[in] filename`

类型：**const wchar_t\***

宽字符字符串，指定需要添加的音频文件名。

`[in,optional] volume`

类型：**float**

音频开始播放时的初始音量，最大为1，最小为0，默认为1。

`[out,optional] instanceId`

类型：**size_t\***

一个指针，用于获取播放实例ID，如果音频足够长且需要一些诸如音量调整的精细操作，则需要接受ID。

`[out,optional] ready`

类型：**readySign\***

函数会将其指向的对象赋为`false`并返回；后台读取线程在完成解析后，会将其更新为`true`。调用方可通过检查该值来确认对应音频是否已就绪。有关`readySign`，请参考[原子类typedef](../atomic/typedef)。

### 示例

```cpp
// 可选的内容
size_t instanceId = 0;
yumo::readySign ready(false);

yumo::addAudio(
	L"./test.wav",
	0.8f,
	&instanceId,
	&ready
);
```