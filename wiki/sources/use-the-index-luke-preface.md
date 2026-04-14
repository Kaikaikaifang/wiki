---
title: Use The Index, Luke — Preface
type: source
tags:
  - SQL
  - 索引
  - 数据库
  - 性能
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-14
---

# Use The Index, Luke — Preface

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/preface)

## 核心主张

前言最重要的一句话是：**数据库索引是开发任务。** SQL 把“要什么”与“怎么做”分开，这种抽象在功能层面非常成功，但一到性能问题就不够了。开发者如果完全不理解数据库如何访问数据，就很容易写出功能正确但访问路径糟糕的查询。

## 为什么索引责任在开发者

- **访问模式掌握在应用侧**：真正决定索引形状的，是应用如何过滤、排序、分页和连接数据。
- **DBA 很难逆向还原真实热点**：他们能看到库和机器，却很难天然知道业务最常跑的查询长什么样。
- **索引的价值来自查询路径**：如果不知道查询怎样访问表，就不知道该如何排列多列索引、哪些列值得覆盖、哪里会出现大范围扫描。

## 全书框架

前言同时给出了整本书的结构：

- 先理解 [[sources/use-the-index-luke-anatomy-of-an-index]]；
- 再进入 [[sources/use-the-index-luke-the-where-clause]] 这个主体；
- 接着看可扩展性、连接、聚簇、排序 / 分组、分页与写入代价；
- 最后通过 [[sources/use-the-index-luke-execution-plans]] 和 [[sources/use-the-index-luke-myth-directory]] 建立诊断能力。

## 我的吸收

这一章的价值不在技术细节，而在责任重分配：**SQL 性能不是“数据库后来帮你优化”的问题，而是“查询一开始是不是给数据库设计了正确访问路径”的问题。**

---

相关页面：[[sources/use-the-index-luke]] · [[topics/sql-indexing]] · [[topics/query-shape-and-index-usage]] · [[entities/markus-winand]]
