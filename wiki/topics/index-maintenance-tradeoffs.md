---
title: Index Maintenance Tradeoffs
type: topic
tags:
  - SQL
  - 索引
  - 写入
  - 性能
source_count: 2
updated: 2026-04-14
---

# Index Maintenance Tradeoffs

> 每一个索引都在提升读路径的同时，给写路径增加持续维护成本。

## 索引是冗余结构

[[sources/use-the-index-luke]] 一再强调：索引是冗余副本。正因为它复制了部分表数据，数据库在 `insert`、`delete`、`update` 时就必须同步维护这些结构。

## 写入为什么会变慢

- **`insert`**：每个索引都要找到正确叶子节点并插入，必要时还会分裂节点；
- **`delete`**：删行不只改表，也要从相关索引移除条目；
- **`update`**：如果修改了被索引的列，通常等价于一次删除再一次插入。

因此，索引越多，写入越慢；而且**第一个索引带来的额外成本通常就已经很明显**。

## `update` 的特别提醒

更新语句并不一定会影响所有索引，它主要影响那些包含被修改列的索引。这也是为什么 ORM 若总是生成“全列更新”，会把本来局部的写入成本放大很多。

## Over-indexing

过度索引的典型迹象是：

- 为每个查询症状各补一个新索引；
- 已有复合索引还能覆盖，却又新建相近单列索引；
- 忽视写入成本与存储成本；
- 不愿意删掉冗余或已失去价值的索引。

这份来源更推荐：先理解访问路径，再尽量扩展已有合适索引，而不是不断堆新索引。

## 何时值得激进一点

只有在读收益非常明确时，才值得为了 covering / index-only scan 增加额外列。批量导入场景下，甚至可以考虑暂时移除部分索引、导入后再重建，因为维护成本可能远高于重建成本。

## 一个实用提醒

每次想新增索引时，同时问一句：**它会让哪些写操作变慢，现有索引里有没有更便宜的改法？**

---

来源：[[sources/use-the-index-luke-clustering-data]] · [[sources/use-the-index-luke-modifying-data]]

相关页面：[[topics/sql-indexing]] · [[topics/b-tree-indexes]] · [[topics/query-shape-and-index-usage]] · [[topics/index-supported-sorting-and-pagination]]
