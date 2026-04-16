---
title: ClickHouse Keeper 协调服务
type: entity
tags: [数据库, ClickHouse, Keeper, 协调服务]
source_count: 2
updated: 2026-04-16
---

> ClickHouse 的原生协调服务，用来承接复制元数据、分布式 DDL 与相关集群状态协调。

## 在这个 wiki 中的重要性

Keeper 让我把 ClickHouse 的“高可用”理解得更具体了。很多时候我们说数据库集群有副本、有 `ON CLUSTER`、有分布式表，但这些能力之所以能稳定运作，背后都依赖一个明确的协调层。

## 我目前对它的理解

- 它是**为 ClickHouse 场景定制**的协调服务，而不是通用协调平台。
- 它在协议层面对 ZooKeeper 兼容，因此 ClickHouse 可以沿用熟悉的交互模型。
- 它在生产部署里通常应该被当作独立组件，而不是完全隐藏在数据库节点背后。
- 它的价值不只是“替代 ZooKeeper”，而是把 ClickHouse 官方推荐路径进一步收敛到更原生的运维模型上。

## 它的边界

Keeper 最重要的边界，是**兼容不等于完全等价**。外部生态、混合集群、动态重配置等问题，都需要按 Keeper 自己的文档来判断，而不是默认套用 ZooKeeper 的全部经验。

---

来源：[[sources/clickhouse-keeper]] · [[sources/clickhouse-replication-and-scaling]]

相关页面：[[entities/clickhouse]] · [[entities/zookeeper]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-deployment-topologies]] · [[sources/clickhouse-keeper]]
