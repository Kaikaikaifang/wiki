---
title: ClickHouse Parallel Replicas
type: source
tags: [数据库, ClickHouse, 分布式查询, 性能优化, 并发]
source_count: 1
updated: 2026-05-13
---

> 来源：[Parallel replicas | ClickHouse Docs](https://clickhouse.com/docs/deployment-guides/parallel-replicas)

## 从分片架构到无分片架构

传统 ClickHouse 集群用 shard 做数据切分，每个 shard 存一部分数据，`Distributed` 表把查询路由到各 shard，协调节点汇总结果。加入副本后，每个 shard 只选一个 replica 执行查询。

ClickHouse Cloud 走了另一条路：基于对象存储的存算分离让"数据量无限大"不再等于"必须分片"。所有 replica 共享同一份对象存储数据，由 ClickHouse Keeper 同步元数据，本地 SSD cache 加速查询。

问题变成：没有 shard 的情况下，如何把单个查询并行化到多个 replica 上？

## Parallel Replicas 的核心机制

Parallel replicas 用 **granule** 作为最小工作单元，而不是 shard。整个流程如下：

1. 客户端查询经负载均衡到达某一节点，该节点成为 **coordinator**；
2. coordinator 分析各 part 的索引，选出需要处理的 parts 和 granules；
3. coordinator 把 granules 拆成任务集，分配给不同 replica；
4. 各 replica 处理完自己的 granules 后，把 mergeable state 回传给 coordinator；
5. coordinator 合并结果并返回客户端。

### Announcements：解决副本状态不一致

副本间的复制是异步的，不同 replica 可能在某一时刻拥有不同的 parts。为了调度正确：

- coordinator 在分配任务前，先向所有 replica 收集 **announcement**（当前拥有的 parts 列表）；
- 只把某个 part 的 granules 分配给报告拥有该 part 的 replica；
- 没有回复 announcement 的 replica 不会被分配任务。

### Dynamic Coordination：解决尾延迟

不是一次性把所有 granules 塞给 replica，而是让 replica **主动请求新任务**。这样：

- 处理快的 replica 可以不断领取新任务；
- 处理慢的 replica 不会阻塞整体进度；
- coordinator 根据 announcement 信息决定还有哪些任务可分配。

### Cache Locality：让重复查询命中热缓存

为了让同一查询多次执行时能利用 replica 本地缓存：

- 对 `part + granules` 做 hash；
- 用 `hash % replica_count` 决定任务分配给哪个 replica；
- 这样同一组 granules 倾向于被同一 replica 处理。

如果 `max_parallel_replicas` 小于实际 replica 数，则随机选取 replica 执行，以平衡负载。

### Task Stealing：处理慢节点

即使做了 hash 分配，某些 replica 仍可能因负载或网络变慢。此时其他 replica 会尝试"窃取"原本属于慢 replica 的任务，进一步降低尾延迟。

## 已知限制

| 限制 | 说明 |
|---|---|
| 复杂查询 | CTE、子查询、JOIN、非扁平查询等可能影响性能 |
| 小查询 | 数据量小时，协调开销可能抵消并行收益，可用 `parallel_replicas_min_number_of_rows_per_replica` 限制 |
| FINAL | 使用 FINAL 时禁用 parallel replicas |
| Projections | 暂不支持与 parallel replicas 同时使用 |
| 高基数聚合 | 需要回传大量中间状态的聚合会显著拖慢查询 |
| 新 Analyzer | 行为可能因场景不同而显著变化 |

## 关键设置

| 设置项 | 说明 |
|---|---|
| `enable_parallel_replicas` | `0` 禁用，`1` 启用，`2` 强制启用（失败则抛异常） |
| `cluster_for_parallel_replicas` | 使用的集群名；Cloud 环境用 `default` |
| `max_parallel_replicas` | 单查询最多使用的 replica 数，可超配以适应水平扩缩容 |
| `parallel_replicas_min_number_of_rows_per_replica` | 按预估行数限制实际使用的 replica 数 |
| `enable_analyzer` | 必须开启新 analyzer 才能使用 parallel replicas |

## 多分片架构下的 Parallel Replicas

官方文档最初在"分片架构"的语境下介绍 Parallel Replicas，这与我之前的理解不同——它不只是无分片架构的专利。

**工作机制：分层并行**

在 `M shards × N replicas` 架构下，Parallel Replicas 与 `Distributed` 表协同工作：

1. **第一层：跨 shard 并行**（由 `Distributed` 表负责）
   - `Distributed` 表把查询拆成 M 个子查询，分发到各 shard
   - 每个 shard 收到自己的子查询

2. **第二层：跨 replica 并行**（由 Parallel Replicas 负责）
   - 每个 shard 内部，某个 replica 成为 **coordinator**
   - coordinator 把该 shard 的 granules 分发到该 shard 的多个 replica
   - 各 replica 处理完后回传 mergeable state
   - shard 内 coordinator 合并结果

3. **最终结果汇总**
   - `Distributed` 表收集所有 shard 的结果
   - 做最终聚合后返回客户端

**关键区别：作用范围**

| 维度 | 无分片（1 shard × N replicas） | 多分片（M shards × N replicas） |
|---|---|---|
| **查询入口** | 直接查本地表 | 必须查 `Distributed` 表 |
| **第一层并行** | 无（只有一个 shard） | `Distributed` 表跨 shard |
| **第二层并行** | Parallel Replicas（所有 replica） | Parallel Replicas（**每个 shard 内部**的 replica） |
| **max_parallel_replicas 作用范围** | 整个集群的所有 replica | **每个 shard 内部**的 replica |

官方文档明确说明：

> "When the `max_parallel_replicas` option is enabled, query processing is parallelized across all replicas **within a single shard**."

这意味着 `max_parallel_replicas` 限制的是**每个 shard** 最多用多少个 replica，而不是整个集群的总 replica 数。

**配置示例：**

```xml
<remote_servers>
    <my_cluster>
        <shard>
            <internal_replication>true</internal_replication>
            <replica><host>node1</host></replica>
            <replica><host>node2</host></replica>
            <replica><host>node3</host></replica>
        </shard>
        <shard>
            <internal_replication>true</internal_replication>
            <replica><host>node4</host></replica>
            <replica><host>node5</host></replica>
            <replica><host>node6</host></replica>
        </shard>
    </my_cluster>
</remote_servers>
```

```sql
-- 查询 Distributed 表，同时开启 Parallel Replicas
SELECT * FROM distributed_table
SETTINGS 
    enable_parallel_replicas = 1,
    cluster_for_parallel_replicas = 'my_cluster',
    max_parallel_replicas = 3;  -- 每个 shard 最多用 3 个 replica
```

**注意事项：**

- `cluster_for_parallel_replicas` 应指向**包含所有 shard 和 replica 的同一个集群名**（与 `Distributed` 表使用的集群一致）
- 如果 `max_parallel_replicas` 小于单个 shard 的 replica 数，会在该 shard 的 replica 中随机选择
- 复杂查询（CTE、JOIN、子查询）、小查询、`FINAL`、projections 等限制同样适用

## 调试手段

- `system.query_log`：查看每查询实际使用的设置；
- `system.events`：过滤 `ParallelReplicas%` 事件；
- `system.text_log`：按 `query_id` 追踪执行日志；
- `EXPLAIN PIPELINE`：对比开启/关闭 parallel replicas 的执行计划差异。

---

来源：[Parallel replicas | ClickHouse Docs](https://clickhouse.com/docs/deployment-guides/parallel-replicas)

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-deployment-topologies]] · [[sources/clickhouse-cloud-architecture]] · [[sources/clickhouse-sharding-decision]]
