---
title: "CC源码剖析 #07 · MCP 协议：多工具协调"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 8
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、MCP 在架构中的位置

MCP（Model Context Protocol）是 Claude Code 连接外部工具服务的协议，类似于 Language Server Protocol（LSP），但用于 AI 工具调用。

```
Claude Code (Client)
    │
    ├─ MCP 协议（HTTPS/WebSocket/stdio）
    │
    ▼
┌─────────────────────────┐
│  MCP Servers            │
│  • 文件系统服务器        │
│  • Git 服务器           │
│  • 数据库服务器         │
│  • 搜索服务器           │
│  • 自定义服务器         │
└─────────────────────────┘
```

---

## 二、MCP 配置格式

> 文件：`src/services/mcp/types.ts`

### 2.1 配置作用域（ConfigScope）

```typescript
const ConfigScopeSchema = z.enum([
  'local',      // 本地项目 .mcp.json
  'user',       // 用户全局 ~/.claude/mcp.json
  'project',    // 项目配置
  'dynamic',    // 动态配置
  'enterprise', // 企业托管
  'claudeai',   // Claude.ai 内置
  'managed',    // 企业托管
])
```

### 2.2 传输类型（Transport）

```typescript
const TransportSchema = z.enum([
  'stdio',    // 标准输入输出（本地进程）
  'sse',      // Server-Sent Events（HTTPS）
  'sse-ide',  // IDE 专用 SSE
  'http',     // HTTP
  'ws',       // WebSocket
  'sdk',      // SDK 内部传输
])
```

### 2.3 服务器配置类型

**Stdio 配置（本地进程）**：

```typescript
const McpStdioServerConfigSchema = z.object({
  type: z.literal('stdio').optional(),
  command: z.string().min(1),
  args: z.array(z.string()).default([]),
  env: z.record(z.string(), z.string()).optional(),
})
```

**SSE 配置（远程 HTTPS）**：

```typescript
const McpSSEServerConfigSchema = z.object({
  type: z.literal('sse'),
  url: z.string(),
  headers: z.record(z.string(), z.string()).optional(),
  headersHelper: z.string().optional(),
  oauth: McpOAuthConfigSchema.optional(),
})
```

**WebSocket 配置**：

```typescript
const McpWebSocketServerConfigSchema = z.object({
  type: z.literal('ws'),
  url: z.string(),
  headers: z.record(z.string(), z.string()).optional(),
})
```

### 2.4 OAuth 支持

```typescript
const McpOAuthConfigSchema = z.object({
  clientId: z.string().optional(),
  callbackPort: z.number().int().positive().optional(),
  authServerMetadataUrl: z.string().url().optional(),
  xaa: z.boolean().optional(),  // Cross-App Access
})
```

---

## 三、MCP Client 实现

> 文件：`src/services/mcp/client.ts`

### 3.1 客户端架构

```typescript
// 基于 @modelcontextprotocol/sdk
import { Client } from '@modelcontextprotocol/sdk/client/index.js'

// 支持多种传输协议
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { SSEClientTransport } from '@modelcontextprotocol/sdk/client/sse.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'
import { WebSocketTransport } from '../../utils/mcpWebSocketTransport.js'
```

### 3.2 核心接口

```typescript
interface MCPServerConnection {
  name: string
  client: Client
  transport: Transport
  tools: ListToolsResult[]
  resources: ListResourcesResult[]
  prompts: ListPromptsResult[]
  capabilities: ServerCapabilities
}
```

### 3.3 工具调用流程

```
Agent 决定调用 MCP 工具
       │
       ▼
MCPTool.call(args)
       │
       ├─ 定位目标 MCP 服务器
       ├─ 通过 Client.call_tool() 发送请求
       ├─ 处理结果或错误
       └─ 返回 ToolResult
```

### 3.4 OAuth 认证流程

```typescript
// OAuth 401 处理
handleOAuth401Error()

// Token 刷新
checkAndRefreshOAuthTokenIfNeeded()

// 获取 OAuth Token
getClaudeAIOAuthTokens()
```

---

## 四、配置文件加载

> 文件：`src/services/mcp/config.ts`

### 4.1 多层配置合并

```typescript
// 优先级（从高到低）：
// 1. 项目本地 .mcp.json
// 2. 企业托管 managed-mcp.json
// 3. 用户全局 ~/.claude/mcp.json
// 4. Claude.ai 内置配置

async function getMergedMcpConfigs(): Promise<Record<string, ScopedMcpServerConfig>> {
  const [project, enterprise, user, claudeai] = await Promise.all([
    loadProjectMcpConfig(),
    loadEnterpriseMcpConfig(),
    loadUserMcpConfig(),
    loadClaudeAIMcpConfig(),
  ])
  return mergeConfigs(project, enterprise, user, claudeai)
}
```

### 4.2 配置文件写入

```typescript
// 写入时保持权限
async function writeMcpJsonFile(config: McpJsonConfig): Promise<void> {
  // 1. 读取现有权限
  // 2. 写入临时文件
  // 3. fsync 刷新
  // 4. rename 原子替换
}
```

### 4.3 环境变量展开

```typescript
// 支持 ${ENV_VAR} 语法
expandEnvVarsInString("http://${API_HOST}:${API_PORT}")
// → "http://localhost:3000"
```

---

## 五、MCP 工具包装

> 文件：`src/tools/MCPTool/MCPTool.ts`

### 5.1 MCPTool 接口

```typescript
// MCP 工具作为 Tool 实现
const MCPTool: Tool = {
  inputSchema: z.object({
    tool: z.string(),           // MCP 工具名
    arguments: z.record(z.string(), unknown),
    server?: z.string(),        // 可选：指定服务器
  }),

  async call(args, context, canUseTool) {
    // 1. 查找 MCP 服务器
    // 2. 调用工具
    // 3. 处理结果
    // 4. 返回 ToolResult
  }
}
```

### 5.2 资源读取工具

```typescript
// ListMcpResourcesTool
// 列出 MCP 服务器提供的资源

// ReadMcpResourceTool
// 读取特定资源内容
```

---

## 六、连接生命周期

### 6.1 连接管理 Hook

```typescript
// useManageMCPConnections.ts
const useManageMCPConnections = () => {
  // 1. 启动时连接所有配置的 MCP 服务器
  // 2. 监控连接状态
  // 3. 断开时自动重连
  // 4. 支持热重载配置
}
```

### 6.2 心跳与超时

```typescript
// WebSocket 心跳检测
// SSE 重新连接机制
// Stdio 进程监控
```

---

## 七、XAA（Cross-App Access）

### 7.1 概念

XAA 允许多个 MCP 服务器之间共享认证上下文：

```typescript
// XAA 配置
interface McpXaaConfig {
  enabled: boolean
  issuer: string      // IdP 地址
  clientId: string   // OAuth 客户端 ID
}
```

### 7.2 IdP 登录流程

```typescript
// xaaIdpLogin.ts
// 处理 XAA 身份提供商登录
```

---

## 八、工具分类与折叠

> 文件：`src/tools/MCPTool/classifyForCollapse.ts`

### 8.1 显示优化

当 MCP 工具输出过长时，自动折叠显示：

```typescript
// 长时间运行的工具显示进度
// 大输出自动截断并提供展开链接
// 错误信息高亮显示
```

---

## 九、MCP 与 Skills 的关系

### 9.1 MCP Skill Builders

```typescript
// mcpSkillBuilders.ts
// 将 MCP 工具包装为可执行的 Skill

registerMCPSkillBuilders()
// MCP 服务器 → Skill 命令
```

### 9.2 MCP 权限控制

MCP 服务器作为外部服务，需要额外的信任确认：

```typescript
// 首次连接时询问用户
// 服务器声明的能力 vs 实际能力
// 工具调用权限检查
```

---

## 十、官方 MCP 注册表

> 文件：`src/services/mcp/officialRegistry.ts`

### 10.1 预配置服务器

Claude Code 维护一组官方 MCP 服务器供用户一键启用：

```typescript
interface OfficialMcpServer {
  name: string
  description: string
  config: McpServerConfig
  recommendedFor?: string[]
}
```

### 10.2 prefetchOfficialMcpUrls

启动时预取官方服务器 URL 列表，加快配置速度。

---

## 下一步

下一篇：[08 - 消息传递：inbound/outbound 架构](./08-messaging.md)，深入消息传递层、inbound/outbound 架构与消息类型定义。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*