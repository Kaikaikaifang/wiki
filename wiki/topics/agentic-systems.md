---
title: Agentic Systems
type: topic
tags: [AI Agent, 工作流, 方法论]
source_count: 1
updated: 2026-04-13
---

# Agentic Systems

> 用一条复杂度递进路径理解增强型 LLM、workflow 与自治 agent。

## 核心区分

[[sources/building-effective-ai-agents]] 给出的关键区分不是“有没有工具”，而是**谁在掌控流程**：

- **Workflow**：执行路径由开发者预定义，模型在框架内完成局部子任务。
- **Agent**：模型根据当前上下文与环境反馈，动态决定下一步做什么。

因此，workflow 更像“带 LLM 的程序编排”，agent 更像“带工具与反馈回路的模型驱动执行体”。

## 复杂度阶梯

从低复杂度到高复杂度，可以把 agentic systems 看成一条连续谱：

1. **增强型 LLM**：单轮调用 + 检索 / 工具 / 记忆。
2. **Prompt chaining**：串行拆解，降低每步难度。
3. **Routing**：按类别把输入分流给不同处理路径。
4. **Parallelization**：并行处理子任务或多次投票。
5. **Orchestrator-workers**：动态分配子任务，再汇总。
6. **Evaluator-optimizer**：生成、评估、重试形成闭环。
7. **Autonomous agent**：在环境中多轮行动，持续自我校正。

这条阶梯的价值不在于“越往后越高级”，而在于提醒自己：**优先选择能满足目标的最低复杂度方案。**

## 什么时候用 workflow

适合 workflow 的任务通常有几个特征：

- 子任务结构相对清晰；
- 可以预先写出主要路径；
- 希望更强的可预测性与一致性；
- 可以接受较低的灵活性，换取更好调试性。

这时，把任务拆成链式、路由式或并行式结构，往往比直接放权给自治 agent 更可靠。

## 什么时候用 agent

适合真正 agent 的任务通常满足：

- 所需步骤数难以提前确定；
- 每一步是否继续，取决于环境反馈；
- 任务允许模型持续做局部决策；
- 有外部“ground truth”可帮助纠错，例如工具返回值、代码执行结果、自动化测试。

最典型例子是 coding agent：它可以修改代码、运行测试、再根据失败结果继续迭代。

## 风险与约束

agent 的优势来自自治，但风险也来自自治：

- 成本更高；
- 错误会在多轮循环中累积；
- 不透明的中间推理让调试更难；
- 如果缺少停止条件与人工检查点，容易失控。

因此，agent 设计通常需要配套：sandbox、guardrails、迭代上限、人工介入点与显式日志。

## 一个实用判断句

如果你很难解释“为什么一定需要多轮自治，而不是更好的单轮 prompt / 检索 / workflow”，那通常说明**现在还不需要 agent**。

---

来源：[[sources/building-effective-ai-agents]]
相关页面：[[topics/agent-computer-interface]] · [[entities/anthropic]]
