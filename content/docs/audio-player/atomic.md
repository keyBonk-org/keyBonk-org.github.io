---
date: 2026-07-24
author: 小狄同学呀
avatar: /imgs/xiaodi.jpg
title: 原子类与其typedef
summary: 简单介绍yumo::atomic及其衍生的typedef
tags: ["Yumo audio","原子类","typedef"]
weight: 5
---

前面的章节中，我们介绍了`preloadAudio`等一众函数，考虑到一般的窗口程序都不希望一个加载过程长时间阻塞导致无法处理事件循环，库对于长耗时调用往往采取新建线程的方式，由调用方传入标志变量，在完成时以此通知。

不过标准的指针在编译器优化和机器高速缓存的双重作用下会出现非实时更新，导致看不到其他线程的修改，`volatile`虽然能避免编译器的优化，但无法避免机器缓存，因此需要原子类辅助。

本库提供了改进的原子类，重载了赋值运算符并提供了隐式转换，使之看上去像是一个一般的类型而不是一个类。另外，库提供了一些`typedef`，以便使用更清晰的类型名称来使得代码可读性更强。

## yumo::atomic模板类

`yumo::atomic`模板类是对`std::atomic`的封装与改进，拥有一个模板参数`T`，指示存储值的类型

### 构造函数

函数有三个构造函数

- `atomic()`：`=default`，不执行操作。
- `atomic(T val)`：使用一个`T`类型的值作为初始值。
- `atomic(const atomic &other)`：复制构造函数，从已有`yumo::atomic`复制。

**示例**

```cpp
yumo::atomic<bool> sign;
yumo::atomic<bool> ready(true);
yumo::atomic<bool> ready_copy(ready);
```

### 运算符重载

`yumo::atomic`提供了一些运算符重载，如下表所示：

|运算符|支持的参数类型|
|---|---|
|=|模板参数（T）、yumo::atomic|
|==|模板参数（T）、yumo::atomic、std::atomic|
|!=|模板参数（T）、yumo::atomic、std::atomic|

**示例**

```cpp
yumo::atomic<bool> bool_a(true);
yumo::atomic<bool> bool_b(false);

std::cout << "bool_a：" << bool_a << std::endl;
std::cout << "bool_b：" << bool_b << std::endl;
std::cout << "是否不等：" << bool_b != bool_a << std::endl;
std::cout << "是否相等：" << bool_b == bool_a << std::endl;

bool_a = bool_b;
std::cout << "赋值后的bool_a：" << bool_a << std::endl;
bool_a = true;
std::cout << "重新赋值回true的bool_a：" << bool_a << std::endl ;
```

### 隐式转换

`yumo::atomic`可以隐式的转换为`T`型值，一特性使得`yumo::atomic<T>`可以在任何需要`T`类型的上下文中使用，包括`if`、`while`等条件判断

**示例**

```cpp
yumo::atomic<bool> ready(false);
yumo::preloadAudio(L"./test.wav",&ready);
while (ready){
	return;
}
```

### 其他成员函数

考虑兼容等因素，`yumo::atomic`保留了`load`和`store`两个标准的原子类操作方法，原型如下：

```cpp
template <typename T>
class atomic {
	// ...
	T load(std::memory_order order = std::memory_order_seq_cst) const;
	void store(T val, std::memory_order order = std::memory_order_seq_cst);
};
```

**示例**

```cpp
yumo::atomic<int> counter(0);

int current = counter.load();
counter.store(current + 1);
```

## typedef

库提供了几个名称更有意义的typedef以增强代码可读性

|名称|类型|意义|
|---|---|---|
|readySign|bool|完成标志，线程操作完成后以此通知调用方|
|switchSign|bool|播放控制开关，应用详见[全局状态管理](../global)|
|volumeSign|float|声音值，应用详见[全局状态管理](../global)|