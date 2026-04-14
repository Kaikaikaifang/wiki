---
title: "Introducing the ClickHouse Query Cache"
type: source
tags: [数据库, ClickHouse, 缓存, OLAP]
source_count: 1
source_file: raw/articles/introducing-the-clickhouse-query-cache.md
author: Robert Schulze
published: 2023-02-09
updated: 2026-04-15
---

# Introducing the ClickHouse Query Cache

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/blog/introduction-to-the-clickhouse-query-cache-and-design)

## 文章定位

这篇博客是 ClickHouse 在 v23.1 刚引入 query cache 时的**设计解读 + 上手演示**。如果说 [[sources/clickhouse-query-cache]] 更像面向当前用户的参考文档，那么这篇文章更像“为什么要这么设计、早期版本怎么用、作者希望后续演化到哪里”的背景说明。

## 核心演示

文章用 GitHub Events 数据集上的一个星标统计查询做示例，先展示一个大约 8 秒的昂贵聚合，再通过 `use_query_cache = true` 尝试复用结果。最有价值的部分不只是“缓存后变快了”，而是作者特意展示了**第一次为什么没有命中缓存**：

- 查询结果约为 1.26 MiB；
- 默认单条缓存上限是 1 MiB；
- 因此缓存根本没有写入成功；
- 打开 trace 日志后可以直接看到 `Skipped insert (query result too big)`。

这说明 query cache 的使用并不是“打开开关就好”，还需要同时理解**准入条件、容量限制与可观测性**。

## 设计动机

文章把 ClickHouse query cache 放进一整个缓存家族里理解：DNS 缓存、数据缓存、schema 缓存、编译查询缓存、正则缓存等都在做同一件事——**尽量避免重复工作**。在这个框架下，query cache 的价值不是优化访问路径，而是直接绕过已经做过的计算。

这和 [[topics/sql-indexing]] 形成了清晰对照：

- 索引优化“怎样更快地找到数据”；
- 查询缓存优化“哪些重复计算可以干脆不再做”。

## 重要设计取舍

### 事务不一致而非强一致

文章明确对比了事务一致缓存与事务不一致缓存，并解释 ClickHouse 为什么选择后者：作为 OLAP 系统，它接受短时间内的轻微过期，以换取避免复杂失效逻辑和更好的可扩展性。作者还特别提到，这种设计可以避开 MySQL query cache 在高吞吐下遇到的扩展性问题。

### 用 AST 而不是原始 SQL 文本做键

缓存键基于查询的 AST，因此大小写差异不影响命中。这让“语义相同、写法略不同”的查询更容易复用同一份缓存结果，也解释了为什么日志里看到的 `SETTINGS` 子句会被内部裁剪。

### 默认不跨用户共享

文章延续了文档里的安全思路：不同用户可能受不同权限或行策略约束，因此缓存默认不共享。只有显式设置时，单条缓存结果才会对其他用户可见。

## 运维与调试价值

这篇文章比文档更强调“怎么排查为什么没命中”：

- 查 `system.query_cache` 看缓存里到底有没有条目；
- 查 `system.query_log` 的 `QueryCacheHits` 看是否命中过；
- 开 `send_logs_level = 'trace'` 看被拒绝写入的具体原因；
- 结合 `result_size`、TTL 与 stale 标记判断是容量问题还是过期问题。

也就是说，query cache 不只是一个功能开关，而是一套需要通过系统表与日志共同理解的运行机制。

## 与当前文档对照后的启发

这篇 2023 年的博客也能让人看见 feature 从实验态走向文档化、产品化的轨迹：

- 当时需要 `allow_experimental_query_cache = true`；
- 当时的部分设置名和清理命令，与当前文档中的正式命名并不完全一样；
- 当时列为“未来计划”的压缩、更多配置能力等，后来已有相当一部分进入正式文档。

因此，这篇文章最有价值的地方不只是介绍功能，而是补上了**设计意图、排障心智与演化历史**。

## 未来改进方向

文章列出了当时计划中的几条改进路线：

- 压缩缓存条目，例如使用 ZSTD；
- 把缓存条目分页到磁盘，让其跨重启保留；
- 缓存子查询和中间结果；
- 提供更细的配置能力，例如按用户大小限制或分区缓存；
- 引入比“仅清理 stale 条目”更成熟的淘汰策略，如 LRU 或按大小淘汰。

这些计划也帮助我理解：query cache 不只是单一功能点，而是一个还会继续扩展的缓存子系统。

---

相关页面：[[sources/clickhouse-query-cache]] · [[topics/query-result-caching]] · [[entities/clickhouse]]
