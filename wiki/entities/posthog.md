---
title: PostHog 全栈开发者平台
type: entity
tags: [产品分析, 开发者工具, 开源]
source_count: 4
updated: 2026-06-13
---

PostHog 是一个全栈开发者平台，提供产品分析、Web 分析、Session Replay、Feature Flags、A/B 测试、数据仓库等功能。它是开源的，采用 MIT 许可证。

在 wiki 中，PostHog 的价值在于它提供了**真实的生产架构案例**：它同时使用了 Postgres、ClickHouse 和 DuckDB 三种数据库，每种负责不同的工作负载。

**PostHog 的三数据库栈：**
- **Postgres**：应用状态、用户数据、metadata——source of truth
- **ClickHouse**：热分析数据——漏斗、趋势、留存、路径分析（十亿级事件，近实时）
- **DuckDB**：数据仓库——用户的全部数据（通过 Duckgres Postgres 协议包装器让 BI 工具连接）

PostHog 还开源了一些有趣的项目：
- **Duckgres**：Postgres 协议包装器，让 DuckDB 看起来像 Postgres
- **MCP Server**：让 agent 通过 MCP 协议访问 PostHog 数据

来源：[[sources/duckdb-vs-clickhouse-posthog]] · [[sources/duckdb-vs-postgres]] · [[sources/duckdb-vs-sqlite]] · [[sources/agent-first-product-engineering]]

相关页面：[[entities/duckdb]] · [[entities/clickhouse]] · [[topics/duckdb-vs-clickhouse]] · [[topics/agent-first-engineering]]
