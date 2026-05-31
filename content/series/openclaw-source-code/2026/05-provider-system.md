---
title: "OpenClaw源码剖析 #05 · Provider 系统：多模型统一接口"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 06
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Provider 系统定位

Provider 系统是 OpenClaw 的**模型抽象层**——通过统一接口接入 40+ 模型厂商，对上屏蔽厂商差异。

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Core                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Agent RT    │  │  Channel     │  │   Skills     │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                │
│         ▼                                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │           Model Selection (model-selection.ts)       │    │
│  │  resolveDefaultModelForAgent()                      │    │
│  │  buildAllowedModelSet()                              │    │
│  │  resolveConfiguredModelRef()                        │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────────────┐
│               Provider 插件层 (extensions/providers/)        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ openai/ │  │anthropic/│  │ ollama/ │  │ gemini/ │ ...  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件 | 职责 |
|:---|:---|
| `agents/model-selection.ts` | 模型选择、解析、规范化 |
| `agents/model-selection-normalize.ts` | ModelRef 规范化 |
| `agents/model-selection-shared.ts` | 模型列表/别名共享逻辑 |
| `agents/model-catalog.ts` | 模型目录加载 |
| `agents/defaults.ts` | 默认 Provider/Model |
| `agents/provider-id.ts` | Provider ID 规范化 |
| `extensions/providers/*/` | 40+ Provider 插件 |

---

## 三、核心类型

### 3.1 ModelRef

```typescript
// agents/model-selection-normalize.ts
export type ModelRef = {
  provider: string;  // e.g. "openai", "anthropic"
  model: string;     // e.g. "gpt-4o", "claude-sonnet-4"
};
```

### 3.2 ModelKey

模型唯一标识：`provider/model`

```typescript
export function modelKey(provider: string, model: string): string {
  return `${normalizeProviderId(provider)}/${model}`;
}
```

### 3.3 ModelCatalogEntry

```typescript
export type ModelCatalogEntry = {
  provider: string;
  id: string;
  label?: string;
  description?: string;
  supportsStreaming?: boolean;
  supportsTools?: boolean;
  supportsVision?: boolean;
  contextWindow?: number;
  reasoning?: boolean;
  // ...
};
```

---

## 四、模型选择流程

### 4.1 解析入口

```typescript
// agents/model-selection.ts
export function resolveDefaultModelForAgent(params: {
  cfg: OpenClawConfig;
  agentId?: string;
}): ModelRef {
  // 1. 检查 Agent 级别的模型覆盖
  const agentModelOverride = params.agentId
    ? resolveAgentEffectiveModelPrimary(params.cfg, params.agentId)
    : undefined;

  // 2. 合并到 Config
  const cfg = agentModelOverride
    ? { ...params.cfg, agents: { ...agents, defaults: { model: { primary: agentModelOverride } } } }
    : params.cfg;

  // 3. 调用共享解析
  return resolveConfiguredModelRef({
    cfg,
    defaultProvider: DEFAULT_PROVIDER,
    defaultModel: DEFAULT_MODEL,
  });
}
```

### 4.2 resolveConfiguredModelRef

```typescript
// agents/model-selection-shared.ts
export function resolveConfiguredModelRef(params: {
  cfg: OpenClawConfig;
  defaultProvider: string;
  defaultModel: string;
}): ModelRef {
  // 1. 解析 primary 模型
  const primary = resolveConfiguredModelPrimary({ ... });

  // 2. 解析 fallback 模型列表
  const fallbacks = resolveConfiguredModelFallbacks({ ... });

  // 3. 返回规范化的 ModelRef
  return {
    provider: primary.provider ?? params.defaultProvider,
    model: primary.model ?? params.defaultModel,
  };
}
```

---

## 五、Provider 规范化

### 5.1 normalizeProviderId

```typescript
// agents/provider-id.ts
export function normalizeProviderId(raw: string): string {
  const trimmed = raw.trim().toLowerCase();
  // 处理别名
  const aliasMap: Record<string, string> = {
    "claude": "anthropic",
    "gpt": "openai",
    // ...
  };
  return aliasMap[trimmed] ?? trimmed;
}
```

### 5.2 模型引用解析

```typescript
export function parseModelRef(
  raw: string,
  defaultProvider?: string,
): ModelRef | null {
  // "gpt-4o" → { provider: "openai", model: "gpt-4o" }
  // "anthropic/claude-sonnet-4" → { provider: "anthropic", model: "claude-sonnet-4" }
  // "claude-sonnet-4" (defaultProvider="anthropic") → { provider: "anthropic", model: "claude-sonnet-4" }
}
```

---

## 六、Allowlist 控制

### 6.1 buildAllowedModelSet

```typescript
export function buildAllowedModelSet(params: {
  cfg: OpenClawConfig;
  catalog: ModelCatalogEntry[];
  defaultProvider: string;
  defaultModel?: string;
  agentId?: string;
}): {
  allowAny: boolean;
  allowedCatalog: ModelCatalogEntry[];
  allowedKeys: Set<string>;
} {
  // 1. 获取 Agent 的模型白名单
  const allowlist = buildConfiguredAllowlistKeys({
    cfg: params.cfg,
    defaultProvider: params.defaultProvider,
    agentId: params.agentId,
  });

  // 2. 如果白名单为空，不限制
  if (allowlist.length === 0) {
    return { allowAny: true, allowedCatalog: [], allowedKeys: new Set() };
  }

  // 3. 过滤 Catalog
  const allowedKeys = new Set(allowlist);
  const allowedCatalog = params.catalog.filter(entry =>
    allowedKeys.has(modelKey(entry.provider, entry.id))
  );

  return { allowAny: false, allowedCatalog, allowedKeys };
}
```

---

## 七、模型别名系统

### 7.1 buildModelAliasIndex

```typescript
export function buildModelAliasIndex(params: {
  cfg: OpenClawConfig;
  defaultProvider: string;
}): ModelAliasIndex {
  // 构建别名 → 规范化引用的映射
  // 用于： shorthand "claude" → "anthropic/claude-sonnet-4"
}
```

### 7.2 别名解析

```typescript
export function resolveModelThroughAliases(
  value: string,
  aliasIndex: ModelAliasIndex,
): string {
  // 已经是 provider/model 格式 → 直接返回
  if (value.includes("/")) return value;

  // 查找别名
  const aliasMatch = aliasIndex.byAlias.get(value.toLowerCase());
  if (aliasMatch) {
    return `${aliasMatch.ref.provider}/${aliasMatch.ref.model}`;
  }

  // 未知字符串 → 原样返回
  return value;
}
```

---

## 八、Provider 插件接口

> 文件：`src/plugins/types.ts`（ProviderPlugin）

```typescript
export type ProviderPlugin = {
  id: string;
  pluginId?: string;
  label: string;
  aliases?: string[];
  envVars?: string[];

  // 认证方法
  auth: ProviderAuthMethod[];

  // 目录
  catalog?: ProviderPluginCatalog;      // 在线（可能需要网络）
  staticCatalog?: ProviderPluginCatalog; // 离线静态

  // 模型解析钩子
  resolveDynamicModel?(ctx): ProviderRuntimeModel | null;
  normalizeModelId?(ctx): string | null;
  normalizeResolvedModel?(ctx): ProviderRuntimeModel | null;

  // Replay/Compaction
  buildReplayPolicy?(ctx): ProviderReplayPolicy | null;
  sanitizeReplayHistory?(ctx): AgentMessage[] | null;

  // 运行时 Auth
  prepareRuntimeAuth?(ctx): ProviderPreparedRuntimeAuth | null;

  // Wizard UI
  wizard?: ProviderPluginWizard;
};
```

---

## 九、支持的 Provider 列表

| Provider | 说明 |
|:---|:---|
| `openai` | OpenAI GPT 系列 |
| `anthropic` | Anthropic Claude 系列 |
| `google` | Google Gemini |
| `ollama` | 本地 Ollama |
| `azure` | Azure OpenAI |
| `amazon-bedrock` | AWS Bedrock |
| `deepseek` | DeepSeek |
| `mistral` | Mistral AI |
| `groq` | Groq |
| `openrouter` | OpenRouter |
| `together` | Together AI |
| `xai` | xAI (Grok) |
| `nvidia` | NVIDIA NIM |
| `cerebras` | Cerebras |
| `moonshot` | Moonshot (Kimi) |
| `qwen` | Qwen (阿里通义) |
| `deepinfra` | DeepInfra |
| `vllm` | vLLM |
| `sglang` | SGLang |
| `kimi-coding` | Kimi Coding |
| `wenxin` | 百度文心 |
| `minimax` | MiniMax |
| `volcengine` | 火山引擎 |
| `baichuan` | 百川 |
| `tencent` | 腾讯混元 |

---

## 十、设计权衡

### 10.1 Provider ID 规范化

不同厂商使用不同的 Provider ID：
- OpenAI: `"openai"`、`"gpt"`、`"o1"`
- Anthropic: `"anthropic"`、`"claude"`

通过 `normalizeProviderId()` 统一映射。

### 10.2 模型引用歧义

用户可能输入：
- `"gpt-4o"` → 需要根据上下文推断 provider
- `"anthropic/claude-sonnet-4"` → 显式指定
- `"claude-sonnet-4"` → 需要 `defaultProvider`

系统通过 `parseModelRef()` + `defaultProvider` 参数解决歧义。

### 10.3 Catalog vs Static Catalog

- `catalog`: 动态发现，可能需要网络请求
- `staticCatalog`: 离线静态目录，用于 setup UI

---

## 下一步

下一篇：[06 - Channel 系统：多渠道消息接入](./06-channel-system.md)，深入消息渠道抽象层。

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*