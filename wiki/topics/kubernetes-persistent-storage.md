---
title: Kubernetes 持久化存储：静态卷、动态卷与快照的选择框架
type: topic
tags: [Kubernetes, 持久化存储, CSI, 存储设计]
source_count: 4
updated: 2026-05-26
---

> 在 Kubernetes 里用存储，表面上是写 YAML，实际上是做一系列不可逆的选型决策：云盘类型、绑定策略、回收行为、备份方式，以及这些选择对应用生命周期和运维成本的长期影响。

这篇文章不是某一类存储的教程，而是把 [[sources/ack-static-disk-volume]]、[[sources/ack-dynamic-disk-volumes]]、[[sources/ack-disk-volume-snapshots]] 和一次 [[sources/cnpg-recovery-incident]] 放到同一个判断框架里，回答一个问题：**什么时候该用静态卷，什么时候该用动态卷，快照又该什么时候介入**。

## 静态卷 vs 动态卷：核心差异不在技术，在生命周期所有权

| 维度 | 静态卷 | 动态卷 |
|---|---|---|
| 云盘生命周期 | 集群外部管理 | 由 StorageClass + CSI 自动管理 |
| 适用场景 | 已有云盘、数据迁移、明确配额 | 新应用、弹性伸缩、独立存储 |
| 关键资源 | PV（手动声明云盘属性） | StorageClass（定义创建模板） |
| 绑定时机 | PV 创建后即可绑定 | `WaitForFirstConsumer` 延迟到 Pod 调度后 |
| 副本支持 | 单 Pod（RWO） | StatefulSet volumeClaimTemplates（每副本独立） |
| 扩容 | 手动 | StorageClass 开启 `allowVolumeExpansion` 后可在线扩容 |

我觉得这个对比里最重要的一点是：**静态卷的"静态"不是指卷的内容不变，而是指卷的创建和销毁不由 Kubernetes 控制**。当你已经有了一块云盘——不管是从旧集群迁移来的、还是云厂商侧预先分配的——静态卷是把它纳入 Kubernetes 管理的最短路径。

动态卷则更适合"应用需要多少存储就给多少"的场景。StatefulSet 的 `volumeClaimTemplates` 让每个 Pod 获得独立的 PVC 和云盘，扩缩容时自动创建或删除，不需要人工干预。

## StorageClass：被低估的架构决策点

很多人把 StorageClass 当成"云盘类型选择器"，但它的参数实际上定义了一套存储治理规则：

- `volumeBindingMode`：`WaitForFirstConsumer` 在多可用区场景下几乎必选，否则 PVC 和 Pod 很容易跨区失配；但虚拟节点（ECI/ACS）场景下反而不能用，因为虚拟调度不遵循这个流程。
- `reclaimPolicy`：`Delete` 适合临时数据或测试环境，`Retain` 适合生产数据库。这个决策一旦做错，误删 PVC 时要么是数据意外丢失，要么是云盘残留产生额外费用。
- `allowVolumeExpansion`：初期不开，后期扩容时可能被迫重建 StorageClass 或走更复杂的替换路径。
- `encrypted`：数据敏感型应用可以直接在存储层加密，无需改动应用代码。

## RWO 约束：应用架构的前置条件

云盘默认是 ReadWriteOnce（RWO）。这个看似简单的访问模式，实际上对应用架构有深刻影响：

- **不能用 Deployment 多副本共享同一个 PVC**。第二个 Pod 会因为挂载冲突永远 Pending。
- **StatefulSet 是标准答案**，但不是唯一答案。单副本 Deployment + 独立 PVC 也可以，只是不具备弹性伸缩能力。
- **多重挂载**（multiAttach）可以突破 RWO 限制，但仅限于裸设备（Block 模式），且需要 NVMe 云盘。标准文件系统（ext4/xfs）仍然不能多节点并发写入。

这个约束意味着：在选择云盘之前，必须先确定应用是可水平拆分的（每副本独立存储）还是需要共享存储的（需要 NAS、OSS 等其他存储类型）。

## CNPG 事故给我的补课：Retain 是刹车，不是备份

这次 [[sources/cnpg-recovery-incident]] 把 `reclaimPolicy` 从文档参数变成了真实事故里的分水岭。Pod 删除和 PVC 删除看起来都像“资源没了”，但数据后果完全不同：Pod 没了，只要 PVC 还在，控制器通常能重新挂载原盘；PVC 没了，如果 PV 是 `Delete`，底层云盘可能也随之删除，如果 PV 是 `Retain`，才有机会通过 Released PV 重新绑定回来。

我现在会把生产数据库的动态云盘策略默认推向 `Retain`，但不会把它当成备份。`Retain` 防的是误删 PVC 连带删盘；它不防逻辑错误、不防坏数据被复制、不防主从一起写坏，也不提供时间点恢复。真正稳妥的组合是：数据库 PVC 使用 Retain，关键操作前做 VolumeSnapshot，长期再配 WAL 归档或数据库级备份。

还有一个实践细节值得保留：Operator 管理的数据库不要只看 Kubernetes 层面的 Ready。对于 PostgreSQL 副本，仍然要回到数据库自己的复制视图——主库看 `pg_stat_replication`，副本看 `pg_stat_wal_receiver`，确认 WAL LSN 能持续追上。否则一个“Ready 的副本”也可能已经因为缺失 WAL segment 而无法继续同步。

## 快照：不是"高级功能"，而是运维基线

VolumeSnapshot 的设计和 PVC/PV 是对称的：VolumeSnapshotContent 对应 PV，VolumeSnapshot 对应 PVC，VolumeSnapshotClass 对应 StorageClass。这种对称性让它很容易被已有 Kubernetes 经验的团队上手。

快照在生产环境中的价值不只是"备份"，更是：

- **迁移验证**：在切生产流量前，先用快照恢复一个完整副本做回归测试。
- **快速恢复**：ESSD 的"快照极速可用"能力可以把 RTO 从小时级缩短到分钟级。
- **开发环境同步**：用生产快照定期刷新开发/测试环境的存储卷，避免数据漂移。

但要注意 `forceDelete` 的默认值变化。从 csi-provisioner v1.26.5 起，强制删除不可关闭，这意味着删除 VolumeSnapshot 时不会保留"已被引用过的快照"。对于需要长期保留的快照（如合规要求），应该在云厂商侧建立独立的快照策略，而不是完全依赖 Kubernetes 层面的生命周期管理。

## 生产检查单

基于三篇文档的实践经验，我总结出以下检查单：

- [ ] 确定应用是否真的需要云盘（I/O 性能要求高、无共享需求）
- [ ] 确定静态卷 vs 动态卷（云盘是否已存在、谁负责生命周期管理）
- [ ] 为 StorageClass 选择合适的 `volumeBindingMode`（多可用区 → WaitForFirstConsumer；虚拟节点 → Immediate）
- [ ] 确认 `reclaimPolicy` 符合数据安全预期（生产数据库推荐 Retain）
- [ ] 为 StatefulSet 开启 `allowVolumeExpansion`（预留未来扩容路径）
- [ ] 配置 `fsGroupChangePolicy: OnRootMismatch`（避免大量文件时挂载超时）
- [ ] 为关键数据配置 VolumeSnapshotClass（定义 retentionDays 和 deletionPolicy）
- [ ] 确认 CSI 组件版本满足快照功能要求（≥ v1.22.12 支持离线快照）
- [ ] 验证节点可用区与云盘可用区的一致性（避免 Pod 重建后无法调度）

## 我对这三篇文档的整体判断

它们不是 Kubernetes 存储的通用教材，而是阿里云 ACK 在云盘这个具体存储后端上的**工程实现手册**。这意味着里面的很多细节——`volume-topology` annotation、`disktype` 节点标签、灵骏节点的特殊要求、`forceDelete` 的版本变化——都是阿里云 CSI 插件的特有行为，而不是 Kubernetes 标准 API 的一部分。

对于在阿里云 ACK 上运行有状态应用的人来说，这些细节是避不开的。对于使用其他云厂商或自管集群的人来说，抽象概念（PV/PVC/StorageClass/VolumeSnapshot 的关系）仍然适用，但具体参数需要对照对应厂商的 CSI 文档。

来源：[[sources/ack-static-disk-volume]] · [[sources/ack-dynamic-disk-volumes]] · [[sources/ack-disk-volume-snapshots]] · [[sources/cnpg-recovery-incident]]

相关页面：[[entities/kubernetes]] · [[entities/cloudnativepg]] · [[topics/cloudnativepg-recovery]] · [[topics/kubernetes-autoscaling]] · [[topics/clickhouse-deployment-topologies]]
