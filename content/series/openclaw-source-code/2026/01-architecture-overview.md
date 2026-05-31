---
title: "OpenClaw源码剖析 #01 · 整体架构概览：目录结构与模块划分"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 2
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、项目定位

OpenClaw 是一个**个人 AI 助手平台**，运行在用户自有设备上，通过用户已有的消息渠道进行交互。

```
用户 ──► OpenClaw ──► 30+ 消息渠道
       │              (Telegram/Discord/WhatsApp...)
       │
       ▼
    模型提供商
  (OpenAI/Anthropic/Google...)
```

**核心特性**：
- 个人化、单用户、本地优先
- 多渠道接入（30+ 消息平台）
- 多模型支持（40+ 厂商）
- 可扩展插件系统
- 支持语音和 Canvas

---

## 二、顶层目录结构

```
openclaw/
├── src/                    # 核心业务逻辑
├── extensions/             # 扩展：Provider/Channel/Skill (~100 个)
├── packages/               # 独立 npm 包
├── apps/                   # 应用程序
├── ui/                      # UI 组件
├── test/                    # E2E 测试
├── docs/                    # 文档
├── scripts/                 # 构建/工具脚本
├── skills/                  # 内置 Skills
├── security/                # 安全相关
├── vendor/                  # 第三方依赖
└── [配置文件]
```

---

## 三、核心模块（src/）

### 3.1 Agent 系统

| 目录 | 职责 |
|:---|:---|
| `src/agents/` | Agent 定义、运行时、prompt 管理 |
| `src/agent-sdk/` | Agent SDK |
| `src/agents/` | Agent 相关类型 |

### 3.2 控制平面

| 目录 | 职责 |
|:---|:---|
| `src/gateway/` | **Gateway 控制平面**：API、路由、协议 |
| `src/gateway/protocol/` | 协议定义 |
| `src/api/` | API 相关 |

### 3.3 插件系统

| 目录 | 职责 |
|:---|:---|
| `src/plugins/` | 插件加载、激活、生命周期管理 |
| `src/plugin-sdk/` | **Plugin SDK**（公开 API，供扩展使用） |
| `src/plugin-state/` | 插件状态管理 |
| `src/plugin-activation-boundary.ts` | 插件激活边界 |

### 3.4 渠道抽象

| 目录 | 职责 |
|:---|:---|
| `src/channels/` | **渠道抽象层** |
| `src/channels/session.ts` | 渠道会话 |

### 3.5 上下文与记忆

| 目录 | 职责 |
|:---|:---|
| `src/context-engine/` | **上下文引擎** |
| `src/memory/` | 记忆系统 |
| `src/memory-host-sdk/` | 记忆 Host SDK |

### 3.6 会话与任务

| 目录 | 职责 |
|:---|:---|
| `src/sessions/` | 会话管理 |
| `src/tasks/` | 任务系统 |
| `src/trajectory/` | 轨迹记录 |

### 3.7 配置与安全

| 目录 | 职责 |
|:---|:---|
| `src/config/` | 配置管理 |
| `src/secrets/` | 密钥管理 |
| `src/security/` | 安全机制 |
| `src/auth/` | 认证授权 |

### 3.8 运行时能力

| 目录 | 职责 |
|:---|:---|
| `src/hooks/` | Hook 系统 |
| `src/flows/` | Flow 工作流 |
| `src/commands/` | 命令系统 |
| `src/tui/` | TUI 界面 |

### 3.9 媒体与生成

| 目录 | 职责 |
|:---|:---|
| `src/media/` | 媒体处理 |
| `src/media-generation/` | 媒体生成 |
| `src/media-understanding/` | 媒体理解 |
| `src/image-generation/` | 图片生成 |
| `src/video-generation/` | 视频生成 |
| `src/music-generation/` | 音乐生成 |
| `src/tts/` | 文本转语音 |
| `src/realtime-voice/` | 实时语音 |
| `src/realtime-transcription/` | 实时转录 |

### 3.10 其他支持模块

| 目录 | 职责 |
|:---|:---|
| `src/i18n/` | 国际化 |
| `src/mcp/` | MCP 协议 |
| `src/bootstrap/` | 启动初始化 |
| `src/daemon/` | 后台守护进程 |
| `src/logger/` | 日志 |
| `src/logging/` | 日志系统 |
| `src/crone/` | 定时任务 |
| `src/poll-params.ts` | 轮询参数 |
| `src/polls.ts` | 轮询系统 |

---

## 四、扩展系统（extensions/）

### 4.1 Provider（模型提供商）

| Provider | 说明 |
|:---|:---|
| `anthropic/` | Anthropic API（Claude） |
| `openai/` | OpenAI API（GPT） |
| `ollama/` | Ollama（本地模型） |
| `google/` | Google AI |
| `azure/` | Azure OpenAI |
| `amazon-bedrock/` | AWS Bedrock |
| `deepseek/` | DeepSeek |
| `mistral/` | Mistral AI |
| `groq/` | Groq |
| `openrouter/` | OpenRouter |
| `together/` | Together AI |
| `xai/` | xAI |
| `nvidia/` | NVIDIA NIM |
| `cerebras/` | Cerebras |
| ` Voyage/` | Voyage AI |
| `fireworks/` | Fireworks AI |
| `deepinfra/` | DeepInfra |
| `vllm/` | vLLM |
| `sglang/` | SGLang |
| `lmstudio/` | LM Studio |
| `kimi-coding/` | Kimi Coding |
| `moonshot/` | Moonshot |
| `qwen/` | Qwen |
| `wenxin/` | 百度文心 |
| `minimax/` | MiniMax |
| `volcengine/` | 火山引擎 |
| `baichuan/` | 百川 |
| `tencent/` | 腾讯混元 |
| `zalo/` | Zalo |

### 4.2 Channel（消息渠道）

| Channel | 说明 |
|:---|:---|
| `telegram/` | Telegram |
| `discord/` | Discord |
| `whatsapp/` | WhatsApp |
| `slack/` | Slack |
| `microsoft/` | Microsoft Teams |
| `googlechat/` | Google Chat |
| `msteams/` | Microsoft Teams（原生） |
| `matrix/` | Matrix |
| `irc/` | IRC |
| `signal/` | Signal |
| `feishu/` | 飞书 |
| `line/` | LINE |
| `mattermost/` | Mattermost |
| `nextcloud-talk/` | Nextcloud Talk |
| `synology-chat/` | 群晖 Chat |
| `tlon/` | Tlon |
| `nostr/` | Nostr |
| `twitch/` | Twitch |
| `bluebubbles/` | BlueBubbles（iMessage） |
| `imessage/` | iMessage |

### 4.3 Skill（技能）

| Skill | 说明 |
|:---|:---|
| `skill-workshop/` | 技能工作流 |

### 4.4 Tool（工具能力）

| Tool | 说明 |
|:---|:---|
| `memory-core/` | 记忆核心 |
| `memory-lancedb/` | LanceDB 记忆存储 |
| `memory-wiki/` | Wiki 记忆 |
| `image-generation-core/` | 图片生成核心 |
| `video-generation-core/` | 视频生成核心 |
| `media-understanding-core/` | 媒体理解核心 |
| `speech-core/` | 语音核心 |

---

## 五、架构设计原则

> 来自 `AGENTS.md`

### 5.1 核心保持扩展无关

```
Core stays extension-agnostic.
No bundled ids in core when manifest/registry/capability contracts work.
```

核心代码不硬编码任何扩展 ID，通过 manifest/registry/capability 契约交互。

### 5.2 扩展通过 SDK 进入核心

```
Extensions cross into core only via openclaw/plugin-sdk/*,
manifest metadata, injected runtime helpers,
documented barrels (api.ts, runtime-api.ts).
```

扩展只能通过：
- `openclaw/plugin-sdk/*`（SDK 接口）
- manifest 元数据
- 注入的运行时助手
- 文档化的 barrel 导出

### 5.3 边界约束

```
Extension prod code: no core src/**, src/plugin-sdk-internal/**,
other extension src/**, or relative outside package.
```

扩展生产代码禁止：
- 引用 `src/**`（核心）
- 引用 `src/plugin-sdk-internal/**`
- 引用其他扩展的 `src/**`
- 引用包外的相对路径

### 5.4 渠道抽象

```
Channels: src/channels/** is implementation;
plugin authors get SDK seams.
```

渠道实现在 `src/channels/`，插件作者使用 SDK 接口。

### 5.5 接口版本管理

```
New seams: backwards-compatible, documented, versioned.
Third-party plugins exist.
```

所有新接口必须：
- 向后兼容
- 已文档化
- 有版本控制

---

## 六、启动流程（简化）

```
main.ts / openclaw.mjs
  │
  ├─► entry.ts（入口）
  │     ├─► 版本检查
  │     ├─► 配置加载
  │     ├─► 插件扫描
  │     └─► Gateway 启动
  │
  ├─► gateway/（控制平面）
  │     ├─► API Server
  │     ├─► WebSocket Server
  │     └─► Plugin Manager
  │
  └─► channels/（渠道）
        └─► 消息监听
```

---

## 七、关键文件

| 文件 | 职责 |
|:---|:---|
| `src/index.ts` | 主入口，导出核心 API |
| `src/entry.ts` | 启动入口，处理 respawn |
| `src/runtime.ts` | 运行时初始化 |
| `src/library.ts` | 库模式入口 |
| `src/gateway/index.ts` | Gateway 主入口 |
| `src/plugins/index.ts` | 插件系统入口 |
| `src/agents/index.ts` | Agent 系统入口 |

---

## 八、与其他项目的架构对比

| 特性 | Claude Code | OpenClaw |
|:---|:---|:---|
| 语言 | TypeScript（Bun） | TypeScript（Node 22+） |
| 插件系统 | 内置命令 | Extension 插件 |
| 渠道接入 | 无 | 30+ 渠道 |
| 模型支持 | Anthropic | 40+ 厂商 |
| 部署模式 | 本地 CLI | Gateway 服务 |
| UI | React + Ink（终端） | Canvas + TUI |

---

## 下一步

下一篇：[02 - Gateway 控制平面：API 路由与协议](./02-gateway-arch.md)，深入 Gateway 模块的 API 路由、插件管理和协议实现。

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*