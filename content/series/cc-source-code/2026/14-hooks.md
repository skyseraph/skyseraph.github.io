---
title: "CC源码剖析 #14 · Hook 系统：生命周期拦截点"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 15
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Hook 系统定位

Hook 系统是 Claude Code 的**生命周期拦截点**——允许外部代码（插件、本地脚本）在特定事件发生时介入并修改行为。

```
用户输入
    │
    ▼
┌─────────────────────────────────┐
│  Hook System                    │
│  processSessionStartHooks()      │
│  processSetupHooks()            │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  QueryEngine                    │
│  preToolCall Hook              │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│  Tool.call()                    │
│  postToolCall Hook             │
└─────────────────────────────────┘
    │
    ▼
结果
```

---

## 二、Hook 类型定义

> 文件：`src/types/hooks.ts`

### 2.1 支持的事件类型

```typescript
// HOOK_EVENTS 列表
type HookEvent =
  | 'PreToolUse'          // 工具调用前
  | 'PostToolUse'         // 工具调用后
  | 'UserPromptSubmit'    // 用户提交输入前
  | 'UserPromptEdit'     // 用户编辑输入时
  | 'RoundStart'         // 回合开始
  | 'RoundEnd'           // 回合结束
  | 'SessionStart'       // 会话开始
  | 'SessionEnd'         // 会话结束
  | 'PreAgentCall'       // Agent 调用前
  | 'PostAgentCall'      // Agent 调用后
  | 'PreProcessModel'    // 模型处理前
  | 'PostProcessModel'   // 模型处理后
```

### 2.2 Hook 接口

```typescript
interface HookDefinition {
  event: HookEvent
  name: string
  source: 'plugin' | 'builtin' | 'user'
  handler: HookHandler
  config?: HookConfig
}

type HookHandler = (
  context: HookContext,
  input: HookInput,
) => Promise<HookResult>
```

### 2.3 Hook 输入/输出

```typescript
// Hook 输入
interface HookInput {
  event: HookEvent
  sessionId: string
  messages: Message[]
  // 事件特定的输入数据
}

// Hook 输出
interface HookResult {
  continue: boolean            // 是否继续执行
  suppressOutput?: boolean     // 是否隐藏输出
  stopReason?: string         // 停止原因
  decision?: 'approve' | 'block'  // 决策
  reason?: string             // 决策原因
  systemMessage?: string       // 系统消息
  updatedInput?: object       // 修改后的输入
  hookSpecificOutput?: object  // Hook 特定输出
}
```

---

## 三、Hook 生命周期

### 3.1 会话启动 Hook

> 文件：`src/utils/sessionStart.ts`

```typescript
async function processSessionStartHooks(
  hooks: HookDefinition[],
  context: HookContext,
): Promise<HookResult[]> {
  // 在会话开始时调用所有 SessionStart hooks
  // 按顺序执行，收集结果
}
```

### 3.2 会话结束 Hook

> 文件：`src/utils/hooks.ts`

```typescript
async function executeSessionEndHooks(
  hooks: HookDefinition[],
  context: HookContext,
  timeoutMs: number = 5000,
): Promise<void> {
  // 会话结束时调用
  // 有超时保护，防止 hook 卡住会话关闭
}
```

### 3.3 Turn 级别 Hook

```typescript
// 每个 turn 开始/结束时调用
// 注入时机：
// - preToolCall：工具调用前
// - postToolCall：工具调用后

onTurnStart(): void
onTurnEnd(): void
```

---

## 四、PreToolUse Hook

### 4.1 功能

在工具调用前拦截，可以：
- **修改输入**：更新工具参数
- **阻止执行**：返回 block 决定
- **添加上下文**：注入额外信息

### 4.2 配置示例

```typescript
// hooks.json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "name": "validate-file-path",
      "handler": "./hooks/validate-path.ts",
      "config": {
        "allowedPaths": ["src/**"]
      }
    }
  ]
}
```

### 4.3 Handler 实现

```typescript
async function validateFilePath(
  context: HookContext,
  input: { toolName: string; toolInput: object },
): Promise<HookResult> {
  if (input.toolName === 'FileEdit') {
    const filePath = input.toolInput.file_path
    if (!isAllowedPath(filePath, context.config.allowedPaths)) {
      return {
        decision: 'block',
        reason: `File path ${filePath} is not in allowed paths`,
      }
    }
  }
  return { continue: true }
}
```

---

## 五、UserPromptSubmit Hook

### 5.1 功能

在用户输入提交给 LLM 前拦截：

```typescript
// 可以：
// - 清理输入（去除敏感信息）
// - 添加上下文
// - 验证输入
// - 拒绝输入
```

### 5.2 结果类型

```typescript
// UserPromptSubmit Hook 特有输出
interface UserPromptSubmitResult extends HookResult {
  updatedInput?: {
    text?: string           // 修改后的文本
    attachments?: Attachment[]  // 添加附件
  }
  suppressOutput?: boolean
}
```

---

## 六、Hook 配置加载

### 6.1 配置文件位置

```typescript
// 加载顺序（优先级从高到低）：
// 1. .claude/hooks.json（项目本地）
// 2. ~/.claude/hooks.json（用户全局）
// 3. 企业托管 hooks（managed）

const HOOK_CONFIG_PATHS = [
  '.claude/hooks.json',
  '~/.claude/hooks.json',
]
```

### 6.2 Hook Schema 验证

> 文件：`src/utils/settings/types.ts`

```typescript
const HooksSchema = z.object({
  hooks: z.array(z.object({
    event: z.enum(HOOK_EVENTS),
    name: z.string(),
    handler: z.string(),  // 文件路径或 inline code
    config: z.record(z.unknown()).optional(),
  }))
})
```

---

## 七、Plugin Hook 加载

> 文件：`src/utils/plugins/loadPluginHooks.ts`

### 7.1 插件 Hook 注册

```typescript
// 插件可以提供 hook
// 通过 plugin.json 声明

interface PluginManifest {
  hooks: HookDefinition[]
}
```

### 7.2 加载流程

```typescript
async function loadPluginHooks(): Promise<HookDefinition[]> {
  const plugins = await loadAllPluginsCacheOnly()
  return plugins
    .filter(p => p.manifest.hooks)
    .flatMap(p => p.manifest.hooks)
}
```

---

## 八、Hook 执行上下文

### 8.1 AppState

```typescript
// Hook 可以访问和修改 AppState
interface HookContext {
  appState: AppState
  setAppState: (updater: (prev: AppState) => AppState) => void
  // ...
}
```

### 8.2 消息历史

```typescript
// Hook 可以访问当前会话消息
interface HookContext {
  messages: Message[]
  appendMessage: (msg: Message) => void
  // ...
}
```

### 8.3 工具列表

```typescript
// Hook 可以访问可用工具
interface HookContext {
  tools: Tool[]
  // ...
}
```

---

## 九、Hook 安全与隔离

### 9.1 权限控制

```typescript
// Hook 执行在受限上下文
// 不能直接访问文件系统
// 需要通过 Tool 间接操作

// 危险操作需要用户确认
```

### 9.2 超时保护

```typescript
// Hook 执行有超时限制
// 防止恶意或低效 Hook 卡住系统

const HOOK_TIMEOUT_MS = 5000

async function executeHookWithTimeout(
  hook: HookDefinition,
  context: HookContext,
): Promise<HookResult> {
  return Promise.race([
    hook.handler(context),
    timeout(HOOK_TIMEOUT_MS),
  ])
}
```

---

## 十、Hook 与 Skills 的区别

| 特性 | Hook | Skill |
| :--- | :--- | :--- |
| 触发方式 | 事件驱动 | 显式调用 |
| 执行位置 | 生命周期特定点 | 任意位置 |
| 权限 | 受限 | 完整工具访问 |
| 配置 | 声明式 | Markdown 文件 |
| 用途 | 拦截/修改行为 | 扩展功能 |

---

## 下一步

一篇：[15 - 安全审查：Security Review 命令实现](https://skyseraph.github.io/series/cc-source-code/2026/15-security-review)，深入安全审查命令的源码实现。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*