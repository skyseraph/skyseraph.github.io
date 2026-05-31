---
title: "CC源码剖析 #09 · 权限系统：PermissionCallbacks 与安全边界"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 10
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、权限系统定位

权限系统是 Claude Code 的安全保障层——决定 Agent 在执行敏感操作前是否需要用户确认。

```
Tool.call()
    │
    ├─→ canUseTool(toolName, input) ─→ Permission 检查
    │                                    │
    │                                    ├─ alwaysAllow → 直接执行
    │                                    ├─ alwaysDeny → 拒绝
    │                                    ├─ auto 模式 → 检查历史决策
    │                                    └─ ask 模式 → 弹出确认对话框
    │
    └─→ 执行 Tool Logic
```

---

## 二、权限模式

> 文件：`src/types/permissions.ts`

### 2.1 模式类型

```typescript
type PermissionMode =
  | 'default'      // 使用用户配置的默认模式
  | 'auto'         // 自动批准已知安全操作
  | 'ask'           // 每次都询问用户
  | 'reject'        // 拒绝所有危险操作
  | 'bypass'        // 绕过（需要特殊标志）
```

### 2.2 CLI 参数

```bash
claude --permission-mode=auto    # 自动模式
claude --permission-mode=ask     # 每次询问
claude --AllowedTools=Read,Bash  # 白名单工具
```

### 2.3 权限模式来源

```typescript
// 优先级（从高到低）：
// 1. CLI 参数 --permission-mode
// 2. 会话缓存的 auto 模式状态
// 3. 全局配置默认值

initialPermissionModeFromCLI()
  ?? checkAutoModeEnabledStateIfCached()
  ?? getDefaultPermissionMode()
```

---

## 三、权限规则（Permission Rules）

### 3.1 规则类型

```typescript
interface ToolPermissionRulesBySource {
  [source: string]: {
    tool: string
    allow?: boolean
    deny?: boolean
  }
}

// 规则来源：
// - alwaysAllowRules: 始终允许
// - alwaysDenyRules: 始终拒绝
// - alwaysAskRules: 始终询问
```

### 3.2 规则示例

```yaml
# 用户配置 (.claude/permissions.yml)
always_allow:
  - tool: "Read"
    paths: ["src/**"]

always_deny:
  - tool: "Bash"
    commands: ["rm -rf /"]

always_ask:
  - tool: "Bash"
    commands: ["rm *"]
```

### 3.3 规则匹配

```typescript
// 规则匹配逻辑
getPermissionDecision(
  toolName: string,
  input: object,
  context: ToolPermissionContext
): 'allow' | 'deny' | 'ask'

// 匹配顺序：
// 1. alwaysDenyRules → deny
// 2. alwaysAllowRules → allow
// 3. alwaysAskRules → ask
// 4. 权限模式决定
```

---

## 四、canUseTool 检查

### 4.1 接口签名

```typescript
type CanUseToolFn = (
  toolName: string,
  input: object,
  context: ToolPermissionContext,
) => Promise<PermissionResult>
```

### 4.2 检查流程

```typescript
async function canUseTool(
  toolName: string,
  input: object,
  context: ToolPermissionContext,
): Promise<PermissionResult> {
  // 1. 检查 bypass 模式
  if (context.mode === 'bypass') {
    return { granted: true }
  }

  // 2. 检查 alwaysAllow
  if (matchesAlwaysAllow(toolName, input, context)) {
    return { granted: true }
  }

  // 3. 检查 alwaysDeny
  if (matchesAlwaysDeny(toolName, input, context)) {
    return { granted: false, reason: 'blocked' }
  }

  // 4. 检查权限模式
  if (context.mode === 'auto') {
    // 查历史决策
    return checkAutoHistory(toolName, input)
  }

  if (context.mode === 'ask') {
    // 弹出 UI 对话框
    return showPermissionDialog(toolName, input)
  }

  return { granted: false, reason: 'default_deny' }
}
```

---

## 五、自动模式（Auto Mode）

### 5.1 历史决策

Auto 模式维护一个本地决策缓存：

```typescript
interface ToolDecision {
  source: string        // 决策来源
  decision: 'accept' | 'reject'
  timestamp: number
}

toolDecisions: Map<string, ToolDecision>

// 缓存 key：toolName + 输入摘要
// 避免重复询问相同操作
```

### 5.2 遗忘机制

```typescript
// 拒绝次数过多时降级为 ask
// 避免"一直拒绝最终用户厌烦"

localDenialTracking: DenialTrackingState
// 跟踪拒绝次数，超阈值触发提示
```

### 5.3 决策续用

```typescript
// 用户同意后，自动模式记住决策
grantPermission(toolName, input): void

// 拒绝后，下次需要重新询问
denyPermission(toolName, input): void
```

---

## 六、权限对话框

### 6.1 PermissionRequest 组件

> 文件：`src/components/permissions/PermissionRequest.tsx`

```typescript
// UI 显示：
// ┌────────────────────────────────────────┐
// │ ⚠️ 权限请求                              │
// │                                        │
// │ Bash 工具请求执行：                      │
// │ $ rm -rf node_modules/                  │
// │                                        │
// │ [允许一次] [始终允许] [拒绝] [取消]      │
// └────────────────────────────────────────┘
```

### 6.2 权限提示信息

```typescript
// 不同工具有不同的风险级别提示
const PERMISSION_WARNING: Record<ToolName, string> = {
  Bash: "此命令将执行 shell 操作",
  FileWrite: "此操作将创建或覆盖文件",
  Network: "此操作将发送网络请求",
}
```

### 6.3 权限结果处理

```typescript
type PermissionResult =
  | { granted: true }
  | { granted: false; reason: 'denied' | 'blocked' | 'cancelled' }
  | { granted: false; reason: 'auto_deny' }
```

---

## 七、危险命令检测

> 文件：`src/tools/BashTool/bashPermissions.ts`

### 7.1 破坏性命令警告

```typescript
// 检测危险命令模式
const DANGEROUS_PATTERNS = [
  /^rm\s+-rf\s+/,           // rm -rf
  /^dd\s+/,                 // dd 磁盘操作
  /^mkfs/,                  // 格式化
  /^shutdown/,             // 关机
  /^reboot/,                // 重启
]

// 当检测到危险命令时：
// - 在 auto 模式下直接拒绝
// - 在 ask 模式下高亮警告
```

### 7.2 路径验证

```typescript
// 只读模式下验证路径
validateReadOnlyPath(input: BashInput): boolean

// 检测是否访问了不允许的目录
const FORBIDDEN_PATHS = [
  '/etc/passwd',
  '/etc/shadow',
  'C:\\Windows\\System32',
]
```

### 7.3 Git 安全

```typescript
// Git 操作安全检查
const GIT_SAFE_PATTERNS = [
  'status',
  'log',
  'diff --staged',
  'add',
  'commit',
  'push',  // 有风险，需要确认
]

const GIT_DANGEROUS_PATTERNS = [
  'push --force',
  'push -f',
  'rebase -i',
]
```

---

## 八、权限上下文传递

### 8.1 ToolPermissionContext

```typescript
type ToolPermissionContext = DeepImmutable<{
  mode: PermissionMode
  additionalWorkingDirectories: Map<string, AdditionalWorkingDirectory>
  alwaysAllowRules: ToolPermissionRulesBySource
  alwaysDenyRules: ToolPermissionRulesBySource
  alwaysAskRules: ToolPermissionRulesBySource
  isBypassPermissionsModeAvailable: boolean
  isAutoModeAvailable?: boolean
  strippedDangerousRules?: ToolPermissionRulesBySource
  shouldAvoidPermissionPrompts?: boolean  // 背景 Agent
  awaitAutomatedChecksBeforeDialog?: boolean
  prePlanMode?: PermissionMode
}>
```

### 8.2 上下文注入

```typescript
// ToolUseContext.toolPermissionContext
const context: ToolUseContext = {
  // ...
  options: {
    // ...
  },
  // ...
}
```

---

## 九、ExitPlanMode 权限请求

> 文件：`src/components/permissions/ExitPlanModePermissionRequest/ExitPlanModePermissionRequest.tsx`

### 9.1 Plan Mode 退出时的权限检查

当用户从 Plan Mode 退出执行时，需要重新检查所有修改的文件：

```typescript
// 收集 plan mode 期间修改的所有文件
const modifiedFiles = collectModifiedFiles(planModeState)

// 构建权限更新请求
const permissionUpdates = buildPermissionUpdates(
  modifiedFiles,
  context
)

// 应用权限更新
applyPermissionUpdates(permissionUpdates)
```

### 9.2 增量权限

```typescript
// 只请求实际修改部分的权限
// 不需要用户重新确认所有操作
```

---

## 十、安全边界总结

```
┌─────────────────────────────────────────────────────────────┐
│                     安全边界                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 始终允许规则（用户配置）                          │
│  Layer 2: 始终拒绝规则（用户配置 + 内置危险模式）             │
│  Layer 3: Auto 模式历史决策                                 │
│  Layer 4: 实时权限对话框                                    │
│  Layer 5: 破坏性操作额外警告                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 下一步

下一篇：[10 - 状态管理：memdir 与会话持久化](./10-memdir-state.md)，深入 `memdir/` 模块的内存目录、会话状态持久化机制。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*