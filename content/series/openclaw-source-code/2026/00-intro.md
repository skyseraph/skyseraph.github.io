---
title: "OpenClaw源码剖析 #00 · 开篇"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 1
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

> 从源码层面深入理解 OpenClaw 的设计思想与实现细节。

---

## 系列介绍

OpenClaw 是一个面向 AI Agent 的开发框架，本系列从源码出发，拆解其核心模块的设计理念与实现机制。

适合对象：对 Agent 架构、工具调用链、任务规划感兴趣，想深入理解 OpenClaw 内部原理的开发者。

---

**核心参考资料**：
- 分析方法论：[ANALYSIS_APPROACH.md](./ANALYSIS_APPROACH.md)
- 官方文档：https://docs.openclaw.ai
- DeepWiki：https://deepwiki.com/openclaw/openclaw

---

## 目录规划

### Part 1：架构层

| # | 文章 | 状态 | 说明 |
|:---|:---|:---|:---|
| 01 | [整体架构概览：目录结构与模块划分](https://skyseraph.github.io/series/openclaw-source-code/2026/01-architecture-overview) | ✅ 完成 | src/ 核心目录 + extensions/ |
| 02 | [Gateway 控制平面：API 路由与协议](https://skyseraph.github.io/series/openclaw-source-code/2026/02-gateway-arch) | ✅ 完成 | Gateway 控制平面 |
| 03 | [Plugin SDK：扩展机制与公开 API](https://skyseraph.github.io/series/openclaw-source-code/2026/03-plugin-sdk) | ✅ 完成 | 插件 SDK 架构 |
| 04 | [Agent Runtime：任务编排与执行](https://skyseraph.github.io/series/openclaw-source-code/2026/04-agent-runtime) | ✅ 完成 | Agent 运行时 |

### Part 2：核心机制

| # | 文章 | 状态 | 说明 |
|:---|:---|:---|:---|
| 05 | [Provider 系统：多模型统一接口](https://skyseraph.github.io/series/openclaw-source-code/2026/05-provider-system) | ✅ 完成 | 40+ 模型厂商抽象 |
| 06 | [Channel 系统：多渠道消息接入](https://skyseraph.github.io/series/openclaw-source-code/2026/06-channel-system) | ✅ 完成 | 消息渠道抽象 |
| 07 | [会话与状态管理](https://skyseraph.github.io/series/openclaw-source-code/2026/07-session-state) | ✅ 完成 | 会话生命周期 |
| 08 | [记忆系统：Memory Architecture](https://skyseraph.github.io/series/openclaw-source-code/2026/08-memory-system) | ✅ 完成 | 长期记忆 |

### Part 3：扩展系统

| # | 文章 | 状态 | 说明 |
|:---|:---|:---|:---|
| 09 | [Extension 开发：Provider 篇](https://skyseraph.github.io/series/openclaw-source-code/2026/09-extension-provider) | ✅ 完成 | 开发新模型 Provider |
| 10 | [Extension 开发：Channel 篇](https://skyseraph.github.io/series/openclaw-source-code/2026/10-extension-channel) | ✅ 完成 | 开发新消息渠道 |
| 11 | [Extension 开发：Skill 篇](https://skyseraph.github.io/series/openclaw-source-code/2026/11-extension-skill) | ✅ 完成 | 开发新 Skill |

### Part 4：工程实践

| # | 文章 | 状态 | 说明 |
|:---|:---|:---|:---|
| 12 | [测试策略：单元/集成/E2E](https://skyseraph.github.io/series/openclaw-source-code/2026/12-testing-strategy) | ✅ 完成 | Vitest + E2E |
| 13 | [配置系统：Schema 与验证](https://skyseraph.github.io/series/openclaw-source-code/2026/13-config-system) | ✅ 完成 | 配置管理 |
| 14 | [安全机制：Auth 与权限](https://skyseraph.github.io/series/openclaw-source-code/2026/14-security-auth) | ✅ 完成 | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](https://skyseraph.github.io/series/openclaw-source-code/2026/15-deployment-docker) | ✅ 完成 | 生产部署 |

---

## 模块速查

### 核心模块（src/）

| 目录 | 功能 |
|:---|:---|
| `src/agents/` | Agent 定义、运行时、prompt 管理 |
| `src/plugins/` | 插件加载、激活、生命周期 |
| `src/gateway/` | 控制平面 API、路由、协议 |
| `src/channels/` | 渠道抽象层 |
| `src/plugin-sdk/` | 插件 SDK（公开 API） |
| `src/context-engine/` | 上下文管理 |
| `src/memory/` | 记忆系统 |
| `src/config/` | 配置管理 |
| `src/sessions/` | 会话管理 |
| `src/tasks/` | 任务系统 |

### 扩展（extensions/）

| 类型 | 数量 | 示例 |
|:---|:---|:---|
| Provider | ~40 | `openai/`, `anthropic/`, `ollama/` |
| Channel | ~30 | `telegram/`, `discord/`, `whatsapp/` |
| Skill | ~5 | `skill-workshop/` |
| Tool | ~10 | `memory-core/`, `image-generation-core/` |

---

## 源码结构概览

```
C:\dev\claude\openclaw\
├── src/
│   ├── agents/           # Agent 运行时
│   ├── gateway/          # 控制平面
│   ├── plugins/         # 插件系统
│   ├── plugin-sdk/       # SDK 公开 API
│   ├── channels/         # 渠道抽象
│   ├── context-engine/   # 上下文
│   ├── memory/           # 记忆
│   ├── sessions/         # 会话
│   ├── config/          # 配置
│   └── ...
├── extensions/
│   ├── providers/        # 模型提供商
│   │   ├── openai/
│   │   ├── anthropic/
│   │   └── ollama/
│   ├── channels/          # 消息渠道
│   │   ├── telegram/
│   │   ├── discord/
│   │   └── whatsapp/
│   └── skills/           # 技能
├── packages/              # 独立包
├── apps/                 # 应用程序
└── ui/                    # UI 组件
```

---

## 关键设计原则

> 来自 `AGENTS.md`

1. **Core stays extension-agnostic** — 核心保持扩展无关，不在核心中硬编码扩展 ID
2. **Extensions cross into core only via SDK** — 扩展只能通过 `openclaw/plugin-sdk/*` 和 manifest 元数据进入核心
3. **Extension prod code: no core src/** — 扩展生产代码禁止引用核心 `src/` 目录
4. **Core/test: no deep plugin internals** — 核心/测试代码禁止引用插件内部实现
5. **New seams: backwards-compatible** — 新接口必须向后兼容、已文档化、有版本控制
6. **Channels: src/channels/** is implementation** — 渠道实现在 `src/channels/`，插件作者使用 SDK 接口

---

*OpenClaw源码剖析 · 2026 · skyseraph*