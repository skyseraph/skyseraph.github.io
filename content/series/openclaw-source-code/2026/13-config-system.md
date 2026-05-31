---
title: "OpenClaw源码剖析 #13 · 配置系统：Schema 与验证"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 14
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、配置系统定位

OpenClaw 采用 **Zod** 作为配置 Schema 定义和验证的核心，提供类型安全的配置加载、验证和环境变量替换。

```
┌─────────────────────────────────────────────────────────────┐
│                    Config System                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                  OpenClawSchema                       │ │
│  │  env · auth · models · agents · channels · plugins   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │   Zod Schema   │  │  Env Vars      │  │  Includes   │ │
│  │   validation   │  │  ${VAR} 替换    │  │  $include   │ │
│  └────────────────┘  └────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件 | 职责 |
|:---|:---|
| `src/config/zod-schema.ts` | 主 Zod Schema 定义 |
| `src/config/validation.ts` | 配置验证入口 |
| `src/config/io.ts` | 配置加载、写入 |
| `src/config/types.openclaw.ts` | TypeScript 类型 |
| `src/config/env-vars.ts` | 环境变量收集 |
| `src/config/env-substitution.ts` | `${VAR}` 替换 |
| `src/config/includes.ts` | `$include` 指令 |
| `src/plugin-sdk/config-schema.ts` | 插件 Config Schema 构建器 |
| `src/channels/plugins/config-schema.ts` | Channel Config Schema |
| `src/plugins/schema-validator.ts` | AJV JSON Schema 验证 |

---

## 三、OpenClawSchema

> 文件：`src/config/zod-schema.ts`

### 3.1 主 Schema 结构

```typescript
export const OpenClawSchema = z.object({
  $schema: z.string().optional(),
  meta: z.object({...}).strict().optional(),
  env: z.object({...}).catchall(z.string()).optional(),
  wizard: z.object({...}).strict().optional(),
  diagnostics: z.object({...}).strict().optional(),
  logging: z.object({...}).strict().optional(),
  browser: z.object({...}).strict().optional(),
  ui: z.object({...}).strict().optional(),
  secrets: SecretsConfigSchema,
  auth: z.object({...}).strict().optional(),
  acp: z.object({...}).strict().optional(),
  models: ModelsConfigSchema,
  agents: AgentsSchema,
  tools: ToolsSchema,
  bindings: BindingsSchema,
  channels: ChannelsSchema,
  cron: z.object({...}).strict().optional(),
  hooks: z.object({...}).strict().optional(),
  gateway: z.object({...}).strict().optional(),
  memory: MemorySchema,
  mcp: McpConfigSchema,
  skills: z.object({...}).strict().optional(),
  plugins: z.object({...}).strict().optional(),
  proxy: ProxyConfigSchema,
  // ...
}).strict()
.superRefine((cfg, ctx) => { /* 跨字段验证 */ });
```

### 3.2 子模块 Schema

| Schema | 职责 |
|:---|:---|
| `zod-schema.agents.ts` | Agent 定义 |
| `zod-schema.providers.ts` | Channel Provider |
| `zod-schema.core.ts` | 核心类型（secrets、models 等） |
| `zod-schema.hooks.ts` | Hooks 配置 |
| `zod-schema.session.ts` | Session 设置 |

---

## 四、配置类型

> 文件：`src/config/types.openclaw.ts`

```typescript
export type OpenClawConfig = {
  $schema?: string;
  meta?: { lastTouchedVersion?: string; lastTouchedAt?: string; };
  env?: { shellEnv?: {...}; vars?: Record<string, string>; [key: string]: ... };
  auth?: AuthConfig;
  acp?: AcpConfig;
  browser?: BrowserConfig;
  ui?: { seamColor?: string; assistant?: {...}; };
  secrets?: SecretsConfig;
  skills?: SkillsConfig;
  plugins?: PluginsConfig;
  models?: ModelsConfig;
  agents?: AgentsConfig;
  tools?: ToolsConfig;
  bindings?: AgentBinding[];
  channels?: ChannelsConfig;
  cron?: CronConfig;
  hooks?: HooksConfig;
  gateway?: GatewayConfig;
  memory?: MemoryConfig;
  mcp?: McpConfigSchema;
  proxy?: ProxyConfig;
};
```

### 4.1 Branded Config States

```typescript
export type SourceConfig = BrandedConfigState<"source">;
export type ResolvedSourceConfig = BrandedConfigState<"resolved-source">;
export type RuntimeConfig = BrandedConfigState<"runtime">;
```

---

## 五、验证流程

### 5.1 validateConfigObjectRaw

> `src/config/validation.ts`

```typescript
export function validateConfigObjectRaw(
  raw: unknown,
  opts?: { touchedPaths?: ReadonlyArray<ReadonlyArray<string>> },
): { ok: true; config: OpenClawConfig } | { ok: false; issues: ConfigValidationIssue[] }
```

验证步骤：
1. 剥离废弃键
2. 检查 Policy 问题（SecretRef surface 验证）
3. 运行旧版配置检测
4. Zod Schema 解析（`OpenClawSchema.safeParse()`）
5. 合并 Policy 和 Schema 问题
6. 验证 Agent 目录唯一性
7. 验证身份头像
8. 验证 Gateway Tailscale 绑定配置

### 5.2 验证层级

```typescript
// 原始验证（无默认值）
validateConfigObjectRaw()

// 应用运行时默认值后验证
validateConfigObject()

// 完整验证（含插件 Schema）
validateConfigObjectWithPlugins()

// 插件验证（无默认值）
validateConfigObjectRawWithPlugins()
```

---

## 六、环境变量

### 6.1 环境变量收集

> `src/config/env-vars.ts`

```typescript
// 收集运行时环境变量
export function collectConfigRuntimeEnvVars(cfg?: OpenClawConfig): Record<string, string>

// 收集服务环境变量
export function collectConfigServiceEnvVars(cfg?: OpenClawConfig): Record<string, string>

// 创建配置运行时环境
export function createConfigRuntimeEnv(
  cfg: OpenClawConfig,
  baseEnv: NodeJS.ProcessEnv = process.env
): NodeJS.ProcessEnv

// 应用配置环境变量
export function applyConfigEnvVars(cfg: OpenClawConfig, env?: NodeJS.ProcessEnv): void
```

### 6.2 环境变量替换

> `src/config/env-substitution.ts`

支持 `${VAR}` 和 `${VAR:-default}` 语法：

```typescript
export function resolveConfigEnvVars(
  raw: string,
  env: NodeJS.ProcessEnv,
): string

// 示例
"api-key: ${OPENAI_API_KEY}"  // 标准替换
"api-key: ${API_KEY:-default}" // 带默认值
```

---

## 七、Includes 系统

> `src/config/includes.ts`

### 7.1 $include 指令

```typescript
export const INCLUDE_KEY = "$include";
export const MAX_INCLUDE_DEPTH = 10;
export const MAX_INCLUDE_FILE_BYTES = 2 * 1024 * 1024;
```

### 7.2 使用方式

```json
{
  "$include": "./base.json5"
}
```

```json
{
  "$include": ["./a.json5", "./b.json5"]
}
```

### 7.3 合并规则

| 类型 | 规则 |
|:---|:---|
| Array | 拼接 |
| Object | 递归合并 |
| Primitive | 源覆盖 |

---

## 八、插件配置 Schema

### 8.1 buildPluginConfigSchema

> `src/plugin-sdk/config-schema.ts`

```typescript
import { z } from "zod";
import { buildPluginConfigSchema } from "openclaw/plugin-sdk/config-schema";

const MyPluginConfigSchema = z.object({
  enabled: z.boolean().optional(),
  apiKey: z.string().optional(),
  models: z.array(z.string()).optional(),
});

export const myPluginConfig = buildPluginConfigSchema(MyPluginConfigSchema);
```

### 8.2 Channel Config Schema

> `src/channels/plugins/config-schema.ts`

```typescript
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/config-schema";

export const telegramChannelConfigSchema = buildChannelConfigSchema(TelegramConfigSchema, {
  uiHints: telegramChannelConfigUiHints,
});
```

### 8.3 完整示例

> `extensions/qqbot/src/config-schema.ts`

```typescript
const QQBotAccountSchema = z.object({
  enabled: z.boolean().optional(),
  name: z.string().optional(),
  appId: z.string().optional(),
  clientSecret: buildSecretInputSchema().optional(),
  allowFrom: AllowFromListSchema,
  groupPolicy: QQBotGroupPolicySchema,
  markdownSupport: z.boolean().optional(),
  streaming: QQBotStreamingSchema,
  execApprovals: QQBotExecApprovalsSchema,
}).passthrough();

export const QQBotConfigSchema = QQBotAccountSchema.extend({
  stt: QQBotSttSchema,
  accounts: z.object({}).catchall(QQBotAccountSchema.passthrough()).optional(),
  defaultAccount: z.string().optional(),
}).passthrough();
```

---

## 九、JSON Schema 验证

### 9.1 AJV 验证器

> `src/plugins/schema-validator.ts`

```typescript
import { validateJsonSchemaValue } from "openclaw/plugin-sdk/schema-validator";

const result = validateJsonSchemaValue({
  schema: jsonSchemaObject,
  cacheKey: "my-plugin-config",
  value: configValue,
  applyDefaults: true,
});
```

### 9.2 Zod to JSON Schema

```typescript
const jsonSchema = OpenClawSchema.toJSONSchema({
  target: "draft-07",
  unrepresentable: "any",
});
```

---

## 十、配置文件格式

### 10.1 支持的格式

| 格式 | 说明 |
|:---|:---|
| JSON5 | 主格式（支持注释、尾逗号） |
| JSON | 标准 JSON |
| 通过 `$include` | 可引用外部文件 |

### 10.2 示例配置

```json5
{
  // OpenClaw 配置
  $schema: "./openclaw-schema.json",
  $include: "./local.json5",
  
  env: {
    OPENAI_API_KEY: "${OPENAI_API_KEY}",
  },
  
  models: {
    providers: {
      openai: {
        apiKey: "${OPENAI_API_KEY:-}",
      },
    },
  },
  
  agents: {
    main: {
      model: "openai/gpt-4o",
    },
  },
  
  channels: {
    telegram: {
      enabled: true,
      botToken: "${TELEGRAM_BOT_TOKEN}",
    },
  },
}
```

---

## 十一、设计权衡

### 11.1 Zod vs JSON Schema

OpenClaw 内部使用 Zod，导出时转换为 JSON Schema 以支持：
- Plugin 配置验证
- UI Schema 生成
- 外部工具集成

### 11.2 验证时机

| 函数 | 何时调用 |
|:---|:---|
| `validateConfigObjectRaw` | 配置加载时（无默认值） |
| `validateConfigObject` | 应用默认值后 |
| `validateConfigObjectWithPlugins` | 完整验证（含插件） |

### 11.3 环境变量安全

未解析的引用保持原样，避免泄露敏感信息。

---

## 下一步

篇目 13 完成，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 14 | [安全机制：Auth 与权限](./14-security-auth.md) | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*