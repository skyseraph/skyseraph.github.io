---
title: "飞牛 NAS 家庭免费听书中心"
date: 2025-10-01T08:00:00+08:00
categories: ["技术"] 
tags: ["NAS"]
toc: true
draft: false
---

> 作者：SkySeraph  
> 原始链接：[飞牛 NAS 家庭免费听书中心](https://skyseraph.github.io/posts/2025/fnos_audiobook)  
> 日期：2025-10-01   
> 本文汇总主流听书解决方案，聚焦如何通过飞牛 NAS 打造私有化家庭听书中心，支持喜马拉雅、得到等主流平台内容免费播放。  

---

## 一、方案汇总对比

| 方案 | 资源来源 | 免费程度 | 存储位置 | 多端支持 | 播放体验 | 推荐指数 |
|------|---------|---------|---------|---------|---------|---------|
| **喜马拉雅专辑下载器** | 喜马拉雅 | 免费（需工具） | 飞牛 NAS | 通用 | 依赖播放器 | ⭐⭐⭐⭐ |
| **得到听书本地化** | 得到 | 部分免费 | 飞牛 NAS | 通用 | 依赖播放器 | ⭐⭐⭐ |
| **泛听类 App（豆瓣/蜻蜓）** | 各平台汇总 | 免费+付费混合 | 手机本地 | 移动端为主 | 优秀 | ⭐⭐ |
| **Audiobookshelf** | 自托管 | 完全免费 | 飞牛 NAS | 优秀 | 优秀 | ⭐⭐⭐⭐⭐ |
| **NasTube 音频模式** | 本地媒体 | 免费 | 飞牛 NAS | 一般 | 一般 | ⭐⭐ |
| **RSS 播客订阅** | 播客平台 | 免费 | 飞牛 NAS | 一般 | 一般 | ⭐⭐⭐ |

---

## 二、各方案详细说明

### 方案 1：喜马拉雅专辑下载器（推荐 ⭐⭐⭐⭐）

喜马拉雅是中国最大的音频平台，拥有大量有声书、课程、播客内容。通过第三方下载工具可将付费/免费专辑下载到 NAS，本地播放绕过平台限制。

#### 核心工具

| 工具 | 说明 | 地址 |
|------|------|------|
| **喜马拉雅专辑批量下载器** | 油猴脚本，一键解析专辑所有音频 | [GreasyFork](https://greasyfork.org/scripts/369419-喜马拉雅专辑批量下载器) |
| **ximalaya-tools** | 命令行工具，支持专辑/声音批量下载 | [GitHub](https://github.com/j好好学习/ximalaya-tools) |
| **book155/ximalaya** | Python 实现的喜马拉雅下载工具 | [GitHub](https://github.com/book155/ximalaya) |

#### 工作原理

```
喜马拉雅音频解密流程：

1. 播放请求 → 喜马拉雅服务器
         │
         ▼
2. 返回加密音频流（.m4a /.mp3 切片）
         │
         ▼
3. 下载器获取密钥（通过 PC 端播放器抓包）
         │
         ▼
4. 本地解密合并 → 完整音频文件
         │
         ▼
5. 存储到 NAS → Audiobookshelf 播放
```

---

### 方案 2：得到听书本地化（可选）

得到是知识付费平台，有大量精品听书内容。部分免费课程/听书可下载到本地。

#### 资源类型

| 类型 | 说明 | 免费情况 |
|------|------|---------|
| **每天听本书** | 每天一本解读版听书 | 部分免费 |
| **课程音频** | 各大系列课程 | 付费为主 |
| **电子书** | 配套电子书 | 付费为主 |

> **注意**：得到大部分内容需要付费订阅，免费内容有限。建议优先考虑喜马拉雅。

---

### 方案 3：Audiobookshelf（推荐 ⭐⭐⭐⭐⭐）

开源的自托管有声书服务器，功能强大，专门针对有声书场景优化：

```
优点：
- 完全免费开源，专门为有声书设计
- 支持有声书元数据刮削（Audible / LibriVox）
- 章节导航、时间记忆（上次播放位置）
- 多用户管理、家长控制
- Web / iOS / Android / macOS 全平台客户端
- 支持播客 RSS 订阅

缺点：
- 主要面向英文有声书，中文元数据支持一般
- 需要手动整理中文音频的元数据
```

#### Audiobookshelf 架构图

```
                        ┌──────────────────┐
                        │     飞牛 NAS      │
                        │                  │
                        │  ┌────────────┐  │
                        │  │Audiobook-   │  │
                        │  │shelf       │  │
                        │  │ (Docker)   │  │
                        │  └──────┬─────┘  │
                        │         │         │
                        │    ┌────┴────┐   │
                        │    ▼         ▼   │
                        │  ┌────┐  ┌────┐  │
                        │  │音频│  │元数据│  │
                        │  │文件│  │封面 │  │
                        │  └────┘  └────┘  │
                        └──────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐     ┌──────────┐      ┌──────────┐
        │  手机     │     │  电视     │      │  电脑     │
        │ Android  │     │ (Apple TV │      │ 浏览器   │
        │   App    │     │  / Shield)│      │   App    │
        └──────────┘     └──────────┘      └──────────┘

        Audiobookshelf 支持播放位置同步
        换设备后从上次位置继续
```

---

### 方案 4：RSS 播客订阅（补充）

通过 RSS 订阅播客内容，聚合到 NAS 播放：

```
推荐播客平台：
- 小宇宙（中文播客）
- Apple Podcasts
- Spotify
- Castbox

获取 RSS 地址后，用 Jellyfin/Audiobookshelf 订阅
```

---

## 三、最优方案：喜马拉雅下载 + Audiobookshelf

### 方案优势

1. **资源丰富**：喜马拉雅拥有中文最大有声书库
2. **完全免费**：利用公开工具下载公开内容
3. **跨平台播放**：Audiobookshelf 支持全平台，多设备无缝衔接
4. **播放位置同步**：换设备从上次位置继续，体验接近付费平台
5. **家庭共享**：多用户管理，家长控制

### 完整流程图

```
┌─────────────────────────────────────────────────────┐
│           完整听书流程                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│   喜马拉雅                      飞牛 NAS              │
│       │                          │                  │
│       ▼                          ▼                  │
│  ┌──────────────┐         ┌──────────────┐          │
│  │  油猴脚本     │         │ Audiobook-   │          │
│  │  批量下载    │ ─────► │  shelf       │          │
│  │  专辑音频    │         │              │          │
│  └──────────────┘         └──────┬───────┘          │
│                                  │                  │
│                                  ▼                  │
│                        ┌──────────────────┐          │
│                        │  家庭多设备播放   │          │
│                        │  手机/电视/电脑   │          │
│                        └──────────────────┘          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 四、详细配置步骤

### 第一步：喜马拉雅专辑批量下载器（油猴脚本）

#### 安装步骤

1. **安装 Tampermonkey 浏览器扩展**
   - Chrome：[Tampermonkey Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - Firefox：[Tampermonkey Firefox](https://addons.mozilla.org/zh-CN/firefox/addon/tampermonkey/)

2. **安装喜马拉雅下载脚本**
   - 访问 [GreasyFork - 喜马拉雅专辑批量下载器](https://greasyfork.org/scripts/369419-喜马拉aya专辑批量下载器)
   - 点击 **安装此脚本**

3. **打开喜马拉雅网页版**
   - 访问 [喜马拉雅](https://www.ximalaya.com/)
   - 登录账号（部分付费内容需登录后下载）

> **图解**：油猴脚本安装流程

```
浏览器扩展市场
  │
  ▼
搜索 "Tampermonkey" → 安装
  │
  ▼
访问 GreasyFork 脚本页面
  │
  ▼
点击 "安装此脚本"
  │
  ▼
打开喜马拉雅，出现下载按钮
```

#### 使用方法

1. 打开任意喜马拉雅专辑页面（如：某本有声书）
2. 页面左侧出现 **"批量下载"** 按钮

```
┌─────────────────────────────────────────────────────┐
│  喜马拉雅专辑页面                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [▶ 播放]  [批量下载]  [♥ 收藏]  [📤 分享]         │
│                                                     │
│  专辑: 《xxx 有声书》                                │
│  主播: xxx                                          │
│  时长: 12小时30分                                   │
│  集数: 全100集                                      │
│                                                     │
│  集列表:                                            │
│  ┌─────────────────────────────────────────────┐   │
│  │ ☑ 第1集  xxx     10:32  [下载]              │   │
│  │ ☑ 第2集  xxx     08:45  [下载]              │   │
│  │ ☑ 第3集  xxx     12:01  [下载]              │   │
│  │ ...                                         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  [全选] [反选]              [批量下载选中]           │
└─────────────────────────────────────────────────────┘
```

3. 点击 **全选** → **批量下载选中**
4. 脚本自动解析并下载所有音频文件到浏览器下载目录

> **截图示意**：
> - 图1：Tampermonkey 扩展已安装
> - 图2：喜马拉雅专辑页面下载按钮
> - 图3：批量下载进度

#### 批量下载进阶技巧

```
技巧1：下载整个专辑
在专辑页面点击 "全选" 后再点 "批量下载"，可一次下载全部100集

技巧2：复制下载链接到 NAS
在 NAS 上用 wget/curl 下载：
wget -c "下载链接" -O "第1集.m4a"

技巧3：定时任务自动下载
使用 NAS 上的定时任务，自动抓取订阅的喜马拉雅专辑更新
```

---

### 第二步：将音频文件上传到 NAS

#### 方式 A：直接下载到 NAS（推荐）

如果浏览器可以直接下载到 NAS：

```bash
# 通过 SSH 登录 NAS，创建听书目录
mkdir -p /volume1/audiobooks/喜马拉雅/xxx专辑

# 使用 wget 下载（需获取直链）
wget -c "音频直链" -O "/volume1/audiobooks/xxx/第1集.m4a"
```

#### 方式 B：PC 下载后上传

1. 在 PC 上使用浏览器下载音频文件
2. 通过飞牛 NAS 的 Web 文件管理器上传

```
飞牛 NAS 后台
  └── 文件管理器
        └── /volume1/audiobooks/
              └── xxx专辑/
                    ├── 第1集.m4a
                    ├── 第2集.m4a
                    └── ...
```

#### 方式 C：SMB 共享上传

1. 在文件管理器中访问 `\\<NAS IP>\audiobooks`
2. 直接拖拽上传文件

> **图解**：文件上传方式对比

```
方式A: 直连下载         方式B: PC中转          方式C: SMB上传
┌────────┐              ┌────────┐            ┌────────┐
│浏览器   │              │ PC     │            │ 文件管理器│
└───┬────┘              └───┬────┘            └───┬────┘
    │                        │                      │
    ▼                        ▼                      ▼
┌────────┐              ┌────────┐            ┌────────┐
│NAS存储 │              │上传NAS │            │NAS存储 │
└────────┘              └────────┘            └────────┘
```

---

### 第三步：部署 Audiobookshelf

#### Docker Compose 部署

1. 创建配置目录：

```bash
mkdir -p /volume1/docker/audiobookshelf/{config,metadata,books,podcasts}
```

2. 创建 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  audiobookshelf:
    image: adv4000/audiobookshelf:latest
    container_name: audiobookshelf
    restart: unless-stopped
    ports:
      - "13378:80"    # Web UI 端口
    volumes:
      - /volume1/docker/audiobookshelf/config:/config
      - /volume1/docker/audiobookshelf/metadata:/metadata
      - /volume1/audiobooks:/books        # 有声书目录（映射多个可多个）
      - /volume1/podcasts:/podcasts        # 播客目录
    environment:
      - TZ=Asia/Shanghai
      - AUDIOBOOKSHELF_UID=1000
      - AUDIOBOOKSHELF_GID=1000
```

3. 启动容器：

```bash
cd /volume1/docker/audiobookshelf
docker-compose up -d
```

4. 访问 Web UI：`http://<NAS IP>:13378`

> **截图示意**：
> - 图4：Docker 容器启动成功
> - 图5：Audiobookshelf 初始登录页

---

### 第四步：初始化 Audiobookshelf

#### 创建管理员账号

```
首次访问 http://<NAS IP>:13378
自动跳转到设置向导：

┌─────────────────────────────────────────────────────┐
│  Audiobookshelf Setup                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Create Admin Account                               │
│                                                     │
│  Username:    [admin                            ]   │
│  Password:    [●●●●●●●●●●●                     ]   │
│  Confirm:     [●●●●●●●●●●●                     ]   │
│                                                     │
│  Library Path:                                      │
│  [/books] ← 保持默认或修改                          │
│                                                     │
│                        [ Setup ]                   │
└─────────────────────────────────────────────────────┘
```

#### 添加有声书库

1. 进入 **设置** → **Libraries** → **Add Library**

```
┌─────────────────────────────────────────────────────┐
│  Add Library                                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Name:           [中文听书库                     ]  │
│                                                     │
│  Display Name:   [听书]                            │
│                                                     │
│  Content Type:   [Audiobooks                   ▼]  │
│                                                     │
│  Folder:                                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ /books                                     │   │
│  │ + Add Folder                             [+]│   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ☑ Scan on startup                                │
│  ☑ Metadata language:  Chinese                    │
│                                                     │
│  [ Cancel ]              [ Save ]                 │
└─────────────────────────────────────────────────────┘
```

2. 配置完成后，Audiobookshelf 会自动扫描目录下的有声书

---

### 第五步：手动编辑元数据（中文书）

由于 Audiobookshelf 主要面向英文有声书，中文有声书需要手动编辑：

#### 手动添加元数据

1. 点击任意有声书 → **Edit Metadata**

```
┌─────────────────────────────────────────────────────┐
│  Edit Metadata                                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Title:        [书名：xxx                        ]  │
│                                                     │
│  Author:       [作者：xxx                        ]  │
│                                                     │
│  Cover:        [拖拽上传封面图片              ]     │
│                                                     │
│  Description:                                    │
│  ┌─────────────────────────────────────────────┐   │
│  │ 书籍简介内容...                              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Narrator:    [播音：xxx                         ]  │
│                                                     │
│  Series:      [系列：xxx                         ]  │
│  # in Series: [1]                                 │
│                                                     │
│  [ Cancel ]              [ Save ]                 │
└─────────────────────────────────────────────────────┘
```

#### 批量重命名文件

为了更好识别，建议重命名音频文件：

```
命名规范：
书名 - 第XX集.m4a

示例：
自卑与超越 - 第01集.m4a
自卑与超越 - 第02集.m4a
```

> **图解**：文件重命名建议

```
/volume1/audiobooks/自卑与超越/
├── 自卑与超越 - 第01集.m4a
├── 自卑与超越 - 第02集.m4a
├── 自卑与超越 - 第03集.m4a
└── cover.jpg           # 封面图片
```

---

### 第六步：多用户与家长控制

#### 添加家庭成员

1. **设置** → **Users** → **Add User**

```
┌─────────────────────────────────────────────────────┐
│  Add User                                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Username:    [家庭成员名字                      ]  │
│                                                     │
│  Password:    [●●●●●●●●●●●                     ]  │
│                                                     │
│  Email:       [email@example.com                ]  │
│                                                     │
│  Library Access:                                   │
│  ☑ 中文听书库                                      │
│  ☐ 播客                                           │
│                                                     │
│  Permissions:                                       │
│  ☑ Can play audiobooks                             │
│  ☐ Can download                                   │
│  ☑ Can upload                                     │
│                                                     │
│  [ Cancel ]              [ Save ]                 │
└─────────────────────────────────────────────────────┘
```

#### 家长控制

可设置内容分级，限制某些书籍：

```
家长控制设置：
- 最高分级：选择可访问的内容分级
- 屏蔽标签：添加需要屏蔽的标签
- 使用时间限制：设置每日收听时长限制
```

---

### 第七步：客户端安装与播放

| 设备 | 客户端 | 下载地址 |
|------|--------|---------|
| **iOS / iPad** | Audiobookshelf App | [App Store](https://apps.apple.com/app/audiobookshelf/id1577199399) |
| **Android** | Audiobookshelf App | [Google Play](https://play.google.com/store/apps/details?id=com.audiobookshelf.app) / [APK](https://github.com/adv4000/audiobookshelf-android/releases) |
| **macOS** | Audiobookshelf App | [官网下载](https://www.audiobookshelf.org/downloads) |
| **Windows** | Audiobookshelf App | [官网下载](https://www.audiobookshelf.org/downloads) |
| **网页** | Web 访问 | `http://<NAS IP>:13378` |
| **智能电视** | Jellyfin TV App | 电视应用市场搜索 Jellyfin |

#### 手机 App 配置

1. 下载并打开 Audiobookshelf App
2. 点击 **Add Server**

```
┌─────────────────────────────────────────────────────┐
│  Audiobookshelf                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Server URL:                                        │
│  [ http://192.168.1.100:13378            ]         │
│                                                     │
│  [ Connect ]                                        │
│                                                     │
│  ──────────────────────────────────                │
│  Don't have a server? Get the app on your         │
│  server at audiobooksshelf.org                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

3. 输入用户名密码登录

#### 播放界面

```
┌─────────────────────────────────────────────────────┐
│  ◀ ▶  🔊 1.0x  ━━━━━━━●━━━━━━━━  35:22 / 45:30     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📖 自卑与超越                                      │
│  📝 阿尔弗雷德·阿德勒                               │
│  🎤 播音：xxx                                       │
│                                                     │
│  章节:                                             │
│  ├─ 第1集  00:00 - 45:30                           │
│  ├─ 第2集  00:00 - 40:15                           │
│  └─ 第3集  00:00 - 42:00  ◀ 当前                   │
│                                                     │
│  [ ❤️ 收藏 ]  [ ⏱ 历史 ]  [ 📤 下载离线 ]          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 第八步：喜马拉雅特定内容下载详解

#### 下载整张专辑的命令行方式

使用 `ximalaya-tools` 批量下载：

```bash
# SSH 登录 NAS
ssh admin@<你的NAS IP>

# 安装 ximalaya-tools（需要 Node.js）
npm install -g ximalaya-tools

# 登录喜马拉雅（需要扫码或账号密码）
ximalaya login

# 下载专辑（获取专辑 ID）
ximalaya download album <专辑ID> --output /volume1/audiobooks/xxx
```

#### 获取专辑 ID

1. 打开喜马拉雅专辑页面
2. 复制 URL 中的专辑 ID

```
URL 示例：
https://www.ximalaya.com/revision/play/v1/audio?id=123456789&type=album

专辑 ID = 123456789（从 URL 中提取）
```

> **图解**：从 URL 提取专辑 ID

```
喜马拉雅专辑 URL 结构：

https://www.ximalaya.com/album/123456789
                                 │
                                 ▼
                           专辑 ID: 123456789

命令行下载：
ximalaya-tools download album 123456789 --output /volume1/audiobooks/xxx
```

---

## 五、进阶功能

### 定时自动下载喜马拉雅更新

#### 创建一个下载脚本

```bash
#!/bin/bash
# save as: /volume1/docker/audiobookshelf/scripts/download_ximalaya.sh

ALBUMS=(
  "album_id_1"
  "album_id_2"
)
OUTPUT="/volume1/audiobooks"

for album_id in "${ALBUMS[@]}"; do
  echo "Downloading album: $album_id"
  ximalaya-tools download album "$album_id" --output "$OUTPUT"
done

# 通知 Audiobookshelf 扫描新文件
curl -X POST "http://localhost:13378/api/library"
```

#### 添加定时任务

```bash
# 编辑 crontab
crontab -e

# 每天早上 6 点执行下载
0 6 * * * /volume1/docker/audiobookshelf/scripts/download_ximalaya.sh
```

---

### RSS 播客订阅

Audiobookshelf 支持直接订阅播客 RSS：

1. **设置** → **Podcasts** → **Add Podcast**
2. 输入播客 RSS 地址

```
推荐中文播客 RSS：
- 小宇宙：https://api.xyzcdn.net/v1/feed/xxx
- 或在小宇宙 App 中获取 RSS 地址
```

---

### 有声书自动刮削（英文为主）

Audiobookshelf 内置 [Audible](https://www.audible.com/) 和 [LibriVox](https://librivox.org/) 元数据刮削：

1. 进入书籍详情 → **Match Metadata**
2. Audiobookshelf 自动匹配封面和元数据

> **注意**：中文有声书主要依赖手动编辑。

---

## 六、常见问题

**Q1：喜马拉雅付费内容可以下载吗？**
> 免费内容可下载，付费内容需要订阅。建议支持正版，喜马拉雅会员可享受离线下载。

**Q2：Audiobookshelf 中文显示乱码？**
> 检查 NAS 系统语言设置，Docker 容器 TZ 环境变量设为 `Asia/Shanghai`。

**Q3：有声书文件很大，存储空间不够？**
> 建议使用压缩格式（如 .m4a 而非 .wav），或使用 NAS 外接硬盘扩展存储。

**Q4：播放时卡顿？**
> 检查 NAS 网络带宽和 CPU 占用；Audiobookshelf 支持实时转码，可降低码率播放。

**Q5：能否在开车时收听？**
> iOS/Android App 支持离线下载，提前下载后在车内通过车载蓝牙播放。

---

## 七、总结推荐

| 场景 | 推荐方案 |
|------|---------|
| 中文有声书（喜马拉雅） | 喜马拉雅下载器 + Audiobookshelf |
| 英文有声书 | Audiobookshelf + Audible 刮削 |
| 播客订阅 | Audiobookshelf 内置 RSS |
| 得到课程 | 得到 App 离线缓存（付费） |
| 家庭多用户共享 | Audiobookshelf 多用户 |

**最优方案**：`喜马拉雅下载 + Audiobookshelf`

- 中文资源最丰富
- 完全免费（下载工具 + 播放服务）
- 多设备无缝衔接，播放位置同步
- 完全私有，不经过第三方

---

## 八、参考来源

1. [Audiobookshelf 官方文档](https://www.audiobookshelf.org/)
2. [Audiobookshelf GitHub](https://github.com/adv4000/audiobookshelf)
3. [喜马拉雅专辑批量下载器 - GreasyFork](https://greasyfork.org/scripts/369419-喜马拉雅专辑批量下载器)
4. [ximalaya-tools GitHub](https://github.com/book155/ximalaya)
5. [Tampermonkey 官方](https://www.tampermonkey.net/)
6. [LibriVox 公共的有声书](https://librivox.org/)
7. [小宇宙播客平台](https://www.xiaoyuziatv.com/)
8. [飞牛 NAS Docker 部署指南](https://www.fnnas.com/help/docker)

---

*更新时间：2026-05-01*