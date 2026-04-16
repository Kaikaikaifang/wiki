---
title: ClickHouse 查询缓存文档
type: source
tags: [数据库, ClickHouse, 缓存, OLAP]
source_count: 1
source_file: raw/articles/query-cache-clickhouse-docs.md
author: ClickHouse
published: 2026-04-15
updated: 2026-04-16
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/operations/query-cache)

## 核心结论

ClickHouse 的 query cache 不是面向 OLTP 的强一致结果缓存，而是面向 OLAP 的**短时有效、允许轻微不一致**的查询结果缓存。它的目标不是保证每次读取都反映最新数据，而是让重复执行的昂贵 `SELECT` 只计算一次，用一个可控的 TTL 窗口换取更低延迟与更低资源消耗。

## 设计取舍

- **一致性模型**：文档明确区分事务一致缓存与事务不一致缓存，并把 ClickHouse 放在后者一侧，更适合报表、分析面板、重复读取的聚合查询。
- **部署位置**：ClickHouse 把缓存逻辑放到服务端，避免客户端工具或代理层重复实现同一套缓存策略。
- **适用范围**：只对独立的 `SELECT` 语句生效；视图查询不会因为建视图时带了 `SETTINGS use_query_cache = true` 就自动缓存。
- **运行边界**：`clickhouse-local` 默认禁用查询缓存，因为它一次只跑一条查询，结果复用没有意义。

## 使用方式

- 通过 `use_query_cache = true` 打开查询缓存。
- 用 `enable_writes_to_query_cache` 与 `enable_reads_from_query_cache` 分别控制写入与读取。
- 文档建议优先按**具体查询**开启，而不是在用户或 profile 级别全局开启，否则所有 `SELECT` 都可能返回缓存结果。
- 可用 `SYSTEM CLEAR QUERY CACHE` 清空整个缓存，也可用 `SYSTEM CLEAR QUERY CACHE TAG 'tag'` 清理某个命名空间。

## 缓存键、隔离与安全

ClickHouse 以查询的 AST 作为缓存键，因此 `SELECT 1` 与 `select 1` 会命中同一条缓存。为了让匹配更自然，查询级别的 query cache 设置和输出格式设置会从 AST 中移除，不参与匹配。

缓存按 **server process** 维护，但默认**不在用户之间共享**。文档给出的理由是安全性：如果用户 A 与用户 B 在行级策略上可见数据不同，那么共享缓存可能泄露本不该看到的结果。虽然可以显式打开 `query_cache_share_between_users`，但这不是推荐默认项。

## 生命周期与准入条件

- **TTL**：默认 60 秒，可在 session、profile 或 query 级别通过 `query_cache_ttl` 调整。
- **惰性淘汰**：条目过期后不会立刻删除，而是在插入新条目且空间不足时优先清理陈旧条目。
- **大小控制**：服务端可限制总字节数、最大条目数、单条缓存大小与记录数。
- **用户配额**：可在 `users.xml` 的 profile 中限制单个用户可占用的缓存字节数和条目数。
- **准入门槛**：可通过 `query_cache_min_query_duration` 和 `query_cache_min_query_runs` 避免把过快或只执行一次的查询也写进缓存。
- **压缩与分块**：缓存条目默认压缩；`query_cache_squash_partial_results` 会在写入前重整结果块大小，以改善压缩率和后续读取时的块粒度。
- **标签命名空间**：`query_cache_tag` 可以让“同一条查询”在不同上下文下保留多份缓存结果。

## 默认不会缓存的情况

- 查询因异常或用户取消而中断；
- 包含非确定性函数，例如 `now()`、随机函数、依赖 block 内部状态的函数、依赖环境的函数；
- 访问系统表或 `information_schema` 等系统元数据。

这些默认值体现了一个原则：**只缓存语义稳定、可安全复用的结果**。如果确有需要，也可以通过专门设置放宽非确定性函数或系统表的限制。

## 观测与运维

文档给出了一套比较完整的可观测入口：

- `system.query_cache`：查看当前缓存内容；
- `system.events`：查看 `QueryCacheHits` 与 `QueryCacheMisses`；
- `system.query_log`：通过 `query_cache_usage` 判断某次查询是读缓存还是写缓存；
- `system.metrics`：查看 `QueryCacheEntries` 与 `QueryCacheBytes`。

如果通过 HTTP 运行查询，ClickHouse 还会返回 `Age` 与 `Expires` 头，直接暴露缓存条目的年龄与过期时间。

## 对我的启发

这篇文档提醒我：数据库性能优化并不只有“让第一次跑得更快”这一条路。对分析型系统而言，还有另一类优化：**承认一个可接受的新鲜度窗口，把已经算过的结果稳妥地复用起来。**

这条思路与索引不同——索引优化的是访问路径，query cache 优化的是重复计算。

---

相关页面：[[sources/introducing-the-clickhouse-query-cache]] · [[topics/query-result-caching]] · [[entities/clickhouse]] · [[topics/sql-indexing]]
