---
title: DuckDB 与 ClickHouse 对比
type: source
tags: [DuckDB, ClickHouse, OLAP, PostHog]
source_count: 1
updated: 2026-06-13
---

PostHog 同时使用 ClickHouse 和 DuckDB 的对比文章，核心不是分出胜负，而是明确两者是**不同场景的工具**——就像洋葱和葱：长得很像，但用途完全不同。

ClickHouse 是"完整数据库"——长驻进程、水平扩展、自管理存储，具备物化视图、成熟压缩、稀疏主键和 MergeTree 家族引擎。它适合**高并发、重复查询、实时分析**的场景，比如 PostHog 的核心漏斗、趋势、留存分析。

DuckDB 是"进程内引擎"——嵌入式、单节点、无需服务器，要么作为查询引擎直接分析 Parquet/CSV 文件（用完即销毁），要么作为 `.duckdb` 持久化数据库文件。它适合**即席查询、探索性分析、轻量级 ETL**。

PostHog 的具体分工：
- **ClickHouse**：处理热分析数据（漏斗、趋势、留存、路径分析）——十亿级事件，需要近实时
- **DuckDB**：处理数据仓库产品——用户自己的全部数据，通过 Duckgres（Postgres 协议包装器）让 BI 工具连接

两个有趣补充：
- **clickhouse-local**：ClickHouse 的便携版本，类似 DuckDB 的轻量级模式，但官方定位是测试工具，不是生产服务
- **DuckLake**：DuckDB 的数据湖格式，解决了 DuckDB 单节点存储限制，数据持久化在对象存储，元数据由 DuckDB 管理

来源：[[sources/duckdb-vs-clickhouse-posthog]]

相关页面：[[entities/duckdb]] · [[entities/clickhouse]] · [[topics/ducklake]] · [[entities/posthog]]
