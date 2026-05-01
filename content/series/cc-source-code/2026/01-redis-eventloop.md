---
title: "CC源码剖析 #01 · 开篇"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 1
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: true
---

> 深入剖析开源项目核心源码，拆解架构设计与实现细节。

---

## 系列导航

本系列从架构、关键模块到代码实现，深入剖析 Claude Code 的设计思想与实现细节。

---

## 目录规划

### Part 1：架构层

| #    | 文章 | 状态 | 说明 |
| :--- | :--- | :--- | :--- |
| 01   | [整体架构概览：目录结构与模块划分](./01-architecture-overview.md) | 🔨 进行中 |  |
| 02   | [入口点解析：从 CLI 到 REPL](./02-entrypoint-repl.md) | 📝 规划中 |  |
| 03   | [Bridge 模块：主进程与渲染进程的通信机制](./03-bridge-arch.md) | 📝 规划中 |  |
| 04   | [Coordinator：多阶段任务编排器](./04-coordinator.md) | 📝 规划中 |  |

### Part 2：核心模块

| #    | 文章 | 状态 | 说明 |
| :--- | :--- | :--- | :--- |
| 05   | [Tools 系统：工具定义、注册与执行](./05-tools-system.md) | 📝 规划中 |  |
| 06   | [Skills 加载与执行机制](./06-skills-system.md) | 📝 规划中 |  |
| 07   | [MCP 协议：多工具协调](./07-mcp-protocol.md) | 📝 规划中 |  |
| 08   | [消息传递：inbound/outbound 架构](./08-messaging.md) | 📝 规划中 |  |

### Part 3：高级特性

| #    | 文章 | 状态 | 说明 |
| :--- | :--- | :--- | :--- |
| 09   | [权限系统：PermissionCallbacks 与安全边界](./09-permission-system.md) | 📝 规划中 |  |
| 10   | [状态管理：memdir 与会话持久化](./10-memdir-state.md) | 📝 规划中 |  |
| 11   | [插件系统：Plugin 架构与生命周期](./11-plugin-system.md) | 📝 规划中 |  |
| 12   | [跨进程通信：RemoteBridge 与远程模式](./12-remote-bridge.md) | 📝 规划中 |  |

### Part 4：代码深度

| #    | 文章 | 状态 | 说明 |
| :--- | :--- | :--- | :--- |
| 13   | [Task 执行引擎：从创建到完成的完整流程](./13-task-engine.md) | 📝 规划中 |  |
| 14   | [Hook 系统：生命周期拦截点](./14-hooks.md) | 📝 规划中 |  |
| 15   | [安全审查：Security Review 命令实现](./15-security-review.md) | 📝 规划中 |  |

---

## 模块速查

| 目录 | 功能 |
| :--- | :--- |
| `src/assistant` | Assistant 会话管理 |
| `src/bridge` | 主进程 ↔ Claude 进程通信层 |
| `src/buddy` | Buddy/Companion 对话伙伴 |
| `src/cli` | 命令行入口 |
| `src/coordinator` | 任务协调编排器 |
| `src/entrypoints` | 各端点入口（VSCode、CLI、Remote） |
| `src/hooks` | 生命周期钩子 |
| `src/ink` | Ink 命令行 UI 渲染 |
| `src/memdir` | 内存目录与会话状态 |
| `src/plugins` | 插件系统 |
| `src/skills` | Skill 加载与执行 |
| `src/state` | 状态管理 |
| `src/tasks` | Task 创建与执行 |
| `src/tools` | 工具定义与注册 |
| `src/types` | 核心类型定义 |

---

## 源码结构概览

```
claude-code
├── src/
│   ├── assistant/      # 会话历史与状态
│   ├── bootstrap/      # 启动初始化
│   ├── bridge/        # IPC 通信（最重要）
│   ├── buddy/         # 对话伙伴模块
│   ├── cli/           # CLI 入口
│   ├── commands/      # Slash Commands
│   ├── coordinator/    # 任务协调
│   ├── entrypoints/   # 入口点（IDE/CLI/Remote）
│   ├── hooks/         # 生命周期钩子
│   ├── memdir/        # 内存目录管理
│   ├── plugins/       # 插件系统
│   ├── skills/        # Skills 系统
│   ├── state/         # 状态管理
│   ├── tasks/         # Task 执行
│   └── tools/         # 工具系统
└── README.md
```

---

*CC源码剖析 · 最后更新：2026-05-01 ·2026 · skyseraph*