---
title: ReplicatedReplacingMergeTree 用法
type: source
tags: [数据库, ClickHouse, 复制, 去重, 教程]
source_count: 1
source_file: raw/articles/oneuptime-replicated-replacingmergetree.md
author: Nawaz Dhandala
published: 2026-03-31
updated: 2026-04-27
---

来源：[[entities/clickhouse]] · [原文](https://oneuptime.com/blog/post/2026-03-31-clickhouse-replicated-replacingmergetree/view)

## 核心结论

这篇 OneUptime 文章是 `ReplicatedReplacingMergeTree` 的 happy path 教程：先配置 `{shard}`、`{replica}` 这类宏，再建一张带 version 列的 replicated replacing 表，用 `ORDER BY` 表达逻辑身份，用 version 表达新旧顺序，用 `FINAL` 获得 merge 之前的去重视图。

它最有价值的地方不是代码样例本身，而是把这套引擎的四个角色摆清楚了：`ORDER BY` 决定哪些行互相替换，version 决定谁赢，Keeper / ZooKeeper 负责复制协调，`FINAL` 和 `OPTIMIZE ... FINAL` 只是把最终状态提前显现出来的读写工具。

## 一张表里的四个决策

文章的示例表是用户资料：`user_id` 是逻辑身份，`version` 是更新版本，`updated_at` 用来分区。它的核心形状可以概括为：

```sql
ENGINE = ReplicatedReplacingMergeTree(
    '/clickhouse/tables/{shard}/user_profiles',
    '{replica}',
    version
)
PARTITION BY toYYYYMM(updated_at)
ORDER BY user_id;
```

这里有一个很重要的直觉：`ORDER BY user_id` 不是普通意义上的查询排序，而是在告诉 `ReplacingMergeTree` “哪些物理行代表同一个逻辑对象”。如果后面插入同一个 `user_id`、更高 `version` 的行，后台 merge 后旧版本会被折叠掉。

我会把这看成 ClickHouse 里的“追加式更新”：不是原地改一行，而是追加一个更高版本的事实，再让 merge 或查询时 `FINAL` 把它解释成当前状态。

## `FINAL` 是读一致性工具，不是免费开关

文章建议在需要立即看到去重结果时使用 `FINAL`：

```sql
SELECT ...
FROM user_profiles FINAL;
```

这个建议是对的，但要带着成本意识理解。`FINAL` 会在查询时做去重，能绕过“后台 merge 还没发生”的窗口，却也把额外计算压到读路径上。对小表、调试、对账和少量强一致读，它很好用；对高并发大范围查询，把 `FINAL` 当成默认读法通常会把写入侧省下来的复杂度重新转嫁给查询侧。

同理，`OPTIMIZE TABLE ... PARTITION ... FINAL` 能强制某个分区尽快合并去重，但它更像维护动作，不是每次更新后的业务流程。真正稳定的系统应该允许 eventual deduplication 存在，并在确实需要当前状态时显式付出 `FINAL` 的成本。

## 复制状态也必须被纳入模型

这篇文章还提醒了一个容易被教程读者忽略的点：`ReplicatedReplacingMergeTree` 不是只多了一个表引擎名字，它还要求 Keeper / ZooKeeper 和副本状态健康。查询 `system.replicas` 里的 `absolute_delay`、`queue_size`、`parts_to_check` 这些字段，实际上是在确认“这个表的复制和合并机器是否还在正常运转”。

这和 [[topics/clickhouse-keeper-vs-zookeeper]] 的判断能接上：协调层不是部署图上的小配件，而是 replicated 表能不能持续写入、复制和恢复的关键路径。

## 和 Issue 20867 放在一起看

这篇文章讲的是标准用法，[[sources/clickhouse-issue-20867]] 讲的是误用边界。两者放在一起，反而让规则更清楚：

- 用 `ORDER BY` 表达逻辑去重身份；
- 用 version 表达确定的新旧顺序；
- 不要把低精度业务时间同时塞进 key 和 version；
- 不要把 replicated insert deduplication 误认为表内 replacement；
- 用 `FINAL` 解决读时可见性，而不是补救 schema 里缺失的版本语义。

如果我以后设计用户资料、订单状态、库存快照这类“分析库里的当前状态表”，会优先用这组问题审表：当前状态的 identity 是什么，版本是否单调或至少可比较，重复插入是否可能被复制层提前去重，以及强一致查询到底有多频繁。

## 对我的启发

`ReplicatedReplacingMergeTree` 的诱惑在于，它看起来像给 ClickHouse 加了 upsert。但更准确地说，它提供的是一套“追加事实，后台收敛”的状态建模方式。用得好，它能在 OLAP 系统里承载很多低频更新的当前状态；用得不好，它会让人误以为自己拥有了 OLTP 式唯一约束和实时更新。

我更愿意把它当成一种带副本的最终一致状态表，而不是传统数据库里的 `UPDATE` 替代品。

---

相关页面：[[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-common-pitfalls]] · [[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]]
