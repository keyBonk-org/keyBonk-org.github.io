---
date: 2026-08-03
author:
  - name: 小狄同学呀
    avatar: /imgs/xiaodi.jpg
  - name: Yumo-sama
    avatar: /imgs/yumo.jpg
title: 音频播放状态管理
summary: 介绍如何管理单个音频的播放状态，包括暂停、静音、音量调节、位置控制等
tags: ["Yumo audio","状态管理","播放控制"]
weight: 6
---

通过`addAudio`函数，可以获得一个`yumo::audioInstance`对象，它代表一个独立的播放实例。通过该对象，您可以对单个音频进行精细控制。

## 播放实例的获取

### 从`addAudio`获得

```cpp
yumo::audioInstance inst = yumo::addAudio(preloadId, 0.8f);
```

### 通过 ID 重新获取

如果你的`audioInstance`对象因为某些原因丢失了，但是ID被保存了下来，比如一些只能按值传递整数的场景，可以使用`regain`函数通过实例ID重新获取：

```cpp
yumo::audioInstance inst = yumo::regain(instanceId);
```

!!! note
    目前的版本中，如果当实例已被移除或播放完毕，`regain`将返回一个`instanceId`为`0`的无效对象，如果传入的ID正好就是`0`则可能会有问题，具体的修复请关注后续版本的文档


## 控制播放

`audioInstance`提供了几个**代理成员**，您可以像操作普通变量一样读写它们，每个操作都会自动同步到播放引擎。

| 成员     | 类型                | 说明                                                      |
|----------|---------------------|-----------------------------------------------------------|
| `position` | `proxy<size_t>`   | 当前播放位置（样本索引）。读取获得当前位置，写入可跳转。 |
| `volume`   | `proxy<float>`    | 音量（0.0 ~ 1.0）。修改立即生效。                         |
| `stopped`  | `proxy<bool>`     | 暂停/恢复：设为`true`暂停（位置不推进），`false` 恢复。 |
| `muted`    | `proxy<bool>`     | 静音：设为`true`静音（位置继续推进），`false` 取消。   |

### 示例：暂停与恢复

```cpp
inst.stopped   = true;   // 暂停
bool isStopped = inst.stopped
inst.stopped   = false;  // 从暂停处继续
```

### 示例：静音控制

```cpp
inst.muted = true;     // 静音，但位置继续推进
inst.muted = false;    // 取消静音
```

### 示例：调节音量

```cpp
inst.volume = 0.5f;    // 设置为 50%
float vol = inst.volume; // 读取当前音量
```

### 示例：跳转播放位置

```cpp
inst.position = 44100 * 10; // 跳转到第 10 秒（44.1kHz 采样率）
size_t current = inst.position; // 获取当前位置
```

> **注意**：`position` 的单位是采样点（样本数），对于立体声 16 位格式，每个采样点对应一个 `int16_t` 值（左声道和右声道交替存储）。调整位置时请确保不超过音频总长度，否则音频会提前结束。

## 检查播放状态

`audioInstance`提供了`isPlaying`方法，通过这个方法可以检查音频是否正在播放

```cpp
bool playing = inst.isPlaying();
```

## 移除播放实例

手动从播放池中移除一个实例，释放资源：

```cpp
bool remove(size_t instanceId);
```

返回 `true` 表示移除成功，`false` 表示 ID 无效。

```cpp
if (yumo::remove(inst.instanceId)) {
    std::cout << "已移除" << std::endl;
}
```

## 重置所有实例

将当前所有播放实例的位置重置到开头，相当于重新播放所有音频：

```cpp
void resetAll();
```

```cpp
yumo::resetAll(); // 所有音频从头开始
```

## 监听播放完成

您可以为库注册一个回调函数，当某个播放实例自然播放结束并被自动回收时，该回调会被触发，通知您该实例的ID。

```cpp
void registerPlaybackFinishedCallback(PlaybackFinishedCallback callback);
void unregisterPlaybackFinishedCallback();
```

`PlaybackFinishedCallback` 定义：
```cpp
using PlaybackFinishedCallback = std::function<void(size_t instanceId)>;
```

示例：
```cpp
const int AUDIO_COUNT = 10;
int playCount = 0;
void myCallback(size_t id) {
    std::cout << "实例 " << id << " 播放完毕" << std::endl;
    playCount++;
}

yumo::registerPlaybackFinishedCallback(myCallback);
// 播放若干音频
while (playCount != AUDIO_COUNT)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
// 注销回调
yumo::unregisterPlaybackFinishedCallback();
// 无回调的播放若干音频

```

!!! important
    回调在库的内部线程中执行，请勿在回调中执行耗时操作或调用可能阻塞的库函数。

## 注意事项

- 所有 `audioInstance` 的代理成员操作都是**线程安全**的，您可以在任何线程中读写它们。
- 当实例被移除或播放结束后，再操作其代理成员可能无效（但不会崩溃）。
- 建议不要试图手动构造`proxy`对象（详见[proxy类说明](../proxy)）。