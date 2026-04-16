---
title: ClickHouse 复制与扩展
type: source
tags: [数据库, ClickHouse, 分片, 副本]
source_count: 1
source_file: raw/articles/clickhouse-replication-and-scaling.md
author: ClickHouse
published: 2026-04-16
updated: 2026-04-16
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/architecture/cluster-deployment)

## 核心结论

这篇官方示例把 ClickHouse 的横向扩展讲得很清楚：**分片负责扩容，副本负责容灾，Keeper 负责协调，`Distributed` 表负责跨分片入口。** 典型示例是 `2 shards × 2 replicas + 3-node Keeper`。

## 关键区分

- **Shard（分片）**：把数据拆开，降低单机存储与 I/O 压力，并让查询可以并行跑在多个节点上。
- **Replica（副本）**：为同一 shard 保留冗余拷贝，用于故障转移和提高可用性。
- **Keeper**：存放复制与协调所需的状态。文档明确建议生产环境使用独立 Keeper 主机，而不是和 ClickHouse Server 混跑。

## 官方示例真正教会我的事

### `remote_servers` 是拓扑声明

文档用 `remote_servers` 中的 `<shard>` 与 `<replica>` 定义集群结构，并把它同时当作 `ON CLUSTER` 分布式 DDL 的模板。这意味着“拓扑配置”不只是给查询路由看，也是给运维动作看。

### `internal_replication = true` 很关键

当 `internal_replication = true` 时，写入只会先落到某个 shard 的一个副本，再由复制机制同步到同 shard 的其他副本。也就是说，它避免了客户端向同一 shard 的所有副本重复写入。

### `ON CLUSTER` 不是 DML 分发器

文档特别提醒：`ON CLUSTER` 只适用于 DDL，不适用于 `INSERT`、`UPDATE`、`DELETE` 这类 DML。要跨分片写入，应该创建 `Distributed` 表，把它当作整个集群的统一入口。

## 代价与边界

- **优点**：并行查询、单节点压力更低、单节点故障可容忍。
- **代价**：副本会显著增加存储开销；双节点故障在某些分布下仍可能让集群不可用。

## 对我的启发

这篇文档让我把“多副本”和“分片”从两个松散词汇变成了明确的职责分工：

- 先问是否需要更多容量与并行度，再决定是否分片；
- 再问是否需要容灾与持续服务，再决定副本数；
- 最后再看 Keeper、Distributed 表和 `ON CLUSTER` 怎么把这些部件接起来。

---

相关页面：[[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]] · [[sources/clickhouse-manage-and-deploy]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-multi-region-replication]]
