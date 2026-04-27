---
title: "LLM时代下的软件范式迁移：从 Prompt Engineering 到 Harness Engineering"
date: 2026-04-26T22:41:30+08:00
categories: ["技术"]   # 技术 / 随笔 / 项目
tags: ["LLM"]
pin: false
toc: false
draft: false
---


> 作者：skyseraph   
> 日期：2026-04-26   
> 原始链接：[llm_soft_lifecycle](https://skyseraph.github.io/posts/2026/llm_soft_lifecycle)    
> 本文汇集业界主流 AI 公司实践、领域大咖公开观点与个人思考，所有引用均注明来源

---

## 目录

1. [宏观判断：软件正在发生根本性变化](#1-宏观判断软件正在发生根本性变化)  
2. [三代范式演进：从 Software 1.0 到 Software 3.0](#2-三代范式演进从-software-10-到-software-30)  
3. [LLM 即操作系统：Karpathy 的计算机科学视角](#3-llm-即操作系统karpathy-的计算机科学视角)  
4. [第一层：Prompt Engineering — 咒语时代的终结](#4-第一层prompt-engineering--咒语时代的终结)  
5. [第二层：Context Engineering — 系统设计的崛起](#5-第二层context-engineering--系统设计的崛起)  
6. [第三层：Harness Engineering — 基础设施时代](#6-第三层harness-engineering--基础设施时代)  
7. [主流 AI 公司的范式实践](#7-主流-ai-公司的范式实践)  
8. [大咖观点汇总](#8-大咖观点汇总)  
9. [个人深度思考：范式迁移的底层逻辑](#9-个人深度思考范式迁移的底层逻辑)  
10. [建设性建议：如何在范式迁移中站稳脚跟](#10-建设性建议如何在范式迁移中站稳脚跟)  
11. [结语：我们身处哪个时刻？](#11-结语我们身处哪个时刻)

---

## 1\. 宏观判断：软件正在发生根本性变化

2025—2026年，一个清晰的信号在产业界不断扩大：软件的生产方式、运行方式、甚至定义方式，都正在经历一次根本性的重写。这不是渐进式的工具升级，而是类比 PC 革命、互联网革命量级的范式迁移。

Anthropic CEO **Dario Amodei** 在 2026 年初多次公开表示，他在 Anthropic 内部的工程师已经基本不再手写代码——"I have engineers within Anthropic who say, 'I don't write any code anymore. I just let the model write the code. I edit it. I do the things around it.'" 他进一步预测，AI 将在 6 至 12 个月内完成软件工程师所做的全部工作。^\[Yahoo Finance, *Anthropic CEO Predicts AI Models Will Replace Software Engineers In 6-12 Months*, 2026-01\]

OpenAI CEO **Sam Altman** 则从组织论的角度描述这个未来：一个人将可以指挥等效于一万人的认知劳动力，做到过去需要庞大组织才能完成的事情。^\[Sam Altman on X / OpenAI Blog, 2025\]

Andrej **Karpathy** 在其 2025 年度总结中给出了更系统的框架：他认为 LLM 是继 1970-80 年代个人计算机之后"下一个主要计算范式"，而目前人类开发出的，还不到这个新范式全部潜力的 10%。^\[Andrej Karpathy, *2025 LLM Year in Review*, karpathy.bearblog.dev, 2025-12\]

这三句话，从微观操作层、组织层、计算范式层，共同描绘了同一个现实：**我们正在从"人写代码让机器执行"，过渡到"人描述意图，AI 生成并执行代码"**。

---

## 2\. 三代范式演进：从 Software 1.0 到 Software 3.0

Karpathy 提出了一个被广泛引用的软件演进三层框架。^\[Karpathy, AI Startup School Talk, YCombinator, 2025-06\]

### Software 1.0：命令式逻辑时代

传统编程。程序员用 C++、Java、Python 等命令式语言，一行一行地将逻辑写入机器。可解释、可审计、可确定性执行。这是工业软件的黄金时代。

### Software 2.0：神经网络时代

以深度学习为核心，程序不再被"写出来"，而是被"训练出来"。参数是权重，行为从数据中涌现。Tesla 用神经网络替换了整个 C++ 自动驾驶栈中大量模块，是这一范式的代表性案例。它的问题是：不透明、不可解释、部署困难。

### Software 3.0：LLM 时代

**LLM 被英语编程**。"英语是新的编程语言"——Karpathy 在 AI Startup School 演讲中明确表示："LLMs are a new kind of computer, and you program them *in English*."^\[ibid.\] 软件的表达层从符号逻辑、矩阵权重，跃迁为自然语言意图。

这一范式的关键特征是：**程序 \= 意图描述 \+ 上下文信息 \+ 执行环境**。而配合执行这一程序的"运行时"，就是 LLM 及其外部封装。

---

## 3\. LLM 即操作系统：Karpathy 的计算机科学视角

Karpathy 在 2023 年的一条推文中，最早系统性地提出了"LLM 即操作系统"的隐喻，并在此后不断深化：

"LLMs orchestrate: Input & Output across modalities (text, audio, vision), Code interpreter, Browser/internet access, Embeddings database for files and internal memory storage & retrieval. TLDR looking at LLMs as chatbots is the same as looking at early computers as calculators."^\[Karpathy on X, @karpathy, 2023-09-19\]

这个框架在 2025—2026 年已成为行业主流认知：

- **LLM \= CPU**：核心推理单元，无状态的 token 预测器  
- **Context Window \= RAM**：工作记忆，有限且宝贵  
- **Agent Harness \= OS**：管理 I/O、内存调度、工具分发、安全策略

这一比喻极具解释力：就像操作系统不是计算机本身，但决定了计算机能做什么；Harness 也不是 LLM 本身，但决定了 AI Agent 能做什么。

"We are moving toward a future where the LLM is simply the CPU, the context window is the RAM, and the Agent Harness is the Operating System that manages I/O, memory, and scheduling."^\[Adnan Masood, *Agent Harness Engineering — The Rise of the AI Control Plane*, Medium, 2026-04\]

当前的 AI 应用层竞争格局，也呼应了这个 OS 比喻：GPT、Claude、Gemini、Llama 之于 LLM OS 领域，正如 Windows、macOS、Linux 之于传统 OS。^\[Karpathy on X, 2023\]

---

## 4\. 第一层：Prompt Engineering — 咒语时代的终结

### 什么是 Prompt Engineering？

Prompt Engineering 是 AI 应用的第一个工程时代：通过精心设计输入文本，引导 LLM 产出预期输出。它的核心问题是："**我应该怎么说？**"（How should I phrase this?）

技术套路包括：zero-shot / few-shot prompt、chain-of-thought（思维链）、角色扮演（"你是一位资深工程师"）、格式约束、负向示例等。

### Prompt Engineering 的黄金时代

2022—2024 年，Prompt Engineering 曾是 AI 应用工程师最核心的差异化能力。对于单次分类、文本摘要、翻译、信息抽取等**自包含任务**，一个精心设计的 prompt 加上一两个 few-shot 样例，往往就能获得很好的结果。^\[Neo4j Blog, *Why AI Teams Are Moving From Prompt Engineering to Context Engineering*, 2026-01\]

### Prompt Engineering 的本质局限

然而，随着 AI 系统复杂度提升，Prompt Engineering 的天花板开始显现：

**1\. 它是静态的。** Prompt 是一个固定字符串。一旦环境变化（用户换了、数据更新了、工具变了），prompt 要重新写。

**2\. 它不解决"知道什么"。** 精妙的措辞无法弥补模型不知道某件事的根本问题。没有用户偏好数据，再好的 prompt 也无法输出个性化推荐。

**3\. 它在 Agent 场景中失效。** 当 LLM 需要多轮执行、调用工具、处理中间结果时，Prompt Engineering 的"一次输入、一次输出"假设已经完全不适用。

"Prompt engineering gets you the first good output. Context engineering is how we scale."^\[Mehul Gupta, *Context Engineering vs Prompt Engineering*, Medium, 2025-06\]

Gartner 在 2025 年中期旗帜鲜明地宣告："Context engineering is in, and prompt engineering is out."^\[Gartner Research, 2025-07，转引自 IntuitionLabs.ai\]

---

## 5\. 第二层：Context Engineering — 系统设计的崛起

### 概念的诞生

"Context Engineering" 这一术语在 2025 年 6 月正式引爆。Shopify CEO **Tobi Lütke** 在推文中率先将其定义为：

"Context engineering is the art of providing all the context for the task to be plausibly solvable by the LLM."^\[Tobi Lütke on X, 2025-06-18\]

随即，**Andrej Karpathy** 为这个概念赋予了更技术性的表述：

"Context engineering is the delicate art and science of filling the context window with just the right information for the next step."^\[Andrej Karpathy on X，引用自 Firecrawl Blog, 2026-02\]

**Anthropic** 则将其正式化为技术文档：

"Context engineering refers to the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts."^\[Anthropic Engineering Blog, *Effective Context Engineering for AI Agents*\]

### Context Engineering 的核心问题

Context Engineering 的核心问题是：**"现在应该给模型看什么信息？"**（What information does the model need access to right now?）

它不再把 prompt 视为终点，而是把整个"填充上下文窗口的系统"视为工程对象。填充上下文窗口的，不只是 prompt 指令，还包括：

- **系统提示（System Prompt）**：角色定义、规则约束  
- **工具定义（Tool Definitions）**：可调用的函数和 API  
- **检索内容（Retrieved Context via RAG）**：向量检索、知识图谱  
- **会话历史（Message History）**：多轮对话记录  
- **工具执行结果（Tool Call Results）**：中间推理产物  
- **用户状态（User State / Memory）**：跨会话记忆

### Context Rot：最关键的工程约束

**Context Rot（上下文腐烂）** 是 Context Engineering 的核心命题。Stanford "Lost in the Middle" 系列研究证明：当关键信息被放置在长上下文的中间位置时，LLM 性能会显著下降。^\[引用自 Firecrawl Blog, 2026-02\] Databricks 研究发现，LLM 准确率在 32K tokens 附近便开始明显下滑，远早于百万 token 上下文窗口的物理极限。

Anthropic 工程团队的 Chroma Research 研究（2025 年 7 月，测试 18 个 LLM，包括 Claude 4、GPT-4.1、Gemini 2.5、Qwen3）发现：即使是在极简单的任务（如复现一段重复词序列）中，随着输入长度增长，模型准确率也会严重下滑。^\[Firecrawl Blog, 引用 Chroma Research 2025-07\]

Context 腐烂有四种具体表现形式：

1. **Poisoning（污染）**：错误信息污染推理链  
2. **Distraction（干扰）**：无关内容分散注意力  
3. **Confusion（混淆）**：矛盾信息导致模型困惑  
4. **Clash（冲突）**：不同来源的信息相互抵触

这意味着：**Context 是有限的且具有递减边际效应的资源**，工程师必须像管理 CPU 缓存一样管理它。

### Context Engineering 的关键设计原则

**1\. 最小必要信息原则（Minimal Signal Tokens）**  
"Not all information. The minimal set of high-signal tokens."^\[Firecrawl Blog, 2026-02\] 应该删除所有与当前推理步骤无关的 token。

**2\. 位置敏感性（Position Matters）**  
静态的决策上下文（System Prompt、规则）放在 Context 开头，利用 Prefix Cache；动态运行时信息（工具结果、当前任务）放在末尾，利用 Recency Bias。这一结构可节省高达 90% 的 token 成本。^\[ibid.\]

**3\. 动态装配而非静态预载（Just-in-Time Assembly）**  
Context 不是一个静态模板，而是一个在每次 LLM 调用前动态运行的系统的输出。维护轻量级指针（文件路径、查询语句），在运行时按需加载。这镜像了人类认知中的"检索而非背诵"机制。

**4\. 层次化记忆管理（Memory Hierarchy）**  
类比操作系统的内存层次（寄存器 → L1/L2 Cache → RAM → 磁盘），建立 AI 的记忆层次：Working Memory（当前上下文）→ Session Memory（会话记录）→ Semantic Memory（向量检索）→ Episodic Memory（结构化事件存储）。

### 一个关键的类比重申

"As an operating system curates what fits into a CPU's RAM, context engineering plays a similar role – deciding which pieces of information get loaded into an LLM's limited attention window."^\[IntuitionLabs.ai, 引用实践者观点, 2026\]

Prompt Engineering 是 Context Engineering 的一个子集，而非竞争关系。^\[Mehul Gupta, Medium, 2025-06\] Prompt 是上下文窗口内部的那一小段指令；而 Context Engineering 决定了那个窗口里究竟装了什么。

---

## 6\. 第三层：Harness Engineering — 基础设施时代

### 定义的清晰化

如果说 Context Engineering 解决了"向模型提供什么信息"，那么 **Harness Engineering** 则解决了"整个 AI 系统如何在生产环境中可靠运行"。

"Agent \= Model \+ Harness. The harness is everything that isn't the model."^\[LangChain, 转引自 DecodingAI.com\]

来自 Thoughtworks 的 Distinguished Engineer Birgitta Böckeler 给出了最早的系统性定义：Harness 是"除模型本身以外的一切"——系统提示、编排逻辑、工具调用、测试验证、反馈控制、安全约束……^\[Birgitta Böckeler, *Harness Engineering for Coding Agent Users*, martinfowler.com, 2026-04\]

Adnan Masood 的定义更为精炼：

"Agent Harness: The non-model runtime software infrastructure that wraps a large language model's (LLM) core reasoning loop to continuously coordinate tool dispatch, context management, safety enforcement, and session persistence. It functions as the operating system around the model's reasoning engine, turning raw capabilities into dependable, repeatable actions."^\[Adnan Masood, *Agent Harness Engineering*, Medium, 2026-04\]

**三层工程栈的关系**：

```
Harness Engineering  ← 全局基础设施（包含以下两层）

  └── Context Engineering  ← 信息管理（包含以下一层）

        └── Prompt Engineering  ← 指令撰写
```

"Prompt engineering crafts the instructions. Context engineering dictates what goes into the context window and when. Harness engineering is the full application and infrastructure."^\[DecodingAI.com, *Agentic Harness Engineering: LLMs as the New OS*, 2026-04\]

### Harness 的核心架构组件

根据 2026 年 4 月 Anthropic npm 包意外泄露事件揭示的 Claude Code 源码结构^\[IDC Community, *The 3rd Generation of Agents: How "Harness Engineering" Changed Games Again*\]，以及学术界的系统整理（Preprints.org 的 Agent Harness Survey, 2026-04），现代 Agent Harness 通常包含以下五层：

**Layer 1：执行循环（Execution Loop）**  
控制 Agent 的 Think → Act → Observe 循环，管理 token 预算，处理停止条件、超时、重试。

**Layer 2：工具层（Tool Layer）**  
管理工具注册、参数验证、执行代理（沙箱/容器）、结果格式化。MCP（Model Context Protocol）协议在此层标准化了工具接入方式。

**Layer 3：记忆与上下文层（Memory & Context Layer）**  
实现多级记忆系统，处理 Context Rot，执行上下文压缩（Context Compaction）。长视野任务中，Anthropic Claude Code 使用的 "Ralph Loop" 模式：当 Agent 因上下文焦虑（Context Anxiety）试图提前退出时，Harness 将原始意图重注入一个压缩后的干净上下文窗口，保证长视野连续性。^\[Masood, ibid.\]

**Layer 4：安全与治理层（Safety & Governance Layer）**  
拦截危险操作（文件删除、资金转移），执行权限策略（RBAC），审计日志。Harness 是比模型权重更灵活的安全实施点。

**Layer 5：可观测性层（Observability Layer）**  
轨迹记录、Token 消耗追踪、成功率监控、失败模式分析。这是闭环优化和 Data Flywheel 的基础。

### Harness Engineering 的产业证据

**数据是最有力的论据：**

- TerminalBench 2.0 实验表明，仅仅修改 Harness（不换模型），可以让某个 Agent 从排名 30 名开外跃升至前 5。^\[DecodingAI.com, 2026-04\]  
- 通过 Prefix Stability 和语义路由等 Harness 级别优化，Token 成本可从 $3.00/MTok 降至 $0.30/MTok，同时实现 4 倍延迟降低——**无需换模型**。^\[Masood, ibid.\]  
- ICML 2025 论文"General Modular Harness for LLM Agents in Multi-Turn Gaming Environments"证明，带 Harness 的模型在所有测试游戏中均优于无 Harness 的同款模型。^\[Parallel.ai Blog, *What is an Agent Harness*\]  
- **OpenAI 最直接的内部案例**（见下节）：一个三人团队通过 Harness Engineering，用 5 个月完成了约 100 万行代码的仓库构建，平均每工程师每天 3.5 个 PR。^\[OpenAI, *Harness Engineering: Leveraging Codex in an Agent-First World*, 2026-02\]

"The problem is that academic research has not caught up. While the model layer has attracted thousands of papers, the harness layer has attracted almost none… The result is a field that understands the engine well and the chassis barely at all."^\[Preprints.org, *Agent Harness for Large Language Model Agents: A Survey*, 2026-04\]

### 自然语言 Harness：下一个前沿

2026 年 3 月，Tsinghua 团队的论文和一篇 Stanford/SambaNova/UC Berkeley 合作研究同期提出：Harness 本身可以用自然语言而非 Python 代码来描述——即 **Natural-Language Agent Harnesses（NLAH）**。^\[arxiv.org/html/2603.25723v1\]

这意味着：Harness 像代码一样可以被版本化、检索、迁移、重组，并且可以被 LLM 本身解释和执行。Harness 从"程序员写死的脚手架"变成了"可被 AI 读懂和优化的工程文档"。这是 Harness Engineering 作为独立学科成熟化的信号。

---

## 7\. 主流 AI 公司的范式实践

### Anthropic：从模型到生态的系统性布局

Anthropic 的战略重心从 Claude 的对话能力，逐步移向 **Agent 基础设施层**：

**Claude Code（2025 年发布）**  
Karpathy 将其评价为"the first convincing demonstration of what an LLM Agent looks like"。^\[Karpathy, *2025 LLM Year in Review*\] Claude Code 的关键设计决策：Local-first（运行在开发者本机，而非云端），让 Agent 直接访问文件系统、环境变量、git 历史——这是 Harness 设计而非模型能力决定的。Anthropic 在 2026 年仅 Claude Code 一项的年化收入据估计已超过 5 亿美元。^\[Turing College AI Engineering Guidebook, 2026\]

**Model Context Protocol（MCP）**  
2024 年底 Anthropic 发布，2025 年底捐献给 Linux Foundation，由 Anthropic、OpenAI、Google、Microsoft、AWS 共同治理。MCP 是工具层的标准化协议，截至 2026 年初已有超过 10,000 个活跃公共服务器，每月 SDK 下载量 9700 万次。^\[The Agent Arms Race Blog, bosio.digital, 2026-03\] MCP 解决的是"碎片化集成"问题——让 Harness 的工具层变成可插拔的标准化基础设施。

**Context Engineering 文档化**  
Anthropic 工程团队于 2025 年正式发布博客 *Effective Context Engineering for AI Agents*，将 Context Engineering 定义为"the set of strategies for curating and maintaining the optimal set of tokens during LLM inference"^\[anthropic.com/engineering/effective-context-engineering-for-ai-agents\]，并系统阐述了上下文腐烂、注意力预算、动态检索等核心概念。

---

### OpenAI：Harness Engineering 的自我证明

OpenAI 在 2026 年 2 月发布的博客 *Harness Engineering: Leveraging Codex in an Agent-First World* 是迄今为止最具说服力的内部实践案例之一：^\[OpenAI, *Harness Engineering*, 2026-02-11\]

- 空仓库第一次提交时间：2025 年 8 月底  
- 初始脚手架（仓库结构、CI 配置、格式化规则、包管理器配置）由 Codex 自动生成  
- 连 AGENTS.md 本身也是由 Codex 写的——一开始就没有人类写的代码  
- 5 个月后：约 100 万行代码，涵盖业务逻辑、基础设施、工具、文档  
- 三名工程师，每人每天平均 3.5 个 PR

这不是概念验证，这是一个从零到生产的闭环证明。Stripe 的 Minions 系统每周通过混合了确定性节点（linters、CI）与 Agentic 循环的"Blueprint"架构自动提交超过 1000 个 PR。^\[Preprints.org, Agent Harness Survey, 2026-04\]

---

### Google：全栈战略与 Agent 标准化

Google 在 2026 年 4 月的 Cloud Next 上进行了重大整合，将 Vertex AI 更名为 **Gemini Enterprise Agent Platform**，并发布了一系列 Harness 层标准化工具：^\[The Next Web, *Google Cloud Next 2026*, 2026-04\]

- **ADK（Agent Development Kit）v1.0 稳定版**：四种语言版本，统一 Agent 开发体验  
- **A2A（Agent-to-Agent）协议 v1.0**：处理 Agent 间的跨组织通信，与 MCP 互补（MCP 管工具接入，A2A 管 Agent 通信）  
- **Workspace Studio**：无代码 Agent 构建器，让业务人员用自然语言描述自动化  
- **Apigee 作为 MCP 网关**：将任何标准 API 转化为 Agent 可发现的工具

Google 的战略叙事是"全栈拥有"——从 TPU 芯片、Gemini 模型、ADK/A2A 运行时，到 Gmail/Workspace 分发渠道，试图形成无法被单一竞争对手复制的垂直整合。

---

### 其他值得关注的实践

**Cursor / Codex（编码 Harness 竞争）**  
Cursor 在 2026 年 3 月已突破年化 20 亿美元营收。这背后不是模型竞争，而是上下文工程竞争——Cursor 的差异化在于更好的代码库理解 Harness（@codebase 检索、多文件编辑协调等）。

**Shopify（组织层面的范式重塑）**  
Tobi Lütke 的 "Context Engineering" 定义不仅是技术术语，也反映了 Shopify 内部的工程文化转型——他们已将 AI Agent 能力定义为员工职业发展的必要条件。

**12-Factor Agents 框架**  
参考"12-Factor App"的设计，社区提出了生产级 AI Agent 应遵循的 12 个原则，涵盖状态外化、工具设计、中断恢复、可观测性等，成为 Harness Engineering 的早期规范化尝试。^\[Elastic Blog, *Context Engineering vs Prompt Engineering*, 2026-01\]

---

## 8\. 大咖观点汇总

| 人物 | 机构 | 核心观点 | 来源 |
| :---- | :---- | :---- | :---- |
| Andrej Karpathy | 独立 / 前 OpenAI | "LLMs are a new kind of computer, programmed in English. We are computing circa \~1960s." | AI Startup School Talk, 2025-06 |
| Andrej Karpathy | \- | "Context engineering is the delicate art and science of filling the context window with just the right information for the next step." | X (@karpathy), 2025-06 |
| Andrej Karpathy | \- | "Claude Code is 'the first convincing demonstration of what an LLM Agent looks like'... Anthropic got this order of precedence correct." | 2025 LLM Year in Review, 2025-12 |
| Tobi Lütke | Shopify CEO | "Context engineering is the art of providing all the context for the task to be plausibly solvable by the LLM." | X (@tobi), 2025-06 |
| Dario Amodei | Anthropic CEO | "We might be 6-12 months away from models doing all of what software engineers do end-to-end." | Multiple public interviews, 2025-2026 |
| Sam Altman | OpenAI CEO | "10,000-person-equivalent companies run by one person." | Multiple public statements, 2025 |
| Gartner | 研究机构 | "Context engineering is in, and prompt engineering is out. AI leaders should prioritize context over prompts." | Gartner Research, 2025-07 |
| Anthropic 工程团队 | Anthropic | "LLMs, like humans, lose focus or experience confusion at a certain point... Context must be treated as a finite resource with diminishing marginal returns." | *Effective Context Engineering for AI Agents*, 2025 |
| Birgitta Böckeler | Thoughtworks | "Agent \= Model \+ Harness. The harness is everything that isn't the model." | martinfowler.com, 2026-04 |
| OpenAI Codex 团队 | OpenAI | "Early progress was slower than we expected, not because Codex was incapable, but because the environment was underspecified." | *Harness Engineering*, 2026-02 |

---

## 9\. 个人深度思考：范式迁移的底层逻辑

### 9.1 这不是工具升级，而是抽象层次的跃迁

每一次计算范式迁移的本质，是**编程抽象层次的提升**：从机器码到汇编，从汇编到高级语言，从高级语言到 SQL/声明式编程，现在从代码到自然语言。

每次抽象提升都有相同的结构：**新的抽象层使大量原来必须显式处理的复杂性变得隐式**，但同时引入了新的隐式复杂性。SQL 让人不再关心 B 树的实现，但引入了查询优化器的黑盒问题。LLM 让人不再关心函数实现，但引入了 Context 管理的新工程问题。

Prompt Engineering → Context Engineering → Harness Engineering 的演进路径，正是沿着"管理新隐式复杂性"的方向展开的：先学会说话，再学会管理信息，最后学会构建可靠系统。

### 9.2 "模型竞争"的护城河正在消失

一个关键的市场现象正在浮现：当底层模型能力趋于同质化（各大 LLM 在大多数基准测试上性能趋同），差异化竞争将完全转移到 **Harness 层**。

这意味着：

- 谁拥有更好的 Context 管理策略，谁就有更低的 Token 成本  
- 谁拥有更可靠的工具层封装，谁就有更高的任务成功率  
- 谁拥有更丰富的记忆系统，谁就有更强的个性化能力

"It's often said in AI product development now that 'the harness makes or breaks an AI product'. Two products might use the same underlying LLM, but the one with a superior harness will deliver a far better user experience."^\[Parallel.ai Blog\] 这句话正在成为产品竞争的第一定律。

### 9.3 软件工程师角色的重新定义

传统软件工程师的核心工作是"确定性地将逻辑翻译为代码"。在 LLM 时代，这个工作正在被自动化。但新的核心工作出现了：

- **意图建模（Intent Architecture）**：将模糊的业务需求转化为结构化的、可被 AI 系统理解的描述  
- **验证工程（Verification Engineering）**：设计测试体系（Computational \+ Inferential），确保 AI 输出的可信度  
- **Harness 架构（Harness Architecture）**：设计 Agent 的执行环境、工具生态、记忆系统  
- **观测与调优（Observability & Tuning）**：从 Agent 轨迹数据中提取信号，持续改进系统

技术的门槛并没有消失，只是从"如何写正确的代码"，迁移到了"如何构建可靠的 AI 系统"。

### 9.4 "Vibe Coding"的误解与真相

Karpathy 提出的"Vibe Coding"（用自然语言描述意图，让 AI 生成代码）被许多人解读为"编程技能不再重要"。但这是一个危险的误解。

Vibe Coding 降低了**写代码**的门槛，但提高了**系统设计**的重要性。一个没有基础的 Vibe Coder 可以很快生成"可以运行的代码"，但无法生成"可维护、可扩展、安全可靠的系统"。理解架构原则、数据模型、安全边界、性能约束——这些能力变得更加核心，因为 AI 不会自动考虑这些。

真正的竞争力变成：**能否精确地定义问题、约束空间、验证结果**。这需要更深的领域理解，不是更少的。

### 9.5 "上下文"正在成为企业的核心资产

在 LLM 时代，数据的价值不再仅仅在于"拥有数据"，而在于\*\*"将数据结构化为 Agent 可消费的上下文"\*\*。哈佛商学院 2026 年 2 月的研究指出：在每个公司都使用相同 AI 模型的前提下，**结构化的机构知识库**——记录决策过程、经验教训、业务规则——成为真正的差异化竞争优势。^\[The Agent Arms Race Blog, 转引 HBR Research, 2026-02\]

这意味着"Context 资产化"将成为企业 AI 战略的核心命题：不只是上云、用 API，而是系统性地将组织智慧转化为可被 AI Agent 调用的结构化上下文。

---

## 10\. 建设性建议：如何在范式迁移中站稳脚跟

### 对于个人工程师

**① 立即转移学习重心**  
从"如何用 X 语言写出 Y 功能"，转向"如何设计一个 AI 系统能够可靠地完成 Y 功能"。核心学习路径：Context Engineering 设计模式 → Agent 架构 → 可观测性 → Harness 组件开发。

**② 建立验证体系优先于自动化体系**  
在你的 AI 系统能够无监督运行之前，先建立能够检验其输出的 Computational Guide（linters、类型检查器、单元测试）和 Inferential Sensor（LLM-as-judge、语义相似度检查）。让 AI 的结果可被快速验证，比让 AI 完全自主运行更有价值。^\[Böckeler, martinfowler.com, 2026-04\]

**③ 培养"意图精确性"的写作能力**  
技术精确的自然语言写作——能够清晰描述任务约束、边界条件、验收标准——是 Software 3.0 时代最核心的工程技能之一。这比掌握某个框架更难学，也更难被替代。

**④ 在自己的领域构建上下文资产**  
创建并维护 SKILL.md、AGENTS.md、CONTEXT.md 等结构化文档，将领域知识、常见错误模式、最佳实践系统化为 AI Agent 可消费的形式。你的领域经验，通过这种方式可以显著放大 AI 的生产效率。

### 对于团队和组织

**① 将 Harness 工程与 LLM 选型分开管理**  
不要将团队的核心能力绑定在单一 LLM 供应商上。Harness 应该是模型无关的——优秀的 Harness 设计应该能够以最小代价切换底层模型。

**② 建立 Agent Observability 基础设施**  
在 Agent 上生产之前，必须有完整的轨迹日志、token 消耗追踪、任务成功率追踪。没有 Observability 的 Agent 系统，是一个无法优化的黑盒。

**③ 渐进式自主化路径**  
不要一开始就追求完全自主 Agent。推荐路径：人工执行（AI 辅助） → 人工审核（AI 起草）→ 例外处理（AI 执行，人工审核异常）→ 完全自主（高置信度场景）。在每个阶段先建立信任，再扩展自主权。

**④ 构建组织级的 Context 知识库**  
将公司的业务规则、决策记录、产品文档系统化为结构化知识库，并建立 RAG 管道使其对 Agent 可访问。这是企业 AI 战略的核心资产，而非辅助工具。

### 对于 AI 产品设计者

**① "Context 即产品"的设计原则**  
一个 AI 产品的差异化，往往不在于用了哪个模型，而在于它能够为用户的任务提供多丰富、多精准的上下文。设计产品时，把"用户的知识、偏好、历史、工具"系统化地纳入 Context 管理框架，是比模型选型更重要的产品决策。

**② 可观测的 AI 体验（Observable AI UX）**  
为用户设计清晰的"AI 正在做什么"可视化——轨迹展示、置信度指示、人工接管节点。降低用户的认知焦虑，是提升 AI 产品采用率的关键。

**③ 为 Agent 设计，而非为人设计**  
随着 AI Agent 成为新的主要信息消费者，CLI 优于 GUI（因为 CLI 输出更结构化）、结构化日志优于富文本界面、API First 优于 UI First。Karpathy 明确指出：LLMs are the new primary consumer of digital information，产品设计应当为此做适配。^\[Karpathy, AI Startup School Talk, 2025-06\]

---

## 11\. 结语：我们身处哪个时刻？

Karpathy 用了一个精确的历史坐标：**"We are computing circa \~1960s."** ^\[ibid.\] 上世纪 60 年代，计算机还是大型机，主要通过批处理、打卡输入来使用，只有少数专业人士能够接触。个人计算、图形界面、互联网，都还没有到来。

我们现在所处的位置，大概就是那个时刻。

今天的"对话框提示词"，是那个时代的命令行。Context Engineering 是我们正在学习如何分配有限的计算资源。Harness Engineering 是我们开始构建这个新计算范式的操作系统基础设施。

三层范式的迁移，不是一个结束，而是一个开始。它们的关系是累积的、嵌套的：

- **Prompt Engineering** 教会了我们 LLM 能理解什么、如何沟通  
- **Context Engineering** 教会了我们信息管理的系统性原则  
- **Harness Engineering** 正在教会我们如何构建可信赖的 AI 系统

这个序列还没有终点。下一层——也许是"**Intent Engineering**"或"**Objective Engineering**"——将是关于如何向 AI 系统清晰定义目标函数和价值约束，而不仅仅是任务描述。

但有一件事是确定的：**工程的本质没有变，只是工程的对象和工具变了。** 那些能够系统性地思考复杂性、严格地验证假设、持续地从反馈中学习的工程师，无论范式怎么迁移，都会找到自己的位置。

---

## 参考资料

1. Andrej Karpathy, *2025 LLM Year in Review*, karpathy.bearblog.dev, 2025-12-21  
2. Andrej Karpathy, *Software Is Changing (Again)*, AI Startup School @ YCombinator, 2025-06  
3. Andrej Karpathy on X (@karpathy), LLM OS tweet, 2023-09-19  
4. Tobi Lütke on X (@tobi), Context Engineering definition, 2025-06-18  
5. Anthropic Engineering Blog, *Effective Context Engineering for AI Agents*, anthropic.com/engineering, 2025  
6. OpenAI, *Harness Engineering: Leveraging Codex in an Agent-First World*, openai.com, 2026-02-11  
7. Birgitta Böckeler, *Harness Engineering for Coding Agent Users*, martinfowler.com, 2026-04  
8. Adnan Masood, *Agent Harness Engineering — The Rise of the AI Control Plane*, Medium, 2026-04  
9. Preprints.org, *Agent Harness for Large Language Model Agents: A Survey*, preprints.org/manuscript/202604.0428, 2026-04  
10. Natural-Language Agent Harnesses paper, arxiv.org/html/2603.25723v1, 2026-03  
11. Gartner, "Context engineering is in, and prompt engineering is out", 2025-07, 转引自 IntuitionLabs.ai  
12. IntuitionLabs.ai, *Context Engineering vs Prompt Engineering*, 2026-04  
13. Firecrawl Blog, *Context Engineering vs Prompt Engineering for AI Agents*, firecrawl.dev/blog/context-engineering, 2026-02  
14. Neo4j Blog, *Why AI Teams Are Moving From Prompt Engineering to Context Engineering*, 2026-01  
15. Elastic Blog, *Context engineering vs. prompt engineering*, elastic.co, 2026-01  
16. DecodingAI.com, *Agentic Harness Engineering: LLMs as the New OS*, 2026-04  
17. IDC Community, *The 3rd Generation of Agents: How "Harness Engineering" Changed Games Again*  
18. Parallel.ai, *What is an Agent Harness in the Context of Large-Language Models?*  
19. The Next Web, *Google Cloud Next 2026: AI agents, A2A protocol, Workspace Studio*, 2026-04  
20. Yahoo Finance / Benzinga, *Anthropic CEO Predicts AI Models Will Replace Software Engineers*, 2026-01  
21. Turing College, *AI Engineering Guidebook: 10 AI Engineering Principles in 2026*  
22. bosio.digital, *The Agent Arms Race: OpenAI, Anthropic, and Google*, 2026-03  
23. The Conversation, *AI agents arrived in 2025 – here's what happened*, 2026-01  
24. Kyle Howells (ikyle.me), *Talk: Andrej Karpathy: Software Is Changing (Again)*, 2025-06  
25. Mehul Gupta, *Context Engineering vs Prompt Engineering*, Medium, 2025-06

---

*By SkySeraph 2026.4，本文为个人技术观察与行业综合整理，欢迎交流探讨。所有观点均注明来源，未注明部分为个人判断。*
