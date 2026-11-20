---
title: "谁验证验证者：Claude Code 团队如何让 90% AI 代码可信——3 类测试、39 条清单与一张不许自己改的考卷"
date: 2026-11-16T08:00:00+08:00
event: "agent"
cover: "https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/og.png"
video: ""
source: "https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/"
sourceName: "claude.dev Blog"
summary: "Claude Code 团队公开验证方法论：约 90% 代码由 Claude 编写评审，靠三类测试与不可自改的检查体系托底。"
ainewstags: ["Anthropic", "Claude-Code", "验证Verify"]
featured: false
draft: false
---

## 摘要

2026-11-16，Addy Osmani 在 claude.dev 发文披露：Claude Code 团队约 90% 的代码由 Claude 编写并评审，支撑这一比例的是一套完整的验证体系。但真正值得写的不在"90%"这个数字里，而在三处细节：其一，验证规则（REVIEW.md、提交门）放在改动无法触及的分支上——考卷不许自己改；其二，39 条可靠性清单按 diff 触发，每次通常只命中 3–10 条，没人需要背下全部事故史；其三，提交被拦截两次后第三次自动放行——门是故意留漏的，防止智能体卡死。

这篇文章拆三件事：三类值得投入的测试及其互补性；Claude Code 团队自己的验证流水线；这套方法论的前提条件与可复制性。

## 原文核心观点

**1. 验证回路是委托智能体干活的基石。** 没有验证回路，人只能盯一两个 Claude；有了它，可以并行跑几十上百个。内部测试中，让一个独立评分器按 rubric 检查 Claude 的产出，任务成功率比标准提示循环最多高 10 个百分点，最难的题目提升最大。

> *"Verification loops are the building block that lets you delegate more work to Claude. Without them, you can really only run one or two Claudes at a time, because you have to check everything yourself. With them, you can run dozens or hundreds in parallel."*
> — claude.dev Blog, How the Claude Code team thinks about verification

> *"having a separate grader check Claude's work against a rubric improved task success by up to 10 points over a standard prompting loop, with the largest gains on the hardest problems."*
> — 同上

**2. 验证的经济学被反转了。** 过去昂贵的验证物（测试、基准、规格、真实端到端运行）现在可以让 agent 快速生成，而且生成之后作为软件运行，几乎不消耗额外 token。验证结果还能反哺 agent：反复失败同一测试，就写进 hook 或 CLAUDE.md 规则，问题基本不再复发。

> *"What was once expensive to verify (tests, benchmarks, specs, real end-to-end runs) is now cheap to request from an agent."*
> — 同上

**3. 测试质量决定 agent 行为模式。** flaky 的测试会训练 agent「重跑直到通过」而不是修代码；慢测试会减少迭代批次。重测试应部署在提交之前。

> *"If your tests are flaky you'll train the agent to run them again rather than fixing the failing code."*
> — 同上

**4. 只选一种测试就选端到端。** E2E 测试难以糊弄——整个功能要么好用要么不好用，有明确的完成判据，还能截图、给出失败步骤。单元测试更快更稳，但可能全部通过而功能仍是坏的，因为 agent 和测试都不理解完整任务。可以用 skill 让 agent 通过 CDP、模拟器、API harness 启动、驱动、检查真实应用，feature map 则充当评分 rubric。

> *"The reason E2E tests are so effective is that they are difficult to fool–either the whole feature works or it doesn't."*
> — 同上

<img src="https://claude.dev/media/3c9c60f4b0696a20f33ef62b6ddcb99c322fd19c440c28de234a6c804f7912a4.png" alt="单元测试失败 vs 端到端测试失败对比：前者只有一个超时报错，后者有步骤轨迹、截图和具体失败原因" style="max-width:100%;border-radius:6px;" />
<p style="text-align:center;font-size:0.85em;color:#888;">原文配图（FIG A）：单元测试只报 "Error: Timeout after 30s"，E2E 测试给出步骤轨迹、截图与「支付表单未加载导致下单按钮保持禁用」的具体归因。</p>

**5. 属性测试用无偏见的边界情况对抗 agent 的生成偏见。** 先写一句「不可能失败」的断言（往返编码、不变量、幂等、等价），再用 fast-check / Hypothesis / proptest 生成上千个输入试图推翻它。属性库生成的边界情况与写出原代码的 agent 不共享同一偏见，在规格已与生产行为漂移的重写场景中尤其有效。

> *"Property libraries are a great way to keep agents honest by using edge cases that aren't created with the same bias as the agent that created the original code."*
> — 同上

**6. 差分测试拿旧系统当标准答案。** 大规模迁移、功能预期不变时，新旧系统喂相同输入比对结果；输入用随机生成或生产流量采样，归一化空白字符，维护一份「批准的差异」清单。

**7. 验证就是真跑一遍，失败三轮才找人。** 团队为各类变更配备真实运行手段（Chrome 扩展、iOS/Android MCP、computer use、本地起服务），并把启动方式固化成仓库里的 `verify` skill——Claude 在提交前知道要用它。检查失败 Claude 先自己修，三轮仍未通过就停下来引入人类。

> *"If a check is still failing after three rounds, Claude stops and brings in a human."*
> — 同上

**8. 考卷不许自己改。** 评审规则 REVIEW.md 从 base 分支读取、绝不读 PR 里的修改；评审绑定具体 commit，push 之后评审结果作废；开 PR 前必须先本地跑测试、构建、linter。39 条可靠性清单每条都带「可从 diff 读出的触发条件」，Claude 只检查命中项，没人需要背事故史。

> *"If a change can modify the check that judges it, the check is broken."*
> — 同上

> *"A passing review on an out-of-date commit means nothing."*
> — 同上

**9. 新门禁先观察后强制，评审器本身也被评审。** 每个提交盖上验证方式戳（含 "none"，便于反查未验证提交）；提交门有 off / observe / enforce 三档，observe 只记录本应拦截的提交以便排查误报；被拦两次后下一次放行，防止 Claude 卡死。团队持续「评审评审器」：跟踪 revert 率、维护者驳回率，用历史事故重建评估集、分阶段（原始发现 / 验证后 / 终审）分别测召回，直到下一步提升会过拟合评估集为止。

> *"If commits have been blocked twice in the session, the next one will be allowed through so Claude doesn't get stuck – Claude Code isn't perfect."*
> — 同上

## 核心亮点

**「不可自改的考卷」被首次表述为工程红线。** 这不是泛泛的「要有测试」，而是明确的权限分离：生成权归改动，验证权归改动摸不到的地方（base 分支的 REVIEW.md、门规则、绑定 commit 的评审）。它把「谁验证验证者」从一个哲学问题降维成了一条分支策略。

**验证物变成了 agent 可再生的资产。** 传统观点里 E2E 测试、基准、规格是人力成本大户；此文把它们归入「可让 agent 生成、生成后近乎零成本复跑」的类别。验证贵这一经济学前提被推翻后，「并行跑几十上百个 Claude」才在成本上成立。

**评审系统自己也被当作被测系统。** 用真实事故重建评估集、给评审器分阶段测召回、拿稳定合并的变更做对照组防过度报告——「评审质量」从主观印象变成了可测量、可调参的指标，且团队自己划定了过拟合边界。

## 深入解读

### 三类测试是一张互补的防御网，不是三选一

| 维度 | E2E 测试 | 属性测试 | 差分测试 |
|---|---|---|---|
| 伪造难度 | 极高（功能整体可用才算过） | 高（输入由库生成，与 agent 不共谋） | 高（旧系统做 oracle） |
| 运行速度 | 慢，提交前跑 | 快，可上千次 | 取决于旧系统 |
| 最佳场景 | 用户关键路径、回归防线 | 解析/序列化、不变量、幂等 | 大规模迁移、重写 |
| 盲区 | 覆盖路径有限、较 flaky | 需要能写出「不可能失败」的断言 | 只验「与旧一致」，验不出旧系统本身的 bug |

值得多看一眼的是属性测试的定位：它对抗的不是普通 bug，而是**同源偏见**——测试作者和代码作者如果是同一个 agent，测试会继承代码的错误假设。属性库的随机输入是团队目前找到的最便宜的「独立第三方」。差分测试则诚实地标定了自己的边界：它只能保证「和旧系统一样」，旧系统原有的 bug 会被原样继承。

### 「谁验证验证者」：团队的分层回答与残余风险

verify skill 本身也是 Claude 写的，验证层凭什么可信？原文的回答是一个多层结构：

<svg viewBox="0 0 720 340" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;background:#faf9f5;border-radius:8px;">
  <!-- 生成区 -->
  <rect x="40" y="20" width="640" height="110" rx="10" fill="#f0ece4" stroke="#b8b2a6" stroke-dasharray="6 3"/>
  <text x="60" y="46" font-size="13" fill="#6b6455" font-weight="bold">生成区（Claude 可修改）</text>
  <rect x="60" y="60" width="180" height="52" rx="6" fill="#fff" stroke="#b8b2a6"/>
  <text x="150" y="82" font-size="12" text-anchor="middle" fill="#333">代码改动 / PR</text>
  <text x="150" y="100" font-size="11" text-anchor="middle" fill="#888">先本地跑测试·构建·lint</text>
  <rect x="280" y="60" width="180" height="52" rx="6" fill="#fff" stroke="#b8b2a6"/>
  <text x="370" y="82" font-size="12" text-anchor="middle" fill="#333">verify skill</text>
  <text x="370" y="100" font-size="11" text-anchor="middle" fill="#888">模拟器/浏览器/MCP 真跑</text>
  <rect x="500" y="60" width="160" height="52" rx="6" fill="#fff" stroke="#b8b2a6"/>
  <text x="580" y="82" font-size="12" text-anchor="middle" fill="#333">提交门</text>
  <text x="580" y="100" font-size="11" text-anchor="middle" fill="#888">off / observe / enforce</text>
  <!-- 验证区 -->
  <rect x="40" y="170" width="640" height="120" rx="10" fill="#eef2ee" stroke="#7a967a"/>
  <text x="60" y="196" font-size="13" fill="#4a644a" font-weight="bold">验证区（base 分支只读，改动不可触及）</text>
  <rect x="60" y="210" width="180" height="60" rx="6" fill="#fff" stroke="#7a967a"/>
  <text x="150" y="235" font-size="12" text-anchor="middle" fill="#333">REVIEW.md</text>
  <text x="150" y="253" font-size="11" text-anchor="middle" fill="#888">从 base 分支读取</text>
  <rect x="280" y="210" width="180" height="60" rx="6" fill="#fff" stroke="#7a967a"/>
  <text x="370" y="235" font-size="12" text-anchor="middle" fill="#333">39 条可靠性清单</text>
  <text x="370" y="253" font-size="11" text-anchor="middle" fill="#888">diff 触发，命中 3–10 条</text>
  <rect x="500" y="210" width="160" height="60" rx="6" fill="#fff" stroke="#7a967a"/>
  <text x="580" y="235" font-size="12" text-anchor="middle" fill="#333">事故重建评估集</text>
  <text x="580" y="253" font-size="11" text-anchor="middle" fill="#888">分阶段测召回</text>
  <!-- 箭头 -->
  <line x1="150" y1="112" x2="150" y2="170" stroke="#7a967a" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="370" y1="112" x2="370" y2="170" stroke="#7a967a" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="580" y1="112" x2="580" y2="170" stroke="#7a967a" stroke-width="1.5" marker-end="url(#arrow)"/>
  <!-- 出口 -->
  <rect x="40" y="304" width="280" height="28" rx="6" fill="#fdf6ec" stroke="#c9a86a"/>
  <text x="180" y="323" font-size="11.5" text-anchor="middle" fill="#7a6435">失败 3 轮 → 引入人类</text>
  <rect x="400" y="304" width="280" height="28" rx="6" fill="#fbeeee" stroke="#c07a7a"/>
  <text x="540" y="323" font-size="11.5" text-anchor="middle" fill="#8a4a4a">被拦 2 次 → 第 3 次放行（故意留漏）</text>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#7a967a"/>
    </marker>
  </defs>
</svg>

规则进入验证区的门槛也不低：从人工评审评论和 revert 中提取的模式须在至少两个 PR 中出现且能从 diff 识别，再由三个 agent 尝试证伪，最后人类在 PR 里审批。剩余的软肋原文没有回避：评估集与调参集分离、召回调到「再往上就是过拟合」为止——这意味着评估集质量成为整个体系的天花板，而评估集本身来自团队自己的历史事故，存在选择偏差。「被拦两次即放行」则明说了这是效率与安全的折中，不是纯洁的门槛。

### 这套方法论的隐含前提，以及「90%」该怎么读

逐条看这些实践——三轮失败引人、39 条清单、规则双人审批、评审器评估集——会发现它们共享一个前提：**有人持续维护验证层**。测试套件、验证步骤、`.md` 规则「只会增长，除非你定期修剪」，原文也承认要例行清理。没有事故积累、没有专人维护的团队照搬骨架，得到的可能只是一堆没人信的检查项。

数字本身也要审着读：「约 90%」是「编写并评审」的合并口径，未区分难度分布与人工复核比例；「提升 10 个百分点」出自结构化文件生成的内部测试，不是通用编码任务；两者都是自报数据，无外部复核。方向性结论（验证回路显著提高可委托度）可信，精确数值仅供参考。

## 扩展衍生

**姊妹篇与系列脉络。** 此文是 Addy Osmani 关于 Claude Code 工程实践的系列之一。此前的《How the Claude Code team does code review》（与 Morgan Westlee Lunt、Qing Wang 合写，2026-10-15 前后发布，[X 文章版](https://x.com/addyosmani/article/2114604912520921136)）给出了配套数据：2026 年 6–9 月间，合并 PR 数量翻倍以上，revert 率下降超 40%。另有《Practical Loop Engineering》（Addy 的 Elevate newsletter）讨论 agent 循环与停止条件，可视为本验证方法论的抽象层。

**传播与报道。** 据 [X 热点页](https://x.com/i/trending/2122502788542550282)（2026-11 中旬），"Anthropic's Claude Writes 90% of Team Code" 成为热议话题；AI/TLDR 等 newsletter 以「verification playbook」角度做了摘报。传播焦点明显偏向「90%」这一数字而非验证体系本身——恰是原文里最需要审读的部分。

**批评声音。** HN 上对 Claude Code 自身代码质量的质疑在此文发布前后一直存在：在 [What Claude Code's Source Revealed About AI](https://news.ycombinator.com/item?id=47772282) 的讨论中，有评论认为以其源码表现「对任何业务来说都是不可接受的」（据搜索摘要转述，原帖发布于源码泄露事件后）；另有讨论称 Claude Code 正成为「vibe coded 产品危险性的典型样本」。这些批评针对的是产品代码质量，与本文「验证方法论降低并行风险」的论点构成互补而非否定——但也提示：90% 覆盖率与最终质量之间没有必然等号。

## 延伸阅读

- [How the Claude Code team thinks about verification（原文）](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/)
- [How the Claude Code team does code review（姊妹篇，X 文章版）](https://x.com/addyosmani/article/2114604912520921136)
- [What Claude Code's Source Revealed About AI — HN 讨论](https://news.ycombinator.com/item?id=47772282)
- [X 热点讨论：Anthropic's Claude Writes 90% of Team Code](https://x.com/i/trending/2122502788542550282)
- [Addy Osmani 关于本文的 X 帖](https://x.com/addyosmani/status/2122590683055993308)
