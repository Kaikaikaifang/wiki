---
title: Use The Index, Luke：数据修改
type: source
tags:
  - SQL
  - 写入
  - 索引
  - 数据库
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/dml)

## 这部分纠正了什么

前面几章都在讲索引如何提升读取性能，而这里提醒：**索引本质上是冗余，因此每一个索引都在给写路径加成本。**

## 三类写操作的代价

- **`insert`**：每个索引都要找到正确叶子节点并插入，必要时触发节点分裂；
- **`delete`**：删行也要同步从相关索引移除记录；
- **`update`**：若修改了被索引列，往往相当于先删旧条目再插新条目。

## 最重要的结论

表上的索引数量会直接放大写入成本。对 `insert` 尤其明显，因为它本身没有 `where` 子句，无法像查询那样直接从索引受益。

## 对应用设计的提醒

- 不要为了局部查询收益无节制加索引；
- ORM 生成的“全列更新”要特别小心，因为它可能让更多索引被迫维护；
- 真正需要批量导入时，临时减少索引有时比硬扛更合理。

---

相关页面：[[sources/use-the-index-luke]] · [[topics/index-maintenance-tradeoffs]] · [[topics/sql-indexing]] · [[topics/b-tree-indexes]]
