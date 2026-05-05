---
title: "飞牛 NAS 家庭影视中心"
date: 2025-10-01T08:00:00+08:00
categories: ["技术"] 
tags: ["NAS"]
toc: true
draft: false
---

> 作者：SkySeraph  
> 原始链接：[飞牛 NAS 家庭影视中心](https://skyseraph.github.io/posts/2025/fnos_video)  
> 日期：2025-10-01   
> 本文汇总主流家庭影视方案，聚焦如何通过飞牛 NAS 打造私有化家庭媒体中心，实现影视、照片多端播放与同步。  

---

## 一、方案汇总对比

| 方案 | 类型 | 存储位置 | 视频格式支持 | 转码能力 | 多设备支持 | 费用 | 推荐指数 |
|------|------|---------|-------------|---------|-----------|------|---------|
| **Plex** | 商业媒体服务器 | 飞牛 NAS | 广泛 | 硬件加速 | 优秀 | 免费+付费 ($5/月) | ⭐⭐⭐⭐ |
| **Jellyfin** | 开源媒体服务器 | 飞牛 NAS | 广泛 | 软件转码 | 优秀 | 完全免费 | ⭐⭐⭐⭐⭐ |
| **Emby** | 商业媒体服务器 | 飞牛 NAS | 广泛 | 硬件加速 | 优秀 | 免费+付费 | ⭐⭐⭐ |
| **Kodi** | 本地播放器 | 设备本地 | 广泛 | 依赖设备 | 单设备 | 免费 | ⭐⭐ |
| **Infuse** | iOS/macOS 播放器 | 远程服务器 | 广泛 | 服务器转码 | 单一平台 | 付费 ($8/年) | ⭐⭐⭐ |
| **DLNA / UPnP** | 协议推送 | 飞牛 NAS | 一般 | 无 | 一般 | 免费 | ⭐⭐ |
| **飞牛影视（自带的）** | 官方套件 | 飞牛 NAS | 一般 | 一般 | 一般 | 免费 | ⭐⭐⭐ |

---

## 二、各方案详细说明

### 方案 1：飞牛影视（官方套件）

飞牛 NAS 自带的影视管理套件，开箱即用：

```
优点：
- 无需配置，直接使用
- 与 NAS 系统深度集成
- 支持基本的影视刮削（自动识别电影/剧集）

缺点：
- 功能相对简单
- 刮削准确性一般
- 多用户管理能力弱
- 无法精细调教字幕和音轨
```

---

### 方案 2：Jellyfin（推荐 ⭐⭐⭐⭐⭐）

开源免费的媒体服务器，功能强大，社区活跃：

```
优点：
- 完全免费开源，无付费墙
- 功能丰富：媒体库、用户管理、实时转码
- 支持硬件加速（Intel QSV / NVENC / AMD）
- 丰富的客户端：Web / Android / iOS / TV / NVIDIA Shield
- 丰富的插件生态
- 数据完全私有

缺点：
- 官方 Docker 镜像较大
- 刮削依赖第三方工具（陈旧的 TMM）
- UI 相对 Plex 稍显朴素
```

---

### 方案 3：Plex（可选）

最成熟的商业媒体服务器，UI 精美，但有付费功能限制：

```
优点：
- UI 精美，用户体验最佳
- 完善的刮削服务（TheMovieDB）
- 丰富的客户端和设备支持
- 强大的转码和串流能力

缺点：
- 最优质的功能需要 Plex Pass（$5/月）
- 某些功能需要联网验证
- 数据存储在 Plex 服务器（隐私顾虑）
```

---

### 方案 4：Emby（可选）

功能介于 Jellyfin 和 Plex 之间，界面美观：

```
优点：
- 界面美观，介于 Jellyfin 和 Plex 之间
- 支持硬件加速
- 移动端 App 体验好

缺点：
- 部分高级功能需要付费
- 社区活跃度不如 Jellyfin
```

---

### 方案 5：DLNA / UPnP（简单场景）

最简单的方式，直接通过 DLNA 协议推送媒体到电视/音箱：

- 飞牛 NAS 内置 DLNA 服务
- 电视/音箱直接发现并播放
- 无需额外安装 App
- 缺点：功能单一，不支持字幕选择/音轨切换

---

## 三、最优方案：Jellyfin + 迅雷影院

### 方案优势

1. **完全免费**：无任何付费墙，所有功能开源
2. **完全私有**：数据存储在自有 NAS，不经过任何第三方
3. **硬件加速**：支持 Intel / NVIDIA / AMD 显卡加速转码
4. **多端覆盖**：Web / TV / 手机 / 平板 / 游戏主机
5. **字幕支持**：支持内挂/外置字幕，自动匹配

### 同步架构图

```
                        ┌──────────────────┐
                        │     飞牛 NAS      │
                        │                  │
                        │  ┌────────────┐  │
                        │  │  Jellyfin   │  │
                        │  │  Docker     │  │
                        │  └──────┬─────┘  │
                        │         │         │
                        │    ┌────┴────┐   │
                        │    ▼         ▼   │
                        │  ┌────┐  ┌────┐  │
                        │  │媒体│  │字幕│  │
                        │  │文件│  │缓存│  │
                        │  └────┘  └────┘  │
                        └──────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐     ┌──────────┐      ┌──────────┐
        │  电视     │     │  手机     │      │  电脑     │
        │ (Apple TV │     │(Android  │      │(浏览器   │
        │  / Shield)│     │   / iOS) │      │  / App)  │
        └──────────┘     └──────────┘      └──────────┘

        各设备通过 Jellyfin 客户端或 Web 访问媒体库
```

---

## 四、详细配置步骤

### 第一步：准备媒体文件

#### 目录结构建议

```
/volume1/media/                    # 媒体库根目录
├── movies/                        # 电影
│   ├── The.Matrix.1999/           # 电影文件夹（带年份便于识别）
│   │   ├── The.Matrix.1999.mkv   # 媒体文件
│   │   └── The.Matrix.1999.srt   # 字幕文件（同名）
│   └── Inception.2010/
│       └── Inception.2010.mkv
├── tv/                            # 剧集
│   └── Stranger.Things/
│       ├── Season 1/
│       │   ├── Stranger.Things.S01E01.mkv
│       │   └── Stranger.Things.S01E02.mkv
│       └── Season 2/
├── documentaries/                  # 纪录片
└── home-videos/                   # 家庭视频
    └── 2025/
```

> **图解**：媒体文件命名规范

```
命名规范（重要！）：
┌─────────────────────────────────────────────────────┐
│  电影：                                             │
│  The.Matrix.1999.1080p.BluRay.x264.mkv             │
│  电影名.年份.分辨率.来源.编码                        │
│                                                     │
│  剧集：                                             │
│  Stranger.Things.S01E01.The.Strange.World.mkv      │
│  剧名.SxxExx.集标题                                  │
│                                                     │
│  字幕（与媒体文件同名）：                            │
│  The.Matrix.1999.srt                                │
└─────────────────────────────────────────────────────┘
```

#### 命名工具推荐

- [FileBot](https://www.filebot.net/)：最强大的媒体文件重命名工具（付费）
- [tinyMediaManager](https://www.tinymediamanager.org/)：免费开源的媒体刮削工具
- [Sonarr](https://sonarr.tv/)：自动化剧集下载与整理
- [Radarr](https://radarr.video/)：自动化电影下载与整理

---

### 第二步：飞牛 NAS 开启 SSH（如需）

> 大部分 Docker 部署可通过 Web UI 完成，SSH 为可选步骤

1. 登录飞牛 NAS 后台 → **控制面板** → **终端**
2. 启用 SSH 服务
3. 使用 PuTTY（Windows）或终端（macOS）登录：

```bash
ssh admin@<你的NAS IP>
```

---

### 第三步：安装 Jellyfin（Docker 方式）

#### 方式 A：通过 Portainer 部署（推荐新手）

Portainer 是可视化的容器管理工具，飞牛 NAS 可通过 Docker 安装：

**步骤 1：安装 Portainer**

```
应用中心 → 搜索 "Portainer" → 安装
```

**步骤 2：配置 Jellyfin 容器**

1. 打开 Portainer Web UI（`http://<NAS IP>:9000`）
2. 点击 **Containers** → **Add container**
3. 填写配置：

```
┌─────────────────────────────────────────────────────┐
│  Add Container                                      │
├─────────────────────────────────────────────────────┤
│  Name:              [jellyfin                    ]   │
│  Image:             [jellyfin/jellyfin:latest  ]   │
│                                                     │
│  Port mapping:                                      │
│  ┌──────────┬────────────┐                         │
│  │  Host    │  Container │                         │
│  ├──────────┼────────────┤                         │
│  │  8096    │  8096      │  # Web UI               │
│  │  8920    │  8920      │  # HTTPS（可选）         │
│  └──────────┴────────────┘                         │
│                                                     │
│  Volume mapping:                                    │
│  ┌────────────────────────────────────────────┐    │
│  │  Host path           │  Container path     │    │
│  ├────────────────────────────────────────────┤    │
│  │  /volume1/media      │  /media              │    │
│  │  /volume1/docker/jellyfin/config /config    │    │
│  │  /volume1/docker/jellyfin/cache  /cache     │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  Restart policy:    [unless-stopped              ]   │
│                                                     │
│  [ Deploy the container ]                          │
└─────────────────────────────────────────────────────┘
```

> **图解**：Portainer 容器配置界面

```
Portainer Web UI
  └── Containers
        └── Add container
              ├── Name: jellyfin
              ├── Image: jellyfin/jellyfin:latest
              ├── Ports: 8096:8096
              └── Volumes: /volume1/media:/media
```

**步骤 3：配置硬件转码（可选）**

如需使用 NVIDIA 显卡转码，需添加额外配置：

```
额外环境变量：
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=all

设备映射：
/dev/nvidia0:/dev/nvidia0
/dev/nvidiactl:/dev/nvidiactl
/dev/nvidia-uvm:/dev/nvidia-uvm
```

#### 方式 B：通过 docker-compose 部署（推荐有经验者）

1. 创建配置目录：

```bash
mkdir -p /volume1/docker/jellyfin/{config,cache,media}
```

2. 创建 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    ports:
      - "8096:8096"      # Web UI
      - "8920:8920"      # HTTPS（可选）
    volumes:
      - /volume1/media:/media:ro        # 媒体文件夹（只读）
      - /volume1/docker/jellyfin/config:/config
      - /volume1/docker/jellyfin/cache:/cache
    environment:
      - TZ=Asia/Shanghai
      - JELLYFIN_PublishedServerUrl=http://<你的NAS IP>:8096
    # GPU 转码（Intel）
    devices:
      - /dev/dri:/dev/dri
    # GPU 转码（NVIDIA）
    # devices:
    #   - /dev/nvidia0:/dev/nvidia0
    # environment:
    #   - NVIDIA_VISIBLE_DEVICES=all
```

3. 启动容器：

```bash
cd /volume1/docker/jellyfin
docker-compose up -d
```

---

### 第四步：初始化 Jellyfin

1. 访问 Jellyfin Web UI：`http://<NAS IP>:8096`
2. 首次登录引导：

```
┌─────────────────────────────────────────────────────┐
│  Welcome to Jellyfin!                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Step 1: 创建管理员账号                             │
│  ┌─────────────────────────────────────────────┐   │
│  │ Username:    [admin                        ]   │
│  │ Password:    [●●●●●●●●●●●               ]   │
│  │ Confirm:     [●●●●●●●●●●●               ]   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  [ Next ]                                           │
└─────────────────────────────────────────────────────┘
```

3. 配置媒体库：

```
┌─────────────────────────────────────────────────────┐
│  Add Media Library                                  │
├─────────────────────────────────────────────────────┤
│  Content type:    [Movies                        ▼] │
│                                                     │
│  Display name:    [电影库                        ] │
│                                                     │
│  Folder paths:                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │ /media/movies                               │   │
│  │ + Add                                    [+] │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Metadata language:   [ Chinese (zh-CN)        ▼]   │
│                                                     │
│  ☑ Automatically refresh metadata from internet   │
│                                                     │
│  [ Cancel ]              [ OK ]                   │
└─────────────────────────────────────────────────────┘
```

4. 重复添加剧集、纪录片等媒体库

---

### 第五步：配置媒体刮削

Jellyfin 依赖 **TheMovieDB**（TMDB）进行刮削，需配置：

1. 进入 **设置** → **服务器** → **媒体库**
2. 点击 **扫描媒体库** 或设置定时刷新
3. 配置刮削信息源优先级：

```
刮削顺序（建议）：
1. TheMovieDB（电影/剧集）
2. TheTVDB（剧集备用）
3. 手动修正（自动刮削后人工检查）
```

> **截图示意**：
> - 图1：Jellyfin 媒体库设置
> - 图2：电影识别结果

#### 手动修正封面/简介

1. 进入电影详情页
2. 点击右上角 **编辑**
3. 手动搜索匹配正确的信息

---

### 第六步：安装客户端

| 设备 | 推荐客户端 | 下载地址 |
|------|-----------|---------|
| **智能电视 / TV Box** | Jellyfin TV App | 电视应用市场搜索 "Jellyfin" |
| **Apple TV** | Jellyfin for Apple TV | App Store |
| **Android TV** | Jellyfin for Android TV | Google Play |
| **NVIDIA Shield** | Jellyfin for Android TV | Google Play |
| **iOS / iPad** | Jellyfin for iOS | App Store |
| **Android 手机** | Jellyfin for Android | Google Play |
| **电脑浏览器** | Web 访问（无需安装） | `http://<NAS IP>:8096` |
| **macOS** | Jellyfin for Apple TV（通用）| App Store |
| **Windows** | Jellyfin for Windows | [官网下载](https://jellyfin.org/downloads/) |

#### 智能电视安装指引

以 Android TV 为例：

1. 打开电视应用市场（如当贝市场、小米应用商店）
2. 搜索 **Jellyfin**
3. 安装并打开
4. 输入 Jellyfin 服务器地址：`http://<NAS IP>:8096`
5. 登录账号即可

> **图解**：TV 客户端连接流程

```
电视打开 Jellyfin App
  │
  ▼
┌─────────────────────────────────────────────────┐
│  Connect to Server                               │
├─────────────────────────────────────────────────┤
│  Server address:                                │
│  [ http://192.168.1.100:8096               ]     │
│                                                 │
│  [ Connect ]                                    │
└─────────────────────────────────────────────────┘
```

---

### 第七步：配置字幕与音轨

#### 字幕配置

Jellyfin 支持多种字幕匹配方式：

1. **内挂字幕**：字幕文件封装在视频中（mkv 内置），自动识别
2. **外置字幕**：与视频同名的 .srt / .ass 文件，自动加载
3. **在线字幕**：通过 OpenSubtitles 等插件自动下载

```
字幕命名规范（外置）：
The.Matrix.1999.srt           # 简体中文
The.Matrix.1999.eng.srt       # 英文
The.Matrix.1999.chs.srt       # 简体中文（另一种命名）
```

#### 音轨配置

1. 在播放时点击右下角设置
2. 选择音轨和字幕
3. 可设置默认语言偏好（**设置** → **播放** → **首选音频/字幕语言**）

---

### 第八步：家庭成员与权限管理

1. 进入 **控制台** → **用户**
2. 点击 **+** 添加用户

```
┌─────────────────────────────────────────────────────┐
│  Create New User                                   │
├─────────────────────────────────────────────────────┤
│  Username:    [家庭成员名字                    ]   │
│  Password:    [●●●●●●●●●●●                   ]   │
│  Confirm:     [●●●●●●●●●●●                   ]   │
│                                                     │
│  Library Access:                                   │
│  ☑ 电影库                                          │
│  ☑ 剧集库                                          │
│  ☑ 纪录片                                          │
│  ☐ 家庭视频                                        │
│                                                     │
│  Parental Control:                                 │
│  ┌─────────────────────────────────────────────┐   │
│  │ Max rating:    [ PG-13                   ▼]  │
│  │ Blocked tags:  [暴力        ] [+ Add]       │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  [ Cancel ]              [ Save ]                │
└─────────────────────────────────────────────────────┘
```

---

## 五、进阶功能

### 远程访问（外网观看）

#### 方案 1：Tailscale（推荐）

```
┌──────────────────────────────────────────────────┐
│  外网观看架构                                      │
├──────────────────────────────────────────────────┤
│                                                  │
│  手机/电脑 ──── Tailscale ──── 飞牛 NAS          │
│  (移动网络)    加密隧道      Jellyfin            │
│                                                  │
└──────────────────────────────────────────────────┘
```

1. 在飞牛 NAS 安装 Tailscale（应用中心搜索）
2. 各设备安装 Tailscale 客户端并登录
3. 通过 Tailscale IP 访问 Jellyfin：`http://<Tailscale IP>:8096`

#### 方案 2：Jellyfin 官方远程访问

Jellyfin 支持配置远程访问代理：

1. **设置** → **服务器** → **远程访问**
2. 启用 **启用远程连接**
3. 可选：配置 **自定义端口映射**

> **注意**：官方远程访问可能受网络环境限制，建议使用 Tailscale。

---

### 自动追剧

配合 Sonarr 实现自动化剧集管理：

```
追剧流程：
1. Sonarr 监控想看的剧集
2. 发现新资源后自动下载
3. 下载完成后自动整理命名
4. Jellyfin 自动刮削更新媒体库
```

#### Sonarr 部署（Docker）

```yaml
version: "3.8"

services:
  sonarr:
    image: linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - /volume1/docker/sonarr/config:/config
      - /volume1/media:/media
    ports:
      - "8989:8989"
    restart: unless-stopped
```

---

### 照片管理：PhotoPrism

家庭照片管理推荐 **PhotoPrism**：

```yaml
version: "3.8"

services:
  photoprism:
    image: photoprism/photoprism:latest
    container_name: photoprism
    environment:
      - PHOTOPRISM_ADMIN_USER=admin
      - PHOTOPRISM_ADMIN_PASSWORD=<你的密码>
      - PHOTOPRISM_SITE_URL=http://<NAS IP>:2342
    volumes:
      - /volume1/photos:/photoprism/originals
      - /volume1/docker/photoprism/config:/photoprism
    ports:
      - "2342:2342"
    restart: unless-stopped
```

---

## 五、常用影视资源站点

> ⚠️ **免责声明**：以下资源仅供学习交流，请尊重版权，使用正版资源。

### 影视资源导航

| 站点类型 | 推荐站点 | 说明 |
|---------|---------|------|
| **综合资源站** | [RARGB](https://rargb.to/) | 国外最大影视资源站，字幕组发布首选 |
| **综合资源站** | [FileList](https://filelist.io/) | 欧洲知名影视站，下载速度快 |
| **综合资源站** | [HDWing](https://hdwing.org/) | 高清资源丰富 |
| **字幕组资源** | [OpenSubtitles](https://www.opensubtitles.org/) | 全球最大字幕库 |
| **字幕组资源** | [SubHD](https://subhd.tv/) | 简体中文字幕下载 |
| **字幕组资源** | [射手网](https://assrt.net/) | 优质中文字幕 |
| **PT 站点** | 各大高校/专业 PT 站 | 高质量、下载快、保种好（需邀请码） |
| **Docker 套件** | 飞牛 NAS 应用中心 | 搜索 "影视" 查看内置资源 |

### 资源评级说明

```
影视资源质量等级（从高到低）：

Blu-ray > REMUX > WEBDL > WEB-DL > HDRip > HDRip > BDRip > DVDrip

说明：
Blu-ray     - 蓝光光盘原盘，容量 20-50GB，画质最佳
REMUX      - 蓝光原盘无损提取，容量 15-30GB，画质无损
WEBDL      - 流媒体平台官方下载，容量 2-5GB
BDRip      - 蓝光压缩版，容量 5-15GB，画质较好
DVDrip     - DVD 压缩版，画质一般

音频质量：
FLAC > DTS > AC3 > MP3

分辨率：
4K > 1080p > 720p > 480p
```

### 搜索技巧

```
搜索格式建议：
电影：[电影名.年份.分辨率.来源.编码]
剧集：[剧名.S01E01.年份.分辨率]

推荐搜索引擎：
- Google: site:rargb.to "电影名"
- RARGB 内置搜索
- FileList 内置搜索
- 各大 PT 站站内搜索
```

---

### 资源命名规范对照表

| 字段 | 示例 | 说明 |
|------|------|------|
| 电影名 | The.Matrix | 英文名，句点分隔 |
| 年份 | 1999 | 上映年份 |
| 分辨率 | 2160p / 1080p / 720p | 4K / 全高清 / 高清 |
| 来源 | BluRay / WEBDL / HDRip | 蓝光/流媒体/压缩版 |
| 编码 | x264 / x265 / H.264 / H.265 | 视频编码格式 |
| 音频 | AAC / AC3 / DTS | 音频编码 |
| 字幕 | CHS / CHT / ENG | 简中/繁中/英文 |

```
完整示例：
The.Matrix.1999.2160p.BluRay.HEVC.DTS-HD.MA.7.1-CHS.srt

分解：
电影名.The.Matrix
年份.1999
分辨率.2160p
来源.BluRay
编码.HEVC
音频.DTS-HD.MA.7.1
字幕.CH
```

---

## 六、下载工具与技巧

### 推荐下载工具

| 工具 | 类型 | 说明 |
|------|------|------|
| **qBittorrent** | BT 下载 | 开源、跨平台、适合 PT |
| **Transmission** | BT 下载 | 轻量、适合低配 NAS |
| **Aria2** | 多协议下载 | 支持 HTTP / FTP / BT / 磁力 |
| **JDownloader2** | 网盘下载 | 自动解析、适合百度网盘 |
| **飞牛 NAS 下载中心** | 内置套件 | 基础下载，适合新手 |

### qBittorrent 部署（Docker）

```yaml
version: "3.8"

services:
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
      - WEBUI_PORT=8080
    volumes:
      - /volume1/docker/qbittorrent/config:/config
      - /volume1/docker/qbittorrent/downloads:/downloads
      - /volume1/media:/media
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"
    restart: unless-stopped
```

#### qBittorrent 关键配置

```
┌─────────────────────────────────────────────────────┐
│  qBittorrent 设置优化                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  工具 → 选项 → 连接：                                │
│  ├─ 监听端口:      [ 6881 ]                        │
│  ├─ 监听端口UDP:   [ 6881 ]                        │
│  └─ UPnP:          [ ☐ 禁用 ]                      │
│                                                     │
│  工具 → 选项 → 速度：                                │
│  ├─ 最大下载:      [ 无限制 ]                      │
│  └─ 最大上传:      [ 设为 0 或限速 1MB/s ]         │
│                                                     │
│  工具 → 选项 → 高级：                                │
│  ├─ 内存使用:      [ 根据 NAS 内存设置 ]           │
│  └─ tracker:       [ 添加高校 PT tracker ]         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

> **图解**：qBittorrent Web UI

```
┌─────────────────────────────────────────────────────┐
│  qBittorrent                                    [▼] │
├─────────────────────────────────────────────────────┤
│  [🔍 搜索]  [📁 种子文件]  [📊 速度]               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  下载中 (3)                                         │
│  ┌─────────────────────────────────────────────────┐ │
│  │ ████████████░░░░░░░  45%                       │ │
│  │ 电影名.The.Matrix.1999.2160p.BluRay            │ │
│  │ 📥 12.5 MB/s  📤 0.5 MB/s  ⏱ 02:34:20         │ │
│  └─────────────────────────────────────────────────┘ │
│                                                     │
│  已完成 (15)                                        │
│  ├─ 电影名1.mkv       [已做种]                     │
│  ├─ 电影名2.mkv       [已做种]                     │
│  └─ 剧集.S01E01.mkv   [已做种]                     │
│                                                     │
│  [ 继续 ]  [ 暂停 ]  [ 删除 ]                      │
└─────────────────────────────────────────────────────┘
```

---

### PT 站下载技巧

#### PT 是什么？

PT（Private Tracker）是小众私用种子站，相比公共 BT：
- **高质量**：资源经过审核，画质有保证
- **保种**：用户有义务做种，否则被封
- **速度快**：站点服务器带宽充足
- **隐私**：相比公共 BT 更安全

#### PT 下载注意事项

```
PT 站行为规范：
1. 保持足够的分享率（通常要求 >1.0）
   - 下载 100GB，需上传 >100GB
2. 定期登录保持活跃
3. 不要使用吸血客户端（会被封号）
4. 遵守站点规则，不发布违规内容

推荐客户端设置：
- qBittorrent（最推荐，支持 PT 协议）
- Transmission（轻量，部分 PT 站认可）
```

#### 做种与保种

```
为什么要做种？
- PT 站要求保持分享率
- 做种帮助其他人下载
- 长时间不做种会被取消资格

qBittorrent 保种设置：
┌─────────────────────────────────────────────────────┐
│  选项 → 任务 → 种子设置                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  初始状态：      [ ✔ 强制做种                    ]  │
│  最大连接数:     [ 100 ]                           │
│  最大 peers:     [ 20 ]                            │
│                                                     │
│  seeding time:   [ 至少保持 7 天 ]                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 自动化下载：Prowlarr + Sonarr + Radarr

完整自动化追剧/追影流程：

```
┌─────────────────────────────────────────────────────┐
│  自动化下载流程                                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│   Prowlarr          Sonarr / Radarr                 │
│   (索引管理器)  ──►  (下载编排)  ──►  qBittorrent    │
│        │                  │                │          │
│        │                  │                ▼          │
│        │                  │           ┌────────┐      │
│        │                  │           │ NAS     │      │
│        │                  ▼           │ 媒体库  │      │
│        │            ┌──────────────┐  └────────┘      │
│        │            │  Jellyfin    │      ▲          │
│        └──────────► │  自动刮削    │──────┘          │
│                     └──────────────┘                  │
│                                                     │
└─────────────────────────────────────────────────────┘

Prowlarr：聚合全网影视资源索引（RARGB、FileList 等 PT 站）
Sonarr：监控/自动下载剧集
Radarr：监控/自动下载电影
```

#### Prowlarr + Sonarr 部署

```yaml
version: "3.8"

services:
  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - /volume1/docker/prowlarr/config:/config
    ports:
      - "9696:9696"
    restart: unless-stopped

  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - /volume1/docker/sonarr/config:/config
      - /volume1/media:/media
    ports:
      - "8989:8989"
    depends_on:
      - prowlarr
    restart: unless-stopped
```

#### Sonarr 配置步骤

1. 访问 Sonarr（`http://<NAS IP>:8989`）
2. **添加索引器**：连接到 Prowlarr
3. **添加下载客户端**：qBittorrent（端口 8080）
4. **添加监控**：
   - 电视剧：输入想看的剧名
   - 设置下载质量（优先 REMUX / WEBDL）
5. 自动化流程：

```
用户添加 → Sonarr 搜索 → Prowlarr 查索引 → 获取种子 → qBittorrent 下载 → 自动整理 → Jellyfin 更新
```

---

## 七、常见问题

**Q1：电视上找不到 Jellyfin App？**
> 部分国内电视可能没有应用市场，可通过安装 APK 或使用当贝市场搜索。部分品牌（小米/华为）需从自带应用市场搜索。

**Q2：播放卡顿、经常转圈？**
> 检查：1) 网络带宽是否足够；2) 是否触发了转码（尝试直接播放原画）；3) NAS 性能是否足够（CPU 占用）。

**Q3：字幕不显示？**
> 确认字幕文件名与视频文件完全一致（同目录同文件名），如使用外置字幕，检查是否放入 `/media/movies/` 同名文件夹。

**Q4：海报/封面不显示？**
> 确认 NAS 时间正确，Jellyfin 能联网获取 TMDB 数据；检查媒体库扫描是否有错误。

**Q5：如何备份 Jellyfin 配置？**
> 定期备份 `/volume1/docker/jellyfin/config` 目录（含用户数据、媒体库配置）。

**Q6：下载速度慢？**
> 1) 检查是否为保种阶段（无 peers）；2) 尝试添加更多 tracker；3) 使用 PT 站获得更好速度。

---

## 八、总结推荐

| 场景 | 推荐方案 |
|------|---------|
| 基础影视播放 | 飞牛 NAS 内置影视套件 |
| 家庭影院（功能完整） | Jellyfin + 迅雷影院 |
| 外网远程观看 | Tailscale + Jellyfin |
| 照片管理 | PhotoPrism |
| 自动追剧 | Sonarr + Jellyfin |
| 高质量下载 | qBittorrent + PT 站 |
| 全自动化 | Prowlarr + Sonarr/Radarr + qBittorrent + Jellyfin |

**最优方案**：`Jellyfin + Tailscale`

- 完全免费，功能完整
- 完全私有，数据不经过第三方
- 硬件加速支持（Intel/NVIDIA/AMD）
- 多端覆盖（TV/手机/电脑）
- 远程访问方案简单可靠

---

## 九、参考来源

1. [Jellyfin 官方文档](https://jellyfin.org/docs/)
2. [Jellyfin Docker 部署指南](https://jellyfin.org/docs/general/administrators/installing.html)
3. [tinyMediaManager 官网](https://www.tinymediamanager.org/)
4. [Sonarr 官方文档](https://sonarr.tv/)
5. [Radarr 官方文档](https://radarr.video/)
6. [PhotoPrism 官方文档](https://docs.photoprism.app/)
7. [Tailscale 官方文档](https://tailscale.com/)
8. [飞牛 NAS Docker 部署指南](https://www.fnnas.com/help/docker)
9. [qBittorrent 官方文档](https://www.qbittorrent.org/)
10. [OpenSubtitles 字幕库](https://www.opensubtitles.org/)
11. [SubHD 字幕站](https://subhd.tv/)
12. [RARGB 影视资源站](https://rargb.to/)

---

*更新时间：2026-05-01*