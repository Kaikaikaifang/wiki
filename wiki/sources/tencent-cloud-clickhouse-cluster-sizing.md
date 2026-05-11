---
title: 腾讯云 ClickHouse 集群实例选型指南
type: source
tags: [数据库, ClickHouse, 腾讯云, 选型, 云服务器]
source_count: 1
updated: 2026-05-11
---

> 来源：[云服务器实例规格 - 腾讯云](https://cloud.tencent.com/document/product/213/11518) 及 [云数据仓库 TCHouse-C 入门指南](https://www.tencentcloud.com/document/product/1129/44393)

## 核心信息

腾讯云 ClickHouse 托管服务（TCHouse-C）的节点规格可分为三类：标准型、存储优化型、高性能型。同时协调层（ZooKeeper）有独立的规格梯度。这些规格与腾讯云 CVM 实例族存在映射关系，但托管服务已经把 IO 配置（磁盘类型、数量、大小）打包进了规格定义。

## 计算节点规格

| 类型 | 规格 | 磁盘配置 | 适用场景 |
|------|------|----------|----------|
| **标准型** | 4核16GB ~ 128核256GB | 云盘（需另配） | 通用分析场景，CPU 与内存比例 1:2，适合大多数工作负载 |
| **存储优化型** | 32核128GB（12×3720GB SATA HDD）<br>64核256GB（24×3720GB SATA HDD）<br>84核320GB（24×3720GB SATA HDD） | 大容量 SATA HDD | 数据量大、以顺序扫描为主的分析场景，单位存储成本最低 |
| **高性能型** | 32核128GB（2×3570GB NVMe SSD）<br>64核256GB（4×3570GB NVMe SSD）<br>84核320GB（4×3570GB NVMe SSD） | NVMe SSD | 延迟敏感、高并发点查或随机读场景，IOPS 与吞吐最高 |

## ZooKeeper 节点规格

协调层节点规格从 4核16GB 到 128核256GB 不等。文档建议：负载越重，规格越高。Keeper 节点主要承载元数据协调、副本同步与分布式 DDL 状态，通常不需要与计算节点同配。

## CVM 实例族映射

腾讯云 CVM 实例族分为标准型（SA9/S9/S8/SA5 等）、计算型、内存型、高 IO 型与裸金属。ClickHouse 作为 CPU 与内存双密集的分析引擎，实际选型时应关注：

- **CPU:内存比**：ClickHouse 推荐 1:2 到 1:4，内存不足会限制聚合、join 与缓存效率；
- **磁盘类型**：本地 NVMe SSD > 增强型 SSD 云盘 > 普通云盘，HDD 仅适合冷数据或归档层；
- **网络带宽**：集群节点间、节点与对象存储之间需要高内网带宽，注意规格表中的内网带宽上限；
- **裸金属**：当虚拟化开销不可接受、需要 pinning NUMA 或绑定本地盘时考虑。

## 定价模式

TCHouse-C 支持包年包月与按量计费。计算节点与 ZooKeeper 节点分别计费，存储（云盘、对象存储）单独计费。不同地域价格存在差异。
