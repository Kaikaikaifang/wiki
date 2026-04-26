---
title: ClickHouse 数据库
type: entity
tags: [数据库, ClickHouse, OLAP, 列式存储]
source_count: 13
updated: 2026-04-26
---

> 我对 ClickHouse 的兴趣，已经不再只是“它是一个跑得很快的分析数据库”，而是它把数据库工程里很多原本被拆开的决策重新摆到了同一张桌面上。

## 在这个 wiki 中的重要性

目前这个 wiki 里的 ClickHouse 内容已经形成几条互补主线。越写我越觉得，ClickHouse 真正有意思的地方不是单点功能，而是它逼着你把“查询、拓扑、复制、存储、网络、成本”这些问题一起看：

- [[sources/clickhouse-query-cache]] 与 [[sources/introducing-the-clickhouse-query-cache]] 讨论**如何减少重复计算**；
- [[sources/clickhouse-replication-and-scaling]] 与 [[sources/clickhouse-multi-region-replication]] 讨论**如何把分析数据库部署成可扩容、可容灾的分布式系统**；
- [[sources/clickhouse-separation-storage-compute]] 与 [[sources/clickhouse-external-disks-for-storing-data]] 讨论**如何让存储介质、成本与冷热数据分层进入架构设计**；
- [[sources/clickhouse-keeper]] 则把问题进一步推进到**协调层到底该如何选型**；
- [[sources/clickhouse-operator-introduction]]、[[sources/clickhouse-replicated-table-engines]] 与 [[sources/clickhouse-attach-as-replicated]] 则把问题继续推进到**生产集群到底该在什么时候选 replicated，引擎选错后又如何迁移**。
- [[sources/clickhouse-13-mistakes]] 则把这些主题拉回到入门阶段最容易被忽略的物理约束：part 合并、稀疏主键、`LIMIT`、物化视图、Keeper 和内存治理。

这让我把“数据库性能”从单一 SQL 优化问题，拆成至少三类工程问题：

- 如何让第一次查询更快；
- 如何让重复查询不必每次重算；
- 如何让整个分析系统在容量、可用性和成本之间取得平衡。

## 从这些文档看到的系统特征

- **OLAP 导向明显**：愿意接受短时不一致的缓存窗口，也愿意通过分片和对象存储换取分析场景下的整体效率。
- **职责边界清楚**：分片管扩容，副本管容灾，Keeper 管协调，`Distributed` 表管跨分片入口。
- **协调层也有专用化取舍**：Keeper 更贴近 ClickHouse 原生路径，ZooKeeper 则保留通用生态与共享基础设施价值。
- **复制也分层**：数据库层的 `Replicated` 解决 schema 同步，表层的 `ReplicatedMergeTree` 解决数据副本。
- **存储策略可组合**：本地盘、对象存储、cache disk、`storage_policy` 可以按工作负载拼出不同拓扑。
- **安全与运维不是附属项**：用户隔离、监控接口、分布式 DDL、网络与升级都被纳入一组完整运维能力。
- **性能来自顺着物理模型设计**：批量写入、低基数分区、合适的 `ORDER BY`、克制使用 mutations 和物化视图，都是让后台 merge、Keeper 和内存池不过载的前提。

这些特征说明 ClickHouse 不是只追求“单条查询快”，而是在构造一台围绕分析工作负载设计的分布式机器。我很喜欢这种系统气质，因为它迫使人停止把数据库仅仅看成一个执行 SQL 的黑盒。

## 在我的知识图谱中的位置

如果说 [[entities/markus-winand]] 帮我建立了“围绕访问路径设计 SQL”的视角，那么 ClickHouse 代表的是另一种数据库工程心智：**围绕分析工作负载设计计算、拓扑与介质。**

它提醒我，数据库优化不仅是索引与执行计划，还是缓存边界、复制拓扑、对象存储、冷热分层与网络时延约束的组合问题。也正因为如此，它在这份 wiki 里的位置越来越像一个“系统级数据库工程”的入口实体，而不是某一篇文档的附属名词。

---

来源：[[sources/clickhouse-query-cache]] · [[sources/introducing-the-clickhouse-query-cache]] · [[sources/clickhouse-manage-and-deploy]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-external-disks-for-storing-data]] · [[sources/clickhouse-multi-region-replication]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]] · [[sources/altinity-converting-mergetree-to-replicated]] · [[sources/clickhouse-replicated-table-engines]] · [[sources/clickhouse-attach-as-replicated]] · [[sources/clickhouse-13-mistakes]]

相关页面：[[topics/query-result-caching]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-common-pitfalls]] · [[topics/sql-indexing]] · [[entities/clickhouse-keeper]] · [[entities/zookeeper]] · [[sources/clickhouse-query-cache]] · [[sources/introducing-the-clickhouse-query-cache]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]] · [[sources/clickhouse-replicated-table-engines]] · [[sources/clickhouse-13-mistakes]]
