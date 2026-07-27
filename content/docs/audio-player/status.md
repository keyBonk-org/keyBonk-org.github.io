---
date: 2026-07-25
author: 小狄同学呀
avatar: /imgs/xiaodi.jpg
title: 音频播放状态管理
summary: 介绍如何管理单个音频的播放状态
tags: ["Yumo audio","状态管理","播放控制"]
weight: 6
---

前面的章节我们已经介绍了如何预处理音频并将其添加到播放队列。`addAudio` 函数会返回一个**播放实例ID**，通过这个ID，我们可以对单个音频的播放状态进行精细控制。

本章将介绍以下接口：

```cpp
namespace yumo {
    void removePreloadedAudio(size_t preloadedId);
    size_t getPreloadedCount();
    size_t getPlayingCount();
    bool isPlaying(size_t instanceId);
    bool stop(size_t instanceId);
    bool resume(size_t instanceId);
    bool setMuted(size_t instanceId, bool muted);
    void setVolume(size_t instanceId, float volume);
    float getVolume(size_t instanceId);
    bool remove(size_t instanceId);
    void resetAll();
}
```

## 检查播放状态

`isPlaying`函数用于检查指定的播放实例是否正在播放。

### 原型

```cpp
bool isPlaying(
    size_t instanceId
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID，由`addAudio`返回。

### 返回值

类型：**bool**

播放实例的播放状态，可能为以下值：

- `true`：该实例正在播放
- `false`：该实例已结束或ID无效

!!! note
    这个时候有的读者就要问了，你直接甩我一个`false`，我怎么区分无效还是结束呢？  
    哎，问得好，因为我没让库抛异常（因为懒得写），下个版本再说吧，嘿嘿。

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId);
// ...
if (yumo::isPlaying(instanceId)) {
    std::cout << "音频正在播放中" << std::endl;
}
```

## 暂停

`stop`函数用于暂停指定的播放实例。暂停时播放位置会被保留，恢复后从暂停位置继续播放。

### 原型

```cpp
bool stop(
    size_t instanceId
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID。

### 返回值

类型：**bool**

- `true`：操作成功
- `false`：ID无效，操作失败

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId);

// 暂停播放
yumo::stop(instanceId);
```

## 恢复

`resume`函数用于恢复被`stop`暂停的播放实例。注意恢复不会恢复[全局的暂停](../global#全局停止)。

### 原型

```cpp
bool resume(
    size_t instanceId
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID。

### 返回值

类型：**bool**

- `true`：恢复成功或音频本就不在停止状态
- `false`：ID无效，操作失败

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId);

// 暂停播放
yumo::stop(instanceId);

// 恢复播放
yumo::resume(instanceId);
```

## 静音控制

`setMuted` 函数用于设置指定播放实例的静音状态。静音时音频位置继续推进，但不会输出声音。

静音和暂停的区别是，静音时音频位置正常推进，只是不会输出声音，暂停则不会推进播放位置。

### 原型

```cpp
bool setMuted(
    size_t instanceId, bool muted
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID。

`[in] muted`

类型：**bool**

- `true`：设置为静音
- `false`：取消静音

### 返回值

类型：**bool**

- `true`：操作成功
- `false`：ID无效，操作失败

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId);

// 设置静音
yumo::setMuted(instanceId, true);

// 取消静音
yumo::setMuted(instanceId, false);
```

## 获取音量

`getVolume`可以获取指定播放实例的音量。

### 原型

```cpp
float getVolume(
    size_t instanceId
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID。

### 返回值

类型：**float**

指定播放实例当前音量值，范围 `0.0` ~ `1.0`。

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId, 0.5f);

float currentVolume = yumo::getVolume(instanceId);
std::cout << "当前音量：" << currentVolume << std::endl;
```

## 设置音量

`setVolume`函数可以调整指定播放实例的音量。

### 原型

```cpp
void setVolume(
    size_t instanceId,
	float  volume
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID。

`[in] volume`

类型：**float**

音量值，范围 `0.0` ~ `1.0`，超出范围会被自动限制。

### 返回值

无

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId, 0.5f);
yumo::setVolume(instanceId, 0.8f);
```

## 移除播放实例

`remove`函数用于从播放池中移除指定的播放实例。

### 原型

```cpp
bool remove(
    size_t instanceId
);
```

### 参数

`[in] instanceId`

类型：**size_t**

播放实例ID。

### 返回值

类型：**bool**

- `true`：移除成功
- `false`：ID无效，移除失败

### 示例

```cpp
size_t instanceId = yumo::addAudio(preloadedId);

// 播放一段时间后移除
yumo::remove(instanceId);
```

!!! warning
    移除播放实例不会立刻停止音频输出，在未来的接口中可能会有调整播放缓冲区大小的功能，到时候如果设置过长可能会有移除但音频不停止的问题。

## 重置所有播放

`resetAll` 函数将所有正在播放的实例的播放位置重置到开头。

### 原型

```cpp
void resetAll();
```

### 参数

无。

### 返回值

无。

### 示例

```cpp
// 重置所有音频到开头
yumo::resetAll();
```

!!! tip
    当需要重新播放所有音频时，使用这个函数比`remove` + `addAudio`的组合来实现重新播放更简单。