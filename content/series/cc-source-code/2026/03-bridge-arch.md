---
title: "CC源码剖析 #03 · Bridge 模块：主进程与渲染进程的通信机制"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 4
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Bridge 在整个架构中的位置

Bridge 是 Claude Code 最复杂的模块，负责 **IDE 扩展（VSCode/JetBrains）与 CLI 进程之间的双向通信**。

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude.ai Web                           │
│                 (Remote Control UI)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ WebSocket / HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│                     Bridge Module                           │
│  src/bridge/                                             │
│  ├── bridgeMain.ts      # 主循环：轮询 + 会话管理           │
│  ├── bridgeApi.ts       # REST API 客户端                   │
│  ├── replBridge.ts      # REPL ↔ Bridge 桥接核心            │
│  ├── replBridgeTransport.ts  # WebSocket 传输层             │
│  ├── bridgeMessaging.ts # 消息协议 + 类型守卫                │
│  ├── sessionRunner.ts   # 子进程 Spawn 管理                  │
│  └── jwtUtils.ts        # JWT 刷新 + 心跳                    │
└────┬────────────────────┬──────────────────────────────────┘
     │                    │
┌────▼────────┐     ┌─────▼────────┐
│ VSCode 扩展  │     │ JetBrains 扩展│
│ (TypeScript)│     │  (Kotlin)   │
└────┬────────┘     └─────┬────────┘
     │ IPC(UDS)          │ IPC(UDS)
┌────▼────────────────────▼────┐
│    CLI 主进程 (claude)       │
│  src/main.tsx               │
│  ├── launchRepl()           │
│  └── REPL.tsx               │
└─────────────────────────────┘
```

---

## 二、三种 Spawn Mode（会话隔离策略）

| Mode | 行为 | 适用场景 |
| :--- | :--- | :--- |
| `single-session` | 每个工作请求独占 cwd，结束后销毁 | 临时任务 |
| `worktree` | 每个会话分配独立 git worktree | 持久服务器，多会话并行 |
| `same-dir` | 多会话共享同一目录（可互相覆盖） | 轻量多会话 |

关键文件：`src/bridge/types.ts:69`

```typescript
export type SpawnMode = 'single-session' | 'worktree' | 'same-dir'
```

---

## 三、`bridgeMain.ts` — 主循环与会话管理

> 文件：`src/bridge/bridgeMain.ts`，约 1,000 行

### 3.1 `runBridgeLoop` 主循环

```typescript
export async function runBridgeLoop(
  config: BridgeConfig,
  environmentId: string,
  environmentSecret: string,
  api: BridgeApiClient,
  spawner: SessionSpawner,
  logger: BridgeLogger,
  signal: AbortSignal,
  backoffConfig: BackoffConfig = DEFAULT_BACKOFF,
): Promise<void> {
  const activeSessions = new Map<string, SessionHandle>()
  const sessionWorkIds = new Map<string, string>()
  const sessionIngressTokens = new Map<string, string>()  // JWT 心跳认证
  const capacityWake = createCapacityWake(loopSignal)      // 容量满时唤醒信号
  // ...
}
```

### 3.2 核心数据结构

```typescript
interface SessionHandle {
  sessionId: string
  workId: string
  process: ChildProcess
  accessToken: string
  transport: ReplBridgeTransport
}
```

### 3.3 心跳机制

```typescript
// heartbeatWorker() 每 1s 发送一次活性证明
// JWT 在 ~3h55m 后过期，通过 refreshToken 续期
const sessionIngressTokens = new Map<string, string>()
// token refresh scheduler 更新 accessToken 字段
```

### 3.4 退避重连配置

```typescript
const DEFAULT_BACKOFF: BackoffConfig = {
  connInitialMs: 2_000,    // 初始 2s
  connCapMs: 120_000,      // 上限 2 分钟
  connGiveUpMs: 600_000,   // 放弃上限 10 分钟
  generalInitialMs: 500,
  generalCapMs: 30_000,
}
```

---

## 四、`bridgeApi.ts` — REST API 客户端

### 4.1 核心接口

```typescript
export type BridgeApiClient = {
  registerBridgeEnvironment(config: BridgeConfig): Promise<{
    environment_id: string
    environment_secret: string
  }>
  pollForWork(
    environmentId: string,
    environmentSecret: string,
    signal?: AbortSignal,
    reclaimOlderThanMs?: number,
  ): Promise<WorkResponse | null>
  acknowledgeWork(
    environmentId: string,
    workId: string,
    sessionToken: string,
  ): Promise<void>
  stopWork(environmentId: string, workId: string, force: boolean): Promise<void>
}
```

### 4.2 WorkSecret 解密

```typescript
export type WorkSecret = {
  version: number
  session_ingress_token: string
  api_base_url: string
  sources: Array<{
    type: string
    git_info?: { type: string; repo: string; ref?: string; token?: string }
  }>
  auth: Array<{ type: string; token: string }>
  claude_code_args?: Record<string, string>
  mcp_config?: unknown
  environment_variables?: Record<string, string>
  use_code_sessions?: boolean  // CCR v2 兼容层标志
}
```

---

## 五、`replBridge.ts` — REPL ↔ Bridge 桥接核心

> 文件：`src/bridge/replBridge.ts`，约 700 行

### 5.1 双向桥接架构

```
IDE Extension                    CLI (REPL)
    │                                │
    │──── init-session ────────────▶│
    │                                │
    │◀───── session_established ────│
    │                                │
    │──── user-message ──────────────▶│
    │◀───── tool_result ─────────────│
    │◀───── tool_use ────────────────│
    │                                │
    │──── control_request ◀─────────│ (服务器下发控制)
    │◀───── control_response ───────│
```

### 5.2 `ReplBridgeHandle` 接口

```typescript
export type ReplBridgeHandle = {
  bridgeSessionId: string
  environmentId: string
  sessionIngressUrl: string
  writeMessages(messages: Message[]): void       // 写入对话消息
  writeSdkMessages(messages: SDKMessage[]): void // 写入 SDK 消息
  sendControlRequest(request: SDKControlRequest): void   // 发控制请求
  sendControlResponse(response: SDKControlResponse): void // 发控制响应
  sendControlCancelRequest(requestId: string): void     // 取消请求
  sendResult(): void                   // 发送结果
  teardown(): Promise<void>            // 清理
}
```

### 5.3 消息路由

`writeMessages()` 将 REPL 内部消息转换为 SDK 格式后写入 transport：

```typescript
// 消息筛选规则：只转发 user/assistant 和 local_command 系统事件
export function isEligibleBridgeMessage(m: Message): boolean {
  if ((m.type === 'user' || m.type === 'assistant') && m.isVirtual) {
    return false  // 虚拟消息（REPL 内部调用）不转发
  }
  return (
    m.type === 'user' ||
    m.type === 'assistant' ||
    (m.type === 'system' && m.subtype === 'local_command')
  )
}
```

### 5.4 `BridgeCoreParams` — 参数注入

```typescript
export type BridgeCoreParams = {
  dir: string
  machineName: string
  branch: string
  gitRepoUrl: string | null
  title: string
  baseUrl: string
  sessionIngressUrl: string
  workerType: string
  getAccessToken: () => string | undefined
  createSession: (opts: {...}) => Promise<string | null>
  archiveSession: (sessionId: string) => Promise<void>
  getCurrentTitle?: () => string
  toSDKMessages?: (messages: Message[]) => SDKMessage[]
}
```

**注入原因**：避免将 REPL 相关模块（`commands.ts`、React 树）拖入 Agent SDK bundle。

---

## 六、`replBridgeTransport.ts` — WebSocket 传输层

### 6.1 V1 vs V2 传输协议

```typescript
// V1: 基础 WebSocket
createV1ReplTransport(ingressUrl, token, handlers)

// V2: 带 seq-num 的可靠消息协议（防重放/防丢失）
createV2ReplTransport(ingressUrl, token, handlers)
```

V2 通过序列号确保消息不重复、不丢失。

### 6.2 `HybridTransport`

```typescript
// 混合传输：同时支持 WebSocket 和 HTTP 流式
class HybridTransport {
  // 优先 WebSocket，fallback HTTP
}
```

---

## 七、`sessionRunner.ts` — 子进程 Spawn 管理

### 7.1 `SessionSpawner` 接口

```typescript
export type SessionSpawnOpts = {
  workId: string
  workSecret: WorkSecret
  dir: string
  branch?: string
  title?: string
  sessionTimeoutMs?: number
}

export type SessionSpawner = {
  spawn(opts: SessionSpawnOpts, dir: string): SessionHandle
  abort(sessionId: string): void
}
```

### 7.2 Spawn 参数处理

```typescript
function spawnScriptArgs(): string[] {
  // npm 安装（node 运行 cli.js）需要传入脚本路径
  // 直接运行二进制则不需要
  if (isInBundledMode() || !process.argv[1]) {
    return []
  }
  return [process.argv[1]]
}
```

---

## 八、消息协议与类型守卫

> 文件：`src/bridge/bridgeMessaging.ts`

### 8.1 核心类型守卫

```typescript
// 判定是否是合法 SDK 消息
export function isSDKMessage(value: unknown): value is SDKMessage {
  return value !== null && typeof value === 'object' && 'type' in value
}

// 控制响应（权限决策）
export function isSDKControlResponse(value: unknown): value is SDKControlResponse {
  return (
    value !== null &&
    typeof value === 'object' &&
    'type' in value &&
    value.type === 'control_response' &&
    'response' in value
  )
}

// 控制请求（服务器下发）
export function isSDKControlRequest(value: unknown): value is SDKControlRequest {
  return (
    value !== null &&
    typeof value === 'object' &&
    'type' in value &&
    value.type === 'control_request' &&
    'request_id' in value &&
    'request' in value
  )
}
```

### 8.2 Ingress 消息处理

```typescript
export function handleIngressMessage(
  data: string,
  recentPostedUUIDs: BoundedUUIDSet,    // 已发送 UUID（去重回声）
  recentInboundUUIDs: BoundedUUIDSet,  // 已接收 UUID（防重放）
  onInboundMessage: ((msg: SDKMessage) => void) | undefined,
  onPermissionResponse?: ((response: SDKControlResponse) => void),
  onControlRequest?: ((request: SDKControlRequest) => void),
): void
```

---

## 九、JWT 认证与刷新

> 文件：`src/bridge/jwtUtils.ts`

### 9.1 Token 刷新调度器

```typescript
// OAuth token ~3h55m 过期，需要刷新
const tokenRefreshScheduler = createTokenRefreshScheduler(
  sessionIngressTokens, // Map<sessionId, token>
  api,
)

// 每隔固定时间检查即将过期的 token，提前刷新
```

### 9.2 Trusted Device Token

```typescript
getTrustedDeviceToken()  // macOS Keychain 读取
// 用于长期设备认证，避免每次重新登录
```

---

## 十、容量控制与唤醒

> 文件：`src/bridge/capacityWake.ts`

```typescript
// 容量满时（activeSessions >= maxSessions），
// 新工作请求会进入等待队列而非立即创建会话
export const capacityWake = createCapacityWake(loopSignal)

// 当会话完成时，wake 唤醒等待中的 poll，继续接受新工作
```

---

## 十一、启动模式对比

| 模式 | 来源 | 通信方式 |
| :--- | :--- | :--- |
| `claude` (本地) | CLI 直接运行 | 无 Bridge |
| `claude remote-control` | 后台守护进程 | WebSocket → bridgeMain |
| VSCode/JetBrains 扩展 | IDE 插件 | UDS IPC → bridgeMain → REPL |
| Agent SDK | 外部进程 | HTTP/WebSocket → replBridge |

---

## 下一步

下一篇：[04 - Coordinator：多阶段任务编排器](https://skyseraph.github.io/series/cc-source-code/2026/04-coordinator)，深入 `coordinator/` 模块的多 Agent 协作机制。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*