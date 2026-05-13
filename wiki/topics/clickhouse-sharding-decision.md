---
title: ClickHouse 分片决策
type: topic
tags: [数据库, ClickHouse, 分片, 架构决策, 容量规划]
source_count: 1
updated: 2026-05-13
---

> 分片不是 ClickHouse 集群的默认配置，而是一个需要被"证明必要"的架构决策。冷热分层已经把容量问题从本地盘转移到了对象存储，分片的唯一理由只剩下"单机处理能力不够"。

## 副本是配置，分片是架构

从单实例迁移到集群时，很多人会把"是否分片"理解成 `remote_servers` 配置里的一个参数区别。但实际上：

| 维度 | 加副本（1 shard × N replicas） | 加分片（M shards × N replicas） |
|---|---|---|
| 数据分布 | 所有节点数据完全相同 | 需要设计分片键，数据按 key 分散 |
| 查询路径 | 任意节点可查全量，可开 Parallel Replicas | 必须通过 `Distributed` 表，涉及跨分片聚合 |
| 写入路径 | 写入一个 replica 自动复制 | 需要写入路由（`Distributed` 表或应用层 shard key） |
| 扩容 | 加 replica，数据自动同步 | resharding，历史数据重分布 |
| 缩容 | 直接下线节点 | 数据迁移到其他 shard |
| 配置复杂度 | `remote_servers` 里加一行 replica | 分片键、路由规则、均衡策略都要设计 |
| 运维面 | 线性增加（N 个相同节点） | 指数增加（分片故障 = 部分数据不可访问） |

这让我把分片从"集群的默认选项"重新定位成"有明确触发条件才引入的复杂度"。

## 分片的合理触发条件

在冷热分层已经开启的前提下，分片的唯一合理触发条件是**单机处理能力成为明确瓶颈**：

| 触发条件 | 具体表现 | 为什么分片 |
|---|---|---|
| 热工作集 > 单机本地盘/内存容量 | 即使冷数据在对象存储，热数据仍然太大，必须拆到多个节点的本地 cache | 单机 cache 无法覆盖热工作集 |
| 写入吞吐量 > 单机 I/O 或 CPU 上限 | 所有 replica 都要处理全量写入，单节点写入能力饱和 | 分散写入压力 |
| 查询并发极高且 CPU 成为瓶颈 | 加 replica 已经不够（或成本太高），需要 shard 分散计算 | Parallel Replicas 效果不足 |
| 特定查询模式需要物理隔离 | compute-compute separation 无法通过 replica 实现 | 独立资源边界 |

如果以上条件都不满足，**不分片是更简洁、更弹性、运维面更小的选择**。

## 一个真实场景的决策过程

以下是我基于实际生产数据做的分片判断：

**生产环境概况：**

- 4 个独立单节点（非集群），各存全量 7.22TB 数据
- 单节点规格：64C / 256GiB
- 近 30 天增量：约 0.53TB
- 目标冷热分层周期：1 个月
- query_log 窗口（2026-04-22 ~ 2026-04-29）：
  - p95 memory_usage：40.06MiB
  - p99 memory_usage：176.85MiB
  - max memory_usage：6.99GiB
- 单实例容器内观测：
  - clickhouse-server 当前 RSS 约 14GiB，历史最大约 31GiB
  - CPU 瞬时约 4C，峰值约 18C
  - OS page cache 约 217GiB

**判断过程：**

1. **热数据量**：目标冷热分层周期 1 个月，热数据 ≈ 0.53TB。ClickHouse 典型压缩率 3-10x，压缩后约 50-170GB。
2. **内存覆盖**：每节点 217GiB page cache，远大于压缩后的热数据量。几乎所有热查询都能命中内存。
3. **CPU 余量**：峰值 18C / 64C = 28%，有大量余量。
4. **内存压力**：query max 7GB，server RSS max 31GB / 256GiB = 12%，内存压力极低。
5. **写入量**：0.53TB/月 ≈ 18GB/天，均匀分布后每个 replica 的写入压力微乎其微。

**结论：不分片。** 所有触发条件都不满足。改为 1 shard × 4 replicas 的全副本集群，配合冷热分层和 Parallel Replicas。

## 为什么冷热分层改变了分片的 ROI

冷热分层开启后，分片的传统动机被大幅削弱：

- **冷数据**（历史归档）已经不在本地盘上，对象存储容量近乎无限；
- 决定本地盘占用的不再是"全量历史"，而是**热工作集**；
- "单节点存不下"这个传统分片动机，已经被"热工作集是否能被单机 cache 覆盖"取代。

这让我把扩容顺序收敛为：

1. 先验证冷热分层是否正常工作（对象存储冷层、cache disk、热盘容量、节点 I/O）；
2. 如果 CPU 或内存先吃紧，优先纵向升配；
3. 只有当单 shard 数据量、写入吞吐或扫描压力成为**明确瓶颈**时，再增加 shard。

## 从独立节点到全副本集群的迁移路径

如果当前是多个独立单节点（非集群），迁移到 1 shard × N replicas 的推荐路径：

1. **部署 ClickHouse Keeper**（3 节点）
2. **选定一个权威源节点**，执行：
   ```sql
   DETACH TABLE your_table;
   ATTACH TABLE your_table AS REPLICATED;
   SYSTEM RESTORE REPLICA your_table;
   ```
3. **其他节点清空重建**，创建同结构 `ReplicatedMergeTree` 表，等待自动复制
4. **建立 `Distributed` 表**作为统一查询入口
5. **配置冷热分层**：`storage_policy` + TTL move
6. **开启 Parallel Replicas**：`enable_parallel_replicas = 1`

**关键前提**：如果当前各独立节点的数据不完全一致，**不要试图对齐数据**，直接选定一个权威源，其他节点重建。这比数据治理更简单、更可控。

## 常见误区

- **"集群默认应该分片"**：ClickHouse 的强项是单机并行，过早分片会增加 `Distributed` 查询 fan-out 和运维面。
- **"7TB 数据必须分片"**：冷热分层后，本地只需要承载热工作集（本例中 < 200GB），7TB 中的大部分会进入对象存储。
- **"加 replica 和加分片一样简单"**：加 replica 是配置参数的变化；加分片需要分片键设计、数据重分布、查询路径调整，是架构重构。
- **"不分片就不能并行查询"**：Parallel Replicas 可以在无分片前提下，以 granule 为工作单元把查询并行到多个 replica。

## 对我的启发

这次决策让我把 ClickHouse 的扩容逻辑从"数据量大就分片"简化成了"先证明单机瓶颈，再引入分片"。冷热分层是这个简化得以成立的关键前提——它把容量层从本地盘转移到了对象存储，让本地节点只需要关心"热工作集是否能被 cache 覆盖"和"单机 CPU/内存是否饱和"。

这也让我意识到，分析数据库的部署优化和 OLTP 世界的思路并不一样。在 OLTP 里，分片（sharding）往往是扩展的默认路径；但在 ClickHouse 里，**全副本 + Parallel Replicas + 冷热分层**已经能解决绝大多数场景的扩展问题，分片应该被当作"最后手段"而不是"默认选项"。

---

来源：[[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-cloud-architecture]] · [[sources/clickhouse-parallel-replicas]] · [[sources/clickhouse-separation-storage-compute]] · [[sources/clickhouse-attach-as-replicated]] · [[sources/clickhouse-cold-hot-storage]]

相关页面：[[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-cluster-sizing]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[entities/clickhouse]]
