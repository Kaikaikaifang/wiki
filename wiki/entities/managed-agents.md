---
title: Managed Agents 产品
type: entity
tags:
  - 产品
  - Agent
  - 运行时
  - Claude
source_count: 1
updated: 2026-04-16
---

Managed Agents 是 Anthropic 在 Claude Platform 上提供的托管式长程 agent 服务。它吸引我的地方，不只是“帮你托管 agent”，而是它把很多人平时混在一起谈的东西拆开了：会话、控制循环、执行环境，其实应该是不同层次的稳定接口。

## 核心定位

根据 [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]，Managed Agents 试图成为一种 **meta-harness**。我觉得这个定位非常关键，因为它说明 Anthropic 想做的不是某一代 agent 模板，而是一层更抗变化的基建抽象：

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

因此，Managed Agents 的价值在于把“未来模型会更强、harness 会继续变”当作设计前提，而不是例外情况。对我来说，这页更像是在记录一种 agent 运行时哲学，而不只是一个产品名词。

---

来源：[[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]

相关页面：[[topics/long-horizon-agents]] · [[topics/multi-agent-systems]] · [[entities/anthropic]]
