---
title: Multi-Agent Systems
type: topic
tags:
  - Agent
  - 多智能体
  - 研究工作流
source_count: 2
updated: 2026-04-14
---

# Multi-Agent Systems

> 多智能体不是“多开几个模型”而已，而是把有限上下文、有限 token 与有限注意力拆成可协作的并行工作单元。

## 什么时候值得用

根据 [[sources/how-we-built-our-multi-agent-research-system]]，多智能体最适合以下任务：

- **开放式问题**：步骤无法预先写死，要边查边改策略；
- **可并行探索**：存在多条相对独立的搜索路径；
- **信息量过大**：超出单个上下文窗口的有效处理范围；
- **任务价值高**：足以覆盖显著上升的 token 成本。

因此，多智能体不是默认升级选项，而是对“单 agent 的上下文与串行瓶颈”做结构性扩展。

## 为什么会更强

它的收益主要来自三点：

- **并行探索**：多个 subagent 同时追不同线索；
- **上下文隔离**：每个 agent 有自己的工作集，降低路径依赖；
- **结果压缩**：subagent 先过滤信息，再把高价值结论返回给 lead agent。

从这个角度看，多智能体本质上是在扩展“可用推理容量”，而不只是复制同一个 agent。

## 常见结构

目前最常见、也最实用的结构是 **orchestrator-worker**：

- lead / orchestrator 负责拆解问题、分配预算、综合结果；
- worker / subagent 负责在各自边界内执行探索；
- 必要时再加入专门的 citation、review 或 evaluator 环节。

这种结构比完全平权的多智能体更容易调试，因为责任分工更清楚。

## 成功关键不只是模型

多智能体系统的上限通常由下面几件事共同决定：

- **分工提示是否明确**；
- **任务预算是否按复杂度缩放**；
- **工具选择与工具描述是否清晰**；
- **是否有足够好的可观测性、评估与恢复机制**。

也就是说，multi-agent 的难点往往不在“再加一个 agent”，而在“如何避免它们重复劳动、互相拖慢、共同失控”。

## 主要代价

- **token 成本高**：并行性几乎总是用成本换性能；
- **协调复杂度高**：分工、同步、去重、回收都更难；
- **可靠性要求更高**：任何单点失败都可能影响整条研究链路；
- **并非所有领域都适合**：如果任务强依赖共享上下文或高度串行，多智能体收益会下降。

## 一个实用判断句

如果问题不能被自然拆成几条彼此相对独立的工作流，那么它通常还不够适合多智能体。

---

来源：[[sources/how-we-built-our-multi-agent-research-system]] · [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]

相关页面：[[topics/agentic-systems]] · [[topics/long-horizon-agents]] · [[topics/agent-computer-interface]] · [[entities/managed-agents]] · [[entities/anthropic]]
