---
title: ClickHouse
type: entity
tags: [数据库, ClickHouse, OLAP, 列式存储]
source_count: 2
updated: 2026-04-15
---

# ClickHouse

> 面向 OLAP 与实时分析场景的列式数据库，也是一套非常强调可观测性与系统级性能取舍的数据库产品。

## 在这个 wiki 中的重要性

目前 wiki 里的数据库内容主要来自 [[sources/use-the-index-luke]]，重点是索引、执行计划与访问路径；[[sources/clickhouse-query-cache]] 则补上了另一条不同但互补的主线：**分析型数据库如何通过结果缓存减少重复计算。**

这让我把“数据库性能”拆成至少两类问题：

- 如何让第一次查询更快；
- 如何让重复查询不必每次重算。

ClickHouse 在第二类问题上提供了一个很清晰的工程化答案。

## 从 Query Cache 文档看到的系统特征

- **OLAP 导向明显**：愿意接受一个短暂的不一致窗口，以换取报表和分析查询的低延迟。
- **服务端统一能力**：把查询缓存放进数据库内核，而不是依赖代理或客户端各自实现。
- **安全默认值保守**：默认不跨用户共享缓存，也默认跳过非确定性函数与系统表查询。
- **观测能力完整**：通过 `system.query_cache`、`system.events`、`system.query_log`、`system.metrics` 提供可见性。

这些特征说明 ClickHouse 的设计不是简单追求“快”，而是把**快、可控、安全、可观测**一起纳入产品接口。

[[sources/introducing-the-clickhouse-query-cache]] 还补上了一层很重要的背景：ClickHouse 不只是给出一份“现成配置手册”，而是公开解释了这个功能最初为什么以实验特性出现、为什么选择事务不一致缓存、以及未来希望如何把它扩展成更成熟的缓存子系统。

## 在我的知识图谱中的位置

如果说 [[entities/markus-winand]] 帮我建立了“围绕访问路径设计 SQL”的视角，那么 ClickHouse 代表的是另一种数据库工程心智：**围绕分析工作负载设计计算与复用机制。**

它也提醒我，数据库优化不仅是索引与执行计划，还是缓存边界、一致性模型、权限隔离和运维观测的组合问题。

---

来源：[[sources/clickhouse-query-cache]] · [[sources/introducing-the-clickhouse-query-cache]]

相关页面：[[topics/query-result-caching]] · [[topics/sql-indexing]] · [[sources/clickhouse-query-cache]] · [[sources/introducing-the-clickhouse-query-cache]]
