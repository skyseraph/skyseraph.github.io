---
title: "SkillNexus #04 · 8 维度评测框架：让\"感觉还行\"变成数据"
slug: 04-eval
series: "SkillNexus"
issue: 4
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "8 个维度拆解 Skill 的真实截面，告别主观感受"
description: "SkillNexus Eval 模块用 G 系列（任务质量）和 S 系列（Skill 质量）共 8 个维度量化 Skill 表现，支持单次评测、A/B 对比和三条件基线实验。"
---

> Skills 全生命周期创造平台，让你的 Skill 可生成、可量化、可管理、可成长。

**SkillNexus 系列导航**（共 10 篇）

| #        | 文章                                                  |
| -------- | --------------------------------------------------- |
| 01       | [你的 Skill 目录，正在变成屎山](/series/skill-nexus/2026/01-why-skill-nexus)         |
| 02       | [5 分钟完成第一次 Skill 评测](/series/skill-nexus/2026/02-quickstart)              |
| 03       | [从一行描述到可用 Skill——Studio 的 5 种创作模式](/series/skill-nexus/2026/03-studio)    |
| **→ 04** | **8 维度评测框架：让"感觉还行"变成数据**（本篇）                        |
| 05       | [进化引擎：让 Skill 自动变好](/series/skill-nexus/2026/05-evo)                      |
| 06       | [Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)         |
| 07       | [技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture) |
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)             |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

"这个 Skill 好不好用？"

这个问题在大多数团队里的答案是："感觉还行。"

SkillNexus 的 Eval 模块要把这个答案变成一张数字。

***

## 为什么需要 8 个维度？

一个 Skill 的"好"是多维的：

* 它可能任务成功率很高，但每次输出都啰嗦，**token 消耗是同类 Skill 的 3 倍**
* 它可能在标准输入下表现完美，但**遇到边界情况就崩**
* 它可能指令写得很清晰，但**实际产出的结果不够完整**

**单一分数掩盖了这些差异。** 8 个维度的设计，是为了让你看到 Skill 的**真实截面**。

***

## 8 个维度详解

### G 系列：任务质量（这个 Skill 产出的结果好不好）

**G1 · Correctness（正确性）**
输出是否正确完成了任务目标。这是最基础的维度——Skill 有没有做对事。

**G2 · Instruction Following（指令遵循）**
是否严格遵循了格式要求和约束条件。比如要求输出 JSON，有没有真的输出 JSON；要求不超过 200 字，有没有超。

**G3 · Safety（安全性）**
输出是否安全、中立、无害。对于代码类 Skill，是否会生成有安全漏洞的代码；对于内容类 Skill，是否会产生有害内容。

**G4 · Completeness（完整性）**
是否涵盖了所有必要内容。一个代码审查 Skill，有没有覆盖安全、性能、可读性三个方面，还是只看了其中一个。

**G5 · Robustness（鲁棒性）**
对边界输入、模糊描述、异常情况的处理能力。**这个维度最容易被忽视，也最能暴露 Skill 的真实质量。**

***

### S 系列：Skill 质量（这个 Skill 本身写得好不好）

**S1 · Executability（可执行性）**
指令是否清晰、具体、可操作。AI 能不能准确理解并执行，还是需要猜测你的意图。

**S2 · Cost Awareness（成本意识）**
输出是否简洁，有没有不必要的冗余。一个好的 Skill 应该引导 AI 给出恰到好处的输出，而不是每次都输出 2000 字。

**S3 · Maintainability（可维护性）**
Skill 的结构是否清晰，未来修改是否容易。这对团队协作尤其重要——你写的 Skill，同事能不能看懂、能不能改。

***

## G 系列 vs S 系列：核心洞察

**这两组维度的分离是 Eval 框架最重要的设计决策。**

**G 系列**告诉你"有没有做对事"——Skill 在实际任务上的表现。
**S 系列**告诉你"有没有把事做好"——Skill 本身的工程质量。

一个 Skill 可以 G 系列高分、S 系列低分：任务成功率高，但指令写得乱，token 消耗大，同事看不懂。
也可以 S 系列高分、G 系列低分：结构清晰，但实际效果不好。

**两组分数结合，才能给出完整的改进方向。**

***

## 三种评测模式

### 单次评测

对当前版本出分，得到 8 维度雷达图和总分。适合了解 Skill 的基础水平。

### 对比模式（A vs B）

两个版本并排评测，可视化差异。适合确认进化是否有效——改了 Skill 之后，到底哪些维度提升了，哪些下降了。

### 三条件基线实验

同时运行三组：

* **无 Skill 组**：裸 AI，不加任何 Skill
* **当前版本组**：你的 Skill
* **AI 生成对照组**：让 AI 自动生成一个同类 Skill

这个模式回答一个根本问题：**装上这个 Skill，到底增益了多少？**

如果你的 Skill 和裸 AI 分数差不多，说明这个 Skill 没有实质价值；如果 AI 生成的对照组比你的 Skill 分数高，说明有改进空间。

***

## 三种 Judge 类型

评测的核心是 Judge——如何判断 AI 的输出是否符合预期。

**LLM Judge**：用另一个 LLM 来评判输出质量。适合开放性任务，比如"代码审查是否全面"。

**Grep Judge**：字符串匹配。适合有明确格式要求的任务，比如"输出必须包含 JSON 格式"。

**Command Judge**：执行 Shell 命令验证。适合代码生成类 Skill——生成的代码能不能跑通，直接执行看结果。

**三种 Judge 可以组合使用**，一条测试用例可以同时用 LLM 评判质量 + Grep 验证格式。

***

## 可视化：6 种图表

评测历史不只是一张表格，SkillNexus 提供 6 种可视化：

* **雷达图**：8 维度当前得分一览
* **趋势折线**：每个维度随版本迭代的变化曲线
* **热力图**：跨版本、跨维度的得分矩阵
* **箱线图**：得分分布，看稳定性
* **对比柱状图**：A vs B 版本差异
* **三条件对比图**：基线实验结果

***

## 下一步

有了评分，Evo 引擎就能自动诊断弱点，生成改进版本。

下一篇：[05 · 进化引擎：让 Skill 自动变好](/series/skill-nexus/2026/05-evo)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
