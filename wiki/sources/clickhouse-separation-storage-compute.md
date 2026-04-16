---
title: ClickHouse 存算分离
type: source
tags: [数据库, ClickHouse, 存算分离, 对象存储]
source_count: 1
source_file: raw/articles/clickhouse-separation-storage-compute.md
author: ClickHouse
published: 2026-04-16
updated: 2026-04-16
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/guides/separation-storage-compute)

这篇文档让我特别清楚地看到，ClickHouse 的“存算分离”不是一个抽象概念包装，而是一套非常具体的介质配置和运维代价交换。也正因为它足够具体，我反而更容易判断它什么时候值得引入。

## 核心结论

ClickHouse 支持把 `MergeTree` 数据放进 S3 一类对象存储中，让计算资源和存储资源独立扩缩容。它尤其适合**冷数据占比高、存储成本敏感、希望计算弹性更强**的场景。

## 这篇文档给出的具体形态

- 在 `storage_configuration` 中声明 `s3_disk`；
- 可选地在前面再挂一层 `s3_cache` 本地缓存盘；
- 定义 `storage_policy = 's3_main'`；
- 创建普通 `MergeTree` 表时直接指定 `storage_policy`，ClickHouse 会在底层处理 S3-backed 存储。

换句话说，存算分离并不是换一个全新 SQL 模型，而是通过**存储配置 + table settings** 改变底层介质。

## 官方强调的两个现实约束

- **这是更复杂的自管理架构**：文档明确说，自建的存算分离比标准部署复杂得多。
- **不要依赖对象存储生命周期规则**：对 AWS / GCS bucket 配置生命周期策略可能会把表弄坏。

## 和高可用的关系

文档还给出一个重要提醒：存算分离不等于自动高可用。若要容灾，仍需要额外叠加复制方案，例如 `ReplicatedMergeTree`。这说明“把数据放到对象存储”解决的是介质与成本问题，不自动解决复制与协调问题。

## 对冷热数据的意义

官方直接指出，这个模式对“冷数据性能不那么关键”的场景尤其有用。也就是说，ClickHouse 并没有把冷热分层包装成一个抽象名词，而是直接通过对象存储 + 缓存 + policy 提供实现原语。

## 对我的启发

这篇文档让我把存算分离看成一种非常具体的工程判断：**当数据量继续增长，但昂贵本地盘未必值得全量承载时，可以把冷数据沉到对象存储，再用本地缓存把真正热的工作集拉回来。** 我会把这页和冷热分层、复制拓扑一起看，因为它们本来就是同一张部署决策表上的不同维度。

---

相关页面：[[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]] · [[sources/clickhouse-external-disks-for-storing-data]] · [[sources/clickhouse-replication-and-scaling]]
