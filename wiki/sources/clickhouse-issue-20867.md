---
title: ClickHouse 去重问题讨论
type: source
tags: [数据库, ClickHouse, 复制, 去重, ReplacingMergeTree]
source_count: 1
source_file: raw/articles/clickhouse-issue-20867.md
author: iameugenejo, den-crane
published: 2021-02-18
updated: 2026-04-27
---

来源：[[entities/clickhouse]] · [原文](https://github.com/ClickHouse/ClickHouse/issues/20867)

## 核心结论

这个 issue 表面上是在问 `ReplicatedReplacingMergeTree` 为什么“只保留更大的字符串值”，但我更愿意把它看成一个很典型的 ClickHouse 建模事故：用户把 `ORDER BY` 去重键、`ReplacingMergeTree` 的 version 列、以及 replicated 引擎的 insert deduplication 放在同一个直觉里理解，结果看到的行为自然像 bug。

真正重要的地方不在 `test`、`test2`、`test3` 谁赢，而在于 ClickHouse 的“去重”有好几层。`ReplacingMergeTree` 家族在 merge 时按排序键折叠行；可选的 version 列只在同一个排序键下决定谁留下；而 replicated 引擎的插入去重是在更早的位置跳过重复 insert block。三者名字都像 deduplication，但语义和发生时机完全不同。

## 复现里最容易误读的地方

原始表把 `timestamp` 同时放在了两个位置：

```sql
Engine = ReplicatedReplacingMergeTree(..., timestamp)
ORDER BY (account_number, timestamp)
```

这会制造一种很别扭的状态：`timestamp` 既是 replacement key 的一部分，又是 version 列。复现里的插入还全部使用 `toStartOfDay(now())`，所以这些行在“哪一天、哪个账号”这个 key 上相同，version 也没有提供真正递增的信息。

从建模角度看，这不是“更小的非主键字段无法覆盖更大的字段”，而是表定义没有给 ClickHouse 一个明确的新旧顺序。`account_name` 不应该承担版本含义；如果业务想表达“当天账号状态取最新一次快照”，就需要把“当天”作为逻辑 key，把“这次快照何时产生”作为独立的版本或唯一插入信号。

## replicated 插入去重是另一层机制

后续讨论更有价值。用户去掉 version 参数之后，仍然在 `ReplicatedReplacingMergeTree` 上看到与普通 `ReplacingMergeTree` 不同的结果。这里 `den-crane` 指向了 `insert_deduplicate=0`，但关键不是简单记住这个开关，而是理解 replicated insert deduplication 的层级。

replicated 插入去重处理的是“重复 insert block”，不是表内同 key 行的逻辑折叠。它的目的更接近避免网络重试、客户端重复提交时把同一批数据写入多次。`ReplacingMergeTree` 的 replacement 则发生在数据已经进入表之后，依赖 merge 或查询时 `FINAL` 才体现。

这解释了为什么一个 cron 周期性全量快照的 workload 会踩坑：从业务角度看，重复插入一批账号状态是正常的“新快照”；但从 replicated insert deduplication 角度看，如果 payload 完全重复，它可能只是同一个 insert block 的重复提交。两层系统对“重复”的定义不一样。

## 更稳的建模方式

这条 issue 最后给出的方向很朴素：让插入 payload 自身携带足够的唯一性。比如保留一个高精度 `timestamp`、`created_at` 或源端生成的 `insert_id`，同时把 `ORDER BY` 设计成真正的业务去重键。

如果我要存“账号每天最后一次状态”，我会把模型拆成两层：

- `date` 或业务日期进入 `ORDER BY`，表达“同一账号同一天只保留一个状态”；
- 高精度时间、递增版本或源端 UUID 表达“哪一次快照更新”；
- 不依赖 `account_name` 这类业务字段的大小关系来决定谁胜出；
- 对 replicated insert deduplication 保持敬畏，确认重复快照到底应被视为新事实，还是应被视为重试。

这件事的教训是：ClickHouse 里很多“看起来像唯一约束”的能力，其实都是异步 merge、排序键和复制协议共同作用后的结果。它们可以非常高效，但前提是 schema 把业务语义说清楚。

## 对我的启发

我会把这条 issue 当作 `ReplacingMergeTree` 建模的一个小型警报器。凡是我想用它表达“最后状态”“最新版本”“每日快照”时，都应该先问三件事：去重 key 是什么，version 从哪里来，重复 insert block 是否可能被 replicated 层提前吃掉。

如果这三个问题答不清楚，`FINAL` 或 `OPTIMIZE FINAL` 只能让问题更快暴露，不能替 schema 补出业务时间线。

---

相关页面：[[topics/clickhouse-common-pitfalls]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[entities/clickhouse]]
