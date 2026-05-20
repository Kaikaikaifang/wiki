---
title: ClickHouse 查询优化
type: topic
tags: [ClickHouse, 查询优化, 性能优化, 索引, 聚合]
source_count: 2
updated: 2026-05-20
---

> 这篇综述是我在摄入两份 ClickHouse 优化资料后的整合。一份来自官方工程博客的权威指南，一份来自社区关于 `optimize_aggregation_in_order` 的专项文章。它们共同帮我建立起一个判断：ClickHouse 的优化不是从"慢"修到"快"，而是从"理解物理架构"到"让查询路径对齐物理架构"。

## 为什么 ClickHouse 的优化和传统数据库不同

传统 OLTP 数据库的优化大多围绕 B-tree 展开：加索引、看执行计划、避免全表扫描。这些在 ClickHouse 里不是没用，但位置变了。ClickHouse 真正的主优化杠杆不在查询计划层面，而在**建表时的数据物理组织**。

理解这个差异需要先接受 ClickHouse 的几个架构事实：

- **数据物理排序**：`ORDER BY` 定义了数据在磁盘上的物理顺序，不是逻辑约束。这意味着建表时的排序设计直接影响查询时的数据跳过效率。
- **Granule 是读写原子单位**：默认 8,192 行一个 granule，索引定位和磁盘读取都以此为界。不能读半个 granule，这不影响正确性但定义了过滤精度的天花板。
- **稀疏索引不是 B-tree**：ClickHouse 的主索引只存储每个 granule 的第一个值，体积小到可以常驻内存，代价是后置列在 high-cardinality 前置列面前几乎退化。
- **后台 Merge 是计算载体**：不只是碎片整理，物化视图维护、TTL 过期和去重都在 merge 过程中完成。写入形状影响的不只是写入速度，还有整个后台计算管道的健康度。

一旦接受这些事实，优化的优先级自然就清楚了：**先让数据物理组织和查询模式对齐，再考虑查询层面的技巧。**

## 优化分层框架

我把 ClickHouse 的优化手段排成一个六层框架，从上到下，影响力递减：

### 第一层：ORDER BY 设计

这层不是"优化"，是"定义"。ORDER BY 选得好与不好，查询性能可以差 100 倍以上。

核心规则三条：
1. **WHERE 列优先**：分析查询模式，把高频过滤列放进 ORDER BY
2. **低基数列排前面**：第一列通过二分搜索（O(log₂ n)）高效定位 granule；后面的列依赖前置列的基数支撑过滤
3. **时序数据包含时间组件**：大多数分析查询都有时间范围，把时间列放进 ORDER BY 能让 ClickHouse 跳过大量 granule

一个反直觉但正确的判断是：**低基数列比高基数列更适合排在 ClickHouse 主键的前面。** 这在传统数据库里说不过去（低基数列索引选择性差），但 ClickHouse 的逻辑不同：后置列的过滤效率依赖于前置列能在多少个 granule 上撑开足够的"视野"。如果第一列是 UUID，每个值几乎只出现在少量 granule 里，后置列的排序边界就几乎不存在，排除搜索退化。

### 第二层：数据类型优化

这层不改变查询模式，但直接影响 I/O 量和内存效率：

- **避免 Nullable**：每个 Nullable 列额外携带一个 UInt8 null mask，从存储、读到计算全链路拖慢。建表前先用 `countIf(col IS NULL)` 验证实际需求，能用默认值替代就用默认值。
- **LowCardinality**：对唯一值 < 10,000 的 String 列，字典编码用整数引用替代重复字符串，存储和比较成本大幅降低。
- **选最小类型**：UInt8 替代 Int64 在单行上省 7 bytes，十亿行就是 7GB。时间列优先 Date、DateTime，而非 DateTime64。

### 第三层：预计算策略

把查询时的工作挪到写入时：

- **增量物化视图**：适合固定模式的聚合查询，在 INSERT 时自动维护目标表。但要记住它只响应 INSERT，不响应源表 mutation。适合仪表盘和周期性报表。
- **Projections**：物化视图解决"预先算好结果"，Projections 解决"换一种排序"。一张表只能有一种物理 ORDER BY，Projections 就是为不同查询模式维护不同排序的数据副本。查询时自动选择，无需改 SQL。从 25.6 开始支持单查询内组合多个 projection。
- **字典**：把 JOIN 替成 O(1) 内存查询，适合频繁引用但相对静态的维度数据。支持自动刷新，可以从 PostgreSQL、MySQL、文件等多种外部源加载。

### 第四层：查询模式优化

这些是查询 SQL 编写层面的技巧：

- **PREWHERE**：先读条件列做过滤，再读 SELECT 列。ClickHouse 经常自动应用，但显式使用可保证行为。适合过滤率高的查询。
- **近似函数**：`uniq()` 替代 `COUNT(DISTINCT)`，用 HyperLogLog 在 ~12KB 固定内存里完成去重，比精确去重快 10-100 倍，误差 1-2%。`uniqCombined()` 支持跨分布式查询合并。
- **反范式化**：ClickHouse 在宽表上的表现强于多表 JOIN。列式压缩让重复字段的存储惩罚可控，而 JOIN 的 hash table 构建成本是实打实的运行时开销。
- **字符串哈希**：对长字符串 GROUP BY 时，`cityHash64()` 转固定长度整数再分组快 5-10 倍。
- **`optimize_aggregation_in_order`**：当 GROUP BY 键是 ORDER BY 前缀时，ClickHouse 可以做流式聚合而不构建 hash table，内存曲线从线性增长变成接近恒定。验证用 `EXPLAIN pipeline` 看 `AggregatingInOrderTransform`。配合 `optimize_read_in_order` 用更佳。

### 第五层：额外索引

这些是"补丁层"——在基础设计到位后仍有特定列需要加速时才用：

- **Skip Indexes**：minmax、set、bloom_filter、tokenbf_v1、ngrambf_v1。致命前提是**索引列必须和 ORDER BY 列有相关性**，否则写入成本付了，查询完全用不上。

### 第六层：分区

分区的主要用途是数据生命周期管理（DROP PARTITION）和分级存储（SSD→HDD→对象存储），不是查询加速器。维持 10-100 个分区，超出一千个会严重退化。分区键应该低基数，主要服务于删除和归档，不应该为了"感觉会变快"加分区。

## 性能诊断方法

优化的起点不是直觉，是数据。ClickHouse 提供的诊断工具链非常完整：

- **`system.query_log`**：自动记录每次查询执行。用 `normalized_query_hash` 找高频重复查询——优化每天跑一万次的查询，投资回报比优化偶尔分析用的一次性查询高一万倍。
- **`EXPLAIN indexes = 1`**：显示 granule 命中比例，这是最直接的"索引帮了多少忙"指标。看到 granule 全选就是全表扫描。
- **`EXPLAIN pipeline`**：看实际走了哪个 pipeline transform，判断 in-order 聚合是否命中、并行度是多少。
- **迭代方法**：关掉文件系统缓存（`enable_filesystem_cache = 0`）测试冷启动性能，然后每次改一个变量后对比 `system.query_log` 里的 `query_duration_ms` 和 `read_rows`。

## 和传统 SQL 优化的关系

ClickHouse 的优化和我之前从 [[entities/markus-winand]] 那里学到的传统 SQL 索引优化既有继承，又有根本分歧。

继承的部分在于思维习惯：[[topics/sql-indexing]] 里强调的"先理解访问路径"、[[topics/query-shape-and-index-usage]] 里强调的"WHERE 子句形状决定索引效率"、[[topics/sql-execution-plans]] 里强调的"把执行计划当第一现场"，在 ClickHouse 里完全适用，只是"执行计划"变成了 `EXPLAIN pipeline`，`EXPLAIN indexes = 1` 和 `system.query_log`。

分歧在于索引哲学。传统 B-tree 索引用精确定位换取写入成本——索引越准，写入越慢。ClickHouse 用稀疏索引 + 物理排序换取的是批量读取效率——它不追求精确定位，而是追求**用最小的索引成本跳过大片无关数据**。这导致两者的主键设计逻辑几乎相反：传统数据库建议高基数列在前（提高选择性），ClickHouse 建议低基数列在前（让后置列有"视野"做排除搜索）。

另一个分歧在于"聚合是在有排序的数据上流式完成的"这个思路。在 B-tree 世界里，GROUP BY 几乎必然依赖 hash table 或排序；在 ClickHouse 里，如果数据建表时就已经排好了，聚合不需要额外排序或 hash——[[sources/clickhouse-optimize-aggregation-in-order]] 把这个"免费午餐"的门槛讲得很清楚：GROUP BY 必须是 ORDER BY 前缀。

## 对我的启发

写完这篇，我意识到 ClickHouse 给我的最大冲击不是"它有多快"，而是**它逼着我把"优化"的定义从"查询层面的技巧"重新定义为"建表时对物理世界的承诺"**。传统数据库里，一张表怎么存和怎么查是松耦合的——你可以事后加索引修补救。ClickHouse 里不是：`ORDER BY` 定义的是数据的物理归宿，选错后没有"加个索引纠正"的退路，只能重建表。

这反过来让我更珍惜 wiki 里已有的 ClickHouse 知识脉络。[[topics/clickhouse-deployment-topologies]] 讨论的副本/分片/存算分离，[[topics/clickhouse-common-pitfalls]] 讨论的 part、主键和物化视图的物理约束，[[topics/clickhouse-sharding-decision]] 讨论的生产判断，都和这篇文章在"顺着 ClickHouse 的物理模型设计系统"这个原则上是连贯的。查询优化不是独立技能，而是这个原则在"如何让查询路径对齐物理组织"这个具体问题上的应用。

---
