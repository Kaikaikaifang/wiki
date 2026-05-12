---
title: 多智能体系统
type: topic
tags:
  - Agent
  - 多智能体
  - 研究工作流
source_count: 4
updated: 2026-05-12
---

> 多智能体最容易被误解成“多堆几份模型调用”，但真正稀缺的从来不是 agent 数量，而是你能不能把问题拆成值得并行的几条独立思路线。

## 什么时候值得用

根据 [[sources/how-we-built-our-multi-agent-research-system]]，多智能体最适合以下任务。我现在基本把这几条当成是否值得上多智能体的前置门槛，而不是优化建议。

- **开放式问题**：步骤无法预先写死，要边查边改策略；
- **可并行探索**：存在多条相对独立的搜索路径；
- **信息量过大**：超出单个上下文窗口的有效处理范围；
- **任务价值高**：足以覆盖显著上升的 token 成本。

因此，多智能体不是默认升级选项，而是对“单 agent 的上下文与串行瓶颈”做结构性扩展。它解决的是结构问题，不是情绪问题。

## 为什么会更强

它的收益主要来自三点，而且每一点都对应着单 agent 很难自然补齐的短板：

- **并行探索**：多个 subagent 同时追不同线索；
- **上下文隔离**：每个 agent 有自己的工作集，降低路径依赖；
- **结果压缩**：subagent 先过滤信息，再把高价值结论返回给 lead agent。

从这个角度看，多智能体本质上是在扩展“可用推理容量”，而不只是复制同一个 agent。

## 常见结构

目前最常见、也最实用的结构是 **orchestrator-worker**：

- lead / orchestrator 负责拆解问题、分配预算、综合结果；
- worker / subagent 负责在各自边界内执行探索；
- 必要时再加入专门的 citation、review 或 evaluator 环节。

这种结构比完全平权的多智能体更容易调试，因为责任分工更清楚。我也更偏好这种设计，因为很多“多智能体协作”一旦没有明确层级，就会很快退化成昂贵的混乱。

## 另一种分工：按时间尺度拆分

[[sources/interaction-models]] 提出了一种不太一样的双模型结构：interaction model 负责实时响应，background model 负责深度推理。两者的分工不是按任务并行度，而是按**时间尺度**——一个处理 200ms 的 micro-turns，另一个处理需要数秒甚至数分钟的复杂推理。

这与 orchestrator-worker 模式有本质区别：

- **Orchestrator-worker**：按任务类型或搜索方向并行拆分，每个 worker 处理不同的子问题
- **Interaction-background**：按延迟需求拆分，两个模型处理的是**同一个对话的不同时间分辨率**

这种结构的优势在于，用户始终感觉到一个持续在场的协作者，而不会被"模型正在思考，请稍候"打断。Interaction model 决定**何时说话、如何保持对话节奏**，background model 决定**说什么最有深度**。两者通过流式结果回注协作，而不是通过最终答案交付协作。

我觉得这个模式对多智能体设计的启示是：**分工的维度不只可以是任务空间，还可以是时间空间**。在某些场景下，让不同智能体负责不同时间尺度的响应，可能比让它们负责不同子任务更有效。

## 成功关键不只是模型

多智能体系统的上限通常由下面几件事共同决定：

- **分工提示是否明确**；
- **任务预算是否按复杂度缩放**；
- **工具选择与工具描述是否清晰**；
- **是否有足够好的可观测性、评估与恢复机制**。

也就是说，multi-agent 的难点往往不在“再加一个 agent”，而在“如何避免它们重复劳动、互相拖慢、共同失控”。这是我觉得这类系统最值得被正视的真实工程问题。

## 主要代价

- **token 成本高**：并行性几乎总是用成本换性能；
- **协调复杂度高**：分工、同步、去重、回收都更难；
- **可靠性要求更高**：任何单点失败都可能影响整条研究链路；
- **并非所有领域都适合**：如果任务强依赖共享上下文或高度串行，多智能体收益会下降。

## 一个生产级实例：oh-my-openagent

[[sources/oh-my-openagent]] 提供了一个非常具体的 orchestrator-worker 实现。Sisyphus 作为总调度，不直接选择模型，而是选择 `category`（如 `visual-engineering`、`ultrabrain`、`quick`），再由 harness 解析为具体模型和 fallback chain。

omo 的后台任务系统把并行执行做成了基础设施：

- 每个 subagent 运行在独立的 OpenCode 子会话中，有自己的模型和上下文。
- 并发限制 5 个/模型，FIFO 队列，避免挤占。
- 完成后通过 `<system-reminder>` 注入结果，不污染主会话上下文。
- 内置熔断器，检测子 agent 陷入工具循环时自动取消。

这个实现让我意识到：多智能体系统的"并行"不只是同时发几个 API 请求，而是**会话隔离 + 生命周期管理 + 结果回注**的一整套机制。缺少其中任何一环，并行都会退化成"同时跑几个不知道彼此进度的黑盒"。

omo 还做了一件事值得记录：它把模型选择从"用户手动操作"变成了"category 语义驱动"。用户说"帮我画个前端"，系统自动路由到 `visual-engineering` → gemini-3.1-pro；用户说"帮我分析架构"，自动路由到 `ultrabrain` → gpt-5.5 xhigh。这种抽象让多智能体的使用门槛降低了一个数量级。

## 一个实用判断句

如果问题不能被自然拆成几条彼此相对独立的工作流，那么它通常还不够适合多智能体。

---

来源：[[sources/how-we-built-our-multi-agent-research-system]] · [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]] · [[sources/oh-my-openagent]] · [[sources/interaction-models]]

相关页面：[[topics/agentic-systems]] · [[topics/ai-agent-harness]] · [[topics/long-horizon-agents]] · [[topics/agent-computer-interface]] · [[topics/interaction-models]] · [[entities/managed-agents]] · [[entities/anthropic]] · [[entities/oh-my-openagent]] · [[entities/thinking-machines-lab]]
