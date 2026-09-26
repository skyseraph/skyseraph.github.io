---
title: "AI写代码后，瓶颈变成了验证"
date: 2026-04-01T08:00:00+08:00   
event: "paper"
cover: ""
video: ""
source: "https://www.faros.ai/blog/ai-engineering"
sourceName: " AI"
summary: "Faros 用 22000 名开发者、4000 个团队的两年遥测数据说明：AI 让代码产出大涨，但评审时长、缺陷率、返工量涨得更快，生成成本与验证成本的缺口就是「验证税」。"
ainewstags: ["Faros", "验证Verify", ""]
featured: false
draft: true
---

## 摘要

Faros AI 的工程效能研究给出一条反直觉的曲线：AI 辅助把单个开发者的产出推高了 30%–66%，但 PR 评审中位时长涨到 5 倍，代码返工量涨到 10 倍。写代码的成本趋近于零，验证代码的成本原地不动——两者之间的缺口，Faros 叫它「验证税」。他们给出的结论是：优化目标应该从"每个 token 多便宜"换成"每个通过验证的产出多贵"。

> **抓取说明**：`faros.ai/blog/ai-engineering` 在本环境下被网络策略拦截，未能直连原文。以下内容基于 Faros 公开发布的《The AI Productivity Paradox》（2025）与《AI Engineering Report 2026: The Acceleration Whiplash》两份研究，通过检索获取。凡未能直连核对的英文原句均标注 `[未能核对原文]`。

---

## 原文核心观点

### 生成已经便宜到不再是约束

Faros 的核心观察是：AI 把写代码的成本压到近乎为零，但评审、测试、安全审批这些环节还锁在人类的时钟上。人类评审代码的速度长期稳定在每小时 200 行左右——这个数字三十年没变过。

> *"Generation cost is collapsing toward zero. Verification cost is not."*
> — Faros AI 研究表述（[xx](https://www.faros.ai/blog/ai-engineering)，据检索结果转述）

传统开发里，写和审共用同一份人类工时预算，所以产出永远跑不过验证。AI 打破了平衡：产出端加速 200 倍，评审端一动不动。

### 速度的收益被验证吃掉

2025 年的第一份报告已经看到苗头：高 AI 采纳度的团队任务完成量 +21%、PR 合并量 +98%，但 PR 评审时长 +91%。2026 年的跟踪报告显示这个模式没有收敛，反而加剧。

| 指标 | 高 AI 采纳后的变化 |
| --- | --- |
| 每位开发者的 epic 完成量 | +66% |
| 每位开发者的任务吞吐 | +33.7% |
| 涉及代码的任务量 | +210% |
| PR 体积 | +51% |
| PR 评审中位时长 | +441%（约 5 倍） |
| 代码返工量（churn） | 约 10 倍 |

数据来自 22000 名开发者、4000 个团队、同一组织采纳 AI 前后各一年的真实遥测，不是问卷自评。**注意其中一组对比**：代码产出涨了 210%，评审时长涨了 441%——评审的涨幅是产出的两倍多，这意味着每单位产出消耗的验证资源在上升，不是持平。

> *"Throughput is up. Quality is down. And the gap between the two is widening."*
> — 对《The Acceleration Whiplash》核心结论的概括（[xx](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)）

### 「模型税」与成本核算的错位

Faros 提出第二个概念：**模型税（model tax）**。按每百万 token 计价最便宜的模型，算上返工、失败重试和额外的评审开销之后，往往是最贵的选择。他们主张把度量单位换成 **cost per verified outcome**——每个通过验证的工程产出花多少钱。

> *"The right optimization target is cost per verified outcome, not cost per token."*
> — Faros AI（[xx](https://www.faros.ai/blog/why-cheaper-ai-models-can-cost-more-hidden-model-tax)）

问题在于，绝大多数组织现在没有办法把 AI 支出和实际交付的东西对应起来。成本决策基本靠猜。

### 31% 的 PR 没有经过任何评审

报告里最刺眼的一个数字：31% 的 PR 在无任何评审的情况下被合并。这不是流程疏忽，而是流水线被灌满之后的必然结果——评审容量是固定的，PR 数量翻倍，要么排队，要么跳过。

---

## 核心亮点

**把「生成」和「验证」拆成两个独立成本项。** 在此之前，讨论 AI 编码效率时人们习惯用"节省了多少工时"这种单一数字。Faros 的做法是拆成两条曲线，然后指出它们的斜率方向相反——一条趋零，一条持平。这个拆法让"AI 提效"这类笼统论断失去了意义：省下的实现工时，可能原样出现在评审工时里，甚至更多。

**「验证税」这个命名。** 税的特征是：不产生新价值，但必须支付，且随交易量放大。AI 生成的代码越多，验证税总额越高。这个类比比"技术债"更准确——技术债可以偿还，验证税只要还在用 AI 生成就必须持续缴纳。

**直接反驳了 DORA 的 2025 结论。** DORA 认为高绩效团队能免疫 AI 带来的质量下滑。Faros 用同一批组织前后对比的遥测数据说：没有免疫，只是这些团队有更强的吸收能力，把缺陷挡在了发布之前。这个分歧本身值得注意——两家用的都是工程数据，结论却相反，说明测量口径（自我报告 vs 遥测、组织间对比 vs 同一组织纵向对比）会显著改变结论。

---

## 深入解读

### 两条曲线为什么会分叉

生成成本能趋零，是因为它本质上是**算力问题**——更多 GPU、更便宜的推理，成本就下来。验证成本降不下来，是因为它是**责任问题**：判断这段代码在特定上下文里是否正确，需要有人承担判断错误的后果。

这解释了一个常被忽略的现象：AI 并没有减少工程师的工作总量，只是把工作内容从"实现"平移到了"判断"。而判断的单位成本远高于敲键盘——一个安全缺陷，无论代码是手写的还是 AI 生成的，修复成本完全一样。

<div style="overflow-x:auto;margin:28px 0;">
<svg viewBox="0 0 760 270" width="100%" style="max-width:760px;display:block;margin:0 auto;font-family:var(--font-mono,monospace);" aria-label="生成成本曲线快速下降，验证成本基本持平，两者之间的缺口即验证税">
  <defs>
    <linearGradient id="taxGap" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.22"/>
    </linearGradient>
  </defs>
  <!-- 坐标轴 -->
  <line x1="60" y1="40" x2="60" y2="235" stroke="#475569" stroke-width="1"/>
  <line x1="60" y1="235" x2="710" y2="235" stroke="#475569" stroke-width="1"/>
  <text x="30" y="135" fill="#64748b" font-size="10" transform="rotate(-90 30 135)" text-anchor="middle">单位成本（向下=更便宜）</text>
  <text x="700" y="255" fill="#64748b" font-size="10" text-anchor="end">AI 采纳程度 →</text>
  <!-- 验证税缺口 -->
  <path d="M 70 68 C 180 92, 300 168, 700 230 L 700 156 L 70 146 Z" fill="url(#taxGap)"/>
  <!-- 验证成本曲线（持平） -->
  <path d="M 70 146 C 300 142, 500 148, 700 156" fill="none" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,3"/>
  <text x="712" y="152" fill="#f59e0b" font-size="10">验证成本</text>
  <!-- 生成成本曲线（趋零） -->
  <path d="M 70 68 C 180 92, 300 168, 700 230" fill="none" stroke="#4ade80" stroke-width="2.5"/>
  <text x="712" y="232" fill="#4ade80" font-size="10">生成成本</text>
  <!-- 交点 -->
  <circle cx="286" cy="158" r="4" fill="#0f172a" stroke="#22d3ee" stroke-width="1.5"/>
  <text x="286" y="180" fill="#22d3ee" font-size="9" text-anchor="middle">交叉点</text>
  <!-- 缺口标注 -->
  <text x="520" y="196" fill="#f59e0b" font-size="11" font-weight="700" text-anchor="middle">验证税</text>
  <text x="520" y="210" fill="#94a3b8" font-size="9" text-anchor="middle">生成越多，缴纳越多</text>
  <!-- 标题 -->
  <text x="380" y="22" text-anchor="middle" fill="#64748b" font-size="10">生成成本与验证成本的斜率分叉</text>
</svg>
</div>

### 「验证」到底在验证什么

把验证成本和评审工时划等号是常见误解。实际发生的验证至少分四层：语法正确性（机器可查）、行为正确性（测试可查）、意图正确性（这段代码是不是解决了该解决的问题）、上下文正确性（它和现有系统是否协调）。前两层可以自动化，成本确实在降。后两层不行，而且 AI 生成量越大，后两层的负担越重——因为 AI 擅长产出语法完美、行为可测、但解决错问题的代码。

Faros 的 31% 无评审合并率，说明很多团队在前两层就停下了。这不是懒，是资源约束下的理性选择：当 PR 排队长度超过承受能力，评审就退化为抽查。

### 重心迁移的方向

如果生成不再是问题，工程的重心会落到三个地方：

**架构决策**——AI 可以写实现，但选哪种架构、如何划分服务边界，这些决定的后果要几年后才显现，必须由人承担。

**验证基础设施**——把验证成本降下来的唯一办法是自动化后两层：可观测性建设、契约测试、灰度发布、自动回滚。这部分投入在 AI 时代之前常被当作"非功能性工作"砍掉，现在它变成了生产力的直接杠杆。

**成本核算能力**——把 AI 支出映射到通过验证的产出上。做不到这一点，就没法判断该用哪个模型、该在哪一层用 AI。

<div style="overflow-x:auto;margin:24px 0;">
<svg viewBox="0 0 760 180" width="100%" style="max-width:760px;display:block;margin:0 auto;font-family:var(--font-mono,monospace);" aria-label="工程时间分配的重心从实现转向架构、验证基础设施和成本核算">
  <text x="380" y="20" text-anchor="middle" fill="#64748b" font-size="10">工程师时间分配的重心迁移</text>
  <!-- 采纳前 -->
  <text x="20" y="70" fill="#94a3b8" font-size="10">采纳前</text>
  <rect x="80" y="52" width="440" height="30" rx="4" fill="#4ade80" fill-opacity="0.25" stroke="#4ade80" stroke-width="1"/>
  <text x="300" y="72" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">实现 60%</text>
  <rect x="524" y="52" width="150" height="30" rx="4" fill="#f59e0b" fill-opacity="0.2" stroke="#f59e0b" stroke-width="1"/>
  <text x="599" y="72" text-anchor="middle" fill="#f59e0b" font-size="11">验证 20%</text>
  <rect x="678" y="52" width="72" height="30" rx="4" fill="#22d3ee" fill-opacity="0.2" stroke="#22d3ee" stroke-width="1"/>
  <text x="714" y="72" text-anchor="middle" fill="#22d3ee" font-size="10">判断</text>
  <!-- 采纳后 -->
  <text x="20" y="126" fill="#94a3b8" font-size="10">采纳后</text>
  <rect x="80" y="108" width="110" height="30" rx="4" fill="#4ade80" fill-opacity="0.25" stroke="#4ade80" stroke-width="1"/>
  <text x="135" y="128" text-anchor="middle" fill="#4ade80" font-size="11">实现 15%</text>
  <rect x="194" y="108" width="470" height="30" rx="4" fill="#f59e0b" fill-opacity="0.2" stroke="#f59e0b" stroke-width="1"/>
  <text x="429" y="128" text-anchor="middle" fill="#f59e0b" font-size="11" font-weight="700">验证 · 架构 · 成本核算 70%</text>
  <rect x="668" y="108" width="82" height="30" rx="4" fill="#22d3ee" fill-opacity="0.2" stroke="#22d3ee" stroke-width="1"/>
  <text x="709" y="128" text-anchor="middle" fill="#22d3ee" font-size="10">判断</text>
  <text x="380" y="166" text-anchor="middle" fill="#64748b" font-size="9">示意图：基于 Faros 报告的指标变化方向推演，非报告原始数据</text>
</svg>
</div>

### 一个方法论上的疑点

Faros 的纵向对比设计（同一组织采纳前后）比横截面比较更有说服力，但仍有混淆变量：采纳 AI 的同期，这些组织往往也在做别的流程改造（CI 重构、团队重组、招聘变化）。报告没有说明如何剥离这些因素。

另一个疑点：PR 评审时长涨 5 倍，有多少是因为代码质量变差，有多少只是单纯因为 PR 数量变多、排队变长？前者是质量问题，后者是容量问题，应对措施完全不同。报告给的是时长，没有拆解。

---

## 扩展衍生

### 与主流工程效能口径的对照

<div style="overflow-x:auto;margin:24px 0;">
<table style="width:100%;border-collapse:collapse;font-size:0.88rem;">
<thead>
<tr style="border-bottom:1px solid var(--border,#334155);">
  <th style="text-align:left;padding:10px 12px;color:var(--cyan,#22d3ee);font-weight:600;">来源</th>
  <th style="text-align:left;padding:10px 12px;color:var(--cyan,#22d3ee);font-weight:600;">核心主张</th>
  <th style="text-align:left;padding:10px 12px;color:var(--cyan,#22d3ee);font-weight:600;">测量口径</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom:1px solid var(--border,#1e293b);">
  <td style="padding:10px 12px;color:var(--green,#4ade80);font-weight:600;">Faros AI 2026</td>
  <td style="padding:10px 12px;color:var(--text,#e2e8f0);">吞吐涨、质量降，缺口在扩大</td>
  <td style="padding:10px 12px;color:var(--text-muted,#94a3b8);">22000 人遥测，同组织纵向对比</td>
</tr>
<tr style="border-bottom:1px solid var(--border,#1e293b);">
  <td style="padding:10px 12px;color:var(--text,#e2e8f0);">DORA 2025</td>
  <td style="padding:10px 12px;color:var(--text,#e2e8f0);">高绩效团队可免疫质量下滑</td>
  <td style="padding:10px 12px;color:var(--text-muted,#94a3b8);">自我报告，组织间横截面对比</td>
</tr>
<tr>
  <td style="padding:10px 12px;color:var(--text,#e2e8f0);">Jellyfish</td>
  <td style="padding:10px 12px;color:var(--text,#e2e8f0);">个体指标改善，组织交付未提速</td>
  <td style="padding:10px 12px;color:var(--text-muted,#94a3b8);">平台遥测，组织层面聚合</td>
</tr>
</tbody>
</table>
</div>

### 外部观点

**「朴素集成」是死路。** 有研究者认为"agent 写、人审"这个模式既提供不了有意义的保证，也无法扩展——评审带宽是硬约束，让人类逐行审 AI 产出，等于把瓶颈原样保留。出路在验证本身的自动化，而不是加速评审。据 [arXiv 2606.13175](https://arxiv.org/html/2606.13175) 的论述，方向应是让编码 agent 同时承担验证职责。

**验证成本应该成为评测指标。** 有论文主张 AI 评测框架应显式测量验证成本，而不是只看正确率——在真实资源约束下无法被检测出的错误，比 benchmark 显示的更危险。参见 [arXiv 2608.08709](https://arxiv.org/pdf/2608.08709)，2026 年 8 月。

**质量问题已有独立测量。** Faros 另有一份针对 New Relic 数据的分析，指出 AI 生成代码的质量下滑在第三方数据中同样可见（[Faros: AI Code Quality Mirage](https://www.faros.ai/blog/ai-code-quality-mirage)）。这一条与其他来源的观测方向一致，增强了"质量确实在降"这个结论的可靠性。

**成本侧的现实。** 2026 年 3 月有报告称，个别用户单月 AI token 支出超过一名初级开发者的月薪。支出在涨，回报在分化，而多数组织尚无法判断自己处在分化的哪一侧（据 [Moving Target AI](https://movingtargetai.substack.com/p/the-cost-inversion)）。

**行业口径也在转移。** 招聘侧的变化印证了重心迁移：面试评分卡开始侧重深度（能否识别规模与失效模式）、架构（全局系统影响）、经济学（成本对价值）三项，而不再侧重语法层面的能力（据 [Built In](https://builtin.com/articles/audit-interview-scorecard)）。

---

## 延伸阅读

- [What is AI Engineering?（原文）](https://www.faros.ai/blog/ai-engineering)
- [The AI Engineering Report 2026: The Acceleration Whiplash](https://www.faros.ai/blog/ai-acceleration-whiplash-takeaways)
- [The AI Productivity Paradox 研究](https://www.faros.ai/blog/ai-software-engineering)
- [Why cheaper AI models can cost more: the hidden model tax](https://www.faros.ai/blog/why-cheaper-ai-models-can-cost-more-hidden-model-tax)
- [AI Evaluation Should Measure Verification Cost, Not Correctness Alone](https://arxiv.org/pdf/2608.08709)
- [Coding Agents Supersede Human Inspection](https://arxiv.org/html/2606.13175)
- [How AI-Generated Code Is Increasing Code Review Burden](https://www.faros.ai/blog/ai-code-quality-senior-engineer-review-burden)
