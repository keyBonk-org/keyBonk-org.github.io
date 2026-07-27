---
date: 2026-07-25
author: 小狄同学呀
avatar: /imgs/xiaodi.jpg
title: 错误处理
summary: 介绍 Yumo audio的异常体系与错误处理机制
tags: ["Yumo audio","异常","错误处理"]
weight: 8
---

Yumo audio使用自定义的异常类体系来报告和处理错误。所有异常类都定义在`yumo_except.hpp`中，位于`yumo`命名空间下。这个头文件是可选的，你完全可以选择不处理异常，当然，对应的就是你可能需要面对程序异常崩溃。

这个文档虽然归属于Yumo audio文档，但实际上yumo_exception有很多独立于Yumo audio的功能特性，库只选用了一部分，所以你可能会觉得文档有很多废话。

## 异常类体系

```cpp
#include "yumo_except.hpp"
```

### 类层次结构

```
yumo::exception          (基础异常类，仅包含错误类型)
    ├── yumo::exception_ex    (扩展异常类，const wchar_t* 存储错误信息)
    └── yumo::exception_ex2   (扩展异常类，std::wstring 存储错误信息)

yumo::w_exception        (独立的宽字符异常类，不继承自 exception)
```

## 错误类型枚举

`yumo::exception`类中定义了一个枚举`type`，用于标识不同的错误类型，包含以下几种类型

|错误类型|说明|库内是否使用|使用场景（部分）|
|---|---|---|---|
|`FileNotFound`|文件未找到|未使用|音频文件路径错误|
|`FileOpenError`|文件打开失败|使用|权限不足等导致打开失败|
|`FileReadError`|文件读取错误|使用|文件损坏或读取权限问题|
|`FileWriteError`|文件写入错误|未使用|文件不存在或读取权限问题|
|`FileCloseError`|文件关闭错误|未使用|<del>我也不知道啥情况会用上这个</del>|
|`FileError`|通用文件错误|使用|文件错误但无法确定是哪个错误|
|`InvalidInput`|输入参数无效|使用|传入的音频ID无效|
|`InvalidFormat`|格式错误|未使用|音频格式不支持|
|`InvalidState`|状态不允许|未使用|在错误的状态下调用了API|
|`OutOfMemory`|内存不足|使用|加载过大的音频文件|
|`MemoryError`|内存错误|未使用|无法确定具体原因的内存错误|
|`UnknownError`|未知错误|使用|原因未知且无法粗略确定归属的错误|

由于这个头的设计目的并不局限于这一个库，有些错误类型实际上并没有使用到，可以参考“库内是否使用”一栏。

!!! note
    冷知识：我懒得写错误处理的时候会直接抛`UnknownError`糊弄你

## 基础异常类

`yumo::exception` 是所有异常的基类，仅包含一个错误类型枚举值。

### 原型

```cpp
class exception {
public:
    enum class type { /* ... */ };

    exception() = delete;
    exception(type t);
    type getType() const;
};
```

### 使用示例

```cpp
try {
    // ...
} catch (const yumo::exception &e) {
    switch (e.getType()) {
        case yumo::exception::type::FileOpenError:
            std::wcout << L"文件打开失败" << std::endl;
            break;
        case yumo::exception::type::InvalidInput:
            std::wcout << L"参数无效" << std::endl;
            break;
        default:
            std::wcout << L"发生错误" << std::endl;
    }
}
```

!!! note
    `yumo::exception` 类不可被直接构造（`= delete`），只能通过其派生类抛出。

## 扩展异常类（指针版本）

`yumo::exception_ex` 继承自 `yumo::exception`，使用 `const wchar_t*` 存储错误信息。

### 原型

```cpp
class exception_ex : public exception {
public:
    exception_ex(type t, const wchar_t *msg) noexcept;
    const wchar_t *what() const noexcept;
};
```

### 特点

- 使用 `const wchar_t*` 存储错误信息
- `noexcept` 保证不会在构造时抛出异常
- 适用于错误信息为静态字符串字面量的场景

### 使用示例

```cpp
try {
    yumo::preloadAudio(L"test.wav");
} catch (const yumo::exception_ex &e) {
    std::wcout << L"错误类型: " << static_cast<int>(e.getType()) << std::endl;
    std::wcout << L"错误信息: " << e.what() << std::endl;
}
```

!!! warning
    `exception_ex` 接收的是 `const wchar_t*` 指针，调用者需要确保该指针指向的字符串在异常对象生命周期内有效。建议使用字符串字面量或静态存储期的字符串。

## 扩展异常类（字符串版本）

`yumo::exception_ex2` 继承自 `yumo::exception`，使用 `std::wstring` 存储错误信息。

### 原型

```cpp
class exception_ex2 : public exception {
public:
    exception_ex2(type t, const std::wstring &msg);
    const std::wstring &what() const noexcept;
};
```

### 特点

- 使用 `std::wstring` 存储错误信息，自动管理内存
- 可以安全地使用临时字符串或动态构造的字符串
- 适用于需要拼接或格式化错误信息的场景

### 使用示例

```cpp
try {
    // ...
} catch (const yumo::exception_ex2 &e) {
    std::wcout << L"错误类型: " << static_cast<int>(e.getType()) << std::endl;
    std::wcout << L"错误信息: " << e.what() << std::endl;
}
```

!!! tip
    `exception_ex2`相比`exception_ex`更安全，因为它内部持有字符串的拷贝。当不确定使用哪种异常时，优先选择 `exception_ex2`。

## 独立异常类

`yumo::w_exception` 是一个独立的异常类，不继承自 `yumo::exception`，仅提供简单的错误信息。

### 原型

```cpp
class w_exception {
public:
    w_exception() = delete;
    w_exception(const wchar_t *msg) noexcept;
    const wchar_t *what() const noexcept;
};
```

### 特点

- 独立的异常体系，不继承自任何基类
- 仅提供 `what()` 方法获取错误信息
- 适用于需要简单错误报告的场景

### 使用示例

```cpp
try {
    // ...
} catch (const yumo::w_exception &e) {
    std::wcout << L"错误: " << e.what() << std::endl;
}
```

## 捕获顺序

当捕获异常时，建议按照从具体到通用的顺序进行捕获：

```cpp
try {
    // 可能抛出异常的代码
} catch (const yumo::exception_ex2 &e) {
    // 捕获 exception_ex2，可获取详细信息
    std::wcout << L"错误: " << e.what() << std::endl;
} catch (const yumo::exception_ex &e) {
    // 捕获 exception_ex
    std::wcout << L"错误: " << e.what() << std::endl;
} catch (const yumo::exception &e) {
    // 捕获所有继承自 exception 的异常
    std::wcout << L"错误类型: " << static_cast<int>(e.getType()) << std::endl;
} catch (const yumo::w_exception &e) {
    // 捕获 w_exception
    std::wcout << L"错误: " << e.what() << std::endl;
} catch (const std::exception &e) {
    // 捕获标准异常
    std::cout << "标准异常: " << e.what() << std::endl;
} catch (...) {
    // 捕获所有未知异常
    std::cout << "未知错误" << std::endl;
}
```

!!! important
    `yumo::exception_ex` 和 `yumo::exception_ex2` 都继承自 `yumo::exception`，因此捕获顺序很重要。应先捕获派生类，再捕获基类。而 `yumo::w_exception` 不继承自 `yumo::exception`，可以单独捕获。

## 常见错误场景

### 文件加载错误

```cpp
try {
    size_t preloadId = yumo::preloadAudio(L"missing.wav");
} catch (const yumo::exception_ex &e) {
    // 可能是 FileNotFound 或 FileOpenError
    std::wcout << L"加载音频失败: " << e.what() << std::endl;
}
```

### 参数错误

```cpp
try {
    size_t instanceId = yumo::addAudio(9999);  // 无效的预加载ID
} catch (const yumo::exception_ex &e) {
    if (e.getType() == yumo::exception::type::InvalidInput) {
        std::wcout << L"无效的音频ID" << std::endl;
    }
}
```

### 设备错误

```cpp
try {
    // 打开音频设备时可能失败
    yumo::addAudio(preloadId);
} catch (const yumo::exception_ex2 &e) {
    if (e.getType() == yumo::exception::type::UnknownError) {
        std::wcout << L"音频设备错误: " << e.what() << std::endl;
    }
}
```

## 完整错误处理示例

```cpp
#include "audioPlayer.hpp"
#include <iostream>

int main() {
    yumo::readySign ready(false);

    try {
        // 预处理音频
        size_t preloadId = yumo::preloadAudio(L"test.wav", &ready);

        // 等待加载完成
        while (!ready) {
            Sleep(10);
        }

        // 添加播放
        size_t instanceId = yumo::addAudio(preloadId);

        // 播放一段时间
        Sleep(5000);

        // 移除
        yumo::remove(instanceId);
        yumo::removePreloadedAudio(preloadId);

    } catch (const yumo::exception_ex2 &e) {
        // 捕获带详细信息的异常
        std::wcout << L"[错误] 类型=" 
                   << static_cast<int>(e.getType()) 
                   << L", 信息=" << e.what() 
                   << std::endl;

    } catch (const yumo::exception_ex &e) {
        // 捕获带字符串信息的异常
        std::wcout << L"[错误] 类型=" 
                   << static_cast<int>(e.getType()) 
                   << L", 信息=" << e.what() 
                   << std::endl;

    } catch (const yumo::exception &e) {
        // 捕获基类异常
        auto type = e.getType();
        switch (type) {
            case yumo::exception::type::FileNotFound:
                std::wcout << L"文件未找到" << std::endl;
                break;
            case yumo::exception::type::InvalidInput:
                std::wcout << L"参数无效" << std::endl;
                break;
            case yumo::exception::type::OutOfMemory:
                std::wcout << L"内存不足" << std::endl;
                break;
            default:
                std::wcout << L"未知错误，类型ID=" 
                           << static_cast<int>(type) 
                           << std::endl;
        }

    } catch (const std::exception &e) {
        // 捕获标准库异常
        std::cout << "标准异常: " << e.what() << std::endl;

    } catch (...) {
        // 兜底：捕获所有异常
        std::cout << "发生未知错误" << std::endl;
        return 1;
    }

    return 0;
}
```

## 最佳实践

1. **总是捕获异常**：调用可能抛出异常的 API 时，使用 `try-catch` 块保护
2. **按照层次捕获**：从最具体的异常类开始捕获，最后捕获基类
3. **检查错误类型**：使用 `getType()` 方法获取错误类型，进行针对性处理
4. **提供用户友好的错误信息**：将内部错误信息转换为用户可理解的提示
5. **资源清理**：在 `catch` 块中进行必要的资源清理

!!! warning
    Yumo audio 的某些操作（如 `addAudio` 使用预加载ID版本）会同步抛出异常，必须在调用处进行捕获。而异步操作（如 `preloadAudio`）的错误信息会存储在 `PreloadedAudio::errorMsg` 中，需要通过检查加载结果来获取错误信息。
