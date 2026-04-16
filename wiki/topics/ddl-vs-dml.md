---
title: DDL vs DML
type: topic
tags:
  - 数据库
  - SQL
  - DDL
  - DML
source_count: 1
updated: 2026-04-16
---

# DDL vs DML

> `DDL` 改结构，`DML` 改数据。理解这个区分，才能看懂为什么 ClickHouse 里的 `ON CLUSTER` 只负责一类语句，不负责另一类语句。

## 先说结论

- **DDL** 是 `Data Definition Language`，数据定义语言，负责定义或修改数据库结构；
- **DML** 是 `Data Manipulation Language`，数据操作语言，负责写入、更新或删除数据内容。

最短的理解方式就是：

- `DDL = 改表、改库、改结构`
- `DML = 改行、改记录、改数据`

## DDL 常见例子

- `CREATE TABLE`
- `ALTER TABLE`
- `DROP TABLE`
- `TRUNCATE`
- `CREATE DATABASE`

这些语句改的是“数据库长什么样”，而不是某一行数据的值。

## DML 常见例子

- `INSERT`
- `UPDATE`
- `DELETE`

这些语句改的是“表里存了什么数据”。

## 放到 ClickHouse 的 `ON CLUSTER` 里理解

[[sources/clickhouse-replication-and-scaling]] 里最重要的边界之一，就是：

- `ON CLUSTER` 可以把 **DDL** 同步发到整个集群；
- `ON CLUSTER` 不承担 **DML** 分发。

也就是说，在 ClickHouse 里通常是：

- 用 `CREATE TABLE ... ON CLUSTER` 把表结构建到所有相关节点；
- 用 `Distributed` 表去承接跨分片的 `INSERT` 与查询。

## 为什么这个区分重要

如果不区分 DDL 和 DML，就很容易误以为：

- 既然 `ON CLUSTER` 能把建表发到所有节点，
- 那它也应该能把写入数据自动发到所有节点。

但 ClickHouse 的设计不是这样：

- **结构变更怎么扩散**，是一类问题；
- **数据写入怎么路由**，是另一类问题。

前者交给 `ON CLUSTER`，后者交给分片拓扑、复制机制和 `Distributed` 表。

## 对我的启发

这个概念看起来基础，但一旦进入分布式数据库语境就很关键。它提醒我，很多“集群能力”其实都在明确区分：

- 哪些是元数据操作；
- 哪些是数据路径操作。

把这两类问题混在一起，通常就会误读文档或误判系统行为。

---

来源：[[sources/clickhouse-replication-and-scaling]]

相关页面：[[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]] · [[sources/clickhouse-replication-and-scaling]]
