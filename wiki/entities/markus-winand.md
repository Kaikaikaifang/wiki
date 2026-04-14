---
title: Markus Winand
type: entity
tags:
  - SQL
  - 数据库
  - 性能
  - 作者
source_count: 1
updated: 2026-04-13
---

# Markus Winand

> 以 [[sources/use-the-index-luke]] 和 SQL 性能教学著称的数据库作者与讲师。

## 在这个 wiki 中的重要性

Markus Winand 的价值，不只是提供了一堆“怎么建索引”的技巧，而是把 SQL 性能问题重写成一个**开发者可操作的心智模型**：

- 索引的本质是 B-tree 与叶子节点链；
- 慢索引通常不是“索引坏了”，而是扫描范围太大或回表太多；
- `where`、`join`、`order by` 与分页的写法，直接决定数据库是否能有效利用索引；
- 执行计划是性能调优的第一现场；
- 很多性能问题靠正确索引即可解决，未必要先诉诸更多硬件。

## 风格特点

他的讲解风格有两个特点很突出：

- **开发者导向**：总是从查询写法出发，而不是从 DBA 配置出发。
- **跨数据库对照**：虽然主要讲 B-tree 的共性，但会不断对照 Oracle、PostgreSQL、MySQL、SQL Server、Db2、SQLite 等系统的执行计划术语差异。

## 在我的知识图谱中的位置

如果说 [[entities/andrej-karpathy]] 帮我建立了“LLM 如何组织知识”的视角，那么 Markus Winand 提供的是另一条更底层的软件工程主线：**如何围绕真实查询模式设计数据访问路径。**

---

来源：[[sources/use-the-index-luke]]

相关页面：[[topics/sql-indexing]] · [[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-join-performance]]
