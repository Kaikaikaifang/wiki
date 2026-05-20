---
title: ClickHouse in-order 聚合优化
type: source
tags: [ClickHouse, 聚合, 性能优化, 查询优化]
source_count: 0
updated: 2026-05-20
---

这篇文章来自 OneUptime 的 Nawaz Dhandala，专注于一个很容易被忽略的 ClickHouse 设置：`optimize_aggregation_in_order`。它的价值在于把一个看似技术细节的开关，放回 ClickHouse 的物理架构里解释清楚，让我对"聚合为什么会吃内存"有了更直觉的理解。

## 核心机制

MergeTree 表的 `ORDER BY` 不仅决定数据在磁盘上的物理排序，还形成了一个天然的分组边界：同一个 `ORDER BY` 前缀下的行在排序后是连续的。`optimize_aggregation_in_order = 1` 就是让 ClickHouse 利用这个连续性做渐进式聚合——读到哪组，算完哪组，立刻输出，**不需要把所有组同时塞进内存的 hash table**。

这对高基数 GROUP BY（比如数万用户、数百万 tenant）的价值特别明显：hash 聚合必须维护每个 group 的中间状态，而 in-order 聚合可以逐个 group 消费和 flush，内存曲线被打平而不是线性上涨。

可以用 `EXPLAIN pipeline` 确认是否真正走这个路径：看到 `AggregatingInOrderTransform` 说明已经命中，看到标准的 `AggregatingTransform` 则说明退回到了 hash 聚合。

## 适用边界

不是所有 GROUP BY 都能用。条件是 GROUP BY 列必须是表 `ORDER BY` 的前缀。如果表以 `(tenant_id, event_date)` 排序，那 `GROUP BY tenant_id` 或 `GROUP BY tenant_id, event_date` 都可以命中，但 `GROUP BY event_date` 不行——因为跳过了第一个排序列。

对于低基数 GROUP BY（比如按星期几分组），标准 hash 聚合反而更快，因为 hash table 本来就不大，in-order 路径的额外检查反而增加开销。

## 与 optimize_read_in_order 的配合

两个设置配合使用时特别优雅：`optimize_read_in_order` 避免随机读取，`optimize_aggregation_in_order` 避免内存 hash table。当查询的模式（WHERE、GROUP BY、ORDER BY）都对齐 `ORDER BY` 列时，ClickHouse 本质上是做了一次顺序扫描加流式聚合，没有排序，没有 hash table，没有内存峰值。

## 多趟分组

文章里介绍的 multi-pass 分组是一个很实用的扩展思路：当单次聚合太大时，可以先在更细粒度上做一层 in-order 聚合（内层 GROUP BY 对齐 ORDER BY），再在外层做二次聚合。中间结果更小，外层 hash table 压力也大幅降低。这让我意识到，`optimize_aggregation_in_order` 不只是开一个全局开关，而是一种可以嵌套使用的聚合策略。

## 对我的启发

这篇文章让我看到 ClickHouse 的"排序键"远比我想的更有用。之前我主要用它来理解索引和过滤，但这篇文章提醒我：排序也是一个天然的聚集结构。数据库不需要额外的索引或 hash 表来加速聚合，因为数据本身的物理顺序已经提前分好了组。这本质上是把"排序的成本"摊销到了写入时，换取了查询时不重复分配聚合内存。

---
