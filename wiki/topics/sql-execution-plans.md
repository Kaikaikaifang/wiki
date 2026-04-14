---
title: SQL Execution Plans
type: topic
tags:
  - SQL
  - 执行计划
  - 数据库
  - 性能
source_count: 1
updated: 2026-04-13
---

# SQL Execution Plans

> 执行计划是 SQL 性能问题的第一现场，不看 plan 就谈调优，通常只是在猜。

## 为什么它重要

[[sources/use-the-index-luke]] 把 execution plan 比作数据库把 SQL 编译后的“可执行程序”。真正决定性能的，不是 SQL 看起来多优雅，而是优化器最后选了什么访问路径、连接顺序、排序方式和回表策略。

## 最重要的观察点

读执行计划时，最应该盯住的是：

- **是否是 index scan 还是 full table scan**；
- **索引只负责 access，还是还有大量 filter predicate**；
- **有没有明显的 table lookup / rowid fetch**；
- **排序与分组是否需要额外 materialize**；
- **行数估算是否离谱**，因为这会直接影响优化器选路。

## Access predicate 与 filter predicate

这个区分几乎贯穿整套内容：

- **Access predicate**：真正决定扫描从哪开始、到哪结束；
- **Filter predicate**：扫描之后再过滤，不缩小主要访问范围。

一个查询“命中索引”但仍然很慢，常见原因就是：它主要靠 filter predicate 在索引上做事，而不是靠 access predicate 缩小范围。

## 跨数据库术语差异

各数据库命名不同，但底层思想相当接近：

- Oracle 常见 `INDEX RANGE SCAN`、`TABLE ACCESS BY INDEX ROWID`；
- Db2 会明确给出 `START` / `STOP` 与 `SARG`；
- PostgreSQL 常见 `Index Cond` 与 `Filter`；
- MySQL 则要特别小心它“看起来像在用索引”却未必高效的输出风格。

所以读 plan 时不能只盯关键词，要理解它在描述什么动作。

## 执行计划的真正用途

执行计划不是用来“确认数据库很聪明”，而是用来回答几个具体问题：

- 扫描范围为什么这么大？
- 为什么需要这么多回表？
- 为什么排序没被索引消掉？
- 为什么连接走了 hash join 而不是 nested loops？
- 为什么同一条 SQL 在不同数据分布下应该用不同策略？

## 一个实用提醒

每当你觉得“这条 SQL 应该挺快”，先打开执行计划看看数据库是不是也这么想。

---

来源：[[sources/use-the-index-luke]]
相关页面：[[topics/query-shape-and-index-usage]] · [[topics/sql-join-performance]] · [[topics/index-supported-sorting-and-pagination]] · [[topics/sql-indexing]]
