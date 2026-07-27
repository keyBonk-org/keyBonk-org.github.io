---
date: 2026-07-25
author: 小狄同学呀
avatar: /imgs/xiaodi.jpg
title: 全局状态管理
summary: 介绍如何使用全局变量控制所有音频的播放状态
tags: ["Yumo audio","全局状态","播放控制"]
weight: 7
---

除了对单个音频实例进行控制外，Yumo audio 还提供了全局状态管理机制，允许一次性控制所有正在播放的音频。

## 全局音频控制信号

库在 `yumo` 命名空间下提供了一个全局变量 `global`，类型为 `yumo::audioSign`：

```cpp
namespace yumo {
    class audioSign {
    public:
        switchSign mute{false};   // 静音
        switchSign stop{false};   // 停止（挂起）
        volumeSign volume{1.0f};  // 音量（0.0-1.0）
    };

    inline yumo::audioSign global;
}
```

### 成员说明

|成员|类型|默认值|说明|
|---|---|---|---|
|`mute`|`switchSign` (`atomic<bool>`)|`false`|全局静音开关|
|`stop`|`switchSign` (`atomic<bool>`)|`false`|全局停止/挂起开关|
|`volume`|`volumeSign` (`atomic<float>`)|`1.0f`|全局音量倍率|

!!! note
    `mute`、`stop` 和 `volume` 均使用 `yumo::atomic` 模板类封装，因此是线程安全的，可以在任何线程中安全访问。有关原子类的详细信息，请参考[原子类与其typedef](../atomic)。

## 全局静音

通过设置`global.mute`为`true`，可以将所有正在播放的音频设置为静音状态。与单个实例的 `setMuted` 不同，全局静音作用于所有音频。

### 示例

```cpp
yumo::global.mute = true;
yumo::global.mute = false;
```

### 效果

- **静音时**：所有音频不输出声音，但播放位置继续推进。静音效果强行覆盖所有播放实例。
- **取消静音后**：音频从当前位置继续播放。覆盖效果失效。

!!! note
    注1：全局静音与为每个播放实例分别设置静音效果相同，但实际使用推荐使用全局静音，因为这样库会直接跳过混音过程，节省效率。

!!! note
	注2：静音效果强行覆盖所有播放实例，取消后，恢复实例在静音前的静音设置。如果静音期间做出了修改，则采用修改后的静音设置。

## 全局停止

通过设置`global.stop`为`true`，可以暂停所有正在播放的音频。与单个实例的 `stop` 不同，全局停止作用于所有音频。

### 示例

```cpp
yumo::global.stop = true;
yumo::global.stop = false;
```

### 效果

- **停止时**：所有音频不输出声音，且播放位置**不推进**
- **恢复后**：音频从暂停位置继续播放

与全局静音相似的，全局停止会覆盖所有单个播放实例的停止设置。

!!! note
    全局停止与为每个播放实例分别设置停止效果相同，但实际使用推荐使用全局停止，因为这样库会直接跳过混音过程，节省效率。

## 全局音量

`global.volume` 作为一个乘法因子应用于所有音频的播放音量。音频实际音量 = 实例音量 × 全局音量。

### 示例

```cpp
yumo::global.volume = 0.5f;
float currentVolume = yumo::global.volume.load();
```

### 音量计算

```text
实际播放音量 = 实例音量 (instance.volume) × 全局音量 (global.volume)
```

例如：
- 实例音量为 `0.8`，全局音量为 `0.5`，实际播放音量为 `0.4`
- 实例音量为 `1.0`，全局音量为 `0.0`，实际播放音量为 `0.0`（等效静音）

!!! tip
    可以通过将 `global.volume` 设置为 `0.0` 来实现全局静音的效果，但这样混音环节不会被跳过且会一一计算，效率低下。
