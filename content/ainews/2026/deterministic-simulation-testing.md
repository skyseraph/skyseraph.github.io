---
title: "把时钟、网卡、磁盘换成 tick：确定性模拟测试让分布式 bug 必然复现——种子化故障与六条军规"
date: 2026-11-17T08:00:00+08:00
event: "paper"
cover: ""
video: ""
source: "https://martinfowler.com/articles/deterministic-simulation-testing.html"
sourceName: "martinfowler.com"
summary: "martinfowler.com 刊发确定性模拟测试长文：tick 驱动模拟替换真实硬件，让分布式 bug 必然复现。"
ainewstags: ["分布式系统", "确定性模拟", "验证Verify"]
featured: false
draft: false
---

## 摘要

2026-11-17，Thoughtworks 杰出工程师 Unmesh Joshi（《Patterns of Distributed Systems》作者）在 martinfowler.com 发表长文，系统讲解确定性模拟测试（Deterministic Simulation Testing，DST），并开源了教学用 Java 实现 Tickloom。但真正值得写的不在"又一种测试方法"里，而在三处细节：其一，时钟、线程调度、网络时序、磁盘时序这四个不确定性来源被统一替换为显式的 `tick()` 调用——谁推动时间，谁就拥有复现；其二，一个文件只用 `visible` / `durable` 两个 byte 数组，就把崩溃后的数据丢失语义完整模拟出来；其三，六条编码军规不靠开发者自觉，而是用 ArchUnit 静态检查加运行时线程归属校验强制执行。

这篇文章拆三件事：DST 与混沌工程、Jepsen 的分界线；Tickloom 的实现机制与代价；这套方法的前提条件、行业采用与适用边界。

## 原文核心观点

**1. 分布式系统最难测的 bug 不在组件里，而在灰失败的交错中。** 单元测试验证局部逻辑，集成测试验证组件交互，但都不能证明"部分失败撞上在途请求"时客户端看到什么。生产环境组件很少干净地失败：网络不是干净地分区，而是非对称路由、选择性丢包、恰好触发一侧超时的延迟；进程不是崩溃，而是一次刚好错过共识心跳的 GC 停顿；磁盘不是坏掉，而是 WAL 同步从 2ms 变 500ms 的局部延迟尖峰。

> *"the hardest bugs do not live inside the isolated components; they live in the unpredictable interactions between the components and the infrastructure where partial failures and live traffic overlap."*
> — Unmesh Joshi, Deterministic Simulation Testing, martinfowler.com

**2. 可用不等于正确，混沌工程与 Jepsen 各测一半。** 混沌工程问"杀掉一个节点后系统还可用吗"；Jepsen 从客户端视角记录操作历史，检查其是否符合系统声称的语义——一个分区期间 Bob 从旧副本读到已确认写入之前的值，系统全程"可用"，但一致性保证已破。

> *"But availability is not the same as correctness."*
> — 同上

**3. 找到 bug 只完成一半，复现才是墙。** 活体测试有两层不可复现：未种子化的故障调度（每次运行的故障序列都不同）和执行不确定性（即使故障序列相同，GC 停顿、线程切换、迟到的 TCP ACK 仍会改变故障命中瞬间的在途消息集合）。同一个隔离 Cyrene 的故障，Run 1 确认及时到达写成功，Run 2 确认延迟到达写超时——两条路径都不算错，但没有任何东西决定你拿到哪一条。

<img src="https://martinfowler.com/articles/deterministic-simulation-testing/deterministic_runs_vary.svg" alt="同一个注入故障的两次运行产生不同执行轨迹：Run 1 确认按时到达，Run 2 协调者在延迟的确认到达前超时" style="max-width:100%;border-radius:6px;background:#fff;" />
<p style="text-align:center;font-size:0.85em;color:#888;">原文 Figure 4：同一注入故障的两次运行，执行轨迹分岔。bug 若只在 Run 2 路径上，重跑可能永远落在 Run 1。</p>

> *"Even with the exact same sequence of faults, the system is still not guaranteed to produce the same execution."*
> — 同上

**4. 核心机制：把整个集群跑在单线程上，没有任何东西自行前进。** 四大不确定性来源各自对应一个被测试接管的控制点：时钟读到测试推进到的值；整个集群单线程运行、按固定顺序执行进程；消息只在网络被 tick 时投递；写只在磁盘被 tick 时变得持久。

> *"Nothing progresses on its own. The test controls when each component executes and delivers its work."*
> — 同上

<img src="https://martinfowler.com/articles/deterministic-simulation-testing/simulated_components_tick.svg" alt="模拟环境中测试显式驱动时钟、进程、网络、磁盘的推进（代码中建模为 tick 调用）" style="max-width:100%;border-radius:6px;background:#fff;" />
<p style="text-align:center;font-size:0.85em;color:#888;">原文 Figure 10：真实系统中 CPU、网卡、磁盘各自前进；模拟系统中一切推进都由测试的 tick 显式驱动。</p>

**5. 种子化故障注入让"随机探索"与"精确复现"同时成立。** 探索巨大故障交互状态空间靠随机注入，但随机数生成器带种子：同一种子产生同一故障序列，同一故障序列产生同一客户端可见结果。seed 42 出现的 bug，重跑 seed 42 必然重现。

> *"The same seed produces the same sequence of faults, and the same sequence of faults produces the same client visible results. If a bug shows up for seed 42, running seed 42 again reproduces it."*
> — 同上

**6. 快进执行改变了故障测试的时间经济学。** 活体集群要看一秒超时就要真等一秒，数千次组合试验累积成天的真实时间；模拟中 100 个 tick 就是驱动循环的 100 次迭代，以 CPU 速度运行。回放帮助修复 bug，快进帮助发现 bug。

> *"Replay helps after a bug is found. Fast-forward helps find it in the first place."*
> — 同上

**7. 正确性检查沿用 Jepsen 范式：客户端可见历史 + 一致性检查器。** 运行结束后把 invoke/ok/fail 历史交给检查器验证线性一致性；发现违例时，产生它的种子足以重现确切执行，开发者可以逐步回放导致 bug 的 tick 序列。

**8. 模拟边界选在哪一层，决定哪些 bug 能被发现。** Tickloom 和 TigerBeetle 在消息级模拟：简单、覆盖协议依赖的一切（丢消息、分区、超时、重试），但永远不跑"把字节变成消息"的代码——分帧 bug 在模拟中不可能出现。FoundationDB 在字节流级模拟（Sim2Conn），能抓住"一个帧跨两次 read 到达"或"帧中途连接断开"这类 bug。另一端是 hypervisor 级模拟（如 Antithesis），拦截系统调用、虚拟化时间，不改代码就能测任意语言系统，但从零自建是艰巨工程。

> *"A message-level simulator is simpler, and it exercises everything a protocol depends on... But it never runs the code that turns bytes into messages... A byte-level simulator catches those bugs."*
> — 同上

**9. 六条编码军规 + 机器强制执行。** 核心代码里禁系统时钟、禁未种子化随机、禁线程与标准 Future、禁直接网络/磁盘 I/O、禁迭代无序集合、禁跨接缝的跨线程回调。原文明说：靠开发者自觉和 code review 强制这些规则不可扩展——单个 `HashMap` 迭代或一次 `System.currentTimeMillis()` 就会在罕见故障序列命中时静默破坏可回放性。解法是 ArchUnit 静态适应度函数 + `TickCompletableFuture` 运行时捕获创建线程并拒绝其他线程的完成调用，再加种子化故障注入与一致性检查器作为整体适应度函数。

> *"relying on developer discipline or code reviews to enforce these rules does not scale."*
> — 同上

**10. 单线程不牺牲生产性能，且 tick 日志与 LLM 有两个交汇点。** 多数分布式系统是 I/O 密集的，单线程异步批量 I/O 消除锁与上下文切换，与 Redis、FoundationDB、TigerBeetle 同构。与 LLM 的交汇：一是带 tick 戳的结构化故障与执行日志交给 LLM 分析出错原因特别有效；二是 LLM 可以把书上（如 DDIA 的仲裁线性一致性异常图）的场景直接翻译成可执行的 Tickloom 测试。

> *"these structured, tick-stamped logs are particularly effective when handed to an LLM to analyze what went wrong."*
> — 同上

## 核心亮点

**"谁推动时间，谁就拥有复现"被落成一句工程口诀。** 这不是又一个测试工具，而是把分布式系统四个隐藏的进度来源（时钟、调度、网络、磁盘）全部显式化为测试可调用的 `tick()`——复现不再是概率事件，而是同一 seed 的必然结果。可用性与正确性之争（混沌 vs Jepsen）被绕过，直接攻击两者共同的软肋：不可复现。

**崩溃语义被压缩成两个 byte 数组。** `visible` 保存已写未刷的字节，`durable` 保存已 sync 的字节，`sync()` 前者拷贝到后者，崩溃时 `visible` 回退到 `durable`——页缓存、存储缓冲、fsync 失败场景这些最容易写错的部分，用最小数据结构获得确定性模拟。这是全文"把基础设施语义装进可控小盒子"思路的最纯样本。

**纪律问题被转化为适应度函数问题。** 六条军规的执行不靠评审靠机器：静态层面 ArchUnit 每次构建原子化校验前五条，运行时层面自定义 Future 校验线程归属，系统层面种子化故障注入 + 线性一致性检查器验证全局不变量——把"写出确定性代码"从个人修养变成 CI 红绿灯。

## 深入解读

### 三种故障测试的分工表

| 维度 | 混沌工程 | Jepsen | 确定性模拟测试 |
|---|---|---|---|
| 验证目标 | 可用性、韧性 | 正确性（客户端视角语义） | 正确性 + 可复现性 |
| 运行环境 | 真实生产/预发集群 | 活体集群 + 故障注入 | 单线程进程内模拟集群 |
| 故障注入 | 真实基础设施层 | 真实基础设施层，种子化可部分复现 | 模拟层精确控制，tick 粒度 |
| 复现能力 | 弱（时序不可控） | 中（种子化故障，执行仍不确定） | 强（seed = 确切执行） |
| 时间成本 | 真实时间 | 真实时间 | 快进，小时级压到秒级 |
| 门槛 | 低，可后加 | 中，需配合跑活系统 | 高，须从第一天设计架构 |

三者不是替代关系：混沌工程验证运维响应，Jepsen 在不改系统的前提下抓语义违例，DST 把"抓到的违例必然可复现"做成架构属性。真正的分界是入场券——DST 不能事后加装。

### 模拟边界是一张威胁模型地图

把边界画在哪一层，等于宣称"我要抓哪一层的 bug"。消息级（Tickloom/TigerBeetle）抓协议层：丢、延迟、分区、重放、超时交错；字节级（FoundationDB Sim2Conn）追加抓传输层：分帧、半写、字节流层面的部分失败；hypervisor 级（Antithesis）追加抓"未改造系统"：任何语言、任何代码，代价是自建工程量巨大，商业化是合理出路。边界越低，能骗过测试的代码越少，模拟器本身的复杂度越高。反过来，消息级模拟有一个诚实的盲区：`NioConnection` 的分帧代码只在真实网络运行，模拟永远盖不上它——选消息级就是签下"传输层代码靠别的手段验证"的合同。

### 前提条件与数据审读

这套方法的三重前提：架构从第一天单线程异步设计（Java 的 `CompletableFuture` 因阻塞方法和后台线程池被禁用，须自研 Future）；团队接受六条军规的约束成本；有维护模拟器本身的能力。原文对其收益的支撑主要是机制论证与先例引用（FoundationDB、TigerBeetle 的生产实践），Tickloom 本身定位是教学库而非生产系统，文中没有给出"采用 DST 后缺陷率下降 X%"之类的量化数据——"数小时压到秒级"也是定性表述。方向可信，幅度未知。值得注意的是致谢名单：Martin Fowler、Rebecca Parsons、Will Wilson（Antithesis CEO）、Joran Dirk Greef（TigerBeetle 创始人）审阅了草稿——这篇长文实际上是 FDB—Antithesis—TigerBeetle 这条 DST 谱系的权威整理版，这是它超出普通教程文章的分量所在。

## 扩展衍生

**TigerBeetle 的最新迭代：协议感知 DST。** 据 [TigerBeetle 博客](https://tigerbeetle.com/blog/2026-08-20-protocol-aware-dst)（2026-08-20），其模拟器进一步走向 protocol-aware——故障注入理解协议语义，并与 Antithesis 式"由外向内"的确定性 hypervisor 路线做了对比。这是原文发表前三个月该领域最近的一次公开演进。

**商业化与采用面。** 原文提到的 Antithesis 是这条技术路线的商业化载体：据 [WarpStream 博客](https://www.warpstream.com/blog/deterministic-simulation-testing-for-our-entire-saas)（2024-03），WarpStream 用 Antithesis 对整个 SaaS——从注册到 Kafka 负载——做确定性模拟；据 [Materialized View 通讯](https://materializedview.io/p/antithesis-in-the-wild)，Polar Signals 等公司也在采用。据 [Amplify Partners 的 DST 入门](https://www.amplifypartners.com/blog-posts/a-dst-primer-for-unit-test-maxxers)（2025-11），投资界的表述是 Antithesis 的使命为"把 DST 带给大众"。

**生态资源。** GitHub 上有 [awesome-deterministic-simulation-testing](https://github.com/ivanyu/awesome-deterministic-simulation-testing) 精选列表；[databases.systems 在连载《开源版 Antithesis》系列](https://databases.systems/posts/open-source-antithesis-p1)，核心结论同样指出前提是系统本身须写成确定性的——与原文"不能事后加装"互为印证。

**传播情况。** Martin Fowler 本人在 [X](https://x.com/martinfowler/status/2122703421161820598) 和 LinkedIn 转发，推荐语大意是"一个可回放的失败运行胜过十个只能看着失败的运行"（据搜索摘要转述）；Unmesh Joshi 另有配套演讲《Taming Chaos: Deterministic Simulation Testing for Distributed Systems》（YouTube）。社区早期反馈正面，有从业者评价其适合"自己在写 DST 或想理解 DST 原理"的读者（据搜索摘要转述）。

## 延伸阅读

- [Deterministic Simulation Testing（原文）](https://martinfowler.com/articles/deterministic-simulation-testing.html)
- [TigerBeetle: Protocol-Aware Deterministic Simulation Testing](https://tigerbeetle.com/blog/2026-08-20-protocol-aware-dst)
- [Antithesis 官方文档：Deterministic simulation testing](https://antithesis.com/docs/resources/deterministic_simulation_testing)
- [WarpStream: Deterministic Simulation Testing for Our Entire SaaS](https://www.warpstream.com/blog/deterministic-simulation-testing-for-our-entire-saas)
- [awesome-deterministic-simulation-testing（GitHub 精选列表）](https://github.com/ivanyu/awesome-deterministic-simulation-testing)
