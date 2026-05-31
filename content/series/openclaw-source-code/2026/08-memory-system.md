---
title: "OpenClaw源码剖析 #08 · 记忆系统：Memory Architecture"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 09
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、记忆系统定位

记忆系统是 OpenClaw 的**长期知识管理模块**——通过搜索、注入、压缩机制扩展 Agent 的上下文能力。

```
┌─────────────────────────────────────────────────────────────┐
│                   Memory System                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              MemoryPluginCapability                   │ │
│  │  promptBuilder · flushPlanResolver · runtime         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │  Prompt Builder  │  │  Search Manager  │              │
│  │  向 System Prompt │  │  向量/全文搜索    │              │
│  │  注入记忆段落      │  │  RAG 检索         │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │            Flush Plan (Compaction)                     │ │
│  │  会话过长时触发记忆压缩，释放上下文窗口                 │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件 | 职责 |
|:---|:---|
| `plugins/memory-state.ts` | Memory 插件状态与注册 |
| `plugin-sdk/memory-host-core.ts` | Memory Host 核心 |
| `plugin-sdk/memory-host-search.ts` | 搜索接口 |
| `plugin-sdk/memory-core-host-runtime-*.ts` | 各后端运行时 |
| `agents/memory-search.ts` | Agent 记忆搜索 |
| `auto-reply/reply/memory-flush.ts` | 记忆刷新 |
| `memory-host-sdk/host/types.ts` | SearchManager 类型 |

---

## 三、核心类型

> 文件：`plugins/memory-state.ts`

### 3.1 MemoryPluginCapability

```typescript
export type MemoryPluginCapability = {
  // Prompt 片段构建器
  promptBuilder?: MemoryPromptSectionBuilder;

  // 刷新计划解析器
  flushPlanResolver?: MemoryFlushPlanResolver;

  // 运行时
  runtime?: MemoryPluginRuntime;

  // 公共产物
  publicArtifacts?: MemoryPluginPublicArtifactsProvider;
};
```

### 3.2 MemoryPromptSectionBuilder

```typescript
export type MemoryPromptSectionBuilder = (params: {
  availableTools: Set<string>;
  citationsMode?: MemoryCitationsMode;
}) => string[];
```

### 3.3 MemoryCorpusSupplement

```typescript
export type MemoryCorpusSupplement = {
  search(params: {
    query: string;
    maxResults?: number;
    agentSessionKey?: string;
  }): Promise<MemoryCorpusSearchResult[]>;

  get(params: {
    lookup: string;
    fromLine?: number;
    lineCount?: number;
    agentSessionKey?: string;
  }): Promise<MemoryCorpusGetResult | null>;
};
```

### 3.4 MemoryFlushPlan

```typescript
export type MemoryFlushPlan = {
  softThresholdTokens: number;
  forceFlushTranscriptBytes: number;
  reserveTokensFloor: number;
  model?: string;
  prompt: string;
  systemPrompt: string;
  relativePath: string;
};
```

---

## 四、注册接口

### 4.1 Capability 注册

```typescript
// 单一插槽（独占）
registerMemoryCapability(pluginId: string, capability: MemoryPluginCapability): void;

getMemoryCapabilityRegistration(): MemoryPluginCapabilityRegistration | undefined;
```

### 4.2 Corpus Supplement 注册

```typescript
// 多插件可共存
registerMemoryCorpusSupplement(pluginId: string, supplement: MemoryCorpusSupplement): void;

listMemoryCorpusSupplements(): MemoryCorpusSupplementRegistration[];
```

### 4.3 Prompt Supplement 注册

```typescript
// 多插件可共存
registerMemoryPromptSupplement(pluginId: string, builder: MemoryPromptSectionBuilder): void;

listMemoryPromptSupplements(): MemoryPromptSupplementRegistration[];
```

---

## 五、Search Manager

> 文件：`memory-host-sdk/host/types.ts`

### 5.1 MemorySearchManager

```typescript
export type MemorySearchManager = {
  // 搜索记忆
  search(params: MemorySearchParams): Promise<MemorySearchResult[]>;

  // 获取记忆详情
  get(params: MemoryGetParams): Promise<MemoryGetResult | null>;

  // 索引新内容
  upsert(params: MemoryUpsertParams): Promise<void>;

  // 删除记忆
  delete(params: MemoryDeleteParams): Promise<void>;

  // 健康检查
  ping?(): Promise<boolean>;
};
```

### 5.2 搜索参数

```typescript
export type MemorySearchParams = {
  query: string;
  maxResults?: number;
  filter?: MemorySearchFilter;
  purpose?: "default" | "status" | "cli";
};
```

---

## 六、Prompt 构建流程

> `plugins/memory-state.ts` 中的 `buildMemorySection()`

```typescript
export function buildMemoryPromptSection(params: {
  availableTools: Set<string>;
  citationsMode?: MemoryCitationsMode;
}): string[] {
  // 1. 获取主 Capability 的 promptBuilder
  const primary = normalizeMemoryPromptLines(
    memoryPluginState.capability?.capability.promptBuilder?.(params) ??
    memoryPluginState.promptBuilder?.(params) ??
    []
  );

  // 2. 收集所有 Prompt Supplements（排序后）
  const supplements = memoryPluginState.promptSupplements
    .toSorted((left, right) => left.pluginId.localeCompare(right.pluginId))
    .flatMap(registration => normalizeMemoryPromptLines(registration.builder(params)));

  // 3. 合并输出
  return [...primary, ...supplements];
}
```

---

## 七、Flush Plan（刷新计划）

### 7.1 触发时机

当会话 token 超过 `softThresholdTokens` 时，触发刷新计划。

### 7.2 解析流程

```typescript
export function resolveMemoryFlushPlan(params: {
  cfg?: OpenClawConfig;
  nowMs?: number;
}): MemoryFlushPlan | null {
  return (
    memoryPluginState.capability?.capability.flushPlanResolver?.(params) ??
    memoryPluginState.flushPlanResolver?.(params) ??
    null
  );
}
```

### 7.3 FlushPlan 内容

```typescript
// flushPlan 定义的内容
{
  softThresholdTokens: 150000,     // 软阈值
  forceFlushTranscriptBytes: 500000,  // 强制刷新字节数
  reserveTokensFloor: 5000,     // 保留 token 下限
  model?: "claude-sonnet-4",       // 用于摘要的模型
  prompt: "...",                  // 摘要 prompt
  systemPrompt: "...",             // 系统 prompt
  relativePath: "memory/flush.md", // 输出路径
}
```

---

## 八、Corpus 搜索

### 8.1 Search Result

```typescript
export type MemoryCorpusSearchResult = {
  corpus: string;
  path: string;
  title?: string;
  kind?: string;
  score: number;
  snippet: string;
  id?: string;
  startLine?: number;
  endLine?: number;
  citation?: string;
  source?: string;
  provenanceLabel?: string;
  sourceType?: string;
  sourcePath?: string;
  updatedAt?: string;
};
```

### 8.2 多插件搜索聚合

```typescript
// 所有注册的 corpus supplements 都会被搜索
const allSupplements = listMemoryCorpusSupplements();
const results = await Promise.all(
  allSupplements.map(s => s.supplement.search({ query, maxResults }))
);
// 结果按 score 排序后返回
```

---

## 九、后端类型

### 9.1 MemoryRuntimeBackendConfig

```typescript
export type MemoryRuntimeBackendConfig =
  | { backend: "builtin" }
  | { backend: "qmd"; qmd?: MemoryRuntimeQmdConfig };
```

### 9.2 QMD 配置

```typescript
export type MemoryRuntimeQmdConfig = {
  command?: string;
};
```

---

## 十、设计权衡

### 10.1 独占 vs 叠加

- `MemoryPluginCapability`（promptBuilder/runtime）是**独占**的——只有一个插件可以注册
- `MemoryCorpusSupplement` / `MemoryPromptSupplement` 是**叠加**的——多个插件可以共存

这种设计平衡了「单一职责」与「可扩展性」。

### 10.2 搜索 vs 注入

OpenClaw 采用**混合策略**：
- **Search**：按需检索，RAG 模式
- **Prompt Builder**：每次都注入，缓存模式

### 10.3 Flush Plan 的外部化

刷新逻辑由插件实现（`flushPlanResolver`），核心只定义接口契约。这允许不同的记忆插件使用不同的压缩算法。

---

## 下一步

篇目 09-15 属于扩展开发与工程实践，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 09 | [Extension 开发：Provider 篇](./09-extension-provider.md) | 开发新模型 Provider |
| 10 | [Extension 开发：Channel 篇](./10-extension-channel.md) | 开发新消息渠道 |
| 11 | [Extension 开发：Skill 篇](./11-extension-skill.md) | 开发新 Skill |
| 12 | [测试策略：单元/集成/E2E](./12-testing-strategy.md) | Vitest + E2E |
| 13 | [配置系统：Schema 与验证](./13-config-system.md) | 配置管理 |
| 14 | [安全机制：Auth 与权限](./14-security-auth.md) | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*