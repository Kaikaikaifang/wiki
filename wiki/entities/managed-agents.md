---
title: Managed Agents
type: entity
tags: [产品, AI Agent, 运行时, Claude]
source_count: 1
updated: 2026-04-13
---

# Managed Agents

Managed Agents 是 Anthropic 在 Claude Platform 上提供的托管式长程 agent 服务。它的意义不只是“帮你托管 agent”，而是提出了一种更一般的 agent 运行时设计思路：**把会话、控制循环与执行环境解耦成稳定接口。**

## 核心定位

根据 [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]，Managed Agents 试图成为一种 **meta-harness**：

- 不把某一种具体 harness 写死；
- 允许未来替换不同的 harness、sandbox 与工具系统；
- 通过稳定接口支持长时程、可恢复、可扩展的 agent 运行。

## 三个核心部件

- **Session**：保存完整事件流；
- **Harness**：负责调用模型与编排工具；
- **Sandbox / Hands**：承担实际执行动作。

这使 Managed Agents 更像一层 agent 基础设施，而不是单一 agent 模板。

## 为什么重要

它体现了 Anthropic 对 agent 基建的一个成熟判断：**真正会过时的通常是具体策略，不应过早把它们固化进不可替换的系统边界。**

因此，Managed Agents 的价值在于把“未来模型会更强、harness 会继续变”当作设计前提，而不是例外情况。

---

来源：[[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]
相关页面：[[topics/long-horizon-agents]] · [[topics/multi-agent-systems]] · [[entities/anthropic]]
