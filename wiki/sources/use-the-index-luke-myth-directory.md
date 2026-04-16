---
title: Use The Index, Luke：性能误区
type: source
tags:
  - SQL
  - 索引
  - 误区
  - 性能
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/myth-directory)

## 这部分在做什么

这一组内容不是增加新技巧，而是在清除错误直觉。它的价值在于：**很多数据库性能问题之所以反复出现，不是因为知识太少，而是因为错误经验太牢固。**

## 被反驳的几类常见迷思

- **索引会“退化”所以要定期重建**：多数情况下这是把慢查询误诊为索引损坏；
- **最左边必须放选择性最高的列**：真正关键是等值 / 范围条件如何影响扫描边界；
- **动态 SQL 一定慢**：需要区分解析成本、执行计划缓存和参数化；
- **`NULL` 不能被索引**：这在不同数据库里并不是绝对命题。

## 为什么这组内容重要

如果不先清理这些误区，就很容易在错误方向上努力：例如反复 rebuild 索引、迷信“高选择性左置”、或者把全文检索问题继续塞给 `LIKE` 和普通 B-tree。

## 我的吸收

这部分很像整本书的“防错层”。它不只是告诉我该做什么，更重要的是告诉我：**哪些看似合理的性能经验，其实会把调优带偏。**

---

相关页面：[[sources/use-the-index-luke]] · [[topics/sql-indexing]] · [[topics/query-shape-and-index-usage]] · [[topics/b-tree-indexes]]
