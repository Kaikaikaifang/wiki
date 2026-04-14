---
title: Agent-Computer Interface
type: topic
tags:
  - Agent
  - 工具设计
  - 提示词工程
source_count: 3
updated: 2026-04-13
---

# Agent-Computer Interface

> 对 agent 而言，工具接口设计不是附属细节，而是系统能力的一部分。

## 什么是 ACI

ACI（agent-computer interface）可以理解为：**agent 如何理解、调用并组合外部工具的接口层**。它对应人机交互中的 HCI，但服务对象从人变成了模型。

[[sources/building-effective-ai-agents]] 的重要提醒是：很多 agent 的上限，不由模型参数量决定，而由工具接口是否清晰、自然、抗误用决定。

## 好的 ACI 长什么样

- **描述清晰**：工具用途、参数、边界、异常情况都写明。
- **格式自然**：尽量使用模型熟悉的文本 / 代码格式，避免额外转义和计数负担。
- **边界明确**：相似工具之间的职责不要重叠模糊。
- **容错内建**：通过参数设计减少误操作空间，也就是 poka-yoke。

## 为什么工具格式很重要

从软件工程视角看，“返回 diff”与“返回完整文件”也许只是不同表示法；但对模型来说，难度可能完全不同。凡是要求模型做额外精确 bookkeeping 的格式，例如：

- 预先写对 diff 行数；
- 在 JSON 中转义大量代码；
- 同时维护多个隐含约束；

都会显著增加出错概率。

因此，一个常见原则是：**让输出格式尽量贴近互联网中自然出现的文本形态。**

[[sources/how-we-built-our-multi-agent-research-system]] 进一步补充了另一层：除了格式本身，**tool selection 也必须被显式教会**。如果 agent 不先审视当前可用工具，不理解每个工具的适用边界，就算模型再强，也可能在一开始就走错搜索空间。

## 设计方法

可以把工具说明当作写给团队里初级工程师的 docstring：

- 它是做什么的；
- 什么时候该用，什么时候不该用；
- 参数分别代表什么；
- 常见误用是什么；
- 有没有示例输入输出。

如果人类读完都需要停下来想一会儿，模型大概率也会困惑。

## 测试方法

ACI 不是写完就算，它需要像产品接口一样被迭代：

- 用多组真实样例测试工具调用；
- 观察模型最常犯的错误；
- 调整参数命名、描述和输出格式；
- 再次测试，直到误用显著下降。

Anthropic 在 SWE-bench coding agent 上的经验甚至是：**优化工具花的时间比优化总 prompt 更多。**

而在 [[sources/how-we-built-our-multi-agent-research-system]] 中，他们甚至让 agent 反复试用 MCP 工具并改写工具描述，最终降低后续 agent 的任务完成时间。这说明 ACI 不只是手工文档工作，也可以进入 agent 驱动的迭代闭环。

## 一个典型案例

文章提到，相对路径工具在 agent 离开根目录后容易出错；改成**始终要求绝对路径**后，工具使用稳定性明显提升。这个例子说明：很多所谓“模型能力问题”，其实是接口设计问题。

[[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]] 则把 ACI 再向下推进一层：当 sandbox、MCP 服务、手机或其他执行环境都统一抽象成 `execute(name, input) → string` 时，agent 面对的是一个更稳定的“手的接口”。这类抽象并不降低复杂度本身，但能降低系统边界的脆弱性。

---

来源：[[sources/building-effective-ai-agents]] · [[sources/how-we-built-our-multi-agent-research-system]] · [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]]

相关页面：[[topics/agentic-systems]] · [[topics/multi-agent-systems]] · [[topics/long-horizon-agents]] · [[entities/managed-agents]] · [[entities/anthropic]]
