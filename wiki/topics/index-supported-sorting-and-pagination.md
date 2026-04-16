---
title: 索引支撑的排序与分页
type: topic
tags:
  - SQL
  - 排序
  - 分页
  - 索引
source_count: 2
updated: 2026-04-16
---

> 索引不只负责查找，还能避免排序、支持流式返回前几条结果。

## `order by` 的第三种力量

[[sources/use-the-index-luke]] 把 pipelined `order by` 称为索引的“第三力量”。它的价值不只是省掉排序，更在于：**数据库可以不等全部结果准备好，就先返回最前面的若干行。**

这对 Top-N 查询、消息列表、时间线与搜索结果页尤其关键。

## `group by` 也可能受益

如果输入本身按分组键有序，数据库就可能避免额外排序，用接近流式的方式完成 `group by`。因此排序键、分组键与过滤键能否在一个索引里协同，非常值得在高频报表或列表页中提前设计。

## `offset` 的问题

`offset` 的语义简单，但性能会随着页码变深而持续变差，因为数据库通常仍要先数过前面那些行。除此之外，它对并发插入也不稳定，容易出现“翻页漂移”。

## Seek Pagination

更好的办法通常是 seek method：

- 记住上一页最后一条记录的排序键；
- 下一页直接用该键作为新的范围边界；
- 让数据库借助索引从这个位置继续往后扫。

这本质上是把分页问题重新表达成一个索引擅长的范围查询问题。

## 排序必须可判定

稳定分页要求确定性排序。仅按非唯一列排序时，同值记录之间的先后并不稳定，因此通常要补一个唯一 tie-breaker，比如主键，并让索引顺序与 `order by` 保持一致。

## 一个实用提醒

如果你的列表页会不断翻到更深页面，优先思考“能否改成 seek pagination”，而不是先接受 `offset` 的线性退化。

---

来源：[[sources/use-the-index-luke-sorting-and-grouping]] · [[sources/use-the-index-luke-partial-results]]

相关页面：[[topics/query-shape-and-index-usage]] · [[topics/sql-execution-plans]] · [[topics/sql-join-performance]] · [[topics/sql-indexing]]
