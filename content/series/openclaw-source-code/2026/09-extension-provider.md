---
title: "OpenClaw源码剖析 #09 · Extension 开发：Provider 篇"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 10
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Provider 扩展定位

Provider 扩展是 OpenClaw 的**模型接入层**——通过插件机制接入 40+ 模型厂商，对上提供统一的 `ProviderPlugin` 接口。

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Core                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Agent RT    │  │  Channel     │  │   Skills     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │              ProviderPlugin Interface               │    │
│  │  id · label · auth · catalog · resolveDynamicModel │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│               extensions/providers/                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ openai/ │  │anthropic/│  │ ollama/ │  │ gemini/ │ ...  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件 | 职责 |
|:---|:---|
| `src/plugins/types.ts` | ProviderPlugin 类型定义 |
| `extensions/providers/<name>/index.ts` | Provider 插件入口 |
| `extensions/providers/<name>/api.ts` | 运行时 API 实现 |
| `extensions/providers/<name>/provider-discovery.ts` | 独立发现插件 |
| `extensions/providers/<name>/openclaw.plugin.json` | Manifest 元数据 |
| `src/agents/model-catalog.ts` | 模型目录加载 |
| `src/agents/model-catalog.types.ts` | ModelCatalogEntry 类型 |

---

## 三、ProviderPlugin 接口

> 文件：`src/plugins/types.ts`

### 3.1 核心字段

```typescript
export type ProviderPlugin = {
  id: string;              // 唯一标识，如 "openai"、"ollama"
  label: string;           // 显示名称，如 "OpenAI"、"Ollama"
  envVars?: string[];      // 环境变量，如 ["OPENAI_API_KEY"]
  aliases?: string[];      // 别名映射

  // 认证方式（必填）
  auth: ProviderAuthMethod[];

  // 模型目录
  catalog?: ProviderPluginCatalog;      // 动态目录（可能有网络 I/O）
  staticCatalog?: ProviderPluginCatalog; // 离线静态目录，用于 Setup UI

  // 模型解析钩子
  resolveDynamicModel?(ctx): ProviderRuntimeModel | null;
  normalizeModelId?(ctx): string | null;
  normalizeResolvedModel?(ctx): ProviderRuntimeModel | null;

  // 运行时 Auth
  prepareRuntimeAuth?(ctx): ProviderPreparedRuntimeAuth | null;

  // Replay/Compaction
  buildReplayPolicy?(ctx): ProviderReplayPolicy | null;
  sanitizeReplayHistory?(ctx): AgentMessage[] | null;

  // Wizard UI
  wizard?: ProviderPluginWizard;
};
```

### 3.2 模型解析上下文

```typescript
export type ProviderRuntimeModel = {
  provider: string;
  model: string;
  reasoning?: boolean;
  supportsStreaming?: boolean;
  supportsTools?: boolean;
  supportsVision?: boolean;
  contextWindow?: number;
  label?: string;
  description?: string;
};
```

### 3.3 Catalog 类型

```typescript
export type ProviderPluginCatalog = {
  order?: ProviderCatalogOrder;  // "simple" | "profile" | "paired" | "late"
  run: (ctx: ProviderCatalogContext) => Promise<ProviderCatalogResult>;
};

export type ProviderCatalogResult =
  | { provider: ModelProviderConfig }
  | { providers: Record<string, ModelProviderConfig> }
  | null
  | undefined;
```

### 3.4 ModelCatalogEntry

```typescript
export type ModelCatalogEntry = {
  id: string;                    // 模型 ID，如 "gpt-4o"
  name?: string;                  // 显示名称
  provider: string;               // provider ID
  alias?: string;                 // 别名
  contextWindow?: number;         // 上下文窗口大小
  reasoning?: boolean;           // 是否支持推理
  input?: ModelInputType[];       // 支持的输入类型
  compat?: ModelCompatConfig;     // 兼容性配置
};
```

---

## 四、认证系统

### 4.1 ProviderAuthMethod

```typescript
export type ProviderAuthMethod = {
  id: string;           // 唯一方法 ID，如 "api-key"、"oauth"
  label: string;        // 显示标签
  hint?: string;        // 帮助文本
  kind: ProviderAuthKind;  // "oauth" | "api_key" | "token" | "device_code" | "custom"
  wizard?: ProviderPluginWizardSetup;  // Onboarding UI 元数据
  run: (ctx: ProviderAuthContext) => Promise<ProviderAuthResult>;
  runNonInteractive?: (ctx) => Promise<OpenClawConfig | null>;
};
```

### 4.2 ProviderAuthContext

```typescript
export type ProviderAuthContext = {
  config: OpenClawConfig;
  env?: NodeJS.ProcessEnv;
  agentDir?: string;
  workspaceDir?: string;
  prompter: WizardPrompter;      // 交互式提示器
  runtime: RuntimeEnv;
  opts?: ProviderAuthOptionBag;  // CLI 预设参数
  secretInputMode?: SecretInputMode;
  allowSecretRefPrompt?: boolean;
  isRemote: boolean;
  openUrl: (url: string) => Promise<void>;
  oauth: { createVpsAwareHandlers: typeof createVpsAwareOAuthHandlers };
};
```

### 4.3 ProviderAuthResult

```typescript
export type ProviderAuthResult = {
  profiles: Array<{
    profileId: string;
    credential: AuthProfileCredential;
  }>;
  configPatch?: Partial<OpenClawConfig>;  // 可选配置默认值
  defaultModel?: string;                  // 默认选择模型
  notes?: string[];
  replaceDefaultModels?: boolean;
};
```

### 4.4 API Key 认证辅助函数

```typescript
// openclaw/plugin-sdk/provider-auth
import { buildApiKeyCredential } from "openclaw/plugin-sdk/provider-auth";

const credential = buildApiKeyCredential(
  providerId,
  apiKey,
  profileId,
  keyLabel,
  expiresAt
);
```

---

## 五、文件结构

### 5.1 标准 Provider 扩展结构

```
extensions/<provider-name>/
├── index.ts           # 插件入口（definePluginEntry）
├── api.ts             # 运行时 API 实现
├── setup-api.ts       # 轻量级 Setup 钩子（可选）
├── provider-discovery.ts  # 独立发现插件（可选）
├── openclaw.plugin.json   # Manifest 元数据
├── package.json       # 包元数据
├── tsconfig.json      # TypeScript 配置
└── src/
    ├── discovery-shared.ts    # 共享发现逻辑
    ├── defaults.ts            # 常量默认值
    ├── embedding-provider.ts  # 记忆嵌入适配器（可选）
    ├── stream.ts              # 自定义流处理（可选）
    ├── provider-models.ts     # 模型目录构建器
    └── provider-base-url.ts   # Base URL 解析
```

### 5.2 Ollama 示例

```
extensions/ollama/
├── index.ts                 # 插件入口
├── provider-discovery.ts    # 独立发现插件
├── openclaw.plugin.json     # Manifest
└── src/
    ├── discovery-shared.ts   # 共享 auth/discovery 逻辑
    ├── defaults.ts           # OLLAMA_DEFAULT_BASE_URL 等
    ├── provider-models.ts    # 模型目录构建器
    ├── provider-base-url.ts  # URL 工具
    ├── embedding-provider.ts # 记忆嵌入适配器
    ├── setup.ts              # 交互式安装向导
    └── stream.ts             # 自定义流封装
```

---

## 六、完整实现示例

### 6.1 index.ts（插件入口）

```typescript
// extensions/ollama/index.ts
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { buildOllamaProvider } from "./api.js";

export default definePluginEntry({
  id: "ollama",
  name: "Ollama Provider",
  description: "Bundled Ollama provider plugin",
  register(api: OpenClawPluginApi) {
    api.registerProvider(buildOllamaProvider());
  },
});
```

### 6.2 api.ts（运行时实现）

```typescript
// extensions/ollama/api.ts
import { type ProviderPlugin } from "openclaw/plugin-sdk/provider-model-shared";

export function buildOllamaProvider(): ProviderPlugin {
  return {
    id: "ollama",
    label: "Ollama",
    docsPath: "/providers/ollama",
    envVars: ["OLLAMA_API_KEY"],
    auth: [
      {
        id: "local",
        label: "Ollama",
        hint: "Local and remote open models",
        kind: "custom",
        run: async (ctx: ProviderAuthContext): Promise<ProviderAuthResult> => {
          const result = await promptAndConfigureOllama({...});
          return {
            profiles: [{
              profileId: "ollama:default",
              credential: buildApiKeyCredential(...),
            }],
            configPatch: result.config,
          };
        },
        runNonInteractive: async (ctx) => {
          return await configureOllamaNonInteractive({...});
        },
      },
    ],
    discovery: {
      order: "late",
      run: async (ctx) => await resolveOllamaDiscoveryResult({...}),
    },
    wizard: {
      setup: {
        choiceId: "ollama",
        choiceLabel: "Ollama",
        groupId: "ollama",
        groupLabel: "Ollama",
        methodId: "local",
        modelSelection: {
          promptWhenAuthChoiceProvided: true,
          allowKeepCurrent: false,
        },
      },
      modelPicker: {
        label: "Ollama (custom)",
        hint: "Detect models from a local or remote Ollama instance",
        methodId: "local",
      },
    },
    resolveDynamicModel: (ctx) => {...},
    createStreamFn: ({ config, model, provider }) => {...},
    resolveThinkingProfile: ({ reasoning }) => ({...}),
    ...OPENAI_COMPATIBLE_REPLAY_HOOKS,
  };
}
```

### 6.3 OpenAI Provider 示例

```typescript
// extensions/openai/openai-provider.ts
export function buildOpenAIProvider(): ProviderPlugin {
  return {
    id: "openai",
    label: "OpenAI",
    hookAliases: ["azure-openai", "azure-openai-responses"],
    docsPath: "/providers/models",
    envVars: ["OPENAI_API_KEY"],
    auth: [
      createProviderApiKeyAuthMethod({
        providerId: "openai",
        methodId: "api-key",
        label: "OpenAI API Key",
        hint: "Use your OpenAI API key directly",
        optionKey: "openaiApiKey",
        flagName: "--openai-api-key",
        envVar: "OPENAI_API_KEY",
        promptMessage: "Enter OpenAI API key",
        defaultModel: "gpt-4o",
        expectedProviders: ["openai"],
        applyConfig: (cfg) => applyOpenAIConfig(cfg),
        wizard: {
          choiceId: "openai-api-key",
          choiceLabel: "OpenAI API Key",
          ...OPENAI_API_KEY_WIZARD_GROUP,
        },
      }),
    ],
    resolveDynamicModel: (ctx) => resolveOpenAIGptForwardCompatModel(ctx),
    normalizeResolvedModel: (ctx) => {...},
    normalizeTransport: ({ provider, api, baseUrl }) => {...},
    resolveReasoningOutputMode: () => "native",
    resolveThinkingProfile: ({ modelId }) => ({
      levels: [
        { id: "off" }, { id: "minimal" }, { id: "low" },
        { id: "medium" }, { id: "high" },
        ...(matchesExactOrPrefix(modelId, OPENAI_XHIGH_MODEL_IDS)
          ? [{ id: "xhigh" as const }] : []),
      ],
    }),
    isModernModelRef: ({ modelId }) =>
      matchesExactOrPrefix(modelId, OPENAI_MODERN_MODEL_IDS),
    buildMissingAuthMessage: (ctx) => {...},
    augmentModelCatalog: (ctx) => {...},
  };
}
```

### 6.4 Discovery Only Provider 示例

```typescript
// extensions/anthropic/provider-discovery.ts
export const anthropicProviderDiscovery: ProviderPlugin = {
  id: "claude-cli",
  label: "Claude CLI",
  docsPath: "/providers/models",
  auth: [],  // 无需 auth，使用合成 auth
  resolveSyntheticAuth: ({ provider }) =>
    provider === "claude-cli" ? resolveClaudeCliSyntheticAuth() : undefined,
  discovery: {
    order: "late",
    run: runAnthropicDiscovery,
  },
};
```

---

## 七、Manifest 配置

> 文件：`extensions/ollama/openclaw.plugin.json`

```json
{
  "id": "ollama",
  "activation": { "onStartup": false },
  "enabledByDefault": true,
  "providers": ["ollama"],
  "providerDiscoveryEntry": "./provider-discovery.ts",
  "modelPricing": { "providers": { "ollama": { "external": false } } },
  "syntheticAuthRefs": ["ollama"],
  "nonSecretAuthMarkers": ["ollama-local"],
  "providerAuthEnvVars": { "ollama": ["OLLAMA_API_KEY"] },
  "providerAuthChoices": [
    {
      "provider": "ollama",
      "method": "local",
      "choiceId": "ollama",
      "choiceLabel": "Ollama",
      "groupId": "ollama",
      "groupLabel": "Ollama"
    }
  ],
  "contracts": {
    "memoryEmbeddingProviders": ["ollama"],
    "webSearchProviders": ["ollama"]
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "discovery": {
        "type": "object",
        "properties": { "enabled": { "type": "boolean" } }
      }
    }
  },
  "uiHints": { "discovery": { "label": "Model Discovery" } }
}
```

---

## 八、开发步骤

### 8.1 创建扩展目录

```
extensions/<provider-name>/
```

### 8.2 创建 package.json

```json
{
  "name": "openclaw-<provider>",
  "version": "0.1.0",
  "type": "module"
}
```

### 8.3 创建 tsconfig.json

```json
{ "extends": "../../../tsconfig.package-boundary.base.json" }
```

### 8.4 创建 index.ts

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { buildProviderProvider } from "./api.js";

export default definePluginEntry({
  id: "<provider-id>",
  name: "<Provider> Provider",
  description: "Bundled <provider> provider plugin",
  register(api: OpenClawPluginApi) {
    api.registerProvider(buildProviderProvider());
  },
});
```

### 8.5 创建 api.ts

实现 `ProviderPlugin` 接口，包括：
- `id`、`label`、`envVars`
- `auth`：认证方法数组
- `catalog` 或 `discovery`：模型目录
- `resolveDynamicModel`：动态模型解析
- `wizard`：可选的 Setup UI

### 8.6 创建 openclaw.plugin.json

配置 Manifest 元数据，包括 contracts、configSchema 等。

---

## 九、关键 SDK 导入

```typescript
// 插件入口
import { definePluginEntry, type OpenClawPluginApi } from "openclaw/plugin-sdk/plugin-entry";

// 类型定义
import {
  type ProviderPlugin,
  normalizeProviderId,
  DEFAULT_CONTEXT_TOKENS,
} from "openclaw/plugin-sdk/provider-model-shared";

// 认证辅助
import { buildApiKeyCredential } from "openclaw/plugin-sdk/provider-auth";

// Setup 工具
import { WizardCancelledError, type WizardPrompter } from "openclaw/plugin-sdk/setup";
```

---

## 十、设计权衡

### 10.1 auth 必填 vs 可选

`auth` 数组是**必填**的，但可以是空数组（用于无认证的本地 provider）。

```typescript
auth: [];  // 用于无认证的 provider
```

### 10.2 catalog vs discovery

| 类型 | 说明 | 适用场景 |
|:---|:---|:---|
| `catalog` | 动态目录，可能有网络 I/O | OpenAI、Anthropic 等需要 API 调用 |
| `staticCatalog` | 离线静态目录 | Setup UI 显示 |
| `discovery` | 运行时发现 | 本地/私有部署（Ollama） |

### 10.3 Wizard 的双重角色

- `wizard.setup`：在 Provider 选择阶段显示
- `wizard.modelPicker`：在模型选择阶段显示

分离允许更细粒度的用户体验控制。

---

## 下一步

篇目 09 完成，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 10 | [Extension 开发：Channel 篇](./10-extension-channel.md) | 开发新消息渠道 |
| 11 | [Extension 开发：Skill 篇](./11-extension-skill.md) | 开发新 Skill |
| 12 | [测试策略：单元/集成/E2E](./12-testing-strategy.md) | Vitest + E2E |
| 13 | [配置系统：Schema 与验证](./13-config-system.md) | 配置管理 |
| 14 | [安全机制：Auth 与权限](./14-security-auth.md) | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*