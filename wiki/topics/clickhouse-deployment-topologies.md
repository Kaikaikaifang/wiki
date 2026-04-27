---
title: ClickHouse 部署拓扑
type: topic
tags: [数据库, ClickHouse, 部署, 架构]
source_count: 9
updated: 2026-04-27
---

> 我对 ClickHouse 部署最强烈的感受是，它逼你放弃“有没有标准架构”这种偷懒问法，转而老老实实回答自己到底想解决哪一类瓶颈。

## 核心判断

ClickHouse 的部署问题不能只问“单机还是集群”。更准确的问法是：

- 需要的是**扩容**还是**容灾**；
- 需要的是**更低单机压力**还是**更低存储成本**；
- 需要的是**同地域高可用**还是**跨地域冗余**；
- 需要的是**热数据高性能**还是**冷数据低成本长期保留**。

官方文档给出的答案不是一套唯一架构，而是一组可组合能力：`ReplicatedMergeTree`、`Distributed`、ClickHouse Keeper、`storage_policy`、对象存储、filesystem cache。我很喜欢这种表达方式，因为它要求使用者自己承担架构判断，而不是期待文档替你选型。

## 分片与副本不是一回事

[[sources/clickhouse-replication-and-scaling]] 让我把这两个常被混说的词真正拆开了。很多部署讨论一开始就糊掉，就是因为扩容和容灾根本不是同一个问题。

- **分片**解决的是单机容量、I/O 和并行度上限；
- **副本**解决的是节点故障下的数据冗余与服务连续性。

因此，一个比较自然的扩展顺序往往是：

1. 单机先跑到接近容量或并发瓶颈；
2. 需要横向扩容时增加 shard；
3. 需要高可用时再给每个 shard 增加 replica。

## 先纵向扩展，再横向扩展

[[sources/clickhouse-13-mistakes]] 又补上了一个我觉得很重要的判断：ClickHouse 新手经常过早水平扩展。因为 Kubernetes 让“多节点部署”看起来很自然，很多人会直接跳到几十个节点、复杂编排和大量 shard。

但 ClickHouse 本来就很擅长吃满单机资源。过滤、排序、聚合这些分析查询阶段通常可以在单机内并行化，优先纵向扩容往往更便宜、运维面更小，join 等操作也少了跨网络搬数据的成本。

这不是说不要 shard，而是不要把 shard 当成默认起点。更稳的顺序是：

1. 先确认单机资源是否真的成为瓶颈；
2. 需要高可用时加副本；
3. 容量、I/O 或并行度超过单机上限时再加 shard；
4. 引入 shard 后，重新评估跨 shard 聚合、Top-N、写入路由和 Keeper 压力。

## Keeper、`Distributed` 与 `ON CLUSTER` 的角色分工

这套拓扑能工作，不只是因为“多几台机器”，而是因为三个角色分得很清楚：

- **Keeper**：维护复制与协调状态，生产环境最好独立部署；
- **`Distributed` 表**：承担跨 shard 的查询和写入入口；
- **`ON CLUSTER`**：负责把 DDL 发到整个集群，但不承担 DML 分发。

这是个很重要的边界。很多系统把“集群”想成一个黑箱，而 ClickHouse 明确要求你区分：

- 元数据变更怎么扩散；
- 数据写入怎么路由；
- 副本同步又依赖什么协调层。

## Keeper 与 ZooKeeper 的选型边界

[[sources/clickhouse-keeper]] 把这个边界写得很清楚：ClickHouse Keeper 与 ZooKeeper 协议兼容，但它不是要成为通用 ZooKeeper 生态的完整替身。

这让我对部署拓扑又多了一层理解：

- 如果协调层只为 ClickHouse 服务，Keeper 往往是更自然的默认项；
- 如果组织已经把 ZooKeeper 作为跨系统共享的基础设施，继续沿用 ZooKeeper 也可能更稳；
- 从 ZooKeeper 迁移到 Keeper 时，应把它当作一次受控切换，而不是“先混着跑再慢慢替换”。

也就是说，协调层选型不是单纯的“技术优劣”问题，而是**专用化与通用化**之间的运维边界选择。对我来说，这种判断比单点 benchmark 有意义得多。

## Operator 下的 replicated 默认值

[[sources/clickhouse-operator-introduction]] 让我补上了 Kubernetes 语境里很重要的一层：

- Operator 推荐生产环境使用 `Replicated` 数据库引擎；
- 它会帮你同步数据库定义；
- 但表数据复制仍然依赖 ClickHouse 自己的复制机制。

这意味着“用了 Operator”不等于“复制问题已经自动解决”。如果目标是副本级高可用，那么数据库层和表层都要选对 replicated 路径。

[[sources/oneuptime-replicated-replacingmergetree]] 还把表层 replicated 的操作面补得更具体：每个副本需要通过 `{shard}`、`{replica}` 这类宏落到稳定的 Keeper 路径上，运行后还要通过 `system.replicas` 观察 `absolute_delay`、`queue_size`、`parts_to_check` 等状态。也就是说，表引擎选择不是 DDL 结束时就完成了，复制队列和合并健康度会持续决定这张表是否真的处在高可用状态。

## 存算分离是另一条独立维度

[[sources/clickhouse-separation-storage-compute]] 说明，ClickHouse 可以把 `MergeTree` 数据放在 S3 等对象存储上，让计算和存储独立扩缩容。这个决策和“要不要分片”并不是同一个问题：

- 分片主要解决单机处理能力不够；
- 存算分离主要解决数据规模大、冷数据多、对象存储更省钱。

官方还明确提醒，这条路线更复杂，自管成本更高。也就是说，它不是默认升级路径，而是当对象存储的成本优势和弹性价值足够大时才值得引入。

## 冷热数据分层本质上是存储策略组合

[[sources/clickhouse-external-disks-for-storing-data]] 没把“冷热分层”包装成单独概念，但它给出了足够完整的底层原语。这里的结论有一部分是**我基于文档做的归纳**：

- **冷层**：对象存储，承接大容量、低成本数据；
- **热层**：本地磁盘或 filesystem cache，承接会重复访问的工作集；
- **策略绑定**：表通过 `storage_policy` 绑定到具体介质组合。

所以，ClickHouse 的冷热分层并不是传统意义上强约束的多层存储产品，更像“把容量层和性能层手工拼起来”的可组合架构。

## 多地域复制是网络预算问题

[[sources/clickhouse-multi-region-replication]] 给出一个非常实用的边界：跨地域复制是支持的，但地域间时延应保持在两位数毫秒。否则，写路径会因为共识和复制而明显变慢。

这意味着多地域副本更适合：

- 区域级容灾；
- 较近地域之间的高可用冗余；
- 明确接受更高写延迟的部署。

它不适合把全球多地域都纳入同一个低延迟写集群想象中。

## 一个实用的部署判断框架

- **先纵向扩容或加副本**：当单机资源仍可提升，或核心诉求是高可用、节点故障自动接管、避免单节点损坏导致服务中断。
- **再加分片**：当单机已经扛不住容量、I/O 或并行查询压力。
- **考虑存算分离**：当冷数据很多、本地盘成本高、需要把容量层转移到对象存储。
- **加冷热分层**：当远端对象存储已经引入，但又需要本地缓存保证热工作集性能。
- **慎用多地域**：当跨地域需求是真实存在的容灾需求，而不是模糊的“全球部署更高级”。

## 对我的启发

这些文档把 ClickHouse 从“快的列式数据库”扩展成了一个更完整的系统形象：它不仅会算得快，还要求使用者明确理解**拓扑、协调、介质、缓存与网络时延**之间的连锁关系。

这也让我意识到，分析数据库的部署优化，和 OLTP 世界那种“主从 + 索引 + 连接池”思路并不一样。这里更像是在拼一台面向分析工作负载的分布式机器。

---

来源：[[sources/clickhouse-manage-and-deploy]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-external-disks-for-storing-data]] · [[sources/clickhouse-multi-region-replication]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]] · [[sources/clickhouse-13-mistakes]] · [[sources/oneuptime-replicated-replacingmergetree]]

相关页面：[[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-common-pitfalls]] · [[entities/clickhouse]] · [[entities/clickhouse-keeper]] · [[entities/zookeeper]] · [[sources/clickhouse-manage-and-deploy]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-external-disks-for-storing-data]] · [[sources/clickhouse-multi-region-replication]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]] · [[sources/clickhouse-13-mistakes]] · [[sources/oneuptime-replicated-replacingmergetree]]
