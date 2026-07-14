项目现在已经支持文章多作者功能！本文将介绍使用方法

## 使用方式

### 单作者（保持向后兼容）

```yaml
---
date: 2026-07-14 10:00:00
author: yumo-sama
avatar: /imgs/yumo.jpg
title: 我的文章
---
```

### 多作者（新功能）

```yaml
---
date: 2026-07-14 10:00:00
author:
  - name: yumo-sama
    avatar: /imgs/yumo.jpg
  - name: Trae AI
    avatar: /imgs/traeAI.webp
title: 多作者文章
---
```

### 多作者（简化版，无头像）

```yaml
---
date: 2026-07-14 10:00:00
author:
  - name: yumo-sama
  - Trae AI
title: 多作者文章
---
```