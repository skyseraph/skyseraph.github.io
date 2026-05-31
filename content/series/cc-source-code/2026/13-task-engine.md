---
title: "CC源码剖析 #13 · Task 执行引擎：从创建到完成的完整流程"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 14
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Task 系统定位

Task 是 Claude Code 的**后台任务执行单元**——允许 Agent 派生子任务并行工作，结果汇总到主会话。

```
主会话（Main REPL）
    │
    ├─→ TaskCreateTool → 创建后台任务
    │       │
    │       ▼
    │   ┌──────────┐
    │   │  Task    │ ← 后台运行
    │   └────┬─────┘
    │        │
    │        │ task-notification
    │        ▼
    └────── Agent 结果汇总
```

---

## 二、Task 类型体系

> 文件：`src/tasks/types.ts`

### 2.1 Task 类型列表

```typescript
export type TaskState =
  | LocalShellTaskState      // 本地 Shell 任务
  | LocalAgentTaskState     // 本地 Agent 任务
  | RemoteAgentTaskState    // 远程 Agent 任务
  | InProcessTeammateTaskState  // 进程内队友任务
  | LocalWorkflowTaskState  // 本地工作流任务
  | MonitorMcpTaskState     // MCP 监控任务
  | DreamTaskState          // 背景做梦任务
```

### 2.2 Task 状态

```typescript
type TaskStatus =
  | 'pending'    // 等待执行
  | 'running'    // 执行中
  | 'completed'  // 完成
  | 'failed'     // 失败
  | 'killed'     // 被停止
  | 'paused'     // 暂停
```

### 2.3 后台任务判断

```typescript
// 判断任务是否显示在后台任务指示器
export function isBackgroundTask(task: TaskState): boolean {
  if (task.status !== 'running' && task.status !== 'pending') {
    return false
  }
  // 前台任务（isBackgrounded === false）不显示
  if ('isBackgrounded' in task && task.isBackgrounded === false) {
    return false
  }
  return true
}
```

---

## 三、Task 创建

### 3.1 TaskCreateTool

> 文件：`src/tools/TaskCreateTool/TaskCreateTool.ts`

```typescript
// 创建新任务
const TaskCreateTool = {
  inputSchema: z.object({
    prompt: z.string(),        // 任务描述
    taskType: z.enum([...]).default('agent'),
    agentType?: string,        // Agent 类型
    background?: boolean,      // 是否后台运行
  }),

  async call(args, context, canUseTool) {
    // 1. 验证参数
    // 2. 创建 Task 实例
    // 3. 如果 background=true，设为后台任务
    // 4. 返回 taskId
  }
}
```

### 3.2 Task 类型决定

| taskType | 执行方式 | 说明 |
| :--- | :--- | :--- |
| `shell` | `LocalShellTask` | 执行 shell 命令 |
| `agent` | `LocalAgentTask` | 本地 Agent |
| `remote_agent` | `RemoteAgentTask` | 远程 Agent |
| `teammate` | `InProcessTeammateTask` | 队友（进程内） |
| `workflow` | `LocalWorkflowTask` | 工作流 |
| `monitor` | `MonitorMcpTask` | MCP 监控 |

---

## 四、Task 执行引擎

### 4.1 LocalAgentTask

> 文件：`src/tasks/LocalAgentTask/LocalAgentTask.ts`

```typescript
interface LocalAgentTaskState {
  taskId: string
  status: TaskStatus
  agentId: string
  prompt: string
  model?: string
  tools: string[]
  isBackgrounded: boolean
  createdAt: number
  startedAt?: number
  completedAt?: number
  result?: string
  error?: string
}
```

### 4.2 Agent 执行流程

```typescript
async function runLocalAgentTask(task: LocalAgentTaskState): Promise<void> {
  // 1. 初始化 Agent 上下文
  // 2. 设置系统提示
  // 3. 注入任务 prompt
  // 4. 执行 Tool Call 循环
  // 5. 返回结果或错误
}
```

### 4.3 In-Process Teammate Task

> 文件：`src/tasks/InProcessTeammateTask/InProcessTeammateTask.tsx`

```typescript
// 进程内队友任务
// 与主会话共享内存
// 通过 mailbox 通信

interface InProcessTeammateTaskState {
  taskId: string
  status: TaskStatus
  teammateId: string
  mailbox: Mailbox
  // 共享消息队列
}
```

---

## 五、Task 状态管理

### 5.1 TaskStore

```typescript
// 全局任务存储
interface TaskStore {
  tasks: Map<string, TaskState>
  addTask(task: TaskState): void
  updateTask(taskId: string, update: Partial<TaskState>): void
  removeTask(taskId: string): void
  getTask(taskId: string): TaskState | undefined
}
```

### 5.2 状态持久化

```typescript
// 任务状态保存到会话存储
// 恢复时可以重建任务

saveTaskState(taskId: string, state: TaskState): void
loadTaskState(taskId: string): TaskState | undefined
```

---

## 六、Task 生命周期事件

### 6.1 状态变更事件

```typescript
// 状态变更回调
onTaskStatusChange((taskId, oldStatus, newStatus) => {
  // taskId 创建的任务状态变更
})

// 可能的事件序列：
// pending → running → completed
// pending → running → failed
// running → killed
```

### 6.2 结果回调

```typescript
// 任务完成时的回调
onTaskComplete((taskId, result) => {
  // 处理任务结果
})

onTaskFailure((taskId, error) => {
  // 处理任务失败
})
```

---

## 七、Task 停止

> 文件：`src/tasks/stopTask.ts`

### 7.1 TaskStopTool

```typescript
const TaskStopTool = {
  inputSchema: z.object({
    taskId: z.string(),
    reason: z.string().optional(),
  }),

  async call(args, context, canUseTool) {
    // 1. 查找任务
    // 2. 发送停止信号
    // 3. 等待任务清理
    // 4. 更新状态为 killed
  }
}
```

### 7.2 停止机制

```typescript
// 任务可以在任意时刻检查停止信号
// 响应 interrupt 信号

class Task {
  private abortController: AbortController

  async stop(): Promise<void> {
    this.abortController.abort()
  }

  isStopped(): boolean {
    return this.abortController.signal.aborted
  }
}
```

---

## 八、Task 结果传递

### 8.1 结果格式

```typescript
// 任务结果通过 task-notification 传递
interface TaskNotification {
  type: 'task-notification'
  taskId: string
  status: 'completed' | 'failed' | 'killed'
  summary: string
  result?: string
  usage?: {
    total_tokens: number
    tool_uses: number
    duration_ms: number
  }
}
```

### 8.2 消息注入

```typescript
// 任务结果注入到主会话消息流
// 作为 user-role message 到达（区分于人类消息）

injectTaskNotification(taskId: string, result: TaskNotification): void
```

---

## 九、Task 列表 UI

> 文件：`src/components/TaskListV2.tsx`

### 9.1 任务列表组件

```typescript
// 显示所有后台任务
// 状态、进度、结果

const TaskListV2: React.FC = () => {
  const tasks = useTasksV2WithCollapseEffect()

  return (
    <Box>
      {tasks.map(task => (
        <TaskItem key={task.taskId} task={task} />
      ))}
    </Box>
  )
}
```

### 9.2 任务项显示

```
┌────────────────────────────────────────┐
│ 🔄 Task Name              [停止] [展开] │
│    状态: 运行中                    │
│    进度: 3/10 工具调用              │
└────────────────────────────────────────┘
```

---

## 十、Task 与其他模块的关系

```
TaskCreateTool
  │
  ├─→ LocalAgentTask / RemoteAgentTask
  │       │
  │       ├─→ QueryEngine（Tool Call 循环）
  │       ├─→ Coordinator（多 Agent 编排）
  │       └─→ Message 系統（结果传递）
  │
  └─→ TaskListV2（UI 显示）
```

---

## 下一步

下一篇：[14 - Hook 系统：生命周期拦截点](https://skyseraph.github.io/series/cc-source-code/2026/14-hooks)，深入 Hook 类型定义、生命周期拦截与扩展点机制。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*