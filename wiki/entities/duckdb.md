---
title: DuckDB 面向分析型负载的进程内数据库
type: entity
tags: [数据库, OLAP, 分析型, 开源]
source_count: 4
updated: 2026-06-13
---

DuckDB 是一个面向分析型工作负载的进程内数据库，由荷兰 Centrum Wiskunde & Informatica (CWI) 的 Mark Raasveldt 和 Hannes Mühleisen 等人开发。它的定位很清晰：不是 SQLite 的 OLAP 版本，而是让分析查询可以在本地笔记本、CI 流水线、Python 脚本或 Jupyter Notebook 中直接运行，无需启动独立的数据库服务器。

我使用 DuckDB 的核心体验是：它把"加载 CSV 然后做 GROUP BY"这种操作从"先启动数据库服务"变成"import duckdb; con.execute(...)"，而执行速度却能接近或超过一些分布式系统。它直接利用内存进行向量化执行，支持高效的 Parquet 读写，与 pandas 生态集成良好。

**两种工作模式**

DuckDB 可以工作在两种完全不同的模式：

1. **查询引擎模式**：导入 duckdb → 指向 Parquet/CSV 文件 → 执行 SQL → 销毁。不保留任何状态。这是 DuckDB 最轻量的用法，直接分析外部数据文件。
2. **数据库模式**：创建 `.duckdb` 持久化文件，包含表、视图、schema。类似 SQLite 的工作方式，状态跨会话保留。

**与 ClickHouse 的对比**

DuckDB 和 ClickHouse 都是 OLAP 数据库，但架构前提完全不同：
- DuckDB 是嵌入式进程内引擎，ClickHouse 是长驻服务器进程
- DuckDB 仅纵向扩展（单节点），ClickHouse 可横向扩展（分片/副本）
- DuckDB 不支持多并发写入，ClickHouse 原生支持
- DuckDB 适合即席查询和探索分析，ClickHouse 适合实时分析服务

PostHog 同时使用两者：ClickHouse 处理热分析数据（漏斗、趋势、留存），DuckDB 处理数据仓库的即席查询。

**与 Postgres 的对比**

DuckDB 和 Postgres 的差异本质上是 OLAP 与 OLTP 的设计决策 masterclass：
- 行式 vs 列式存储
- B-tree 堆 vs zone map (min-max 索引)
- Volcano 模型（一次拉一行） vs 向量化执行（一次处理 2048 行）
- 客户端-服务器 vs 嵌入式

**与 SQLite 的对比**

DuckDB 常被称为 "SQLite of OLAP"，但核心特质不是"本地性"，而是"便携性 + 分析马力"。SQLite 的杀手锏是"本地 + 极小 + 零配置"（750 kB），DuckDB 的杀手锏是"便携 + 分析"（20 MB）——它可以直接查询 S3 上的 Parquet 文件，不需要数据在本地。

DuckDB 团队同时也是 DuckLake 的创建者。DuckLake 可以看作是 DuckDB 设计哲学在数据湖格式领域的延伸：保持简单、进程内可用、用 SQL 作为统一接口，同时把元数据管理从复杂的文件协议中解放出来。

来源：[[sources/ducklake-manifesto]] · [[sources/ducklake-v1-0-announcement]] · [[sources/duckdb-vs-clickhouse-posthog]] · [[sources/duckdb-vs-postgres]] · [[sources/duckdb-vs-sqlite]]

相关页面：[[topics/ducklake]] · [[entities/ducklake]] · [[topics/duckdb-vs-clickhouse]] · [[entities/posthog]]
