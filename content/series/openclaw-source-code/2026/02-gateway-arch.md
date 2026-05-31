---
title: "OpenClaw源码剖析 #02 · Gateway 控制平面：API 路由与协议"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 3
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Gateway 定位

Gateway 是 OpenClaw 的**控制平面**——负责接收来自渠道的消息、管理会话、协调 Agent 执行。

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                     │
│                    控制平面                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ 渠道接入 │  │  会话    │  │  凭证   │               │
│  │          │  │  管理    │  │  管理   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  协议    │  │  API     │  │  运行时  │               │
│  │  处理器  │  │  路由    │  │  协调    │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────┘
         │                │               │
         ▼                ▼               ▼
┌──────────────────────────────────────────────────┐
│              Extensions / Plugins                  │
│   Channel (Telegram/Discord)  │  Provider (OpenAI) │
└──────────────────────────────────────────────────┘
```

---

## 二、模块结构

> 文件：`src/gateway/`

### 2.1 核心文件

| 文件 | 职责 |
|:---|:---|
| `boot.ts` | 启动引导（BOOT.md） |
| `call.ts` | Gateway 调用接口 |
| `client.ts` | Gateway 客户端 |
| `auth.ts` | 认证系统 |
| `auth-config-utils.ts` | 认证配置工具 |
| `auth-mode-policy.ts` | 认证模式策略 |
| `auth-rate-limit.ts` | 认证限流 |
| `auth-token-resolution.ts` | Token 解析 |
| `auth-surface-resolution.ts` | 认证表面解析 |
| `credentials.ts` | 凭证管理 |
| `connection-auth.ts` | 连接认证 |
| `connection-details.ts` | 连接详情 |

### 2.2 会话与状态

| 文件 | 职责 |
|:---|:---|
| `session.ts` | 会话管理 |
| `sessions.ts` | 会话列表 |
| `session-store.ts` | 会话存储 |
| `session-keys.ts` | 会话 Key 解析 |

### 2.3 协议与 API

| 文件 | 职责 |
|:---|:---|
| `protocol/` | 协议定义 |
| `api-builder.ts` | API 构建器 |
| `method-scopes.ts` | 方法权限范围 |
| `control-plane-audit.ts` | 控制平面审计 |

### 2.4 渠道管理

| 文件 | 职责 |
|:---|:---|
| `channel-health-monitor.ts` | 渠道健康监控 |
| `channel-health-policy.ts` | 渠道健康策略 |
| `channel-status-patches.ts` | 渠道状态补丁 |

---

## 三、启动引导（Boot）

> 文件：`src/gateway/boot.ts`

### 3.1 BOOT.md 机制

Gateway 启动时可以执行 `BOOT.md` 中的指令：

```typescript
const BOOT_FILENAME = "BOOT.md";

function buildBootPrompt(content: string) {
  return [
    "You are running a boot check. Follow BOOT.md instructions exactly.",
    "",
    "BOOT.md:",
    content,
    "",
    "If BOOT.md asks you to send a message, use the message tool.",
    `After sending, reply with ONLY: ${SILENT_REPLY_TOKEN}.`,
    `If nothing needs attention, reply with ONLY: ${SILENT_REPLY_TOKEN}.`,
  ].join("\n");
}
```

### 3.2 引导流程

```typescript
type BootRunResult =
  | { status: "skipped"; reason: "missing" | "empty" }
  | { status: "ran" }
  | { status: "failed"; reason: string };
```

1. 读取 workspace 中的 `BOOT.md`
2. 如果文件为空或不存在，跳过
3. 构建引导 prompt
4. 执行引导指令（发送消息等）
5. 返回执行结果

---

## 四、Gateway 调用接口

> 文件：`src/gateway/call.ts`

### 4.1 CallGatewayBaseOptions

```typescript
type CallGatewayBaseOptions = {
  url?: string;           // Gateway URL
  token?: string;         // 认证 token
  password?: string;      // 密码
  tlsFingerprint?: string; // TLS 指纹
  config?: OpenClawConfig; // 配置对象
  method: string;          // 调用的方法名
  params?: unknown;       // 方法参数
  expectFinal?: boolean;  // 等待最终响应
  timeoutMs?: number;     // 超时
  clientName?: GatewayClientName;
  clientDisplayName?: string;
  clientVersion?: string;
  platform?: string;
  mode?: GatewayClientMode;
  deviceIdentity?: DeviceIdentity | null;
  instanceId?: string;
  minProtocol?: number;
  maxProtocol?: number;
  requiredMethods?: string[];
};
```

### 4.2 调用类型

```typescript
// 作用域调用（需要显式权限）
export type CallGatewayScopedOptions = CallGatewayBaseOptions & {
  scopes: OperatorScope[];
};

// CLI 调用（可选权限）
export type CallGatewayCliOptions = CallGatewayBaseOptions & {
  scopes?: OperatorScope[];
};
```

### 4.3 Client Modes

```typescript
// GATEWAY_CLIENT_MODES 定义了不同的客户端模式
type GatewayClientMode = /* 客户端模式枚举 */;

// GATEWAY_CLIENT_NAMES 定义了客户端名称
type GatewayClientName = /* 客户端名称枚举 */;
```

---

## 五、认证系统

> 文件：`src/gateway/auth.ts`

### 5.1 认证流程

```typescript
// 认证核心流程
interface AuthResult {
  success: boolean;
  token?: string;
  error?: string;
}

async function authenticate(
  credentials: Credentials,
  config: AuthConfig
): Promise<AuthResult>;
```

### 5.2 认证模式策略

> 文件：`src/gateway/auth-mode-policy.ts`

```typescript
// 不同的认证模式
type AuthMode =
  | "token"        // Token 认证
  | "password"    // 密码认证
  | "device"       // 设备认证
  | "anonymous";   // 匿名
```

### 5.3 凭证优先级

> 文件：`src/gateway/auth-token-resolution.ts`

```typescript
// 凭证解析优先级
type GatewayCredentialPrecedence = [
  "env",           // 环境变量
  "config",        // 配置文件
  "interactive",  // 交互式输入
  "keychain",      // 系统密钥链
];
```

### 5.4 限流

> 文件：`src/gateway/auth-rate-limit.ts`

```typescript
interface RateLimitConfig {
  maxAttempts: number;
  windowMs: number;
  lockoutMs: number;
}
```

---

## 六、凭证管理

> 文件：`src/gateway/credentials.ts`

### 6.1 凭证类型

```typescript
type GatewayCredentialMode =
  | "env"           // 环境变量
  | "config"        // 配置文件
  | "interactive"  // 交互式
  | "secret";      // 密钥管理
```

### 6.2 凭证解析

```typescript
// 从多种来源解析凭证
export async function resolveGatewayCredentials(
  options: CallGatewayBaseOptions
): Promise<GatewayCredentials>;
```

### 6.3 密钥存储

> 文件：`src/gateway/credentials-secret-inputs.ts`

```typescript
// 密钥输入处理
export function resolveGatewayCredentialsWithSecretInputs(
  secretInputs: SecretInputs,
  config: OpenClawConfig
): Promise<GatewayCredentials>;
```

---

## 七、协议层

> 文件：`src/gateway/protocol/`

### 7.1 协议版本

```typescript
import { PROTOCOL_VERSION } from "./protocol/index.js";

// 协议版本检查
const minProtocol: number = /* 最小支持版本 */;
const maxProtocol: number = /* 最大支持版本 */;
```

### 7.2 方法权限范围

> 文件：`src/gateway/method-scopes.ts`

```typescript
// 操作员权限范围
type OperatorScope =
  | "gateway:read"     // 读取网关状态
  | "gateway:write"   // 修改网关配置
  | "channel:manage"   // 管理渠道
  | "session:read"     // 读取会话
  | "session:write";   // 修改会话

// 解析方法需要的最小权限
function resolveLeastPrivilegeOperatorScopesForMethod(
  method: string
): OperatorScope[];

// 判断方法是否属于某权限类
function isGatewayMethodClassified(
  method: string,
  scope: OperatorScope
): boolean;
```

---

## 八、会话管理

### 8.1 会话 Key 解析

> 文件：`src/config/sessions/main-session.ts`

```typescript
// 解析会话 Key
function resolveAgentIdFromSessionKey(sessionKey: string): string;
function resolveMainSessionKey(agentId: string): string;
function resolveAgentMainSessionKey(agentId: string): string;
```

### 8.2 会话存储

> 文件：`src/config/sessions/store.ts`

```typescript
// 加载会话存储
function loadSessionStore(
  storePath: string,
  options?: { skipCache?: boolean }
): SessionStore;

// 更新会话存储
function updateSessionStore(
  storePath: string,
  updater: (store: SessionStore) => void
): void;
```

### 8.3 会话类型

> 文件：`src/config/sessions/types.ts`

```typescript
interface SessionEntry {
  sessionKey: string;
  agentId: string;
  createdAt: number;
  updatedAt: number;
  lastActiveAt: number;
  messages: Message[];
  metadata?: Record<string, unknown>;
}
```

---

## 九、连接详情

> 文件：`src/gateway/connection-details.ts`

```typescript
interface GatewayConnectionDetails {
  url: string;
  port: number;
  protocol: "http" | "https" | "ws" | "wss";
  auth?: {
    token?: string;
    username?: string;
  };
  tls?: {
    enabled: boolean;
    fingerprint?: string;
  };
}

// 构建连接详情（带域名解析）
function buildGatewayConnectionDetailsWithResolvers(
  config: OpenClawConfig
): GatewayConnectionDetails;
```

---

## 十、渠道健康监控

> 文件：`src/gateway/channel-health-monitor.ts`

### 10.1 健康检查

```typescript
interface ChannelHealth {
  channelId: string;
  status: "healthy" | "degraded" | "down";
  lastCheckAt: number;
  latencyMs?: number;
  errorRate?: number;
}

// 监控所有渠道的健康状态
async function monitorChannelHealth(): Promise<ChannelHealth[]>;
```

### 10.2 健康策略

> 文件：`src/gateway/channel-health-policy.ts`

```typescript
interface HealthPolicy {
  maxLatencyMs: number;
  maxErrorRate: number;
  checkIntervalMs: number;
  recoveryIntervalMs: number;
}

// 默认策略
const DEFAULT_HEALTH_POLICY: HealthPolicy = {
  maxLatencyMs: 5000,
  maxErrorRate: 0.05,
  checkIntervalMs: 60000,
  recoveryIntervalMs: 300000,
};
```

---

## 十一、控制平面审计

> 文件：`src/gateway/control-plane-audit.ts`

### 11.1 审计日志

```typescript
interface AuditEvent {
  timestamp: number;
  clientId: string;
  method: string;
  params: unknown;
  result: "success" | "failure";
  error?: string;
  durationMs: number;
}

// 记录审计事件
function recordAuditEvent(event: AuditEvent): void;
```

### 11.2 敏感信息过滤

```typescript
// 过滤敏感参数
function sanitizeAuditParams(
  method: string,
  params: Record<string, unknown>
): Record<string, unknown>;
```

---

## 十二、启动流程

```
Gateway 启动
    │
    ├─► 加载配置（loadConfig）
    │      │
    │      ├─► 解析环境变量
    │      ├─► 读取配置文件
    │      └─► 验证配置 Schema
    │
    ├─► 初始化凭证（resolveGatewayCredentials）
    │      │
    │      ├─► 检查环境变量
    │      ├─► 读取密钥链
    │      └─► 解析 Token
    │
    ├─► 连接详情（buildGatewayConnectionDetailsWithResolvers）
    │      │
    │      ├─► 解析 Gateway URL
    │      ├─► TLS 配置
    │      └─► 协议版本协商
    │
    ├─► 启动引导（boot.ts）
    │      │
    │      └─► 执行 BOOT.md（可选）
    │
    ├─► 渠道健康检查（channel-health-monitor）
    │
    └─► Gateway 就绪
```

---

## 下一步

下一篇：[03 - Plugin SDK：扩展机制与公开 API](./03-plugin-sdk.md)，深入插件 SDK 的架构设计与公开接口。

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*