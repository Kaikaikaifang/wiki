---
title: DuckDB 与 SQLite 对比
type: source
tags: [DuckDB, SQLite, OLAP, OLTP]
source_count: 1
updated: 2026-06-13
---

PostHog 写的 DuckDB 与 SQLite 对比，核心问题是：**DuckDB 真的配得上"SQLite of OLAP"这个称号吗？**

**答案是：大部分 yes，但 DuckDB 的核心特质不是"本地性"，而是"便携性 + 分析马力"。**

**架构对比：**

| 维度 | SQLite | DuckDB |
|------|--------|--------|
| 定位 | OLTP（事务型） | OLAP（分析型） |
| 存储 | 行式 | 列式 |
| 体积 | 750 kB | 20 MB |
| 查询优化 | 规则为主，保守 | 成本优化，自动向量化 |
| 并发 | 单写多读（WAL 模式） | 单写多读（MVCC） |
| 多线程 | 单线程 | 多线程并行扫描/聚合/Join |
| 数据位置 | 本地文件 | 本地文件或远程对象存储 |

**关键区分：**

SQLite 的杀手锏是**"本地 + 极小 + 零配置"**——在没有网络、没有服务器的任何环境下提供事务型数据库。它用在移动端、浏览器、飞机操作系统里。

DuckDB 的杀手锏是**"便携 + 分析"**——你不需要数据在本地，只需要查询引擎在本地。它可以直接查询 S3 上的 Parquet 文件。所以 DuckDB 不是"SQLite of OLAP"那样强调本地性，而是强调**把分析能力带到数据所在的地方**。

**在各自品类中的独特性：**
- SQLite：在 OLTP 世界里，它抛弃了客户端-服务器架构，变成了"库"
- DuckDB：在 OLAP 世界里，它抛弃了分布式服务器，变成了"单机分析引擎"

两者共享的是**哲学**（嵌入式、零配置、库而非服务），但**用途**完全不同。

来源：[[sources/duckdb-vs-sqlite]]

相关页面：[[entities/duckdb]] · [[entities/posthog]]
