---
title: "OpenClaw源码剖析 #03 · Plugin SDK：扩展机制与公开 API"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 4
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Plugin SDK 定位

Plugin SDK 是 OpenClaw 的**扩展接入层**——定义扩展如何与核心交互、如何注册能力、如何参与生命周期。

```
┌──────────────────────────────────────────────────────────────┐
│                       OpenClaw Core                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  Gateway   │  │   Agent    │  │  Config    │             │
│  │            │  │  Runtime   │  │            │             │
│  └────────────┘  └────────────┘  └────────────┘             │
│                         ▲                                     │
│                         │ plugin-sdk/*                        │
│                         │ (公开 API)                          │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│              Plugin SDK 公开接口 (src/plugin-sdk/)           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              OpenClawPluginApi                        │   │
│  │  registerProvider() · registerChannel()              │   │
│  │  registerTool() · registerHook() · registerCommand() │   │
│  │  registerHttpRoute() · registerService()             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Plugin Manifest (openclaw.plugin.json)   │   │
│  │  id · configSchema · kind · providers · channels    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                    Extensions                                │
│  extensions/providers/   extensions/channels/   extensions/   │
│  openai/                 telegram/               skill-workshop/│
└─────────────────────────────────────────────────────────────┘
```

**核心原则**（来自 `AGENTS.md`）：

```
Extensions cross into core only via openclaw/plugin-sdk/*,
manifest metadata, injected runtime helpers,
documented barrels (api.ts, runtime-api.ts).
```

扩展只能通过 SDK 公开接口进入核心，禁止直接引用 `src/**`。

---

## 二、模块结构

### 2.1 核心文件

| 文件 | 职责 |
|:---|:---|
| `src/plugin-sdk/index.ts` | SDK 公开导出（barrel file） |
| `src/plugins/types.ts` | `OpenClawPluginApi` 接口定义 |
| `src/plugins/manifest.ts` | `openclaw.plugin.json` 解析 |
| `src/plugins/manifest-types.ts` | Manifest 类型定义 |
| `src/plugins/activation-planner.ts` | 插件激活计划生成器 |
| `src/plugins/bundle-manifest.ts` | 第三方 Bundle 格式支持 |

### 2.2 插件种类（PluginKind）

| Kind | 说明 | 注册方法 |
|:---|:---|:---|
| `provider` | 模型提供商（40+） | `registerProvider()` |
| `channel` | 消息渠道（30+） | `registerChannel()` |
| `tool` | 工具能力 | `registerTool()` |
| `hook` | 生命周期钩子 | `registerHook()` / `on()` |

---

## 三、Manifest 系统

> 文件：`src/plugins/manifest.ts`

### 3.1 Plugin Manifest

每个插件根目录必须有 `openclaw.plugin.json`：

```typescript
// src/plugins/manifest.ts
export const PLUGIN_MANIFEST_FILENAME = "openclaw.plugin.json";

export type PluginManifest = {
  id: string;
  configSchema: JsonSchemaObject;
  enabledByDefault?: boolean;
  kind?: PluginKind | PluginKind[];
  channels?: string[];        // 拥有的渠道 ID
  providers?: string[];        // 拥有的 Provider ID
  skills?: string[];
  name?: string;
  description?: string;
  version?: string;
  contracts?: PluginManifestContracts;  // 声明式能力契约
  activation?: PluginManifestActivation; // 激活触发条件
  setup?: PluginManifestSetup;           // Setup 元数据
  channelConfigs?: Record<string, PluginManifestChannelConfig>;
};
```

### 3.2 激活条件（Activation）

```typescript
export type PluginManifestActivationCapability = "provider" | "channel" | "tool" | "hook";

export type PluginManifestActivation = {
  onStartup?: boolean;           // Gateway 启动时激活
  onProviders?: string[];        // 指定 Provider 被使用时激活
  onAgentHarnesses?: string[];   // 指定 Agent Harness 被选中时激活
  onCommands?: string[];         // 指定命令被调用时激活
  onChannels?: string[];         // 指定 Channel 被使用时激活
  onRoutes?: string[];           // 指定路由被访问时激活
  onCapabilities?: PluginManifestActivationCapability[];  // 能力类型
};
```

### 3.3 能力契约（Contracts）

```typescript
export type PluginManifestContracts = {
  embeddedExtensionFactories?: string[];
  agentToolResultMiddleware?: string[];
  externalAuthProviders?: string[];
  memoryEmbeddingProviders?: string[];
  speechProviders?: string[];
  realtimeTranscriptionProviders?: string[];
  realtimeVoiceProviders?: string[];
  mediaUnderstandingProviders?: string[];
  imageGenerationProviders?: string[];
  videoGenerationProviders?: string[];
  musicGenerationProviders?: string[];
  webFetchProviders?: string[];
  webSearchProviders?: string[];
  tools?: string[];
};
```

### 3.4 第三方 Bundle 格式

> 文件：`src/plugins/bundle-manifest.ts`

OpenClaw 支持加载其他生态的插件格式：

| 格式 | Manifest 路径 |
|:---|:---|
| Codex | `.codex-plugin/plugin.json` |
| Claude | `.claude-plugin/plugin.json` |
| Cursor | `.cursor-plugin/plugin.json` |

```typescript
export function detectBundleManifestFormat(rootDir: string): PluginBundleFormat | null {
  if (fs.existsSync(path.join(rootDir, CODEX_BUNDLE_MANIFEST_RELATIVE_PATH))) {
    return "codex";
  }
  if (fs.existsSync(path.join(rootDir, CURSOR_BUNDLE_MANIFEST_RELATIVE_PATH))) {
    return "cursor";
  }
  if (fs.existsSync(path.join(rootDir, CLAUDE_BUNDLE_MANIFEST_RELATIVE_PATH))) {
    return "claude";
  }
  // ...
}
```

---

## 四、OpenClawPluginApi 接口

> 文件：`src/plugins/types.ts`

### 4.1 注册方法一览

```typescript
export type OpenClawPluginApi = {
  id: string;
  name: string;
  version?: string;
  description?: string;
  source: string;
  rootDir?: string;
  registrationMode: PluginRegistrationMode;
  config: OpenClawConfig;
  pluginConfig?: Record<string, unknown>;
  runtime: PluginRuntime;

  // ===== Provider 注册 =====
  registerProvider(provider: ProviderPlugin): void;
  registerSpeechProvider(provider: SpeechProviderPlugin): void;
  registerRealtimeTranscriptionProvider(provider: RealtimeTranscriptionProviderPlugin): void;
  registerRealtimeVoiceProvider(provider: RealtimeVoiceProviderPlugin): void;
  registerMediaUnderstandingProvider(provider: MediaUnderstandingProviderPlugin): void;
  registerImageGenerationProvider(provider: ImageGenerationProviderPlugin): void;
  registerVideoGenerationProvider(provider: VideoGenerationProviderPlugin): void;
  registerMusicGenerationProvider(provider: MusicGenerationProviderPlugin): void;
  registerWebFetchProvider(provider: WebFetchProviderPlugin): void;
  registerWebSearchProvider(provider: WebSearchProviderPlugin): void;

  // ===== Channel 注册 =====
  registerChannel(registration: OpenClawPluginChannelRegistration | ChannelPlugin): void;

  // ===== Tool 注册 =====
  registerTool(tool: AnyAgentTool | OpenClawPluginToolFactory, opts?: OpenClawPluginToolOptions): void;
  registerTrustedToolPolicy(policy: PluginTrustedToolPolicyRegistration): void;
  registerToolMetadata(metadata: PluginToolMetadataRegistration): void;

  // ===== Hook 注册 =====
  registerHook(events: string | string[], handler: InternalHookHandler, opts?: OpenClawPluginHookOptions): void;
  on<K extends PluginHookName>(hookName: K, handler: PluginHookHandlerMap[K], opts?: { priority?: number; timeoutMs?: number }): void;

  // ===== Command 注册 =====
  registerCommand(command: OpenClawPluginCommandDefinition): void;

  // ===== HTTP Route 注册 =====
  registerHttpRoute(params: OpenClawPluginHttpRouteParams): void;

  // ===== Gateway Method 注册 =====
  registerGatewayMethod(method: string, handler: GatewayRequestHandler, opts?: { scope?: OperatorScope }): void;

  // ===== 生命周期 =====
  registerService(service: OpenClawPluginService): void;
  registerRuntimeLifecycle(lifecycle: PluginRuntimeLifecycleRegistration): void;
  onConversationBindingResolved(handler: (event: PluginConversationBindingResolvedEvent) => void): void;

  // ===== 其他 =====
  registerCli(registrar: OpenClawPluginCliRegistrar, opts?: { commands?: string[]; descriptors?: OpenClawPluginCliCommandDescriptor[] }): void;
  registerReload(registration: OpenClawPluginReloadRegistration): void;
  registerConfigMigration(migrate: PluginConfigMigration): void;
  registerMemoryCapability(capability: MemoryPluginCapability): void;
  registerAgentHarness(harness: AgentHarness): void;
  // ...
};
```

### 4.2 ProviderPlugin 结构

```typescript
export type ProviderPlugin = {
  id: string;
  pluginId?: string;
  label: string;
  docsPath?: string;
  aliases?: string[];
  envVars?: string[];

  // 认证方法
  auth: ProviderAuthMethod[];

  // 目录发现
  catalog?: ProviderPluginCatalog;        // 在线目录（可能需要网络）
  staticCatalog?: ProviderPluginCatalog; // 离线静态目录

  // 模型解析钩子
  resolveDynamicModel?(ctx: ProviderResolveDynamicModelContext): ProviderRuntimeModel | null;
  normalizeModelId?(ctx: ProviderNormalizeModelIdContext): string | null;
  normalizeResolvedModel?(ctx: ProviderNormalizeResolvedModelContext): ProviderRuntimeModel | null;
  prepareRuntimeAuth?(ctx: ProviderPrepareRuntimeAuthContext): ProviderPreparedRuntimeAuth | null;

  // Replay/Compaction 策略
  buildReplayPolicy?(ctx: ProviderReplayPolicyContext): ProviderReplayPolicy | null;
  sanitizeReplayHistory?(ctx: ProviderSanitizeReplayHistoryContext): AgentMessage[] | null;

  // Wizard UI
  wizard?: ProviderPluginWizard;

  // ...
};
```

### 4.3 ChannelPlugin 结构

```typescript
export type OpenClawPluginChannelRegistration = {
  plugin: ChannelPlugin;
};
```

---

## 五、激活计划（Activation Planner）

> 文件：`src/plugins/activation-planner.ts`

### 5.1 触发类型

```typescript
export type PluginActivationPlannerTrigger =
  | { kind: "command"; command: string }
  | { kind: "provider"; provider: string }
  | { kind: "agentHarness"; runtime: string }
  | { kind: "channel"; channel: string }
  | { kind: "route"; route: string }
  | { kind: "capability"; capability: PluginManifestActivationCapability };
```

### 5.2 激活计划生成

```typescript
export function resolveManifestActivationPlan(
  params: ResolveManifestActivationPlanParams,
): PluginActivationPlan {
  const registry = loadPluginManifestRegistryForPluginRegistry({
    config: params.config,
    workspaceDir: params.workspaceDir,
    env: params.env,
    includeDisabled: true,
  });

  const entries = registry.plugins
    .flatMap((plugin) => {
      // 按 origin 过滤
      if (params.origin && plugin.origin !== params.origin) return [];
      // 按 onlyPluginIds 过滤
      if (onlyPluginIdSet && !onlyPluginIdSet.has(plugin.id)) return [];

      const reasons = listManifestActivationTriggerReasons(plugin, params.trigger);
      if (reasons.length === 0) return [];

      return [{ pluginId: plugin.id, origin: plugin.origin, reasons }];
    })
    .toSorted((left, right) => left.pluginId.localeCompare(right.pluginId));

  return {
    trigger: params.trigger,
    pluginIds: [...new Set(entries.map((entry) => entry.pluginId))],
    entries,
    diagnostics: registry.diagnostics,
  };
}
```

### 5.3 原因列表

```typescript
export type PluginActivationPlannerReason =
  | PluginActivationPlannerHintReason      // 运行时 Hint
  | PluginActivationPlannerManifestReason; // Manifest 声明

// Hint 原因
| "activation-agent-harness-hint"
| "activation-capability-hint"
| "activation-channel-hint"
| "activation-command-hint"
| "activation-provider-hint"
| "activation-route-hint"

// Manifest 原因
| "manifest-channel-owner"
| "manifest-command-alias"
| "manifest-hook-owner"
| "manifest-provider-owner"
| "manifest-setup-provider-owner"
| "manifest-tool-contract"
```

---

## 六、注册模式（Registration Mode）

> 文件：`src/plugins/types.ts`

```typescript
export type PluginRegistrationMode =
  | "full"           // 完整运行时激活，可启动长生命周期副作用
  | "discovery"      // 只读能力发现，跳过 socket/worker/client 初始化
  | "setup-only"     // 仅渠道配置入口
  | "setup-runtime"  // 渠道配置 + 运行时通道入口
  | "cli-metadata";   // CLI 命令元数据收集
```

---

## 七、Provider 认证系统

### 7.1 认证方法

```typescript
export type ProviderAuthMethod = {
  id: string;
  label: string;
  hint?: string;
  kind: ProviderAuthKind;  // "oauth" | "api_key" | "token" | "device_code" | "custom"
  wizard?: ProviderPluginWizardSetup;
  run: (ctx: ProviderAuthContext) => Promise<ProviderAuthResult>;
  runNonInteractive?: (ctx: ProviderAuthMethodNonInteractiveContext) => Promise<OpenClawConfig | null>;
};
```

### 7.2 认证上下文

```typescript
export type ProviderAuthContext = {
  config: OpenClawConfig;
  env?: NodeJS.ProcessEnv;
  agentDir?: string;
  workspaceDir?: string;
  prompter: WizardPrompter;
  runtime: RuntimeEnv;
  opts?: ProviderAuthOptionBag;
  secretInputMode?: SecretInputMode;
  allowSecretRefPrompt?: boolean;
  isRemote: boolean;
  openUrl: (url: string) => Promise<void>;
  oauth: { createVpsAwareHandlers: typeof createVpsAwareOAuthHandlers };
};
```

### 7.3 Wizard Setup

```typescript
export type ProviderPluginWizardSetup = {
  choiceId?: string;
  choiceLabel?: string;
  choiceHint?: string;
  assistantPriority?: number;
  assistantVisibility?: "visible" | "manual-only";
  groupId?: string;
  groupLabel?: string;
  onboardingScopes?: Array<"text-inference" | "image-generation">;
  modelAllowlist?: { allowedKeys?: string[]; initialSelections?: string[]; loadCatalog?: boolean };
  modelSelection?: { promptWhenAuthChoiceProvided?: boolean; allowKeepCurrent?: boolean };
};
```

---

## 八、插件命令系统

### 8.1 命令定义

```typescript
export type OpenClawPluginCommandDefinition = {
  name: string;                    // 命令名（无前导斜杠）
  nativeNames?: Partial<Record<string, string>>;
  nativeProgressMessages?: Partial<Record<string, string>>;
  description: string;
  agentPromptGuidance?: readonly string[];
  acceptsArgs?: boolean;
  requireAuth?: boolean;
  requiredScopes?: OperatorScope[];
  ownership?: "plugin" | "reserved";
  handler: PluginCommandHandler;
};
```

### 8.2 命令上下文

```typescript
export type PluginCommandContext = {
  senderId?: string;
  channel: string;
  channelId?: ChannelId;
  isAuthorizedSender: boolean;
  senderIsOwner?: boolean;
  gatewayClientScopes?: string[];
  sessionKey?: string;
  sessionId?: string;
  args?: string;
  commandBody: string;
  config: OpenClawConfig;
  from?: string;
  to?: string;
  accountId?: string;
  messageThreadId?: string | number;
  threadParentId?: string;
  requestConversationBinding: (params?: PluginConversationBindingRequestParams) => Promise<PluginConversationBindingRequestResult>;
  detachConversationBinding: () => Promise<{ removed: boolean }>;
  getCurrentConversationBinding: () => Promise<PluginConversationBinding | null>;
};
```

---

## 九、Plugin 生命周期

```
插件加载
    │
    ├─► Manifest 解析（loadPluginManifest）
    │      └─► 验证 configSchema、id、kind
    │
    ├─► 激活计划生成（resolveManifestActivationPlan）
    │      └─► 按 trigger 匹配激活条件
    │
    ├─► 插件运行时加载
    │      ├─► 模块加载（index.ts / index.js）
    │      ├─► register(api) 调用
    │      └─► activate(api) 调用
    │
    └─► 能力注册
          ├─► registerProvider() → ProviderRegistry
          ├─► registerChannel() → ChannelRegistry
          ├─► registerTool() → ToolRegistry
          └─► registerHook() → HookSystem
```

---

## 十、设计权衡

### 10.1 Manifest-First 原则

OpenClaw 采用 **Manifest-First** 设计——在加载插件运行时代码之前，先通过 Manifest 声明式地了解插件能力。

**优势**：
- Setup/配置 UI 可以在插件运行前显示
- 激活计划可以在不导入插件的情况下生成
- 诊断和错误可以在运行时前发现

**代价**：
- 双重定义（Manifest + 代码）可能存在不一致
- 需要解析和验证逻辑

### 10.2 能力契约（Contracts）vs 运行时钩子

OpenClaw 使用 `contracts` 字段声明插件拥有的能力，替代运行时检查。

```typescript
// 而非运行时检查
// if (plugin.registerProvider) { ... }

// 使用声明式契约
contracts?: { imageGenerationProviders?: string[] };
```

### 10.3 多格式兼容

通过 `bundle-manifest.ts` 支持 Codex、Claude、Cursor 三种第三方格式，降低用户迁移成本。

---

## 下一步

下一篇：[04 - Agent Runtime：任务编排与执行](./04-agent-runtime.md)，深入 Agent 运行时如何接收任务、调度工具、执行编排。

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*