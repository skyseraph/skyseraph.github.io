---
title: "CC源码剖析 #02 · 入口点解析：从 CLI 到 REPL"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 3
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、整体启动流程

Claude Code 的启动链路非常清晰：

```
main.tsx（入口）
  ├── Commander.js CLI 解析
  ├── 并行预加载（MDM配置/Keychain/API预连接/GrowthBook）
  ├── Ink React 渲染
  │     ├── commands.ts 注册 Slash Commands
  │     ├── tools.ts 注册 Tool
  │     ├── QueryEngine 初始化
  │     └── REPL.tsx 主交互界面
```

---

## 二、`main.tsx` — 入口编排

> 文件：`src/main.tsx`，约 4,000 行

### 2.1 启动顺序

**第一步：模块加载前的副作用（必须先执行）**

```typescript
// 这些副作用必须在所有 import 之前执行
profileCheckpoint('main_tsx_entry');
startMdmRawRead();       // 并行读取 MDM 配置（macOS 企业配置）
startKeychainPrefetch(); // 并行读取 Keychain（OAuth + API Key）
```

这三个调用 firing 了三个独立子进程并行获取配置数据，为后续初始化节省 ~65ms。

**第二步：Commander.js CLI 解析**

```typescript
program
  .name('claude')
  .description('Cloudshell enhanced with AI')
  .option('--model <model>', 'Specify model')
  .option('--no-input', 'Non-interactive mode')
  // ... 80+ 选项
  .parse(args);
```

CLI 解析后，通过 `program.opts()` 提取所有配置，准备初始化 AppState。

**第三步：并行预加载（Prefetch）**

```typescript
// 这些异步操作在 REPL 渲染前并行启动，不阻塞首屏
fetchBootstrapData();           // 获取启动引导数据
prefetchPassesEligibility();    // 用户推荐资格检查
prefetchOfficialMcpUrls();      // 官方 MCP 服务器 URL 预取
prefetchFastModeStatus();       // 快速模式状态
prefetchAwsCredentialsIfSafe(); // AWS 凭证
prefetchGcpCredentialsIfSafe(); // GCP 凭证
initializeGrowthBook();         // Feature Flag 服务
refreshPolicyLimits();          // 策略限制
loadRemoteManagedSettings();    // 企业托管设置
```

每个 prefetch 都是独立网络请求，共用 `Promise.all` 并行发出。

### 2.2 GrowthBook 初始化

```typescript
import { initializeGrowthBook } from './services/analytics/growthbook.js';

// GrowthBook 是功能开关系统，决定哪些实验特性对当前用户开放
initializeGrowthBook().then(() => {
  // 特性开关就绪后，注册条件命令
  registerConditionalCommands();
});
```

### 2.3 权限模式解析

CLI 解析后从多个来源确定权限模式：

```typescript
const permissionMode = initialPermissionModeFromCLI()  // CLI 参数
  ?? (await checkAutoModeEnabledStateIfCached())       // 缓存的自动模式
  ?? getDefaultPermissionMode();                       // 默认值

const allowedTools = parseToolListFromCLI();            // --allowed-tools
const removedTools = removeDangerousPermissions(       // 过滤危险权限
  allowedTools,
  permissionMode
);
```

---

## 三、Feature Flag 编译时裁剪

> 本节使用 `bun:bundle` 的 `feature()` 函数，在编译时消除未激活代码

### 3.1 条件导入模式

```typescript
import { feature } from 'bun:bundle';

const proactive = feature('PROACTIVE') || feature('KAIROS')
  ? require('./commands/proactive.js').default
  : null;

const voiceCommand = feature('VOICE_MODE')
  ? require('./commands/voice/index.js').default
  : null;
```

如果 `VOICE_MODE` 未激活，`./commands/voice/` 整个目录的代码不会打包进最终二进制。

### 3.2 主要 Feature Flags

| Flag | 控制模块 |
| :--- | :--- |
| `PROACTIVE` / `KAIROS` | 主动建议 Agent |
| `BRIDGE_MODE` | VSCode/JetBrains 桥接 |
| `DAEMON` | 后台驻守模式 |
| `VOICE_MODE` | 语音输入 |
| `COORDINATOR_MODE` | 多 Agent 编排 |
| `WORKFLOW_SCRIPTS` | 工作流脚本 |
| `AGENT_TRIGGERS` | 定时任务触发 |
| `UDS_INBOX` | 进程间消息队列 |
| `FORK_SUBAGENT` | Sub-agent 派生 |
| `BUDDY` | 对话伙伴模式 |
| `ULTRAPLAN` | 增强规划模式 |
| `TORCH` | 批量操作模式 |

### 3.3 命令注册条件过滤

```typescript
const COMMANDS = memoize((): Command[] => [
  addDir, advisor, agents, branch,
  // ... 基础命令
  ...(webCmd ? [webCmd] : []),           // CCR_REMOTE_SETUP
  ...(forkCmd ? [forkCmd] : []),         // FORK_SUBAGENT
  ...(buddy ? [buddy] : []),             // BUDDY
  ...(process.env.USER_TYPE === 'ant'
    ? INTERNAL_ONLY_COMMANDS              // 内部命令
    : []),
]);
```

---

## 四、`commands.ts` — 命令注册中心

> 文件：`src/commands.ts`，约 25,000 行，~100 个命令

### 4.1 命令类型

```typescript
interface Command {
  type: 'prompt' | 'builtin' | 'alias';
  name: string;
  aliases?: string[];
  description: string;
  contentLength?: number;
  progressMessage?: string;
  source?: 'builtin' | 'plugin' | 'skill';
  // prompt 类型命令有生成器函数
  getPromptForCommand?: (args: string[], context: Context) => Promise<string>;
}
```

两种核心类型：
- **`prompt` 类型**：由 LLM 处理，通过 `getPromptForCommand` 生成 prompt
- **`builtin` 类型**：直接执行原生逻辑（如 `/clear`, `/help`）

### 4.2 命令注册流程

```typescript
// 命令以逗号分隔列表静态导入（~80 个文件）
import commit from './commands/commit.js';
import diff from './commands/diff/index.ts';
import doctor from './commands/doctor/index.ts';
// ...

// 所有命令汇聚到 COMMANDS 数组
const COMMANDS = memoize((): Command[] => [
  addDir, advisor, agents, branch, btw, chrome, clear, color,
  compact, config, copy, desktop, context, // ...
]);

// 别名映射
export const builtInCommandNames = memoize(
  (): Set<string> => new Set(
    COMMANDS().flatMap(_ => [_.name, ...(_.aliases ?? [])])
  )
);
```

### 4.3 Skills 命令加载

```typescript
async function getSkills(cwd: string): Promise<{
  skillDirCommands: Command[];   // 用户自定义 skills 目录
  pluginSkills: Command[];       // 插件提供的 skills
  bundledSkills: Command[];      // 内置 skills（Markdown/Explain/Review）
  builtinPluginSkills: Command[]; // 内置插件命令
}> {
  const [skillDirCommands, pluginSkills] = await Promise.all([
    getSkillDirCommands(cwd),
    getPluginSkills(),
  ]);
  const bundledSkills = getBundledSkills();
  const builtinPluginSkills = getBuiltinPluginSkillCommands();
  return { skillDirCommands, pluginSkills, bundledSkills, builtinPluginSkills };
}
```

所有命令在 REPL 渲染前汇聚完毕。

### 4.4 核心内置命令 TOP 10

| 命令 | 文件 | 功能 |
| :--- | :--- | :--- |
| `/commit` | `commands/commit.ts` | Git 提交（含自动 staging） |
| `/review` | `commands/review.ts` | PR/code review |
| `/ask` | `commands/ask.ts` | 回答代码问题 |
| `/diff` | `commands/diff/index.ts` | 查看变更 |
| `/test` | `commands/test.ts` | 生成/运行测试 |
| `/explain` | `bundled/index.ts` | 解释代码（内置 skill） |
| `/search` | `commands/search.ts` | 代码库搜索 |
| `/debug` | `commands/debug.ts` | 调试辅助 |
| `/refactor` | `commands/refactor.ts` | 重构建议 |
| `/session` | `commands/session/index.ts` | 会话管理 |

---

## 五、`replLauncher.tsx` — REPL 启动器

> 文件：`src/replLauncher.tsx`，约 50 行

```typescript
export async function launchRepl(
  root: Root,
  appProps: AppWrapperProps,
  replProps: REPLProps,
  renderAndRun: (root: Root, element: React.ReactNode) => Promise<void>
): Promise<void> {
  const { App } = await import('./components/App.js');
  const { REPL } = await import('./screens/REPL.js');
  await renderAndRun(root, <App {...appProps}><REPL {...replProps} /></App>);
}
```

启动器做两件事：
1. 动态导入 `App` 和 `REPL` 组件（懒加载）
2. 调用 `renderAndRun` 执行 Ink 渲染

---

## 六、`screens/REPL.tsx` — 主交互界面

> 文件：`src/screens/REPL.tsx`，约 5,000 行，React 组件

### 6.1 核心状态

```typescript
// REPL 是状态最重的组件，持有大量状态
interface REPLState {
  messages: Message[];          // 对话消息历史
  toolUses: ToolUse[];          // 工具调用记录
  agents: Agent[];              // 子 Agent
  tasks: Task[];                // 后台任务
  queuedCommands: QueuedCommand[]; // 队列中的命令
  // ... 100+ 状态字段
}
```

### 6.2 核心 Hooks 使用

```typescript
const messages = useLogMessages();           // 消息订阅
const tools = useMergedTools();             // 工具组合
const commands = useMergedCommands();        // 命令组合
const mcpClients = useMergedClients();      // MCP 客户端
const appState = useAppState();             // 全局状态
const replBridge = useReplBridge();         // IDE 桥接
const remoteSession = useRemoteSession();   // 远程会话
```

### 6.3 渲染树

```
<App>
  <KeybindingSetup>
    <GlobalKeybindingHandlers>
      <CommandKeybindingHandlers>
        <REPL>
          <Messages>          {/* 对话消息列表 */}
          <TaskListV2>        {/* 后台任务 */}
          <PromptInput>       {/* 用户输入框 */}
            <PromptInputQueuedCommands /> {/* 队列命令 */}
          </PromptInput>
          <CostThresholdDialog />  {/* 费用上限对话框 */}
          <IdleReturnDialog />    {/* 空闲返回对话框 */}
          <PermissionRequest />    {/* 权限请求 */}
          <WorkerPendingPermission /> {/* Agent 权限等待 */}
        </REPL>
      </CommandKeybindingHandlers>
    </GlobalKeybindingHandlers>
  </KeybindingSetup>
</App>
```

### 6.4 主要功能分区

| 区域 | 组件 | 职责 |
| :--- | :--- | :--- |
| 消息区 | `Messages.tsx` | 历史消息、工具输出、Agent 输出 |
| 输入区 | `PromptInput/` | 用户命令输入、Tab 补全、Anarchy 模式前缀 |
| 任务栏 | `TaskListV2.tsx` | 后台任务状态、子 Agent 管理 |
| 权限区 | `PermissionRequest.tsx` | 工具权限确认、Auto Mode 权限流 |
| 对话框 | `CostThresholdDialog.tsx` | 费用超限警告 |
| 快捷键 | `KeybindingSetup` | 全局键盘处理 |

---

## 七、启动参数与环境变量

### 7.1 核心 CLI 参数

| 参数 | 说明 |
| :--- | :--- |
| `--model <model>` | 指定模型 |
| `--no-input` | 非交互模式 |
| `--output-format <json\|stream-json>` | 输出格式 |
| `--resume <sessionId>` | 恢复会话 |
| `--print` | 仅打印 response |
| `--add-dir <path>` | 添加附加代码目录 |
| `--AllowedTools <tool1,tool2>` | 限制可用工具 |
| `--permission-mode <auto|ask|reject>` | 权限模式 |
| `--dangerously-permit-aws` | 允许 AWS 操作 |

### 7.2 环境变量映射

```typescript
// main.tsx 中将 CLI 参数转换为环境变量供子模块使用
// CLAUDE_CODE_MODEL → model
// CLAUDE_CODE_PERMISSION_MODE → permissionMode
// CLAUDE_CODE_OUTPUT_FORMAT → outputFormat
```

---

## 八、启动时序图（简化）

```
main.tsx
  │
  ├─ profileCheckpoint('main_tsx_entry')
  ├─ startMdmRawRead()          [并行子进程]
  ├─ startKeychainPrefetch()    [并行子进程]
  │
  ├─ program.parse(args)        [Commander.js]
  │
  ├─ loadGlobalConfig()         [配置文件]
  ├─ validateApiKey()           [API Key 检查]
  │
  ├─ initializeGrowthBook()    [Feature Flags]
  ├─ refreshPolicyLimits()      [策略限制]
  │
  ├─ getTools()                 [工具注册]
  ├─ getCommands()              [命令注册]
  ├─ getSkills(cwd)             [Skill 加载]
  │
  ├─ createRoot(renderOptions)  [Ink 根]
  │
  ├─ fetchBootstrapData()       [预加载]
  ├─ prefetchPassesEligibility()
  ├─ prefetchOfficialMcpUrls()
  └─ launchRepl(root, appProps, replProps)
        │
        ├─ import('./components/App.js')
        ├─ import('./screens/REPL.js')
        │
        └─ renderAndRun(root, <App><REPL>...</REPL></App>)
              │
              └─ REPL.tsx 渲染 → 等待用户输入
```

---

## 下一步

下一篇：[03 - Bridge 模块：主进程与渲染进程的通信机制](./03-bridge-arch.md)，深入 IDE 扩展与 CLI 之间的双向通信层。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*