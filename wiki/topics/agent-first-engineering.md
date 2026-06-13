---
title: Agent 优先的产品设计原则
type: topic
tags: [Agent, 产品设计, MCP, AI工程]
source_count: 1
updated: 2026-06-13
---

> PostHog 的 agent-first 工程经验让我看到：agent 不是产品的附加功能，而是一种新的交互层——它坐在用户和产品之间。设计得好，它能让用户用自然语言完成复杂的操作；设计得不好，它会让用户陷入"agent 卡住了，我得手动去 UI 补完"的挫败感。

## 核心判断：Agent 是新的交互层

PostHog 把 agent 比作一种"新形态"（form factor），类似于从桌面到移动端的变化。这意味着：

- 不能把它当作 UI 的自动化脚本
- 不能把它当作 API 的薄包装
- 必须把它当作一个**独立的用户群体**来设计

## 原则一：Agent 应该能做用户能做的一切

这是最基础但也最容易被忽略的原则。如果 agent 缺少某个功能，用户就会被迫跳出 agent 去手动完成——这破坏了 agent 的价值。

PostHog 的 v2 方案：
1. 自动生成 OpenAPI spec（从 Django 类型化端点）
2. 转换为 TypeScript Zod schema
3. 产品团队**手动 opt-in**（YAML 配置）——默认不暴露任何端点
4. 组合生成 MCP tool handlers

**关键决策**：默认关闭所有端点，而不是默认开放。这避免了"agent 能做太多危险的事"的问题，同时确保产品团队对暴露什么有明确意识。

## 原则二：在 Agent 的抽象层级上设计

不要给 agent 提供 UI 原语。agent 不懂"打开 insight 页面"或"点击 funnel 标签"，它懂 SQL、懂 API、懂数据。

PostHog 的 v1 → v2 演进：
- **v1**：`projects-get` → `insight-get` → `insight-query` × 2（4 个 API 调用）
- **v2**：一个 `executeSql` 调用

```sql
SELECT toStartOfWeek(timestamp) AS week, countIf(event = 'signed_up') AS signups
FROM events WHERE timestamp >= now() - INTERVAL 2 WEEK
GROUP BY week ORDER BY week
```

agent 已经懂 SQL，不需要你教它你的 UI 概念。这不仅减少了 API 调用，还释放了 agent 的创造力——它可以用 SQL 做你没想到的分析。

## 原则三：预加载通用上下文

Agent 的上下文是有限资源。不要每次让 agent 重新发现产品的基本概念。

PostHog 的 v1 系统提示："Here are some tools for using PostHog, GLHF."（4 行）
PostHog 的 v2 系统提示：
- PostHog 专属术语（feature flag, experiment, session replay 等）
- PostHog SQL 语法（ClickHouse SQL 的 custom translation layer）
- 关键查询规则（永远按时间范围过滤）

其他内容按需拉取。这是**固定上下文 + 动态上下文**的平衡。

## 原则四：写 Skill 是人类的技能

不要把 skill 写成 step-by-step 手册。agent 不需要"先点 A，再点 B，最后点 C"——它需要的是**领域知识**。

好的 skill 像给优秀员工的入职指南：
- **内部知识**：缩写、命名约定、风格指南
- **边界情况**：哪里容易出错，怎么处理
- **品味和工艺**：不仅做"对"，还要做"好"

PostHog 的例子：retention 查询默认使用 `$pageview` 事件。这不是硬性规则，而是产品经验——用户随便提到的某个事件通常会导致 retention 看起来比实际差。agent 无法自己推断这个判断。

## 原则五：把 Agent 当作真实用户

传统的测试方法覆盖不了 agent 的行为，因为相同的输入可能产生不同输出。需要新的验证方法：

- **Headless dogfooding**：用 CLI 而不是 UI 测试 agent 功能。这让你暴露在 agent 的真实环境中——同样的错误、语法、摩擦。
- **人工 trace review**：每周 review 真实用户会话，包括负面反馈。自动化测试不会发现"agent 给出了一个技术上正确但业务上错误的回答"。
- **Eval loop**：把人工发现的好案例和坏案例转化为自动化 eval，防止未来的模型或 prompt 变化导致好的行为退化。

## 与现有 Agent 架构的关系

这些原则补充了 wiki 中已有的 agent 主题：

- [[topics/agentic-systems]] 讨论 agent 的复杂度阶梯（prompt chaining → routing → orchestrator-workers）
- [[topics/agent-computer-interface]] 讨论面向模型的工具接口设计
- [[topics/ai-agent-harness]] 讨论 harness 与 platform 的分层
- [[topics/interaction-models]] 讨论实时交互的新范式

而这篇文章补充的是**产品层面的设计**：不是 agent 内部怎么工作，而是**产品怎么让 agent 工作得好**。

## 对我的启发

最让我印象深刻的是第二条原则：**"在 agent 的抽象层级上设计"**。PostHog 从 4 个 API 调用减少到 1 个 SQL 查询，这不是性能优化，而是**认知层级的对齐**——agent 理解 SQL，不理解你的 UI 结构。

这也让我反思：我们在设计 agent 工具时，应该问的不是"agent 怎么调用我们的 API"，而是"agent 怎么思考我们的数据"。

来源：[[sources/agent-first-product-engineering]]

相关页面：[[entities/posthog]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/ai-agent-harness]] · [[topics/interaction-models]]
