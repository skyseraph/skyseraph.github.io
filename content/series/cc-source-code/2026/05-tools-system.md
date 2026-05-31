---
title: "CC源码剖析 #05 · Tools 系统：工具定义、注册与执行"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 6
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Tool 在 Agent 架构中的位置

Tool 是 Agent 与外界交互的接口。每个 Tool 是一个自包含模块，包含输入 Schema、权限模型和执行逻辑。

```
LLM 决定调用 Tool
       │
       ▼
    Tool.call(args, context, canUseTool, parentMessage, onProgress)
       │
       ├─ Zod Schema 验证输入
       ├─ Permission 检查
       ├─ 执行逻辑
       └─ 返回 ToolResult + 新消息
```

---

## 二、Tool 基类定义

> 文件：`src/Tool.ts`，约 1,500 行

### 2.1 核心类型签名

```typescript
export type Tool<
  Input extends AnyObject = AnyObject,  // Zod 输入 Schema
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = {
  // 可选别名（用于工具重命名后的向后兼容）
  aliases?: string[]

  // 工具调用入口
  call(
    args: z.infer<Input>,
    context: ToolUseContext,
    canUseTool: CanUseToolFn,
    parentMessage: AssistantMessage,
    onProgress?: ToolCallProgress<P>,
  ): Promise<ToolResult<Output>>

  // 生成工具描述（用于 prompt）
  description(
    input: z.infer<Input>,
    options: {
      isNonInteractiveSession: boolean
      toolPermissionContext: ToolPermissionContext
      tools: Tools
    },
  ): Promise<string>

  // Zod 输入 Schema
  readonly inputSchema: Input

  // 可选 JSON Schema（用于 MCP 工具）
  readonly inputJSONSchema?: ToolInputJSONSchema

  // 并发安全性
  isConcurrencySafe(input: z.infer<Input>): boolean

  // 是否启用
  isEnabled(): boolean

  // 是否只读
  isReadOnly(input: z.infer<Input>): boolean

  // 是否破坏性（删除/覆盖）
  isDestructive?(input: z.infer<Input>): boolean

  // 用户提交新消息时的行为
  interruptBehavior?(): 'cancel' | 'block'

  // 是否为搜索/读取操作（决定 UI 折叠显示）
  isSearchOrReadCommand?(input: z.infer<Input>): {
    isSearch: boolean
    isRead: boolean
    isList?: boolean
  }

  // 是否延迟加载（需要 ToolSearch 预热）
  readonly shouldDefer?: boolean

  // 是否始终加载（turn 1 就出现）
  readonly alwaysLoad?: boolean
}
```

### 2.2 ToolResult 结构

```typescript
export type ToolResult<T> = {
  data: T
  // 可选：工具执行过程中产生的新消息
  newMessages?: (
    | UserMessage
    | AssistantMessage
    | AttachmentMessage
    | SystemMessage
  )[]
  // 内容替换状态（用于工具结果预算）
  contextModifier?: (context: ToolUseContext) => ToolUseContext
  // MCP 协议元数据
  mcpMeta?: {
    _meta?: Record<string, unknown>
    structuredContent?: Record<string, unknown>
  }
}
```

### 2.3 ToolUseContext — 执行上下文

```typescript
export type ToolUseContext = {
  options: {
    commands: Command[]
    debug: boolean
    mainLoopModel: string
    tools: Tools
    verbose: boolean
    thinkingConfig: ThinkingConfig
    mcpClients: MCPServerConnection[]
    mcpResources: Record<string, ServerResource[]>
    isNonInteractiveSession: boolean
    agentDefinitions: AgentDefinitionsResult
    maxBudgetUsd?: number
    customSystemPrompt?: string
    appendSystemPrompt?: string
    querySource?: QuerySource
    refreshTools?: () => Tools
  }
  abortController: AbortController
  readFileState: FileStateCache
  getAppState(): AppState
  setAppState(f: (prev: AppState) => AppState): void
  // ... 50+ 字段
  messages: Message[]
}
```

---

## 三、Tool 注册中心

> 文件：`src/tools.ts`，约 800 行

### 3.1 静态注册

```typescript
// 基础工具（始终启用）
import { AgentTool } from './tools/AgentTool/AgentTool.js'
import { SkillTool } from './tools/SkillTool/SkillTool.js'
import { BashTool } from './tools/BashTool/BashTool.js'
import { FileEditTool } from './tools/FileEditTool/FileEditTool.js'
import { FileReadTool } from './tools/FileReadTool/FileReadTool.js'
import { FileWriteTool } from './tools/FileWriteTool/FileWriteTool.js'
import { GlobTool } from './tools/GlobTool/GlobTool.js'
// ... 30+ 工具
```

### 3.2 Feature Flag 条件注册

```typescript
// COORDINATOR_MODE
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js')
  : null

// AGENT_TRIGGERS: 定时任务工具
const cronTools = feature('AGENT_TRIGGERS')
  ? [
      require('./tools/ScheduleCronTool/CronCreateTool.js').CronCreateTool,
      require('./tools/ScheduleCronTool/CronDeleteTool.js').CronDeleteTool,
      require('./tools/ScheduleCronTool/CronListTool.js').CronListTool,
    ]
  : []

// KAIROS: 睡眠工具
const SleepTool = feature('PROACTIVE') || feature('KAIROS')
  ? require('./tools/SleepTool/SleepTool.js').SleepTool
  : null
```

### 3.3 内置 Agent Tool 子类型

```typescript
// AgentTool 内置的 subagent_type
built-in/
├── claudeCodeGuideAgent.ts   // /claude-code-guide
├── exploreAgent.ts           // /explore
├── generalPurposeAgent.ts   // /general-purpose
├── planAgent.ts             // /plan
├── statuslineSetup.ts        // /statusline-setup
└── verificationAgent.ts     // /verify
```

---

## 四、核心工具详解

### 4.1 BashTool

| 特性 | 值 |
| :--- | :--- |
| 权限模式 | `auto` / `ask` / `reject` |
| 沙箱 | 可选（`shouldUseSandbox()`） |
| 破坏性检测 | `destructiveCommandWarning.ts` |
| 路径验证 | `pathValidation.ts` |
| 只读验证 | `readOnlyValidation.ts` |

### 4.2 FileEditTool

最常用工具，字符串替换编辑：

```typescript
// 输入 Schema
{
  file_path: string,      // 必须
  old_string: string,     // 必须（精确匹配）
  new_string?: string,    // 可选（为空则是删除）
  older_than?: number,   // 时间戳守卫
  dry_run?: boolean,      // 试运行
}
```

**精确匹配规则**：`old_string` 必须在文件中唯一存在，否则报错。

### 4.3 AgentTool

用于派生 Sub-agent 或 Worktree：

```typescript
{
  prompt: string,          // Agent 的任务描述
  subagent_type?: string,   // 'worker' | 内置 agent 名
  model?: string,          // 可选模型覆盖
  agentId?: string,        // 继续已有 agent
  description?: string,    // 任务描述（用于日志）
}
```

### 4.4 SkillTool

执行用户定义的 Skill：

```typescript
{
  skill: string,           // Skill 名称
  args?: string,           // 传递给 skill 的参数
}
```

### 4.5 MCPTool

调用 MCP 服务器工具：

```typescript
{
  tool: string,            // MCP 工具名
  arguments: Record<string, unknown>,  // 工具参数
  server?: string,        // 可选：指定服务器
}
```

---

## 五、权限系统

### 5.1 权限模式

```typescript
type PermissionMode =
  | 'default'      // 用户配置决定
  | 'auto'         // 自动批准已知安全操作
  | 'ask'           // 每次询问
  | 'reject'        // 拒绝所有危险操作
  | 'bypass'        // 绕过（需特殊标志）
```

### 5.2 Permission 检查流程

```
Tool.call()
  │
  ├─ canUseTool(toolName, input)  ← 检查是否可执行
  │     │
  │     ├─ alwaysAllowRules 匹配？→ 直接批准
  │     ├─ alwaysDenyRules 匹配？→ 直接拒绝
  │     ├─ 权限模式 = auto？→ 检查历史决策
  │     └─ 权限模式 = ask？→ 弹出 UI 对话框
  │
  └─ 执行 tool logic
```

### 5.3 规则类型

```typescript
type ToolPermissionRulesBySource = {
  [source: string]: {
    tool: string
    allow?: boolean
    deny?: boolean
  }
}
```

---

## 六、工具搜索（Tool Search）

### 6.1 延迟加载机制

```typescript
// 当工具设置 shouldDefer: true 时
// 模型首轮只看到 ToolSearchTool
// 实际工具调用需要先经过 ToolSearch 检索

const ToolSearchTool = {
  shouldDefer: false,  // ToolSearchTool 自身不需要延迟
  alwaysLoad: true,   // turn 1 就出现
}
```

### 6.2 关键字搜索

每个 Tool 可以设置 `searchHint` 关键字：

```typescript
// FileReadTool
searchHint: 'jupyter notebook cell'  // 帮助 ToolSearch 找到它
```

---

## 七、并发安全

### 7.1 `isConcurrencySafe`

```typescript
// 并发安全工具可以同时运行多个实例
// 并发不安全工具同时只能有一个实例在运行

// BashTool: 不安全（共享终端状态）
isConcurrencySafe = () => false

// GlobTool: 安全（只读）
isConcurrencySafe = () => true

// FileEditTool: 不安全（文件写入）
isConcurrencySafe = () => false
```

### 7.2 `interruptBehavior`

```typescript
// 用户在新消息到达时中断正在运行的工具

// 'cancel' — 停止工具，丢弃结果（如 BashTool）
interruptBehavior = () => 'cancel'

// 'block' — 保持运行，新消息排队等待（如 WebSearchTool）
interruptBehavior = () => 'block'
```

---

## 八、工具结果预算（Content Replacement）

当工具结果非常大时，系统会触发内容替换：

```typescript
contentReplacementState?: ContentReplacementState

// 超出预算时：
// 1. 工具结果被压缩/截断
// 2. 替换为引用（可在后续按需展开）
// 3. 节省 context window
```

---

## 九、进度回调

```typescript
type ToolCallProgress<P extends ToolProgressData> = (
  progress: ToolProgress<P>,
) => void

type ToolProgress<P> = {
  toolUseID: string
  data: P
}

// 使用场景：长时间运行的工具（如 Bash执行）
onProgress?.({ toolUseID, data: { type: 'bash', output: '...' } })
```

---

## 十、工具 vs 命令

| 特性 | Tool | Command |
| :--- | :--- | :--- |
| 执行方式 | LLM 决定调用 | 用户显式触发 |
| 输入 | Zod Schema | 字符串参数 |
| 权限 | 权限系统 | 无特殊权限 |
| 触发 | `/tool-name` 或自动 | 只能显式调用 |
| 上下文 | ToolUseContext | Context |

---

## 下一步

下一篇：[06 - Skills 加载与执行机制](./06-skills-system.md)，深入 `skills/` 模块的动态加载、Skill 定义格式与执行流程。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*