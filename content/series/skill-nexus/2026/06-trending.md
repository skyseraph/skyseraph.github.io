---
title: "SkillNexus #06 · Trending 榜单：你的 Skill 资产地图"
slug: "06-trending"
series: "SkillNexus"
issue: 6
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "用 Trending 榜单管理你的 Skill 资产，找到最有价值的能力"
description: "介绍 SkillNexus 的 Trending 功能：多维度排序、Sparkline 趋势线、信任等级体系，帮你从评测数据中发现明星 Skill、定位短板、驱动进化决策。"
---

> Skills 全生命周期创造平台，让你的 Skill 可生成、可量化、可管理、可成长。

**SkillNexus 系列导航**（共 10 篇）

| #        | 文章                                                  |
| -------- | --------------------------------------------------- |
| 01       | [你的 Skill 目录，正在变成屎山](/series/skill-nexus/2026/01-why-skill-nexus)         |
| 02       | [5 分钟完成第一次 Skill 评测](/series/skill-nexus/2026/02-quickstart)              |
| 03       | [从一行描述到可用 Skill——Studio 的 5 种创作模式](/series/skill-nexus/2026/03-studio)    |
| 04       | [8 维度评测框架：让"感觉还行"变成数据](/series/skill-nexus/2026/04-eval)                  |
| 05       | [进化引擎：让 Skill 自动变好](/series/skill-nexus/2026/05-evo)                      |
| **→ 06** | **Trending 榜单：你的 Skill 资产地图**（本篇）                   |
| 07       | [技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture) |
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)             |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

当你积累了 20 个、50 个 Skill，一个新问题出现了：**哪些 Skill 真的有价值？**

Trending 页面回答这个问题。

***

## 不只是排行榜

表面上，Trending 是一个按评分排名的列表。实质上，它是你的 **Skill 资产地图**。

它从 `eval_history` 表实时聚合，把所有历史评测数据转化成可操作的洞察：

**找出明星 Skill**：总分高、评测次数多的 Skill，是你最可靠的能力资产，**值得优先维护和分享**。

**发现潜力股**：某个 Skill 在某个单维度异常高分（比如 S2 成本意识特别好），**可能有值得迁移到其他 Skill 的设计模式**。

**定位拖后腿的**：低分 Skill **优先送入 Evo 进化**，或者直接淘汰。

**追踪版本演进**：同一个 Skill 的多个版本在榜单上的位置变化，**直观反映进化是否有效**。

***

## 多维度排序

Trending 支持按 9 个维度独立排序：

* **总分**（默认）：综合 8 维度的加权平均
* **G1 Correctness**：正确性最强的 Skill
* **G2 Instruction Following**：指令遵循最好的
* **G3 Safety**：最安全的
* **G4 Completeness**：最完整的
* **G5 Robustness**：最鲁棒的
* **S1 Executability**：指令最清晰的
* **S2 Cost Awareness**：最省 token 的
* **S3 Maintainability**：最易维护的

**按不同维度排序，你会发现不同的"冠军"**——这正是多维度评测的价值所在。

***

## Sparkline：趋势一眼看

每个 Skill 卡片右侧有一条 Sparkline——过去 N 次评测的总分趋势线。

* **持续上升**：进化有效，继续
* **平稳**：稳定，可以考虑更激进的进化策略
* **下降**：需要关注，可能是测试用例变难了，也可能是 Skill 退化了

***

## 信任等级体系

Trending 里每个 Skill 都有信任等级标记：

| 等级      | 含义               |
| ------- | ---------------- |
| T1 AI 生成 | Studio 自动生成，未经验证 |
| T2 质量达标 | 通过格式校验，5D 预评分合格  |
| T3 已评测  | 完成过至少一次 8 维度评测   |
| T4 已批准  | 用户手动审核批准，最高信任    |

这个体系让你在使用 Skill 时有明确的质量预期：**T4 的 Skill 可以放心用于生产，T1 的需要先评测**。

***

## 从榜单到行动

**Trending 不是终点，而是决策入口**：

* 点击任意 Skill → 进入详情，查看完整评测历史
* 低分 Skill → 一键跳转到 Evo，选择进化策略
* 高分 Skill → 一键导出到目标 AI 工具，或分享到 Marketplace

***

## 下一步

了解了核心功能，下一篇我们看技术层面：SkillNexus 的架构是怎么设计的，为什么进化 SDK 可以脱离 Electron 独立运行。

下一篇：[07 · 技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
