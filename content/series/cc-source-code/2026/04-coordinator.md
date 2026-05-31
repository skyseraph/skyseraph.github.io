---
title: "CC源码剖析 #04 · 多阶段任务编排器"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 5
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Coordinator 模式定位

Coordinator 是 Claude Code 的**多 Agent 并行编排模式**，通过 `COORDINATOR_MODE` Feature Flag 激活。

当用户任务需要多路并行研究、验证时，Coordinator 派生出多个 Worker Agent，各自独立工作，结果汇总到 Coordinator。

```
用户输入
    │
    ▼
┌─────────────┐
│ Coordinator │ ←── Feature Flag: COORDINATOR_MODE
│  (主 Agent) │
└──────┬──────┘
       │ parallel launch
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────┐   ┌──────────┐
│ Worker A │   │ Worker B │
│ Research │   │ Research │
└────┬─────┘   └────┬─────┘
     │              │
     │ task-notification (结果)
     ▼              ▼
┌──────────────┐
│ Coordinator │ ←── 合成结果，发给用户
│  (汇总统筹) │
└──────────────┘
```

---

## 二、核心工具集

Coordinator 通过四个核心 Tool 管理 Worker 生命周期：

| Tool | 功能 |
| :--- | :--- |
| `AgentTool` | 派生子 Worker（`subagent_type: "worker"`） |
| `SendMessageTool` | 向已有 Worker 发消息（继续工作） |
| `TaskStopTool` | 停止正在运行的 Worker |
| `TeamCreateTool` / `TeamDeleteTool` | 团队级管理 |

关键文件：`src/coordinator/coordinatorMode.ts`

---

## 三、AgentTool — Worker 派生

### 3.1 subagent_type: "worker"

```typescript
// 派生 Worker 时指定 subagent_type = "worker"
AGENT_TOOL_NAME({ description: "Investigate auth bug", subagent_type: "worker", prompt: "..." })
```

### 3.2 工具权限控制

```typescript
// Coordinator 的 workers 使用受限工具集
const INTERNAL_WORKER_TOOLS = new Set([
  TEAM_CREATE_TOOL_NAME,
  TEAM_DELETE_TOOL_NAME,
  SEND_MESSAGE_TOOL_NAME,
  SYNTHETIC_OUTPUT_TOOL_NAME,
])

// SIMPLE 模式下只有 Bash/Read/Edit
const workerTools = isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)
  ? [BASH_TOOL_NAME, FILE_READ_TOOL_NAME, FILE_EDIT_TOOL_NAME]
  : Array.from(ASYNC_AGENT_ALLOWED_TOOLS)
      .filter(name => !INTERNAL_WORKER_TOOLS.has(name))
```

### 3.3 Worker 能力差异

| 模式 | 可用工具 |
| :--- | :--- |
| `SIMPLE` | Bash, Read, Edit |
| `标准` | 全部工具（除内部工具） + MCP + Skills |

---

## 四、任务通知机制

### 4.1 task-notification 格式

Worker 完成后，结果以 `<task-notification>` XML 格式发回：

```xml
<task-notification>
<task-id>{agentId}</task-id>
<status>completed|failed|killed</status>
<summary>{human-readable status summary}</summary>
<result>{agent's final text response}</result>
<usage>
  <total_tokens>N</total_tokens>
  <tool_uses>N</tool_uses>
  <duration_ms>N</duration_ms>
</usage>
</task-notification>
```

### 4.2 消息路由

```
Worker → 消息发回 Coordinator 作为 user-role message
       → Coordinator 解析 <task-notification> 标签识别来源
       → 决定继续（SendMessage）还是启动新 Worker
```

---

## 五、四阶段工作流

### 5.1 阶段划分

| Phase | 执行者 | 目的 |
|-------|-------|------|
| Research | Workers（并行） | 调查代码库、理解问题 |
| Synthesis | **Coordinator** | 阅读发现，制定实现规格 |
| Implementation | Workers | 按规格改代码、提交 |
| Verification | Workers | 测试验证 |

### 5.2 并行策略

```typescript
// Coordinator 系统提示中的并行指导：
"Launch independent workers concurrently whenever possible
— don't serialize work that can run simultaneously and look
for opportunities to fan out. When doing research, cover
multiple angles. To launch workers in parallel, make
multiple tool calls in a single message."
```

### 5.3 并发冲突处理

| 场景 | 策略 |
|:-----|:-----|
| 只读任务（研究） | 自由并行 |
| 写任务（实现） | 每次一组文件串行 |
| 验证 | 可与不同文件区实现并行 |

---

## 六、Continue vs Spawn 决策

### 6.1 判断矩阵

| Situation | Mechanism | Why |
|-----------|-----------|-----|
| 研究已探索了需要编辑的文件 | **Continue** (`SendMessageTool`) | Worker 已加载文件上下文 |
| 研究广泛但实现狭窄 | **Spawn fresh** | 避免探索噪声干扰实现 |
| 修正失败或延伸近期工作 | **Continue** | 有错误上下文 |
| 验证另一 Worker 刚写的代码 | **Spawn fresh** | 独立验证，不带实现假设 |
| 第一次尝试方向完全错误 | **Spawn fresh** | 错误上下文会污染重试 |
| 完全无关任务 | **Spawn fresh** | 无可复用上下文 |

### 6.2 合成规则（最重要）

```typescript
// 核心原则：Worker 看不到你的对话
// 每个 prompt 必须自包含所有必要信息

// Anti-pattern（禁止）：
AGENT_TOOL_NAME({ prompt: "Based on your findings, fix the auth bug", ... })

// Good（必须）：
AGENT_TOOL_NAME({
  prompt: "Fix the null pointer in src/auth/validate.ts:42.
  The user field on Session (src/auth/types.ts:15) is undefined
  when sessions expire but the token remains cached.
  Add a null check before user.id access — if null, return 401
  with 'Session expired'. Commit and report the hash.",
  ...
})
```

**"Never write 'based on your findings'"** — 这是 Coordinator 最重要的规则。

---

## 七、Coordinator 系统提示

### 7.1 角色定义

```typescript
"You are Claude Code, an AI assistant that orchestrates
software engineering tasks across multiple workers."

// Coordinator 的职责：
// 1. 帮助用户达成目标
// 2. 指挥 workers 研究、实现、验证
// 3. 合成结果与用户沟通
// 4. 能直接回答的不委托
```

### 7.2 结果报告规则

```typescript
// Worker 结果是内部信号，不是对话伙伴
// 不要感谢或确认它们
"Every message you send is to the user. Worker results
and system notifications are internal signals, not
conversation partners — never thank or acknowledge them.
Summarize new information for the user as it arrives."
```

---

## 八、错误恢复

### 8.1 Worker 失败处理

```typescript
// Worker 报告失败（测试失败、构建错误）：
// → 用 SendMessageTool 继续同一 Worker（有完整错误上下文）
// → 修正失败则尝试不同方法
// → 无法恢复则报告用户
```

### 8.2 停止 Worker

```typescript
// 用 TASK_STOP_TOOL_NAME 停止方向错误的 Worker
TASK_STOP_TOOL_NAME({ task_id: "agent-x7q" })

// 然后用 SendMessageTool 继续，给出正确方向
SEND_MESSAGE_TOOL_NAME({ to: "agent-x7q", message: "Stop the JWT refactor..." })
```

---

## 九、Feature Flag 注入

```typescript
// main.tsx 中条件导入
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js')
  : null;

// coordinatorMode.ts 中检查
export function isCoordinatorMode(): boolean {
  if (feature('COORDINATOR_MODE')) {
    return isEnvTruthy(process.env.CLAUDE_CODE_COORDINATOR_MODE)
  }
  return false
}
```

未激活时，整个 `coordinator/` 模块代码不打包进二进制。

---

## 十、与其他模块的关系

```
coordinatorMode.ts
  ├── 被 main.tsx 条件导入（COORDINATOR_MODE）
  ├── AgentTool → 工具系统
  ├── SendMessageTool → 消息传递
  ├── TaskStopTool → 任务管理
  └── getCoordinatorUserContext() → context.ts（系统提示构建）
```

---

## 下一步

下一篇：[05 - Tools 系统：工具定义、注册与执行](https://skyseraph.github.io/series/cc-source-code/2026/05-tools-system)，深入 `tools/` 模块的 Tool 基类、Schema 验证与权限模型。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*