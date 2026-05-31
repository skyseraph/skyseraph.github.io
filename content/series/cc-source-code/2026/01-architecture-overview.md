---
title: "CC源码剖析 #01 · 整体架构概览：目录结构与模块划分"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 2
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、项目背景

Claude Code 源码于 2026 年 3 月 31 日通过 npm 包中的 `.map` 文件意外暴露，指向 Anthropic R2 存储桶中未经混淆的 TypeScript 源码。此镜像仅用于**教育、安全研究和软件供应链分析**。

- **语言**：TypeScript（strict 模式）
- **运行时**：Bun
- **终端 UI**：React + [Ink](https://github.com/vadimdemedes/ink)
- **规模**：约 1,900 个文件，512,000+ 行代码

---

## 二、顶层目录结构

```
C:\dev\claude\claude-code\
├── src/                    # 全部业务逻辑
├── .vscode/                # VSCode 调试配置
├── README.md               # 研究背景文档（非官方）
└── package.json
```

---

## 三、`src/` 模块全景图

### 3.1 核心运行模块

| 目录 | 文件数(估) | 核心职责 |
| :--- | :--- | :--- |
| `tools/` | ~40 | Tool 定义、注册、执行（FileEdit/Bash/Grep 等） |
| `commands/` | ~50 | Slash Commands 实现（/commit /review /diff 等） |
| `coordinator/` | - | 多 Agent 任务编排与协调 |
| `assistant/` | - | 会话历史、Session 管理 |
| `buddy/` | - | Companion 对话伙伴（sprite/prompt） |

### 3.2 通信层

| 目录 | 核心职责 |
| :--- | :--- |
| `bridge/` | **最重要**：IDE（VSCode/JetBrains）与 CLI 之间的双向通信 |
| `remote/` | 远程会话管理 |
| `server/` | 服务端模式 |

### 3.3 任务与状态

| 目录 | 核心职责 |
| :--- | :--- |
| `tasks/` | Task 的创建、执行、状态追踪 |
| `state/` | 状态管理 |
| `memdir/` | 内存目录与会话持久化（~Memory 功能核心） |
| `skills/` | Skill 加载与执行系统 |

### 3.4 UI 与交互

| 目录 | 核心职责 |
| :--- | :--- |
| `ink/` | Ink（React for CLI）渲染封装 |
| `components/` | ~140 个 Ink UI 组件 |
| `screens/` | 全屏 UI（Doctor/REPL/Resume） |
| `entrypoints/` | 各端点初始化（CLI/VSCode/Remote） |

### 3.5 生态扩展

| 目录 | 核心职责 |
| :--- | :--- |
| `plugins/` | 插件系统 |
| `mcp/` | Model Context Protocol 服务连接 |
| `services/` | API/OAuth/LSP/Analytics 等外部集成 |

### 3.6 其他

| 目录 | 说明 |
| :--- | :--- |
| `hooks/` | React 生命周期钩子 |
| `types/` | 核心 TypeScript 类型定义 |
| `schemas/` | Zod 配置模式验证 |
| `migrations/` | 配置迁移 |
| `keybindings/` | 快捷键配置 |
| `vim/` | Vim 模式支持 |
| `voice/` | 语音输入 |
| `upstreamproxy/` | 代理配置 |
| `native-ts/` | 原生 TS 工具函数 |
| `outputStyles/` | 输出样式 |
| `bootstrap/` | 启动初始化 |

---

## 四、最关键模块详解

### 4.1 `tools/` — 工具系统（Agent 的"手"）

Claude Code 的 Agent 通过 Tool 与外界交互。每个 Tool 都是一个自包含模块：

| Tool | 功能 |
| :--- | :--- |
| `BashTool` | Shell 命令执行 |
| `FileReadTool` | 文件读取（含图片/PDF/Notebook） |
| `FileWriteTool` | 文件创建/覆盖 |
| `FileEditTool` | **最常用**：字符串替换编辑 |
| `GlobTool` | 文件模式匹配搜索 |
| `GrepTool` | 基于 ripgrep 的内容搜索 |
| `WebFetchTool` | URL 内容获取 |
| `WebSearchTool` | 网络搜索 |
| `AgentTool` | 子 Agent 派生 |
| `SkillTool` | Skill 执行 |
| `MCPTool` | MCP 服务器工具调用 |
| `TaskCreateTool` / `TaskUpdateTool` | 任务创建管理 |
| `TeamCreateTool` / `TeamDeleteTool` | 团队 Agent 管理 |
| `EnterPlanModeTool` / `ExitPlanModeTool` | 计划模式切换 |
| `EnterWorktreeTool` / `ExitWorktreeTool` | Git Worktree 隔离 |
| `CronCreateTool` | 定时任务创建 |

每个 Tool 定义：
- 输入 Schema（Zod 验证）
- 权限模型（Permission Model）
- 执行逻辑

### 4.2 `bridge/` — 进程间通信（最复杂模块）

Claude Code 可作为 VSCode/JetBrains 插件使用，Bridge 是 IDE 扩展与 CLI 之间的双向通信层。

核心文件：

| 文件 | 作用 |
| :--- | :--- |
| `bridgeMain.ts` | Bridge 主循环 |
| `bridgeMessaging.ts` | 消息协议定义 |
| `bridgePermissionCallbacks.ts` | 权限回调处理 |
| `replBridge.ts` | REPL 会话桥接 |
| `jwtUtils.ts` | JWT 认证 |
| `sessionRunner.ts` | 会话执行管理 |
| `remoteBridgeCore.ts` | 远程桥接核心 |
| `initReplBridge.ts` | REPL 桥接初始化 |

通信模式：双向 IPC，支持消息队列、心跳检测、JWT 鉴权。

### 4.3 `coordinator/` — 多 Agent 编排

处理多 Agent 协作场景：
- Sub-agent 的派生与管理
- 团队级并行工作（`TeamCreateTool`）
- 任务协调与结果聚合

### 4.4 `services/` — 外部集成

| 服务 | 说明 |
| :--- | :--- |
| `api/` | Anthropic API 客户端、文件上传、bootstrap |
| `mcp/` | MCP 服务器连接与管理 |
| `oauth/` | OAuth 2.0 认证 |
| `lsp/` | Language Server Protocol 管理器 |
| `analytics/` | GrowthBook 特性开关与数据分析 |
| `compact/` | 对话上下文压缩 |
| `tokenEstimation.ts` | Token 数量估算 |

### 4.5 `entrypoints/` — 各端点入口

Claude Code 支持多种启动方式：

- **CLI 模式**：终端直接运行
- **VSCode 扩展**：集成到 VSCode
- **JetBrains 扩展**
- **Remote 模式**：远程连接

每个端点有独立的初始化逻辑。

---

## 五、核心文件 TOP 5

| 文件 | 估算行数 | 重要性 | 说明 |
| :--- | :--- | :--- | :--- |
| `QueryEngine.ts` | ~46K | ⭐⭐⭐⭐⭐ | LLM API 调用核心，处理流式响应、Tool Call 循环、重试逻辑、Token 计数 |
| `Tool.ts` | ~29K | ⭐⭐⭐⭐⭐ | 所有 Tool 的基类定义、Schema、权限模型、进度状态类型 |
| `commands.ts` | ~25K | ⭐⭐⭐⭐ | Slash Command 注册与执行管理（~50 个命令） |
| `main.tsx` | - | ⭐⭐⭐⭐ | Commander.js CLI 解析 + React/Ink 渲染初始化，含并行预加载优化 |
| `context.ts` | - | ⭐⭐⭐⭐ | 系统上下文收集（文件内容、Git 状态等） |

---

## 六、关键技术栈

| 类别 | 技术 |
| :--- | :--- |
| 运行时 | Bun |
| 语言 | TypeScript strict |
| CLI 解析 | Commander.js |
| 终端 UI | React + Ink |
| Schema 验证 | Zod v4 |
| 代码搜索 | ripgrep |
| 协议 | MCP SDK, LSP |
| API | Anthropic SDK |
| 遥测 | OpenTelemetry + gRPC |
| 特性开关 | GrowthBook |
| 认证 | OAuth 2.0, JWT, macOS Keychain |

---

## 七、启动流程（简化版）

```
main.tsx（入口）
  ├── Commander.js CLI 解析
  ├── 并行预加载（MDM配置/Keychain/API预连接）
  ├── GrowthBook 初始化
  └── Ink React 渲染
       ├── commands.ts 注册 Slash Commands
       ├── tools.ts 注册 Tool
       ├── QueryEngine 初始化
       └── 等待用户输入 → 进入 Tool Call 循环
```

---

## 八、Feature Flags（编译时裁剪）

Claude Code 使用 Bun 的 `bun:bundle` 特性标志在编译时裁剪未激活代码：

```typescript
import { feature } from 'bun:bundle'

const voiceCommand = feature('VOICE_MODE')
  ? require('./commands/voice/index.js').default
  : null
```

主要标志：`PROACTIVE`, `KAIROS`, `BRIDGE_MODE`, `DAEMON`, `VOICE_MODE`, `AGENT_TRIGGERS`, `MONITOR_TOOL`

---

## 九、模块依赖关系（简化视图）

```
main.tsx
├── commands.ts
├── tools.ts
├── QueryEngine.ts
│   └── context.ts
├── coordinator/
├── bridge/  ←→ IDE Extensions（VSCode/JetBrains）
├── services/
│   ├── api/
│   ├── mcp/
│   └── lsp/
└── entrypoints/
```

---

## 下一步

下一篇：[02 - 入口点解析：从 CLI 到 REPL](https://skyseraph.github.io/series/cc-source-code/2026/02-entrypoint-repl)，深入 `main.tsx`、`commands.ts` 与 REPL 初始化流程。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*