---
title: "OpenClaw源码剖析 #07 · 会话与状态管理"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 08
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、会话系统定位

会话系统是 OpenClaw 的**状态管理核心**——管理会话生命周期、持久化、解析与投递。

```
┌─────────────────────────────────────────────────────────────┐
│                     Session System                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    SessionEntry                        │  │
│  │  sessionId · model · tokenCount · skillsSnapshot      │  │
│  │  acp meta · pluginExtensions · compactionState        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Session Key   │  │ Session     │  │  Transcript │     │
│  │  解析          │  │ Store       │  │  管理        │     │
│  └────────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、核心类型

> 文件：`config/sessions/types.ts`

### 2.1 SessionEntry

```typescript
export type SessionEntry = {
  // 身份
  sessionId: string;
  updatedAt: number;
  sessionFile?: string;

  // 父子关系
  spawnedBy?: string;           // 孵化此会话的父会话
  parentSessionKey?: string;    // Dashboard 创建的子会话
  spawnedWorkspaceDir?: string; // 子会话继承的工作目录

  // 时间戳
  sessionStartedAt?: number;    // 首次活跃时间
  lastInteractionAt?: number;   // 最后交互时间
  startedAt?: number;           // 首次运行开始
  endedAt?: number;             // 最后运行结束
  runtimeMs?: number;           // 累计运行时长

  // 模型与 Token
  model?: string;
  modelOverride?: string;
  providerOverride?: string;
  authProfileOverride?: string;
  inputTokens?: number;
  outputTokens?: number;
  totalTokens?: number;
  cacheRead?: number;
  cacheWrite?: number;
  estimatedCostUsd?: number;

  // 运行时状态
  status?: "running" | "done" | "failed" | "killed" | "timeout";
  thinkingLevel?: string;
  fastMode?: boolean;
  verboseLevel?: string;
  agentRuntimeOverride?: string;

  // 渠道信息
  channel?: string;
  groupId?: string;
  groupChannel?: string;
  space?: string;
  origin?: SessionOrigin;
  deliveryContext?: DeliveryContext;

  // Skills
  skillsSnapshot?: SessionSkillSnapshot;
  systemPromptReport?: SessionSystemPromptReport;

  // ACP
  acp?: SessionAcpMeta;

  // 插件扩展
  pluginExtensions?: Record<string, Record<string, SessionPluginJsonValue>>;
  pluginNextTurnInjections?: Record<string, SessionPluginNextTurnInjection[]>;

  // Compaction
  compactionCount?: number;
  compactionCheckpoints?: SessionCompactionCheckpoint[];
  memoryFlushAt?: number;
  memoryFlushCompactionCount?: number;

  // 子 Agent
  spawnDepth?: number;
  subagentRole?: "orchestrator" | "leaf";
  subagentControlScope?: "children" | "none";
  subagentRecovery?: SubagentRecoveryState;
};
```

### 2.2 SessionScope

```typescript
export type SessionScope = "per-sender" | "global";
```

### 2.3 SessionOrigin

```typescript
export type SessionOrigin = {
  label?: string;
  provider?: string;
  surface?: string;
  chatType?: SessionChatType;
  from?: string;
  to?: string;
  nativeChannelId?: string;
  nativeDirectUserId?: string;
  accountId?: string;
  threadId?: string | number;
};
```

---

## 三、会话 Key 系统

> 文件：`config/sessions/session-key.ts`

### 3.1 Key 格式

```
agent:{agentId}:{scope}:{id}
```

示例：
- `agent:main:session:abc123` — 主 Agent 会话
- `agent:main:sender:telegram:user:123` — Telegram 用户会话
- `agent:codex:acp:uuid` — ACP 子 Agent 会话

### 3.2 Key 解析

```typescript
export function parseAgentSessionKey(
  sessionKey: string
): { agentId: string; scope: string; id: string } | null;

export function resolveAgentIdFromSessionKey(sessionKey: string): string;

export function resolveMainSessionKey(agentId: string): string;

export function resolveAgentMainSessionKey(agentId: string): string;
```

---

## 四、会话存储

> 文件：`config/sessions/store.ts`

### 4.1 SessionStore

```typescript
export type SessionStore = Record<string, SessionEntry>;

export function loadSessionStore(
  storePath: string,
  options?: { skipCache?: boolean }
): SessionStore;

export function updateSessionStore(
  storePath: string,
  updater: (store: SessionStore) => void
): void;
```

### 4.2 存储结构

```
{agentDir}/
└── sessions/
    └── {sessionKey}.json   // 每个会话一个文件
```

### 4.3 合并策略

```typescript
export function mergeSessionEntry(
  existing: SessionEntry | undefined,
  patch: Partial<SessionEntry>
): SessionEntry;

export function mergeSessionEntryWithPolicy(
  existing: SessionEntry | undefined,
  patch: Partial<SessionEntry>,
  options?: { policy?: "touch-activity" | "preserve-activity" }
): SessionEntry;
```

---

## 五、Transcript 管理

> 文件：`config/sessions/transcript.ts`

### 5.1 Transcript 文件

每个会话关联一个 transcript 文件，记录完整的对话历史：

```typescript
export function resolveSessionTranscriptFile(params: {
  sessionId: string;
  sessionKey: string;
  sessionEntry?: SessionEntry;
  sessionStore?: Record<string, SessionEntry>;
  storePath: string;
  agentId: string;
  threadId?: string | number;
}): Promise<{ sessionFile: string; sessionEntry: SessionEntry | undefined }>;
```

### 5.2 写入 Transcript

```typescript
// command/attempt-execution.ts
const sessionManager = SessionManager.open(sessionFile);
sessionManager.appendMessage({
  role: "user",
  content: promptText,
  timestamp: Date.now(),
});
sessionManager.appendMessage({
  role: "assistant",
  content: [{ type: "text", text: replyText }],
  api: "cli",
  provider, model,
  usage: resolveTranscriptUsage(params.assistant.usage),
  stopReason: "stop",
  timestamp: Date.now(),
});
```

---

## 六、会话生命周期

### 6.1 创建

> `config/sessions/lifecycle.ts`

```typescript
export function resolveSession(params: {
  cfg: OpenClawConfig;
  to?: string;
  sessionId?: string;
  sessionKey?: string;
  agentId?: string;
}) {
  // 1. 解析 Key
  // 2. 查找现有会话或创建新会话
  // 3. 返回会话元数据
}
```

### 6.2 更新

> `command/session-store.runtime.ts`

```typescript
export async function updateSessionStoreAfterAgentRun(params: {
  cfg: OpenClawConfig;
  sessionId, sessionKey, storePath, sessionStore,
  defaultProvider, defaultModel,
  fallbackProvider, fallbackModel,
  result,
  touchInteraction: boolean,
}) {
  // 更新 token 计数
  // 更新最后交互时间
  // 持久化到磁盘
}
```

### 6.3 重置

> `config/sessions/reset.ts`

```typescript
export function resolveSessionReset(params: {
  sessionKey: string;
  reason: "manual" | "idle" | "daily" | "compaction";
}): Promise<void>;
```

---

## 七、Compaction（压缩）

### 7.1 概念

会话过长时，通过 Compaction 将历史消息压缩为摘要，释放上下文窗口。

### 7.2 CompactionCheckpoint

```typescript
export type SessionCompactionCheckpoint = {
  checkpointId: string;
  sessionKey: string;
  sessionId: string;
  createdAt: number;
  reason: SessionCompactionCheckpointReason;
  tokensBefore?: number;
  tokensAfter?: number;
  summary?: string;
  firstKeptEntryId?: string;
  preCompaction: SessionCompactionTranscriptReference;
  postCompaction: SessionCompactionTranscriptReference;
};
```

### 7.3 触发条件

| 条件 | 说明 |
|:---|:---|
| `manual` | 用户手动触发 |
| `auto-threshold` | Token 超过阈值 |
| `overflow-retry` | 上下文溢出重试 |
| `timeout-retry` | 超时重试 |

---

## 八、ACP 会话

### 8.1 SessionAcpMeta

```typescript
export type SessionAcpMeta = {
  backend: string;
  agent: string;
  runtimeSessionName: string;
  identity?: SessionAcpIdentity;
  mode: "persistent" | "oneshot";
  runtimeOptions?: AcpSessionRuntimeOptions;
  cwd?: string;
  state: "idle" | "running" | "error";
  lastActivityAt: number;
  lastError?: string;
};
```

### 8.2 ACP Identity

```typescript
export type SessionAcpIdentity = {
  state: "pending" | "resolved";
  acpxRecordId?: string;
  acpxSessionId?: string;
  agentSessionId?: string;
  source: "ensure" | "status" | "event";
  lastUpdatedAt: number;
};
```

---

## 九、插件扩展

### 9.1 Plugin Extensions

```typescript
export type SessionPluginExtension = {
  pluginId: string;
  namespace: string;
  value: SessionPluginJsonValue;
};

// 存储结构
pluginExtensions: {
  [pluginId]: {
    [namespace]: value
  }
}
```

### 9.2 Next Turn Injection

```typescript
export type SessionPluginNextTurnInjection = {
  id: string;
  pluginId: string;
  text: string;
  placement: "prepend_context" | "append_context";
  ttlMs?: number;
  createdAt: number;
};
```

---

## 十、设计权衡

### 10.1 持久化策略

OpenClaw 采用**每会话单文件**策略：
- 避免单一大文件锁竞争
- 支持按会话独立清理
- 简化备份和迁移

### 10.2 Activity 合并策略

```typescript
// "touch-activity" — 更新 interaction 时间
// "preserve-activity" — 保留原有 interaction 时间
```

用于处理并发更新时的是否覆盖问题。

### 10.3 Subagent 继承

子 Agent 会话继承父会话的：
- `spawnedWorkspaceDir` — 工作目录复用
- `spawnDepth` — 深度计数
- `subagentRole` — 角色分配

---

## 下一步

下一篇：[08 - 记忆系统：Memory Architecture](./08-memory-system.md)，深入长期记忆与上下文注入。

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*