---
title: "SkVM 深度解析：为 LLM Agent Skills 构建的编译与运行时系统"
date: 2026-04-26T22:59:00+08:00
categories: ["技术"]   # 技术 / 随笔 / 项目
tags: ["Skill"]
pin: false
toc: true
draft: false
---

# SkVM 深度解析：为 LLM Agent Skills 构建的编译与运行时系统

> 作者：skyseraph    
> 日期：2026-04-26    
> 原文链接：[SkVM 深度解析](https://skyseraph.github.io/posts/2026/skvm/)    
> 参考论文：[SkVM: Revisiting Language VM for Skills across Heterogenous LLMs and Harnesses](https://arxiv.org/abs/2604.03088)    
> 开源代码：[SkVM](https://github.com/SJTU-IPADS/SkVM/)    
> 开源工具：[SkillNexus](https://github.com/skyseraph/SkillNexus)  


---

## 一、背景与问题

在 LLM Agent 工程实践中，有一个长期被忽视但极其棘手的问题：**Skill 的可移植性**。

一个在 Claude Sonnet 4.6 上运行流畅的 Agent Skill，换到 Qwen3-35B 上可能错误百出；一套针对 OpenClaw 写好的指令集，迁移到 Hermes Agent 后往往需要大量手工调整。这背后的根因是：不同的 LLM 在代码生成、推理、工具调用、指令遵从等维度上能力参差不齐，不同的 Agent 框架在工具集、沙箱环境、交互协议上也各自为政。

这个问题的本质，和传统计算机体系结构中的**ISA（指令集架构）移植性问题**高度同构：

- 高级语言（Skill 指令）需要编译到具体硬件（LLM + Harness）
- 不同的目标平台能力不同，需要针对性的代码生成
- 运行时需要 JIT 优化来弥补静态分析的不足

**SkVM（Skill Virtual Machine）** 正是从这个类比出发，构建了一套完整的 LLM Skill 编译与运行时系统。

---


## 二、核心原理：语言 VM 的类比

SkVM 的核心设计哲学是将 **LLM + Agent Harness 的组合**类比为计算机体系结构中的"硬件平台"，将 **Agent Skill（一组 Markdown 指令 + 配套脚本）**类比为"高级语言程序"。

```
传统编译体系                    SkVM 类比
─────────────────────────────────────────────────────
高级语言代码                    Skill（SKILL.md + 脚本）
目标硬件平台                    LLM 模型 + Agent Harness
ISA / ABI                       Primitive 能力目录（26 个原语）
编译器                          AOT Compiler（3 pass）
性能分析                        Profiler（TCP 生成）
JIT 编译器                      JIT-Boost + JIT-Optimize
```

这个类比不是噱头，而是整个系统设计的骨架——每个子系统的存在都有其在传统 VM 体系中的对应角色。

---


## 三、系统架构

### 3.1 整体数据流

```
Profile Tool ──TCP──> AOT Compiler ──Variant──> Runtime + Agent
     │                    │                         │
 26 primitives         3 passes               JIT-boost + JIT-optimize
 L1 → L2 → L3        1: capability gaps       - code solidification
                     2: env binding           - skill content improvement
                     3: concurrency DAG       - headless optimizer loop
```

整个系统分为三个相互独立、可单独使用的层：

1. **Profile 层**：测量目标 LLM + Harness 的能力，生成 TCP（Target Capability Profile）
2. **Compile 层**：基于 TCP 编译 Skill，生成针对目标平台优化的 Variant
3. **Optimize 层**：运行时 JIT 优化，包括代码固化（Boost）和内容改进（Optimize）

### 3.2 代码结构

```
src/
├── index.ts            # CLI 入口，手写 flag 解析器
├── core/               # 共享基础：类型、配置、日志、并发、headless agent
├── providers/          # LLM 后端（Anthropic SDK、OpenRouter）
├── adapters/           # 5 种 Agent Harness 适配器
├── profiler/           # 26 个微基准测试生成器 + 运行器
├── compiler/           # 3-pass AOT 编译器
├── runtime/            # RuntimeHooks 接口定义
├── jit-boost/          # 运行时代码固化
├── jit-optimize/       # 基于 Proposal 的 Skill 内容优化循环
├── proposals/          # Proposal 存储与部署管理
├── framework/          # 任务运行器 + 评估引擎（profiler 和 bench 共用）
└── bench/              # 基准测试编排器
```

---

## 四、核心模块深度解析

### 4.1 Profiler：建立能力基线

Profiler 是整个系统的"侦察兵"。它的核心工作是：**用 26 个预定义的微基准测试，测量目标 LLM + Harness 组合在各原语上的能力等级**，最终生成 TCP（Target Capability Profile）。

#### 26 个 Primitive 原语目录

这 26 个原语按照 4 个大类组织：

| 大类 | 原语示例 | 说明 |
|------|----------|------|
| **Generation（生成）** | `gen.code.python`, `gen.code.bash`, `gen.text.summary` | 代码生成、文本生成能力 |
| **Reasoning（推理）** | `reason.logic`, `reason.math`, `reason.plan` | 逻辑推理、数学计算、规划能力 |
| **Tool Use（工具调用）** | `tool.file.read`, `tool.file.write`, `tool.shell.exec` | 文件操作、命令执行 |
| **Instruction Following（指令遵从）** | `follow.format`, `follow.constraint`, `follow.multi-step` | 格式遵从、约束遵从、多步指令 |

每个原语有 3 个能力等级（L1/L2/L3），对应从简单到复杂的任务难度。

#### 两种评估模式

- **工具调用型原语**（`gen.code.*`、`tool.*`）：Agent 实际运行工具，评估脚本检查 `workDir` 中的文件结果
- **纯文本型原语**（`reason.*`、`follow.*`、`gen.text.*`）：Profiler 把 LLM 响应写入 `response.txt`，脚本读取并评分

评估脚本统一使用 `python3 << 'PYEOF'` heredoc 模式，规避 shell 引号转义问题。

#### TCP 输出格式

```json
{
  "model": "anthropic/claude-sonnet-4-6",
  "adapter": "bare-agent",
  "primitives": {
    "gen.code.python": "L3",
    "reason.math": "L2",
    "tool.file.write": "L3",
    "follow.constraint": "L1"
  }
}
```

> 关键设计决策：TCP 是模型+harness 组合的属性，不是模型单独的属性。同一个模型在 bare-agent 下和在 OpenClaw 下的 TCP 可能不同，因为工具集和交互协议不同。

### 4.2 AOT Compiler：三遍静态编译

编译器是 SkVM 的核心，它将一个通用 Skill 重写为针对特定目标平台优化的 Variant。编译过程分为三遍，每遍都有明确的职责边界。

#### Pass 1：能力缺口弥补

**输入**：原始 Skill + TCP  
**核心步骤**：
1. **SCR 提取**（LLM 调用）：从 Skill 中提取 Skill Capability Requirements，即这个 Skill 假设目标模型具备哪些能力
2. **缺口分析**（纯计算）：对比 SCR 和 TCP，找出 "Skill 需要 L2 但模型只有 L1" 的原语
3. **Agentic 重写**（LLM 调用）：让 `compiler-agent.ts` 分析每个缺口，决定重写策略——是降级任务复杂度、拆分步骤、还是添加更详细的示例

Pass 1 中只有 SCR 提取和重写两步调用 LLM，缺口分析是纯计算，这是有意为之的设计——缺口分析频繁、确定性强，不适合用 LLM。

#### Pass 2：环境绑定

**职责**：处理 Skill 的外部依赖。  
**步骤**：
1. LLM 从 Skill 中提取依赖清单（dependency manifest）
2. Shell 脚本检查这些依赖在目标环境中是否存在
3. 生成幂等的 `env-setup.sh`，确保 Skill 运行前环境就绪

这一遍解决的是"Skill 假设 `git` 已安装但实际没有"这类环境不匹配问题。

#### Pass 3：并发 DAG 提取

**职责**：从 Skill 的工作流中提取可并行执行的任务图。  
**步骤**：
1. LLM 进行工作流分解，识别步骤间的依赖关系
2. 纯计算构建 DAG（有向无环图）
3. 提取三类并行性：
   - **DLP**（Data-Level Parallelism）：同一操作作用于多个数据项
   - **ILP**（Instruction-Level Parallelism）：独立指令同时执行
   - **TLP**（Task-Level Parallelism）：独立子任务并行运行

最新版本（PR #5）还对 ILP 工具分发做了并行化，进一步提升编译效率。

#### 编译产物位置

```
~/.skvm/proposals/aot-compile/{adapter}/{safeModel}/{skillName}/{passTag}/
```

每个 pass 的产物独立存储，支持增量重编译。

### 4.3 JIT-Boost：运行时代码固化

JIT-Boost 解决的是**运行时效率**问题：当 Agent 在执行 Skill 时反复产生相同模式的工具调用，完全可以用确定性代码替代 LLM 推理，节省 token 和延迟。

#### 工作原理

**候选生成**（`candidates.ts`）：headless agent 分析完整 Skill 目录，识别可能被固化的模式，输出 `boost-candidates.json`：

```json
{
  "candidates": [
    {
      "keywords": ["list files", "directory contents"],
      "codeSignature": "list_directory({path})",
      "functionTemplate": "ls -la {path}",
      "params": ["path"]
    }
  ]
}
```

**运行时监控与提升**（`solidifier.ts`）：
- `afterLLM` hook：监控每次 LLM 工具调用，与代码签名匹配，统计连续命中次数
- `beforeLLM` hook：当连续命中达到阈值（默认 3 次），直接从 prompt 中提取参数、执行模板，**完全绕过 LLM**
- 失败时回退到 LLM，连续失败 M 次（默认 3 次）后降级该候选

这是一个经典的自适应优化策略：观察 → 统计 → 提升 → 验证 → 回退。

```
                  ┌─────────────────────────────┐
beforeLLM ──────> │ 命中阈值？                   │
                  │  是 → 执行模板，跳过 LLM     │
                  │  否 → 正常走 LLM             │
                  └─────────────────────────────┘
afterLLM  ──────> 更新命中计数，管理候选状态
```

### 4.4 JIT-Optimize：基于证据的 Skill 内容改进

JIT-Optimize 是系统中最复杂、最有创意的子系统。它的目标是：**基于真实执行证据，自动改进 Skill 的内容本身**。

#### 三个正交轴

| 维度 | 选项 |
|------|------|
| **任务来源** | `synthetic-task`（LLM 从 Skill 自动推导）/ `real-task`（真实 bench 任务）/ `execution-log`（解析已有对话日志，无需重跑） |
| **循环控制** | rounds 轮数、runsPerTask 每任务跑数、convergence 收敛条件、holdoutTestSet 保留测试集、baseline 基线 |
| **交付方式** | 统一为 Proposal，`keepAllRounds` 控制剪枝，`autoApply` 控制是否自动覆盖原始 Skill |

#### Optimizer 运行协议

这是整个系统中最精妙的设计之一：**Optimizer 本身是一个 Headless Agent**。

```
1. Engine 将 Skill 目录复制到临时工作区
2. 将执行证据 + 历史记录序列化到 .optimize/ 目录（JSON + Markdown）
3. 启动 Headless Agent（默认驱动：opencode），cwd 指向工作区
4. Agent 使用自身工具（read/edit/write/glob/grep/bash）编辑 Skill 文件
5. Agent 将结果写入 .optimize/submission.json：
   {
     "rootCause": "...",  // 必填：诊断出的根本原因
     "reasoning": "...",
     "confidence": 0.85,
     "changedFiles": ["SKILL.md"],
     "changes": {...}
   }
6. Engine 对工作区做快照，计算实际 diff，验证 changedFiles 声明
```

**关键约束**：`rootCause` 字段是强制要求的。Optimizer 必须阐明诊断出的根本问题，而不仅仅描述它做了什么改动。历史记录中保留每轮的 rootCause，避免后续轮次重复同样的失败诊断。

#### Proposal 树结构

```
~/.skvm/proposals/jit-optimize/{harness}/{safeTargetModel}/{skillName}/{timestamp}/
  original/          # 起始 Skill 快照
  round-0/           # 基线（与 original 相同，保持轮次枚举统一）
  round-1/ … round-N/ # 每轮优化后的完整 Skill 目录
  history.json       # HistoryEntry[] + bestRound + bestRoundReason
  analysis.md        # 人类可读摘要
  meta.json          # { status, acceptedRound, bestRound, optimizerModel, … }
  round-N-agent-logs/     # Agent 对话日志
  round-N-optimizer-logs/ # Optimizer NDJSON
```

每个 round 目录都是完整、可用的 Skill 目录，做到了"每轮可独立部署"。

### 4.5 Adapters：统一 Agent Harness 接口

SkVM 通过 `AgentAdapter` 接口屏蔽了不同 Agent 框架的差异，目前支持 5 种适配器：

| 适配器 | 特点 |
|--------|------|
| `bare-agent` | 内置最小化循环，5 个基础工具（`read_file`/`write_file`/`list_directory`/`execute_command`/`web_fetch`），是 profile/test 的主力适配器 |
| `opencode` | 包装 OpenCode CLI，解析 NDJSON 事件流 |
| `openclaw` | 包装 OpenClaw CLI，管理临时 agent 实例 |
| `hermes` | 包装 hermes CLI，解析 session export JSON，支持完整的 token/cost 统计 |
| `jiuwenclaw` | 通过 JSON-RPC 调用 `jiuwenclaw-cli`，token/cost 不在上游持久化 |

每个适配器都支持 `RuntimeHooks`（`beforeLLM`/`afterLLM`/`afterTool`/`afterRun`），JIT-Boost 正是通过这些 hook 注入到任意适配器中。

**两种配置模式**：
- `managed`：SkVM 在沙箱内配置一个全新的 harness 实例，干净基线，无主机状态依赖
- `native`：克隆用户本机已有的 harness 配置，需要本地已安装该 harness

### 4.6 并发调度器：层级式槽位管理

`src/core/concurrency.ts` 实现了一个定制化的层级调度器，用于 `profile` 和 `bench` 的大规模并发任务分配。

核心概念：
- **`Pool`**：并发槽位池，支持跨组的槽位"偷取"（slot stealing）
- **`runScheduled`**：按调度策略分发任务，支持"组内"和"跨组"两种槽位分配
- **`distributeSlots`**：层级化地向 adapter × model × task 三维矩阵分配并发配额

这个调度器使得在大规模基准测试中，空闲的工作单元可以自动"偷取"其他组的任务，最大化硬件利用率。

### 4.7 评估框架：四种评分策略

`src/framework/evaluator.ts` 定义了四种固定的顶层评估方法：

| 方法 | 适用场景 |
|------|----------|
| `script` | Shell 退出码（0=通过，非0=失败） |
| `file-check` | 检查文件内容（精确匹配/包含/正则/JSON schema） |
| `llm-judge` | LLM 作为评委，打分 0-1，适合主观质量评估 |
| `custom` | 注册自定义评估器（`grade.py` 等），通过 `evaluatorId` 分发 |

`llm-judge` 支持 `--async-judge` 模式，在 bench 跑完之后批量异步评分，不阻塞主流程。

---

## 五、关键技术选型

### 5.1 Bun 运行时

SkVM 选择 [Bun](https://bun.sh/) 而非 Node.js，原因包括：
- 内置 TypeScript 支持，无需编译步骤
- `Bun.file()` / `Bun.write()` 比 `node:fs` 更符合人体工学
- 自动加载 `.env` 文件
- 更快的启动速度（CLI 工具中体验明显）

### 5.2 Zod 模式验证

所有跨子系统的 JSON 产物（TCP、SCR、Proposal、日志）都用 Zod schema 定义并验证。类型定义和 schema 定义放在同一文件（`types.ts`），保证类型系统和运行时验证的一致性。

### 5.3 双层结构化输出策略

`providers/structured.ts` 中的 `extractStructured()` 采用两层降级策略：
1. **优先**：使用 `tool_use`（结构化工具调用，Anthropic SDK 原生支持）
2. **降级**：如果模型不支持 tool_use，则 prompt + parse（提示 JSON 格式，然后解析响应）

这使得 SkVM 在 OpenRouter 上的弱模型上也能稳定运行。

### 5.4 `<provider>/` 前缀路由

所有模型 ID 必须携带 `<provider>/` 前缀：
- `anthropic/claude-sonnet-4-6` → Anthropic 原生 SDK
- `openrouter/qwen/qwen3.5-35b-a3b` → OpenRouter（三段式）
- `openai/gpt-4o` → OpenAI 兼容接口

这个设计使 provider 路由完全显式，避免了隐式猜测引发的错误，也让多 provider 混用变得自然。

---

## 六、典型业务流程

### 流程 A：从零到可运行的优化 Skill

```bash
# Step 1：配置向导（一次性）
skvm config init

# Step 2：Profile 目标模型（约 20 分钟，--concurrency 可加速）
skvm profile --adapter=openclaw --model=anthropic/claude-haiku-4-5-20251001

# Step 3：AOT 编译 Skill（3 个 pass 顺序执行）
skvm aot-compile \
  --skill=path/to/my-skill \
  --model=anthropic/claude-haiku-4-5-20251001 \
  --adapter=openclaw \
  --pass=1,2,3 \
  --compiler-model=anthropic/claude-sonnet-4-6

# Step 4：用 JIT-Optimize 自动调优（合成任务模式）
skvm jit-optimize \
  --skill=path/to/my-skill \
  --task-source=synthetic \
  --target-model=anthropic/claude-haiku-4-5-20251001 \
  --optimizer-model=anthropic/claude-sonnet-4-6 \
  --target-adapter=openclaw \
  --rounds=3

# Step 5：Review 并接受最佳 Proposal
skvm proposals serve   # Web UI
skvm proposals accept <id>
```

### 流程 B：从事后日志优化（Post-Mortem）

```bash
# 任务运行完成后，用已有对话日志做分析
skvm jit-optimize \
  --skill=path/to/my-skill \
  --task-source=log \
  --logs=~/.openclaw/sessions/session-xyz.jsonl \
  --target-model=anthropic/claude-haiku-4-5-20251001 \
  --optimizer-model=anthropic/claude-sonnet-4-6 \
  --target-adapter=openclaw
```

### 流程 C：基准测试对比

```bash
# 对比原始、编译后、JIT 优化后三个版本的性能
skvm bench \
  --skill=my-skill \
  --model=anthropic/claude-haiku-4-5-20251001 \
  --adapter=openclaw \
  --conditions=original,aot-compiled,jit-optimized \
  --tasks=all
```

---

## 七、使用案例

### 案例 1：跨模型部署能力降级

**场景**：一个复杂的代码审查 Skill，依赖模型具备 L3 的 `reason.logic` 能力（深度逻辑推理）。但目标部署模型（一个成本更低的开源模型）在该原语上只有 L1。

**SkVM 解法**：
- Profiler 检测到缺口
- Pass 1 编译器将 Skill 改写：将"一步完成的复杂推理"拆分为"多步引导式推理链"，并增加 CoT（Chain-of-Thought）提示
- 编译后的 Variant 在弱模型上的通过率显著提升

### 案例 2：跨 Harness 迁移

**场景**：原本为 OpenClaw 写的 Skill 需要迁移到 Hermes Agent，两者工具集和指令风格不同。

**SkVM 解法**：
- Pass 2 编译器重新绑定环境依赖，处理工具调用 API 差异
- Adapters 层屏蔽 Harness 差异，同一 Skill 可以用不同 adapter 运行

### 案例 3：JIT-Boost 加速重复操作

**场景**：一个文件分析 Skill 在处理每个文件前都会调用 `list_directory`，每次都产生 LLM 推理开销。

**SkVM 解法**：
- JIT-Boost 检测到 `list_directory` 调用连续出现 3 次
- 自动将后续调用固化为直接的 shell 命令执行
- 跳过 LLM，节省 token 和延迟

### 案例 4：数据集规模验证

SkVM 附带的 `skvm-data` 包含：
- **108 个** Skill 目录
- **216 个** 任务目录
- 预建的多模型 TCP profile

可以直接基于这些数据运行系统级基准测试。

---

## 八、体会与思考

### 8.1 "把 LLM 视为硬件"是个深刻的类比

传统软件工程中，抽象硬件差异是整个计算机体系结构的核心任务。SkVM 把这个思路搬到 LLM Agent 领域，不是简单的比喻，而是真正落地的工程实践。

26 个 Primitive 原语目录的设计尤其值得称赞。它将 LLM 能力从"模糊的感知"变成了"可量化的测量"。以前我们说"这个模型推理能力弱"，现在可以说"这个模型在 `reason.logic` 上是 L1"，精确、可重现、可比较。

### 8.2 Agentic Compiler 的范式转移

传统编译器是确定性的符号变换。SkVM 的 Pass 1/2/3 编译器核心步骤都调用 LLM，这意味着编译过程本身是非确定性的。

这带来了一个有趣的工程问题：如何保证编译质量？SkVM 的答案是：
- `guard.ts` 对每个 pass 的输出做 Zod 验证
- 每个 pass 的产物独立存储，失败可以单独重跑
- JIT-Optimize 通过运行时证据弥补编译不足

这是"编译时尽力、运行时修正"的务实工程哲学。

### 8.3 Headless Agent 作为基础设施

SkVM 在多个关键节点（JIT-Boost 候选生成、JIT-Optimize Optimizer）都使用 Headless Agent 来执行复杂分析和编辑任务。

这个选择背后有深刻的工程考量：文件编辑、代码分析、多文件协调——这些任务本来就是 Agent 擅长的。与其自己写一个复杂的文件操作库，不如用一个已经会这些的 Agent。

但这也意味着 Optimizer 本身的质量依赖于底层 Agent Driver 的质量。SkVM 通过 `OptimizeConfig.driver` 将 Driver 抽象化，支持插件化替换（bare-agent/opencode/claude-code），这是正确的解耦方向。

### 8.4 rootCause 的强制要求是工程智慧

在 JIT-Optimize 的 `submission.json` 中，`rootCause` 字段是**强制的**。这个约束看起来很小，但背后的工程智慧不小：

没有 rootCause 的修改是"打补丁"，有 rootCause 的修改是"治根本"。在多轮优化中，历史 rootCause 记录让 Optimizer 在后续轮次可以明确避免"已经试过但没用的方向"，防止无效循环。这是从大量 Agent 工程实践中提炼出来的约束。

### 8.5 可移植性 vs 最优性的权衡

SkVM 的目标是**可移植性**，但这和**在特定平台上的最优性**存在天然张力。

一个为 Claude Sonnet 原生优化的 Skill，未必比经过 SkVM 编译的通用 Skill 更差——但在极端情况下（比如需要非常特定的提示风格），SkVM 的通用化改写可能会牺牲一定性能。

这是所有"中间层"系统都面临的根本权衡。SkVM 的应对策略是：
- 提供 JIT-Optimize 做运行时弥补
- 保留每轮产物，让用户可以选择接受哪一轮
- 提供完整的基准测试系统，让数据说话

### 8.6 从论文到工程的落地

SkVM 背后有 [arXiv 论文](https://arxiv.org/abs/2604.03088) 支撑，但代码库本身的工程质量独立于论文评价。几个值得学习的工程点：

- **TypeScript + Bun，no build step**：降低贡献门槛，减少工程摩擦
- **Zod schema 作为系统边界**：所有跨模块数据结构强制验证，减少运行时惊喜
- **`src/adapters/registry.ts` 单一注册点**：新增 Adapter 只需在一个文件中注册，避免分散修改
- **Cache root 全局共享，可覆盖**：`~/.skvm/` 在所有目录下共享，同时支持 `SKVM_CACHE` 覆盖，兼顾便利性和灵活性

---

## 九、总结

SkVM 是一个在 LLM Agent 工程领域思路非常新颖的系统。它把传统计算机体系结构中"编译 → 运行时优化"的完整体系移植到了 Skill 的生命周期管理上，每个子系统都有清晰的职责和良好的解耦。

**对于 Agent 工程师**，SkVM 提供了一套系统化解决"Skill 可移植性"问题的工具链，从量化能力（Profiler）到自动适配（Compiler）再到持续改进（JIT-Optimize），覆盖了 Skill 全生命周期。

**对于系统设计者**，SkVM 展示了如何将传统系统软件的设计范式——能力抽象、静态分析、动态优化、中间表示——迁移到以 LLM 为核心的新型计算范式中。

未来最值得期待的方向，或许是 Skill 之间的依赖管理和版本化——类似包管理器，当一个 Skill 依赖另一个 Skill 的输出时，SkVM 能否自动管理这些组合的兼容性？这将是让 SkVM 从工具变成生态的关键一步。

---

*By SkySeraph 2026.4，本文基于 SkVM 开源代码库（主分支，2026-04-26），结合源码阅读与实践体会。*


- [SkVM 深度解析：为 LLM Agent Skills 构建的编译与运行时系统](https://mp.weixin.qq.com/s/xKn5XVgsqhJiQ0tCG1gpug)