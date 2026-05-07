---
title: ClickHouse production-v4 腾讯云验证
type: source
tags: [ClickHouse, 腾讯云, TKE, CBS, COS, 迁移]
source_count: 1
updated: 2026-05-06
---

这组 production-v4 文档对我最大的价值，是把前一轮迁移方案从“能在验证集群跑通”推进到“放进腾讯云生产形态里还剩哪些硬边界”。它不是一份泛泛的 ClickHouse 部署模板，而是在 TKE、CBS、COS、ClickHouse Operator 和现有业务数据规模之间重新做了一次取舍。

## 这次验证真正改变了什么

之前我更倾向用更多 shard 把历史数据摊薄，因为脑子里默认的是“全量数据长期留在热盘”。production-v4 把这个前提改掉了：目标集群从一开始就要启用冷热分层，热层只按最近一个月的数据和 merge / TTL move 写放大来规划，深历史数据最终沉到 COS 兼容的 S3 disk 后面。

在这个前提下，`2 shards x 2 replicas` 反而比 `6 shards x 2 replicas` 更像一个稳妥起点。它减少了 `Distributed` 查询 fan-out、Pod / PVC / 副本队列和 Keeper 元数据数量，同时仍然给最近一个月热数据留下足够空间。真正需要扩的时候，优先顺序也变了：先把单 ClickHouse Pod 从 `16C / 64GiB` 升到 `32C / 128GiB`，再看是否扩热盘，最后才考虑增加 shard。

这不是说更多 shard 错了，而是它回答的是另一类问题。若全量 `7 TiB` 级数据都要长期放在本地高性能盘里，多 shard 能直接降低单 shard 压力；但若首版生产设计已经把对象存储冷层作为长期成本治理机制，就不应该为了历史容量过早把查询和运维复杂度放大。

## 当前资源口径

production-v4 的资源规格收敛为：

```text
ClickHouse Server:
- 拓扑：2 shards x 2 replicas
- 单 Pod：16C / 64GiB
- 单 Pod 热盘：2TiB CBS，优先增强型 SSD

ClickHouse Keeper:
- 拓扑：3 replicas
- 单 Pod：4C / 16GiB
- 单 Pod 磁盘：20Gi CBS
```

这个设计背后的输入很具体：现网全量约 `7.22TB`，近 `30` 天增量约 `0.53TB`；`query_log` 观测窗口里，查询内存的 `p95` 约 `40MiB`，`p99` 约 `176.85MiB`，最大值约 `6.99GiB`。这说明当前更像是存储形态和迁移窗口问题，而不是单查询内存已经逼近大规格节点上限。

我会把 `2TiB` 热盘理解成“稳态热层容量 + merge / TTL move 临时空间 + 对象存储 cache + 云盘性能余量”，而不是简单地拿最近一个月 `0.53TB` 除以两个 shard 得到的数学答案。首次迁移和历史回填阶段仍然要按全量数据、写放大和回灌节奏单独评估，不能拿 steady-state 热层容量替代迁移期容量预算。

## 腾讯云环境暴露的执行边界

这轮验证已经确认了几件基础事实：目标 TKE 集群可访问，目标 namespace 是新环境，CBS 是默认持久化入口，ClickHouse Operator 的 CRD 可以安装，COS 冷层按 S3 兼容协议接入，而不是通过 `cos-csi` 把对象存储伪装成本地文件系统。

但它也暴露了几个不能跳过的边界：

- Operator chart 能安装不代表 controller manager 能在节点侧拉到镜像，镜像分发必须提前验证。
- CRD 存在不等于 `KeeperCluster` / `ClickHouseCluster` 能被调谐，controller Ready 才是下一步创建集群的前提。
- 当前节点形态如果是超级节点 / serverless 类形态，就必须额外确认它是否适合数据库的持久化、独占资源和稳定 I/O。
- COS bucket、endpoint、prefix、凭据和生命周期策略没有提供前，冷热分层只能停留在模板阶段，不能算已验证。
- manifest 中不能固化真实密钥；Secret 只能作为运行环境交付物，wiki 里也不记录任何真实对象存储路径或访问凭据。

这些点提醒我，云厂商迁移验证的阻塞不一定来自 ClickHouse 本身。很多时候，真正决定迁移能否进入下一步的是镜像、节点形态、StorageClass、对象存储 endpoint、Secret 管理和调度约束。

## 我会保留的判断

production-v4 不推翻之前的迁移纪律：`S0` 快照、`T0` 双写确认、静态源历史回灌、缺口补数、统一对账和切换观察仍然是主路径。它改变的是目标集群资源起点和腾讯云落地边界。

我现在会把生产迁移拆成两层判断：

第一层是数据一致性路径。这里不因云厂商变化而变化，仍然要靠双水位、静态源、文件式回灌和独立对账来保证。

第二层是运行形态。这里必须服从腾讯云 TKE / CBS / COS 的真实验证结果：先让 `2 x 2 + 3 Keeper` 的最小生产形态跑稳，把镜像、冷热分层和持久化打通，再根据 CPU、内存、热盘、merge backlog 和查询 fan-out 决定是升配还是加 shard。

这也是我对这份材料最重要的吸收：生产迁移方案不能只写“理想拓扑”，必须把云厂商控制面能否承载这套拓扑一起验证。否则 ClickHouse DDL 再正确，也会卡在节点拉镜像、PVC 行为或对象存储连通性这种更底层的问题上。

来源：production-v4 腾讯云 TKE 验证文档（本地项目文档，不记录本机绝对路径）

相关页面：[[topics/clickhouse-production-migration]] · [[topics/clickhouse-deployment-topologies]] · [[entities/clickhouse]] · [[entities/clickhouse-keeper]]
