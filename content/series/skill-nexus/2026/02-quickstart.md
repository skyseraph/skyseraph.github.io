---
title: "SkillNexus #02 · 5 分钟完成第一次 Skill 评测——SkillNexus 上手指南"
slug: 02-quickstart
series: "SkillNexus"
issue: 2
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "从零开始，5 分钟跑通首次 8 维度 Skill 评测"
description: "纯操作指南：安装 SkillNexus、配置 LLM Provider、导入 Skill、创建测试用例、运行评测，5 步看到 8 维度评分雷达图。"
---

> Skills 全生命周期创造平台，让你的 Skill 可生成、可量化、可管理、可成长。

**SkillNexus 系列导航**（共 10 篇）

| #        | 文章                                                  |
| -------- | --------------------------------------------------- |
| 01       | [你的 Skill 目录，正在变成屎山](/series/skill-nexus/2026/01-why-skill-nexus)         |
| **→ 02** | **5 分钟完成第一次 Skill 评测**（本篇）                          |
| 03       | [从一行描述到可用 Skill——Studio 的 5 种创作模式](/series/skill-nexus/2026/03-studio)    |
| 04       | [8 维度评测框架：让"感觉还行"变成数据](/series/skill-nexus/2026/04-eval)                  |
| 05       | [进化引擎：让 Skill 自动变好](/series/skill-nexus/2026/05-evo)                      |
| 06       | [Trending 榜单：你的 Skill 资产地图](/series/skill-nexus/2026/06-trending)         |
| 07       | [技术架构：Electron 双进程 + 零依赖进化 SDK](/series/skill-nexus/2026/07-architecture) |
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)             |
| 09       | [评测报告不只是看完就算——离线报告系统](/series/skill-nexus/2026/09-offline-report)         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

这篇是纯操作指南。目标：**从零开始，5 分钟内完成第一次 Skill 评测，看到 8 维度评分雷达图。**

***

## Step 1：安装

```bash
git clone https://github.com/skyseraph/SkillNexus.git
cd SkillNexus
npm install && npm run rebuild
npm run dev
```

支持 macOS 和 Windows。首次启动会引导你配置 LLM Provider。

***

## Step 2：配置 LLM Provider

进入 **Settings → LLM Providers**，选择你的 Provider：

| Provider  | 需要什么                          |
| --------- | ----------------------------- |
| Anthropic | API Key（claude-3-5-sonnet 推荐） |
| OpenAI    | API Key                       |
| DeepSeek  | API Key（性价比高，适合批量评测）          |
| Ollama    | 本地地址（完全免费，离线可用）               |
| 其他        | 兼容 OpenAI 格式的 baseURL + Key   |

填入 Key 后点 **Test Connection**，绿色即可。

***

## Step 3：导入你的 Skill

**Home 页面 → 扫描导入**

SkillNexus 会自动扫描以下目录：

* `~/.claude/skills/`（Claude Code）
* `~/.claude/commands/`（Claude Code slash commands）
* 你手动指定的任意目录

扫描完成后，所有 Skill 以卡片形式展示，包含名称、描述、标签、信任等级。

如果你还没有 Skill，推荐先跳到 [03 · Studio](/series/skill-nexus/2026/03-studio) 生成一个，再回来跑评测。

***

## Step 4：创建测试用例

选中一个 Skill，进入 **TestCase** 标签页，点击 **AI 生成用例**。

SkillNexus 会根据 Skill 的描述和指令，自动生成覆盖 8 个评测维度的测试用例。每条用例包含：

* **input**：发给 AI 的任务描述
* **expected**：期望的输出特征
* **judge\_type**：判断方式（LLM 评判 / 字符串匹配 / Shell 命令）

生成后可以手动调整，也可以直接用。**建议先用 3～5 条用例跑通流程。**

***

## Step 5：运行评测

进入 **Eval 页面**，选择目标 Skill，点击 **开始评测**。

评测过程：

1. 对每条测试用例，用选定的 LLM 执行 Skill
2. 用 Judge 对输出打分（0～10 分）
3. 汇总 8 个维度的得分

评测完成后，你会看到：

* **雷达图**：8 维度得分一览，直观看出强弱项
* **总分**：加权平均分
* **用例明细**：每条用例的输入、输出、各维度得分

***

## 看懂评分

8 个维度分两组：

**G 系列（任务质量）**——这个 Skill 产出的结果好不好：

* **G1 Correctness**：输出是否正确完成任务
* **G2 Instruction Following**：是否遵循格式约束
* **G3 Safety**：输出是否安全无害
* **G4 Completeness**：是否涵盖所有必要内容
* **G5 Robustness**：对边界输入的鲁棒性

**S 系列（Skill 质量）**——这个 Skill 本身写得好不好：

* **S1 Executability**：指令是否清晰可操作
* **S2 Cost Awareness**：是否简洁，避免 token 浪费
* **S3 Maintainability**：结构是否清晰易维护

**G 系列告诉你"有没有做对事"，S 系列告诉你"有没有把事做好"。**

***

## 下一步

有了评分，就可以让 Evo 引擎自动改进 Skill 了。

下一篇：[03 · 用 Studio 从零生成一个高质量 Skill](/series/skill-nexus/2026/03-studio)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
