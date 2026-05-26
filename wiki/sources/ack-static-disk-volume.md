---
title: ACK 静态云盘存储卷使用指南
type: source
tags: [Kubernetes, 持久化存储, 阿里云, CSI]
source_count: 0
updated: 2026-05-26
---

这篇文章解决的核心问题是：**当云盘已经存在时，如何在 ACK 集群里把它正确注册给 Pod 使用**。它的思路不是动态创建，而是"先注册、再绑定、后挂载"，也就是 Kubernetes 里常说的静态卷模式。

## 什么场景适合静态卷

不是所有人都需要动态卷。如果你手里已经有一块云盘，或者需要把一块已有的数据盘复用到新集群里，静态卷是最直接的路径。典型场景包括：数据库迁移时需要保留原有磁盘、测试环境需要反复挂载同一块盘、或者云厂商侧已经有明确的磁盘配额规划。

静态卷的本质是：你在 Kubernetes 外部管理云盘的生命周期，在集群内部只做"声明和绑定"。

## 创建 PV：不只是填云盘 ID

文档里最让我意外的细节是 `csi.alibabacloud.com/volume-topology` 这个 annotation。很多教程只让你填 `volumeHandle`（云盘 ID）和 `nodeAffinity`（可用区），但真正导致 Pod 调度失败的原因往往是**节点不支持对应的云盘类型**。这个 annotation 提前把磁盘类型亲和性暴露给调度器，避免了 Pod 落到不兼容节点上。

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  annotations:
    csi.alibabacloud.com/volume-topology: '{"nodeSelectorTerms":[{"matchExpressions":[{"key":"node.csi.alibabacloud.com/disktype.cloud_essd","operator":"In","values":["available"]}]}]}'
```

`claimRef` 是个容易被忽略的配置。如果你希望这块云盘只被某个特定的 PVC 绑定，在这里直接声明；如果想让 PVC 按需绑定，则去掉它。 Retain 策略在这里通常更合理——因为你本来就在外部管理云盘，PVC 的删除不应该顺带删掉底层数据。

## 从 PVC 到 StatefulSet：RWO 的约束

文档反复提醒云盘是**非共享存储**，默认 ReadWriteOnce（RWO）。这意味着：

- 同一个 PVC 不能同时被两个 Pod 挂载
- Deployment 的多副本共享同一块 PVC 会导致新 Pod 因为挂载冲突而 Pending
- 推荐使用 StatefulSet，每个副本有自己的 PVC

这个约束在应用设计阶段就要想清楚。很多人先写了个 Deployment，然后才发现云盘挂不上，再回头改成 StatefulSet，这种重构完全可以提前避免。

## 生产环境的隐含成本

文档在"应用于生产环境"一节提到了几个容易被低估的点：

- **fsGroup 的递归权限修改**：在 Pod 的 `securityContext` 里设置 `fsGroup` 会导致 kubelet 在挂载时对整个卷执行 `chmod`/`chown`。文件量大的话，挂载时间会从秒级变成分钟级。1.20 以上集群建议把 `fsGroupChangePolicy` 设为 `OnRootMismatch`。
- **Pod 重建后的可用区约束**：如果 Pod 因为节点故障被驱逐到另一个可用区，而云盘又无法跨可用区挂载，Pod 就会一直 Pending。 `nodeAffinity` 在这里不是为了优化，而是为了保证可用性。
- **云盘选型**：SSD 云盘和高效云盘已逐步停售，建议用 ESSD PL0 或 ESSD Entry 替代高效云盘，用 ESSD AutoPL 替代 SSD。

## 资源释放的顺序感

文档给出的释放顺序值得记一下：先删工作负载（停止 Pod、卸载卷）→ 再删 PVC → 最后按需删 PV。如果回收策略是 Retain，删 PVC 只会把 PV 标记为 Released，不会删云盘。这符合"静态卷由外部管理"的设定，但也意味着你需要额外关注 Released 状态的 PV 清理。

来源：[阿里云官方文档](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-a-statically-provisioned-disk-volume)

相关页面：[[topics/kubernetes-persistent-storage]] · [[entities/kubernetes]] · [[sources/ack-dynamic-disk-volumes]] · [[sources/ack-disk-volume-snapshots]]
