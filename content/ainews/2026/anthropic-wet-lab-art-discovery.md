---
title: "Anthropic湿实验室发现新酶系"
date: 2026-09-23T08:00:00+08:00
event: "paper"
cover: ""
video: ""
source: "https://techcrunch.com/2026/09/23/anthropic-says-its-biology-lab-has-already-found-something-big/"
sourceName: "TechCrunch"
summary: "Anthropic秘密运营的湿实验室公开亮相，950个Claude智能体协作21小时发现类CRISPR新酶系统ART，预印本已发布，功能尚待确认。"
ainewstags: [科学AI, 论文研究, 智能体, 产品更新]
featured: false
draft: false
---

## 摘要

2026年9月23日，Anthropic宣布其分子生物学湿实验室正式公开亮相，该实验室自2026年春季起已秘密运营。首个公开成果是：950个Claude智能体协作运行约21小时，发现了一种此前未被表征的新型酶系统——阵列相关逆转录酶（ART，array-associated reverse transcriptases）。ART的重复阵列结构与CRISPR阵列高度相似，但其生物学功能尚不明确，预印本已发布且未经同行评审。

## 原文核心观点

- Anthropic湿实验室位于旧金山湾区，运营于BSL-1和BSL-2生物安全级别，不处理人类病原体。

- ART酶系统由三个组件构成：一个逆转录酶、一个邻近伴侣基因，以及一个包含3至21个等间距短重复拷贝的非编码DNA重复阵列，该结构在形态上类似于CRISPR阵列，主要发现于噬菌体（感染细菌的病毒）中。

- 发现过程完全由AI完成：950个Claude智能体并行协作，耗时约21小时完成筛查和标注。

  > *"The ultimate test in conducting biological research is actual lab work."*
  > — Eric Koudelaer-Abrams，Anthropic生命科学负责人

- Anthropic承认ART的精确功能和生物技术应用潜力目前仍不清楚。

## 核心亮点

**AI首次在生物实验室中完成从计算发现到预印本的完整闭环。** 以往AI辅助生物研究多停留在计算预测层面，Anthropic此次将湿实验室验证纳入流程，意味着AI不再只是数据分析工具，而是实验研究的主动驱动者。

**950个并行Agent协作完成科学发现，改变了研究的时间尺度。** 21小时完成人工可能需要数月的文献筛查和序列分析，这是大规模多Agent系统在硬科学领域的首批实证结果之一。

**逆转录酶系统与CRISPR类结构的结合暗示潜在的基因编辑应用路径。** 细菌使用逆转录酶将RNA逆转录为DNA作为抗病毒防御机制，ART的结构若功能得以确认，可能开辟与现有CRISPR体系互补的新工具路线。

## 深入解读

### 湿实验室战略的意图

Anthropic一贯以AI安全研究为主轴，进入生物实验室领域是明显的战略扩展。与DeepMind的AlphaFold路线不同，Anthropic选择直接建立湿实验室，将AI决策链延伸到物理实验环节，这意味着其目标不止于预测蛋白质结构，而是主动介入生物发现流程本身。这一布局值得关注的前提是：生物安全（biosecurity）既是Anthropic的核心风险议题，也是其选择BSL-1/2而非更高级别的边界。

### "发现"的认识论边界

ART的论文标题和报道措辞（"发现"、"类CRISPR"）在科学传播层面存在夸大风险。预印本尚未经过同行评审，ART的实际功能仍为未知——研究团队本身也明确表示"功能尚不明确"。发帖当日X上的1580万阅读量意味着公众预期已被拉高，若后续实验无法复现或功能确认困难，将面临较大的信誉压力。

### 多Agent系统进入硬科学的系统性挑战

950个智能体协作并不意味着无监督——背后仍需人类研究者设计任务分解方式、验证逻辑、以及决定何时将计算发现送入湿实验室验证。这一流程的可重复性、质量控制机制，以及如何避免智能体集群产生系统性偏差，是当前论文中尚未充分披露的部分。

## 扩展衍生

据 [The Scientist](https://www.the-scientist.com/anthropic-s-secretive-ai-powered-wet-lab-breaks-cover-and-makes-first-discovery-75037) 报道（2026-09-23），该实验室此前一直保持低调，此次主动公开是Anthropic有意将"AI用于科学发现"打造为差异化叙事的信号，区别于其他大模型公司以工程能力为核心的竞争轴。

从行业横向对比来看：

<table>
  <thead>
    <tr>
      <th>机构</th>
      <th>生物AI路线</th>
      <th>是否有湿实验室</th>
      <th>代表成果</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Anthropic</td>
      <td>多Agent协作 + 湿实验室验证</td>
      <td>✅ BSL-1/2</td>
      <td>ART酶系统（2026）</td>
    </tr>
    <tr>
      <td>DeepMind / Google</td>
      <td>结构预测 + 序列设计</td>
      <td>部分（通过合作）</td>
      <td>AlphaFold 3、AlphaProteo</td>
    </tr>
    <tr>
      <td>OpenAI</td>
      <td>通用推理辅助生物研究</td>
      <td>❌ 无公开实验室</td>
      <td>—</td>
    </tr>
    <tr>
      <td>Recursion Pharmaceuticals</td>
      <td>高通量表型筛查 + AI</td>
      <td>✅ 工业级</td>
      <td>药物管线（临床阶段）</td>
    </tr>
  </tbody>
</table>

据 [Cryptopolitan](https://www.cryptopolitan.com/claude-agents-crispr-like-enzyme-21-hours/) 报道（2026-09-24），外部研究者对该发现持谨慎态度，认为"类CRISPR"的描述在功能确认前是形态类比而非功能等价，呼吁等待同行评审结果。

## 延伸阅读

- [Anthropic says its biology lab has already found something big](https://techcrunch.com/2026/09/23/anthropic-says-its-biology-lab-has-already-found-something-big/) — TechCrunch
- [Anthropic's Secretive AI-Powered Wet Lab Breaks Cover](https://www.the-scientist.com/anthropic-s-secretive-ai-powered-wet-lab-breaks-cover-and-makes-first-discovery-75037) — The Scientist
- [Claude agents flag a CRISPR-like enzyme system in 21 hours](https://www.cryptopolitan.com/claude-agents-crispr-like-enzyme-21-hours/) — Cryptopolitan
- [Anthropic's 950 AI Agents Uncover CRISPR-Like Enzyme System](https://finance.yahoo.com/technology/ai/articles/anthropic-950-ai-agents-uncover-052038947.html) — Yahoo Finance
- [Anthropic's New Science Lab Announced Its First Major Discovery](https://www.forbes.com/sites/saibala/2026/09/25/anthropics-new-science-lab-announced-its-first-major-discovery-this-week/) — Forbes
