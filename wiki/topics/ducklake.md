---
title: DuckLake 数据格式的 SQL 元数据架构
type: topic
tags: [数据湖仓, 数据格式, 数据库设计, SQL]
source_count: 2
updated: 2026-06-11
---

> 读 DuckLake 宣言时，我有一种被"点醒"的感觉：Iceberg 和 Delta Lake 为了不依赖数据库，用 JSON 和 Avro 在对象存储上搭了一个复杂的文件协议；但既然 lakehouse 的 catalog 层最终还是要引入数据库来保证事务一致性，那为什么不干脆让数据库管理所有元数据？

## 核心判断：元数据不是文件的附庸

DuckLake 的核心设计判断是：**元数据管理本质上是数据库事务问题，不是文件存储问题。**

Iceberg 的表架构用 JSON 文件描述快照、schema、分区信息，用 Avro 文件存储 manifest list，再用两层 manifest 来减少 S3 请求。这些设计都是"在没有数据库的前提下做数据库该做的事"——原子写、一致性读取、并发控制。DuckLake 说：既然最终还是要一个数据库，那不如把所有元数据直接放在数据库的表里。

这个选择的实际影响是：

- 一次查询只需要**单次 SQL 查询**就能获得文件列表和统计信息，而不是多次 S3 请求
- schema 变更、数据注册、快照创建都在**同一 ACID 事务**中完成
- 小写入可以直接"内联"到 catalog 数据库中，**避免生成大量微小 Parquet 文件**

## 架构对比：文件优先 vs 数据库优先

| 维度 | Iceberg / Delta Lake | DuckLake |
|------|----------------------|----------|
| 元数据存储 | JSON/Avro 文件 | SQL 数据库表 |
| 事务一致性 | 依赖对象存储原子写 | 数据库 ACID 事务 |
| 查询规划 | 多次 S3 请求获取文件列表 | 单次 SQL 查询 |
| 小文件问题 | 需要 compaction 或合并 | 小写入直接内联到数据库 |
| 跨表事务 | 不支持 | 原生支持 |
| catalog 依赖 | 仍需外部数据库做 catalog | catalog 即数据库 |

这种差异不是简单的"实现方式不同"，而是**数据湖格式与数据库之间边界的重新划分**。Iceberg 和 Delta Lake 试图在不依赖数据库的前提下实现数据库功能；DuckLake 则承认数据库在事务和元数据管理上的不可替代性，然后在此基础上构建数据湖格式。

## 数据内联：解决小文件问题的工程直觉

DuckLake 的 Data Inlining 功能让我看到了一个具体的工程直觉：当写入量很小时，不要把数据写到对象存储上，而是直接存在 catalog 数据库里。

v1.0 默认阈值是 10 行。插入、删除、更新都在这个阈值内时，数据不会生成新的 Parquet 文件，而是作为数据库行存在。只有当执行 `CHECKPOINT` 或阈值被突破时，数据才会被 flush 到对象存储。

这个设计的精妙之处在于：

1. **它避免了数据湖格式中最常见的"小文件问题"**
2. **对应用层完全透明**——应用仍然写标准的 INSERT/DELETE/UPDATE
3. **利用了数据库本身的能力**——数据库本来就擅长管理小量数据的事务

这让我反思：我们在 ClickHouse 生产迁移里讨论的"OSS 中转 + 批次导入"策略，本质上也是在解决"大量小文件写入对象存储"的问题。DuckLake 用内联来避免小文件，ClickHouse 用 part 合并来吸收小文件——两者解决的是同一类问题，但路径不同。

## 排序表与分区：把优化成本从查询移到写入

DuckLake 支持 `SET SORTED BY` 来定义表的排序键。排序发生在 compaction、flush 或插入时，让 row group 和文件级别的 min/max 统计能直接服务于查询过滤。

Bucket Partitioning 则是 Iceberg 兼容的 `bucket(N, column)` 变换，用 murmur3 哈希把高基数列映射到固定桶数。这与 ClickHouse 里 `projectId` 分片策略的直觉相似——用哈希来避免高基数列直接分区导致的大量目录。

这些功能的核心逻辑是：**在写入路径上支付排序/分桶成本，换取查询时的过滤效率。** 这与 ClickHouse 的 `ORDER BY` 设计逻辑高度一致——数据的物理组织应该提前对齐查询模式。

## 兼容性与迁移：数据层对齐，元数据层独立

DuckLake v1.0 实现了对 Iceberg 数据格式的兼容：DuckLake 写入的 Parquet 文件和删除文件可以直接被 Iceberg 读取。这意味着数据层是通用的，差异只在元数据层。

这个兼容策略很聪明：

- **数据文件**是通用的——Parquet 是行业事实标准
- **元数据**是 DuckLake 的——SQL 数据库管理，而不是 Iceberg 的 JSON 文件
- **迁移路径**可以是元数据层面的——不需要移动数据文件

这也让我意识到， lakehouse 格式的竞争不在数据层，而在元数据层。Parquet 已经是赢家，真正的差异在于谁管理这些 Parquet 文件的目录、版本、统计和事务。

## Variant 类型：数据湖格式的类型系统演进

DuckLake 把 Variant 类型作为 JSON 的替代方案：二进制编码、支持更丰富的类型（DATE、TIMESTAMP）、支持 shredding 到原生类型。

文章认为 Variant 最终会替代 JSON 成为半结构化数据的主流类型。这个判断值得关注的理由是：它触及了数据湖格式和查询引擎之间的接口设计。如果数据湖格式能提供更精确的类型信息，查询引擎就能做更激进的下推优化——这正是 DuckLake 把元数据放在数据库里能带来的好处之一。

## 与现有 Lakehouse 格式的关系

DuckLake 不是 Iceberg 或 Delta Lake 的替代者，而是**同一设计空间中的不同选择**。

- **Iceberg** 适合已经投入大量工程在 JSON/Avro 元数据协议上的生态，优势是广泛的生态集成（Spark、Flink、Trino、Dremio 等）
- **Delta Lake** 适合 Databricks 生态，优势是 Unity Catalog 和 Databricks 的垂直集成
- **DuckLake** 适合 DuckDB 生态和需要简单本地部署的场景，优势是极致的简洁性和低延迟元数据访问

三者使用相同的底层数据格式（Parquet），竞争在元数据层。这种"数据通用、元数据独立"的格局，让 lakehouse 格式的选择更像是"选哪个 catalog 系统"，而不是"选哪种数据格式"。

## 对我的启发

DuckLake 让我重新思考了数据湖格式的本质问题：我们到底在解决什么？

- 如果问题是"如何把 Parquet 文件组织成可查询的表"，那么 Iceberg 的 JSON 元数据协议是一个合理选择
- 如果问题是"如何用事务保证数据一致性"，那么数据库事务是比对象存储原子写更可靠的基础设施
- 如果问题是"如何让小写入也能高效地进入数据湖"，那么把数据暂时存在数据库里，比不断生成小 Parquet 文件更优雅

DuckLake 的核心判断是：**不要在没有数据库的地方重新发明数据库。** 这个判断简单，但执行它需要勇气——因为它承认 Iceberg 和 Delta Lake 的某些设计妥协是不必要的，并且给出了一个更直接的替代方案。

对于我的 ClickHouse 迁移工作，DuckLake 提供了一种有趣的对比：ClickHouse 用本地 part 合并和对象存储外部卷来管理数据生命周期；DuckLake 用 SQL 数据库管理元数据，用对象存储承载数据。两者都把对象存储作为容量层，但元数据管理的路径完全不同。这种对比让我更清楚 ClickHouse 的设计选择——以及它的局限性。

来源：[[sources/ducklake-manifesto]] · [[sources/ducklake-v1-0-announcement]]

相关页面：[[entities/duckdb]] · [[entities/ducklake]] · [[topics/clickhouse-deployment-topologies]] · [[sources/clickhouse-cold-hot-storage]] · [[topics/clickhouse-data-export]] · [[topics/hdfs-and-oss-hdfs]]
