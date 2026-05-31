---
title: "CC源码剖析 #11 · 插件系统：Plugin 架构与生命周期"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 12
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、插件系统定位

插件系统是 Claude Code 的**扩展生态层**——允许第三方通过 Markdown 文件和配置文件提供 Skills、Hooks、MCP 服务器等能力。

```
用户安装插件
    │
    ▼
┌─────────────────────────────────────┐
│  Plugin Manager                      │
│  ├── loadPluginCommands()           │
│  ├── loadPluginHooks()              │
│  ├── loadPluginMcpServers()         │
│  └── loadPluginAgents()            │
└─────────────────────────────────────┘
    │
    ├─→ Skill Commands（/plugin-name）
    ├─→ Hooks（sessionStart/turnEnd...）
    ├─→ MCP Servers
    └─→ Agent Definitions
```

---

## 二、插件类型

### 2.1 内置插件（Built-in）

> 文件：`src/plugins/builtinPlugins.ts`

```typescript
// 内置插件 vs Skills：
// - Skills: 单个 Markdown 文件
// - 内置插件: 多组件（skills + hooks + MCP servers）

// 插件 ID 格式：{name}@builtin
export function isBuiltinPluginId(pluginId: string): boolean {
  return pluginId.endsWith('@builtin')
}

// 注册内置插件
export function registerBuiltinPlugin(
  definition: BuiltinPluginDefinition,
): void {
  BUILTIN_PLUGINS.set(definition.name, definition)
}
```

### 2.2 市场插件（Marketplace）

```typescript
// 从插件市场安装
// 插件市场：plugins.claude.com

interface MarketplacePlugin {
  id: string           // name@marketplace
  name: string
  version: string
  description: string
  skills: SkillDefinition[]
  hooks: HookDefinition[]
  mcpServers?: McpServerConfig[]
}
```

### 2.3 项目插件

```typescript
// 项目本地的 .claude/plugins/ 目录
// 对项目成员可见
```

---

## 三、插件生命周期

### 3.1 加载流程

```
启动时
  │
  ├─→ initBuiltinPlugins()         // 初始化内置插件
  ├─→ loadAllPluginsCacheOnly()    // 加载已安装插件（缓存）
  ├─→ initializeVersionedPlugins() // 版本管理
  │
  └─→ cleanupOrphanedPluginVersionsInBackground()  // 清理旧版本

运行时
  │
  ├─→ 动态加载新插件
  ├─→ 插件更新检查
  └─→ 插件卸载处理
```

### 3.2 生命周期阶段

| 阶段 | 函数 | 说明 |
| :--- | :--- | :--- |
| Init | `initBuiltinPlugins()` | 注册内置插件 |
| Load | `loadAllPluginsCacheOnly()` | 加载插件列表 |
| Enable | `enablePlugin(id)` | 启用插件 |
| Disable | `disablePlugin(id)` | 禁用插件 |
| Uninstall | `uninstallPlugin(id)` | 卸载插件 |

---

## 四、插件加载器

> 文件：`src/utils/plugins/pluginLoader.ts`

### 4.1 核心接口

```typescript
export interface LoadedPlugin {
  name: string
  manifest: PluginManifest
  path: string
  skills: Command[]
  hooks: HookDefinition[]
  mcpServers?: McpServerConfig[]
  agents?: AgentDefinition[]
}

// 加载插件
loadAllPluginsCacheOnly(): Promise<LoadedPlugin[]>
```

### 4.2 插件清单格式

```yaml
# plugin.json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My Claude Code plugin",
  "skills": ["skills/*.md"],
  "hooks": ["hooks/*.ts"],
  "mcpServers": ["mcp.json"],
  "agents": ["agents/*.md"]
}
```

### 4.3 插件隔离

```typescript
// 插件代码在独立作用域执行
// 防止插件之间的命名冲突

// 插件只能访问显式导出的内容
```

---

## 五、插件目录结构

> 文件：`src/utils/plugins/pluginDirectories.ts`

### 5.1 目录布局

```typescript
// 插件安装目录
const PLUGIN_DIRS = {
  user: '~/.claude/plugins/',        // 用户插件
  project: '.claude/plugins/',        // 项目插件
  managed: '{managedPath}/plugins/',  // 企业托管
  bundled: '{installPath}/bundled/'    // 内置插件
}
```

### 5.2 插件目录

```
~/.claude/plugins/
└── {plugin-name}/
    ├── plugin.json      # 清单文件
    ├── skills/         # Skill 文件
    ├── hooks/          # Hook 脚本
    ├── mcp/            # MCP 配置
    └── resources/       # 资源文件
```

---

## 六、插件命令加载

> 文件：`src/utils/plugins/loadPluginCommands.ts`

### 6.1 加载流程

```typescript
export async function getPluginCommands(): Promise<Command[]> {
  const plugins = await loadAllPluginsCacheOnly()
  return plugins.flatMap(p => p.skills)
}

// Skill 文件格式与标准 Skills 相同
// 通过 frontmatter 定义参数和行为
```

### 6.2 依赖解析

> 文件：`src/utils/plugins/dependencyResolver.ts`

```typescript
// 插件可能依赖其他插件
// 依赖解析确保加载顺序正确

interface PluginDependency {
  name: string
  version: string  // 支持 semver 范围
}

resolveDependencies(plugins: LoadedPlugin[]): LoadedPlugin[]
```

---

## 七、插件 Hooks

> 文件：`src/utils/plugins/loadPluginHooks.ts`

### 7.1 Hook 类型

```typescript
type HookType =
  | 'sessionStart'      // 会话开始
  | 'sessionEnd'        // 会话结束
  | 'turnEnd'          // 回合结束
  | 'preToolCall'      // 工具调用前
  | 'postToolCall'      // 工具调用后
  | 'preAgentCall'     // Agent 调用前
  | 'postAgentCall'     // Agent 调用后
```

### 7.2 Hook 接口

```typescript
interface HookDefinition {
  type: HookType
  name: string
  handler: (context: HookContext) => Promise<void | HookResult>
}

interface HookContext {
  sessionId: string
  messages: Message[]
  tools: Tool[]
  // ...
}
```

---

## 八、插件 MCP 服务器

> 文件：`src/utils/plugins/mcpPluginIntegration.ts`

### 8.1 MCP 配置

```typescript
// 插件可以提供 MCP 服务器配置
// 加载后自动连接

interface PluginMcpConfig {
  servers: McpServerConfig[]
}
```

### 8.2 集成流程

```typescript
// 1. 解析插件的 mcp.json
// 2. 验证 MCP 配置
// 3. 连接到 MCP 服务器
// 4. 注册 MCP 工具
```

---

## 九、插件版本管理

> 文件：`src/utils/plugins/pluginVersioning.ts`

### 9.1 版本检查

```typescript
// 支持 semver 语义化版本
// 自动更新检查

interface PluginVersion {
  major: number
  minor: number
  patch: number
  prerelease?: string
}

// 版本兼容性检查
isCompatible(current: Version, required: Version): boolean
```

### 9.2 自动更新

> 文件：`src/utils/plugins/pluginAutoupdate.ts`

```typescript
// 检查插件更新
// 自动下载新版本
// 回滚机制
```

---

## 十、插件安全

### 10.1 插件隔离

```typescript
// 插件代码在受限环境运行
// 不能直接访问系统资源

// 文件访问：只允许插件目录内
// 网络访问：只允许配置的端点
// 敏感API：需要明确授权
```

### 10.2 权限检查

> 文件：`src/utils/plugins/pluginPolicy.ts`

```typescript
// 企业可以配置插件策略
// 允许/禁止特定插件

interface PluginPolicy {
  allowedPlugins: string[]
  blockedPlugins: string[]
  requireApproval: string[]
}
```

### 10.3 恶意插件检测

```typescript
// 静态分析插件代码
// 检测可疑模式
// 隔离执行
```

---

## 下一步

下一篇：[12 - 跨进程通信：RemoteBridge 与远程模式](https://skyseraph.github.io/series/cc-source-code/2026/12-remote-bridge)，深入远程桥接、SSH 会话与跨进程通信机制。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*