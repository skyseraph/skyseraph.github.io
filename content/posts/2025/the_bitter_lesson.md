---
title: "The Bitter Lesson（苦涩的教训）"
date: 2025-10-05T10:00:00+08:00
categories: ["技术"] 
tags: ["LLM"]
toc: true
draft: false
---

> 作者：SkySeraph  
> 原始链接：[The Bitter Lesson](https://skyseraph.github.io/posts/2025/the_bitter_lesson)   
> 核心总结：人类总以为聪明能赢蛮力，但 70 年 AI 史反复证明：算力 + 通用方法，才是终极赢家。 
> 原文作者：Richard S. Sutton（强化学习之父）   
> 发表：2019-03-13    

---

## 中英文

- The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin. The ultimate reason for this is Moore’s law, or rather its generalization of continued exponentially falling cost per unit of computation. Most AI research has assumed that the computation available to the agent is constant (in which case leveraging human knowledge would be one of the only ways to improve performance) but over time, far more computation becomes available than could be anticipated by any research project. To get short-term results, researchers have sought to leverage their knowledge of the domain, but in the long run, the only thing that matters is leveraging computation. The two are not necessarily in conflict, but in practice they often are. Time spent on one is time not spent on the other. There are psychological commitments to investment in one approach or the other. And the human-knowledge approach tends to complicate methods in ways that make them less suited to taking advantage of general methods leveraging computation.
  - 70 年人工智能研究留给我们的最大教训是：利用计算能力的通用方法，最终总是最有效的，而且优势巨大。其根本原因是摩尔定律 —— 或者更准确地说，是 “单位计算成本持续指数级下降” 这一规律的普遍化。绝大多数 AI 研究都假定智能体可用的计算量是固定的（在这种前提下，利用人类知识几乎是提升性能的唯一途径），但随着时间推移，实际可用的计算量会远超任何研究项目最初的预期。为了快速见到成果，研究者总想注入自己对领域的专业知识，但从长远来看，真正决定性的，只有利用计算能力这一条路。两者并非天然冲突，但实践中往往互斥：投入一方的时间，就无法投入另一方。人们还会对自己选择的路径产生心理上的执念。而且，依赖人类知识的方法，往往会把系统设计得越来越复杂，反而难以享受通用计算方法带来的红利。
- There are many examples of AI researchers’ delayed learning of this bitter lesson, and it is instructive to review some of the most prominent.
  - AI 研究者迟迟未能吸取这一苦涩教训的例子比比皆是，回顾其中最典型的几个，极具启发意义。

> In computer chess 国际象棋

- In computer chess, the methods that defeated the world champion, Kasparov, in 1997 were based on massive, deep search. At the time, most computer chess researchers, who had worked on using human understanding of chess’s special structure, were frustrated. When a simpler, search-based method with specialized hardware and software proved more effective, these human-knowledge-based chess researchers were not receptive to the defeat. They said that brute-force search may have won this time, but it was not a general strategy, and anyway it was not how people played chess. These researchers wanted methods based on human input to win and were disappointed when they did not.
  - 1997 年击败世界冠军卡斯帕罗夫的程序，核心是大规模、深度搜索。当时，绝大多数深耕国际象棋的研究者，都在试图把人类对棋类结构的理解编码进程序，结果却无比沮丧。当一套更简单、基于搜索、搭配专用软硬件的方案完胜时，这些坚持 “人类知识优先” 的研究者难以接受。他们说：“蛮力搜索这次赢了，但这不是通用策略，而且这根本不是人类下棋的方式。” 他们希望 “注入人类智慧” 的方法获胜，失败后倍感失落。

> In computer Go 围棋
- A similar pattern of research progress was seen in computer Go, only delayed by a further 20 years. Enormous initial efforts went into avoiding search by taking advantage of human knowledge, or of the special features of the game, but all those efforts proved irrelevant, or worse, once search was applied effectively at scale. Also important was the use of learning by self-play to learn a value function (as it was in many other games and even in chess, although learning did not play a big role in the 1997 program that first beat a world champion). Learning by self-play, and learning in general, is like search in that it enables massive computation to be brought to bear. Search and learning are the two most important classes of techniques for utilizing massive amounts of computation in AI research. In computer Go, as in computer chess, researchers’ initial effort was directed towards utilizing human understanding (so that less search was needed) and only much later was much greater success had by embracing search and learning.
  - 围棋领域重演了几乎一模一样的剧情，只是晚了 20 年。早期研究者耗费巨大精力，试图避免搜索—— 靠人类棋理、靠围棋规则特性来设计程序。可一旦大规模搜索 + 学习真正成熟，所有这些努力瞬间变得无关紧要，甚至拖后腿。另一关键是自我对弈学习（用来训练价值函数），这在很多棋类（包括国际象棋）里都至关重要（尽管 1997 年深蓝的学习成分不多）。自我对弈、乃至所有机器学习，本质上都和搜索一样：把海量算力用起来。搜索与学习，是 AI 研究中利用大规模算力的两大核心技术。围棋和国际象棋一样：早期拼 “人类理解”、减少搜索；后期靠 “搜索 + 学习”，才真正实现质的飞跃。

> In speech recognition 语音识别
- In speech recognition, there was an early competition, sponsored by DARPA, in the 1970s. Entrants included a host of special methods that took advantage of human knowledge—knowledge of words, of phonemes, of the human vocal tract, etc. On the other side were newer methods that were more statistical in nature and did much more computation, based on hidden Markov models (HMMs). The statistical methods won, and the field transitioned to them. Later, neural networks with even more computation and less human knowledge took over, progressing steadily, leading to today’s speech recognition systems.
  - 1970 年代 DARPA 举办的早期语音识别竞赛中，一派是人工设计规则：把单词、音素、人类声道结构等语言学知识硬编码进去；另一派是统计方法（隐马尔可夫模型 HMM）：计算量大、依赖数据、几乎不注入人类规则。结果：统计方法完胜，整个领域全面转向。后来，神经网络登场 —— 算力更强、人类知识更少、效果更好，一路迭代至今，成就了今天的语音识别系统。

> In computer vision 计算机视觉
- The same pattern holds in computer vision. Early methods built on human-designed feature detectors, such as SIFT and HOG, were replaced by convolutional neural networks that learned features from scratch using massive computation and data.
  - 同样的剧本再次上演：早期靠人工设计特征（如 SIFT、HOG），把人类对图像的理解写成特征提取器；后来被卷积神经网络（CNN）彻底取代 ——CNN 从原始数据里自动学特征，靠的是海量计算 + 海量数据，几乎不依赖人工设计。

> 教训的本质
- To see this, and to effectively resist it, we have to understand the appeal of these mistakes. We have to learn the bitter lesson that building in how we think we think does not work in the long run. The bitter lesson is based on the historical observations that:
  - 要理解这种反复犯错的吸引力、并有效避免重蹈覆辙，我们必须认清一个残酷事实：从长远看，试图把 “人类自以为的思考方式” 硬编码进系统，注定走不通。这个苦涩教训，来自四条反复验证的历史规律：
- AI researchers have often tried to build knowledge into their agents;
This always helps in the short term, and is personally satisfying to the researcher;
  - 1、AI 研究者总想把人类知识直接植入智能体；
  - 2、这种做法短期有效、成就感强；
  - 3、但长期必然撞上性能瓶颈、甚至阻碍后续突破；
  - 4、真正的颠覆性突破，永远来自相反路径：靠搜索和学习，放大算力、规模化计算。
- But in the long run it plateaus and even inhibits further progress;
Breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning.
  - 最终，“算力派” 的胜利带着苦涩，甚至难以被完全消化 —— 因为赢的，是一套取代了人类中心主义的方法。

> 两大核心启示
- The eventual success is tinged with bitterness, and often incompletely digested, because it is success over a favored, human-centric approach.
One thing that should be learned from the bitter lesson is the great power of general purpose methods, of methods that continue to scale with increased computation even as the available computation becomes very great. The two methods that seem to scale arbitrarily in this way are search and learning.
  - 通用方法的巨大力量：真正强大的，是那些能随算力增长而无限扩展的通用方法。其中，搜索和学习是仅有的两种、能近乎无限扩展的核心范式。

- The second general point to be learned from the bitter lesson is that the actual contents of minds are tremendously, irredeemably complex; we should stop trying to find simple ways to think about the contents of minds, such as simple ways to think about space, objects, multiple agents, or symmetries. All these are part of the arbitrary, intrinsically-complex, outside world. They are not what should be built in, as their complexity is endless; instead, we should build in only the meta-methods that can find and capture this arbitrary complexity. The key thing about these meta-methods is that they can find good approximations, but the algorithms should be based on our methods, not on the knowledge we have found. We want AI agents that can discover like we do, not ones that contain what we have discovered.
  - 人类心智的复杂度，远超想象：别再试图用简单规则去模拟人类思考（比如空间、物体、多智能体、对称性等概念）。这些都是外部世界的、无限复杂的、随机的一部分，不该被硬编码进系统。正确做法：只构建元方法（meta-methods）—— 让系统自己去发现、去捕捉这种复杂。关键在于：算法要 “会发现”，而不是 “装着人类已发现的知识”。我们想要的 AI，是能像人类一样探索发现的 AI，而不是装满人类既有知识的 AI。


## 核心思想拆解

### 两大核心真理（Sutton 的终极结论）
- 真理 1：搜索 + 学习 = 唯一可无限扩展的范式
  - 任何需要 “人工设计” 的东西，都会成为瓶颈；只有搜索和学习，能随算力增长无限变强。

- 真理 2：不要 “装知识”，要 “会发现”
  - 人类知识是有限的、过时的、偏见的；世界是无限复杂的。AI 不该是 “装着人类知识的容器”，而该是 “会自己探索的探险家”。

### 对今天的现实启示

1）大模型（GPT-4o / Claude / Gemini）
完全印证：Transformer = 学习 + 海量算力 + 海量数据，几乎不注入语言学规则；
人类曾经以为必须 “语法、句法、语义”，结果全被纯统计 + 算力碾压。

2）AI 创业 / 工程
少做规则、多做数据 + 算力；
警惕 “短期优化陷阱”：今天好用的人工规则，明天就是瓶颈；
架构要通用、可扩展，为未来算力增长留空间。

3）科研方向
放弃 “模拟人类思考”；
专注元方法：让机器自己学、自己搜、自己发现。