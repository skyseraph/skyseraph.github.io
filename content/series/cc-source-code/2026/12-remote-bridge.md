---
title: "CC源码剖析 #12 · 跨进程通信：RemoteBridge 与远程模式"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 13
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、远程模式定位

远程模式允许 Claude Code 通过 Bridge 与远程运行的 CLI 实例通信，使得 IDE 可以在本地但 Agent 执行在远程。

```
本地 IDE (VSCode)
    │
    │ UDS IPC
    │
┌───▼──────────┐
│  Bridge Main  │ ← 本地桥接进程
└───┬──────────┘
    │ WebSocket / HTTPS
    │
┌───▼──────────┐
│ Remote CLI    │ ← 远程机器上运行
│ (REPL)        │
└───────────────┘
```

---

## 二、RemoteBridge 架构

> 文件：`src/bridge/remoteBridgeCore.ts`

### 2.1 核心组件

```typescript
interface RemoteBridgeCore {
  // 连接管理
  connect(sessionId: string): Promise<void>
  disconnect(): Promise<void>

  // 消息传递
  sendMessage(msg: SDKMessage): void
  onMessage(handler: (msg: SDKMessage) => void): void

  // 状态同步
  syncState(): Promise<State>
  onStateChange(handler: (state: State) => void): void
}
```

### 2.2 传输协议

```typescript
// 支持多种传输方式
type Transport =
  | 'websocket'   // WebSocket 连接
  | 'ssh'         // SSH 隧道
  | 'http'        // HTTP 流（stream-json）

// 传输选择逻辑：
// 1. 优先 WebSocket（低延迟）
// 2. SSH（企业防火墙环境）
// 3. HTTP（最后兜底）
```

---

## 三、SSH 会话

> 文件：`src/ssh/createSSHSession.ts`

### 3.1 SSH 会话管理

```typescript
interface SSHSession {
  sessionId: string
  host: string
  port: number
  user: string
  auth: SSHAuth  // password | key | agent
  process: ChildProcess
}

// 创建 SSH 会话
async function createSSHSession(config: SSHConfig): Promise<SSHSession> {
  // 1. 建立 SSH 连接
  // 2. 启动远程 CLI 进程
  // 3. 建立双向通信
  // 4. 返回会话句柄
}
```

### 3.2 认证方式

```typescript
type SSHAuth =
  | { type: 'password'; password: string }
  | { type: 'key'; keyPath: string; passphrase?: string }
  | { type: 'agent' }  // SSH Agent 转发
```

### 3.3 SSH 转发模式

```typescript
// 本地端口转发：远程 CLI 的端口映射到本地
// 使得 IDE 可以像连接本地一样连接远程

// Agent forwarding：让远程 Agent 感知本地 IDE 上下文
```

---

## 四、WebSocket 传输

> 文件：`src/utils/mcpWebSocketTransport.ts`

### 4.1 WebSocket 配置

```typescript
interface WebSocketTransportConfig {
  url: string
  headers?: Record<string, string>
  reconnect?: boolean
  heartbeatInterval?: number
}

// 心跳保活
// 自动重连
// 消息队列（离线缓冲）
```

### 4.2 消息序列化

```typescript
// 使用 JSON-RPC 2.0 格式
interface JSONRPCMessage {
  jsonrpc: '2.0'
  id?: string | number
  method: string
  params?: unknown
}

// 支持批处理
// 双向通信
```

---

## 五、Session 管理

> 文件：`src/remote/RemoteSessionManager.ts`

### 5.1 远程会话状态

```typescript
interface RemoteSession {
  sessionId: string
  remoteId: string
  status: 'connecting' | 'connected' | 'disconnected' | 'error'
  startTime: number
  lastActivity: number
  transport: Transport
}
```

### 5.2 会话恢复

```typescript
// 断线后尝试恢复
// 恢复时重建状态
// 消息不丢失

async function resumeRemoteSession(sessionId: string): Promise<void> {
  // 1. 重连传输层
  // 2. 请求远程状态
  // 3. 同步本地状态
  // 4. 恢复消息流
}
```

---

## 六、消息路由

### 6.1 入站消息（Inbound）

```typescript
// IDE → Bridge → Remote CLI
// 用于：
// - 用户输入
// - 文件变更通知
// - IDE 上下文

interface InboundMessage {
  type: 'user_message' | 'ide_context' | 'file_change'
  payload: unknown
  timestamp: number
}
```

### 6.2 出站消息（Outbound）

```typescript
// Remote CLI → Bridge → IDE
// 用于：
// - Agent 输出
// - 工具执行结果
// - 状态更新

interface OutboundMessage {
  type: 'assistant_message' | 'tool_result' | 'status_update'
  payload: unknown
  timestamp: number
}
```

### 6.3 消息队列

```typescript
// 当连接断开时，消息缓冲到队列
// 重连后按序发送
// 防止消息丢失

class MessageQueue {
  enqueue(msg: Message): void
  flush(): Message[]
  clear(): void
}
```

---

## 七、Direct Connect

> 文件：`src/server/createDirectConnectSession.ts`

### 7.1 直接连接模式

```typescript
// 不通过 Bridge，直接连接远程 CLI
// 适用于信任的网络环境

interface DirectConnectConfig {
  host: string
  port: number
  authToken: string
  sessionId: string
}

// 使用流式 HTTP（stream-json）
// 双向通信
```

### 7.2 认证

```typescript
// Token 认证
// Token 在连接时交换
// 支持过期和刷新
```

---

## 八、状态同步

### 8.1 同步协议

```typescript
// 定期同步状态
// 状态包括：
// - 消息历史
// - 文件系统状态
// - 工具状态

interface StateSnapshot {
  sessionId: string
  messages: Message[]
  files: FileState[]
  tools: Tool[]
  timestamp: number
}
```

### 8.2 差异同步

```typescript
// 不传输完整状态
// 只传输差异（diff）

interface StateDiff {
  added: Message[]
  modified: FileState[]
  removed: string[]  // file paths
}
```

---

## 九、性能优化

### 9.1 消息压缩

```typescript
// 大消息压缩传输
// 支持：
// - gzip
// - brotli

compressMessage(msg: Message, threshold: number): CompressedMessage
```

### 9.2 流式传输

```typescript
// 避免大消息缓冲
// 流式处理
// 边收边处理
```

### 9.3 连接池

```typescript
// 复用连接
// 减少建立连接的开销

class ConnectionPool {
  acquire(): Connection
  release(conn: Connection): void
}
```

---

## 十、安全考虑

### 10.1 传输加密

```typescript
// 所有传输使用 TLS
// SSH 隧道加密
// WebSocket over WSS
```

### 10.2 认证与授权

```typescript
// Bearer Token
// OAuth 2.0（企业环境）
// SSH Key
```

### 10.3 网络隔离

```typescript
// 企业网络隔离
// VPC 配置
// 防火墙规则
```

---

## 下一步

篇 13-15 聚焦代码深度，涵盖 Task 执行引擎、Hook 系统与安全审查命令实现。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*