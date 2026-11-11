---
title: "痛点为真，形态撞车：ProofGate 创意研究——「生成即证明」门禁已被 Aristotle 做出一半，活路在「反例优先」"
date: 2026-11-11T21:15:00+08:00
categories: ["技术"]
tags: ["形式验证", "AI编码", "创意研究"]
pin: false
toc: true
draft: false
---

> 研究对象：[《AI 产品洞察日报｜2026-11-11》创意 2](/series/aiproduct/2026/2026-11-11/)：ProofGate — PR 级「生成即证明」门禁。

## 摘要

**结论：改造后 Go——放弃「证明优先」，改做「反例优先」的证伪门禁。** 痛点一关证据过量：审查负担倒挂有了社区定量讨论，AI 生成测试「永远通过且看起来合理」成了共识性抱怨，形式验证的人力成本（50-100 倍于写代码）也有一手证词。但竞品检索发现日报的空白点判断已经过期一半：**Harmonic 的 Aristotle 不仅在做「AI 写证明 + Lean 机器检查」，连 ProofGate 设想的「已证明 / 反例 / 超出能力」三态输出都逐字实现了**，目前只差语言覆盖（Verilog/C，主流应用语言未开放）。正面做通用证明门禁等于撞进对方路线图；反例发现才是当下就能交付、不受「规约是否写对」质疑的价值——反例自己会说话。

## 一、日报的原始判断

日报创意 2 的定位是「对 AI 生成的纯函数代码自动生成正确性证明或反例，作为合并门禁」，MVP 为 6-8 周覆盖可形式化子集（算法、数据变换、金融计算），接 GitHub Actions 输出三态结果，定价对标高合规行业的人工审计人天成本。它承接洞察 6 的判断：[AlphaProof Code](https://deepmind.google/blog/introducing-alphaproof-code/) 把定理证明带进工程代码（[HN 538 分、170 评论](https://news.ycombinator.com/item?id=50439193)），「生成 + 证明」一旦成对出售，金融、航空、内核的 AI 编码就解锁，「把 proof-carrying code 做成 CI 门禁的团队先吃头啖汤」。

这个判断隐含两个待检验的命题：一是 AI 代码的信任缺口真的大到有人为「证明」付钱；二是「证明门禁」这个产品位置还空着。趋势记录里「模型信任」已连续两日出现，本研究同时是对该趋势的回检。

## 二、审查倒挂、测试失效、证明太贵

痛点证据不仅够三条，而且三条各占一个独立侧面。

**侧面一：审查负担倒挂，有社区定量讨论。** r/ClaudeCode 的帖子标题就是一份痛点自白——[《Anyone else spending more time reviewing AI code than writing it?》](https://www.reddit.com/r/ClaudeCode/comments/1rv83qo/anyone_else_spending_more_time_reviewing_ai_code)，发帖人批量采用 AI 编码半年后发现自己写代码确实快了，但整体时间反而更长，"kinda ironic"。[Builder.io 的调研](https://www.builder.io/blog/developers-drowning-in-ai-prs)给出数字：96% 的开发者不完全信任 AI 生成代码，38% 认为审查它比审查人写的更费劲；[CIO 年初的报道](https://www.cio.com/article/4117049/developers-still-dont-trust-ai-generated-code.html)补充了原因——冗长输出、无谓的复杂度、过度自信的注释。

**侧面二：AI 测试失效，「绿了」不再等于「对了」。** AlphaProof 的 HN 讨论里，最高赞主线从一条质疑开始：一位开发者让 Claude 形式化验证过自己的加密与存储代码：

> *"It wrote theorems that looked fine and the formal verification passed but the resulting code contained many, many bugs"*
> — HN 评论，[AlphaProof Code 讨论](https://news.ycombinator.com/item?id=50439193)

同帖另一位用户讲了完整的翻车故事：agent 跑了几小时完成重构、自愿附赠全套测试、全绿，仔细一看整个实现方向是反的——并得出结论 *"it might as well have written me a mathematical proof for the code it wrote, and the proof would have passed, and the code would still be wrong!"*。跟帖一句 *"This is why I think tests are useless if written by AI. They will always pass and look reasonable."* 把痛点钉死：测试与代码同源时，验证形同虚设。

**侧面三：形式验证的替代品太贵，贵到没人用得起。** 同帖一位有实操经验的评论者给出成本量级：

> *"Driving a lean proof manually is a lot of effort. It's often 50x or 100x the effort of writing the initial program in the first place."*
> — HN 评论，[AlphaProof Code 讨论](https://news.ycombinator.com/item?id=50439193)

付费行为侧同样有锚：[AWS 内部开设 Dafny 培训课程](https://dafny.org/blog/2023/12/15/teaching-program-verification-in-dafny-at-amazon/)并用它[验证 Cedar 授权引擎](https://www.amazon.science/blog/how-we-built-cedar-with-automated-reasoning-and-differential-testing)；[Certora 融资 4320 万美元](https://finder.startupnationcentral.org/company_page/certora)给 Aave 等协议做付费验证；更宏观的是 [CodeRabbit 以 15 亿美元估值融 1.43 亿美元](https://www.reuters.com/technology/ai-code-review-platform-coderabbit-valued-15-billion-latest-funding-round-2026-08-12)，把自己定位成 AI 代码的治理层——为 AI 代码质量付钱的预算池已经存在，问题只是流向「LLM 再看一遍」还是「机器检查的证明」。

痛点验证通过，无需降级。真正的变量在竞品。

## 三、三态门禁已被做出一半

直接竞品检索的结果比 KeyTrail 案例更戏剧性：日报设想的产品形态，不是一个近似物，而是一个逐字命中。

[Aristotle](https://www.harmonic.fun/aristotle) 是 Harmonic 公司（[IMO 金牌级自动定理证明器 Aristotle](https://arxiv.org/abs/2510.01346) 的作者团队）的产品，首页定位一句话与本创意的痛点假设完全同源：*"Your agents write more code than your team can review. Aristotle finds what your code must get right and proves it on every commit."*。工作方式是代码编译进 Lean（确定性编译器）、AI 从自然语言描述生成定理并逐步提出证明、Lean 内核检查每一步。而它的结果输出是三态：**Proved**（附所依赖的假设）、**Refuted**（附可运行的反例）、**Unresolved**（标注未能判定）——与 ProofGate MVP 设计的「已证明 / 反例 / 超出能力」三态语义逐字相同。定价按用量计费、无席位、支持 on-prem，客户已含 ASIC 团队与核聚变设施。

| 竞品 | 形态 | 与 ProofGate 的重叠 | 弱点 |
|---|---|---|---|
| [Harmonic Aristotle](https://www.harmonic.fun/aristotle) | AI 写证明 + Lean 检查，按 commit 验证，用量计费 | **几乎全部**：三态输出、CI 定位、反例回放 | 目前只支持 [Verilog 和 C](https://www.harmonic.fun/aristotle)，主流应用语言未开放；聚焦硬件与固件客户 |
| [DeepMind AlphaProof Code](https://deepmind.google/blog/introducing-alphaproof-code/) | 多 agent 框架：专家定规约、Gemini Carbon 生成数百万行 Lean 证明 | 证明引擎的天花板参照；[验证工件已开源](https://deepmind.google/blog/introducing-alphaproof-code/) | 研究框架而非自助产品，[HN 评论直指](https://news.ycombinator.com/item?id=50439193) *"This is not a 'verify my code' kind of product"* |
| [Kani / CBMC](https://github.com/model-checking/kani) | 开源有界模型检查（Rust/C），[失败时可生成回放反例的单测](https://model-checking.github.io/kani/usage.html) | 反例态的技术底座 | 需人手写 proof harness；保证仅在展开边界内成立 |
| [Dafny](https://dafny.org) | 验证感知语言，[AWS 用于 Cedar 等生产系统](https://www.amazon.science/blog/how-we-built-cedar-with-automated-reasoning-and-differential-testing) | 「生成即证明」的语言级做法 | 要求用 Dafny 重写，无法验证存量 Python/Java 代码 |
| [Certora](https://www.certora.com) | 智能合约形式验证，[Prover 已开源](https://www.certora.com/blog/certora-goes-open-source) | 付费验证的商业模式先例 | 绑定 EVM 生态，出了智能合约圈没有分发 |

间接方案（用户现在怎么凑合）：CodeRabbit / [Greptile](https://siliconangle.com/2025/09/23/greptile-bags-25m-funding-take-coderabbit-graphite-ai-code-validation) / [Qodo（融资 1.2 亿美元）](https://tracxn.com/d/companies/qodo/__wtaaFohGzayV3JMoVN-4Q-oj9cTOWqJDEwt9nGxQNZA) 的 AI 代码审查——便宜、零接入成本，但本质是「再用一个 LLM 看一遍」，无形式保证；AI 测试生成——已被侧面二的用户证词判了死缓；SAST/SBOM——静态规则扫描，查的是模式不是语义正确性。

判断：**空白点不成立一半。**「三态证明门禁」作为产品形态已被 Aristotle 占位，剩下的是语言与客群空隙——Python/TypeScript/Java 的应用层、GitHub Action 开箱即用、面向 AI 生成代码的规约自动生成。但这个空隙不是护城河，是对方公开宣告的路线图（"more on the way"）。

## 四、证明贵，反例便宜

日报 MVP 的「自动生成正确性证明」需要一次诚实的拆解：三态里两态的技术成熟度完全不对称。

**反例态：现成引擎，今天就能跑。** Python 侧有 [CrossHair](https://github.com/pschanely/crosshair)（SMT 符号执行，可作为 [Hypothesis 的后端](https://pschanely.github.io/2021/08/25/hypothesis-crosshair-integration.html)），Rust/C 侧有 Kani/CBMC。HN 上已有实践者验证了这条链路的增量价值：*"Even for stuff I thought was really logically tight, Lean found a few minor things I had to fix. Similar to fuzzing where I have never not found bugs"*。LLM 在这里的角色是自动生成规约与 proof harness——把「人写不动」的部分吃掉，[DafnyBench](https://namin.seas.harvard.edu/pubs/dafnybench.pdf) 一类基准也证明 LLM 辅助 Dafny 验证在快速进步。

**证明态：可行但不便宜，且时延是硬伤。** AlphaProof 验证一个 Signal 协议库用了四周期、数百万行 Lean；Aristotle 靠的是 IMO 金牌级的专有证明模型。PR 门禁的预算是分钟级，证明搜索是小时级（推断）——MVP 里「已证明」态只能覆盖小纯函数，覆盖率会难看。

关键技术风险两个。**其一，规约瓶颈**：形式验证三十年的教训是写规约比写代码难，HN 讨论里被反复重申——*"You'd just move from bugs in code to bugs in the spec"*，而 AI 生成规约引入新变体：模型可能为凑证明改写规约（侧面一那条"many, many bugs"评论就是实例）。**其二，可形式化子集的覆盖率**：纯函数在业务代码里占比有限，*"The scope of what we can verify is still tiny"* 是社区对验证范围的共识——门禁只查 5% 的代码时，用户很快学会无视它（推断）。外部依赖：GitHub Actions 生态位、开源证明引擎、以及跑证明搜索的 LLM API 账单。超出 MVP 能力的部分：并发、IO、GUI 与整程序行为验证，这些在可见的未来都做不了。

## 五、这个创意会怎么死

**死法一：Aristotle 正面碾压，且路线图压顶。** 三态输出、每 commit 验证、按量计费全都已在对方产品页上，语言扩展是明牌。更底层的是 HN 那条釜底抽薪的质疑：*"I do not understand how this is materially different to just asking existing frontier model to 'rewrite thing in Lean', then check for verifiably unintended diffs."*——当前沿模型的重写与证明能力每季度上一个台阶，独立门禁产品的技术溢价会被模型能力直接吸收（推断：DeepMind 已开源验证工件，正是这种吸收的先兆）。

**死法二：spec 瓶颈无解，「证明」证明错了东西。** ProofGate 卖的是「这段代码正确」，但形式方法只能证明「代码符合规约」。金融客户要的正确是业务意图正确——而意图恰恰是规约捕获不到的部分：*"In many cases we don't even know ourselves what the program should do"*。AI 生成规约 + AI 生成证明的组合还制造出信任两头悬空：HN 评论称之为 *"Truly a trusting trust scenario"*。高合规行业恰恰是最有耐心问你「你的规约谁审的」的客户。

**死法三：成本结构与门禁时延互相拆台。** 同帖的黑色幽默——*"it'll be much better once each CI run costs $10,000 for the AI to make sure you didn't break its giant proof"*。证明搜索吃 token 与算力，CI 要快又要便宜；为压时延缩小验证范围，又撞上死法二的覆盖率问题。加上 CodeRabbit 们手握渠道与信任（尽管[其企业案例已开始被社区审计质疑](https://www.reddit.com/r/ChatGPTCoding/comments/1x4fwxa/we_audited_coderabbits_enterprise_case_study_174)），一个初创公司在「AI 代码治理」大类里再讲一个更贵、更慢、更窄的故事，销售上没有胜算（推断）。

## 六、改造后 Go——从「证明门禁」退到「证伪门禁」

**三选一结论：改造后 Go。** 一句话理由：痛点真实、预算池存在，但「证明优先」的通用门禁与 Aristotle 逐字撞车且被巨头路线图覆盖；把第一交付物从 Proved 换成 Refuted——反例用现成引擎（CrossHair/Kani）、分钟级时延、且天然免疫「规约写没写对」的质疑，因为一个能复现的反例不需要你信任任何东西。

改造后的定位：**证伪门禁（refutation-first gate）**——LLM 从代码与注释自动生成属性规约，符号执行引擎只找反例，PR 上挂出「反例（可复现）／未发现（附覆盖说明）」两态；「已证明」降级为远期路线图，等证明成本降到 CI 预算内再启用。目标客群避开 Aristotle 的硬件/固件主场，打 Python/TypeScript 的金融计算与数据变换场景——那里恰好是日报 MVP 指名的子集，也是 CodeRabbit 的 LLM 审查在语义正确性上最无能为力的子集（推断）。

**下周可执行的验证实验（成本 ≤ 1 天）**：取 10 个有标准答案的金融计算任务（复利、摊销、日期滚动利息、舍入规则等），让两个前沿模型各生成一份实现；再让 LLM 独立生成属性规约，接 CrossHair 符号执行跑反例。记录三个数：AI 生成代码的缺陷率、反例发现率（对照标准答案判定真假阳性）、每函数的平均机器耗时。若一天内能在 AI 生成代码里稳定挖出可复现的真实反例，证伪门禁的核心假设（反例态便宜且有效）成立；若 CrossHair 在这个子集上一无所获，则连改造方向也应放弃——反例都找不到的引擎，更不可能撑起证明。
