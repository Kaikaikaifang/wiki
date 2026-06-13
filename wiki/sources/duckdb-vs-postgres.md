---
title: DuckDB 与 Postgres 对比
type: source
tags: [DuckDB, Postgres, OLAP, OLTP]
source_count: 1
updated: 2026-06-13
---

PostHog 写的 DuckDB 与 Postgres 对比，本质上是**OLAP 与 OLTP 的设计决策 masterclass**。两者几乎在每一个层面都走了不同路径。

**核心差异：**

| 维度 | Postgres (OLTP) | DuckDB (OLAP) |
|------|----------------|---------------|
| 存储 | 行式 (row-based) | 列式 (column-based) |
| 数据结构 | 堆 + B-tree | 列存 + zone map (min-max 索引) |
| 查询执行 | Volcano 模型（一次拉一行） | 向量化执行（一次处理 2048 行） |
| 架构 | 客户端-服务器 | 嵌入式/进程内 |
| 写入优化 | 事务、高并发小写入 | 批量加载、分析型查询 |
| 查询优化 | 规则为主，保守稳定 | 成本优化，贪婪算法 |
| 扩展 | 垂直 + 水平（分区、Citus） | 仅垂直（单机） |
| 存储耦合 | 数据在数据库内 | 数据可解耦（直接查询外部 Parquet/CSV） |

**DuckDB 的杀手锏：解耦存储**

DuckDB 可以查询存储在 S3 上的 TB 级 Parquet 文件，而本地服务器只有 4GB RAM。它只读取查询需要的列和 row group，用临时数据结构（zone map、列缓冲）在内存中组织。这让"小服务器分析大数据"成为可能。

**Postgres Wire Protocol 与 Duckgres**

DuckDB 不是 Postgres，但 PostHog 开源了 Duckgres——一个 Postgres 协议包装器，让 DuckDB 看起来像 Postgres。这让 BI 工具、dbt、ORM 可以直接连接 DuckDB。

**PostHog 的三数据库栈：**
- **Postgres**：应用状态、用户数据、source of truth
- **ClickHouse**：实时分析（热数据）
- **DuckDB**：数据仓库（即席查询，通过 Duckgres 暴露）

来源：[[sources/duckdb-vs-postgres]]

相关页面：[[entities/duckdb]] · [[entities/clickhouse]] · [[entities/posthog]]
