---
title: 用 AI 做仪表盘前先补上的五步检查单
author: MotherDuck
published: "2026-04-14"
link: "https://motherduck.com/blog/vibecoding-dashboards-best-practices/"
file: raw/articles/vibe-coding-dashboards-best-practices.md
type: source
tags: [数据可视化, 仪表盘, Agent, DuckDB]
source_count: 1
updated: 2026-06-15
---

这篇文章表面上是在讲“怎么用 AI 做一个不难看的 dashboard”，但我读下来更在意的其实不是 prompt 技巧，而是它把数据可视化重新拉回到了一个更朴素的判断：**图表不是装饰，而是决策界面。**

文章给出的五步框架非常适合拿来约束 Agent 式的数据产品工作流。第一步不是先挑图，而是先回答“给谁看、要支持什么决策、只允许留下哪个核心结论”；第二步才是按问题类型匹配图表类型，比如趋势看折线、排名看条形、相关性看散点；第三步往下落到颜色、层级、参考线和数据墨水比；第四步要求整个页面有 setup、tension、insight、action 的叙事弧线；第五步则强调交互最后再加，而不是一开始就把筛选器贴满屏幕。

我特别认同它对“vibe-coding”局限的提醒：AI 可以服从规则，但不会替我真正理解为什么这些规则成立。所以像 `From Data to Viz`、Tufte、`Storytelling with Data` 这些框架，价值不是给模型喂术语，而是让我在最后审稿时知道什么地方值得怀疑。

来源：[[sources/vibe-coding-dashboards-best-practices]]

相关页面：[[topics/dashboard-storytelling]] · [[entities/motherduck]] · [[entities/duckdb]]
