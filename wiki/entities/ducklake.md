---
title: DuckLake 元数据库优先的 Lakehouse 格式
type: entity
tags: [数据湖仓, DuckDB, 数据格式, SQL]
source_count: 3
updated: 2026-06-15
---

DuckLake 是 DuckDB 团队提出的一种 lakehouse 格式，核心设计是把全部元数据放在 SQL 数据库中，而不是像 Iceberg 或 Delta Lake 那样用 JSON/Avro 文件存储。数据文件仍使用开放的 Parquet 格式，存放在对象存储上。

这个设计选择的关键直觉是：既然 lakehouse 的 catalog 层最终需要引入数据库来保证事务一致性，那不如干脆让数据库管理所有元数据。这带来了几个实际优势：

- **低延迟查询规划**：单次查询即可获得文件列表和统计信息，无需多次 S3 往返
- **ACID 事务**：schema 变更、快照创建、数据文件注册都在同一数据库事务中完成
- **小文件问题**：小写入可以"内联"到 catalog 数据库中，避免生成大量微小 Parquet 文件
- **跨表事务**：支持多 schema、多表之间的 ACID 事务

DuckLake 的参考实现是 DuckDB 的 `ducklake` 扩展，支持 SQLite、PostgreSQL 和 DuckDB 作为 catalog 后端。v1.0 于 2026 年 4 月发布，承诺向后兼容。

新增的 [[sources/announcing-ducklake-1-0-on-motherduck]] 还让我看到 DuckLake 的另一个重要侧面：它已经开始被包装成托管 lakehouse 服务，而不是只存在于本地扩展和架构讨论里。MotherDuck 把它组织成 Fully Managed、Bring-Your-Own-Bucket、Bring-Your-Own-Compute 三种形态，说明 DuckLake 的开放格式路线和“元数据归数据库”路线，天然适合长出多引擎与多拥有权模型。

来源：[[sources/ducklake-manifesto]] · [[sources/ducklake-v1-0-announcement]] · [[sources/announcing-ducklake-1-0-on-motherduck]]

相关页面：[[topics/ducklake]] · [[entities/duckdb]] · [[entities/motherduck]]
