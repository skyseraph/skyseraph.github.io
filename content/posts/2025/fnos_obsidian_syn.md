---
title: "飞牛 NAS + Obsidian 多端同步方案"
date: 2025-10-01T08:00:00+08:00
categories: ["技术"] 
tags: ["NAS","Obsidian"]
toc: true
draft: false
---

> 作者：SkySeraph  
> 原始链接：[飞牛 NAS + Obsidian 多端同步方案](https://skyseraph.github.io/posts/2025/fnos_obsidian_syn)  
> 日期：2025-10-01   
> 本文汇总主流 Obsidian 同步方案，聚焦如何通过飞牛 NAS 实现私有化多端同步。  

---

## 一、方案汇总对比

| 方案 | 同步原理 | 存储位置 | 多设备冲突处理 | 优点 | 缺点 | 推荐指数 |
|------|---------|---------|--------------|------|------|---------|
| **Obsidian Sync**（官方） | 官方云服务 | 官方服务器 | 自动合并 | 体验最佳、稳定 | 付费 $8/月、私有性低 | ⭐⭐⭐ |
| **iCloud / OneDrive** | 文件夹同步 | 云盘 | 冲突文件保留副本 | 无额外成本 | 同步慢、不支持符号链接、移动端文件组织混乱 | ⭐⭐ |
| **Git + GitHub/Gitea** | 版本控制 | 自托管或云端 | 手动 merge | 完全免费、版本可控 | 不支持二进制、手动 push/pull、操作繁琐 | ⭐⭐⭐ |
| **Rsync / Syncthing** | 点对点同步 | 本地 NAS | 冲突保留双方 | 完全私有、免费 | 配置复杂、无自动冲突解决、多设备同时修改有风险 | ⭐⭐⭐ |
| **WebDAV** | HTTP 文件服务 | 飞牛 NAS | 无自动合并（插件处理） | 兼容性好、NAS 原生支持 | 无原生冲突解决 | ⭐⭐⭐⭐ |
| **Cloudflare Tunnel + 私有 Git** | Git + 内网穿透 | 自托管 | 自动 merge | 完全私有、可团队协作 | 配置门槛较高 | ⭐⭐⭐ |

---

## 二、各方案详细说明

### 方案 1：Obsidian 官方 Sync（不推荐）

- **原理**：Obsidian 自建加密同步服务
- **费用**：$8/月（个人）/ $16/月（团队）
- **缺点**：数据在第三方、非真正私有

---

### 方案 2：iCloud / OneDrive 文件夹同步（不推荐）

- **原理**：将保险库直接放在云盘同步文件夹
- **问题**：移动端体验差，多设备同时编辑易冲突，删除同步文件夹会引发连锁反应

---

### 方案 3：Git 版本控制（可用）

适合开发者背景用户，配合 GitHub 或 Gitea 自托管：

```
优点：
- 完全免费
- 版本历史完整
- 可团队协作

缺点：
- 不适合二进制附件（图片、PDF）
- 需手动操作（git add / commit / push）
- 多人同时编辑风险高
```

推荐搭配 **Obsidian Git** 插件，可实现自动 commit 和定时 push。

---

### 方案 4：Rsync / Syncthing（可选）

点对点同步，完全私有：

```
优点：
- 完全免费、无需公网暴露
- NAS 作为同步节点

缺点：
- 无冲突自动合并
- 同时编辑可能覆盖
- 配置复杂
```

---

### 方案 5：WebDAV（推荐 ⭐）

飞牛 NAS 内置 WebDAV 服务，搭配 **Remotely Save** 插件：

| 项目 | 说明 |
|------|------|
| 存储位置 | 飞牛 NAS 本地 |
| 同步方式 | HTTP/WebDAV |
| 冲突处理 | 冲突时保存为副本文件（Remotely Save 处理） |
| 私有性 | 完全私有 |
| 成本 | 免费（利用已有 NAS） |

> 推荐原因：飞牛 NAS 原生支持 WebDAV，无需额外安装套件，配置简单，安全性高。

---

## 三、最优方案：WebDAV + Remotely Save

### 方案优势

1. **完全私有**：数据存储在自有 NAS，不经过任何第三方
2. **兼容性好**：WebDAV 是标准协议，Obsidian 生态插件支持完善
3. **配置简单**：飞牛 NAS 一键开启，无需折腾
4. **跨平台**：支持 Windows / macOS / Linux / iOS / Android

### 同步架构图

```
                        ┌─────────────┐
                        │  飞牛 NAS   │
                        │  (WebDAV)  │
                        └──────┬──────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐     ┌──────────┐      ┌──────────┐
        │ Windows  │     │   macOS  │      │  iOS /   │
        │   PC     │     │   Mac    │      │ Android  │
        └──────────┘     └──────────┘      └──────────┘

        多设备通过 WebDAV 协议读写同一保险库
        Remotely Save 插件负责冲突副本管理
```

---

### 详细配置步骤

#### 第一步：飞牛 NAS 开启 WebDAV

> **图解**：飞牛 NAS 后台 → 控制面板 → 应用服务 → WebDAV

```
操作路径：
飞牛 NAS 后台
  └── 控制面板
        └── 应用服务
              └── WebDAV → 启用
```

1. 登录飞牛 NAS 后台（`http://<你的NAS IP>:3000`）
2. 进入 **控制面板** → **应用服务** → **WebDAV**
3. 启用 WebDAV 服务，记下：
   - 服务地址：`http://<NAS IP>:<端口>/dav/`
   - 用户名 / 密码（就是你 NAS 的账号密码）
4. 创建同步专用文件夹，例如：`/volume1/obsidian-vault`

> **截图示意**（请根据实际界面补充）：
> - 图1：控制面板 → 应用服务 入口
> - 图2：WebDAV 设置页面，启用开关
> - 图3：创建好的 obsidian-vault 文件夹

#### 第二步：创建 Obsidian 保险库

1. Obsidian 中新建保险库，命名为 `obsidian-vault`
2. 建议放在本地磁盘中（如 `D:\Obsidian\obsidian-vault`），后续配置远程同步
3. 将保险库路径记下来，后续配置需要

```
保险库目录结构示例：
obsidian-vault/
├── .obsidian/          # Obsidian 配置（含插件配置）
├── 附件/                # 图片、PDF 等附件
│   └── image.png
├── 笔记/
│   ├── 工作/
│   └── 私人/
└── vault-config.json   # 保险库元数据
```

#### 第三步：安装 Remotely Save 插件

> **图解**：Obsidian 设置 → 第三方插件 → 搜索 Remotely Save

```
操作路径：
Obsidian
  └── 设置（左下角齿轮图标）
        └── 第三方插件
              └── 社区插件市场
                    └── 搜索 "Remotely Save"
                          └── 安装 → 启用
```

1. 打开 Obsidian → 设置（ 左下角齿轮图标）
2. 进入 **第三方插件** → 关闭安全模式
3. 点击 **社区插件市场**，搜索 **Remotely Save**
4. 安装并启用插件

> **截图示意**：
> - 图4：第三方插件页面，安全模式已关闭
> - 图5：社区插件市场搜索 Remotely Save
> - 图6：Remotely Save 插件安装完成

#### 第四步：配置 WebDAV 远程

> **图解**：Remotely Save 配置界面参数填写

在 Remotely Save 插件设置中填写以下参数：

| 参数 | 填写内容 | 说明 |
|------|---------|------|
| Remote service | `WebDAV` | 选择 WebDAV 协议 |
| WebDAV URL | `http://<NAS IP>:<端口>/dav/` | 飞牛 NAS 的 WebDAV 地址 |
| Username | 你的飞牛 NAS 用户名 | 如 `admin` |
| Password | 飞牛 NAS 密码 | 对应用户名的密码 |
| Vault name or subfolder | `/obsidian-vault/` | 与 NAS 上创建的文件夹名一致 |
| Don't delete remote files | ✅ 开启 | 防止误删远程文件 |
| Conflict handling | `Create a copy` | 冲突时保留副本 |

> **截图示意**：
> - 图7：Remotely Save 配置面板，填写 WebDAV 参数
> - 图8：关键参数对照表

```
┌─────────────────────────────────────────────────────┐
│  Remotely Save 设置                                  │
├─────────────────────────────────────────────────────┤
│  Remote service:    [WebDAV              ▼]         │
│                                                      │
│  WebDAV URL:       http://192.168.1.100:3000/dav/   │
│                                                      │
│  Username:         admin                             │
│  Password:         ●●●●●●●●                          │
│                                                      │
│  Vault name:       /obsidian-vault/                  │
│                                                      │
│  ☐ Don't delete remote files                    [✅] │
│  Conflict handling: [Create a copy          ▼]       │
│                                                      │
│                          [ Check remote ] [ Save ]   │
└─────────────────────────────────────────────────────┘
```

点击 **Check remote** 验证连接，确认成功后点击 **Save** 保存。

#### 第五步：验证同步

1. 在 PC 上新建一条笔记，输入测试内容
2. 点击左侧边栏 Remotely Save 图标 → 点击 **Sync Now** 按钮
3. 观察同步状态，出现 ✅ 即成功

> **截图示意**：
> - 图9：Remotely Save 同步按钮位置
> - 图10：同步成功状态

4. 在另一台设备（手机）上：
   - 打开 Obsidian App
   - 同样安装 Remotely Save 插件并配置相同参数
   - 点击 Sync Now，从 NAS 下载保险库

---

#### 移动端配置（iOS / Android）

```
┌─────────────────────────────────────────────────────┐
│                    iOS / Android                     │
│                                                      │
│  1. 从 App Store / Play Store 下载 Obsidian          │
│                                                      │
│  2. 安装 Remotely Save 插件（步骤同 PC）            │
│                                                      │
│  3. 配置相同的 WebDAV 参数                           │
│                                                      │
│  4. 首次同步：从 NAS 下载完整保险库（可能有延迟）    │
│                                                      │
│  5. 之后每次编辑后手动点 Sync 同步                   │
└─────────────────────────────────────────────────────┘
```

> **注意**：首次同步建议在 Wi-Fi 环境下进行，保险库较大的话会消耗较多流量和时间。

---

## 四、多设备同步最佳实践

```
同步前检查清单：
┌────────────────────────────────────────────────────┐
│  ☑ 确认 NAS WebDAV 服务正常运行                     │
│  ☑ 确认各设备 Remotely Save 参数一致                │
│  ☑ 确认网络互通（内网测试）                         │
│  ☑ 首次同步前可备份本地保险库                       │
└────────────────────────────────────────────────────┘
```

1. **避免同时编辑同一笔记**：WebDAV 无自动锁，建议同一笔记同一时间只在一端编辑
2. **定期手动同步**：点击 Remotely Save 的同步按钮，而非依赖后台自动
3. **开启冲突副本**：发生冲突时 Remotely Save 会创建 `conflict-xxx-YYYYMMDDHHMMSS.md` 副本，便于人工合并
4. **图片附件**：建议使用相对路径存储（如 `./附件/`），Obsidian 自带附件同步无需额外配置
5. **保险库不要放在 iCloud/OneDrive 文件夹**：避免双重同步冲突

---

## 五、进阶方案：内网穿透实现外网访问

如需在外网环境同步，需要将 NAS 的 WebDAV 暴露到公网：

### 方案对比

| 方案 | 复杂度 | 成本 | 稳定性 | 推荐度 |
|------|--------|------|--------|--------|
| **Tailscale** | 低 | 免费（个人用途） | 稳定 | ⭐⭐⭐⭐⭐ |
| **Cloudflare Tunnel** | 中 | 免费 | 稳定 | ⭐⭐⭐⭐ |
| **蒲公英 VPN** | 低 | 免费 | 一般 | ⭐⭐⭐ |
| **DDNS + 端口映射** | 中 | 需公网 IP | 依赖网络 | ⭐⭐⭐ |

### Tailscale 部署步骤（推荐）

> **图解**：Tailscale 网络架构

```
你的设备                          飞牛 NAS
   │                                  │
   │    Tailscale 虚拟网络             │
   ▼                                  ▼
┌──────┐                         ┌──────┐
│手机   │ ←─── 加密隧道 ────→   │ NAS   │
│电脑   │                         │(WebDAV)│
└──────┘                         └──────┘

外网设备通过 Tailscale IP 访问 NAS 的 WebDAV
```

**部署步骤：**

1. **NAS 端安装 Tailscale**
   - 在飞牛 NAS 的应用中心搜索并安装 Tailscale
   - 登录并连接，记录分配到的 Tailscale IP（如 `100.x.x.x`）

2. **各设备安装 Tailscale 客户端**
   - Windows / macOS / iOS / Android 均支持
   - 用同一账号登录，自动加入同一私人网络

3. **获取 NAS 的 Tailscale IP**
   - 在 NAS 的 Tailscale 控制台查看分配的 IP

4. **修改 Remotely Save 配置**
   - 将 WebDAV URL 改为：`http://<Tailscale IP>:3000/dav/`
   - 例如：`http://100.123.45.67:3000/dav/`

5. **验证外网同步**
   - 断开内网 Wi-Fi，使用手机流量
   - 点击 Sync Now，检查是否正常同步

> **截图示意**：
> - 图11：Tailscale 设备列表界面
> - 图12：Remotely Save 中填入 Tailscale IP

---

## 六、总结推荐

| 场景 | 推荐方案 |
|------|---------|
| 纯内网多设备同步 | WebDAV + Remotely Save |
| 需要外网访问 | Tailscale + WebDAV |
| 技术背景强、需版本控制 | Git + Obsidian Git |
| 完全不想折腾 | Obsidian Sync 官方付费版 |

**最优方案**：`WebDAV（飞牛 NAS）+ Remotely Save 插件`

- 完全私有，无第三方依赖
- 配置简单，5 分钟可搞定
- 支持全平台（Win/Mac/Linux/iOS/Android）
- 免费，成本为零

---

## 七、参考来源

1. [Remotely Save 插件官方文档](https://github.com/remotely-save/remotely-save)
2. [Obsidian 官方同步方案介绍](https://obsidian.md/sync)
3. [飞牛 NAS WebDAV 官方帮助](https://www.fnnas.com/help/webdav)
4. [Tailscale 官方文档 - Headscale](https://tailscale.com/)
5. [Obsidian Git 插件](https://github.com/denolehov/obsidian-git)
6. [WebDAV 协议说明 - MDN](https://developer.mozilla.org/en-US/docs/WebDAV)
7. [Syncthing 官方文档](https://docs.syncthing.net/)

---

## 八、常见问题

**Q1：同步时提示 401 未授权？**
> 检查用户名密码是否正确，WebDAV URL 格式是否正确，注意末尾斜杠 `/`。

**Q2：同步后图片显示不出来？**
> 确认附件使用相对路径存储，如 `![[image.png]]`，避免使用绝对路径。

**Q3：冲突文件怎么合并？**
> Remotely Save 会在冲突文件名后加时间戳，如 `conflict-笔记名-202605012030.md`，手动打开对比合并即可。

**Q4：能否多个设备同时编辑？**
> WebDAV 无自动锁，建议使用前先 Sync，编辑完成后及时 Sync，避免多人同时改同一笔记。

**Q5：移动端同步很慢怎么办？**
> 首次同步建议在 Wi-Fi 环境下；检查 NAS 和手机的互联网延迟；可考虑仅同步部分笔记而非完整保险库。