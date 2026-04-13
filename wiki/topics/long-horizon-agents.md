---
title: Long-Horizon Agents
type: topic
tags: [AI Agent, 长程任务, 上下文管理, 运行时]
source_count: 2
updated: 2026-04-13
---

# Long-Horizon Agents

> 长程 agent 的核心难题不是“能不能多跑几轮”，而是如何在长时间、可失败、可恢复的过程中保持状态一致与任务连续性。

## 问题本质

[[sources/how-we-built-our-multi-agent-research-system]] 和 [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]] 都指出：一旦 agent 运行时间拉长，系统面对的就不再只是 prompt 质量问题，而是**状态、恢复、上下文与部署**问题。

## 为什么长程会更难

- **错误会复利**：一次工具失败可能把后续整条轨迹带偏；
- **上下文会溢出**：任务跨越数十到数百轮时，窗口必然不够；
- **部署会打断进行中的会话**：线上 agent 不会在发版时自动停下来；
- **debug 更难**：非确定性让“复现一次再看”不再可靠。

## 记忆层与工作集要分开

最重要的设计原则是：**可恢复历史 ≠ 当前上下文窗口。**

根据 [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]，更稳的做法是：

- 把完整、可回放的事件历史放进 session；
- 把压缩、裁剪、重排等上下文工程留给 harness；
- 让 agent 在需要时回读事件，而不是只依赖一次性摘要。

这样做的好处是，未来即使上下文工程策略变化，也不会损坏底层历史。

## 可靠性模式

在长程任务中，常见的工程模式包括：

- **checkpoint 与 resume**：故障后从上次状态继续；
- **durable log**：把关键事件写入可持久化的会话层；
- **tool retry + graceful degradation**：把失败显式暴露给 agent，由它调整策略；
- **observability**：记录决策模式、工具调用结构与关键转折点；
- **渐进部署**：例如 rainbow deployment，避免一次发版打断全部运行中任务。

## 与多智能体的关系

多智能体会进一步放大长程问题：

- 多个 subagent 同时产生状态更新；
- lead agent 需要管理预算、同步和综合；
- 如果切到异步执行，协调成本会继续上升。

因此，越是多智能体，越需要先把长程运行时打牢。

## 一个实用判断句

如果系统无法优雅地恢复、回放和重读过去发生的事，它就还没有准备好做真正的长程 agent。

---

来源：[[sources/how-we-built-our-multi-agent-research-system]] · [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]
相关页面：[[topics/multi-agent-systems]] · [[topics/agentic-systems]] · [[entities/managed-agents]] · [[entities/anthropic]]
