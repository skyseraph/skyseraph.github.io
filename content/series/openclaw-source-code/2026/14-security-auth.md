---
title: "OpenClaw源码剖析 #14 · 安全机制：Auth 与权限"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 15
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、安全系统定位

OpenClaw 安全系统采用分层设计，区分认证（Authentication）与授权（Authorization），覆盖 Gateway、Provider、Channel 三大维度。

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Architecture                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    Gateway Auth                       │ │
│  │  token · password · trusted-proxy · device-token     │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    Auth Profiles                      │ │
│  │  api_key · token · oauth · SecretRef                  │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Channel Security                         │ │
│  │  dm-policy · allowlist · pairing                      │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、Gateway 认证

### 2.1 认证模式

> `src/gateway/auth-resolve.ts`

```typescript
export type ResolvedGatewayAuthMode = "none" | "token" | "password" | "trusted-proxy";
```

认证模式解析优先级：
1. 显式覆盖（最高）
2. 配置指定模式
3. 有密码配置 → `password`
4. 有 Token 配置 → `token`
5. 默认 → `token`

### 2.2 认证结果

> `src/gateway/auth.ts`

```typescript
export type GatewayAuthResult = {
  ok: boolean;
  method?:
    | "none"
    | "token"
    | "password"
    | "tailscale"
    | "device-token"
    | "bootstrap-token"
    | "trusted-proxy";
  user?: string;
  reason?: string;
  rateLimited?: boolean;
  retryAfterMs?: number;
};
```

### 2.3 认证流程

```typescript
// authorizeGatewayConnect()
export async function authorizeGatewayConnect(
  params: AuthorizeGatewayConnectParams,
): Promise<GatewayAuthResult> {
  // 1. trusted-proxy 模式（反向代理头标识）
  // 2. none 模式（开放访问）
  // 3. Tailscale 头认证（WS Control UI）
  // 4. Token 认证（共享密钥）
  // 5. Password 认证（共享密码）
  // 6. 未授权
}
```

### 2.4 Token 解析

> `src/gateway/auth-token-resolution.ts`

```typescript
export async function resolveGatewayAuthToken(params: {
  cfg: OpenClawConfig;
  env: NodeJS.ProcessEnv;
  explicitToken?: string;
  envFallback?: GatewayAuthTokenEnvFallback;
}): Promise<{
  token?: string;
  source?: GatewayAuthTokenResolutionSource;
  secretRefConfigured: boolean;
}>
```

**Token 来源优先级**：
1. `explicit` — 直接提供
2. `config` — 配置文件
3. `secretRef` — SecretRef 解析器
4. `env` — 环境变量回退

---

## 三、Auth Profiles

### 3.1 凭证类型

> `src/agents/auth-profiles/types.ts`

```typescript
export type AuthProfileCredential =
  | ApiKeyCredential
  | TokenCredential
  | OAuthCredential;

export type ApiKeyCredential = {
  type: "api_key";
  provider: string;
  key?: string;
  keyRef?: SecretRef;
  copyToAgents?: boolean;
  email?: string;
  displayName?: string;
  metadata?: Record<string, string>;
};

export type TokenCredential = {
  type: "token";
  provider: string;
  token?: string;
  tokenRef?: SecretRef;
  expires?: number;
};

export type OAuthCredential = {
  type: "oauth";
  provider: string;
  clientId?: string;
  access: string;
  refresh: string;
  expires: number;
  copyToAgents?: boolean;
};
```

### 3.2 Provider API Key 解析

> `src/plugin-sdk/provider-auth.ts`

```typescript
export async function resolveProviderAuthProfileApiKey(params: {
  provider: string;
  cfg?: OpenClawConfig;
  agentDir?: string;
}): Promise<string | undefined>
```

### 3.3 Auth Profile 存储

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

结构：
```typescript
export type AuthProfileSecretsStore = {
  version: number;
  profiles: Record<string, AuthProfileCredential>;
};

export type AuthProfileStateStore = {
  version: number;
  order?: Record<string, string[]>;     // 每 Agent 的 Profile 顺序覆盖
  lastGood?: Record<string, string>;
  usageStats?: Record<string, ProfileUsageStats>;  // 轮询 + 冷却追踪
};
```

---

## 四、Secret 管理

### 4.1 SecretRef 类型

> `src/config/types.secrets.ts`

```typescript
export type SecretRefSource = "env" | "file" | "exec";

export type SecretRef = {
  source: SecretRefSource;
  provider: string;
  id: string;
};

export type SecretInput = string | SecretRef;
```

**Secret 来源**：
| 来源 | 说明 |
|:---|:---|
| `env` | 环境变量（如 `OPENAI_API_KEY`） |
| `file` | 文件密钥（如挂载的 JSON 配置） |
| `exec` | 外部命令执行（如 Vault CLI） |

### 4.2 时序安全比较

> `src/security/secret-equal.ts`

```typescript
export function safeEqualSecret(
  provided: string | undefined | null,
  expected: string | undefined | null,
): boolean {
  // 使用 crypto.timingSafeEqual + 填充防止时序攻击
  const providedBytes = Buffer.from(provided, "utf8");
  const expectedBytes = Buffer.from(expected, "utf8");
  const byteLength = Math.max(providedBytes.length, expectedBytes.length);
  return (
    timingSafeEqual(
      padSecretBytes(providedBytes, byteLength),
      padSecretBytes(expectedBytes, byteLength),
    ) && providedBytes.length === expectedBytes.length
  );
}
```

---

## 五、Channel 安全策略

### 5.1 DM Policy

> `src/security/dm-policy-shared.ts`

```typescript
export type DmGroupAccessDecision = "allow" | "block" | "pairing";

export const DM_GROUP_ACCESS_REASON = {
  GROUP_POLICY_ALLOWED: "group_policy_allowed",
  GROUP_POLICY_DISABLED: "group_policy_disabled",
  GROUP_POLICY_EMPTY_ALLOWLIST: "group_policy_empty_allowlist",
  GROUP_POLICY_NOT_ALLOWLISTED: "group_policy_not_allowlisted",
  DM_POLICY_OPEN: "dm_policy_open",
  DM_POLICY_DISABLED: "dm_policy_disabled",
  DM_POLICY_ALLOWLISTED: "dm_policy_allowlisted",
  DM_POLICY_PAIRING_REQUIRED: "dm_policy_pairing_required",
} as const;
```

**DM Policy 模式**：
| 模式 | 说明 |
|:---|:---|
| `open` | 允许任何人（allowlist 中 `*` 通配） |
| `allowlist` | 仅允许名单中的用户 |
| `pairing` | 需要配对批准 |
| `disabled` | 阻止所有 DM |

### 5.2 Group Policy

| 模式 | 说明 |
|:---|:---|
| `open` | 所有群成员允许 |
| `allowlist` | 仅允许名单中的群成员 |
| `disabled` | 阻止群组访问 |

### 5.3 AllowFrom 解析

> `src/channels/allow-from.ts`

```typescript
export function mergeDmAllowFromSources(params: {
  allowFrom?: Array<string | number>;
  storeAllowFrom?: Array<string | number>;
  dmPolicy?: string;
}): string[]

export function resolveGroupAllowFromSources(params: {
  allowFrom?: Array<string | number>;
  groupAllowFrom?: Array<string | number>;
  fallbackToAllowFrom?: boolean;
}): string[]
```

---

## 六、速率限制

> `src/gateway/auth-rate-limit.ts`

```typescript
export interface AuthRateLimiter {
  check(ip: string | undefined, scope?: string): RateLimitCheckResult;
  recordFailure(ip: string | undefined, scope?: string): void;
  reset(ip: string | undefined, scope?: string): void;
  size(): number;
  prune(): void;
  dispose(): void;
}
```

**限制范围**：
| Scope | 说明 |
|:---|:---|
| `AUTH_RATE_LIMIT_SCOPE_SHARED_SECRET` | Token/Password 尝试 |
| `AUTH_RATE_LIMIT_SCOPE_DEVICE_TOKEN` | Device Token 尝试 |
| `AUTH_RATE_LIMIT_SCOPE_HOOK_AUTH` | Hook 认证 |

**默认配置**：
```typescript
export interface RateLimitConfig {
  maxAttempts?: number;      // 默认: 10
  windowMs?: number;         // 默认: 60_000 (1 分钟)
  lockoutMs?: number;        // 默认: 300_000 (5 分钟)
  exemptLoopback?: boolean;  // 默认: true（豁免回环地址）
  pruneIntervalMs?: number;  // 默认: 60_000
}
```

---

## 七、Trusted Proxy 认证

> `src/gateway/auth.ts`

配置：`gateway.auth.mode: "trusted-proxy"`

```typescript
function authorizeTrustedProxy(params: {
  req?: IncomingMessage;
  trustedProxies?: string[];
  trustedProxyConfig: GatewayTrustedProxyConfig;
}): { user: string } | { reason: string }
```

**检查项**：
1. 源 IP 在 `gateway.trustedProxies` 列表中
2. 必需的头信息存在
3. 从配置的头提取用户身份
4. 用户在 `allowUsers` 白名单中（如配置）
5. 浏览器来源策略通过（Control UI）

---

## 八、Device Token 认证

> `src/gateway/device-auth.ts`

### 8.1 Device Auth Payload

```typescript
export type DeviceAuthPayloadParams = {
  deviceId: string;
  clientId: string;
  clientMode: string;
  role: string;
  scopes: string[];
  signedAtMs: number;
  token?: string | null;
  nonce: string;
};

// 格式: v2|deviceId|clientId|clientMode|role|scopes|signedAtMs|token|nonce
export function buildDeviceAuthPayload(params: DeviceAuthPayloadParams): string

// v3 格式（含平台信息）
export function buildDeviceAuthPayloadV3(params: DeviceAuthPayloadV3Params): string
```

### 8.2 Connect Auth State

```typescript
// src/gateway/server/ws-connection/auth-context.ts
export type ConnectAuthState = {
  authResult: GatewayAuthResult;
  authOk: boolean;
  authMethod: GatewayAuthResult["method"];
  sharedAuthOk: boolean;
  sharedAuthProvided: boolean;
  bootstrapTokenCandidate?: string;
  deviceTokenCandidate?: string;
  deviceTokenCandidateSource?: DeviceTokenCandidateSource;
};
```

**认证决策流程**：
1. 共享密钥认证（token/password）优先
2. Tailscale 头认证（如启用）
3. Bootstrap Token（如存在设备标识）
4. Device Token 作为回退
5. 追踪速率限制

---

## 九、安全审计

> `src/security/audit.ts`

```typescript
export type SecurityAuditSeverity = "info" | "warn" | "critical";

export type SecurityAuditFinding = {
  checkId: string;
  severity: SecurityAuditSeverity;
  title: string;
  detail: string;
  remediation?: string;
};
```

**审计类别**：
- Gateway 配置安全
- Channel 安全契约
- Plugin 信任边界
- 文件系统访问控制
- DM Policy 执行
- 浏览器加固
- Trusted Proxy 配置
- 主机环境安全策略

---

## 十、设计权衡

### 10.1 Fail-Closed 默认

```typescript
// 无认证方法成功时返回未授权
limiter?.recordFailure(ip, rateLimitScope);
return { ok: false, reason: "unauthorized" };
```

### 10.2 回环豁免

```typescript
// 速率限制器默认豁免回环地址
function isExempt(ip: string): boolean {
  return exemptLoopback && isLoopbackAddress(ip);
}
```

### 10.3 SecretRef 解析链

```
Config value → SecretRef → Source (env/file/exec) → Resolved value
```

### 10.4 Auth Profile 缓存

```typescript
// 缓存 Provider auth 检查结果
const authCache = new Map<string, boolean>();
return (provider: string) => {
  const cached = authCache.get(key);
  if (cached !== undefined) return cached;
  // ... 计算并缓存
};
```

---

## 下一步

篇目 14 完成，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*