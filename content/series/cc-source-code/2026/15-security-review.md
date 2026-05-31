---
title: "CC源码剖析 #15 · 安全审查：Security Review 命令实现"
date: 2026-05-01T08:00:00+08:00
series: "CC源码剖析"
issue: 16
categories: ["专栏"]
tags: ["Claude Code", "架构", "开源"]
toc: true
draft: false
---

> 基于 2026-03-31 公开的源码快照，~512,000 行代码

---

## 一、Security Review 命令定位

`/security-review` 是 Claude Code 内置的**安全审查命令**，通过解析 git diff 分析 PR 中的代码变更，识别高置信度的安全漏洞。

```
用户执行 /security-review
    │
    ▼
┌────────────────────────────────────────┐
│  Security Review Command               │
│  1. 获取 git diff                      │
│  2. 获取修改文件列表                   │
│  3. 构建安全审查 prompt               │
└────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────┐
│  Agent 处理                            │
│  分析 diff → 识别漏洞 → 输出报告      │
└────────────────────────────────────────┘
    │
    ▼
结构化安全报告（Markdown 格式）
```

---

## 二、命令实现

> 文件：`src/commands/security-review.ts`

### 2.1 命令定义

```typescript
// 允许的工具（白名单）
allowed-tools: Bash(git diff:*), Bash(git status:*),
               Bash(git log:*), Bash(git show:*),
               Bash(git remote show:*), Read, Glob, Grep, LS, Task

// 描述
description: Complete a security review of the pending changes
             on the current branch
```

### 2.2 工具白名单策略

```typescript
// 限制只能使用：
// 1. Git 读取命令（diff, status, log, show, remote show）
// 2. 文件读取（Read, Glob, Grep, LS）
// 3. Task（用于并行分析）

// 禁止：
// - Bash（其他命令）
// - FileWrite / FileEdit
// - Network tools
```

---

## 三、安全审查 Prompt

> 文件：`src/commands/security-review.ts:6-179`

### 3.1 核心 Objective

```
Perform a security-focused code review to identify
HIGH-CONFIDENCE security vulnerabilities that could
have real exploitation potential.
```

**关键约束**：
- 只报告置信度 >80% 的漏洞
- 排除理论性问题
- 聚焦高影响漏洞

### 3.2 排除类别（False Positive 过滤）

```typescript
// 自动排除以下类型：
HARD EXCLUSIONS:
1. DOS / 资源耗尽
2. 磁盘上的 secrets（其他工具处理）
3. 速率限制问题
4. 内存/CPU 耗尽
5. 非安全关键字段的输入验证
6. GitHub Action workflow 漏洞（除非明确可触发）
7. 内存安全语言中的内存安全问题（Rust 等）
8. 测试文件中的问题
9. 日志伪造
10. SSRF（仅控制 path 时）
11. AI prompt 注入
12. Regex injection/DOS
13. 文档文件中的问题
14. 缺少审计日志
```

### 3.3 优先规则

```typescript
PRECEDENTS:
1. 明文日志记录高价值 secrets → HIGH
2. UUIDs → 不可猜测，无需验证（安全）
3. 环境变量和 CLI flags → 信任（安全）
4. React/Angular XSS → 除非使用 dangerouslySetInnerHTML（安全）
5. 客户端 JS 缺少权限检查 → 不算漏洞（安全）
6. Notebook 漏洞 → 需要明确攻击路径（安全）
```

---

## 四、安全审查类别

### 4.1 输入验证漏洞

| 类型 | 检查内容 |
| :--- | :--- |
| SQL Injection | 未清理的用户输入进入 SQL 查询 |
| Command Injection | system calls / subprocesses 中的命令注入 |
| XXE Injection | XML 解析中的外部实体 |
| Template Injection | 模板引擎中的模板注入 |
| NoSQL Injection | 数据库查询中的 NoSQL 注入 |
| Path Traversal | 文件操作中的路径遍历 |

### 4.2 认证与授权

| 类型 | 检查内容 |
| :--- | :--- |
| Auth Bypass | 认证绕过逻辑 |
| Privilege Escalation | 权限提升路径 |
| Session Management | 会话管理缺陷 |
| JWT Vulnerabilities | JWT token 漏洞 |
| Authorization Bypass | 授权逻辑绕过 |

### 4.3 加密与密钥管理

| 类型 | 检查内容 |
| :--- | :--- |
| Hardcoded Secrets | 硬编码的 API keys / passwords / tokens |
| Weak Crypto | 弱加密算法实现 |
| Key Storage | 不当的密钥存储 |
| Randomness Issues | 加密随机性问题 |
| Cert Validation Bypass | 证书验证绕过 |

### 4.4 注入与代码执行

| 类型 | 检查内容 |
| :--- | :--- |
| RCE via Deserialization | 反序列化导致的 RCE |
| Pickle Injection | Python pickle 注入 |
| YAML Deserialization | YAML 反序列化漏洞 |
| Eval Injection | 动态代码执行中的 eval 注入 |
| XSS | Web 应用中的 XSS（reflected/stored/DOM） |

### 4.5 数据泄露

| 类型 | 检查内容 |
| :--- | :--- |
| Sensitive Logging | 敏感数据日志记录 |
| PII Violations | PII 处理违规 |
| API Leakage | API 端点数据泄露 |
| Debug Exposure | 调试信息暴露 |

---

## 五、分析方法论

### 5.1 三阶段分析

```typescript
// Phase 1: 仓库上下文研究
// - 识别现有安全框架和库
// - 查找established secure coding patterns
// - 理解项目的安全模型

// Phase 2: 对比分析
// - 比较新代码与现有安全模式
// - 识别偏离安全实践的地方
// - 标记引入新攻击面的代码

// Phase 3: 漏洞评估
// - 检查每个修改文件的安全影响
// - 追踪数据流从用户输入到敏感操作
// - 识别注入点和unsafe反序列化
```

---

## 六、输出格式

### 6.1 要求的 Markdown 格式

```markdown
# Vuln 1: XSS: `foo.py:42`

* Severity: High
* Description: ...
* Exploit Scenario: ...
* Recommendation: ...
```

### 6.2 严重级别定义

| 级别 | 定义 |
| :--- | :--- |
| **HIGH** | 直接可利用的漏洞，导致 RCE、数据泄露或认证绕过 |
| **MEDIUM** | 需要特定条件但影响显著 |
| **LOW** | 纵深防御问题或低影响漏洞 |

### 6.3 置信度评分

| 分数 | 定义 |
| :--- | :--- |
| 0.9-1.0 | 确定的利用路径，已测试 |
| 0.8-0.9 | 清晰的漏洞模式，已知利用方法 |
| 0.7-0.8 | 可疑模式，需要特定条件利用 |
| <0.7 | 不报告（太理论化） |

---

## 七、执行流程

```
/security-review
  │
  ├─→ 获取 git status
  ├─→ 获取 git diff --name-only origin/HEAD...
  ├─→ 获取 git log origin/HEAD...
  ├─→ 获取 git diff origin/HEAD...
  │
  ├─→ 构建 prompt（diff + 指令）
  │
  └─→ Agent 分析 → Markdown 报告
```

---

## 八、与 /review 的区别

| 特性 | `/security-review` | `/review` |
| :--- | :--- | :--- |
| 焦点 | 安全漏洞 | 通用代码质量 |
| 输入 | git diff | PR 或代码变更 |
| 工具限制 | 严格（只读 git + 文件） | 宽松（所有工具） |
| 排除规则 | 详细 False Positive 过滤 | 较少 |
| 输出 | 结构化漏洞报告 | 通用 review 意见 |

---

## 九、其他内置 Review 命令

| 命令 | 功能 |
| :--- | :--- |
| `/review` | 通用代码 review |
| `/security-review` | 专注安全漏洞 |
| `/ultrareview` | 深度 review（多轮） |

---

*Claude Code 源码研究系列 · 2026 · skyseraph*