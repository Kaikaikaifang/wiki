---
title: ClickHouse 外部存储
type: source
tags: [数据库, ClickHouse, 存储策略, 冷热分层]
source_count: 1
source_file: raw/articles/clickhouse-external-disks-for-storing-data.md
author: ClickHouse
published: 2026-04-16
updated: 2026-04-16
---

来源：[[entities/clickhouse]] · [原文](https://clickhouse.com/docs/operations/storing-data)

## 核心结论

这篇文档给的不是一个固定“冷热存储方案”，而是一组能拼出冷热分层的底层原语：**disk、storage policy、object storage、local metadata、filesystem cache**。

## 文档提供的能力原语

- `MergeTree` / `Log` 家族表可把数据放到 S3、Azure Blob Storage 等外部存储；
- 表可以通过 `SETTINGS storage_policy = '...'` 或 `SETTINGS disk = '...'` 指定存储落点；
- 对远端存储可以再挂一层 `cache` 类型磁盘，由本地路径承载文件系统缓存；
- 缓存支持大小上限、命中阈值、旁路阈值、写穿与按查询限制；
- 还给了 `system.filesystem_cache`、`system.filesystem_cache_log`、`SHOW FILESYSTEM CACHES` 等观察接口。

## 我对“冷热分层”的归纳

这里关于冷热分层的理解是**我基于文档做的归纳**：

- **冷层**：对象存储，容量大、成本低，但远端访问延迟更高；
- **热层**：本地文件系统缓存或更快磁盘，承载最近读过、会被重复访问的数据段；
- **策略层**：`storage_policy` 决定表默认使用哪种介质组合。

也就是说，ClickHouse 的冷热分层更像**存储策略组合**，而不是某个独立产品开关。

## 为什么这篇文档很重要

如果只看“存算分离”那篇文章，很容易把对象存储理解成一个高层架构名词；这篇文档则把它拆回实现细节，让我看到：

- 数据文件和元数据不一定放在同一个地方；
- 缓存不是附属优化，而是远端对象存储可用性的关键补偿；
- 真正决定行为的是磁盘定义、policy 绑定和查询级缓存设置。

## 对我的启发

冷热分层不是简单把“旧分区丢到 S3”就完事，而是要同时考虑：

- 访问路径是否还可接受；
- 缓存是否足以覆盖工作集；
- 可观测性是否能告诉我哪些读在回源、哪些读命中了本地缓存。

---

相关页面：[[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-manage-and-deploy]]
