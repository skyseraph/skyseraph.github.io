---
title: "OpenClaw源码剖析 #10 · Extension 开发：Channel 篇"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 11
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Channel 扩展定位

Channel 扩展是 OpenClaw 的**消息渠道接入层**——通过插件机制接入 30+ 消息平台，对上提供统一的 `ChannelPlugin` 接口。

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Core                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Gateway     │  │  Agent RT   │  │   Memory    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │              ChannelPlugin Interface               │    │
│  │  id · meta · capabilities · config · setup        │    │
│  │  outbound · gateway · lifecycle                    │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│               extensions/channels/                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │telegram/│  │discord/ │  │whatsapp/│  │  slack/  │ ...  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件 | 职责 |
|:---|:---|
| `src/channels/plugins/types.plugin.ts` | ChannelPlugin 接口定义 |
| `src/channels/plugins/types.core.ts` | 核心类型（Capabilities、Meta） |
| `src/channels/plugins/types.adapters.ts` | 各 Adapter 接口 |
| `src/channels/plugins/config-schema.ts` | 配置 Schema 构建器 |
| `src/channels/plugins/setup-wizard-types.ts` | Setup Wizard 类型 |
| `src/plugin-sdk/core.ts` | `createChatChannelPlugin()` 辅助函数 |
| `extensions/channels/<name>/` | 各 Channel 插件实现 |

---

## 三、ChannelPlugin 接口

> 文件：`src/channels/plugins/types.plugin.ts`

### 3.1 核心字段

```typescript
export type ChannelPlugin<
  ResolvedAccount = any,
  Probe = unknown,
  Audit = unknown,
> = {
  // 必填字段
  id: ChannelId;                    // 唯一标识，如 "telegram"
  meta: ChannelMeta;                // 用户可见的标签、文档路径
  capabilities: ChannelCapabilities; // 静态能力标志
  config: ChannelConfigAdapter<ResolvedAccount>;  // 账号配置读写

  // 生命周期
  setup?: ChannelSetupAdapter;      // 账号配置应用
  gateway?: ChannelGatewayAdapter<ResolvedAccount>;  // 运行时生命周期
  lifecycle?: ChannelLifecycleAdapter;  // 配置变更回调

  // 安全与群组
  security?: ChannelSecurityAdapter<ResolvedAccount>;
  groups?: ChannelGroupAdapter;
  mentions?: ChannelMentionAdapter;
  allowlist?: ChannelAllowlistAdapter;

  // 消息收发
  outbound?: ChannelOutboundAdapter;
  status?: ChannelStatusAdapter<ResolvedAccount, Probe, Audit>;
  messaging?: ChannelMessagingAdapter;
  streaming?: ChannelStreamingAdapter;
  threading?: ChannelThreadingAdapter;

  // 配对与认证
  pairing?: ChannelPairingAdapter;
  auth?: ChannelAuthAdapter;
  approvalCapability?: ChannelApprovalCapability;
  elevated?: ChannelElevatedAdapter;

  // 命令与工具
  commands?: ChannelCommandAdapter;
  agentTools?: ChannelAgentToolFactory | ChannelAgentTool[];

  // Wizard
  setupWizard?: ChannelSetupWizard | ChannelSetupWizardAdapter;

  // 其他
  secrets?: ChannelSecretsAdapter;
  doctor?: ChannelDoctorAdapter;
  agentPrompt?: ChannelAgentPromptAdapter;
  directory?: ChannelDirectoryAdapter;
  resolver?: ChannelResolverAdapter;
  actions?: ChannelMessageActionAdapter;
  bindings?: ChannelConfiguredBindingProvider;
  conversationBindings?: ChannelConversationBindingSupport;
};
```

---

## 四、ChannelCapabilities

> 文件：`src/channels/plugins/types.core.ts`

### 4.1 能力标志

```typescript
export type ChannelCapabilities = {
  chatTypes: Array<ChatType | "thread">;  // "direct" | "group" | "channel" | "thread"
  polls?: boolean;                         // 支持发送/创建投票
  reactions?: boolean;                     // 支持发送反应
  edit?: boolean;                         // 支持编辑消息
  unsend?: boolean;                      // 支持删除消息
  reply?: boolean;                        // 支持回复消息
  effects?: boolean;                      // 支持消息效果
  groupManagement?: boolean;               // 支持管理群组设置
  threads?: boolean;                      // 支持线程对话
  media?: boolean;                         // 支持发送图片/视频/音频
  tts?: {                                  // 文本转语音支持
    voice?: ChannelTtsVoiceDeliveryCapabilities;
  };
  nativeCommands?: boolean;               // 支持原生渠道命令
  blockStreaming?: boolean;                // 应阻止流式响应
};
```

### 4.2 Telegram 示例

```typescript
capabilities: {
  chatTypes: ["direct", "group", "channel", "thread"],
  reactions: true,
  threads: true,
  media: true,
  tts: { voice: { synthesisTarget: "voice-note" } },
  polls: true,
  nativeCommands: true,
  blockStreaming: true,
},
```

---

## 五、文件结构

### 5.1 标准 Channel 扩展结构

```
extensions/<channel-id>/
├── openclaw.plugin.json       # Plugin manifest
├── package.json               # 包定义
├── index.ts                   # 主入口（defineChannelPluginEntry）
├── setup-entry.ts             # Setup 入口（defineSetupPluginEntry）
├── channel-plugin-api.ts      # 插件 API 重导出
├── runtime-api.ts             # 运行时 API 定义
└── src/
    ├── channel.ts             # 主插件定义
    ├── shared.ts              # 共享基类和配置适配器
    ├── setup-surface.ts       # Setup Wizard 定义
    ├── setup-core.ts          # Setup Adapter 实现
    ├── config-schema.ts       # Zod 配置 Schema
    ├── config-ui-hints.ts     # 配置 UI 提示
    ├── accounts.ts            # 账号解析和列表
    ├── account-inspect.ts     # 账号检查工具
    ├── outbound-adapter.ts    # 出站消息适配器
    ├── channel-actions.ts    # 消息操作（发送、反应等）
    ├── monitor.ts             # 运行时监控/启动逻辑
    ├── probe.ts               # 健康检查实现
    ├── doctor.ts              # 配置修复
    ├── security.ts            # 安全适配器
    ├── runtime.ts             # 运行时访问器
    └── send.ts                # 底层发送函数
```

### 5.2 核心创建函数

```typescript
// src/plugin-sdk/core.ts
import {
  createChatChannelPlugin,
  createChannelPluginBase,
  defineChannelPluginEntry,
  defineSetupPluginEntry,
} from "openclaw/plugin-sdk/core";
```

---

## 六、Config Schema

### 6.1 buildChannelConfigSchema

> 文件：`src/channels/plugins/config-schema.ts`

```typescript
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/config-schema";
import { z } from "zod";

// 定义 Channel 特定的配置 Schema
export const <Channel>ConfigSchema = z.object({
  enabled: z.boolean().optional(),
  botToken: z.string().optional(),
  // ... 更多字段
});

// 构建完整的 Channel 配置 Schema
export const <Channel>ChannelConfigSchema = buildChannelConfigSchema(
  <Channel>ConfigSchema,
  {
    uiHints: <channel>ConfigUiHints,
  }
);
```

### 6.2 配置适配器

```typescript
// shared.ts
import { createScopedChannelConfigAdapter } from "openclaw/plugin-sdk/channel-core";

export const <channel>ConfigAdapter = createScopedChannelConfigAdapter({
  scope: CHANNEL_ID,
  schema: <Channel>ChannelConfigSchema,
  read: (cfg, accountId) => {/* 读取配置 */},
  write: (cfg, accountId, updates) => {/* 写入配置 */},
});
```

---

## 七、Setup Wizard

### 7.1 ChannelSetupWizard 结构

> 文件：`src/channels/plugins/setup-wizard-types.ts`

```typescript
export type ChannelSetupWizard = {
  channel: string;
  status: ChannelSetupWizardStatus;
  introNote?: ChannelSetupWizardNote;
  envShortcut?: ChannelSetupWizardEnvShortcut;
  credentials: ChannelSetupWizardCredential[];
  textInputs?: ChannelSetupWizardTextInput[];
  finalize?: ChannelSetupWizardFinalize;
  completionNote?: ChannelSetupWizardNote;
  dmPolicy?: ChannelSetupDmPolicy;
  allowFrom?: ChannelSetupWizardAllowFrom;
  groupAccess?: ChannelSetupWizardGroupAccess;
  disable?: (cfg: OpenClawConfig) => OpenClawConfig;
};
```

### 7.2 示例

```typescript
// setup-surface.ts
export const telegramSetupWizard: ChannelSetupWizard = {
  channel: "telegram",
  status: createStandardChannelSetupStatus({...}),
  credentials: [{
    inputKey: "token",
    providerHint: "telegram",
    credentialLabel: "Telegram bot token",
    preferredEnvVar: "TELEGRAM_BOT_TOKEN",
    helpTitle: "Telegram bot token",
    helpLines: TELEGRAM_TOKEN_HELP_LINES,
  }],
  allowFrom: createAllowFromSection({...}),
  dmPolicy: telegramSetupDmPolicy,
};
```

---

## 八、Outbound 适配器

### 8.1 ChannelOutboundAdapter

> 文件：`src/channels/plugins/outbound.types.ts`

```typescript
export type ChannelOutboundAdapter = {
  deliveryMode: "direct" | "gateway" | "hybrid";

  // 消息分块
  chunker?: (text: string, limit: number, ctx?: ChannelOutboundChunkContext) => string[];
  textChunkLimit?: number;

  // 发送方法
  sendPayload?: (ctx: ChannelOutboundPayloadContext) => Promise<OutboundDeliveryResult>;
  sendText?: (ctx: ChannelOutboundContext) => Promise<OutboundDeliveryResult>;
  sendMedia?: (ctx: ChannelOutboundContext) => Promise<OutboundDeliveryResult>;
  sendPoll?: (ctx: ChannelPollContext) => Promise<ChannelPollResult>;

  //钩子
  beforeDeliverPayload?: (ctx: ChannelOutboundPayloadContext) => Promise<void>;
  afterDeliverPayload?: (ctx: ChannelOutboundPayloadContext) => Promise<void>;
  renderPresentation?: (payload: ReplyPayload, ctx: ChannelOutboundContext) => Promise<ReplyPayload>;
  sanitizeText?: (text: string) => string;
};
```

### 8.2 Telegram 示例

```typescript
// outbound-adapter.ts
export const telegramOutbound: ChannelOutboundAdapter = {
  deliveryMode: "direct",
  chunker: markdownToTelegramHtmlChunks,
  textChunkLimit: 4000,
  sendPayload: async ({ cfg, to, payload, ... }) => {
    // 渲染呈现，发送媒体序列，返回结果
  },
};
```

---

## 九、完整实现示例

### 9.1 index.ts（插件入口）

```typescript
// index.ts
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/core";
import { <channel>Plugin } from "./src/channel.js";

export default defineChannelPluginEntry({
  id: CHANNEL_ID,
  name: "<channel>",
  description: "OpenClaw <channel> channel plugin",
  plugin: <channel>Plugin,
});
```

### 9.2 setup-entry.ts（Setup 入口）

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/core";
import { <channel>Plugin } from "./src/channel.js";

export default defineSetupPluginEntry(<channel>Plugin);
```

### 9.3 shared.ts（共享基类）

```typescript
// src/shared.ts
import { createChatChannelPlugin, createChannelPluginBase } from "openclaw/plugin-sdk/channel-core";

export const <channel>ConfigAdapter = createScopedChannelConfigAdapter({...});

export function create<Channel>PluginBase(params) {
  return createChannelPluginBase({
    id: CHANNEL_ID,
    meta: { ...getChatChannelMeta(CHANNEL_ID) },
    setupWizard: params.setupWizard,
    capabilities: {
      chatTypes: ["direct", "group"],
      media: true,
      reactions: true,
    },
    config: { ...<channel>ConfigAdapter, ... },
    setup: params.setup,
  });
}
```

### 9.4 channel.ts（主插件）

```typescript
// src/channel.ts
export const <channel>Plugin = createChatChannelPlugin({
  base: {
    ...create<Channel>PluginBase({ setupWizard, setup }),
  },
  outbound: {
    base: {
      deliveryMode: "direct",
      sendText: async (ctx) => {/* 发送文本 */},
      sendMedia: async (ctx) => {/* 发送媒体 */},
    },
  },
  gateway: {
    startAccount: async (ctx) => {/* 启动监控 */},
    stopAccount: async (ctx) => {/* 停止监控 */},
  },
  security: <channel>SecurityAdapter,
});
```

### 9.5 package.json

```json
{
  "name": "@openclaw/<channel>",
  "version": "2026.4.25",
  "type": "module",
  "dependencies": {
    // channel-specific deps
  },
  "devDependencies": {
    "@openclaw/plugin-sdk": "workspace:*"
  },
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "<channel-id>",
      "label": "<Channel Name>",
      "selectionLabel": "<Channel Name> (Bot API)"
    }
  }
}
```

---

## 十、Gateway 适配器

### 10.1 ChannelGatewayAdapter

```typescript
export type ChannelGatewayAdapter<ResolvedAccount> = {
  startAccount(ctx: ChannelGatewayStartAccountContext): Promise<void>;
  stopAccount(ctx: ChannelGatewayStopAccountContext): Promise<void>;
  restartAccount?(ctx: ChannelGatewayRestartAccountContext): Promise<void>;
};
```

### 10.2 启动监控模式

Channel 实现通常在 `startAccount` 中启动：
- **长轮询**：定期拉取新消息
- **Webhook**：注册回调 URL 接收消息

```typescript
gateway: {
  startAccount: async ({ config, accountId, runtime }) => {
    const channelRuntime = await load<Channel>ChannelRuntime();
    await channelRuntime.startPolling({ config, accountId });
  },
  stopAccount: async ({ config, accountId }) => {
    const channelRuntime = await load<Channel>ChannelRuntime();
    await channelRuntime.stopPolling({ accountId });
  },
},
```

---

## 十一、WhatsApp 特殊示例（QR 登录）

WhatsApp 使用 QR 码登录而非 Token：

```typescript
export const whatsappPlugin = createChatChannelPlugin<ResolvedWhatsAppAccount>({
  base: {
    ...createWhatsAppPluginBase({
      setupWizard: whatsappSetupWizardProxy,
      setup: whatsappSetupAdapter,
      isConfigured: async (account) => {
        const channelRuntime = await loadWhatsAppChannelRuntime();
        return (await channelRuntime.readWebAuthState(account.authDir)) === "linked";
      },
    }),
    agentTools: () => [createWhatsAppLoginTool()],
  },
  auth: {
    login: async ({ cfg, accountId, runtime, verbose }) => {
      // WhatsApp 使用 QR 码登录流程
    },
  },
  pairing: { idLabel: "whatsappSenderId" },
});
```

---

## 十二、设计权衡

### 12.1 Adapter 模式

ChannelPlugin 使用大量 Adapter 接口，允许插件选择性地实现功能：

```typescript
// 每个 Adapter 都是可选的
setup?: ChannelSetupAdapter;
pairing?: ChannelPairingAdapter;
security?: ChannelSecurityAdapter;
// ...
```

简单渠道（如 IRC）只需实现核心接口，复杂渠道（如 Discord）可以实现全套。

### 12.2 createChatChannelPlugin 组合模式

```typescript
createChatChannelPlugin({
  base: { /* 通用基础 */ },
  outbound: { /* 出站消息 */ },
  gateway: { /* 运行时生命周期 */ },
  security: { /* 安全策略 */ },
});
```

组合模式允许复用基础实现并选择性覆盖。

### 12.3 Config Schema 分离

- `configSchema`：声明式配置定义（用于 UI 生成）
- `config`：运行时配置访问

这种分离允许 Setup UI 在不加载运行时的情况下渲染配置表单。

---

## 下一步

篇目 10 完成，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 11 | [Extension 开发：Skill 篇](./11-extension-skill.md) | 开发新 Skill |
| 12 | [测试策略：单元/集成/E2E](./12-testing-strategy.md) | Vitest + E2E |
| 13 | [配置系统：Schema 与验证](./13-config-system.md) | 配置管理 |
| 14 | [安全机制：Auth 与权限](./14-security-auth.md) | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*