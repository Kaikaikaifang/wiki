---
title: Agent 优先产品设计的黄金法则
type: source
tags: [Agent, 产品设计, MCP, AI工程]
source_count: 1
updated: 2026-06-13
---

PostHog 的 agent-first 产品设计经验总结，基于 6000+ 日活用户的两次架构迭代。核心判断：agent 不是附加功能，而是一种**新的交互层**——它坐在用户和产品之间。

**五个黄金法则：**

**1. 让 agent 能做用户能做的一切**

如果一个功能用户可以手动完成，agent 也应该能完成。不要故意留缺口。PostHog 的做法：自动生成 OpenAPI spec → TypeScript Zod schema → 产品团队手动 opt-in（YAML 配置）→ 组合生成 MCP tool handlers。**默认不暴露任何 endpoint，只有产品团队明确授权后才暴露。**

**2. 在 agent 的抽象层级上设计**

不要给 agent 提供 UI 原语（"get insight"、"get funnel"），而是提供 agent 已经会的东西。PostHog 从 v1 的四个 API 调用（projects-get, insight-get, insight-query x2）简化为 v2 的**一个 SQL 查询**：

```sql
SELECT toStartOfWeek(timestamp) AS week, countIf(event = 'signed_up') AS signups
FROM events WHERE timestamp >= now() - INTERVAL 2 WEEK
GROUP BY week ORDER BY week
```

把 read/get 端点全部关掉，用 `executeSql` 替代。agent 已经懂 SQL，不需要你教它你的 UI 概念。

**3. 预加载通用上下文**

v1 系统提示只有 4 行（"Here are some tools, GLHF"）。v2 改为预加载：
- PostHog 专属术语（feature flag, experiment, session replay 等）
- PostHog SQL 语法（ClickHouse SQL 的 custom translation layer）
- 关键查询规则（永远按时间范围过滤）

其他内容按需拉取。这平衡了上下文消耗和功能完整性。

**4. 写 skill 是人类的技能**

不要把 skill 写成 step-by-step 手册。好的 skill 像**给优秀员工的入职指南**——只提供 agent 无法自己发现的信息：
- 内部缩写、命名约定
- 边界情况和异常处理
- 品味和工艺（"how to use it well, not just correctly"）

PostHog 的例子：retention 查询默认使用 `$pageview` 事件，而不是用户随便提到的某个事件。这是产品经验，agent 无法自己推断。

**5. 把 agent 当作真实用户**

- **Headless dogfooding**：用 CLI 而不是 UI 测试 agent 功能，暴露在相同环境中
- **人工 trace review**：每周 review 真实用户会话，包括负面反馈
- **Eval loop**：把人工发现的好案例和坏案例转化为自动化 eval，防止未来回归

来源：[[sources/agent-first-product-engineering]]

相关页面：[[entities/posthog]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]]
