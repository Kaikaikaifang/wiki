---
title: DuckLake v1.0 发布
author: DuckDB Team
published: "2026-04-13"
link: "https://ducklake.select/2026/04/13/ducklake-10/"
file: raw/articles/ducklake-v1-0-announcement.md
type: source
tags: [数据湖仓, DuckDB, 数据格式, SQL]
source_count: 1
---

DuckLake v1.0 发布文章不只是版本公告，而是 DuckLake 团队把一年来的工程判断和盘托出：一个把元数据全部放在 SQL 数据库里的 lakehouse 格式，已经通过了生产环境的验证。

文章里我最关注的不是功能列表，而是几个具体设计决策的生产级落地：

1. **Data Inlining**：小写入（默认 10 行以内）直接存在 catalog 数据库里，不生成新的 Parquet 文件。这是 DuckLake 宣言里"简单性"原则的具体实现——它避免了数据湖格式中最常见的"小文件问题"，且对应用层完全透明。

2. **Sorted Tables**：支持在 compaction 或 flush 时按指定列排序，从而让 row group 和 file pruning 能直接利用 min/max 统计。这本质上是在写入路径上提前支付排序成本，换取查询时的过滤效率。

3. **Bucket Partitioning**：Iceberg 兼容的 `bucket(N, column)` 变换，用 murmur3 哈希把高基数列映射到固定桶数。对 ClickHouse 里 `projectId` 这类列的分区策略，我有一种直觉上的共鸣。

4. **Variant 类型**：比 JSON 更丰富的类型支持，二进制编码，且支持 shredding 到原生类型。文章认为 Variant 最终会替代 JSON 作为半结构化数据的主流类型——这个判断值得关注，因为它直接触及了数据湖格式和查询引擎之间的接口设计。

5. **Deletion Vectors**：实验性支持 Iceberg V3 的删除向量，用 Puffin 文件存储 roaring bitmap。这是 DuckLake 兼容 Iceberg 数据层的具体信号，意味着 DuckLake 和 Iceberg 之间可能有更平滑的迁移路径。

文章附录列出了 108 个 PR，其中 68 个聚焦可靠性和正确性，12 个重构，12 个性能优化。这个分布比例本身就是一个信号：v1.0 不是功能堆叠，而是把一年前宣言里的架构判断打磨到可以扛住生产负载。

来源：[[sources/ducklake-v1-0-announcement]]

相关页面：[[topics/ducklake]] · [[entities/duckdb]] · [[entities/ducklake]] · [[sources/ducklake-manifesto]]
