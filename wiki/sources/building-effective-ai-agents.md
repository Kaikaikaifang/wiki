---
title: "Building Effective AI Agents"
type: source
tags: [AI Agent, 方法论, 工作流, 工具设计]
source_count: 1
source_file: raw/articles/building-effective-ai-agents.md
author: Erik Schluntz, Barry Zhang
published: 2026-04-13
updated: 2026-04-13
---

# Building Effective AI Agents

来源：[[entities/anthropic]] · [原文](https://www.anthropic.com/engineering/building-effective-agents)

## 核心论点

这篇文章的主张非常克制：**高效 agent 往往不是靠复杂框架堆出来的，而是靠简单、可组合的模式逐步扩展出来的。** 在能用单次 LLM 调用解决问题时，不必急着上 workflow；在 workflow 已足够可预测时，也不必过早升级为高度自治的 agent。

## 两类 agentic systems

- **Workflow**：由代码预先编排路径，LLM 与工具沿既定流程执行。
- **Agent**：由 LLM 动态决定下一步、工具使用方式与任务推进路径。

文章把二者都归入 agentic systems，但强调它们在**控制权位置**上的本质差异：workflow 的控制权主要在程序，agent 的控制权更多交给模型。

## 复杂度递进

Anthropic 给出了一条从低到高的复杂度梯度：

1. **增强型 LLM**：在单次调用上加入检索、工具、记忆。
2. **Prompt chaining**：把任务拆成串行步骤，并在中间加 gate 检查。
3. **Routing**：先分类，再把问题交给更专门的提示、工具或模型。
4. **Parallelization**：并行跑多个子任务，或对同一任务投票。
5. **Orchestrator-workers**：由一个中心模型动态拆任务，再综合 worker 结果。
6. **Evaluator-optimizer**：生成与评估形成闭环，迭代改进输出。
7. **Autonomous agent**：在环境反馈中循环规划、执行、检查，必要时再求助人类。

## 什么时候该上 agent

文章给出的判断标准很实用：

- 如果任务边界明确、流程稳定、希望高可预测性，优先用 [[topics/agentic-systems]] 中的 workflow 思路。
- 如果任务步骤数无法预先写死、需要模型持续判断下一步、且环境允许较高自治，才考虑真正的 agent。
- 如果单次调用配合检索和示例已经够好，继续保持简单通常更优。

这背后是一条重要原则：**只在复杂度确实带来可测量收益时才增加复杂度。**

## 三条设计原则

文章在总结部分把成功经验压缩为三条：

- **Simplicity**：设计保持简单，避免不必要抽象。
- **Transparency**：让规划步骤显式可见，便于调试与审查。
- **ACI 质量**：把 agent-computer interface 设计成清晰、可测试、少歧义的工具接口。

## 关于框架的态度

Anthropic 并不反对框架，但建议先直接使用 LLM API 建立最小可行版本。原因是：框架虽然加速起步，却也容易遮蔽 prompt、工具定义和响应细节，使调试困难，并诱导过早复杂化。

## ACI：工具设计比总 prompt 更重要

附录 2 的启发很强：很多 agent 失败不是因为模型不够强，而是因为**工具接口设计得不适合模型使用**。文章强调：

- 工具描述要像写给初级工程师的 docstring 一样清楚；
- 参数命名、格式选择、边界条件都要显式；
- 尽量贴近模型熟悉的自然文本 / 代码格式；
- 要通过测试反复观察模型如何误用工具，再调整接口。

其中最值得记住的一句是：**设计 ACI 时，应投入接近 HCI 的认真程度。**

## 实践中最有价值的场景

文章认为两个场景特别适合 agent：

- **客户支持**：既需要对话，也需要访问外部系统与执行操作。
- **Coding agent**：因为代码结果可以用测试验证，形成稳定反馈闭环。

这说明 agent 最适合那些既能行动、又能从环境拿到明确反馈信号的任务。

---

相关页面：[[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[entities/anthropic]]
