---
title: "OpenClaw源码剖析 #04 · Agent Runtime：任务编排与执行"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 05
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Agent Runtime 定位

Agent Runtime 是 OpenClaw 的**任务执行引擎**——负责接收消息、选择模型、调度工具、生成回复。

```
┌──────────────────────────────────────────────────────────────┐
│                     Agent Runtime                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   agent-command.ts                       │ │
│  │  入口：解析参数 → 解析会话 → 路由到 Harness            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                   │
│         ┌─────────────────┼─────────────────┐                 │
│         ▼                 ▼                 ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ ACP Harness │  │ PI Harness  │  │ CLI Harness │           │
│  │ (外部 Agent)│  │ (内置模型)  │  │ (Claude CLI)│           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              attempt-execution.ts                        │ │
│  │  认证计划 · 模型选择 · Fallback · 生命周期              │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件 | 职责 |
|:---|:---|
| `agent-command.ts` | 命令入口，解析参数，协调执行流程 |
| `command/attempt-execution.ts` | 核心执行引擎，运行单次 Agent Attempt |
| `command/delivery.ts` | 结果投递到渠道 |
| `command/session.ts` | 会话解析与创建 |
| `command/run-context.ts` | 运行上下文构建 |
| `harness/types.ts` | Harness 接口定义 |
| `harness/registry.ts` | Harness 注册表 |
| `harness/selection.ts` | Harness 选择策略 |
| `acp-spawn.ts` | ACP 子 Agent 孵化 |

---

## 三、Agent 命令入口

> 文件：`agent-command.ts`

### 3.1 执行流程

```typescript
// agent-command.ts
export async function agentCommand(opts: AgentCommandOpts, runtime: RuntimeEnv, deps?: CliDeps) {
  return await agentCommandInternal({
    ...opts,
    senderIsOwner: opts.senderIsOwner ?? true,
    allowModelOverride: opts.allowModelOverride ?? true,
  }, runtime, deps);
}

async function agentCommandInternal(opts, runtime = defaultRuntime, deps?) {
  // Step 1: 准备执行
  const prepared = await prepareAgentCommandExecution(opts, runtime);

  // Step 2: 判断运行模式
  // ACP 模式：直接调用 ACP Runtime
  if (acpResolution?.kind === "ready") {
    return await acpManager.runTurn({ ... });
  }

  // 标准模式：通过 Harness 执行
  // Step 3: 解析 Skills Snapshot
  const skillsSnapshot = needsSkillsSnapshot
    ? await buildWorkspaceSkillSnapshot(workspaceDir, { ... })
    : currentSkillsSnapshot;

  // Step 4: 解析模型
  const { provider, model } = resolveModelRef(...);

  // Step 5: 执行 Attempt（带 Fallback）
  const result = await runWithModelFallback({
    run: async (providerOverride, modelOverride) => {
      return attemptExecutionRuntime.runAgentAttempt({ ... });
    }
  });

  // Step 6: 投递结果
  return deliverAgentCommandResult({ result, ... });
}
```

### 3.2 AgentCommandOpts

```typescript
export type AgentCommandOpts = {
  message: string;
  to?: string;
  sessionId?: string;
  sessionKey?: string;
  agentId?: string;
  model?: string;
  provider?: string;
  thinking?: string;
  thinkingOnce?: string;
  verbose?: string;
  timeout?: string;
  lane?: string;
  deliver?: boolean;
  threadId?: string | number;
  spawnedBy?: string;
  groupId?: string;
  groupChannel?: string;
  groupSpace?: string;
  workspaceDir?: string;
  images?: string[];
  imageOrder?: string[];
  clientTools?: Record<string, unknown>;
  extraSystemPrompt?: string;
  bootstrapContextMode?: string;
  bootstrapContextRunKind?: string;
  internalEvents?: unknown[];
  inputProvenance?: unknown;
  streamParams?: unknown;
  modelRun?: boolean;
  promptMode?: "none" | "default";
};
```

---

## 四、Harness 系统

> 文件：`harness/types.ts`

### 4.1 Harness 接口

Harness 是 Agent 执行能力的抽象：

```typescript
export type AgentHarness = {
  id: string;
  label: string;
  pluginId?: string;

  // 支持性检查
  supports(ctx: AgentHarnessSupportContext): AgentHarnessSupport;

  // 执行 Attempt
  runAttempt(params: AgentHarnessAttemptParams): Promise<AgentHarnessAttemptResult>;

  // 结果分类（可选）
  classify?(result, ctx): AgentHarnessResultClassification | undefined;

  // 压缩会话（可选）
  compact?(params): Promise<AgentHarnessCompactResult | undefined>;

  // 重置会话（可选）
  reset?(params): Promise<void> | void;

  // 释放资源（可选）
  dispose?(): Promise<void> | void;
};
```

### 4.2 内置 Harness 类型

| Harness | 说明 | 用途 |
|:---|:---|:---|
| `builtin-pi` | 内置 PI Agent | 默认的 pi-ai 嵌入式 Agent |
| `codex-app-server` | Codex App Server | 代码任务专用 |
| `cli` | Claude CLI | 调用本地 Claude CLI |

### 4.3 Harness 选择策略

> 文件：`harness/selection.ts`

```typescript
export function resolveAgentHarnessPolicy(params: {
  provider: string;
  modelId: string;
  config: OpenClawConfig;
  agentId: string;
  sessionKey: string;
}): { runtime: string; fallback: string } {
  // 1. 检查会话是否固定了 Harness
  // 2. 检查 Agent 配置
  // 3. 检查 Provider 策略
  // 4. 回退到默认策略
}
```

---

## 五、执行引擎（Attempt Execution）

> 文件：`command/attempt-execution.ts`

### 5.1 runAgentAttempt

```typescript
export function runAgentAttempt(params: {
  providerOverride: string;
  modelOverride: string;
  originalProvider: string;
  cfg: OpenClawConfig;
  sessionEntry: SessionEntry | undefined;
  sessionId: string;
  sessionKey: string | undefined;
  sessionAgentId: string;
  sessionFile: string;
  workspaceDir: string;
  body: string;
  isFallbackRetry: boolean;
  resolvedThinkLevel: ThinkLevel;
  timeoutMs: number;
  runId: string;
  opts: AgentCommandOpts;
  runContext: ReturnType<typeof resolveAgentRunContext>;
  spawnedBy: string | undefined;
  messageChannel: ReturnType<typeof resolveMessageChannel>;
  skillsSnapshot: ReturnType<typeof buildWorkspaceSkillSnapshot> | undefined;
  resolvedVerboseLevel: VerboseLevel | undefined;
  agentDir: string;
  authProfileProvider: string;
  sessionStore?: Record<string, SessionEntry>;
  storePath?: string;
}) {
  // 1. 解析 Prompt（含重试上下文）
  const effectivePrompt = annotateInterSessionPromptText(resolvedPrompt, ...);

  // 2. 选择 Harness
  const agentHarnessPolicy = resolveAgentHarnessPolicy({ ... });
  const sessionPinnedAgentHarnessId = resolveSessionPinnedAgentHarnessId({ ... });

  // 3. 构建认证计划
  const harnessAuthSelection = resolveHarnessAuthProfileSelection({ ... });
  const runtimeAuthPlan = buildAgentRuntimeAuthPlan({ ... });

  // 4. 分发到对应执行器
  if (isCliProvider(cliExecutionProvider)) {
    return runCliAgent({ ... });
  }
  return runEmbeddedPiAgent({ ... });
}
```

### 5.2 模型回退（Model Fallback）

```typescript
// attempt-execution.ts 中的执行循环
for (;;) {
  try {
    const fallbackResult = await runWithModelFallback({
      provider,
      model,
      runId,
      classifyResult: ({ provider, model, result }) =>
        classifyEmbeddedPiRunResultForModelFallback({ provider, model, result }),
      run: async (providerOverride, modelOverride) => {
        return attemptExecutionRuntime.runAgentAttempt({
          providerOverride,
          modelOverride,
          ...
        });
      },
    });
    result = fallbackResult.result;
    break;
  } catch (err) {
    if (err instanceof LiveSessionModelSwitchError) {
      // Live 模型切换重试
      liveSwitchRetries++;
      if (liveSwitchRetries > MAX_LIVE_SWITCH_RETRIES) throw err;
      provider = err.provider;
      model = err.model;
      continue;
    }
    throw err;
  }
}
```

---

## 六、ACP 子 Agent 系统

> 文件：`acp-spawn.ts`

### 6.1 ACP Spawn 参数

```typescript
export type SpawnAcpParams = {
  task: string;              // 任务描述
  label?: string;            // 会话标签
  agentId?: string;          // 目标 Agent ID
  resumeSessionId?: string;   // 恢复会话 ID
  model?: string;            // 模型覆盖
  thinking?: string;         // 思考层级
  runTimeoutSeconds?: number; // 超时（秒）
  cwd?: string;              // 工作目录
  mode?: "run" | "session"; // 运行模式
  thread?: boolean;           // 是否绑定线程
  sandbox?: "inherit" | "require"; // 沙箱模式
  streamTo?: "parent";       // 输出流目标
};
```

### 6.2 ACP Spawn 结果

```typescript
type SpawnAcpAcceptedResult = {
  status: "accepted";
  childSessionKey: string;
  runId: string;
  mode: "run" | "session";
  streamLogPath?: string;
  note?: string;
};

type SpawnAcpFailedResult = {
  status: "forbidden" | "error";
  error: string;
  errorCode: SpawnAcpErrorCode;
};
```

### 6.3 Spawn 错误码

```typescript
export const ACP_SPAWN_ERROR_CODES = [
  "acp_disabled",           // ACP 被策略禁用
  "requester_session_required", // 需要请求者会话
  "runtime_policy",           // 运行时策略冲突
  "resume_forbidden",        // 恢复会话被禁止
  "subagent_policy",         // 子 Agent 策略限制
  "thread_required",         // 需要线程上下文
  "target_agent_required",   // 需要目标 Agent
  "runtime_agent_mismatch",   // Agent 类型不匹配
  "agent_forbidden",          // Agent 被策略禁止
  "cwd_resolution_failed",    // 工作目录解析失败
  "thread_binding_invalid",   // 线程绑定无效
  "spawn_failed",             // 孵化失败
  "dispatch_failed",          // 分发失败
] as const;
```

---

## 七、会话与状态管理

### 7.1 会话解析

> 文件：`command/session.ts`

```typescript
export function resolveSession(params: {
  cfg: OpenClawConfig;
  to?: string;
  sessionId?: string;
  sessionKey?: string;
  agentId?: string;
}) {
  // 1. 按优先级尝试解析：
  //    sessionKey > sessionId > (to + agentId)
  // 2. 查找或创建会话
  // 3. 返回会话元数据
}
```

### 7.2 会话存储更新

> 文件：`command/session-store.runtime.ts`

```typescript
export async function updateSessionStoreAfterAgentRun(params: {
  cfg: OpenClawConfig;
  sessionId, sessionKey, storePath, sessionStore,
  defaultProvider, defaultModel,
  fallbackProvider, fallbackModel,
  result,
  touchInteraction: boolean,
}) {
  // 更新会话的：
  // - 模型使用计数
  // - Token 使用量
  // - 最后交互时间
  // - 运行元数据
}
```

---

## 八、执行流程图

```
agentCommand()
    │
    ├─► prepareAgentCommandExecution()
    │      ├─► 解析会话
    │      ├─► 解析模型和 Provider
    │      ├─► 构建 Skills Snapshot
    │      └─► 解析 Thinking 层级
    │
    ├─► [ACP 模式?] ─► acpManager.runTurn()
    │
    └─► [标准模式]
           │
           ├─► runWithModelFallback()
           │      │
           │      └─► runAgentAttempt()
           │             ├─► 选择 Harness (pi / cli / codex)
           │             ├─► 构建 Auth Plan
           │             └─► 执行 (runEmbeddedPiAgent / runCliAgent)
           │
           ├─► updateSessionStoreAfterAgentRun()
           ├─► persistCliTurnTranscript()
           ├─► runCliTurnCompactionLifecycle()
           └─► deliverAgentCommandResult()
```

---

## 九、设计权衡

### 9.1 Harness 抽象

引入 Harness 层是为了解耦**执行引擎**与**运行时**：

- `pi` harness：嵌入式 AI 模型执行
- `cli` harness：调用外部 Claude CLI
- 自定义 harness：第三方执行引擎

这种设计允许 OpenClaw 在不改变核心逻辑的情况下接入新的执行后端。

### 9.2 模型 Fallback

模型选择不是一次性决策，而是**带重试的尝试链**：

```typescript
runWithModelFallback({
  provider, model,
  fallbacks: [...],
  run: (p, m) => attempt(...),
  classifyResult: (...) => { ... }
})
```

当主模型失败时，自动尝试 fallback 列表中的下一个。

### 9.3 ACP 子 Agent 的沙箱隔离

ACP Spawn 支持沙箱模式：

- `sandbox="require"`：强制在沙箱中运行
- `sandbox="inherit"`：继承父 Agent 的沙箱状态
- 子 Agent 有深度限制（`maxSpawnDepth`）和并发限制（`maxChildrenPerAgent`）

---

## 下一步

下一篇：[05 - Provider 系统：多模型统一接口](./05-provider-system.md)，深入 Provider 抽象层如何支持 40+ 模型厂商。

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*