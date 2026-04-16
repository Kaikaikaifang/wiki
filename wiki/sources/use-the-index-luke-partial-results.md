---
title: 分页与 Top-N
type: source
tags:
  - SQL
  - 分页
  - TopN
  - 索引
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/partial-results)

## 核心问题

很多列表页、消息流和搜索页并不需要全量结果，只需要前几条。问题在于，如果数据库必须先排序完全部结果，前几条也会变得很贵。

## 这一章的答案

作者把高效分页建立在 **pipelined `order by`** 之上：先确保索引能按需要的顺序吐出结果，再只取前 N 条。

## Offset 的问题

`offset` 最大的问题是它经常仍要从头数过去，因此：

- 页码越深越慢；
- 新数据插入后，页内容容易漂移；
- 本质上没有真正“跳过”前面那些行。

## Seek Method

更优方案通常是 seek pagination：

- 记住上一页最后一行的排序键；
- 下一页用这个键作为新的范围边界；
- 让数据库从该位置继续扫描。

这样分页就从“跳过很多行”变成了“从一个已知边界继续查找”，也就是索引擅长的问题。

## 一个关键提醒

稳定分页依赖**确定性排序**。如果 `order by` 不能唯一确定行顺序，就必须补 tie-breaker 列，并让索引顺序与之对齐。

---

相关页面：[[sources/use-the-index-luke]] · [[topics/index-supported-sorting-and-pagination]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-indexing]]
