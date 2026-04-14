---
title: B-Tree Indexes
type: topic
tags:
  - SQL
  - BTree
  - 索引
  - 数据库
source_count: 2
updated: 2026-04-13
---

# B-Tree Indexes

> 用“树遍历 + 叶子链表 + 回表”理解为什么索引既能快，也能慢。

## 基本结构

[[sources/use-the-index-luke]] 对 B-tree 的解释非常清楚：数据库索引不是一张简单的有序表，而是两层结构的结合：

- **平衡树**：负责快速找到扫描起点；
- **叶子节点链表**：负责按顺序继续遍历后续条目。

叶子节点里保存的是索引键以及指向表行的引用，因此索引本质上是一份**有序冗余副本**。

## 为什么“用了索引”还会慢

慢索引通常不是树坏了，而是出在另外两步：

1. **叶子节点遍历过长**：匹配范围太大，需要沿链表扫很多条目；
2. **回表过多**：每个命中条目都要去表里取完整行，产生大量随机 IO。

因此，一个索引访问通常包含三步：树遍历、叶子扫描、表访问。只有第一步天然有上界；后两步如果失控，查询照样会慢。

## 聚簇因子

索引顺序与表中物理行顺序越接近，回表越可能命中同一批数据块，成本越低。这个相关性常被总结为**clustering factor**。它解释了为什么两个看起来都“用到索引”的执行计划，实际速度可能相差很大。

## 覆盖与索引仅扫描

如果索引本身已经包含查询所需的过滤列与返回列，数据库就可能直接从索引完成查询，不再访问表。这类执行方式通常被称为 **index-only scan** 或 covering behavior。

但这不是免费午餐：

- 索引会变大；
- 写入维护成本会上升；
- 一旦查询又多要一个不在索引里的列，优势可能立刻消失。

## 聚簇表 / IOT

SQL Server 的 clustered index、MySQL InnoDB 的主键组织方式，以及 Oracle 的 index-organized table，都是把“表本身”按索引结构组织起来的做法。它们把聚簇能力推到极致，但也意味着一个表只能有一种主顺序。

## 一个实用提醒

不要把索引理解成“一个开关”。真正重要的是：**你的查询是只做了很短的树遍历，还是还要扫很长叶子链、再回表很多次。**

---

来源：[[sources/use-the-index-luke-anatomy-of-an-index]] · [[sources/use-the-index-luke-clustering-data]]

相关页面：[[topics/sql-indexing]] · [[topics/query-shape-and-index-usage]] · [[topics/index-maintenance-tradeoffs]] · [[topics/sql-execution-plans]]
