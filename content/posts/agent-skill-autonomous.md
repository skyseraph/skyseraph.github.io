---
title: "Agent Skill Autonomous"
date: 2026-04-22T08:00:00+08:00
categories: ["技术"]   # 技术 / 随笔 / 项目
tags: ["LLM","Agent","Skill","Autonomous"]
toc: true
draft: false
---

# Agent Skill Autonomous

**时间：** 2026年4月22日  
**范围：** 2026年1月—4月 arXiv 论文 \+ 官方工具 \+ 主要开源项目  
**总量：** 32 篇论文 \+ 6 个工程项目，全部附链接

---


## 一、背景速览

Anthropic 于 2025 年 10 月发布 Agent Skills 开放标准：一个 **Skill** 是以 SKILL.md 为核心的结构化目录，包含声明式工作流指令、可执行脚本与领域参考资料，推理时按需动态加载。与单次 Tool Call（单一函数）不同，Skill 是可复用、可组合的**过程性知识包**。

- 2025-10 Anthropic 发布 Agent Skills 标准  
- 2025-12 作为开放标准发布，OpenAI Codex 等采纳  
- 2026-02 公开可用 Skill 超过 28 万个，ClawHub 日提交量峰值超 500  
- 2026-04 Skill 生态安全事件频发，学术界进入"创建→进化→安全"三线并行研究阶段

---

## 二、综述 / 框架类（4 篇）

---

### 2.1 SoK: Agentic Skills — Beyond Tool Use in LLM Agents

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2602.20867](https://arxiv.org/abs/2602.20867) |
| 发布 | 2026-02-24 |
| 性质 | Systematization of Knowledge |

**核心原理：** 覆盖 Skill 全生命周期（发现、实践、蒸馏、存储、组合、评估、更新），提出两套互补分类体系：
- ① **七个系统级设计模式**（Pattern-1 元数据驱动渐进披露 → Pattern-7 市场分发）
- ② 正交的表示×调用×存储分类。是全领域坐标系的必读基础文献。

---

### 2.2 Agent Skills for LLMs: Architecture, Acquisition, Security, and the Path Forward

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2602.12430](https://arxiv.org/abs/2602.12430) |
| 发布 | 2026-02-17（v3 更新） |

**核心原理：** 梳理三范式演进：Prompt 工程(2022–23) → Tool 调用(2023–24) → **Skill 工程(2025–)**，提出 Skill 与 MCP 正交（Skill 提供过程智能，MCP 提供连接性）
- 原创贡献是四阶段验证（G1-G4）+ T1-T4 信任等级的完整治理框架，跨越技能来源追溯、验证和运行时权限全生命周期。

---

### 2.3 SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2602.12670](https://arxiv.org/abs/2602.12670) |
| 项目页 | [skillsbench.ai](https://www.skillsbench.ai/blogs/introducing-skillsbench) |
| 发布 | 2026-02-13（v3: 2026-03-13） |
| 规模 | 86 任务 · 11 领域 · 7 模型配置 · 7,308 条轨迹 |

**核心原理：** 三条件对照评估框架——无 Skill / 精心策划 Skill / 自生成 Skill。每个任务配确定性验证器（pytest），实现可复现的二元 pass/fail。
- 关键发现：精心策划 Skill \+16.2pp，但自生成 Skill 平均 \-1.3pp（"模型无法可靠撰写自己受益的 Skill"）——这是整个进化研究的根本动机。

---

### 2.4 How Well Do Agentic Skills Work in the Wild?

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.04323](https://arxiv.org/abs/2604.04323) |
| GitHub | [UCSB-NLP-Chang/Skill-Usage](https://github.com/UCSB-NLP-Chang/Skill-Usage) |
| 发布 | 2026-04-07 |
| 模型 | Claude Opus 4.6 · Kimi K2.5 · Qwen3.5-397B |

**核心原理：** 渐进真实场景测试——理想化手工 Skill → 加干扰 Skill → 真实检索池（含目标技能）→ 检索池（不含目标技能）。随设置真实化，收益持续下降最终接近无技能基线。两大瓶颈：
- ① Agent 难判断哪些 Skill 值得加载
- ② 检索到的 Skill 内容嘈杂。**查询特定精细化**策略可在 Terminal-Bench 2.0 将 Opus 4.6 从 57.7% → 65.5%

---

## 三、Anthropic 官方工具：skill-creator（元技能）

---

### 3.1 Claude Code skill-creator

| 字段 | 内容 |
| :---- | :---- |
| 官方 SKILL.md | [anthropics/skills/skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) |
| 文档 | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| 性质 | Anthropic 官方元技能（技能创建技能） |

**核心原理：** skill-creator 是一个**元技能（meta-skill）**，本身就是一个 SKILL.md，用来帮助用户创建其他 Skill——递归地将 Skill 系统用于自身。工作流：

1. **描述阶段**：用户用自然语言描述期望能力、触发场景、预期输出；  
2. **生成阶段**：Claude 生成完整 SKILL.md，包括 YAML frontmatter（name/description/compatibility）和 Markdown 主体（指令/示例/格式定义）；  
3. **评估循环**：内置触发率评估脚本，将 eval 集 60/40 分为训练/测试集，对每个 description 运行 3 次取平均触发率，迭代最多 5 次，最终以测试集分数（而非训练集）选择最优 description，防止过拟合；  
4. **安装**：生成物可直接放入 `.claude/skills/` 或通过 `claude.ai → Settings → Capabilities → Skills` 上传。

**设计哲学：** "Context window 是公共品"——Skill 应携带最小化但足够的知识；Description 是主要触发机制，既要具体又不能过窄；模型本来就很聪明，不要在指令里解释显而易见的事情。

**地位：** 学术文献（如 EvoSkills、Trace2Skill）将 skill-creator 作为\*\*基线（Baseline）\*\*进行对照实验，是当前自动创建研究的参照基准。

---

## 四、自动创建（Auto-Creation）论文（7 篇）

---

### 4.1 CASCADE: Cumulative Agentic Skill Creation through Autonomous Development and Evolution

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2512.23880](https://arxiv.org/abs/2512.23880) |
| 发布 | 2025-12-29（v2: 2026-01-28） |
| 领域 | 材料科学 · 化学 |

**核心原理：** 通过两个**元技能**驱动能力累积：
- ① **持续学习**（网络搜索 \+ 代码提取 \+ 记忆利用）
- ② **自反思**（内省 \+ 知识图谱探索）。Agent 掌握复杂外部工具后将知识编码为可共享技能。SciSkillBench（116 任务）上 GPT-5 成功率 93.3%（vs 无进化机制 35.4%）。技能可跨 Agent 和科学家共享，向 "LLM \+ 技能习得"范式过渡的早期实例。

---

### 4.2 CUA-Skill: Develop Skills for Computer Using Agent

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2601.21123](https://arxiv.org/abs/2601.21123) |
| 发布 | 2026-02-02 |

**核心原理：** 将人类计算机使用知识编码为**参数化技能**，配以显式**执行图**和**组合图**。初始版本包含跨数十个 Windows 热门应用的数百个原子技能。通过参数化 \+ 组合可实例化为百万级可执行任务变体。Agent 支持：
- ① 动态技能检索；② 参数实例化（将任务参数填入技能模板）
- ③ 记忆感知故障恢复（从历史失败中学习重试策略）

---

### 4.3 EvoSkill: Automated Skill Discovery for Multi-Agent Systems

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.02766](https://arxiv.org/abs/2603.02766) |
| 发布 | 2026-03-03 |

**核心原理：** 迭代**失败分析**驱动的技能发现——分析执行失败轨迹 → 提出新技能或修改现有技能 → 物化为结构化技能目录。**Pareto 前沿**管理技能选择，仅保留能提升保留验证集性能的技能，防止技能集膨胀。底层模型保持冻结（非 fine-tuning）。**局限**：失败诊断依赖 ground-truth 标注，限制真实部署适用性。

---

### 4.4 AutoSkill: Experience-Driven Lifelong Learning via Skill Self-Evolution

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.01145](https://arxiv.org/abs/2603.01145) |
| 发布 | 2026-03-01 |

**核心原理：** 从**用户对话和交互轨迹**中自动提炼技能（而非预定义），技能格式为**提示模板**（而非可执行包）。三阶段技能生命周期：① 从经验中抽象技能（归纳用户稳定偏好）；② 技能自进化（随新交互持续更新）；③ 动态注入（相关技能按需注入未来请求，无需重训）。模型无关插件层，支持跨 Agent/用户/任务的标准化技能表示共享。面向个性化场景（减少幻觉、遵循写作规范等）。

---

### 4.5 SkillNet: Create, Evaluate, and Connect AI Skills

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.04448](https://arxiv.org/abs/2603.04448) |
| GitHub | [zjunlp/SkillNet](https://github.com/zjunlp/SkillNet) |
| 技能库 | [skillnet.openkg.cn](http://api-skillnet.openkg.cn/v1/search?q=pdf) |
| 发布 | 2026-02-26 |
| 规模 | 200,000+ 技能，150,000+ 高质量节点 |

**核心原理：** 在统一**技能本体**中构建知识图谱，关系类型包括 compose/belong\_to/depend\_on/similar\_to，形成**可推理、可规划、可进化**的能力空间。五维评估维度（安全性/完整性/可执行性/可维护性/成本意识）。Agent 可以"像查地图一样"导航能力空间。ALFWorld/WebShop/ScienceWorld 上平均奖励 \+40%，执行步骤 \-30%。`pip install skillnet-ai` 开箱即用，与 JiuwenClaw/OpenClaw 原生集成，MCP 服务器已发布。

---

### 4.6 AgentSkillOS: Organizing, Orchestrating, and Benchmarking Agent Skills at Ecosystem Scale

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.02176](https://arxiv.org/abs/2603.02176) |
| 发布 | 2026-03-02 |

**核心原理：** 两阶段框架：
- ① **管理技能**——节点级递归分类，将技能组织为**能力树**（Capability Tree）实现高效发现
- ② **解决任务**——DAG 管道检索、编排、执行多个技能协同完成任务。构建了跨数据计算、文档创建、运动视频等五类共 30 个富含产出物的基准任务，使用 Bradley-Terry 模型聚合 LLM-as-judge 成对比较分数。截至 2026-02 已有 28 万+ 公开技能，其中绝大多数由去中心化第三方贡献。

---

### 4.7 Meta Context Engineering (MCE) via Agentic Skill Evolution

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2601.21557](https://arxiv.org/abs/2601.21557) |
| GitHub | [metaevo-ai/meta-context-engineering](https://github.com/metaevo-ai/meta-context-engineering) |
| 发布 | 2026-01-29（v2: 2026-02-11） |
| 机构 | 北京大学通用人工智能国家重点实验室 |

**核心原理：** 将 **Context Engineering（CE）本身作为可进化对象**。双层框架：
- ① 元级 Agent 通过 **Agentic Crossover**（对历史技能、执行、评估的蓄意搜索）精炼 CE 技能
- ② 基础级 Agent 执行这些技能，从训练 rollout 中学习。将上下文形式化为 `c(x) = (F_k ∘ ... ∘ F_1)(x; ρ)`（静态组件 \+ 动态算子）。五领域（金融/化学/医学/法律/AI安全）上相比 SOTA CE 方法实现 5.6–53.8% 相对改进（均值 16.9%）。

---

## 五、自主进化（Self-Evolution）论文（7 篇）

---

### 5.1 CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.01687](https://arxiv.org/abs/2604.01687)（v2 正式名 CoEvoSkills） |
| GitHub | [Zhang-Henry/CoEvoSkills](https://github.com/Zhang-Henry/CoEvoSkills) |
| 项目页 | [zhang-henry.github.io/CoEvoSkills](https://zhang-henry.github.io/CoEvoSkills/) |
| 发布 | 2026-04-02（v2: 2026-04-12） |
| 机构 | UIC · Columbia · Chonnam · UBC |

**核心原理：** 两个核心组件**协同进化**（Co-Evolution）：

- **Skill Generator**：迭代生成并精炼多文件技能包，维护跨迭代的持久对话上下文积累高保真反馈；  
- **Surrogate Verifier**：信息隔离的独立 LLM 会话（不继承 Generator 的偏见），自主进化测试断言，在**无法访问 ground-truth** 的情况下提供密集的可操作失败反馈。

Ground-truth Oracle 仅返回不透明 pass/fail 信号，当 Surrogate 失败时触发 Oracle 升级，严格保持信息隔离。5 轮进化后超越人工策划技能，SkillsBench 上在 Claude Code 和 Codex 两个 harness 下均取得五个基线中最高通过率，并对 6 个额外 LLM 表现出强泛化能力。

**关键区别**（v1 曾标题为 EvoSkills）：v2 更名 CoEvoSkills 以明确"协同进化"的双主体性质。

---

### 5.2 Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.25158](https://arxiv.org/abs/2603.25158) |
| 发布 | 2026-03-26（v3: 2026-03-31） |
| 机构 | ETH Zürich / Microsoft Research 等 |

**核心原理：** 镜像人类专家写作技能的方式——先整体分析广泛执行经验，再蒸馏为单一全面指南。核心机制：
- ① **并行子 Agent 分析**（而非顺序处理）——调度子 Agent 并行分析多样轨迹池
- ② **层级归纳合并**——通过归纳推理将轨迹特定经验层次化整合为统一、无冲突的技能目录。支持深化已有人工技能和从零创建新技能。Qwen3.5-35B 自身轨迹进化的技能让 Qwen3.5-122B 在 WikiTableQuestions 上提升最多 \+57.65 pp，无需参数更新。

---

### 5.3 SkillX: Automatically Constructing Skill Knowledge Bases for Agents

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.04804](https://arxiv.org/abs/2604.04804) |
| GitHub | [zjunlp/SkillX](https://github.com/zjunlp/SkillX) |
| 发布 | 2026-04-06（v2: 2026-04-19） |
| 机构 | 浙大 NLPLAB |
| 基准 | AppWorld · BFCL-v3 · τ²-Bench |

**核心原理：** 三创新协同构建插件式技能知识库：
- ① **多层次技能设计**——将原始轨迹蒸馏为三级层次（战略计划/功能技能/原子技能）
- ② **迭代技能精炼**——基于执行反馈自动修订技能，持续提升库质量
- ③ **探索性技能扩展**——主动生成并验证新技能，覆盖范围扩展至种子训练数据之外，解决未见行为泛化问题。用强骨干（GLM-4.6）构建库后，直接注入弱 Agent 实现**强→弱迁移**，无需重训。

---

### 5.4 SkillClaw: Let Skills Evolve Collectively with Agentic Evolver

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.08377](https://arxiv.org/abs/2604.08377) |
| GitHub | [AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw) |
| 发布 | 2026-04-09 |

**核心原理：** 首个**多用户集体进化**框架。流水线：
- ① **Session 记录**——将每次交互存储为因果链（提示→动作→反馈→答案），保留完整中间过程（因为技能级失败在最终答案中不可见）
- ② **按技能分组**——聚合所有引用同一技能的 session
- ③ **Agentic Evolver**——LLM Agent 配结构化 Harness，基于开放式推理（非预定义规则）独立决策：Refine（修正错误）/ Create（发现新子流程时创建新技能）/ Skip（证据不足时保持不变）
- ④ **夜间验证门控**——延迟更新直至安全滚出
- ⑤ **跨用户同步**——改进结果写回共享库，无需用户额外操作。WildClawBench 6轮进化后 Creative Synthesis 相对提升 88.41%。

---

### 5.5 ARISE: Agent Reasoning with Intrinsic Skill Evolution in Hierarchical RL

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.16060](https://arxiv.org/abs/2603.16060) |
| 发布 | 2026-03-17 |
| 领域 | 数学推理（竞赛数学 \+ Omni-MATH） |

**核心原理：** 层次强化学习框架，共享策略同时充当高层**技能管理器（Manager）和低层Worker**。Manager 通过专用技能生成 rollout，对成功解题轨迹进行结构化摘要，维护分层技能库；Worker 在执行时受 Manager 的策略驱动选择技能。**层次奖励设计**引导推理能力和库质量协同进化（双路径训练信号）。7 个数学基准上一致优于 GRPO 系列，OOD 任务上收益尤其显著，且消融实验确认库质量和推理性能在训练中同步提升。

---

### 5.6 SkillMOO: Multi-Objective Optimization of Agent Skills for Software Engineering

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.09297](https://arxiv.org/abs/2604.09297) |
| 发布 | 2026-04-11 |

**核心原理：** 将 Skill 优化建模为**多目标优化（MOO）问题，同时优化通过率和推理成本。算法核心：NSGA-II 存活选择（非支配排序 \+ 拥挤距离）+ LLM 提议编辑（剪枝/替换/重排/重写）的迭代循环。两 Agent 架构：
- ① 任务求解器 Agent 评估候选技能包，产出通过率/成本/错误追踪
- ② 技能优化器 Agent 根据失败证据和当前优化器技能提示提议子技能包，同时更新自身优化器技能（元优化）。SkillsBench 三个 SE 任务上，通过率最高提升 131%，成本最高降低 32%。模式分析揭示剪枝和替换**是改进的主要驱动因素，有效技能包应倾向最小化、聚焦的内容而非累积指令。

---

### 5.7 SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2602.08234](https://arxiv.org/abs/2602.08234) |
| 发布 | 2026-02-11 |

**核心原理：** 通过 RL 从轨迹中蒸馏层次化技能库，配合教师指导蒸馏过程，产生提示级启发而非可执行产物。将技能反复注入 RL 训练，形成"技能→更好轨迹→更好技能"的递归正向循环。与 ARISE 的区别在于：SkillRL 更侧重技能辅助 RL 训练本身（技能是训练基础设施），而 ARISE 侧重推理时技能管理。

---

## 六、基准测试 / 评测（专栏）（5 篇）

---

### 6.1 SWE-Skills-Bench: Do Agent Skills Actually Help in Real-World Software Engineering?

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.15401](https://arxiv.org/abs/2603.15401) |
| 发布 | 2026-03-16 |
| 机构 | 南京大学 · MBZUAI · UNSW |
| 规模 | 49 个公开 SWE 技能 · \~565 任务实例 · 6 个 SWE 子领域 |

**核心原理：** 首个**需求驱动**的 SWE 专项技能基准。四阶段流水线：
- ① 从大型公开仓库策划 SWE 技能
- ② 每个技能与固定提交的 GitHub 仓库 \+ 需求文档（含显式验收标准）配对
- ③ 需求标准 → pytest 单元测试（确定性验证器）
- ④ 有技能 vs 无技能的对照评估。**关键结论**：49 个技能中 39 个（80%）通过率为零改进，平均增益仅 \+1.2%。只有 7 个专项技能产生有意义的增益（最高 \+30%），3 个导致性能下降（最低 \-10%）——版本错配的指导与项目上下文冲突所致。

---

### 6.2 SkillCraft: Can LLM Agents Learn to Use Tools Skillfully?

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.00718](https://arxiv.org/abs/2603.00718) |
| 发布 | 2026-02-28（v2: 2026-03-10） |

**核心原理：** 聚焦 Agent **在线即时技能获取**能力的基准——不预先提供技能，而是测试 Agent 能否在任务执行中将原子工具**自动组合为可复用的高阶技能**并跨任务缓存复用。特点：
- ① 真实、高度组合的工具使用场景
- ② 沿定量和结构两个维度缩放难度
- ③ 轻量级评估协议（auto-compose → cache → reuse），既测量效率又积累性能。与 SkillsBench 的根本区别：SkillsBench 测静态已有技能的效用，SkillCraft 测 Agent 动态习得技能的能力。

---

### 6.3 SkillReducer: Optimizing LLM Agent Skills for Token Efficiency

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.29919](https://arxiv.org/abs/2603.29919) |
| 发布 | 2026 年 3 月 |

**核心原理：** 两阶段压缩流水线：
- ① **Stage 1（路由层优化）**——通过对抗 delta 调试压缩冗余描述，并为缺失描述生成语义描述
- ② **Stage 2（主体重构）**——分类法驱动的渐进披露，将可操作核心规则与按需加载的补充内容分离，通过忠实性检查和自修正反馈循环验证。在 600 个技能上评估：描述 Token \-48%，主体 Token \-39%，同时功能质量 \+2.8%——揭示"**少即是多**"效应（移除非必要内容减少上下文窗口干扰）。在 SkillsBench 上 87/87 任务零回归，跨四个模型系列平均保留率 0.965。

---

### 6.4 SkillRouter: Skill Routing for LLM Agents at Scale

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.22455](https://arxiv.org/abs/2603.22455) |
| 发布 | 2026 年 3 月 |

**核心原理：** 将技能路由形式化为**大规模精确检索**问题——约 8 万技能池（含 51 类 Claude Skill Registry Core \+ 780 个 LLM 生成干扰技能）。区分 Easy（78,361 候选）和 Hard（79,141 候选，含功能相关但相似度高的干扰技能）两个难度。SkillRouter 超越最强基础路由器 \+1.78pp（top-1）和 \+2.33pp（top-10），恢复约 71–73% 的黄金技能增益差距。关键发现：简单描述相似度在大规模池上严重失效，需要实现感知（implementation-aware）的路由策略。

---

## 七、安全与可信测评专栏（6 篇）

---

### 7.1 Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale（SkillScan）

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2601.10338](https://arxiv.org/abs/2601.10338) |
| 发布 | 2026-01-15 |

**核心原理：** 首个大规模 Skill 安全实证研究。爬取 skills.rest 和 skillsmp.com 共 42,447 个技能，分析 31,132 个。构建 **SkillScan**：多阶段检测框架，集成静态代码分析与 LLM-Guard 语义分类器（提示注入/密钥检测/内容审核）。花费两人月手工标注 500 个技能构建 ground-truth。结论：26.1% 存在至少一个漏洞，涵盖 14 种模式，四类：提示注入/数据外泄（13.3%）/权限提升（11.8%）/供应链风险。携带可执行脚本的技能漏洞率高 2.12 倍。

---

### 7.2 Malicious Agent Skills in the Wild: A Large-Scale Security Empirical Study

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2602.06547](https://arxiv.org/abs/2602.06547) |
| 发布 | 2026-02-06 |

**核心原理：** 构建首个**已确认恶意技能**的 ground-truth 数据集——通过行为验证（而非静态推断）证明技能的恶意性。从 skills.rest 和 skillsmp.com 收集 98,380 个技能，在隔离 Docker 容器（tcpdump \+ strace \+ auditd \+ 蜜罐凭证）中动态执行 4,287 个候选。在 157 个确认恶意技能（632 个漏洞）中识别出两种攻击原型：
- ① **Data Thieves**（通过供应链技术外泄凭证）
- ② **Agent Hijackers**（通过指令操纵颠覆 Agent 决策）。使用适配 MITRE ATT\&CK 框架（6 个攻击阶段）组织攻击行为。

---

### 7.3 SkillProbe: Security Auditing for Emerging Agent Skill Marketplaces via Multi-Agent Collaboration

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.21019](https://arxiv.org/abs/2603.21019) |
| 服务 | [skillhub.holosai.io](https://skillhub.holosai.io) |
| 发布 | 2026-03（ClawHub 数据截至 2026-03-16） |

**核心原理：** **"Skills-for-Skills"范式——将审计流程本身封装为标准技能模块，由专业化 Agent 驱动执行。三阶段流水线：
- ① 准入过滤（快速排除明显良性技能）
- ② 语义-行为对齐检测（检查 SKILL.md 声明的能力与实际代码行为是否一致）；③ 组合风险仿真（模拟技能在协作调用链中的涌现攻击）。在 2,500 个 ClawHub 真实技能上评估 8 个主流 LLM 系列。揭示流行度-安全性悖论**：下载量不是安全质量的可靠代理，90% 以上高人气技能未通过严格审计。发现高风险技能在风险链接维度形成**单一巨大连通分量**，表明级联风险是系统性而非孤立的。

---

### 7.4 SkillSieve: A Hierarchical Triage Framework for Detecting Malicious AI Agent Skills

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.06550](https://arxiv.org/abs/2604.06550) |
| 发布 | 2026-04-08 |

**核心原理：** 三层递进检测框架，**渐进加深分析深度、仅在必要时调用更昂贵的分析层**：

- **Layer 1**（零 API 成本）：正则表达式 \+ AST \+ 元数据特征 → XGBoost 分类器，平均 \<40ms，过滤约 86% 良性技能；  
- **Layer 2**（单 LLM）：将分析拆分为四个并行子任务（意图对齐/权限合理性/隐蔽行为/跨文件一致性），各有独立 prompt 和结构化输出；  
- **Layer 3**（三 LLM 陪审团）：高风险技能由三个不同 LLM 独立投票，意见不一致时展开辩论再裁决。

在 49,592 个真实 ClawHub 技能 \+ 五种规避技术对抗样本上评估，F1=0.800（vs ClawVet 的 0.421），平均成本 $0.006/技能，全套流程可在 $440 单板计算机上运行。代码/数据/基准开源。

---

### 7.5 SkillTester: Benchmarking Utility and Security of Agent Skills

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2603.28815](https://arxiv.org/abs/2603.28815) |
| 服务 | [skilltester.ai](https://skilltester.ai) |
| GitHub | [skilltester-ai/skilltester](https://github.com/skilltester-ai/skilltester) |
| 发布 | 2026-03-28 |

**核心原理：** 效用和安全**双轨评估**框架，方法论核心是**对照原则**（Comparative Utility Principle）：始终以无技能执行作为参照条件衡量技能贡献价值（而非绝对评分）。评估产出三个标准化指标：效用分数、安全分数和三级安全状态标签（绿/黄/红）。安全探针按三个方向组织（异常行为控制/权限边界/敏感数据保护），并与 OWASP Top 10 for Agentic Applications 2026 对应。提供公开 SaaS 服务和开源框架，可嵌入 CI/CD 流水线实现持续 Skill 质量保障。

---

### 7.6 Towards Secure Agent Skills: Architecture, Threat Taxonomy, and Security Analysis

| 字段 | 内容 |
| :---- | :---- |
| arXiv | [2604.02837](https://arxiv.org/abs/2604.02837) |
| 发布 | 2026-04-03 |

**核心原理：** 第一篇对 Agent Skills 框架进行**全面系统安全分析**的论文。定义四阶段生命周期（创建/分发/部署/执行），识别每阶段结构性攻击面。构建包含**七类别、十七场景、三攻击层**的威胁分类法，以五个已确认安全事件进行验证（包括 Mitiga Labs 2026-02 演示的无声代码库外泄攻击——仅需四次用户交互，skill-audit.log 完全空白）。核心发现：最严重威胁来自框架**结构属性**本身（数据-指令边界缺失、单次审批持久信任模型、市场缺乏强制安全审查），无法通过渐进式缓解措施解决。

---

## 八、通用自进化 Agent 论文（3 篇）

---

### 8.1 DGM-Hyperagents: Metacognitive Self-Modification

| 来源 | [evoailabs Medium](https://evoailabs.medium.com/self-evolving-agents-open-source-projects-redefining-ai-in-2026-be2c60513e97) | | 发布 | 2026 年上半年 |

**核心原理：** 将任务 Agent 和元 Agent 整合为**单一可编辑程序**（Self-Referential Agent）。关键：**元级修改过程本身也是可编辑的**——实现元认知自修改，不仅改善任务求解行为，还改善产生未来改进的机制。通过允许改进过程本身进化，消除对任务性能与自修改能力之间领域特定对齐的假设。跨编程/论文评审/机器人奖励设计/数学评分多元领域持续提升性能。

---

### 8.2 CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended Discovery

| 来源 | [VoltAgent awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) | | 发布 | 2026 年上半年 |

**核心原理：** 引入长时运行的多 Agent 系统，通过**共享持久记忆**（多 Agent 写入同一知识库）、**异步执行**（Agent 独立运行不阻塞彼此）和**心跳式干预**（定期检查并按需重启失效 Agent）实现自进化。在 10 个数学/算法/系统任务上比固定进化搜索基线高出 3–10 倍改进率。

---

### 8.3 EvoFSM: Controllable Self-Evolution with Finite State Machines

| 来源 | [VoltAgent awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) | | 发布 | 2026 年上半年 |

**核心原理：** 进化\*\*显式有限状态机（FSM）\*\*而非自由形式的代码重写——将流程优化和技能优化约束在结构化表示中，提供可控可验证的自进化能力。FSM 的状态转移可审计，与黑箱自修改相比提供更好的可解释性和安全性保证。

---

## 九、工程项目（6 个）

---

### 9.1 SkillNet Platform（zjunlp/SkillNet）

| GitHub | [zjunlp/SkillNet](https://github.com/zjunlp/SkillNet) | | 技能库 API | [http://api-skillnet.openkg.cn/v1/search](http://api-skillnet.openkg.cn/v1/search) |

类似 AI 能力的 npm，提供端到端工具搜索/安装/创建/评估/组织技能。与 JiuwenClaw/OpenClaw 原生集成，MCP 服务器已发布（pip install skillnet-ai）。技能图谱动态更新，关系随任务分布、执行反馈和环境变化持续修订。

---

### 9.2 SkillClaw Platform（AMAP-ML/SkillClaw）

| GitHub | [AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw) |

多用户集体进化平台，Client Proxy 拦截 Agent 请求、记录 session 产物并管理本地技能库；Evolve Server 读取共享存储 session 数据、进化或创建技能后写回。支持两种引擎：workflow（固定三阶段 LLM 流水线）和 agent（OpenClaw 驱动的 Agent 工作空间，直接编辑技能）。与 Hermes/Codex/Claude Code/OpenClaw/QwenPaw 等原生集成。

---

### 9.3 anthropics/skills（Anthropic 官方技能库）

| GitHub | [anthropics/skills](https://github.com/anthropics/skills) | | 文档 | [platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) |

包含 skill-creator 元技能及官方预构建技能（pptx/xlsx/docx/pdf）。skill-creator 内置触发率评估脚本，支持 Claude API 中的 `skill_id` 引用和自定义技能上传（/v1/skills 端点）。

---

### 9.4 DeerFlow RFC（bytedance/deer-flow \#1865）

| GitHub Issue | [bytedance/deer-flow \#1865](https://github.com/bytedance/deer-flow/issues/1865) | | 发布 | 2026-04-05 |

在 DeerFlow（LangGraph \+ 中间件链 \+ Markdown 技能架构）中集成技能自进化机制的 RFC。Agent 基于任务经验自主创建/修补/编辑技能，将成功方法转化为可复用过程性记忆。每个技能目录有自己的 HISTORY.jsonl（追加式，prev\_content 字段支持回滚），与 SkillClaw 正在探讨跨框架技能共享。

---

### 9.5 SkillsBench（官方评测平台）

| 项目页 | [skillsbench.ai](https://www.skillsbench.ai) | | GitHub | （随论文发布）|

基于 Harbor 框架的容器化评估环境，提供确定性验证器和完整轨迹日志。当前 Skill Auto-Creation/Evolution 研究的标准评测基准，CoEvoSkills/EvoSkill 等均在此验证结果。

---

### 9.6 SkillProbe SaaS（安全审计服务）

| 服务 | [skillhub.holosai.io](https://skillhub.holosai.io) |

SkillProbe 框架的公开 SaaS 服务，提供多 Agent 协作的技能安全审计，OpenClaw 插件可在 LLM 环境内通过轻量脚本触发审计工作流并检索结构化结果，无需复杂宿主环境配置。

---

## 十、核心对比矩阵（完整版）

| 论文/项目 | 月份 | 核心范式 | 技能表示 | 进化信号 | 需GT标注 | 跨模型迁移 | arXiv/链接 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CASCADE | Jan | 科学领域累积创建 | 可执行包 | 网搜+反思 | 否 | 是 | [2512.23880](https://arxiv.org/abs/2512.23880) |
| CUA-Skill | Feb | 桌面参数化技能库 | 参数化图 | 人工工程 | — | 是 | [2601.21123](https://arxiv.org/abs/2601.21123) |
| MCE | Jan | CE元进化 | CE工作流 | 双层crossover | 否 | 是 | [2601.21557](https://arxiv.org/abs/2601.21557) |
| Skills-in-Wild | Jan | 安全基线研究 | — | 静态+语义分析 | 是 | — | [2601.10338](https://arxiv.org/abs/2601.10338) |
| SkillsBench | Feb | 基准评估 | SKILL.md | 确定性验证器 | 是 | 7配置 | [2602.12670](https://arxiv.org/abs/2602.12670) |
| Agent Skills Survey | Feb | 架构综述 | 全类型 | — | — | — | [2602.12430](https://arxiv.org/abs/2602.12430) |
| Malicious Skills | Feb | 恶意技能基准 | — | 行为动态验证 | 是 | — | [2602.06547](https://arxiv.org/abs/2602.06547) |
| SkillRL | Feb | RL技能蒸馏 | 提示级 | RL奖励 | 是 | 一定 | [2602.08234](https://arxiv.org/abs/2602.08234) |
| SoK Agentic | Feb | 全面综述 | 全类型 | — | — | — | [2602.20867](https://arxiv.org/abs/2602.20867) |
| AutoSkill | Mar | 个性化提示模板 | 提示模板 | 对话轨迹 | 否 | 是(跨用户) | [2603.01145](https://arxiv.org/abs/2603.01145) |
| SkillCraft | Mar | 在线技能习得基准 | 工具组合 | 任务执行 | 否 | 是 | [2603.00718](https://arxiv.org/abs/2603.00718) |
| EvoSkill(Alzubi) | Mar | 失败分析驱动发现 | 结构化目录 | Failure+GT | 是(GT需要) | 是(冻结) | [2603.02766](https://arxiv.org/abs/2603.02766) |
| AgentSkillOS | Mar | 生态编排管理 | 能力树 | 任务执行 | 否 | 是 | [2603.02176](https://arxiv.org/abs/2603.02176) |
| SkillNet | Mar | 大规模知识图谱 | 图谱节点 | 本体+执行 | 否 | 是 | [2603.04448](https://arxiv.org/abs/2603.04448) |
| SWE-Skills-Bench | Mar | SWE专项基准 | SKILL.md | 确定性pytest | 是 | 多配置 | [2603.15401](https://arxiv.org/abs/2603.15401) |
| ARISE | Mar | RL层次技能进化 | 推理策略 | RL层次奖励 | 是(可验证) | 2模型 | [2603.16060](https://arxiv.org/abs/2603.16060) |
| SkillRouter | Mar | 大规模精准路由 | SKILL.md | 检索评估 | 是 | 4模型 | [2603.22455](https://arxiv.org/abs/2603.22455) |
| Trace2Skill | Mar | 并行轨迹蒸馏 | SKILL.md目录 | 并行轨迹池 | 否 | 跨尺度 | [2603.25158](https://arxiv.org/abs/2603.25158) |
| SkillTester | Mar | 效用+安全双轨评测 | SKILL.md | 对照执行+探针 | 是(有限) | 是 | [2603.28815](https://arxiv.org/abs/2603.28815) |
| SkillReducer | Mar | Token效率优化 | SKILL.md | 压缩+评估 | 否 | 是 | [2603.29919](https://arxiv.org/abs/2603.29919) |
| SkillProbe | Mar | 多Agent安全审计 | SKILL.md | 语义-行为对齐 | 否 | 8系列 | [2603.21019](https://arxiv.org/abs/2603.21019) |
| Secure Skills | Apr | 威胁分类法 | 全类型 | 安全事件分析 | — | — | [2604.02837](https://arxiv.org/abs/2604.02837) |
| CoEvoSkills | Apr | 协同进化验证 | 多文件包 | Surrogate Verifier | 否 | 8 LLM | [2604.01687](https://arxiv.org/abs/2604.01687) |
| Wild Skills | Apr | 真实场景测评 | SKILL.md | 检索+精炼 | 否 | 3模型 | [2604.04323](https://arxiv.org/abs/2604.04323) |
| SkillX | Apr | 三层次知识库 | 3级层次 | 执行+探索扩展 | 否 | 强→弱迁移 | [2604.04804](https://arxiv.org/abs/2604.04804) |
| SkillSieve | Apr | 三层分级检测 | SKILL.md | 静态+LLM+陪审 | 是(标注集) | 多LLM | [2604.06550](https://arxiv.org/abs/2604.06550) |
| SkillClaw | Apr | 多用户集体进化 | SKILL.md | 多用户轨迹 | 否 | 跨用户 | [2604.08377](https://arxiv.org/abs/2604.08377) |
| SkillMOO | Apr | 多目标优化进化 | 多文件包 | 通过率+成本 | 否 | 是 | [2604.09297](https://arxiv.org/abs/2604.09297) |

---

## 十一、安全研究专项对比

| 论文 | 方法范式 | 数据规模 | 关键指标 | 检测能力上限 |
| :---- | :---- | :---- | :---- | :---- |
| Skills-in-Wild (SkillScan) | 静态+语义多阶段 | 42,447 技能 | 86.7% P / 82.5% R | 静态可见漏洞 |
| Malicious Skills | 行为动态验证 | 98,380 技能 | Cohen's κ=0.91 | 确认恶意行为 |
| SkillProbe | 多Agent+组合风险仿真 | 2,500 真实技能 | — | 涌现级联攻击 |
| SkillSieve | 三层分级检测 | 49,592 技能 | F1=0.800, $0.006/技能 | 5种规避技术 |
| SkillTester | 对照+安全探针 | 个体技能评估 | 效用/安全双分数 | OWASP Top 10 对齐 |
| Secure Skills | 威胁分类法 | 5个安全事件验证 | 7类17场景 | 框架结构性缺陷 |

---

## 十二、三大维度核心对比

### 维度一：自动创建方法的信号来源

| 方法 | 信号来源 | 优势 | 劣势 |
| :---- | :---- | :---- | :---- |
| EvoSkill (Alzubi) | Ground-truth 失败轨迹 | 诊断精确 | 依赖标注，成本高 |
| CoEvoSkills | Surrogate Verifier（无GT） | 真实部署友好 | Surrogate 可能引偏 |
| Trace2Skill | 并行轨迹池（全局视野） | 跨模型迁移强 | 需大规模轨迹 |
| SkillX | 执行反馈+探索扩展 | 覆盖范围超训练分布 | 强骨干 Agent 要求较高 |
| SkillClaw | 多用户异质交互 | 集体智能，零额外操作 | 冷启动需用户量 |
| SkillMOO | 通过率+成本双目标 | 同时优化性能和成本 | 目前仅验证 SE 场景 |
| AutoSkill | 用户对话偏好 | 个性化精准 | 轻量模板，不可执行 |

### 维度二：Skill 表示粒度的演进

提示模板（AutoSkill）

    ↓ 可执行单文件（早期 SKILL.md）

        ↓ 多文件结构化包（CoEvoSkills、SkillX）

            ↓ 三层次层级（战略/功能/原子，SkillX）

                ↓ 知识图谱（组合/依赖/相似，SkillNet）

粒度越高，迁移性和组合性越强，但生成难度和维护成本也越高。

### 维度三：进化范围

| 范围 | 代表方法 | 特点 |
| :---- | :---- | :---- |
| 单任务进化 | EvoSkill, CoEvoSkills | 针对特定 Skill 深度优化 |
| 跨任务迁移 | Trace2Skill, SkillX | 技能泛化到新任务/模型 |
| 个人终身学习 | AutoSkill | 跨会话个性化积累 |
| 多用户集体进化 | SkillClaw | 跨用户知识汇聚 |
| 生态系统级管理 | AgentSkillOS, SkillNet | 大规模技能治理 |

---

## 十三、关键数字汇总

| 指标 | 数值 | 来源 |
| :---- | :---- | :---- |
| 精心策划 Skill 平均提升 | \+16.2 pp | SkillsBench |
| 医疗领域最高提升 | \+51.9 pp | SkillsBench |
| 自生成 Skill 平均效果 | \-1.3 pp（无益） | SkillsBench |
| SWE 专项场景 Skill 增益 | \+1.2%（80% 技能无效） | SWE-Skills-Bench |
| CoEvoSkills 超越人工 | 5 轮内 | CoEvoSkills |
| Trace2Skill 跨模型提升 | \+57.65 pp | WikiTableQuestions |
| SkillClaw 6轮后提升 | \+88.41%（相对） | Creative Synthesis |
| SkillMOO 通过率提升 | 最高 \+131% | SkillsBench SE |
| SkillReducer 压缩率 | 描述-48%，主体-39% | SkillReducer |
| Terminal-Bench 2.0 增益 | 57.7%→65.5% | Wild Skills |
| CASCADE 科学任务 | 93.3%（vs 35.4%） | SciSkillBench |
| SkillNet 技能规模 | 200,000+ | SkillNet |
| 公开可用 Skill 总数（2026-02） | 280,000+ | AgentSkillOS |
| ClawHub 技能安全漏洞率 | 13–26% | SkillSieve / SkillProbe |
| SkillSieve 检测 F1 | 0.800 | SkillSieve |
| 大规模研究漏洞率 | 26.1%（14种模式） | Skills-in-Wild |

---

## 十四、总结：三条关键研究主线与研究者注意事项

### 主线 A：创建范式之争——"无监督进化"是终极目标

SkillsBench 证明模型无法单次自生成好 Skill → 迫使研究转向进化路径 → EvoSkill 依赖 GT 标注 → CoEvoSkills 用 Surrogate Verifier 打破 GT 依赖 → **核心问题**：如何在无任何外部监督信号下实现高质量技能生成，是下一轮竞争的关键。

### 主线 B：粒度演进——从"提示"到"知识图谱"

Skill 表示正从单文件提示模板，经多文件结构化包、三层次层级，向可查询知识图谱演进。SkillNet 的 compose/depend\_on 关系是方向先驱。下一代技能系统需要解决图谱上的自动技能布线（SkillRouter 问题）与技能版本管理问题。

### 主线 C：安全治理——"Auto-Evolution \+ 开放市场 \= 高风险组合"

26.1% 漏洞率（静态分析）+ 流行度不代表安全（SkillProbe）+ 级联风险系统性（SkillProbe 单一连通分量）= **Skill 安全是生产部署的硬门槛**。SkillSieve（检测）+ SkillTester（评估）+ Secure Skills（框架设计）是当前三条防线，但 Secure Skills 指出：最严重的威胁源于框架结构属性本身（数据-指令边界缺失），无法通过缓解措施根本解决。

**对 SkillBench/EvalClaw 系统的直接启示：** 进化信号设计（Surrogate Verifier 模式）+ 多维评估（效用/安全/迁移性）+ 安全验证门控（G1-G4 信任等级）的三位一体架构，正好填补当前生态中最稀缺的空白。

---

## 附录：完整论文索引（含链接）

| \# | 简称 | arXiv/链接 | 月份 |
| :---- | :---- | :---- | :---- |
| 1 | CUA-Skill | [2601.21123](https://arxiv.org/abs/2601.21123) | Jan |
| 2 | MCE | [2601.21557](https://arxiv.org/abs/2601.21557) | Jan |
| 3 | Skills-in-Wild (SkillScan) | [2601.10338](https://arxiv.org/abs/2601.10338) | Jan |
| 4 | CASCADE | [2512.23880](https://arxiv.org/abs/2512.23880) | Jan(v2) |
| 5 | Malicious Skills | [2602.06547](https://arxiv.org/abs/2602.06547) | Feb |
| 6 | SkillRL | [2602.08234](https://arxiv.org/abs/2602.08234) | Feb |
| 7 | SkillsBench | [2602.12670](https://arxiv.org/abs/2602.12670) | Feb |
| 8 | Agent Skills Survey | [2602.12430](https://arxiv.org/abs/2602.12430) | Feb |
| 9 | SoK Agentic Skills | [2602.20867](https://arxiv.org/abs/2602.20867) | Feb |
| 10 | AutoSkill | [2603.01145](https://arxiv.org/abs/2603.01145) | Mar |
| 11 | SkillCraft | [2603.00718](https://arxiv.org/abs/2603.00718) | Mar |
| 12 | EvoSkill (Alzubi) | [2603.02766](https://arxiv.org/abs/2603.02766) | Mar |
| 13 | AgentSkillOS | [2603.02176](https://arxiv.org/abs/2603.02176) | Mar |
| 14 | SkillNet | [2603.04448](https://arxiv.org/abs/2603.04448) | Mar |
| 15 | SWE-Skills-Bench | [2603.15401](https://arxiv.org/abs/2603.15401) | Mar |
| 16 | ARISE | [2603.16060](https://arxiv.org/abs/2603.16060) | Mar |
| 17 | SkillRouter | [2603.22455](https://arxiv.org/abs/2603.22455) | Mar |
| 18 | Trace2Skill | [2603.25158](https://arxiv.org/abs/2603.25158) | Mar |
| 19 | SkillTester | [2603.28815](https://arxiv.org/abs/2603.28815) | Mar |
| 20 | SkillReducer | [2603.29919](https://arxiv.org/abs/2603.29919) | Mar |
| 21 | SkillProbe | [2603.21019](https://arxiv.org/abs/2603.21019) | Mar |
| 22 | Secure Agent Skills | [2604.02837](https://arxiv.org/abs/2604.02837) | Apr |
| 23 | CoEvoSkills | [2604.01687](https://arxiv.org/abs/2604.01687) | Apr |
| 24 | Wild Skills | [2604.04323](https://arxiv.org/abs/2604.04323) | Apr |
| 25 | SkillX | [2604.04804](https://arxiv.org/abs/2604.04804) | Apr |
| 26 | SkillSieve | [2604.06550](https://arxiv.org/abs/2604.06550) | Apr |
| 27 | SkillClaw | [2604.08377](https://arxiv.org/abs/2604.08377) | Apr |
| 28 | SkillMOO | [2604.09297](https://arxiv.org/abs/2604.09297) | Apr |
| 29 | DGM-Hyperagents | [evoailabs Medium](https://evoailabs.medium.com/self-evolving-agents-open-source-projects-redefining-ai-in-2026-be2c60513e97) | 2026 |
| 30 | CORAL | [awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) | 2026 |
| 31 | EvoFSM | [awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers) | 2026 |
| P1 | skill-creator | [anthropics/skills](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) | 官方 |
| P2 | DeerFlow RFC | [deer-flow \#1865](https://github.com/bytedance/deer-flow/issues/1865) | Apr |
| P3 | SkillNet Platform | [zjunlp/SkillNet](https://github.com/zjunlp/SkillNet) | Mar |
| P4 | SkillClaw Platform | [AMAP-ML/SkillClaw](https://github.com/AMAP-ML/SkillClaw) | Apr |
| P5 | SkillsBench Platform | [skillsbench.ai](https://www.skillsbench.ai) | Feb |
| P6 | SkillProbe SaaS | [skillhub.holosai.io](https://skillhub.holosai.io) | Mar |

---

*by skyseraph + AI 2026.4*  