---
title: 执行计划
type: source
tags:
  - SQL
  - 执行计划
  - 索引
  - 数据库
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/explain-plan)

这部分虽然被放在附录，但我一点也不觉得它像附属内容。恰恰相反，它更像前面所有索引原则真正落地时的验证器，没有它，前面的判断很容易重新退回感觉流。

## 为什么它是附录却非常重要

这部分虽然被放在附录，但其实是整本书的诊断工具箱。作者把 execution plan 视为数据库执行 SQL 的“汇编结果”，真正的调优必须从这里看起。我很喜欢这个比喻，因为它让执行计划不再像一个 DBA 专属黑箱。

## 这部分教会我的核心区分

- **Access predicate**：决定扫描边界；
- **Filter predicate**：扫描后再过滤；
- **Index scan 与 table access**：必须分开看，不能因为“用了索引”就默认已经高效；
- **行数估算与成本值**：优化器所有选择都建立在这些估算之上。

## 跨数据库阅读方式

作者分别解释了 Db2、MySQL、Oracle、PostgreSQL、SQL Server、SQLBase、SQLite 的输出差异，但底层阅读方法是一致的：

- 看它从哪张表开始；
- 看访问路径是否被真正收紧；
- 看哪里发生排序、聚合或回表；
- 看谓词到底在哪个阶段才生效。

## 这一部分的真正价值

它把“感觉某条 SQL 很慢”转化成了可验证问题：**慢在哪一步、扫描了多少、为什么没有更早过滤、为什么排序没有被索引消掉。** 这正是我想从这类来源里得到的东西：把模糊直觉压成可检查的问题列表。

---

相关页面：[[sources/use-the-index-luke]] · [[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-join-performance]]
