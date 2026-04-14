---
title: Use The Index, Luke — Clustering Data
type: source
tags:
  - SQL
  - 聚簇
  - 索引
  - 性能
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-14
---

# Use The Index, Luke — Clustering Data

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/clustering)

## 第二种索引力量

这一章把“聚簇”称为索引的第二种力量。它关注的不是如何更快找到第一条命中记录，而是**如何让接下来要访问的多条记录尽量落在相近的数据块里**，从而减少回表 IO。

## 关键概念

- **clustering factor**：索引顺序与表中物理顺序的贴近程度；
- **index-only scan**：索引本身就包含查询所需列，于是完全不回表；
- **clustered / index-organized table**：把表直接按索引结构组织。

## 这一章最有价值的判断

很多查询之所以慢，不是因为找不到正确索引项，而是因为找到了太多分散的 `ROWID`，必须去不同数据块里一条条拿完整行。改善这件事，要么让数据更聚簇，要么让索引覆盖更多查询所需列。

## 代价也很真实

覆盖索引和聚簇优化都不是免费午餐：索引会更大、维护更重、设计更激进，所以更适合用于高频关键查询，而不是到处盲目铺开。

---

相关页面：[[sources/use-the-index-luke]] · [[topics/b-tree-indexes]] · [[topics/sql-indexing]] · [[topics/index-maintenance-tradeoffs]]
