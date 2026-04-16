---
title: ZooKeeper
type: entity
tags: [数据库, ZooKeeper, 协调服务, 分布式系统]
source_count: 1
updated: 2026-04-16
---

# ZooKeeper

> 经典的分布式协调服务，在这个 wiki 里主要作为 ClickHouse Keeper 的对照基线出现。

## 在这个 wiki 中的重要性

ZooKeeper 让我更清楚地看到一个现实：很多“新组件替代旧组件”的问题，真正比的不是单点功能，而是**通用生态与专用集成**之间的取舍。

## 在 ClickHouse 语境中的位置

- 它长期承担 ClickHouse 复制和协调层角色。
- Keeper 与它协议兼容，因此两者天然会被拿来比较。
- 当组织需要一套被多个系统共享的协调基础设施时，ZooKeeper 仍然有现实价值。

## 为什么它没有被简单淘汰

不是因为 Keeper 不够可用，而是因为 ZooKeeper 的价值本来就不只在 ClickHouse 内部。只要团队还依赖它的外部生态、既有脚本和组织经验，它就仍然是合理选择。

---

来源：[[sources/clickhouse-keeper]]

相关页面：[[entities/clickhouse-keeper]] · [[entities/clickhouse]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[sources/clickhouse-keeper]]
