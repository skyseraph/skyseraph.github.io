---
title: "SkillNexus #07 · 技术架构：Electron 双进程 + 零依赖进化 SDK"
slug: 07-architecture
series: "SkillNexus"
issue: 7
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "双进程安全隔离 + 接口注入解耦，进化引擎可独立运行"
description: "SkillNexus 采用 Electron 双进程模型，7 条 IPC 安全不变量保护 API Key，进化 SDK 通过接口注入与 Electron 完全解耦，可在 CLI 和 CI/CD 中独立运行。"
---

> Skills 全生命周期创造平台，让你的 Skill 可生成、可量化、可管理、可成长。

**SkillNexus 系列导航**（共 10 篇）

| #        | 文章                                                |
| -------- | ------------------------------------------------- |
| 01       | [你的 Skill 目录，正在变成屎山](/series/skill-nexus/2026/01-why-skill-nexus)       |
| 02       | [5 分钟完成第一次 Skill 评测](/series/skill-nexus/2026/02-quickstart)            |
| 03       | [从一行描述到可用 Skill——Studio 的 5 种创作模式](/series/skill-nexus/2026/03-studio)  |
| 04       | [8 维度评测框架：让"感觉还行"变成数据](/series/skill-nexus/2026/04-eval)                |
| 05       | [进化引擎：让 Skill 自动变好](/series/skill-nexus/2026/05-evo)                    |
| 06       | [Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)       |
| **→ 07** | **技术架构：Electron 双进程 + 零依赖进化 SDK**（本篇）             |
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)           |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)       |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization) |

***

这篇聊技术。SkillNexus 的架构有几个决策值得单独说清楚，因为它们不只是实现细节，而是影响整个产品边界的设计选择。

***

## Electron 双进程模型

SkillNexus 是标准的 Electron 应用，主进程（Main）和渲染进程（Renderer）严格隔离。

```
┌─────────────────────────────────────────────────────┐
│  Renderer Process（React 18 + TypeScript）           │
│  UI 渲染、用户交互、流式输出展示                        │
│  contextBridge 暴露的 API 是唯一出口                   │
└──────────────────┬──────────────────────────────────┘
                   │ IPC（contextBridge）
┌──────────────────▼──────────────────────────────────┐
│  Main Process（Node.js）                             │
│  文件系统访问、AI SDK 调用、SQLite 读写、API Key 管理   │
└─────────────────────────────────────────────────────┘
```

**渲染进程永远拿不到 API Key**——Key 只在主进程内存中存在，渲染进程通过 IPC 发起 AI 调用请求，主进程执行后返回结果。这和很多"AI 工具"直接在前端 localStorage 存 Key 的做法有根本差异。

***

## 7 条 IPC 安全不变量

IPC 层是 Electron 应用最容易出安全问题的地方。SkillNexus 定义了 **7 条不变量，违反任一规则阻止代码合并**：

| 规则     | 要求                                               |
| ------ | ------------------------------------------------ |
| SEC-R1 | 文件路径经 `assertPathAllowed()` 白名单校验                |
| SEC-R2 | name 参数写文件前 `basename + sanitize`，验证目标在安全目录内     |
| SEC-R3 | `config:get` 返回 `AppConfigPublic`，永不暴露 apiKey 明文 |
| SEC-R4 | `shell.openExternal` 只接受 `https?://` 协议          |
| SEC-R5 | 所有 AI 调用包裹 30s 超时，防止 UI 永久挂起                     |
| SEC-R6 | `testCaseIds` 数组长度 ≤ 50，防止批量滥用                   |
| SEC-R7 | `skills:readFile` 验证文件在该 Skill 的 rootDir 内       |

这些规则对应了专门的安全测试套件（`tests/security/`），每次 CI 都会跑。

***

## 零依赖进化 SDK

**这是架构层面最重要的决策，也是最容易被忽视的亮点。**

进化引擎完全通过接口注入与 Electron 解耦：

```typescript
// 核心三接口，无任何 Electron 依赖
interface IDataStore {
  getEvalHistory(skillId: string): EvalRecord[]
  saveSkillVersion(skill: Skill): void
}

interface ISkillStorage {
  readSkill(path: string): string
  writeSkill(path: string, content: string): void
}

interface IProgressReporter {
  report(step: string, progress: number): void
}

class BaseEvolutionEngine {
  constructor(
    protected dataStore: IDataStore,
    protected skillStorage: ISkillStorage,
    protected reporter: IProgressReporter,
  ) {}
}
```

**为什么这很重要？**

1. **进化引擎可以独立运行**：CLI、Node.js 脚本、CI/CD 管道，不需要启动 Electron，不需要 GUI
2. **可测试性**：对 SDK 的单元测试不需要模拟 Electron，mock 三个接口即可，测试速度快、稳定性高
3. **可扩展性**：社区可以开发第三方进化算法，只需实现接口，不需要了解 Electron 内部

***

## 数据层设计

**业务数据**：better-sqlite3，存储 Skill 元数据、评测历史、进化记录、测试用例。

选 SQLite 而不是文件 JSON 的原因：

* 评测历史是时序数据，需要**聚合查询**（Trending 榜单就是 SQL 聚合）
* **事务完整性**：进化过程中途中断不会产生脏数据
* **零网络延迟**：本地文件，查询速度可预期

**配置数据**：electron-store（加密），存储 LLM Provider 配置。**API Key 不写 SQLite，单独存储，加密静态存储。**

***

## 流式输出架构

Studio 生成和 Eval 评测都是流式的——AI 输出一个 token，UI 立刻显示一个 token。

实现方式：主进程通过 `webContents.send()` 把流式 token 推送到渲染进程，渲染进程用 React state 累积显示。

```typescript
// 主进程
for await (const chunk of stream) {
  event.sender.send('stream:chunk', chunk.delta.text)
}
event.sender.send('stream:done')

// 渲染进程
window.api.on('stream:chunk', (text) => {
  setOutput(prev => prev + text)
})
```

**这个模式让"等待 AI 响应"变成"看着 AI 思考"，体验差异很大。**

***

## Plugin 热加载

自定义进化算法放入 `{userData}/plugins/*.js`，主进程启动时扫描加载：

```javascript
// 扫描插件目录
const plugins = fs.readdirSync(pluginsDir)
  .filter(f => f.endsWith('.js'))
  .map(f => require(path.join(pluginsDir, f)))
```

**无需修改源码，无需重新构建，放文件即生效。**

***

## 技术栈一览

| 层      | 选择                              | 理由                               |
| ------ | ------------------------------- | -------------------------------- |
| 桌面框架   | Electron 31 + electron-vite 2.3 | 跨平台、原生文件访问、IPC 安全隔离              |
| 前端     | React 18 + TypeScript 5.5       | 流式渲染、类型安全                        |
| 业务存储   | better-sqlite3 11               | 零网络延迟、事务完整性、聚合查询                 |
| 配置存储   | electron-store 8（加密）            | API Key 安全、跨重启持久                 |
| AI SDK | @anthropic-ai/sdk 0.39          | 流式输出；via baseURL 兼容 13+ Provider |
| 测试     | Vitest 2（653 tests，37 suites）   | 纯逻辑层快速测试，无 Electron 依赖           |

***

## 下一步

最后一篇，聊聊 SkillNexus 的现状和路线图——它现在能做什么，接下来要做什么。

下一篇：[08 · 现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
