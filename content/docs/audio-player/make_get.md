---
date: 2026-07-13
author: Yumo-sama
avatar: /imgs/yumo.jpg
title: 为make管理的项目引入Yumo audio
summary: 在一个make管理的项目中，引入Yumo audio
tags: ["Yumo audio", "开发", "make","项目"]
weight: 3
---

对于一个make管理的项目（尤指MinGW编译的C++项目），引入Yumo Audio非常轻易，可以在不直接引入源码的情况下将本库接入项目。

核心逻辑是：库文件的获取直接从GitHub下载并自动解压缩

## 准备脚本

将以下脚本保存为`download_audio_lib.ps1`，放在项目根目录（或`Makefile`同级目录）。

这个脚本几乎完全通用，不需要针对你的项目做任何改动，它负责从 GitHub 获取最新的 Release 压缩包、解压并校验库文件。

```powershell
param(
    [string]$Repo,
    [string]$Arch,
    [string]$DownloadDir,
    [string]$TargetFile
)

$ErrorActionPreference = "Stop"

# 1. 创建下载目录
if (-not (Test-Path $DownloadDir)) {
    New-Item -ItemType Directory -Path $DownloadDir -Force | Out-Null
}

$zipPath = Join-Path $DownloadDir "release.zip"

# 2. 获取最新 Release 下载 URL
Write-Host "获取最新 Release 信息..." -ForegroundColor Cyan
$apiUrl = "https://api.github.com/repos/$Repo/releases/latest"
try {
    $response = Invoke-RestMethod -Uri $apiUrl -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Error "无法获取 Release 信息: $_"
    exit 1
}

$pattern = if ($Arch -eq "x64") { "x64" } else { "x86" }
$asset = $response.assets | Where-Object { $_.name -match $pattern } | Select-Object -First 1
if (-not $asset) {
    Write-Error "未找到匹配 '$pattern' 的压缩包"
    exit 1
}

$downloadUrl = $asset.browser_download_url
Write-Host "下载链接: $downloadUrl" -ForegroundColor Gray

# 3. 下载（带重试）
$maxRetries = 3
$attempt = 0
$downloaded = $false
while (-not $downloaded -and $attempt -lt $maxRetries) {
    $attempt++
    Write-Host "下载尝试 $attempt/$maxRetries ..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
        $downloaded = $true
        Write-Host "下载成功" -ForegroundColor Green
    } catch {
        Write-Warning "下载失败 (尝试 $attempt): $_"
        if ($attempt -lt $maxRetries) {
            Write-Host "等待 2 秒后重试..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $downloaded) {
    Write-Error "下载失败，已达最大重试次数"
    exit 1
}

# 4. 验证 ZIP 完整性
Write-Host "验证 ZIP 文件完整性..." -ForegroundColor Cyan
Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
try {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    $zip.Dispose()
    Write-Host "ZIP 文件有效" -ForegroundColor Green
} catch {
    Write-Error "ZIP 文件损坏或无法读取: $_"
    exit 1
}

# 5. 解压
Write-Host "解压到 $DownloadDir ..." -ForegroundColor Cyan
try {
    Expand-Archive -Path $zipPath -DestinationPath $DownloadDir -Force -ErrorAction Stop
    Write-Host "解压完成" -ForegroundColor Green
} catch {
    Write-Error "解压失败: $_"
    exit 1
}

# 6. 删除 ZIP 文件
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

# 7. 验证目标库文件
Write-Host "验证库文件 $TargetFile ..." -ForegroundColor Cyan
if (-not (Test-Path $TargetFile)) {
    Write-Error "库文件不存在: $TargetFile"
    exit 1
}

# 使用 ar 检查格式（需在 PATH 中）
$ar = "ar.exe"
$test = & $ar t $TargetFile 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "库文件格式无效 (ar t 失败): $($test -join "`n")"
    exit 1
}

Write-Host "库文件验证通过" -ForegroundColor Green
Write-Host "所有操作完成！" -ForegroundColor Green
exit 0
```

## 修改makefile

接着，准备makefile，确保makefile与刚刚的powershell脚本在同级目录下：

```makefile
# （可省略的）架构判断
# 主要针对兼容64+32位的项目
ARCH ?= 64
ifeq ($(ARCH),32)
ARCH_TEXT= x86
else
ARCH_TEXT= x64
endif
#你的构建路径（请根据实际修改）
BUILD_DIR := ...
# 库文件下载路径
LIB_DOWNLOAD_PATH := $(BUILD_DIR)/libs
# GitHub仓库名
AUDIO_LIB_REPO    := keybonk-org/audio-player
# 库文件理论实际文件名
AUDIO_LIB := $(LIB_DOWNLOAD_PATH)/audioPlayer_$(ARCH_TEXT).a

$(AUDIO_LIB):
	@echo 正在下载/更新 audio-player 库 ...
	@powershell -ExecutionPolicy Bypass -File "download_audio_lib.ps1" -Repo "$(AUDIO_LIB_REPO)" -Arch "$(ARCH_TEXT)" -DownloadDir "$(LIB_DOWNLOAD_PATH)" -TargetFile "$(AUDIO_LIB)"
	@echo 库已就绪。
```

!!! note
	如果你希望提供一个单独的 update 目标来手动更新库，只需将上述规则中的命令复制到`update`目标的命令中即可，比如：
	```makefile
	update:
		@echo 正在下载/更新 audio-player 库 ...
		@powershell -ExecutionPolicy Bypass -File "download_audio_lib.ps1" -Repo "$(AUDIO_LIB_REPO)" -Arch "$(ARCH_TEXT)" -DownloadDir "$(LIB_DOWNLOAD_PATH)" -TargetFile "$(AUDIO_LIB)"
		@echo 库已就绪。
	```
	不过你也可以将`%(AUDIO_LIB)`作为`update`的依赖，比如：
	```makefile
	update: $(AUDIO_LIB)
		@echo 更新完成。
	```

## 链接

现在，将`$(AUDIO_LIB)`设置为项目编译的最终文件的一个依赖项（通常是`.exe`或`.dll`），并在链接命令中引用它。如果你在链接时使用`$^` 自动展开所有依赖，那么无需额外改动链接命令。

示例：

```makefile
# 链接 
$(BIN): $(CXX_OBJS) $(RES_OBJ) $(AUDIO_LIB) | $(BUILD_DIR)/bin/default
	@echo 正在链接生成可执行文件 $@ ...
	@$(CXX) $(LDFLAGS) $^ -o $@ $(LDLIBS)
```

Yumo Audio 底层依赖三个 Windows 多媒体库，链接时需要显式添加：`-lwinmm -lmsacm32 -lcomdlg32`，你可以将它们添加到你自己makefile中形似于`LDFLAGS`或`LDLIBS`的变量中，比如：

```makefile
LDFLAGS += -lwinmm -lmsacm32 -lcomdlg32
```