---
title: Use The Index, Luke 总览
type: source
tags:
  - SQL
  - 索引
  - 数据库
  - 性能
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/table-of-contents)

> 这页保留为整本来源的总览入口；详细内容已拆到章节来源页中。

## 核心判断

这套内容最重要的判断非常明确：**索引设计不是 DBA 事后兜底的工作，而是开发者在设计查询时就必须承担的应用层职责。** 因为决定索引好坏的，不是磁盘型号或机器规格，而是应用到底怎样写 `where`、`join`、`order by` 与分页查询。

## 全书结构

本次摄入的是目录页及其下 89 个相关章节。为了便于查询与归档，现已拆成以下章节来源页：

- [[sources/use-the-index-luke-preface]] — 前言：为什么索引是开发任务
- [[sources/use-the-index-luke-anatomy-of-an-index]] — 索引结构、叶子节点、B-tree 与慢索引
- [[sources/use-the-index-luke-the-where-clause]] — `where` 谓词设计、范围、`LIKE`、函数与反模式
- [[sources/use-the-index-luke-testing-and-scalability]] — 数据量增长、负载与真正的可扩展性
- [[sources/use-the-index-luke-the-join-operation]] — nested loops、hash join、sort-merge join 的索引策略
- [[sources/use-the-index-luke-clustering-data]] — 聚簇因子、覆盖索引与 index-only scan
- [[sources/use-the-index-luke-sorting-and-grouping]] — 索引支持排序、分组与 pipelined 执行
- [[sources/use-the-index-luke-partial-results]] — Top-N、seek pagination 与 offset 的局限
- [[sources/use-the-index-luke-modifying-data]] — `insert`、`update`、`delete` 的索引维护成本
- [[sources/use-the-index-luke-execution-plans]] — 跨数据库执行计划阅读方法
- [[sources/use-the-index-luke-myth-directory]] — 常见索引与 SQL 性能误区

如果把这些章节再压缩一层，内容大致可归成七组主题：

- **索引结构**：解释 B-tree、叶子节点、树遍历，以及为什么“用了索引”仍可能很慢。
- **谓词设计**：系统讨论等值、范围、`LIKE`、函数、`NULL`、部分索引与常见反模式。
- **执行计划**：把 execution plan 当作数据库的“汇编”，学习区分 access predicate 与 filter predicate。
- **连接性能**：比较 nested loops、hash join、sort-merge join 的适用场景与索引策略。
- **排序 / 分组 / 分页**：说明索引如何避免排序、支持 pipelined `order by`，以及为什么 seek pagination 通常优于 offset。
- **写入代价**：强调索引是冗余结构，会直接拖慢 `insert`、`update`、`delete`。
- **可扩展性与误区**：指出正确索引往往比“加硬件”更能改善响应时间，也反驳了一批常见数据库性能迷思。

## 最值得记住的原则

- **等值优先、范围其次**：多列索引通常先放等值条件，再放范围条件。
- **只缩小真正扫描范围**：决定性能的不是结果集大小，而是数据库为了找到结果必须扫描多少索引项与表行。
- **看执行计划，不靠感觉**：是否用到索引不是二元判断，更重要的是索引是被当作 access path 还是 filter 扫描。
- **避免把列“藏起来”**：函数、拼接、隐式类型转换、日期计算与自作聪明的逻辑，都可能让索引失效。
- **索引不是越多越好**：每多一个索引，写入路径就多一份维护成本。

## 对我的直接启发

这份来源把“索引”从零散技巧整理成了一个完整框架：**先理解 B-tree 的物理与逻辑结构，再用它解释查询形状、执行计划、连接、排序、分页和写入代价。** 它特别适合作为以后判断 SQL 是否“写得可被索引利用”的基线教材。

---

相关页面：[[sources/use-the-index-luke-preface]] · [[sources/use-the-index-luke-anatomy-of-an-index]] · [[sources/use-the-index-luke-the-where-clause]] · [[sources/use-the-index-luke-execution-plans]] · [[topics/sql-indexing]] · [[topics/b-tree-indexes]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-execution-plans]] · [[topics/sql-join-performance]] · [[topics/index-supported-sorting-and-pagination]] · [[topics/index-maintenance-tradeoffs]] · [[entities/markus-winand]]
