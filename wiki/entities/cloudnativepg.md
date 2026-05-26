---
title: CloudNativePG
type: entity
tags: [CloudNativePG, PostgreSQL, Kubernetes, Operator]
source_count: 1
updated: 2026-05-26
---

> CloudNativePG 对我来说最重要的定位，不是“把 PostgreSQL 放进 Kubernetes 的工具”，而是一个会持续调和 PostgreSQL 集群状态的 Operator。它让数据库更云原生，但也要求运维者更清楚地理解 PV/PVC、Service、WAL 和副本状态之间的边界。

## 我怎么理解它

CloudNativePG 管的是 PostgreSQL 集群的控制面：实例创建、primary/replica 角色、Service、证书、存储卷、failover 和副本重建。它的价值在于把很多原本靠人手维护的数据库运行细节变成 Kubernetes 资源状态。

但这次恢复经验也提醒我，Operator 不会替我解决所有数据语义问题。它可以创建一个新副本，却不能判断被删掉的 PVC 背后哪块云盘才是事故前的权威数据；它可以把 Cluster 状态汇总成 Ready，却不代表每个 replica 的 WAL replay 都健康。

## 在事故恢复中的关键边界

我会把 CloudNativePG 的边界记成三句话。

第一，**Pod 是可重建的，PVC 不是随便能重建的**。Pod 删除通常只需要等待调和；PVC 删除则取决于 PV 的回收策略和底层云盘是否仍在。

第二，**Service 是流量事实，不是数据事实**。临时把 Service 指到恢复 clone 可以救业务，但最终仍要把数据迁回 CNPG 管理的 primary，并让 Service 回到 CNPG 生成的读写入口。

第三，**副本健康要看 PostgreSQL 自己的复制视图**。`pg_stat_replication`、`pg_stat_wal_receiver` 和 WAL LSN 比 Operator 总览更接近真实复制状态。

## 相关经验

这次会话沉淀出的实践是：生产或准生产数据库的 StorageClass 应优先使用 `Retain`，并配合快照或备份；恢复 clone 应作为临时路径，迁回时用集群内 Job 做逻辑迁移；副本追不上 WAL 时应重建副本，而不是无限等待。

来源：[[sources/cnpg-recovery-incident]]

相关页面：[[topics/cloudnativepg-recovery]] · [[topics/kubernetes-persistent-storage]] · [[entities/kubernetes]]
