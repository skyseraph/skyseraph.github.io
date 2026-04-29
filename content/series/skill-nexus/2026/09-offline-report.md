---
title: "SkillNexus #09 · 评测报告不只是看完就算——SkillNexus 的离线报告系统"
slug: 09-offline-report
series: "SkillNexus"
issue: 9
categories: ["专栏"]
tags: ["SkillNexus", "Agent", "Skill",  "Claude Code"]
toc: true
draft: false
pin: false
summary: "一键导出自包含 HTML 报告 + 机器可读 JSON，离线可用"
description: "SkillNexus 支持一键导出 ZIP 报告包，包含完全自包含的 HTML 可视化报告和原始 JSON 数据。支持单次报告、A/B 对比报告和三条件基线报告，可用于 CI 质量门禁。"
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
| 08       | [现状与路线图：SkillNexus 的下一步](/series/skill-nexus/2026/08-roadmap)             |
| **→ 09** | **评测报告不只是看完就算——离线报告系统**（本篇）                         |
| 10       | [可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)   |

***

评测跑完，雷达图出来了，然后呢？

很多时候你需要的不只是"自己看一眼"——你需要把结果发给同事，存档留底，或者在没有网络的环境下回顾。

SkillNexus 的离线报告系统解决的就是这个问题。

***

## 一键导出 ZIP 报告包

在 Eval 页面任意一次评测结果右上角，点击 **导出报告**，SkillNexus 会生成一个 ZIP 包，包含两个文件：

```
skill-code-review-eval-20250115.zip
├── report.html    # 完整可视化报告，单文件，无需联网
└── data.json      # 原始评测数据，机器可读
```

**report.html 是完全自包含的单页应用**——所有图表、样式、数据都内联在这一个文件里，不依赖任何 CDN，不需要网络，双击即可在浏览器打开。

**data.json** 包含完整的原始数据：每条测试用例的输入、AI 输出、8 个维度的得分和违规详情、Judge 类型和参数。方便你用脚本做二次分析，或者导入其他工具。

***

## 报告里有什么

打开 report.html，你会看到：

**概览区**：

* Skill 名称、版本、评测时间、使用的 LLM Provider
* 总分（加权平均）和 8 维度得分一览
* 测试用例数量、通过率

**雷达图**：

* 8 维度当前得分的可视化截面
* 如果有历史数据，**叠加显示上一版本的轮廓，直观看出进化效果**

**用例明细表**：

* 每条测试用例一行：输入摘要、各维度得分、总分
* 点击任意行展开：完整输入、AI 完整输出、每个维度的评分理由和违规描述

**维度分析**：

* 每个维度的得分分布（箱线图）
* 最常见的违规类型（按频次排序）
* **得分最低的 3 条用例**（重点改进方向）

***

## 对比报告：A vs B

如果你跑了对比评测（两个版本并排），导出的报告会额外包含：

* 两个版本的雷达图叠加
* **差值热力图**：哪些维度 B 比 A 好，好多少
* 胜负统计：A 赢几维、B 赢几维、平局几维
* 用例级别的对比：同一条输入，两个版本的输出和得分并排

这个报告格式特别适合 **code review 场景**：进化了一个 Skill，想让团队成员确认进化是否有效，直接发 HTML 文件，对方不需要安装 SkillNexus 就能看到完整对比。

***

## 三条件基线报告

三条件受控实验（无 Skill 组 vs 当前版本 vs AI 生成对照）的报告是最有说服力的格式：

```
                裸模型    你的 Skill    AI 生成对照
总分              6.2        8.1           7.4
G1 正确性         6.8        8.5           7.8
G2 指令遵循       5.9        8.3           7.1
S2 成本意识       7.1        7.9           6.2
...

增益 Δpp（你的 Skill vs 裸模型）：+1.9
增益 Δpp（你的 Skill vs AI 对照）：+0.7
```

这个数字回答了一个根本问题：**这个 Skill 到底值不值得维护？**

如果你的 Skill 比裸模型只高 0.2 分，说明这个 Skill 几乎没有价值；如果比 AI 随机生成的对照还低，说明需要认真重写。

***

## data.json 的用法

原始数据文件的结构：

```json
{
  "skill": {
    "name": "code-review",
    "version": "v3",
    "content": "..."
  },
  "eval_config": {
    "provider": "anthropic/claude-3-5-sonnet",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "summary": {
    "total_score": 8.1,
    "dimensions": {
      "G1": 8.5, "G2": 8.3, "G3": 9.1,
      "G4": 7.8, "G5": 7.2,
      "S1": 8.6, "S2": 7.9, "S3": 8.4
    }
  },
  "cases": [
    {
      "input": "...",
      "output": "...",
      "scores": { "G1": 9, "G2": 8 },
      "violations": { "G4": ["未覆盖边界情况：空输入"] },
      "details": { "G1": "输出正确，逻辑清晰" }
    }
  ]
}
```

几个常见用法：

**批量分析多次评测的趋势**：

```python
import json, glob
scores = []
for f in glob.glob('eval-reports/*/data.json'):
    d = json.load(open(f))
    scores.append({'date': d['eval_config']['timestamp'], 'score': d['summary']['total_score']})
```

**提取所有违规描述，找高频问题**：

```python
violations = []
for case in data['cases']:
    for dim, msgs in case['violations'].items():
        violations.extend(msgs)
# Counter(violations).most_common(10)
```

**CI 中的质量门禁**：

```bash
score=$(jq '.summary.total_score' data.json)
if (( $(echo "$score < 7.5" | bc -l) )); then
  echo "Skill quality below threshold: $score"
  exit 1
fi
```

***

## 报告的存档价值

离线报告的另一个用途是**历史存档**。

每次重要的 Skill 版本发布前，导出一份报告存档。几个月后回头看，你能清楚地看到这个 Skill 是怎么一步步变好的——不只是分数数字，而是具体的用例、具体的违规、具体的改进。

**这是 Skill 的"成长档案"，也是团队知识的沉淀。**

***

## 下一篇

报告里的图表是怎么设计的？为什么选雷达图而不是柱状图？为什么要有箱线图？

下一篇：[10 · 可视化设计：为什么 Skill 评测需要 6 种图表](/series/skill-nexus/2026/10-visualization)

***

*SkillNexus · 2026 · skyseraph · [GitHub](https://github.com/skyseraph/SkillNexus)*
