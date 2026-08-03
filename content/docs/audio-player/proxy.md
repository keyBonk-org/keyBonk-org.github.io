---
date: 2026-08-03
author:
  - name: 小狄同学呀
    avatar: /imgs/xiaodi.jpg
  - name: Yumo-sama
    avatar: /imgs/yumo.jpg
title: proxy代理类
summary: 了解audioInstance中的代理成员工作原理
tags: ["Yumo audio","proxy","内部机制"]
weight: 7
---

## 什么是 `yumo::audioInstance::proxy`？

`proxy`是`audioInstance`内部定义的一个模板类，用于**模拟普通变量的读写行为**。它的作用是让您能够像操作普通成员变量一样操作播放状态，而无需调用额外的函数

### 原型

```cpp
template <typename T>
class proxy
{
public:
    proxy();
    proxy(T &value);
    proxy(const proxy &other);
    proxy &operator=(const proxy &other) = delete;
    operator T() const;
    proxy &operator=(T value);
};
```

## 为什么要设计成代理？

在老版本API中，控制播放状态通常需要一系列函数，例如：

```cpp
setVolume(id, 0.5f);
float v = getVolume(id);
stop(id);
resume(id);
```

这种设计虽然清晰，但略显繁琐。而通过代理成员，您可以直接写出更自然的代码：

```cpp
inst.volume = 0.5f;
float v = inst.volume;
inst.stopped = true;
inst.stopped = false;
```

这大大简化了状态管理，使代码更简洁、易读。

## 使用场景

`proxy`仅作为`audioInstance`的成员出现，你**永远不应该**需要直接声明或初始化一个`proxy`对象。您只需要通过`audioInstance`的成员（如`position`、`volume`、`stopped`等）来读写即可。

```cpp
yumo::audioInstance inst = ...;
inst.volume = 0.8f;          // 赋值 -> 修改音量
float vol = inst.volume;     // 读取 -> 获取当前音量
```

## 为什么不要手动构造 `proxy`？

- `proxy`对象内部依赖 `audioInstance` 提供的互斥锁和指针，手动构造会破坏内部状态。
- 它只是一个**语法糖**，其本质是对底层播放引擎的调用封装。直接操作 `proxy` 对象本身没有意义。
- 如果您需要在其他上下文中控制播放，请始终通过有效的`audioInstance`对象来操作。

> **结论**：`proxy`的设计目的在于让状态控制更自然。您无需理解其实现，只需按普通变量的方式使用它即可。
