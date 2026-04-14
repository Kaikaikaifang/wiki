---
title: Use The Index, Luke — Sorting and Grouping
type: source
tags:
  - SQL
  - 排序
  - 分组
  - 索引
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-14
---

# Use The Index, Luke — Sorting and Grouping

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/sorting-grouping)

## 第三种索引力量

这一章把 pipelined `order by` 称为索引的第三种力量。重点不是单纯“避免排序”，而是**让数据库可以边扫描边返回前几行，而不必先把全量结果准备完。**

## `order by` 与索引顺序

如果索引顺序与查询需要的排序顺序一致，数据库就可能直接借用索引的有序性，省掉昂贵的排序与中间缓冲。这个优化和 `where` 子句会互相影响，所以单独看排序键往往不够，必须看过滤条件与排序条件是否能在同一索引里协同。

## `group by` 的启发

`group by` 通常也需要中间结构，但如果输入天然按分组键有序，就可能避免额外排序，接近流式完成聚合。因此“分组是否能利用索引”本质上仍然是“输入流是不是已经按需要顺序到来”。

## 一个很实用的认知升级

排序和分组不只是结果展示问题，它们直接决定：

- 是否要 materialize 中间结果；
- 是否能以低启动成本返回前几行；
- 分页是否能做成真正高效的 Top-N 查询。

---

相关页面：[[sources/use-the-index-luke]] · [[topics/index-supported-sorting-and-pagination]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-execution-plans]]
