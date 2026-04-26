---
title: ClickHouse 入门 13 个误区
type: source
tags: [数据库, ClickHouse, 性能, 运维]
source_count: 1
source_file: raw/articles/clickhouse-13-mistakes.md
author: ClickHouse
published: 2026-04-26
updated: 2026-04-26
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/blog/common-getting-started-issues-with-clickhouse)

## 核心结论

这篇文章表面上是在列 ClickHouse 新手常见的 13 个错误，但我更愿意把它看成一张生产化检查表：ClickHouse 的很多事故并不是“数据库突然不行了”，而是写入粒度、分区键、主键、物化视图、Keeper、内存限制和查询形状这些决策在一开始没有被放到同一个系统里思考。

它最有价值的提醒是：ClickHouse 很快，但它不是一个可以靠默认值无脑吞下所有工作负载的黑盒。它的性能来自一组明确的物理假设：数据以 part 形式写入和合并，按 `ORDER BY` 排序形成稀疏主键，复制依赖 Keeper 协调，聚合和 join 会消耗真实内存。违背这些假设时，问题通常不会表现为单一慢查询，而会变成 part 堆积、插入变慢、复制延迟、只读表、内存超限或物化视图拖垮写入。

## 写入侧最先暴露的问题

我读这篇文章时最先被强化的是 `Too many parts` 这条线。ClickHouse 的 `MergeTree` 不是每来一行就原地更新某个页，而是把插入数据变成 part，再靠后台 merge 把 part 数量压回去。因此两类新手动作尤其危险：

- 用高基数列做 partition key，让不同分区的 part 永远不能合并；
- 频繁做小批量 INSERT，让系统不断制造微小 part。

文章给出的经验边界很实用：partition key 的基数通常应低于 `1000`，插入最好客户端攒批，至少 `1000` 行一批，常见理想批量是 `10000` 到 `100000` 行。如果客户端不能缓冲，优先考虑 async inserts，并保持 `wait_for_async_insert=1`，让确认发生在数据真正落盘之后。

这背后的判断比数字本身更重要：ClickHouse 的写入性能不是只看吞吐，还要看写入形状是否尊重后台 merge 的节奏。

## 不要过早横向扩展

文章反复强调一个有点反直觉的原则：ClickHouse 新手不该太早把问题推进到几十上百个节点。ClickHouse 本来就擅长吃满单机资源，很多分析查询的过滤、排序、聚合都可以在单机内部并行化。

所以默认顺序应是先纵向扩容，再横向扩展。横向扩展当然有价值，但它会把网络、分片路由、跨 shard 聚合、Keeper 压力和运维复杂度一起带进来。如果一个工作负载还没有被证明超过单机上限，过早上 Kubernetes 和大规模 shard，常常是在把简单问题提前复杂化。

## 模型设计比后补索引更关键

ClickHouse 的主键不是 OLTP 里那种“快速定位一行”的 B-tree 主键，而是依赖磁盘排序的稀疏索引。真正决定查询能否少扫数据的是 `ORDER BY` 选择了什么列，以及这些列的顺序是否贴合过滤模式。

文章给出的方向是：主键列通常来自高频过滤条件，一般不需要超过 2 到 3 列；为了兼顾过滤和压缩，主键列顺序常按基数从低到高排列。这里我会加一个自己的理解：这不是在背诵规则，而是在为 ClickHouse 提供一种“数据应该怎样被物理聚在一起”的提示。

data skipping index 也被放在类似的位置。它不是 ClickHouse 的万能二级索引，只在非主键列与主键排序之间存在强相关时才更可能有效。否则它只会增加插入和维护成本，却很难减少真正读取的 granule。

## `LIMIT` 和点查很容易制造错觉

从 OLTP 世界迁过来的人很容易把 `LIMIT 10` 理解成“数据库只要找到 10 行就停”。这在 ClickHouse 里不总成立。只有当查询可以流式执行，或者排序、分组顺序能被主键顺序利用时，`LIMIT` 才更可能提前终止。

如果查询需要先按非主键列排序，或者聚合必须消费全表后才能返回结果，`LIMIT` 只是最后一步裁剪。到了分布式表上，每个 shard 还可能各自返回 Top-N，再由协调节点汇总，资源消耗并不会因为最终只看几行就自动消失。

这对我很像索引主题里的老问题：查询语义上“只要一点结果”，不等于执行层真的有一条便宜路径拿到那一点结果。

## 更新、去重与物化视图都不是免费午餐

文章把 mutations、轻量更新、轻量删除、`ReplacingMergeTree` 和物化视图放在一起看，我觉得这是非常对的。它们都在解决“写入之后还想改变或重塑数据”的需求，但每一种都有代价。

经典 mutation 会重写 part，并与 merge 共享资源池；轻量更新通过 patch part 降低改写成本，但仍然会影响读取与后续 merge；`ReplacingMergeTree` 的去重是 merge 驱动的 best effort，不等于实时唯一性；增量物化视图本质上是插入触发器，只看新插入 block，不会自动感知源表后续 mutation、partition drop 或 merge。

我会把这些能力理解成“OLAP 系统提供的补救和预计算工具”，而不是把 ClickHouse 当成频繁原地更新的 OLTP 数据库。

## Keeper 是生产系统的一部分

只读表这个误区很有代表性：在自管复制环境里，节点如果失去与协调服务的连接，就可能无法参与复制并拒绝写入。很多时候根因不是表本身，而是 Keeper / ZooKeeper 与 ClickHouse 混部、资源不足或协调层没有被当作一级生产组件。

这与已有的 [[topics/clickhouse-keeper-vs-zookeeper]] 能接上：Keeper 不是附属配置项，而是复制、去重窗口和分布式元数据路径的一部分。生产环境里把它独立部署、监控和容量规划，不是洁癖，是避免数据库在关键路径上退化成只读的基础条件。

## 内存问题要从查询形状治理

`Memory Limit Exceeded for Query` 不是单纯把 `max_memory_usage` 调大就结束。文章把高基数聚合、大 join、排序、分布式协调节点汇总和失控用户查询都列进来，说明 ClickHouse 的内存治理要同时覆盖三层：

- 查询写法：过滤前置，join 右表尽量小，必要时用 `ANY JOIN`、`ASOF JOIN` 等更贴近语义的 join 类型；
- 执行策略：通过外部 group by / sort 允许溢写磁盘，用 `join_algorithm = 'auto'` 或更合适算法在性能与内存之间折中；
- 多租户治理：用 quotas、query complexity 限制和 memory overcommit，让少数重查询不拖垮整台机器。

这部分和 [[topics/sql-join-performance]] 的关系很直接：不要机械地问 ClickHouse “为什么 join 慢”，先看 join 形状、数据规模、过滤时机和算法是否匹配。

## 实验功能不要放在核心路径

ClickHouse 迭代很快，beta 与 experimental 功能看起来很诱人。但文章明确区分了 beta 与 experimental：beta 处于官方支持并走向生产就绪的路径上，experimental 更像早期原型，通常要显式开启。

我的判断是，实验功能可以用来探索未来形态，但不要把核心生产路径建在它上面。尤其是数据库这种底层系统，一旦数据模型、查询路径或运维流程依赖了实验特性，后续迁移成本会远高于功能试用时的爽感。

## 对我的启发

这篇文章让我对 ClickHouse 的理解从“有哪些高级功能”往回收了一步：真正的入门，不是把所有功能都知道一遍，而是知道哪些默认直觉会害你。

如果要给自己留一条检查句，我会写成：**每一个 ClickHouse 设计决策，都先问它是在减少 part、减少扫描、减少跨节点协调，还是只是在把成本推给后台 merge、Keeper 和内存池。**

---

相关页面：[[topics/clickhouse-common-pitfalls]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/sql-join-performance]] · [[topics/query-shape-and-index-usage]] · [[entities/clickhouse]]
