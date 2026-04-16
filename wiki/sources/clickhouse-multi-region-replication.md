---
title: "Does ClickHouse support multi-region replication?"
type: source
tags: [数据库, ClickHouse, 多地域, 副本]
source_count: 1
source_file: raw/articles/clickhouse-multi-region-replication.md
author: ClickHouse
published: 2026-04-16
updated: 2026-04-16
---

# Does ClickHouse support multi-region replication?

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/knowledgebase/multi-region-replication)

## 核心结论

ClickHouse 支持多地域复制，但官方给出的边界非常直接：**地域间时延最好保持在两位数毫秒，否则写入性能会因为分布式共识路径而明显受损。**

## 文档最重要的提醒

- 美国东西海岸之间的复制大概率可行；
- 美国和欧洲之间的复制则被明确举例为“不太适合”；
- 配置方式和单地域复制没有本质差别，只是把 replica 放到了不同地域。

## 这意味着什么

这篇 FAQ 很短，但它补上了一个经常被忽略的现实：多地域复制不是“把副本放远一点”这么简单，而是把**网络时延直接写进了写路径**。因此，多地域更适合作为：

- 跨机房容灾；
- 区域级故障备份；
- 在低时延地域之间做有限的跨地域冗余。

它不适合作为一个默认的全球化写入拓扑。

## 对我的启发

这让我把 ClickHouse 的多副本能力进一步拆分成两个问题：

- 同地域副本，主要是高可用；
- 跨地域副本，已经变成网络与共识预算问题。

这两者虽然都叫 replica，但工程代价完全不同。

---

相关页面：[[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-separation-storage-compute]]
