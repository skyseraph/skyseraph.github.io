---
title: "SkillNexus #05 · 进化引擎：让 Skill 自动变好"
slug: 05-evo
series: "SkillNexus"
date: 2026-05-01
issue: 5
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "基于评测数据自动诊断弱点，6 种算法生成改进版本"
description: "SkillNexus Evo 模块提供交互式三范式（Evidence / Strategy / Capability）和自动化 SDK 六算法（SkVM / EvoSkill / CoEvoSkill / SkillX / SkillClaw / SkillMOO），支持 Plugin 热加载自定义进化策略。"
---

> Skills 全生命周期创造平台，让你的 Skill 可生成、可量化、可管理、可成长。

**SkillNexus 系列导航**（共 10 篇）

| #        | 文章                                                  |
| -------- | --------------------------------------------------- |
| 01       | [你的 Skill 目录，正在变成屎山](/series/skill-nexus/2026/01-why-skill-nexus)         |
| 02       | [5 分钟完成第一次 Skill 评测](/series/skill-nexus/2026/02-quickstart)              |
| 03       | [从一行描述到可用 Skill——Studio 的 5 种创作模式](/series/skill-nexus/2026/03-studio)    |
| 04       | [8 维度评测框架：让"感觉还行"变成数据](/series/skill-nexus/2026/04-eval)                  |
| **→ 05** | **进化引擎：让 Skill 自动变好**（本篇）                           |
| 06       | [Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)         |
| 07       | [技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture) |
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)             |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

评测出了分，然后呢？

大多数工具到这里就停了——给你一张报告，剩下的靠你自己。

SkillNexus 的 Evo 模块做的是下一步：**基于评测数据，自动诊断弱点，生成改进版本。**

***

## 两类进化路径

Evo 的进化策略分两类：**交互式**（你参与，实时可见）和**自动化**（后台批量，无需干预）。

***

## 交互式进化：Studio 三范式

在 Studio 里，你可以选择三种进化范式，流式生成，实时看到 Skill 内容如何变化。

### Evidence（证据驱动）

**核心思路**：外科手术式修复。

把评测低分的用例作为"证据"输入，AI 精准定位问题所在，只修改有问题的部分，不动其他内容。

适合场景：你知道 Skill 在某类输入上表现差，想针对性修复，不想大改。

### Strategy（策略矩阵）

**核心思路**：目标导向优化。

你指定优化目标，比如"提升 G1 正确性和 S2 成本意识"，AI 给出针对性的改进方案，并解释每处修改的理由。

适合场景：你有明确的优化方向，想让 AI 系统性地改，而不是随机调整。

### Capability（能力感知）

**核心思路**：降低执行门槛。

分析 Skill 对 AI 执行能力的要求，识别哪些指令对模型来说太模糊或太复杂，重写成更容易被执行的形式。

适合场景：Skill 在强模型上表现好，但换到弱模型或本地模型就变差。

***

## 自动化 SDK 引擎：6 种算法

如果你想批量优化、无人值守运行，SDK 引擎是更好的选择。

### SkVM：证据驱动外科手术

取最近评测历史中最弱的 2 个维度，找出对应的失败样本作为"证据"，针对性修复，不动其他内容。同时**追溯 4 代祖先版本，防止在同一问题上来回振荡**。

逻辑：**有证据的改动比随机调整更可靠，改得少比改得多更安全。**

### EvoSkill：最差样本驱动

找出评分最低的测试用例，针对这些"最差情况"改进 Skill，多轮迭代直到收敛。

逻辑：**一个 Skill 的下限决定它的可靠性。** 持续提升最差情况，整体质量自然上升。

### CoEvoSkill：生成器 - 验证器循环

两个 AI 角色相互博弈：

* **生成器**：提出 Skill 改进方案
* **验证器**：对改进方案进行对抗性测试，找漏洞

循环迭代，直到验证器找不到明显问题。

逻辑：**单一 AI 的盲点可以被另一个 AI 发现。对抗性验证比自我评估更可靠。**

### SkillX：成功模式提取

从历史高分用例中归纳规律——什么样的输入结构、什么样的任务类型，这个 Skill 表现最好？把这些规律编码进 Skill 正文。

逻辑：**与其修复失败，不如放大成功。**

### SkillClaw：集体失败分析

跨多个会话、多个用例，聚类失败模式——找出结构性缺陷，而不是个案问题。

逻辑：**单次失败可能是偶然，多次失败的共同模式才是真正的问题所在。**

### SkillMOO：多目标 Pareto 优化

在多个相互冲突的目标之间找最优解集。比如"提升 G1 正确性"和"降低 S2 token 消耗"往往是矛盾的——更详细的输出通常更正确，但也更贵。

SkillMOO 不给你一个"最优解"，而是给你一组 **Pareto 前沿**：在不牺牲其他目标的前提下，每个目标能达到的最好结果。你根据实际需求选择。

***

## 进化历史树

每次进化都会记录：

* 进化前后的 Skill 内容（Diff 视图）
* 使用的进化策略
* 进化前后的评分变化
* 进化时间和使用的模型

这形成一棵**进化历史树**——你可以看到 Skill 是怎么一步步变好的，也可以随时回滚到任意历史版本。

***

## Plugin 系统：自定义进化算法

如果内置的 6 种算法不够用，你可以开发自己的进化算法：

```javascript
// {userData}/plugins/my-evo.js
module.exports = class MyEvoEngine extends BaseEvolutionEngine {
  async evolve(skill, evalResults) {
    // 你的进化逻辑
  }
}
```

放入 `{userData}/plugins/` 目录，**无需修改源码，无需重新构建，热加载即可使用**。

***

**进化引擎与 Electron 完全解耦**，可以在 CLI、CI/CD 管道中独立运行——架构细节见 [07 · 技术架构](/series/skill-nexus/2026/07-architecture)。

***

## 下一步

Skill 进化了，怎么知道哪些 Skill 是你资产库里的"明星"？

下一篇：[06 · Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
