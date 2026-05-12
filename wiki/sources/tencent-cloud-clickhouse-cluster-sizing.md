---
title: 腾讯云 ClickHouse 集群实例选型指南
type: source
tags: [数据库, ClickHouse, 腾讯云, 选型, 云服务器]
source_count: 1
updated: 2026-05-12
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

## CVM 实例族详细映射

腾讯云 CVM 实例族分为标准型、计算型、内存型、高 IO 型、大数据型、裸金属等。以下是与 ClickHouse 相关的核心实例族：

### 标准型实例族（CPU:内存 = 1:2 或 1:4）

适合大多数 ClickHouse 通用分析场景，平衡的计算、内存和网络资源。

| 实例族 | 处理器 | 内存 | 最高网络 | 特点 |
|--------|--------|------|----------|------|
| **SA9** | AMD EPYC Turin-Dense | DDR5 | 6750万 PPS / 300Gbps | 最新一代，全核睿频 3.4GHz，支持超线程开关 |
| **S9** | Intel Sierra Forest | DDR5 | 3370万 PPS | 最新一代，睿频 2.7GHz，平衡型 |
| **SA9e** | AMD EPYC Turin-Classic | DDR5 | 6750万 PPS | 全核睿频 4.1GHz，更高单核性能 |
| **S9e** | Intel Granite Rapids | DDR5 | 3370万 PPS | 睿频 3.3GHz |
| **S9pro** | Intel Granite Rapids | DDR5 | 3370万 PPS | 睿频 3.6GHz，更高单核性能 |
| **S8** | Intel Emerald Rapids | DDR5 | 4500万 PPS / 120Gbps | 次新一代，睿频 3.0GHz |
| **SA5** | AMD EPYC Bergamo | DDR5 | 4500万 PPS | 支持 AMD SEV-SNP 机密计算 |
| **SA4** | AMD EPYC Genoa | DDR5 | 4500万 PPS / 100Gbps | 睿频 3.7GHz |
| **S6** | Intel Xeon Ice Lake | DDR4 | 1900万 PPS / 100Gbps | 主频 2.7GHz，睿频 3.3GHz |
| **SA3** | AMD EPYC Milan | DDR4 | 1900万 PPS / 100Gbps | 睿频 3.5GHz |

### 内存型实例族（CPU:内存 = 1:8）

适合需要大量内存的 ClickHouse 场景，如宽表聚合、复杂 JOIN、大缓存。

| 实例族 | 处理器 | 内存 | 最高网络 | 特点 |
|--------|--------|------|----------|------|
| **MA9** | AMD EPYC Turin-Dense | DDR5 | 6750万 PPS | 最新一代，1:8 配比 |
| **M9** | Intel Sierra Forest | DDR5 | 3370万 PPS | 最新一代 |
| **MA9e** | AMD EPYC Turin-Classic | DDR5 | 6750万 PPS | 全核睿频 4.1GHz |
| **M9e** | Intel Granite Rapids | DDR5 | 3370万 PPS | 睿频 3.3GHz |
| **M9pro** | Intel Granite Rapids | DDR5 | 3370万 PPS | 睿频 3.6GHz |
| **M8** | Intel Emerald Rapids | DDR5 | 4500万 PPS / 120Gbps | 同规格内存价格最低 |
| **MA5** | AMD EPYC Bergamo | DDR5 | 4500万 PPS | 同规格内存价格最低 |
| **MA4** | AMD EPYC Genoa | DDR5 | 4500万 PPS / 100Gbps | 同规格内存价格最低 |
| **MA3** | AMD EPYC Milan | DDR4 | 1900万 PPS / 100Gbps | 同规格内存价格最低 |
| **M6** | Intel Xeon Ice Lake | DDR4 | 1900万 PPS / 100Gbps | 同规格内存价格最低 |
| **M5** | Intel Xeon Cascade/Cooper Lake | DDR4 | 29Gbps | 配有 AVX-512 |

### 高 IO 型实例族（本地 NVMe SSD）

适合延迟敏感、高并发随机读的 ClickHouse 热数据层。

| 实例族 | 处理器 | 存储 | 最高网络 | 特点 |
|--------|--------|------|----------|------|
| **ITA5** | AMD EPYC Bergamo | NVMe SSD | 4500万 PPS | 单盘 7140GB，整机最高 24 盘 |
| **IT5** | Intel Xeon Cascade Lake | NVMe SSD | 23Gbps | 单盘 3570GB，整机最高 205万 IOPS |
| **IT3** | Intel Xeon Skylake | NVMe SSD | 23Gbps | 单盘 3720GB，整机最高 180万 IOPS |
| **IA5se** | AMD EPYC Bergamo | 单副本 SSD | 4500万 PPS | 单盘 3570GB，随机读写约 10万 IOPS |
| **IA3se** | AMD EPYC Milan | 单副本 SSD | 1900万 PPS | 单盘 3570GB |

### 大数据型实例族（SATA HDD）

适合海量数据归档、顺序扫描为主的 ClickHouse 冷数据层。

| 实例族 | 处理器 | 存储 | 最高网络 | 特点 |
|--------|--------|------|----------|------|
| **D3** | Intel Xeon Cascade Lake | SATA HDD | 27Gbps | 最高 24 块 4TB 盘，94TB 本地存储 |
| **D2** | Intel Xeon Skylake | SATA HDD | 25Gbps | 最高 12 块 12TB 盘，144TB 本地存储 |

### 计算型实例族（高主频）

适合计算密集型、需要高单核性能的 ClickHouse 查询场景。

| 实例族 | 处理器 | 主频 | 最高网络 | 特点 |
|--------|--------|------|----------|------|
| **C6** | Intel Xeon Ice Lake | 3.2GHz / 睿频 3.5GHz | 1900万 PPS / 100Gbps | 最新一代 |
| **C5** | Intel Xeon Cooper Lake | 3.4GHz / 睿频 3.8GHz | 36Gbps | 支持 bfloat16 |
| **C4** | Intel Xeon Cascade Lake | 3.2GHz / 睿频 3.7GHz | 25Gbps | 配有 AVX-512 |

## 网络性能关键指标

实例网络性能与规格对应，规格越高网络转发性能越强：

- **PPS（包每秒）**：最高达 6750万（SA9/SA9e 系列）
- **内网带宽**：最高达 300Gbps（SA9.192XLARGE2304）
- **队列数**：最高 48 队列
- **连接数**：最高 2400万（SA9.192XLARGE2304）

当 PPS 超过 1000万、带宽大于 50Gbps 时，内核协议栈损耗较大，建议用 DPDK 方法获取真实网络性能。

## 定价模式

TCHouse-C 支持包年包月与按量计费。计算节点与 ZooKeeper 节点分别计费，存储（云盘、对象存储）单独计费。不同地域价格存在差异。
