---
title: "OpenClaw源码剖析 #12 · 测试策略：单元/集成/E2E"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 13
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、测试系统定位

OpenClaw 采用 **Vitest** 作为主要测试框架，配合 Playwright 进行浏览器测试，构建了多层次的测试体系。

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Infrastructure                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Vitest    │  │  Playwright  │  │    V8        │      │
│  │  单元/集成    │  │   浏览器测试  │  │   覆盖率     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、测试框架

| 工具 | 版本 | 用途 |
|:---|:---|:---|
| `vitest` | ^4.1.5 | 单元/集成测试框架 |
| `@vitest/coverage-v8` | ^4.1.5 | V8 引擎代码覆盖率 |
| `@vitest/browser-playwright` | - | 浏览器 E2E 测试 |
| `jsdom` | ^29.1.0 | DOM 模拟 |
| `playwright` | - | 浏览器自动化 |

---

## 三、目录结构

```
C:\dev\claude\openclaw\
├── test/
│   ├── vitest/                    # Vitest 配置文件（70+）
│   │   ├── vitest.config.ts       # 根配置
│   │   ├── vitest.unit.config.ts  # 单元测试
│   │   ├── vitest.unit-fast.config.ts  # 快速单元
│   │   ├── vitest.e2e.config.ts   # E2E 测试
│   │   ├── vitest.gateway.config.ts
│   │   ├── vitest.channels.config.ts
│   │   └── vitest.contracts-*.config.ts  # 契约测试
│   │
│   ├── helpers/                   # 测试工具
│   │   ├── openclaw-test-instance.ts  # Gateway 实例启动器
│   │   ├── gateway-e2e-harness.ts     # E2E 测试 harness
│   │   └── ...
│   │
│   ├── mocks/                     # Mock 定义
│   ├── fixtures/                  # 测试夹具
│   ├── setup.ts                   # 全局 Setup
│   ├── setup.shared.ts            # 共享 Setup
│   └── setup-openclaw-runtime.ts  # 运行时环境
│
├── src/
│   └── **/*.test.ts               # 单元测试分散在 src/
│
└── ui/
    └── src/**/*.test.ts           # UI 组件测试（~100 文件）
```

---

## 四、配置文件

### 4.1 根配置

> `test/vitest/vitest.config.ts`

定义 54+ 项目配置，包括 unit、e2e、channels、contracts 等。

### 4.2 共享配置

> `test/vitest/vitest.shared.config.ts`

```typescript
export const sharedConfig = defineConfig({
  test: {
    timeout: 120000,           // 测试超时 120s
    hookTimeout: 180000,      // Hook 超时 180s（Windows）
    coverage: {
      provider: "v8",
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 55,
        statements: 70,
      },
    },
  },
});
```

### 4.3 单元测试配置

> `test/vitest/vitest.unit.config.ts`

```typescript
export function createUnitVitestConfigWithOptions(env, options) {
  return defineConfig({
    test: {
      name: "unit",
      isolate: true,  // 隔离运行
      include: [...unitTestIncludePatterns],
      exclude: [
        ...exclude,
        "**/*.e2e.test.ts",
        "**/*.live.test.ts",
        "**/*.node.test.ts",
      ],
      setupFiles: [
        "test/setup.ts",
        "test/setup-openclaw-runtime.ts",
      ],
    },
  });
}
```

### 4.4 快速单元配置

> `test/vitest/vitest.unit-fast.config.ts`

```typescript
return defineConfig({
  test: {
    name: "unit-fast",
    isolate: false,     // 不隔离，提升速度
    runner: undefined,  // 使用默认 runner
    setupFiles: [],     // 无 Setup 文件
    include: unitFastTestFiles,
  },
});
```

### 4.5 E2E 测试配置

> `test/vitest/vitest.e2e.config.ts`

```typescript
export default defineConfig({
  test: {
    maxWorkers: e2eWorkers,  // CI: 2, 本地: 1
    include: [
      "test/**/*.e2e.test.ts",
      "src/**/*.e2e.test.ts",
      "src/gateway/gateway.test.ts",
    ],
    exclude: ["**/*.live.test.ts"],
  },
});
```

---

## 五、测试文件命名

| 后缀 | 说明 | 示例 |
|:---|:---|:---|
| `*.test.ts` | 标准单元测试 | `agents.test.ts` |
| `*.node.test.ts` | Node.js 环境测试 | `file-system.node.test.ts` |
| `*.browser.test.ts` | 浏览器环境测试 | `component.browser.test.ts` |
| `*.live.test.ts` | 需要外部服务的测试 | `api.live.test.ts` |
| `*.e2e.test.ts` | 端到端测试 | `chat.e2e.test.ts` |

---

## 六、测试工具

### 6.1 OpenClaw Test Instance

> `test/helpers/openclaw-test-instance.ts`

```typescript
export type OpenClawTestInstance = {
  name: string;
  port: number;
  url: string;
  hookToken: string;
  gatewayToken: string;
  homeDir: string;
  stateDir: string;
  state: OpenClawTestState;
  stdout: string[];
  stderr: string[];
  child?: ChildProcessWithoutNullStreams;
  env: NodeJS.ProcessEnv;
  entrypoint: () => Promise<string[]>;
  cli: (args: string[], options?) => Promise<CommandResult>;
  startGateway: () => Promise<void>;
  stopGateway: () => Promise<void>;
  cleanup: () => Promise<void>;
};
```

### 6.2 Gateway E2E Harness

> `test/helpers/gateway-e2e-harness.ts`

```typescript
// 启动 Gateway 实例
spawnGatewayInstance(name: string): Promise<OpenClawTestInstance>

// 停止实例
stopGatewayInstance(inst: OpenClawTestInstance): Promise<void>

// 连接 Node 客户端
connectNode(inst, label: string): Promise<void>

// 等待节点状态
waitForNodeStatus(inst, nodeId: string): Promise<void>

// 等待聊天完成事件
waitForChatFinalEvent(params: {...}): Promise<void>
```

### 6.3 Shared Setup

> `test/setup.shared.ts`

```typescript
import { installSharedTestSetup } from "./setup.shared.js";

installSharedTestSetup();
// - 模拟 OAuth 和 clipboard 模块
// - 设置 VITEST=true
// - 设置 OPENCLAW_TEST_TRUST_BUNDLED_PLUGINS_DIR=1
// - 增加 MaxListeners 到 256
```

---

## 七、测试脚本

### 7.1 package.json 脚本

```json
{
  "test": "node scripts/test-projects.mjs",
  "test:unit": "pnpm test:unit:fast && node scripts/run-vitest.mjs run --config test/vitest/vitest.unit.config.ts",
  "test:unit:fast": "node scripts/run-vitest.mjs run --config test/vitest/vitest.unit-fast.config.ts",
  "test:e2e": "node scripts/run-vitest.mjs run --config test/vitest/vitest.e2e.config.ts",
  "test:fast": "node scripts/run-vitest.mjs run --config test/vitest/vitest.unit.config.ts",
  "test:changed": "node scripts/test-projects.mjs --changed origin/main",
  "test:channels": "node scripts/run-vitest.mjs run --config test/vitest/vitest.channels.config.ts",
  "test:contracts": "pnpm test:contracts:channels && pnpm test:contracts:plugins",
  "test:contracts:channels": "node scripts/test-projects.mjs --maxWorkers=1 test/vitest/vitest.contracts-channel-*.config.ts",
  "test:contracts:plugins": "node scripts/run-vitest.mjs run --config test/vitest/vitest.contracts-plugin.config.ts",
  "test:coverage": "node scripts/run-vitest.mjs run --config test/vitest/vitest.unit.config.ts --coverage",
  "test:watch": "node scripts/test-projects.mjs --watch",
  "test:all": "pnpm lint && pnpm build && pnpm test && pnpm test:e2e && pnpm test:live && pnpm test:docker:all"
}
```

### 7.2 测试运行器

```bash
# 单配置运行
node scripts/run-vitest.mjs run --config test/vitest/vitest.unit.config.ts

# 多项目运行（分片）
node scripts/test-projects.mjs

# 指定分片
node scripts/test-projects.mjs --changed origin/main

# 最大并发
OPENCLAW_VITEST_MAX_WORKERS=8 node scripts/test-projects.mjs

# 串行运行
OPENCLAW_TEST_PROJECTS_SERIAL=1 OPENCLAW_VITEST_MAX_WORKERS=1 node scripts/test-projects.mjs
```

---

## 八、覆盖率阈值

```typescript
coverage: {
  provider: "v8",
  thresholds: {
    lines: 70,       // 70%
    functions: 70,   // 70%
    branches: 55,    // 55%
    statements: 70,  // 70%
  },
}
```

---

## 九、CI/CD 测试运行

### 9.1 GitHub Actions 工作流

> `.github/workflows/ci.yml`

| Job | 说明 |
|:---|:---|
| `checks-node-core-test` | 主测试运行器（动态矩阵） |
| `checks-fast` | 快速检查（bundled plugin、channels、contracts） |
| `checks-node-core-nondist` | 非分布式测试 |
| `checks-node-core-dist` | 需要构建产物的分布式测试 |

### 9.2 CI 环境变量

```bash
OPENCLAW_VITEST_MAX_WORKERS=8       # 最大 workers
OPENCLAW_TEST_WORKERS               # 替代 workers 数量
OPENCLAW_VITEST_INCLUDE_FILE        # 覆盖测试文件模式
OPENCLAW_E2E_WORKERS                # E2E workers 数量
OPENCLAW_E2E_VERBOSE                # E2E 详细输出
```

### 9.3 测试分片

> `scripts/lib/ci-node-test-plan.mjs`

基于运行时和配置创建测试分片，每个分片有加权运行时用于负载均衡。

---

## 十、UI 测试

> `ui/vitest.config.ts`

支持 3 种环境：

```typescript
projects: [
  defineProject({
    name: "unit",
    include: ["src/**/*.test.ts"],
    environment: "jsdom",
  }),
  defineProject({
    name: "unit-node",
    include: ["src/**/*.node.test.ts"],
    environment: "jsdom",
  }),
  defineProject({
    name: "browser",
    include: ["src/**/*.browser.test.ts"],
    browser: {
      provider: playwright(),
      instances: [{ browser: "chromium" }],
    },
  }),
]
```

---

## 下一步

篇目 12 完成，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 13 | [配置系统：Schema 与验证](./13-config-system.md) | 配置管理 |
| 14 | [安全机制：Auth 与权限](./14-security-auth.md) | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*