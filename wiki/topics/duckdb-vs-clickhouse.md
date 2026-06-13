---
title: DuckDB 与 ClickHouse 的互补定位
type: topic
tags: [DuckDB, ClickHouse, OLAP, 数据库选型]
source_count: 3
updated: 2026-06-13
---

> PostHog 的对比文章让我意识到：DuckDB 和 ClickHouse 的竞争不是"谁更快"，而是"谁更适合你的工作负载类型"。两者甚至可以同时存在——就像 PostHog 那样，ClickHouse 处理热分析，DuckDB 处理数据仓库。

## 核心判断：它们不是同一类产品

虽然都是 OLAP 数据库，但 DuckDB 和 ClickHouse 的架构前提完全不同：

| 维度 | DuckDB | ClickHouse |
|------|--------|------------|
| 进程模型 | 嵌入式（进程内） | 服务器（长驻进程） |
| 扩展方向 | 仅纵向（单节点） | 纵向 + 横向（分片/副本） |
| 并发写入 | 不支持 | 原生支持（多线程） |
| 存储 | 本地文件或外部对象存储 | 自管理（MergeTree 家族） |
| 典型用法 | 即席查询、探索分析、ETL | 实时分析、监控、仪表盘 |
| 启动成本 | 零（import duckdb） | 需要部署服务器 |
| 数据规模 | 单机可处理（TB 级） | 集群可处理（PB 级） |

## DuckDB 更适合什么

DuckDB 的核心优势是**"零成本启动 + 数据湖查询"**。

- 直接查询 S3/本地 Parquet 文件，不需要导入
- 用完即销毁，不需要运维
- 与 Python/pandas 生态无缝集成
- 单节点性能在中小数据集上（5M-50M 行）甚至超过 ClickHouse

典型场景：数据分析师在 Jupyter Notebook 里探索数据、BI 工具连接数据仓库做即席查询、ETL 流水线中的轻量级转换。

## ClickHouse 更适合什么

ClickHouse 的核心优势是**"生产级 OLAP 服务"**。

- 持续高吞吐写入（事件流、日志、指标）
- 物化视图预计算聚合
- 多副本高可用
- 重复查询的缓存和优化
- 物化视图、稀疏索引、MergeTree 引擎的完整工具链

典型场景：实时漏斗分析、用户行为监控、日志聚合、时序数据存储。

## PostHog 的实际分工

PostHog 同时使用三个数据库，这是最有价值的参考案例：

- **Postgres**：应用状态、用户数据、source of truth
- **ClickHouse**：热分析数据——漏斗、趋势、留存、路径分析（十亿级事件，近实时）
- **DuckDB**：数据仓库产品——用户的全部数据（通过 Duckgres Postgres 协议包装器让 BI 工具连接）

这个分工说明了一个判断：**ClickHouse 是"在线服务"，DuckDB 是"查询工具"。** 当你需要持续服务查询时选 ClickHouse；当你需要让用户偶尔查询大量数据时选 DuckDB。

## DuckDB 的两种模式

DuckDB 可以工作在两个完全不同的模式：

1. **查询引擎模式**：导入 duckdb → 指向 Parquet/CSV 文件 → 执行 SQL → 销毁。不保留任何状态。这是 DuckDB 最轻量的用法。
2. **数据库模式**：创建 `.duckdb` 持久化文件，包含表、视图、schema。类似 SQLite 的工作方式。

ClickHouse 的对应物是 `clickhouse-local`——一个便携版的 ClickHouse，可以查询本地文件，但官方定位是测试工具，不是生产服务。

## 一个有趣的类比

PostHog 把 ClickHouse 比作"洋葱"，DuckDB 比作"葱"——它们长得很像，但用途完全不同。我觉得这个类比很准确：

- 你不会用葱做洋葱汤（DuckDB 不适合做 ClickHouse 的工作）
- 你不会用洋葱做葱花（ClickHouse 太重了，不适合做 DuckDB 的工作）
- 两者可以同时出现在同一个菜里（PostHog 同时用两者）

## 对我的启发

这个对比让我更清楚：我们在 wiki 里讨论的 ClickHouse 生产迁移、分片决策、冷热分层，都是围绕"在线服务"的运维问题。而 DuckDB 解决的是"分析查询"的问题——不需要分片、不需要 Keeper、不需要冷热分层，只需要把查询引擎指向数据所在的位置。

对于 wandb 这类指标记录场景，如果写入量极大且需要实时查询，ClickHouse 更合适。如果数据已经以 Parquet 形式存在，偶尔需要分析，DuckDB 更合适。

来源：[[sources/duckdb-vs-clickhouse-posthog]] · [[sources/duckdb-vs-postgres]] · [[sources/duckdb-vs-sqlite]]

相关页面：[[entities/duckdb]] · [[entities/clickhouse]] · [[entities/posthog]] · [[topics/ducklake]]
