---
title: "Vibe Coding 深度观察：一场关于编程本质的世纪之争"
date: 2026-04-12T22:00:56+08:00
categories: ["技术"]   # 技术 / 随笔 / 项目
tags: ["LLM","Agentic","Vibe Coding","Harness","Hermes Agent","OpenClaw","未来编程"]
toc: true
draft: false
---

> 作者：SkySeraph  
> 原始链接：[vibe-coding](https://skyseraph.github.io/posts/2026/vibe-coding)  
> 日期：2026-04-12     
> 开源工具：[SkillNexus](https://github.com/skyseraph/SkillNexus)   

---

## 目录

1. [起源：一条"随手发的推文"引爆全球](#1-起源)  
2. [关键数据：一年内规模有多大](#2-关键数据)  
3. [业内大咖观点全梳理](#3-业内大咖观点)  
4. [核心争议：三组真正的分歧](#4-核心争议)  
5. [技术现实：能力边界的实证](#5-技术现实)  
6. [演进方向一：Agentic Engineering（Karpathy）](#6-演进方向一)  
7. [演进方向二：OpenClaw — Gateway-First 生态范式](#7-演进方向二-openclaw)  
8. [演进方向三：Hermes Agent — Learning-First 自进化范式](#8-演进方向三-hermes-agent)  
9. [演进方向四：Harmless AI — Constitutional AI 安全范式](#9-演进方向四-harmless-ai)  
10. [未来程序员的主要工作与核心价值](#10-未来程序员)  
11. [对开发者、团队和组织的建设性建议](#11-建设性建议)  
12. [个人思考：编程的本质是否变了？](#12-个人思考)  
13. [参考来源](#13-参考来源)

---

## 1\. 起源：一条"随手发的推文"引爆全球

2025年2月6日，Andrej Karpathy 在 X 上发了一条他后来称之为"随手一写的淋浴思考推文"（*a shower of thoughts throwaway tweet*）。原文核心如下：

"There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists. I just see stuff, say stuff, run stuff, and copy-paste stuff, and it mostly works."

—— Andrej Karpathy，2025年2月6日，X（原推文 4.5 million 浏览）[^1]

这条推文迅速获得 450 万次浏览，成为 2025 年科技圈最具话题性的词汇引爆点之一。Karpathy 描述了一种开发体验：用自然语言描述意图，AI 生成代码，报错直接粘贴回 AI，循环直到它跑起来——全程几乎不看代码，更不去理解代码。

这条推文命中了一个集体情绪：无数开发者正在用 Cursor、Claude、Copilot 进行类似实践，只是缺少一个准确的词汇。"Vibe Coding"在命名的那一刻，同时完成了对一种方法论的合法化宣告。

**重要里程碑：**

- **2025年3月**：Merriam-Webster 将"Vibe Coding"收录为"俚语与流行词"[^2]  
- **2025年末**：Collins English Dictionary 评选其为**2025年度词汇**[^3]  
- **2026年2月**：Karpathy 发文宣告范式演进，提出"Agentic Engineering"[^4]

值得注意的是，Karpathy 在原推文中保留了脚注：AI 有时确实无法修复某个 bug，代码也会增长到超出他自己的理解范围。他承认这"相当有趣"，但也许最适合非关键项目。[^5]

---

## 2\. 关键数据：一年内规模有多大

Vibe Coding 并不是少数极客的实验，它在 2025 年触及了整个软件工业。

| 指标 | 数值 | 来源 |
| :---- | :---- | :---- |
| Google 搜索量单季涨幅 | **\+6,700%** | Exploding Topics，2025年春季 [^6] |
| 2025年全年 AI 参与生成代码占比 | **\~41%** | TATEEDA/GLOBAL 研究报告 [^7] |
| 开发者已使用或计划使用 AI 编码工具 | **84%** | 行业调查，2025年末 [^8] |
| Vibe Coding 用户中非专业开发者占比 | **63%** | v0 State of Vibe Coding Report [^9] |
| YC W2025 批次 95% 代码由 AI 生成的初创比例 | **25%** | Y Combinator，2025年3月 [^10] |
| AI 协作代码安全漏洞率（vs 人工） | **2.74×** | CodeRabbit 分析，2025年12月 [^11] |
| AI 生成代码引入安全漏洞的比例 | **45%** | Veracode 研究，2025年 [^12] |
| 开发者对 AI 工具正面情绪（2025年） | **60%**（从2024年70%下滑） | Stack Overflow 2025年度调查 [^13] |

**最反直觉的数据**：METR 随机对照实验（2025年7月）显示，有经验的开源开发者使用 AI 工具反而比不用**慢 19%**，尽管他们预测自己会快 24%，事后仍认为自己快了 20%。[^14] 感知与客观效能存在严重偏差，这是整个 Vibe Coding 热潮中最值得深思的认知偏差。

**Karpathy 本人的逆转**：2025年10月，他构建 Nanochat（8,000 行 Python \+ Rust 的 ChatGPT 克隆）时，坦承"基本全部手写"，因为"尝试用 Claude/Codex 代理，但它们在这种规模的项目上表现不够好，总体上没有帮助"。[^15] 概念的提出者，在严肃项目上却回归了传统方式。

---

## 3\. 业内大咖观点全梳理

### 3.1 支持与肯定派

**Andrej Karpathy（OpenAI 联合创始人，概念提出者）**

"你完全沉入 vibe，拥抱指数增长，忘记代码的存在。我甚至用语音让 AI 调整侧边栏的内边距。它大多数时候都有效。"  
—— X，2025年2月6日 [^16]

**Y Combinator（顶级创业加速器）**

W2025 批次中 25% 的初创公司拥有 95% AI 生成的代码库，反映了向 AI 辅助开发的结构性转移。  
—— YC 公开声明，2025年3月 [^17]

**Mario Rodriguez（GitHub 首席产品官）**

"Vibe Coding 解锁了创造力和速度，但只有在搭配严格的代码审查、安全保障和开发者判断力时，才能真正产生生产价值。"  
—— GitHub 公开声明 [^18]

---

### 3.2 质疑与批评派

**Andrew Ng（斯坦福教授，前 Google Brain 负责人）**

"这个名字很不幸，它让人误以为工程师只是随便接受或拒绝建议。实际上这是一项极其耗神的脑力活动——用 AI 编程一整天，我到晚上精疲力竭。"  
—— LangChain Interrupt 会议，2025年5月 [^19]

"告诉年轻工程师不必学编程是我听过**最糟糕的职业建议**。"  
—— 同上 [^20]

**Simon Willison（Django 联合创始人，开发者倡导者）**

"如果 LLM 写了你所有的代码，但你都仔细审查、测试、理解了——那在我看来这根本不是 Vibe Coding，那只是把 LLM 当打字助手。"  
—— simonwillison.net，2025年3月19日 [^21]

"Vibe coding your way to a production codebase is clearly risky. Most of the work we do as software engineers involves evolving existing systems, where the quality and understandability of the underlying code is crucial."  
—— 引自 Ars Technica [^22]

**Raymond Kok（Mendix CEO，Siemens 旗下）**

"Vibe Coding 快速且富有创意，但对企业用途而言极度不可靠。它生成的代码缺乏完整架构结构，bug 丛生，难以调试和集成到企业系统。"  
—— Technology Magazine 采访，2025年 [^23]

---

### 3.3 进化与重新定义派

**Andrej Karpathy（2026年重新定义）**

"今天（一年后），通过 LLM 代理编程正逐渐成为专业工作者的默认工作流——但需要更多监督和审查。目标是获取代理带来的杠杆效应，同时不在软件质量上有任何妥协。"  
—— X，2026年2月，"Agentic Engineering"概念发布 [^24]

**Thoughtworks 技术雷达（2025年度报告）**

"2025年的清晰信号：从 Vibe Coding 到 Context Engineering——软件工程的进步不再只是模型的规模和速度，而是有效管理 LLM 上下文的能力。人类开发者的角色正在演进，但依然绝对关键。"  
—— Thoughtworks Technology Radar，2025年 [^25]

**Scott H. Young（认知科学研究者）**

"Vibe Coding 基本上消除了所有实现难度，但我仍然面临大量概念难度——如何决定软件的行为。这种编程方式不需要写代码，但似乎确实依赖对软件工作原理的抽象认知。"  
—— scotthyoung.com，2025年11月 [^26]

**Fast Company（2025年9月报道）**

"Vibe coding 的宿醉来了。"——报道记录了资深工程师群体出现"开发地狱"、"有毒废料"、"AI 保姆"等词汇来描述与 AI 生成代码协作的痛苦现实。[^27]

---

## 4\. 核心争议：三组真正的分歧

### 4.1 "Vibe"的定义战争

这是最根本的争议。Karpathy 原始定义的核心是"忘记代码的存在"——接受一切 AI 建议，不阅读 diff，不理解逻辑，靠结果反馈驱动。Simon Willison 对此提出了精准的反驳：如果你审查、测试、理解了所有 LLM 生成的代码，那不是 Vibe Coding。[^28]

这造成了一个语义困境：人们在讨论"Vibe Coding"时，实际上描述的是三种截然不同的实践：

| 类型 | 代码审查 | 代码理解 | 适用场景 | 安全性 |
| :---- | :---- | :---- | :---- | :---- |
| **纯 Vibe Coding** | 跳过 | 不需要 | 原型/一次性 | ⚠️ 高风险 |
| **AI 辅助编程** | 逐行 | 完全理解 | 任何场景 | ✅ 可控 |
| **Agentic Engineering** | 目标导向 | 架构理解 | 生产级 | ✅ 系统保障 |

### 4.2 民主化还是劣质化

支持者最有力的论据是民主化：Replit 75% 的用户从未写过一行代码；领域专家可以直接将专业知识软件化。[^29]

但反对者的数据同样令人警醒：

- 62% AI 生成 SaaS 平台缺乏认证端点的速率限制 [^30]  
- Lovable 平台：1,645 个应用中 170 个暴露用户隐私数据 [^31]  
- AI 协作代码的配置错误率高出人工代码 75% [^32]

### 4.3 初级开发者消亡还是转型

数据显示，**高级开发者**（10年以上经验）更能从 Vibe Coding 中获益——有能力捕捉错误、设定架构约束、进行质量判断。相比之下，初级开发者采用比例更低（约13%），且难以从 AI 工具中获得实质性生产力提升。[^33]

这引发了一个更深的问题：当初级任务被 AI 自动化，10-20 年后谁来成为有经验的高级工程师？**经验本身是通过"做初级工作"积累的，如果积累路径被切断，软件工程的人才梯队将如何演进？**

---

## 5\. 技术现实：能力边界的实证

### 5.1 确实擅长的场景

| 场景 | 评价 | 典型案例 |
| :---- | :---- | :---- |
| 快速原型 | ✅ 显著有效 | 团队 1 小时内构建完整活动管理应用（原需数周） |
| 个人工具/脚本 | ✅ 极其有效 | Karpathy 的 YouTube 中文学习助手、水彩规划工具 |
| 领域知识软件化 | ✅ 革命性 | 医疗专家构建患者管理工具、教育者开发学习平台 |
| 重复性 boilerplate | ✅ 高效 | CRUD 接口、UI 组件、配置文件生成 |
| 学习与探索 | 🔵 适中 | 快速验证想法、了解新框架基本用法 |

### 5.2 真正的局限

| 局限 | 严重程度 | 说明 |
| :---- | :---- | :---- |
| 架构决策盲区 | 🔴 严重 | AI 优化当前问题，不考虑长期接口、故障模式和扩展性 |
| 技术债积累 | 🔴 严重 | 速度优先的代码随时间变得越来越难修改和维护 |
| 安全漏洞 | 🔴 极严重 | AI 实现功能，但不默认嵌入安全最佳实践 |
| 现有系统演进 | 🟡 较严重 | 大多数工程工作是维护现有代码库，AI 理解上下文能力有限 |
| 复杂调试 | 🟡 较严重 | METR 实验：有经验开发者使用 AI 工具反而慢 19% |
| 领域知识空白 | 🔵 场景相关 | AI 不会主动引入专业领域知识——需要人类主动引导 |

---

## 6\. 演进方向一：Agentic Engineering（Karpathy）

**代表人物**：Andrej Karpathy  
**提出时间**：2026年2月  
**核心论断**：Vibe Coding 已过时，专业工作流需要"Agentic Engineering"

Karpathy 在 2026 年 2 月发文[^34]，明确将"Agentic Engineering"定义为 Vibe Coding 的专业继承者：

"今天，通过 LLM 代理编程正逐渐成为专业工作者的默认工作流，**但需要更多监督和审查**。目标是获取代理带来的杠杆效应，同时不在软件质量上有任何妥协。"

与此同时，Thoughtworks 将其概括为从"Vibe Coding"到\*\*Context Engineering（上下文工程）\*\*的演进[^35]：

- 上下文管理（agents.md、Context7、Mem0）成为核心工程能力  
- 将代理锚定到参考应用，提供"上下文基准真相"  
- 多代理团队协作，分散单代理的上下文负担  
- 从"更多规模和速度"转向"有效处理上下文的能力"

**Vibe Coding → Agentic Engineering 对比：**

| 维度 | Vibe Coding | Agentic Engineering |
| :---- | :---- | :---- |
| 代码生成 | Accept All，不看 diff | 强 Spec 先行，系统性审查 |
| 代码理解 | 增长超出理解 | 架构理解，不妥协质量 |
| 上下文管理 | 随机/自然语言描述 | 显式上下文架构设计 |
| 安全性 | 靠运气 | 系统性安全保障流程 |
| 适用人群 | 所有人 | 专业工程师 |

---

## 7\. 演进方向二：OpenClaw — Gateway-First 生态范式

**项目起源**：2025年末，奥地利开发者 Peter Steinberger 的周末项目（原名 Clawdbot）[^36]  
**规模**：截至 2026 年 4 月，GitHub Stars 超过 **345,000**；拥有 5,700+ 社区构建技能 [^37]  
**语言**：TypeScript/Node.js  
**核心哲学**：**Gateway-First**——中心控制平面管理一切

OpenClaw 的核心架构围绕一个单一长运行的 Gateway 进程，它拥有会话、路由、工具执行和状态：

"OpenClaw 确立了模板：一个 Gateway 将来自聊天应用的消息路由到 ReAct 循环 Brain，使用基于 Markdown 的记忆和插件化技能体系。"  
—— Lushbinary 技术分析 [^38]

**核心特性：**

- **22+ 消息渠道支持**：Telegram、Discord、Slack、WhatsApp、Signal、iMessage、LINE、Feishu、Nostr、Twitch、Zalo、WeChat 等[^39]  
- **5,700+ 社区技能**：ClawHub 生态，即插即用  
- **MCP 生态整合**：大多数社区技能已成为 MCP Server 的封装器[^40]  
- **快速上手**：`npx openclaw` 即可启动，15 分钟内连接 WhatsApp[^41]

**OpenClaw 的问题：**

- **严重安全事件**：CVE-2026-30741（请求端 prompt injection 远程代码执行）；Snyk 在 ClawHub 发现 1,467 个恶意技能（91% 结合 prompt injection 与传统恶意软件）；超过 135,000 个实例以不安全默认配置在公网暴露[^42]  
- **静态技能**：OpenClaw 技能是人工编写的静态文件，不会自我改进[^43]  
- **维护疲劳**：30% 的活跃开发者已迁移到 Hermes，原因是"维护社区插件的疲劳"[^44]

"OpenClaw 把赌注押在：难题是路由和控制——谁可以到达你的代理，在什么条件下，从什么渠道，有什么权限。"  
—— Trilogy AI Center of Excellence 技术深度分析 [^45]

---

## 8\. 演进方向三：Hermes Agent — Learning-First 自进化范式

**项目来源**：NousResearch（Nous Research），2026年2月发布[^46]  
**GitHub Stars**：截至 2026 年 4 月 \~22,000（快速增长）  
**语言**：Python 3.11  
**核心哲学**：**Learning-First**——把 AI Agent 从"被操作的系统"变成"被培育的心智"

Hermes Agent 代表了与 OpenClaw 截然不同的架构哲学：

"OpenClaw 把 agent 视为**被编排的系统**（a system to be orchestrated）。Hermes 把 agent 视为**被培育的心智**（a mind to be developed）。"  
—— Medium 深度分析，2026年3月 [^47]

**核心架构——五阶段学习循环（Execute → Evaluate → Extract → Refine → Retrieve）：**

1. **执行**：完成任务  
2. **评估**：判断方法是否值得保留  
3. **提取**：将推理模式抽象为命名技能  
4. **精炼**：新结果持续更新技能质量  
5. **检索**：未来任务主动匹配历史技能

"一个使用自生成技能的代理完成复杂研究和代码执行任务的速度比全新非学习实例快 **40%**。"  
—— Nous Research 内部基准测试，2026年4月 [^48]

**Hermes 的独特能力：**

- **持久记忆**：SQLite \+ FTS5 全文检索，跨会话搜索所有历史对话[^49]  
- **用户建模**：Honcho 辩证用户建模，不需要每次会话重新指导[^50]  
- **自主技能创建**：成功任务后自动生成可复用技能，无需人工干预[^51]  
- **安全设计**：容器硬化、只读根文件系统、Tirith 执行前扫描器、文件系统检查点+回滚[^52]  
- **SOUL.md**：定义 Agent 身份与个性的核心文件[^53]

**OpenClaw vs Hermes 核心对比：**

| 维度 | OpenClaw | Hermes Agent |
| :---- | :---- | :---- |
| 核心架构 | Gateway 控制平面 | AIAgent 执行循环 |
| 技能来源 | 人工编写（社区） | 自主生成（代理自身） |
| 记忆方式 | Markdown \+ JSON | SQLite FTS5 \+ 多层记忆栈 |
| 学习能力 | 无（静态） | 持续自进化 |
| 消息渠道 | 22+ | 13 |
| 安全默认 | ⚠️ 弱（需手动加固） | ✅ 强（默认安全设计） |
| 语言 | TypeScript/Node.js | Python 3.11 |
| 部署复杂度 | 低（npx 一键启动） | 中（需要基础设施能力） |
| 迁移支持 | — | `hermes claw migrate` 自动迁移 OpenClaw 配置 |
| 适合场景 | 快速启动、多渠道集成、团队 | 长期使用、深度个性化、研究 |

"两个框架并非零和博弈——2026 年许多设置使用 Agent Communication Protocol (ACP) 让它们协同工作。"  
—— KuCoin 技术分析，2026年4月 [^54]

**MCP 与 ACP 成为基础设施标准**：

MCP（Model Context Protocol，由 Anthropic 创建，现由 Linux Foundation 治理）已成为 Agent-to-Tool 通信的事实标准。OpenClaw 将其作为资源层，Hermes 采取"MCP-First"立场。[^55]

---

## 9\. 演进方向四：Harmless AI — Constitutional AI 安全范式

**代表机构**：Anthropic  
**核心方法论**：Constitutional AI（CAI）  
**关键论文**：*Constitutional AI: Harmlessness from AI Feedback*（2022年）[^56]

当 Vibe Coding 将安全讨论推向主流时，Anthropic 的 Constitutional AI 方法论提供了一个系统性的思考框架——不是通过规则约束，而是通过**让模型内化价值观**来实现"Harmless"：

"CAI 训练可以产生帕累托改进（双赢）：Constitutional RL 在有害输入响应上既更有帮助，又更无害，优于来自人类反馈的强化学习。"  
—— Anthropic，Constitutional AI 论文 [^57]

### 9.1 四层优先级体系（2026年新宪法）

Anthropic 于 2026 年 1 月 22 日发布更新版 Claude 宪法（23,000 字，较 2023 年的 2,700 字大幅扩展），明确了四层优先级体系[^58]：

1. **Safety（安全）**：广泛支持人类对 AI 的监督与控制  
2. **Ethics（伦理）**：遵循良好的价值观和道德原则  
3. **Compliance（合规）**：遵守 Anthropic 的具体规范  
4. **Helpfulness（有用）**：在上述约束内尽可能有帮助

这一框架对 Vibe Coding 的安全问题有直接的方法论启示：安全不是"附加功能"，而是**设计优先级中位于最高层的基础约束**。

### 9.2 对 Vibe Coding 安全危机的直接回应

2026 年 2 月，Anthropic 推出 **Claude Code Security**，专门审查代码库以识别漏洞[^59]。这是对 Vibe Coding 安全危机的直接产品回应：

- Lovable 事件（1,645 个应用中 170 个暴露隐私）[^60]  
- Veracode 研究（45% AI 生成代码含安全漏洞）[^61]  
- GTG-2002 威胁行为者事件（使用 Claude Code 攻击 17 个组织）[^62]

### 9.3 Harmless AI 的更广泛含义

Harmless 不仅是"拒绝有害请求"，更是一种**系统设计哲学**，在 Vibe Coding 语境下体现为：

- **最小权限原则**：AI Agent 只获得完成当前任务所需的最小权限  
- **可解释性审计**：AI 生成的代码必须可被人类理解和审计  
- **故障安全默认**：系统崩溃时回退到安全状态，而非未知状态  
- **人类监督保留**：即使在高度自动化的 Agentic 工作流中，关键决策节点仍保留人类审批

"当面对似乎令人信服的越线论据时，Claude 应该保持坚定。一个有说服力的越线理由反而应该增加 Claude 的警觉——这通常意味着某些可疑的事情正在发生。"  
—— Claude 新宪法，Anthropic，2026年1月 [^63]

---

## 10\. 未来程序员的主要工作与核心价值

这是整个 Vibe Coding 讨论中最重要、也最少被认真回答的问题：**当 AI 能够生成大部分代码，程序员的核心价值在哪里？**

### 10.1 角色重心迁移图谱

```
传统程序员角色

├── 语法记忆与代码编写  ──────▶ \[AI 完全接管\]
├── API 调用与框架使用  ──────▶ \[AI 高效执行\]
├── 基础功能实现        ──────▶ \[AI 高效执行\]
│
├── 调试与排错          ──────▶ \[人机协作，人类主导\]
├── 架构设计            ──────▶ \[人类主导，AI 辅助\]
├── 约束建模            ──────▶ \[人类核心价值\]
├── 领域知识转化        ──────▶ \[人类核心价值\]
└── 价值判断与伦理决策  ──────▶ \[人类不可替代\]
```

### 10.2 未来程序员的五大核心工作

**① 约束工程师（Constraint Engineer）**

这是 Agentic Engineering 最核心的新技能：将对系统行为的隐性期望，转化为 AI 可以遵循的显式约束。

- 编写高质量的 Spec（规范文档）  
- 定义系统的不变量（invariants）和边界条件  
- 设计失败模式和恢复策略  
- 构建 agents.md、SKILL.md 等上下文基础设施

**② 系统架构师（System Architect）**

AI 可以快速实现代码，但不能替代对系统整体形态的设计判断：

- 接口设计与模块边界划定  
- 扩展性与可维护性的权衡决策  
- 技术栈选型与依赖管理  
- 分布式系统的一致性与可用性平衡

**③ 质量守门人（Quality Gatekeeper）**

当 AI 成为高速代码生成器，人类的核心价值在于判断输出质量：

- 安全审查与漏洞识别（AI 协作代码漏洞率是人工代码的 2.74 倍[^64]）  
- 架构合理性评估（短期可用 vs 长期可维护）  
- 测试策略设计与覆盖率决策  
- 技术债的识别、量化与管理

**④ 领域翻译官（Domain Translator）**

这是最被低估的价值来源。AI 不具备领域知识的自发应用能力——它需要人类主动引导：

"当我提起 Zipf 定律、ACT-R 技能习得模型、贝叶斯参数估计时，ChatGPT 很乐意跟随我的思路。但如果我不主动引导，AI 永远不会自己提出这些。"  
—— Scott H. Young，认知科学研究者 [^65]

这意味着：懂医疗的程序员、懂金融的程序员、懂教育的程序员，其价值将远超仅懂编程的程序员。

**⑤ 伦理与治理负责人（Ethics & Governance Owner）**

随着 AI 生成代码渗透到越来越多的关键系统，人类工程师必须承担：

- AI 生成代码的问责制（Accountability）  
- 隐私保护与数据治理合规  
- AI 偏见识别与公平性评估  
- 在监管框架下（如 EU AI Act）的合规管理

### 10.3 不会消失但会转型的技能

| 技能 | 变化方向 |
| :---- | :---- |
| 编程基础（算法、数据结构） | 从"实现"转向"评估 AI 实现质量" |
| 代码审查 | 从"人工查错"转向"AI 辅助+人类架构判断" |
| 系统设计 | 价值显著提升，成为核心竞争力 |
| 测试编写 | AI 生成测试用例，人类设计测试策略 |
| 文档写作 | 从"给人看的文档"扩展为"给 AI 看的上下文"（SKILL.md、agents.md） |

### 10.4 新增必备技能

- **Prompt Engineering（提示工程）**：精准表达意图，减少 AI 的歧义填充  
- **Context Engineering（上下文工程）**：管理 LLM 上下文窗口，维护跨会话知识  
- **Agent Orchestration（代理编排）**：设计多 Agent 协作工作流  
- **AI Output Evaluation（AI 输出评估）**：判断 AI 生成内容的质量与可靠性  
- **Security-First Mindset（安全优先思维）**：在 AI 辅助环境中保持安全第一的设计直觉

### 10.5 核心价值的本质

**程序员的不可替代价值，来自于三个层次的认知工作：**

```
第一层：知道"什么是正确的"
    → 领域知识 \+ 业务理解 → AI 没有    

第二层：知道"如何判断好坏"  
    → 架构直觉 \+ 质量标准 → AI 难以独立建立    

第三层：知道"为什么这样做"
    → 价值判断 \+ 伦理约束 → AI 需要人类赋予
```

这三个层次的认知工作，构成了 Agentic Engineering 时代程序员真正的核心价值。**编程技能从"与机器沟通的能力"演进为"定义正确性的能力"。**

---

## 11\. 对开发者、团队和组织的建设性建议

### 11.1 个人开发者：建立"三区分离"工作法

| 区域 | 使用方式 | 原则 |
| :---- | :---- | :---- |
| **探索区（纯 Vibe）** | 个人脚本、想法验证、Demo 原型 | 完全拥抱 Vibe，快速出结果，用完即弃 |
| **过渡区（审查辅助）** | 内部工具、MVPs、个人项目 | AI 生成但必须理解关键路径；用 AI 生成测试用例 |
| **生产区（Agentic Engineering）** | 生产系统、核心功能 | 强 Spec 先行，严格审查，安全扫描，架构负责 |

**Andrew Ng 的告诫值得铭记**：一定要学编程基础。不是因为 AI 无法写代码，而是因为你需要基础才能判断 AI 在说什么、设定正确约束、在 AI 走弯路时纠正方向。引导 AI 是深度的脑力活动，基础越扎实，引导越精准。[^66]

### 11.2 工程团队：AI 使用分级策略

| 代码类型 | AI 使用级别 | 强制措施 |
| :---- | :---- | :---- |
| 认证/授权/支付 | 🔴 高度受限 | 安全审计 \+ 渗透测试 \+ 双人审查 |
| 数据访问/API 接口 | 🟡 受限使用 | 安全扫描 \+ 合规检查 \+ 测试覆盖率要求 |
| 业务逻辑 | 🔵 标准流程 | 常规代码审查 \+ 单元测试 |
| UI 组件/样式 | ✅ 自由使用 | 视觉验收测试 |
| 配置/脚手架/测试 | ✅ 推荐使用 | 基本审查 |

同时，建立团队范围内的**上下文基础设施**：高质量的 README、架构决策记录（ADRs）、代码风格规范——这些不只是给人类工程师的文档，更是为 AI 代理提供"上下文基准"的核心资产。

### 11.3 技术组织：五项结构性建议

1. **不要断掉初级工程师的成长通道**：把 AI 导向的"快速交付"任务保留给有经验者，把需要深度理解的"慢速探索"任务分配给初级工程师，这才是可持续的人才梯队建设。  
     
2. **建立 AI 代码问责制**：谁提的 prompt，谁负责。AI 是工具不是作者，commit 的工程师对代码质量全权负责，不允许以"AI 生成"为由推卸责任。  
     
3. **投资上下文工程能力**：这是 2026 年核心竞争力。帮助团队掌握 agents.md、有效 Spec 写作、多代理协作编排等新型工程技能。  
     
4. **安全前置，不能后补**：在 AI 编码工具工作流中嵌入自动化安全扫描（SAST/DAST），不能依赖开发者手动识别 AI 引入的漏洞。  
     
5. **跟踪真实生产力，抵抗感知偏差**：METR 实验证明——自我感觉快了 20%，实际慢了 19%。用数据度量 AI 工具的真实 ROI，而不是主观印象。[^67]

---

## 12\. 个人思考：编程的本质是否变了？

在深度构建 AI Agent 基础设施的过程中（[SkillNexus](https://github.com/skyseraph/SkillNexus)、EvalClaw等系统），我对这个问题有了自己的答案：**编程的语法变了，但编程的本质没有变。**

编程的本质，从来不是"用某种语法指挥机器"，而是**问题分解与约束建模**——把人类世界中模糊的需求，转化为机器可以确定性执行的逻辑。这个转化过程需要的不是打字速度，而是认知精度。

Vibe Coding 做了什么？它把"认知精度→代码"这一步的摩擦大幅降低了。但认知精度本身——对问题的深刻理解——它没有降低，也无法降低。

**Vibe Coding 最大的陷阱，不是它会生成糟糕的代码，而是它让你产生一种错觉：你已经思考清楚了——因为你"发布"了。** 但那些你没有语言描述的隐性期望，AI 会默默地用它认为合理的方式填充。

因此，我认为真正需要建立的新技能不是"如何使用 AI 工具"，而是**显式化隐性知识的能力**——把你对系统行为的隐性期望，转化为 AI 可以遵循的显性约束。这就是为什么 Spec-first 开发、SKILL.md 方法论、Harness 会成为下一阶段的核心竞争力：它们本质上都是在练习把认知显式化的肌肉。

对于 Karpathy 的"Agentic Engineering"，我想补充一点：这个演进不只是关于"更多监督"，而是关于**人类工程师角色的重心迁移**——从"代码实现者"迁移到"系统架构者与约束提供者"。这不是技能的退化，而是一种升维。

那些能够清晰定义问题边界、设计约束系统、判断 AI 输出质量的工程师，将在这个时代获得远超以往的杠杆效应。而那些把 Vibe Coding 理解为"我不需要懂编程了"的人，将很快遭遇他们自己创造的"vibe hangover"。

**一句话总结**：Vibe Coding 不是编程的终结，而是对"谁真正在思考"这件事的终极考验。AI 正在把代码的生产成本压向零，但把系统设计与约束建模的价值推向新高。工具越好，设计师的价值越凸显。

---

## 13\. 参考来源

---

*by SkySeraph as AI 2026.4*  

[Vibe Coding 深度观察：一场关于编程本质的世纪之争](https://mp.weixin.qq.com/s/ZDF70r7VyuzSszfAz8qpdQ)

*文章最后更新：2026年4月23日*  
*欢迎引用，转载请注明出处：SkySeraph · AI Agent Infrastructure*  


[^1]: Andrej Karpathy，X（Twitter），2025年2月6日。原推文：[https://x.com/karpathy/status/1886192184808149383](https://x.com/karpathy/status/1886192184808149383)

[^2]: Wikipedia，"Vibe coding"词条，2026年4月（持续更新）。[https://en.wikipedia.org/wiki/Vibe\_coding](https://en.wikipedia.org/wiki/Vibe_coding)

[^3]: Technology Magazine，"Vibe-Coding: The Future of Code or Just a 'Short-Term Con'?"，2025年11月。[https://technologymagazine.com/news/vibe-coding-the-future-of-code-or-just-a-short-term-con](https://technologymagazine.com/news/vibe-coding-the-future-of-code-or-just-a-short-term-con)

[^4]: The New Stack，"Vibe Coding is Passé. Karpathy Has a New Name for the Future of Software."，2026年2月。[https://thenewstack.io/vibe-coding-is-passe/](https://thenewstack.io/vibe-coding-is-passe/)

[^5]: Andrej Karpathy，X（Twitter），2025年2月6日。原推文：[https://x.com/karpathy/status/1886192184808149383](https://x.com/karpathy/status/1886192184808149383)

[^6]: TATEEDA | GLOBAL，"Vibe Coding vs. Engineering: A 2026 Guide"，2026年1月。[https://tateeda.com/blog/vibe-coding-vs-professional-engineering](https://tateeda.com/blog/vibe-coding-vs-professional-engineering)

[^7]: TATEEDA | GLOBAL，"Vibe Coding vs. Engineering: A 2026 Guide"，2026年1月。[https://tateeda.com/blog/vibe-coding-vs-professional-engineering](https://tateeda.com/blog/vibe-coding-vs-professional-engineering)

[^8]: TATEEDA | GLOBAL，"Vibe Coding vs. Engineering: A 2026 Guide"，2026年1月。[https://tateeda.com/blog/vibe-coding-vs-professional-engineering](https://tateeda.com/blog/vibe-coding-vs-professional-engineering)

[^9]: Product Hunt，"The State of Vibe Coding 2025 \- Key Takeaways"（引用 v0 by Vercel 报告）。[https://www.producthunt.com/p/vibecoding/the-state-of-vibe-coding-2025-key-takeaways](https://www.producthunt.com/p/vibecoding/the-state-of-vibe-coding-2025-key-takeaways)

[^10]: Wikipedia，"Vibe coding"词条，2026年4月（持续更新）。[https://en.wikipedia.org/wiki/Vibe\_coding](https://en.wikipedia.org/wiki/Vibe_coding)

[^11]: CodeRabbit，开源 GitHub PR 分析报告，2025年12月（分析 470 个 PR）。引自 Wikipedia Vibe coding 词条。

[^12]: byteiota，"Vibe Coding Backlash: When the Hype Meets Reality"，2025年11月。[https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/](https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/)

[^13]: byteiota，"Vibe Coding Backlash: When the Hype Meets Reality"，2025年11月。[https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/](https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/)

[^14]: METR，开发者生产力随机对照实验，2025年7月。引自 Wikipedia Vibe coding 词条。

[^15]: byteiota，"Vibe Coding Backlash: When the Hype Meets Reality"，2025年11月。[https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/](https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/)

[^16]: Andrej Karpathy，X（Twitter），2025年2月6日。原推文：[https://x.com/karpathy/status/1886192184808149383](https://x.com/karpathy/status/1886192184808149383)

[^17]: Wikipedia，"Vibe coding"词条，2026年4月（持续更新）。[https://en.wikipedia.org/wiki/Vibe\_coding](https://en.wikipedia.org/wiki/Vibe_coding)

[^18]: byteiota，"Vibe Coding Backlash: When the Hype Meets Reality"，2025年11月。[https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/](https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/)

[^19]: Klover.ai，"Andrew Ng Pushes Back on AI 'Vibe Coding'"（引用 LangChain Interrupt 会议，2025年5月）。[https://www.klover.ai/andrew-ng-pushes-back-ai-vibe-coding-hard-work-not-hype/](https://www.klover.ai/andrew-ng-pushes-back-ai-vibe-coding-hard-work-not-hype/)

[^20]: Klover.ai，"Andrew Ng Pushes Back on AI 'Vibe Coding'"（引用 LangChain Interrupt 会议，2025年5月）。[https://www.klover.ai/andrew-ng-pushes-back-ai-vibe-coding-hard-work-not-hype/](https://www.klover.ai/andrew-ng-pushes-back-ai-vibe-coding-hard-work-not-hype/)

[^21]: Simon Willison，"Not all AI-assisted programming is vibe coding (but vibe coding rocks)"，simonwillison.net，2025年3月19日。[https://simonwillison.net/2025/Mar/19/vibe-coding/](https://simonwillison.net/2025/Mar/19/vibe-coding/)

[^22]: Wikipedia，"Vibe coding"词条，2026年4月（持续更新）。[https://en.wikipedia.org/wiki/Vibe\_coding](https://en.wikipedia.org/wiki/Vibe_coding)

[^23]: Technology Magazine，"Vibe-Coding: The Future of Code or Just a 'Short-Term Con'?"，2025年11月。[https://technologymagazine.com/news/vibe-coding-the-future-of-code-or-just-a-short-term-con](https://technologymagazine.com/news/vibe-coding-the-future-of-code-or-just-a-short-term-con)

[^24]: The New Stack，"Vibe Coding is Passé. Karpathy Has a New Name for the Future of Software."，2026年2月。[https://thenewstack.io/vibe-coding-is-passe/](https://thenewstack.io/vibe-coding-is-passe/)

[^25]: MIT Technology Review / Thoughtworks，"From Vibe Coding to Context Engineering: 2025 in Software Development"，2025年11月。[https://www.technologyreview.com/2025/11/05/1127477/from-vibe-coding-to-context-engineering-2025-in-software-development/](https://www.technologyreview.com/2025/11/05/1127477/from-vibe-coding-to-context-engineering-2025-in-software-development/)

[^26]: Scott H. Young，"Is Vibe Coding the Future of Skilled Work?"，scotthyoung.com，2025年11月。[https://www.scotthyoung.com/blog/2025/11/12/vibe-coding-future-work/](https://www.scotthyoung.com/blog/2025/11/12/vibe-coding-future-work/)

[^27]: byteiota，"Vibe Coding Backlash: When the Hype Meets Reality"，2025年11月。[https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/](https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/)

[^28]: Simon Willison，"Not all AI-assisted programming is vibe coding (but vibe coding rocks)"，simonwillison.net，2025年3月19日。[https://simonwillison.net/2025/Mar/19/vibe-coding/](https://simonwillison.net/2025/Mar/19/vibe-coding/)

[^29]: Product Hunt，"The State of Vibe Coding 2025 \- Key Takeaways"（引用 v0 by Vercel 报告）。[https://www.producthunt.com/p/vibecoding/the-state-of-vibe-coding-2025-key-takeaways](https://www.producthunt.com/p/vibecoding/the-state-of-vibe-coding-2025-key-takeaways)

[^30]: The Vibe Coding Revolution，futuristspeaker.com，2025年9月。[https://futuristspeaker.com/technology-trends/the-vibe-coding-revolution/](https://futuristspeaker.com/technology-trends/the-vibe-coding-revolution/)

[^31]: Wikipedia，"Vibe coding"词条，2026年4月（持续更新）。[https://en.wikipedia.org/wiki/Vibe\_coding](https://en.wikipedia.org/wiki/Vibe_coding)

[^32]: CodeRabbit，开源 GitHub PR 分析报告，2025年12月（分析 470 个 PR）。引自 Wikipedia Vibe coding 词条。

[^33]: Technology Magazine，"Vibe-Coding: The Future of Code or Just a 'Short-Term Con'?"，2025年11月。[https://technologymagazine.com/news/vibe-coding-the-future-of-code-or-just-a-short-term-con](https://technologymagazine.com/news/vibe-coding-the-future-of-code-or-just-a-short-term-con)

[^34]: The New Stack，"Vibe Coding is Passé. Karpathy Has a New Name for the Future of Software."，2026年2月。[https://thenewstack.io/vibe-coding-is-passe/](https://thenewstack.io/vibe-coding-is-passe/)

[^35]: MIT Technology Review / Thoughtworks，"From Vibe Coding to Context Engineering: 2025 in Software Development"，2025年11月。[https://www.technologyreview.com/2025/11/05/1127477/from-vibe-coding-to-context-engineering-2025-in-software-development/](https://www.technologyreview.com/2025/11/05/1127477/from-vibe-coding-to-context-engineering-2025-in-software-development/)

[^36]: The New Stack，"OpenClaw vs. Hermes Agent: The Race to Build AI Assistants That Never Forget"，2026年3月。[https://thenewstack.io/persistent-ai-agents-compared/](https://thenewstack.io/persistent-ai-agents-compared/)

[^37]: KuCoin，"Hermes Agent vs OpenClaw: Which Open-Source AI Agent Wins in 2026?"，2026年4月。[https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026](https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026)

[^38]: Lushbinary，"Hermes Agent vs OpenClaw: Key Differences & Comparison"，2026年4月。[https://lushbinary.com/blog/hermes-vs-openclaw-key-differences-comparison/](https://lushbinary.com/blog/hermes-vs-openclaw-key-differences-comparison/)

[^39]: Trilogy AI Center of Excellence，"Technical Deep Dive: Hermes vs. OpenClaw"，2026年3月。[https://trilogyai.substack.com/p/technical-deep-dive-hermes-vs-openclaw](https://trilogyai.substack.com/p/technical-deep-dive-hermes-vs-openclaw)

[^40]: KuCoin，"Hermes Agent vs OpenClaw: Which Open-Source AI Agent Wins in 2026?"，2026年4月。[https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026](https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026)

[^41]: NxCode，"Hermes Agent vs OpenClaw 2026: Which AI Agent Should You Choose?"，2026年4月。[https://www.nxcode.io/resources/news/hermes-agent-vs-openclaw-2026-which-ai-agent-to-choose](https://www.nxcode.io/resources/news/hermes-agent-vs-openclaw-2026-which-ai-agent-to-choose)

[^42]: Lushbinary，"Hermes Agent vs OpenClaw: Key Differences & Comparison"，2026年4月。[https://lushbinary.com/blog/hermes-vs-openclaw-key-differences-comparison/](https://lushbinary.com/blog/hermes-vs-openclaw-key-differences-comparison/)

[^43]: Medium / Yin & Yang，"The Quiet Shift in AI Agents: Why Hermes Is Gaining Ground Beyond OpenClaw"，2026年3月。[https://medium.com/@kunwarmahen/the-quiet-shift-in-ai-agents-why-hermes-is-gaining-ground-beyond-openclaw-6364df765d3a](https://medium.com/@kunwarmahen/the-quiet-shift-in-ai-agents-why-hermes-is-gaining-ground-beyond-openclaw-6364df765d3a)

[^44]: KuCoin，"Hermes Agent vs OpenClaw: Which Open-Source AI Agent Wins in 2026?"，2026年4月。[https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026](https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026)

[^45]: Trilogy AI Center of Excellence，"Technical Deep Dive: Hermes vs. OpenClaw"，2026年3月。[https://trilogyai.substack.com/p/technical-deep-dive-hermes-vs-openclaw](https://trilogyai.substack.com/p/technical-deep-dive-hermes-vs-openclaw)

[^46]: GitHub，NousResearch/hermes-agent，README。[https://github.com/nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent)

[^47]: Medium / Yin & Yang，"The Quiet Shift in AI Agents: Why Hermes Is Gaining Ground Beyond OpenClaw"，2026年3月。[https://medium.com/@kunwarmahen/the-quiet-shift-in-ai-agents-why-hermes-is-gaining-ground-beyond-openclaw-6364df765d3a](https://medium.com/@kunwarmahen/the-quiet-shift-in-ai-agents-why-hermes-is-gaining-ground-beyond-openclaw-6364df765d3a)

[^48]: KuCoin，"Hermes Agent vs OpenClaw: Which Open-Source AI Agent Wins in 2026?"，2026年4月。[https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026](https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026)

[^49]: GitHub，NousResearch/hermes-agent，README。[https://github.com/nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent)

[^50]: MindStudio，"What Is Hermes Agent? The OpenClaw Alternative with a Built-In Learning Loop"，2026年3月。[https://www.mindstudio.ai/blog/what-is-hermes-agent-openclaw-alternative](https://www.mindstudio.ai/blog/what-is-hermes-agent-openclaw-alternative)

[^51]: GitHub，NousResearch/hermes-agent，README。[https://github.com/nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent)

[^52]: The New Stack，"OpenClaw vs. Hermes Agent: The Race to Build AI Assistants That Never Forget"，2026年3月。[https://thenewstack.io/persistent-ai-agents-compared/](https://thenewstack.io/persistent-ai-agents-compared/)

[^53]: MindStudio，"What Is Hermes Agent? The OpenClaw Alternative with a Built-In Learning Loop"，2026年3月。[https://www.mindstudio.ai/blog/what-is-hermes-agent-openclaw-alternative](https://www.mindstudio.ai/blog/what-is-hermes-agent-openclaw-alternative)

[^54]: KuCoin，"Hermes Agent vs OpenClaw: Which Open-Source AI Agent Wins in 2026?"，2026年4月。[https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026](https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026)

[^55]: KuCoin，"Hermes Agent vs OpenClaw: Which Open-Source AI Agent Wins in 2026?"，2026年4月。[https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026](https://www.kucoin.com/blog/hermes-agent-vs-openclaw-which-open-source-ai-agent-wins-in-2026)

[^56]: Anthropic，"Constitutional AI: Harmlessness from AI Feedback"，研究论文，2022年。[https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)

[^57]: Anthropic，"Constitutional AI: Harmlessness from AI Feedback"，研究论文，2022年。[https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)

[^58]: Anthropic，"Claude's New Constitution"，2026年1月22日。[https://www.anthropic.com/news/claude-new-constitution](https://www.anthropic.com/news/claude-new-constitution)

[^59]: Wikipedia，"Claude (language model)"词条，2026年4月。[https://en.wikipedia.org/wiki/Claude\_(language\_model)](https://en.wikipedia.org/wiki/Claude_\(language_model\))

[^60]: Wikipedia，"Vibe coding"词条，2026年4月（持续更新）。[https://en.wikipedia.org/wiki/Vibe\_coding](https://en.wikipedia.org/wiki/Vibe_coding)

[^61]: byteiota，"Vibe Coding Backlash: When the Hype Meets Reality"，2025年11月。[https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/](https://byteiota.com/vibe-coding-backlash-when-the-hype-meets-reality/)

[^62]: Wikipedia，"Claude (language model)"词条，2026年4月。[https://en.wikipedia.org/wiki/Claude\_(language\_model)](https://en.wikipedia.org/wiki/Claude_\(language_model\))

[^63]: Anthropic，"Claude's New Constitution"，2026年1月22日。[https://www.anthropic.com/news/claude-new-constitution](https://www.anthropic.com/news/claude-new-constitution)

[^64]: CodeRabbit，开源 GitHub PR 分析报告，2025年12月（分析 470 个 PR）。引自 Wikipedia Vibe coding 词条。

[^65]: Scott H. Young，"Is Vibe Coding the Future of Skilled Work?"，scotthyoung.com，2025年11月。[https://www.scotthyoung.com/blog/2025/11/12/vibe-coding-future-work/](https://www.scotthyoung.com/blog/2025/11/12/vibe-coding-future-work/)

[^66]: Klover.ai，"Andrew Ng Pushes Back on AI 'Vibe Coding'"（引用 LangChain Interrupt 会议，2025年5月）。[https://www.klover.ai/andrew-ng-pushes-back-ai-vibe-coding-hard-work-not-hype/](https://www.klover.ai/andrew-ng-pushes-back-ai-vibe-coding-hard-work-not-hype/)

[^67]: METR，开发者生产力随机对照实验，2025年7月。引自 Wikipedia Vibe coding 词条