---
title: "SkillNexus #08 · 现状与路线图：SkillNexus 的下一步"
slug: 08-roadmap
series: "SkillNexus"
issue: 8
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "v0.1.0 核心功能已完整，下一步：Marketplace、团队协作、CLI"
description: "SkillNexus 当前 v0.1.0 内测阶段，653 测试全绿。近期优化评测稳定性和 Studio 体验，中期规划 Skill Marketplace、团队协作和 CI/CD CLI，长期方向是多模态 Skill 和跨模型基准。"
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
| 06       | [Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)         |
| 07       | [技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture) |
| **→ 08** | **现状与路线图：SkillNexus 的下一步**（本篇）                      |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

这是系列的最后一篇，聊聊 SkillNexus 现在在哪里，接下来要去哪里。

***

## 当前状态

**版本**：0.1.0（内测阶段）
**平台**：macOS + Windows
**测试覆盖**：653 个单元测试，37 个测试套件，全绿
**协议**：Apache 2.0

**核心功能已完整**：Home 管理、Studio 生成、TestCase 用例、Eval 评测、Evo 进化、Trending 榜单全部可用。

***

## 近期优先修复

**评测稳定性**：

* 长时间评测任务的进度持久化（中途关闭窗口后可恢复）
* 批量评测的并发控制（避免同时发起过多 AI 请求）
* Judge 超时后的优雅降级

**Studio 体验**：

* 生成历史记录（可以回看之前生成的版本）
* 多轮对话式调整（生成后继续对话微调，而不是重新生成）

**数据管理**：

* 评测历史导出（CSV / JSON）
* Skill 批量操作（批量评测、批量导出）

***

## 中期规划

### Skill Marketplace

目前 Home 页面支持从 GitHub 搜索安装 Skill，但这依赖 GitHub 搜索质量。

计划建立专门的 Skill Marketplace：

* 统一的 Skill 发布标准
* **基于真实评测数据的质量评级**（不是作者自评）
* 按工具、按场景、按维度筛选
* 一键安装到本地

### 团队协作

当前是单机工具。团队场景需要：

* Skill 库共享（局域网 / 私有云同步）
* 评测结果共享（团队成员可以看到彼此的评测历史）
* 进化审批流程（进化版本需要 review 才能合并）

### CI/CD 集成

**进化 SDK 已经与 Electron 解耦**，下一步是提供官方 CLI：

```bash
# 在 CI 中运行评测
skillnexus eval --skill code-review --testcases ./testcases/

# 如果分数下降超过阈值，自动触发进化
skillnexus evo --skill code-review --strategy evidence --threshold 0.8
```

***

## 长期方向

**多模态 Skill**：支持包含图像理解、代码执行、工具调用的复杂 Skill 评测。

**跨模型基准**：同一个 Skill 在不同模型上的表现对比——帮助你选择最适合这个 Skill 的模型。

**Skill 组合优化**：多个 Skill 协同工作时的整体效果评测，而不只是单个 Skill 的孤立评分。

***

## 如何参与

SkillNexus 以 Apache 2.0 开源，欢迎贡献：

**最需要的贡献**：

* 新的进化算法（实现 `BaseEvolutionEngine` 接口即可）
* 新的 Judge 类型（目前支持 LLM / Grep / Command，可以扩展）
* 更多 AI 工具的集成（目前支持 8 种）
* 真实使用场景的测试用例集

**参与方式**：

```bash
git clone https://github.com/skyseraph/SkillNexus.git
cd SkillNexus
npm install && npm run rebuild
npm run dev
```

Issues 和 PR 都欢迎。如果你有想法但不确定是否值得做，先开 Issue 讨论。

***

如果你在用 Claude Code、Cursor 或任何支持 Skill 标准的 AI 工具，欢迎试用 SkillNexus，告诉我你的反馈。

***

下一篇：[09 · 评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
