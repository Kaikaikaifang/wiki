---
title: 以 Replicated 方式挂载
type: source
tags: [数据库, ClickHouse, ATTACH, ReplicatedMergeTree]
source_count: 1
source_file: raw/articles/clickhouse-attach-as-replicated.md
author: ClickHouse
published: 2026-04-16
updated: 2026-04-16
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/sql-reference/statements/attach#attach-mergetree-table-as-replicatedmergetree)

这篇文档虽然很短，但它把一个迁移里最容易被低估的问题说得非常透：数据文件已经在盘上，并不意味着复制身份就已经成立。对我来说，这种“短文档里藏着关键边界”的材料特别值得单独记下来。

## 核心结论

`ATTACH TABLE ... AS REPLICATED` 把“原地转换”的入口变得更简单了，但文档同时把一个容易踩坑的点写得很明白：**表本地数据和 Keeper / ZooKeeper 元数据不是同一回事。**

## 这条语句真正做了什么

- 把已经 detach 的 `MergeTree` 表按 replicated 方式重新 attach；
- 使用 `default_replica_path` 与 `default_replica_name` 生成 replicated 表所需参数。

## 它没有替你做什么

- 不会自动修复或生成 Keeper / ZooKeeper 元数据；
- 不会自动处理已有 replicated 表中的 replica 元信息冲突；
- 如果你是在给现有 replicated 表补 replica，本地数据还会被 detach。

因此，`ATTACH` 不是“从普通表秒变高可用表”的魔法命令，而只是把迁移过程里最繁琐的一段手工操作收敛成了标准语法。

## 对我的启发

这篇文档把一个很实用的原则说透了：**只看数据文件转换成功还不够，还得看复制元数据是否和新身份一致。** 这也是为什么生产迁移不能只验证 `ATTACH` 成功，还要验证 `SYSTEM RESTORE REPLICA` 后的真实状态。我很喜欢这种提醒，因为它直接把注意力从“语法成功了没”拉回到“系统身份真的对了吗”。

---

相关页面：[[topics/clickhouse-replicated-engines-and-conversion]] · [[entities/clickhouse]] · [[sources/clickhouse-replicated-table-engines]]
