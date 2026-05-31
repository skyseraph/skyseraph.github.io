---
title: "CC源码剖析 #08 · 消息传递：inbound/outbound 架构"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 9
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、消息系统概述

Claude Code 的消息系统是其核心——负责用户输入、LLM 输出、工具调用结果之间的流转。

```
用户输入
    │
    ▼
┌─────────┐
│ Message │ ← discriminated union: user/assistant/system
└────┬────┘
     │
     ├─→ normalizeMessagesForAPI() → Anthropic API
     │      │
     │      ▼
     │   API Response
     │      │
     ├─→ Tool Call 循环
     │      │
     │      ▼
     │   Tool 执行
     │      │
     └─→ 渲染到 REPL UI
```

---

## 二、消息类型体系

> 文件：`src/utils/messages.ts`

### 2.1 核心消息类型

```typescript
// UserMessage — 用户输入
type UserMessage = {
  type: 'user'
  message: {
    content: ContentBlock[]  // text/image/tool_use
  }
  origin?: MessageOrigin
  isMeta?: boolean
  toolUseResult?: boolean    // 工具执行结果
  isCompactSummary?: boolean
}

// AssistantMessage — LLM 输出
type AssistantMessage = {
  type: 'assistant'
  message: {
    content: ContentBlock[]  // text/thinking/tool_use
  }
  isVirtual?: boolean        // 虚拟消息（REPL 内部调用）
  stopReason?: string
  usage?: Usage
}

// SystemMessage — 系统消息
type SystemMessage =
  | SystemLocalCommandMessage   // /命令输出
  | SystemApiErrorMessage       // API 错误
  | SystemBridgeStatusMessage   // Bridge 状态
  | SystemPermissionRetryMessage // 权限重试
  | SystemInformationalMessage   // 信息提示
```

### 2.2 特殊消息类型

```typescript
// ProgressMessage — 长时间运行工具的进度
type ProgressMessage = {
  type: 'progress'
  data: ToolProgressData | HookProgress
}

// AttachmentMessage — 附件（图片/文件）
type AttachmentMessage = {
  type: 'attachment'
  attachment: Attachment
}
```

### 2.3 ContentBlock 类型

```typescript
type ContentBlock =
  | TextBlock
  | ThinkingBlock
  | ToolUseBlock
  | RedactedThinkingBlock

// ToolUseBlock — 工具调用
type ToolUseBlock = {
  type: 'tool_use'
  id: string
  name: string           // Bash/FileEdit/Grep...
  input: object         // 工具参数
  type: 'input JSON'
}

// ToolResultBlock — 工具结果
type ToolResultBlock = {
  type: 'tool_result'
  toolUseId: string
  content: ContentBlock[]
  isError?: boolean
}
```

---

## 三、消息规范化（Normalization）

### 3.1 `normalizeMessagesForAPI`

```typescript
// 将内部 Message[] 转换为 Anthropic API 格式
normalizeMessagesForAPI(
  messages: Message[],
  systemPrompt: string,
  tools: Tool[],
  toolChoice?: ToolChoice
): Promise<APIMessage[]>
```

### 3.2 规范化规则

```typescript
// 1. 虚拟消息（isVirtual）过滤掉
// 2. 工具调用合并到 tool_use
// 3. 结果转为 tool_result
// 4. thinking block 处理（保留/删除）
// 5. Token 计数更新
```

### 3.3 消息裁剪

```typescript
// 当消息过长时触发 compact
partialCompactConversation(
  messages: Message[],
  direction: 'pre' | 'post'
): Promise<Message[]>
```

---

## 四、inbound/outbound 架构

### 4.1 inbound（入站消息）

来自用户、工具执行、系统事件的消息：

```typescript
// 用户输入
user input → UserMessage

// 工具执行结果
ToolResult → UserMessage（toolUseResult: true）

// 系统事件
SystemEvent → SystemMessage
```

### 4.2 outbound（出站消息）

发给 LLM API 的消息：

```typescript
// API 请求
normalizeMessagesForAPI(messages)
  → API format
  → POST /v1/messages

// 流式响应
SSE stream
  → parse events
  → AssistantMessage
```

### 4.3 消息流转图

```
┌──────────────────────────────────────────────────────────────┐
│                      REPL UI                              │
│  PromptInput → user message → Message[] → Messages.tsx    │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    QueryEngine                              │
│  normalizeMessagesForAPI() → API Messages                  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Anthropic API                             │
│  Streaming Response → parseStreamEvent()                   │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    Tool Call 循环                          │
│  tool_use → Tool.call() → ToolResult → tool_result         │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    渲染回 UI                                │
│  Message[] → Messages.tsx → 用户看到结果                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 五、流式事件处理

> 文件：`src/query.ts`

### 5.1 流式解析

```typescript
type StreamEvent =
  | { type: 'content_block_start'; index: number }
  | { type: 'content_block_delta'; index: number; delta: Delta }
  | { type: 'content_block_stop'; index: number }
  | { type: 'message_delta'; delta: MessageDelta; usage }
  | { type: 'message_stop' }
```

### 5.2 增量更新

```typescript
// content_block_delta 用于增量构建：
// - text delta → 追加到文本块
// - thinking delta → 追加到思考块
// - input_json_delta → 追加到工具参数
```

---

## 六、消息队列管理

> 文件：`src/utils/messageQueueManager.ts`

### 6.1 队列类型

```typescript
interface MessageQueueManager {
  enqueue(msg: Message): void
  dequeue(): Message | undefined
  peek(): Message | undefined
  size(): number
}
```

### 6.2 优先级队列

某些消息需要优先处理（如权限请求），队列支持优先级：

```typescript
enqueue(msg: Message, priority: 'high' | 'normal' | 'low')
```

---

## 七、Bridge 消息传递

> 文件：`src/bridge/bridgeMessaging.ts`

### 7.1 桥接消息筛选

```typescript
// 只转发这些消息类型到 IDE
export function isEligibleBridgeMessage(m: Message): boolean {
  if ((m.type === 'user' || m.type === 'assistant') && m.isVirtual) {
    return false  // 虚拟消息不转发
  }
  return (
    m.type === 'user' ||
    m.type === 'assistant' ||
    (m.type === 'system' && m.subtype === 'local_command')
  )
}
```

### 7.2 标题提取

```typescript
// 从第一条用户消息提取会话标题
export function extractTitleText(m: Message): string | undefined {
  if (m.type !== 'user' || m.isMeta || m.toolUseResult) {
    return undefined
  }
  // 提取文本内容的前 N 个词
}
```

### 7.3 Ingress 消息处理

```typescript
export function handleIngressMessage(
  data: string,
  recentPostedUUIDs: BoundedUUIDSet,   // 防回声
  recentInboundUUIDs: BoundedUUIDSet,  // 防重放
  onInboundMessage,
  onPermissionResponse,
  onControlRequest,
): void
```

---

## 八、消息类型守卫

### 8.1 类型判断

```typescript
// 判断消息类型
function isUserMessage(m: Message): m is UserMessage {
  return m.type === 'user'
}

function isAssistantMessage(m: Message): m is AssistantMessage {
  return m.type === 'assistant'
}

function isSystemMessage(m: Message): m is SystemMessage {
  return m.type === 'system'
}

// 判断内容块类型
function isTextBlock(b: ContentBlock): b is TextBlock {
  return b.type === 'text'
}

function isToolUseBlock(b: ContentBlock): b is ToolUseBlock {
  return b.type === 'tool_use'
}
```

### 8.2 消息谓词

> 文件：`src/utils/messagePredicates.ts`

```typescript
// 消息谓词集合
isHumanTurn(m: Message): boolean       // 人类用户消息
isAgentTurn(m: Message): boolean        // Agent 消息
isSyntheticMessage(m: Message): boolean  // 合成消息
isCompactBoundaryMessage(m: Message): boolean  // 压缩边界
```

---

## 九、消息存储与会话恢复

### 9.1 会话持久化

```typescript
// 保存消息到磁盘
saveTranscript(sessionId: string, messages: Message[])

// 从磁盘加载
loadTranscript(sessionId: string): Message[]

// 转换为可恢复格式
serializeForSession(messages: Message[]): string
deserializeFromSession(data: string): Message[]
```

### 9.2 会话恢复

```typescript
// resume 时重新构造消息历史
processResumedConversation(
  sessionId: string,
  opts: { direction?: 'newest' | 'oldest' }
): Promise<Message[]>
```

---

## 十、工具结果存储

> 文件：`src/utils/toolResultStorage.ts`

### 10.1 内容替换状态

```typescript
type ContentReplacementState = {
  records: ContentReplacementRecord[]
  budgetUsed: number
  budgetTotal: number
}

type ContentReplacementRecord = {
  toolUseId: string
  originalSize: number
  compressedSize: number
  replacementRef: string  // 可按需展开的引用
}
```

### 10.2 大结果处理

当工具结果超过预算时：
1. 压缩或截断结果
2. 存储到磁盘
3. 用引用替换
4. 用户可按需展开

---

## 下一步

下一篇：[09 - 权限系统：PermissionCallbacks 与安全边界](./09-permission-system.md)，深入权限检查、PermissionCallbacks 与安全边界机制。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*