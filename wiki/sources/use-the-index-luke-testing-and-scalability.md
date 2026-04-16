---
title: 可扩展性
type: source
tags:
  - SQL
  - 可扩展性
  - 索引
  - 性能
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/testing-scalability)

## 核心判断

这一章反复强调：**硬件扩容主要提升吞吐，不会神奇修复单条低效查询的访问路径。** 如果查询本身在扫描大量无关索引项或表行，更多机器通常只是缓解，不是根治。

## 可扩展性的正确看法

作者把可扩展性定义成“性能对环境变化的依赖”，而不只是谁家机器更大。对数据库来说，最关键的变化包括：

- 数据量增长；
- 并发负载增加；
- 不同值分布导致的访问路径差异。

## 索引与数据量增长

这一章最有启发的点是：**两条现在都够快的查询，在数据量扩大后可能呈现完全不同的退化速度。**

如果索引只能把一部分条件当 access predicate，随着数据增长，它会被迫扫描越来越大的区间；反过来，真正把访问范围收紧的索引，增长曲线会平滑得多。

## 我的吸收

看这章时，最应该改掉的习惯是：**不要用开发环境里的“目前很快”替代对长期数据规模的判断。** 更靠谱的问题应该是：这条 SQL 在 10 倍、100 倍数据量下会沿着什么曲线变慢？

---

相关页面：[[sources/use-the-index-luke]] · [[topics/sql-indexing]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-execution-plans]]
