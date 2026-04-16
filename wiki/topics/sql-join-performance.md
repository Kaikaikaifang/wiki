---
title: SQL 连接性能
type: topic
tags:
  - SQL
  - 连接
  - 数据库
  - 性能
source_count: 2
updated: 2026-04-16
---

> 连接并不天然慢，慢的是不匹配连接算法的索引与查询形状。

## 三种主流连接思路

[[sources/use-the-index-luke]] 把 join 的性能问题拆成三类：

- **Nested Loops**：外层每来一行，就去内层查一次；
- **Hash Join**：先把一侧装进哈希表，再用另一侧去探测；
- **Sort-Merge Join**：把双方都排好序，再像拉链一样合并。

这三种算法没有绝对高下，关键在于查询规模、过滤条件与索引结构是否匹配。

## Nested Loops 的关键

Nested loops 的痛点是重复查内表，因此最关键的是：**让内表上的 join key 能被高效索引访问。**

这也是 ORM 中 N+1 问题之所以昂贵的原因：同一类 B-tree 遍历与回表动作被放大了很多次。

## Hash Join 的关键

Hash join 与 nested loops 的思路几乎相反。它不依赖对 join key 的反复索引查找，所以：

- **给 join key 建索引，并不必然改善 hash join**；
- 更有效的做法是索引独立于 join 的 `where` 过滤条件；
- 另一种优化方式是减少进入哈希表的数据量与列宽。

换句话说，hash join 的关注点更像“先把候选集缩小”，而不是“让单次查找更快”。

## Sort-Merge Join 的关键

如果两边都能以合适顺序提供数据，sort-merge join 就能避免额外排序。此时索引的价值在于**提前提供顺序**。

## 连接顺序与复杂度

多表连接不是一次完成，而是两两组合、逐步形成中间结果。即使逻辑结果相同，连接顺序也会显著影响成本；表越多，可评估的执行计划组合增长越快。因此复杂 join 更依赖：

- 合理的独立过滤条件；
- 稳定的绑定参数；
- 可解释的执行计划。

## 一个实用提醒

调优 join 时，先问“数据库打算怎么连”，再决定索引该服务哪个算法，而不是机械地给所有连接列都补索引。

---

来源：[[sources/use-the-index-luke-the-join-operation]] · [[sources/use-the-index-luke-execution-plans]]

相关页面：[[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]] · [[topics/index-supported-sorting-and-pagination]] · [[topics/sql-indexing]]
