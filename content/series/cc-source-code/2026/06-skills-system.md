---
title: "CC源码剖析 #06 · Skills 加载与执行机制"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 7
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Skill 定位：用户自定义 Agent 能力扩展

Skill 是用户通过 Markdown 文件定义的命令，本质是一个**带 frontmatter 的 prompt 模板**。

```
用户执行 /my-skill arg1 arg2
       │
       ▼
Skill 定义文件（Markdown + frontmatter）
       │
       ├─ name: "my-skill"
       ├─ description: "..."
       ├─ arguments: [...]
       ├─ prompt: "模板内容 + {{arg1}} {{arg2}}"
       └─ tools?: [...]  ← 可选：允许使用的工具列表
       │
       ▼
LLM 处理 prompt → 返回结果
```

**Skills 与 Tools 的区别**：

| 特性 | Skill | Tool |
| :--- | :--- | :--- |
| 定义方式 | Markdown 文件 | TypeScript 代码 |
| 编写门槛 | 低（无需编程） | 高（需要编码） |
| 执行方式 | LLM 处理 prompt | 直接执行逻辑 |
| 灵活性 | 受 prompt 限制 | 可实现任意逻辑 |

---

## 二、Skill 文件格式

### 2.1 Frontmatter 结构

```yaml
---
name: "skill-name"           # Skill 标识符
description: "What this skill does and when to use it"
# 触发短语：用户可用这些短语激活 skill
whenToUse: "When the user asks about X or wants to Y"
arguments:                    # 可选：参数定义
  - name: arg1
    description: Description
    required: true
  - name: arg2
    description: Description
    default: "default value"
tools:                        # 可选：允许使用的工具
  - Read
  - Edit
  - Bash
---
```

### 2.2 Prompt 模板

```markdown
---
name: "code-review"
description: "Review code for bugs and style issues"
whenToUse: "User asks for a review or wants to check code quality"
---

# Code Review Skill

Review the following code for:
1. Security vulnerabilities
2. Performance issues
3. Style consistency

Code to review:
{{code}}
```

### 2.3 参数替换

```typescript
// {{arg}} 替换为用户输入的参数值
// {{arg|default}} 提供默认值

substituteArguments(prompt, args)
// "Fix the bug in {{file}}" + { file: "auth.ts" }
// → "Fix the bug in auth.ts"
```

---

## 三、加载体系

> 文件：`src/skills/loadSkillsDir.ts`，约 600 行

### 3.1 四种来源

```typescript
export type LoadedFrom =
  | 'commands_DEPRECATED'  // 旧式命令目录（已废弃）
  | 'skills'               // 用户 skills 目录
  | 'plugin'               // 插件提供的 skills
  | 'managed'              // 企业托管 skills
  | 'bundled'              // 内置 skills
  | 'mcp'                  // MCP 服务器提供的 skills
```

### 3.2 加载路径

```typescript
function getSkillsPath(source: SettingSource | 'plugin', dir: 'skills' | 'commands'): string {
  switch (source) {
    case 'policySettings':  // 企业托管
      return join(getManagedFilePath(), '.claude', dir)
    case 'userSettings':    // 用户全局
      return join(getClaudeConfigHomeDir(), dir)
    case 'projectSettings': // 项目本地
      return `.claude/${dir}`
    case 'plugin':          // 插件
      return 'plugin'
  }
}
```

### 3.3 优先级（生效优先级从高到低）

```
1. Project skills（项目本地 .claude/skills/）
2. User skills（用户全局 ~/.claude/skills/）
3. Managed skills（企业托管）
4. Bundled skills（内置）
5. Plugin skills（插件）
6. MCP skills（MCP 服务器）
```

---

## 四、内置 Skills（Bundled）

> 文件：`src/skills/bundled/index.ts`

### 4.1 内置 Skill 列表

| Skill | 功能 |
| :--- | :--- |
| `/update-config` | 更新配置文件 |
| `/keybindings` | 查看快捷键 |
| `/verify` | 验证代码变更 |
| `/debug` | 调试辅助 |
| `/lorem-ipsum` | 生成占位文本 |
| `/skillify` | 将 prompt 转为 Skill |
| `/remember` | 记忆信息 |
| `/simplify` | 简化文本 |
| `/batch` | 批量操作 |
| `/stuck` | 当卡住时获取建议 |
| `/loop` | 循环执行（AGENT_TRIGGERS） |
| `/claude-api` | Claude API 助手（BUILDING_CLAUDE_APPS） |
| `/claude-in-chrome` | Chrome 中的 Claude |

### 4.2 注册模式

```typescript
export function initBundledSkills(): void {
  registerUpdateConfigSkill()
  registerKeybindingsSkill()
  registerVerifySkill()
  // ...

  if (feature('AGENT_TRIGGERS')) {
    const { registerLoopSkill } = require('./loop.js')
    registerLoopSkill()
  }
}
```

---

## 五、Skill 执行流程

### 5.1 执行链路

```
用户输入 /skill-name arg1 arg2
       │
       ▼
commands.ts → getCommands() → SkillCommand
       │
       ▼
SkillTool.call(args)
       │
       ├─ 解析 frontmatter
       ├─ 参数替换（substituteArguments）
       ├─ 构建完整 prompt
       └─ 发给 LLM 处理
       │
       ▼
LLM 返回结果 → 返回给用户
```

### 5.2 参数解析

```typescript
interface ArgumentDef {
  name: string
  description: string
  required?: boolean
  default?: string
}

// 从 frontmatter 解析参数定义
parseFrontmatter(markdown) → FrontmatterData

// 参数验证与替换
substituteArguments(prompt, userArgs) → string
parseArgumentNames(prompt) → string[]
```

---

## 六、Skill 与 Tools 的交互

### 6.1 工具声明

Skill 的 frontmatter 可以声明允许使用的工具：

```yaml
---
name: "safe-read"
description: "Read file safely"
tools:
  - Read
  - Glob
---
```

### 6.2 权限继承

当 Skill 声明了工具列表时，Agent 只能使用这些工具：

```typescript
// SkillTool 执行时设置工具限制
const allowedTools = skillFrontmatter.tools ?? []
// → Agent 只能使用声明的工具
```

---

## 七、Skill 发现机制

### 7.1 自动发现

```typescript
// 用户输入时，模糊匹配可用 skills
// "run t" → /test, /terminal 等

parseSlashCommandToolsFromFrontmatter(markdown)
// 从 frontmatter 解析可用命令
```

### 7.2 Skill 搜索（实验性）

```typescript
// EXPERIMENTAL_SKILL_SEARCH 启用时
// 支持基于语义的 skill 搜索

clearSkillIndexCache()  // 清除缓存
// 本地向量搜索（基于关键词 TF-IDF）
```

---

## 八、Plugin Skills

### 8.1 插件 Skill 加载

```typescript
// plugins/ 目录下的 skills
getPluginSkills() → Command[]

// 插件 Skill 具有更高优先级
// 可覆盖同名内置 Skill
```

### 8.2 内置插件

```typescript
// plugins/bundled/index.ts
// 内置插件提供的 skills

getBuiltinPluginSkillCommands()
```

---

## 九、Skillify：Prompt 转 Skill

### 9.1 功能

用户可以将自己写的 prompt 保存为 Skill：

```typescript
// 用户输入
/skillify "My custom prompt" "Description of when to use"

// 系统创建 .claude/skills/my-custom-prompt.md
// 内容为用户 prompt
```

### 9.2 注册流程

```typescript
registerSkillifySkill()
// 提供 /skillify 命令
// 引导用户完成 Skill 创建
```

---

## 十、MCP Skills

MCP 服务器也可以提供 Skills：

```typescript
// MCP 服务器的工具包装为 Skill
registerMCPSkillBuilders()

// MCP Skill 具有 MCP 服务器的访问权限
// 可调用 MCP 服务器定义的资源
```

---

## 下一步

下一篇：[07 - MCP 协议：多工具协调](./07-mcp-protocol.md)，深入 `services/mcp/` 模块的 MCP 服务器连接与管理。

---

*Claude Code 源码研究系列 · 2026 · skyseraph*