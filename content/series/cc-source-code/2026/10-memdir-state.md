---
title: "CC源码剖析 #10 · 状态管理：memdir 与会话持久化"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 11
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、memdir 定位

memdir（Memory Directory）是 Claude Code 的**会话持久化与记忆系统**——负责在会话之间保存上下文，让 Agent 能够"记住"之前的对话内容。

```
会话开始
    │
    ├─→ 读取 MEMORY.md
    │       │
    │       ▼
    │    系统提示 + 记忆内容
    │
    ├─→ 会话进行中...
    │
    └─→ 会话结束
            │
            ├─→ 更新 MEMORY.md（新增记忆）
            ├─→ 保存会话记录
            └─→ 保存会话元数据
```

---

## 二、目录结构

> 文件：`src/memdir/paths.ts`

### 2.1 路径解析

```typescript
export function getMemoryBaseDir(): string {
  // 优先级：
  // 1. CLAUDE_CODE_REMOTE_MEMORY_DIR 环境变量（CCR 远程模式）
  // 2. ~/.claude（默认配置目录）
}

// 内存目录布局
~/.claude/
└── memory/
    └── projects/
        └── {sanitized-cwd}/
            └── memory/
                ├── MEMORY.md          # 主入口
                ├── {topic}.md        # 主题记忆文件
                └── {session}/        # 按会话的记录
```

### 2.2 路径安全验证

```typescript
// SECURITY: 验证内存路径，防止路径遍历攻击
function validateMemoryPath(raw: string | undefined): string | undefined {
  // 拒绝：
  // - 相对路径（可能被解释为 CWD 相对）
  // - 根目录（"/", "C:"）
  // - UNC 路径（\\server\share）
  // - 含 null 字节
}
```

### 2.3 开关控制

```typescript
export function isAutoMemoryEnabled(): boolean {
  // 1. CLAUDE_CODE_DISABLE_AUTO_MEMORY = 1 → 关闭
  // 2. CLAUDE_CODE_SIMPLE (--bare) → 关闭
  // 3. CCR 无持久化 → 关闭
  // 4. settings.json autoMemoryEnabled
  // 5. 默认：开启
}
```

---

## 三、MEMORY.md 入口

> 文件：`src/memdir/memdir.ts`

### 3.1 入口文件格式

```markdown
---
name: "memory"
description: "Auto memory for Claude Code sessions"
---

# Memory

## Index
- [[topic-a]] — Topic A summary
- [[topic-b]] — Topic B summary

## Individual

### Topic A
Topic A detail...

## What Not to Save
- API keys
- Passwords
- Tokens

## When to Access
Use for context on user's project and preferences.
```

### 3.2 大小限制

```typescript
const MAX_ENTRYPOINT_LINES = 200
const MAX_ENTRYPOINT_BYTES = 25_000

// 超限时截断并添加警告
function truncateEntrypointContent(raw: string): EntrypointTruncation {
  // 1. 先按行截断（200行）
  // 2. 再按字节截断（25KB）
  // 3. 添加警告信息
}
```

---

## 四、记忆类型

> 文件：`src/memdir/memoryTypes.ts`

### 4.1 记忆分类

```typescript
const MEMORY_FRONTMATTER_EXAMPLE = `
# 记忆类型说明

## Index（索引）
短条目，每个一行，格式：- [[topic]] — 摘要
用于快速浏览和检索

## Individual（个体记忆）
详细记忆，每个主题一个文件
格式：### Topic Name\n\n详细描述...

## What Not to Save（禁止保存）
敏感信息列表
- API 密钥
- 密码
- Token

## When to Access（访问时机）
说明何时应该访问这些记忆
`
```

### 4.2 记忆内容规则

```typescript
// 应该保存：
// - 项目结构
// - 用户偏好
// - 重要的决策和结论
// - 上下文信息（当前任务、目标）

// 不应该保存：
// - API 密钥
// - 密码
// - 敏感凭证
// - 训练数据（版权问题）
```

---

## 五、记忆提取（Extract Memories）

### 5.1 背景 Agent 提取

```typescript
// 会话结束时，背景 Agent 提取新记忆
export function isExtractModeActive(): boolean {
  // GrowthBook flag: tengu_passport_quail
  // 只有交互式会话才能提取
}
```

### 5.2 提取流程

```typescript
// 1. 分析会话消息
// 2. 识别有价值的信息点
// 3. 更新 MEMORY.md 索引
// 4. 创建或更新主题文件
```

### 5.3 增量更新

```typescript
// 只更新新增内容，不重复已有记忆
// hasMemoryWritesSince() 检查是否有新的写入
```

---

## 六、会话持久化

### 6.1 会话存储

> 文件：`src/utils/sessionStorage.ts`

```typescript
interface SessionStorage {
  sessionId: string
  messages: Message[]
  metadata: {
    title: string
    createdAt: number
    lastActiveAt: number
    model: string
    tools: string[]
  }
  attachments: Attachment[]
}

// 保存
saveSession(sessionId, messages, metadata)

// 加载
loadSession(sessionId): SessionStorage

// 搜索
searchSessions(query: string): SessionSummary[]
```

### 6.2 会话恢复

```typescript
// resume 时重建消息历史
loadConversationForResume(sessionId: string): Message[]

// 处理恢复后的会话
processResumedConversation(sessionId: string): Promise<Message[]>
```

---

## 七、文件历史（File History）

> 文件：`src/utils/fileHistory.ts`

### 7.1 文件状态追踪

```typescript
interface FileHistoryState {
  files: Map<string, FileState>
  sessions: SessionHistory[]
}

interface FileState = {
  path: string
  changes: FileChange[]
  lastSeen: number
}

interface FileChange = {
  type: 'edit' | 'create' | 'delete'
  timestamp: number
  sessionId: string
  diff?: string
}
```

### 7.2 文件重写追踪

```typescript
// 检测文件是否被外部修改
// 如果是，提供重新加载选项

fileHistoryMakeSnapshot(): FileHistorySnapshot
fileHistoryRewind(snapshot: FileHistorySnapshot): void
```

---

## 八、团队记忆（Team Memory）

> 文件：`src/memdir/teamMemPaths.ts`

### 8.1 TEAMMEM Feature Flag

```typescript
const teamMemPaths = feature('TEAMMEM')
  ? require('./teamMemPaths.js')
  : null
```

### 8.2 跨会话记忆同步

```typescript
// 团队成员共享的记忆
// 存储在共享位置
// 所有团队成员可见
```

---

## 九、Memory 与 System Prompt

### 9.1 构建 Memory Prompt

```typescript
// 将 MEMORY.md 内容注入系统提示
function buildMemoryPrompt(): string {
  const memoryFiles = getMemoryFiles()
  const memoryContent = memoryFiles
    .map(f => readFile(f))
    .join('\n\n')
  return `## Memory\n\n${memoryContent}`
}
```

### 9.2 访问时机

```typescript
// 每次新会话开始时加载
// Turn 开始时加载相关记忆
// 显式请求时加载（/remember 命令）
```

---

## 十、相关命令

| 命令 | 功能 |
| :--- | :--- |
| `/remember` | 显示/搜索记忆 |
| `/forget` | 删除特定记忆 |
| `/memory` | 管理记忆设置 |

---

## 下一步

下一篇：[11 - 插件系统：Plugin 架构与生命周期](https://skyseraph.github.io/series/cc-source-code/2026/11-plugin-system)，深入 `plugins/` 模块的插件架构与生命周期管理。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*