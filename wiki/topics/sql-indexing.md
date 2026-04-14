---
title: SQL Indexing
type: topic
tags:
  - SQL
  - 索引
  - 数据库
  - 性能
source_count: 9
updated: 2026-04-13
---

# SQL Indexing

> 把索引当作开发者必须掌握的查询设计能力，而不是数据库团队事后补救的技巧。

## 核心观点

[[sources/use-the-index-luke]] 最重要的主张是：**索引设计是开发任务。**

原因不复杂：决定索引是否有效的关键信息，是应用会用什么查询路径访问数据，而这恰恰掌握在开发者手里。DBA 可以看到表、统计信息和机器负载，却很难天然知道业务查询的真实热点、分页方式、排序方式与连接模式。

## 三种“索引力量”

Markus Winand 把索引的价值分成三层：

- **第一力量**：B-tree 遍历，让数据库快速定位起始位置。
- **第二力量**：数据聚簇，让相近访问的数据尽量集中，减少回表 IO。
- **第三力量**：pipelined `order by`，让数据库不必先读完再排序，而能边扫描边返回前几行结果。

这也解释了为什么“是否用了索引”这个问题太粗糙。真正该问的是：**它到底利用了哪一层力量？**

## 好索引与坏索引的区别

好索引不是指“命中了索引”，而是指它能：

- 缩小扫描范围；
- 减少回表次数；
- 尽量复用同一索引完成过滤、排序、分组或部分结果获取；
- 在读收益与写入维护成本之间保持平衡。

坏索引则常见于：

- 列顺序错误；
- 把高频过滤条件写成函数或表达式，遮蔽原始列；
- 为局部问题不断新增索引，造成严重 over-indexing；
- 忽略执行计划，只看结果是否“暂时够快”。

## 索引比加硬件更直接

这份来源反复强调：很多所谓“可扩展性”讨论，其实在回避索引设计问题。横向扩展能提升吞吐，但**不能神奇地缩短单条低效查询的响应时间**。如果查询把大量无关索引项、表块和排序步骤都卷了进来，硬件只能缓解，不能从根上修正访问路径。

## 一个实用判断句

如果一个 SQL 查询很慢，先不要问“数据库为什么这么慢”，而要先问：**我的查询有没有给数据库一条可被 B-tree 高效利用的路径？**

---

来源：[[sources/use-the-index-luke-preface]] · [[sources/use-the-index-luke-anatomy-of-an-index]] · [[sources/use-the-index-luke-the-where-clause]] · [[sources/use-the-index-luke-testing-and-scalability]] · [[sources/use-the-index-luke-clustering-data]] · [[sources/use-the-index-luke-sorting-and-grouping]] · [[sources/use-the-index-luke-partial-results]] · [[sources/use-the-index-luke-modifying-data]] · [[sources/use-the-index-luke-myth-directory]]

相关页面：[[topics/b-tree-indexes]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-execution-plans]] · [[topics/index-maintenance-tradeoffs]] · [[entities/markus-winand]]
