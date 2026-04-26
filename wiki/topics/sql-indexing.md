---
title: SQL 索引
type: topic
tags:
  - SQL
  - 索引
  - 数据库
  - 性能
source_count: 10
updated: 2026-04-26
---

> 我越来越不喜欢把“索引优化”说成数据库专家的黑魔法，因为它本质上更像应用开发者是否真正理解自己在怎么访问数据。

## 核心观点

[[sources/use-the-index-luke]] 最重要的主张是：**索引设计是开发任务。** 我觉得这一点几乎值得作为所有 SQL 性能讨论的起点，因为它会直接改变你看待慢查询的责任归属。

原因不复杂：决定索引是否有效的关键信息，是应用会用什么查询路径访问数据，而这恰恰掌握在开发者手里。DBA 可以看到表、统计信息和机器负载，却很难天然知道业务查询的真实热点、分页方式、排序方式与连接模式。换句话说，如果访问路径本身就是歪的，再熟练的运维也只能帮你止血，很难替你改写这个问题。

## 三种“索引力量”

Markus Winand 把索引的价值分成三层。我很喜欢这种讲法，因为它强迫我不再用“有索引 / 没索引”这种过于粗糙的二元判断来思考性能。

- **第一力量**：B-tree 遍历，让数据库快速定位起始位置。
- **第二力量**：数据聚簇，让相近访问的数据尽量集中，减少回表 IO。
- **第三力量**：pipelined `order by`，让数据库不必先读完再排序，而能边扫描边返回前几行结果。

这也解释了为什么“是否用了索引”这个问题太粗糙。真正该问的是：**它到底利用了哪一层力量？** 只要问得足够具体，很多原本抽象的性能问题就会突然变得可诊断。

## 好索引与坏索引的区别

好索引不是指“命中了索引”，而是指它能真正替查询省掉主要成本：

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

这份来源反复强调：很多所谓“可扩展性”讨论，其实在回避索引设计问题。横向扩展能提升吞吐，但**不能神奇地缩短单条低效查询的响应时间**。如果查询把大量无关索引项、表块和排序步骤都卷了进来，硬件只能缓解，不能从根上修正访问路径。我很认同这一点，因为它把“先加资源”从默认反应，重新拉回到了“先理解访问路径”。

## ClickHouse 的主键提醒我不要套用旧直觉

[[sources/clickhouse-13-mistakes]] 让我看到同一个主题在 OLAP 系统里的变体：ClickHouse 的 primary key 不是 B-tree 式点查入口，而是依赖 `ORDER BY` 物理排序的稀疏索引。它的核心价值是让系统少扫 granule、提升压缩效果，而不是为每一行提供精确定位路径。

这让我更确定一件事：所谓“索引能力”不能脱离存储引擎谈。B-tree、稀疏主键、data skipping index 都是在为查询提供访问路径，但它们服务的物理模型完全不同。把 OLTP 的主键直觉直接搬到 ClickHouse，会让人高估点查和 `LIMIT`，低估排序键设计的重要性。

## 一个实用判断句

如果一个 SQL 查询很慢，先不要问“数据库为什么这么慢”，而要先问：**我的查询有没有给数据库一条可被 B-tree 高效利用的路径？**

---

来源：[[sources/use-the-index-luke-preface]] · [[sources/use-the-index-luke-anatomy-of-an-index]] · [[sources/use-the-index-luke-the-where-clause]] · [[sources/use-the-index-luke-testing-and-scalability]] · [[sources/use-the-index-luke-clustering-data]] · [[sources/use-the-index-luke-sorting-and-grouping]] · [[sources/use-the-index-luke-partial-results]] · [[sources/use-the-index-luke-modifying-data]] · [[sources/use-the-index-luke-myth-directory]] · [[sources/clickhouse-13-mistakes]]

相关页面：[[topics/b-tree-indexes]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-execution-plans]] · [[topics/index-maintenance-tradeoffs]] · [[topics/service-db-network-latency-diagnosis]] · [[topics/clickhouse-common-pitfalls]] · [[entities/markus-winand]] · [[sources/clickhouse-13-mistakes]]
