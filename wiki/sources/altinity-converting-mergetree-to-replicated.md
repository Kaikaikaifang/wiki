---
title: Altinity Converting MergeTree to Replicated
type: source
tags: [数据库, ClickHouse, 复制, 迁移]
source_count: 1
source_file: raw/articles/altinity-converting-mergetree-to-replicated.md
author: Altinity
published: 2026-04-16
updated: 2026-04-16
---

# Altinity Converting MergeTree to Replicated

来源：[[entities/clickhouse]] · [原文](https://kb.altinity.com/altinity-kb-setup-and-maintenance/altinity-kb-converting-mergetree-to-replicated/)

## 核心结论

这篇 KB 的价值在于它没有把“从 `MergeTree` 转成 `ReplicatedMergeTree`”描述成单一路径，而是把它当成一个**按数据量、停机窗口和风险偏好选择迁移手法**的问题。

## 它给出的迁移路线图

- 小表可以直接 `INSERT INTO new_table SELECT * FROM old_table`；
- 大表更适合旁路创建新表，再用 `ATTACH PARTITION ... FROM ...` 挂分区；
- 也可以走原地改造、备份恢复，或者新版本里的 `ATTACH TABLE ... AS REPLICATED`。

## 为什么旁路 + `ATTACH PARTITION` 很重要

这篇文档最实用的点，是明确指出这种方式：

- 基本不额外占用同等量磁盘；
- 对大表更现实；
- cutover 时只需要 rename；
- 原表还可以暂时保留成便宜的回滚缓冲。

也就是说，它不是在教一个“语法技巧”，而是在给**大表生产迁移的操作模板**。

## 对我的启发

官方文档更多是在告诉我“支持怎么转”，Altinity 这篇文章则更像在告诉我“面对真实生产表时，哪条路更像人会走的路”。这两者放在一起，刚好能把“可行”与“可操作”区分开来。

---

相关页面：[[topics/clickhouse-replicated-engines-and-conversion]] · [[entities/clickhouse]] · [[sources/clickhouse-replicated-table-engines]] · [[sources/clickhouse-attach-as-replicated]]
