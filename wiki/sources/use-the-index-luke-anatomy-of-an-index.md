---
title: Use The Index, Luke — Anatomy of an Index
type: source
tags:
  - SQL
  - 索引
  - BTree
  - 数据库
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-13
---

# Use The Index, Luke — Anatomy of an Index

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/anatomy)

## 章节范围

这一部分覆盖索引结构、叶子节点、B-tree 平衡树，以及“慢索引”的真正来源，是理解整本书的物理基础。

## 关键模型

这组章节把索引拆成两个结构：

- **平衡树**：快速定位到扫描起点；
- **叶子节点双向链表**：按序继续读取后续索引项。

索引因此不是一张静态排序表，而是一个既支持查找、又支持持续插入更新的动态有序结构。

## 为什么索引会慢

作者把一次索引访问分成三步：

1. **树遍历**：找到起始叶子节点；
2. **叶子链扫描**：沿链表读取所有匹配项；
3. **回表**：根据 `ROWID` / `RID` 取回完整行。

真正容易失控的是后两步，而不是树遍历本身。因此“索引变坏了”往往是误诊，真正的问题通常是扫描范围太大或回表太多。

## 这一章给后文的支点

后面关于 `where`、排序、分页、连接和覆盖索引的几乎所有判断，都能回到这里：**好的索引设计，本质上就是缩短叶子扫描并尽量减少回表。**

---

相关页面：[[sources/use-the-index-luke]] · [[topics/b-tree-indexes]] · [[topics/sql-indexing]] · [[topics/sql-execution-plans]]
