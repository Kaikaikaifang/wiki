---
title: ClickHouse 复制表引擎
type: source
tags: [数据库, ClickHouse, ReplicatedMergeTree, 复制]
source_count: 1
source_file: raw/articles/clickhouse-replicated-table-engines.md
author: ClickHouse
published: 2026-04-16
updated: 2026-04-16
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/engines/table-engines/mergetree-family/replication#converting-from-mergetree-to-replicatedmergetree)

## 核心结论

这段官方文档说明，从 `MergeTree` 转成 `ReplicatedMergeTree` 是**受支持的正式迁移路径**，但它并不是“一条命令自动善后”的无状态切换。

## 官方给出的三类路径

- **`ATTACH ... AS REPLICATED`**：适合已经 detach 的表；
- **`convert_to_replicated` + 重启**：适合可以接受重启，并且 `default_replica_path` / `default_replica_name` 已配置妥当的场景；
- **手工迁移**：rename 旧表、新建 replicated 表、移动数据到 `detached`、再 `ATTACH PARTITION`。

## 文档暴露出的运维前提

- 如果多份数据不一致，要先同步或只保留一个权威副本；
- 需要知道数据目录、replica path 这类底层细节；
- 这件事本质上仍然是一次受控迁移，而不是普通 DDL。

## 对我的启发

这让我更愿意把“从非复制表转成复制表”视为一类**迁移工程**，而不是一类 schema 改动。因为它牵涉的不只是引擎名字变化，而是底层元数据路径、数据一致性和恢复语义。

---

相关页面：[[topics/clickhouse-replicated-engines-and-conversion]] · [[entities/clickhouse]] · [[sources/clickhouse-attach-as-replicated]] · [[sources/altinity-converting-mergetree-to-replicated]]
