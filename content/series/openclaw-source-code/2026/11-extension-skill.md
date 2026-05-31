---
title: "OpenClaw源码剖析 #11 · Extension 开发：Skill 篇"
date: 2026-05-01T08:00:00+08:00
series: "OpenClaw源码剖析"
issue: 12
categories: ["专栏"]
tags: ["OpenClaw", "Agent", "架构", "开源"]
toc: true
draft: false
---

## 一、Skill 扩展定位

Skill 扩展是 OpenClaw 的**技能模块**——通过描述匹配触发，为 Agent 提供专用工具和知识。

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Core                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Agent RT    │  │  Skills     │  │   Memory     │      │
│  └──────────────┘  └──────┬───────┘  └──────────────┘      │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Skill System                          │    │
│  │  SKILL.md · scripts/ · references/               │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、模块结构

| 文件/目录 | 职责 |
|:---|:---|
| `src/agents/skills/types.ts` | Skill 类型定义 |
| `src/agents/skills/workspace.ts` | Skill 加载、过滤、Prompt 构建 |
| `src/agents/skills/frontmatter.ts` | Frontmatter 解析 |
| `src/agents/skills/local-loader.ts` | 文件系统加载 |
| `src/agents/skills/plugin-skills.ts` | 插件内嵌 Skill 加载 |
| `skills/` | 内置 Skill 目录 |
| `extensions/*/skills/` | 插件内嵌 Skill |

---

## 三、两种 Skill 类型

### 3.1 独立 Skill

存储在 `skills/` 目录：

```
~/.openclaw/skills/
workspaceDir/skills/
C:\dev\claude\openclaw\skills/
```

通过 `loadWorkspaceSkillEntries()` 扫描发现（查找包含 `SKILL.md` 的目录）。

### 3.2 插件内嵌 Skill

存储在 `extensions/*/skills/`：

```
extensions/skill-workshop/skills/
extensions/acpx/skills/
```

在 `openclaw.plugin.json` 中声明：

```json
{
  "id": "skill-workshop",
  "skills": ["./skills"],
  "configSchema": { "type": "object" }
}
```

通过 `resolvePluginSkillDirs()` 加载。

---

## 四、SKILL.md 格式

### 4.1 必需 Frontmatter

```yaml
---
name: skill-name                    # 唯一标识符（小写、连字符）
description: |                      # 触发条件 + 功能描述
  When to use this skill and what it does.
  Include specific contexts where it should trigger.
---
```

### 4.2 metadata.openclaw（可选）

```yaml
metadata:
  openclaw:
    emoji: "☔"                      # emoji 标识
    always: true                    # 始终加载到上下文
    primaryEnv: "WEATHER_API_KEY"   # 主要环境变量
    requires:                       # 依赖检查
      bins: ["curl", "jq"]          # 必需二进制文件
      anyBins: ["curl", "wget"]     # 至少有一个存在
      env: ["API_KEY"]              # 必需环境变量
      config: ["~/.config/app"]     # 必需配置文件
    install:                        # 安装说明
      - id: brew
        kind: brew
        formula: curl
        bins: ["curl"]
        label: "Install curl (brew)"
```

### 4.3 Body（正文）

Skill 触发后才加载，应简洁（<500 行）：

```markdown
## 技能名称

### 使用方法
1. 第一步
2. 第二步

### 示例
...
```

---

## 五、SkillEntry 类型

> 文件：`src/agents/skills/types.ts`

```typescript
export type OpenClawSkillMetadata = {
  always?: boolean;
  skillKey?: string;
  primaryEnv?: string;
  emoji?: string;
  homepage?: string;
  os?: string[];
  requires?: {
    bins?: string[];
    anyBins?: string[];
    env?: string[];
    config?: string[];
  };
  install?: SkillInstallSpec[];
};

export type SkillEntry = {
  skill: Skill;
  frontmatter: ParsedSkillFrontmatter;
  metadata?: OpenClawSkillMetadata;
  invocation?: SkillInvocationPolicy;
};
```

---

## 六、触发机制

### 6.1 描述匹配触发

Skill 通过 `description` 在模型 Prompt 中触发：

```
<available_skills>
<name>weather</name>
<description>Get current weather, rain, temperature...</description>
<location>...</location>
</available_skills>
```

模型根据描述决定何时读取 Skill。

### 6.2 触发策略

```yaml
user-invocable: false        # 用户是否可通过 /skill-name 调用
disable-model-invocation: false  # 模型是否可自动触发
```

### 6.3 命令调度

用户输入 `/skill-name` 时，通过 `resolveSkillCommandInvocation()` 解析。

---

## 七、开发步骤

### 7.1 初始化 Skill

```bash
python scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

示例：

```bash
python scripts/init_skill.py my-skill --path skills/public --resources scripts,references
```

### 7.2 编辑 SKILL.md

1. 填写 `name` 和 `description`（最重要）
2. 编写 body 指令

### 7.3 添加资源（可选）

```
skill-name/
├── SKILL.md
├── scripts/           # 可执行代码
├── references/        # 按需加载的文档
└── assets/           # 输出文件（模板、图片）
```

### 7.4 验证和打包

```bash
python scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

生成 `.skill` 文件（zip 格式）。

---

## 八、完整示例

### 8.1 weather Skill

> `skills/weather/SKILL.md`

```yaml
---
name: weather
description: "Get current weather, rain, temperature, and forecasts for locations or travel planning."
metadata:
  openclaw:
    emoji: "☔"
    requires: { bins: ["curl"] }
    install:
      - id: brew
        kind: brew
        formula: curl
        bins: ["curl"]
---

## Weather Skill

Use `wttr.in` to get weather information.

### Usage
```
curl wttr.in/{location}
```

### Examples
- `curl wttr.in/Tokyo` - Tokyo weather
- `curl wttr.in/NewYork` - New York weather
```

### 8.2 插件内嵌 Skill 示例

> `extensions/acpx/skills/acp-router/SKILL.md`

```yaml
---
name: acp-router
description: "Route ACP messages and manage acp-* commands. Use when user mentions acp-router, acp-* commands, or needs to manage ACP routing."
metadata:
  openclaw:
    emoji: "🔀"
    always: false
---
```

---

## 九、Plugin 声明

### 9.1 openclaw.plugin.json

```json
{
  "id": "my-plugin",
  "activation": { "onStartup": true },
  "skills": ["./skills"],
  "configSchema": { "type": "object" }
}
```

### 9.2 多 Skill 目录

```json
{
  "skills": ["./skills", "./custom-skills"]
}
```

---

## 十、Skill 提示构建

> `src/agents/skills/workspace.ts`

```typescript
export function buildWorkspaceSkillsPrompt(params: {
  skills: SkillEntry[];
  // ...
}): string {
  // 生成 <available_skills> 块
  // 每个 Skill 输出 name、description、location
}
```

---

## 十一、设计权衡

### 11.1 描述驱动触发

Skill 使用自然语言描述而非命令关键字，模型可以理解何时需要使用技能。

### 11.2 按需加载

Skill body 只在触发后加载，保持核心 Prompt 简洁。

### 11.3 渐进式披露

```
1. Metadata（name + description）— 始终在上下文
2. SKILL.md body — 触发后加载
3. Bundled resources — 按需执行
```

---

## 十二、Skill 创建工具

### 12.1 init_skill.py

初始化新 Skill 目录结构：

```bash
python scripts/init_skill.py <name> --path <path> [--resources]
```

### 12.2 package_skill.py

打包 Skill 为 `.skill` 文件：

```bash
python scripts/package_skill.py <skill-folder> [output]
```

---

## 下一步

篇目 11 完成，继续：

| # | 文章 | 说明 |
|:---|:---|:---|
| 12 | [测试策略：单元/集成/E2E](./12-testing-strategy.md) | Vitest + E2E |
| 13 | [配置系统：Schema 与验证](./13-config-system.md) | 配置管理 |
| 14 | [安全机制：Auth 与权限](./14-security-auth.md) | 认证授权 |
| 15 | [部署与运维：Docker 与容器化](./15-deployment-docker.md) | 生产部署 |

---

*OpenClaw 源码剖析系列 · 2026 · skyseraph*