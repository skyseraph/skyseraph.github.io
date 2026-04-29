---
title: "SkillNexus #01 · 你的 Skill 目录，正在变成屎山"
slug: 01-why-skill-nexus
series: "SkillNexus"
issue: 1
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "Skill 缺少量化和进化基础设施，SkillNexus 填补这个空白"
description: "AI Skill 解决了能力载体问题，但写完不知好坏、进化靠猜、模型换代失效。SkillNexus 用数据驱动闭环让 Skill 可生成、可量化、可进化。"
---

> Skills 全生命周期创造平台，让你的 Skill 可生成、可量化、可管理、可成长。

**SkillNexus 系列导航**（共 10 篇）

| #        | 文章                                                  |
| -------- | --------------------------------------------------- |
| **→ 01** | **你的 Skill 目录，正在变成屎山**（本篇）                          |
| 02       | [5 分钟完成第一次 Skill 评测](/series/skill-nexus/2026/02-quickstart)              |
| 03       | [从一行描述到可用 Skill——Studio 的 5 种创作模式](/series/skill-nexus/2026/03-studio)    |
| 04       | [8 维度评测框架：让"感觉还行"变成数据](/series/skill-nexus/2026/04-eval)                  |
| 05       | [进化引擎：让 Skill 自动变好](/series/skill-nexus/2026/05-evo)                      |
| 06       | [Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)         |
| 07       | [技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture) |
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)             |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

打开 `~/.claude/skills/`，你能说清楚里面哪个 Skill 还在用、哪个已经失效、哪个其实跟另一个功能重叠吗？

大多数人不能。

这不是管理能力的问题，是 **Skill 开发本身缺少基础设施**：

* **写完不知道好不好**——靠主观感受，没有量化数据
* **进化靠猜**——改了一版，感觉"差不多"，但不知道哪个维度变好了、哪个退步了
* **模型换代后失效**——Claude 升级，原来调好的 Skill 悄悄变差，你甚至不知道
* **多人重复造轮子**——团队里三个人各自维护功能几乎相同的 code-review Skill，谁也不知道哪个最好
* **没有淘汰机制**——旧 Skill 堆在那里，越来越多，越来越乱

Skill 解决了"能力的载体"问题——模块化、可分发、跨工具。但它没有解决：**如何知道这个 Skill 好不好？怎么让它持续变好？**

***

## SkillNexus 要做的事

一句话：**让 AI Skill 可生成、可量化、可进化的全生命周期平台。**

核心是一个数据驱动的闭环：

```
Studio（生成）
    → TestCase（用例）→ Eval（评测）
    → Evo（进化）
    → Trending（榜单）
```

每一步都不是孤立功能，而是数据流转的节点：

**生成有依据**——Studio 内置 AI 辅助生成，同时提供 5 维实时质量预评分，写出来就知道大概在什么水平。

**评测有标准**——8 个维度量化 Skill 在真实任务上的表现：正确性、指令遵循、安全性、完整性、鲁棒性，以及 Skill 自身的可执行性、成本意识、可维护性。每次评测都留下历史记录。

**进化有数据**——Evo 消费评测历史，自动诊断哪个维度最弱、哪些样本最差，用 4 种算法（EvoSkill / CoEvoSkill / SkillX / SkillClaw）生成改进版本，并**对比新旧版本的分数变化，防止回归**。

**排名有依据**——Trending 从所有评测历史中聚合排行，哪个 Skill 真正在用、真正好用，数据说话。

***

## 为什么是桌面应用？

**你的 Skill 文件和 API Key 都是本地资产，不应该经过任何第三方服务器。**

* Skill 文件存在 `~/.claude/skills/`，与 Claude Code 直接共享，**零迁移成本**
* API Key 只在主进程内存中存在，渲染进程拿不到
* 评测任务（Shell 命令执行）需要访问本地环境
* 支持本地 Ollama，**完全离线可用**

***

## 下一步

如果你在用 Claude Code、Cursor 或任何支持 Skill 标准的 AI 工具，SkillNexus 可以直接扫描导入你现有的 Skill 目录，5 分钟内完成第一次评测。

下一篇我们讲具体怎么上手：[02 · 5 分钟完成第一次 Skill 评测](/series/skill-nexus/2026/02-quickstart)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
