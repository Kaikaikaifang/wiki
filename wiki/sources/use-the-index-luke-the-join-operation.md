---
title: Use The Index, Luke：连接操作
type: source
tags:
  - SQL
  - 连接
  - 索引
  - 性能
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/join)

## 核心视角

这一部分的重要启发是：**join 是否快，取决于数据库打算用哪种 join 算法，而不同算法对应的索引策略并不一样。**

## 三类连接策略

- **Nested Loops**：外层每出一行，就去内层查一次；
- **Hash Join**：先把一侧装进哈希表，再用另一侧探测；
- **Sort-Merge Join**：把双方都整理成有序流，再合并。

## 索引策略为何不同

- 对 **nested loops**，内表的 join key 索引非常关键，因为它要被反复探测；
- 对 **hash join**，join key 索引未必是重点，更重要的是索引独立的 `where` 过滤条件，缩小进入哈希表的候选集；
- 对 **sort-merge join**，索引的价值更多在于提前提供顺序，减少额外排序。

## ORM 视角的补充

书里借 N+1 问题和 partial objects 说明，很多 ORM 性能问题并不神秘，本质上只是把某种连接策略的成本放大了。特别是 nested loops 型访问，如果在应用层重复触发，会把 B-tree 遍历和回表次数成倍放大。

## 这一章的价值

它把“给 join 列建索引”这种粗糙建议，推进成了更精确的问题：**当前执行计划到底在做哪种 join，而索引该服务哪个动作？**

---

相关页面：[[sources/use-the-index-luke]] · [[topics/sql-join-performance]] · [[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]]
