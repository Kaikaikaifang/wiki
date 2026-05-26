---
title: ACK 云盘存储卷快照与恢复指南
type: source
tags: [Kubernetes, 持久化存储, 阿里云, 快照, CSI]
source_count: 0
updated: 2026-05-26
---

这篇文章解决的核心问题是：**在 ACK 里如何为云盘存储卷做备份，以及备份之后如何恢复**。它不是讲传统的手动快照操作，而是把 Kubernetes 的 VolumeSnapshot API 和阿里云 ECS 快照能力衔接起来的完整工作流。

## Kubernetes 快照的三层抽象

文档用一张表把三个资源类型的关系说得很清楚：

| 资源 | 类比 | 谁创建 | 命名空间 |
|---|---|---|---|
| VolumeSnapshotContent | PV | 管理员 | 无 |
| VolumeSnapshot | PVC | 操作员 | 有 |
| VolumeSnapshotClass | StorageClass | 管理员 | 无 |

这个类比帮我理解了一个之前模糊的点：VolumeSnapshotContent 是后端的快照在 Kubernetes 里的投影，VolumeSnapshot 是用户侧的申请，VolumeSnapshotClass 则是"快照模板"。和 PVC/PV 一样，它们之间是一对一绑定的。

## 动态快照：最简路径

动态创建快照的流程很直接：

1. 创建 VolumeSnapshotClass（定义 retentionDays、forceDelete、deletionPolicy）
2. 创建 VolumeSnapshot（引用 PVC 和 VolumeSnapshotClass）
3. 系统自动创建 VolumeSnapshotContent 和底层 ECS 快照
4. 用新 PVC 引用这个 VolumeSnapshot 作为 `dataSource` 来恢复数据

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: default-snapclass
driver: diskplugin.csi.alibabacloud.com
parameters:
  retentionDays: "5"
  forceDelete: "true"
deletionPolicy: Delete
```

这里有几个值得注意的细节：

- `retentionDays` 让快照可以自动过期回收，避免手动清理的遗漏。
- `forceDelete` 从 csi-provisioner v1.26.5 起默认开启且不可修改。这意味着删除 VolumeSnapshot 时，无论快照是否被其他资源引用过，都会被强制删除。这个默认值变化的历史细节说明阿里云在快照治理上越来越倾向于"清理优先"。
- `deletionPolicy` 和 PV 的 `reclaimPolicy` 语义一致：`Delete` 表示删 VolumeSnapshot 时同时删后端快照，`Retain` 则保留。

## 快照恢复：不只是 dataSource

恢复数据的关键是在 PVC 的 spec 里声明 `dataSource`：

```yaml
dataSource:
  name: new-snapshot-demo
  kind: VolumeSnapshot
  apiGroup: snapshot.storage.k8s.io
```

这个机制不只适用于 StatefulSet 的 `volumeClaimTemplates`，也适用于独立 PVC。如果你的 StorageClass 使用了 `WaitForFirstConsumer`，恢复出来的 PVC 在第一次被挂载前会保持 Pending，期间需要确保 VolumeSnapshot 和对应的 ECS 快照没有被删除。

文档还提到一个版本相关的细节：CSI 组件版本低于 v1.22.12 时，创建快照要求云盘必须处于挂载状态（有 Running Pod 使用 PVC）。新版本取消了这个限制，可以对任意挂载过的云盘创建快照。这个变化说明快照能力的实现正在从"运行时依赖"走向"存储层原生"。

## 静态快照导入：把已有的 ECS 快照接进 Kubernetes

除了动态创建，文档还讲了如何把已经在 ECS 控制台里创建好的快照导入到 ACK 集群里。这适用于运维团队已经在云厂商侧建立了快照策略的场景。

流程是反过来的：先手动创建 VolumeSnapshotContent（声明已有的 snapshot ID），再创建 VolumeSnapshot 去绑定它。关键点在于 `volumeSnapshotRef` 里的 name 和 namespace 必须和之后创建的 VolumeSnapshot 一致。

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotContent
metadata:
  name: new-snapshot-content-test
spec:
  deletionPolicy: Retain
  driver: diskplugin.csi.alibabacloud.com
  source:
    snapshotHandle: <YOUR-SNAPSHOTID>
  volumeSnapshotRef:
    name: new-snapshot-demo
    namespace: default
```

这个模式让我意识到：VolumeSnapshot API 的设计并没有假设所有快照都必须由 Kubernetes 创建。它和 PV 一样，允许外部创建的资源以声明式方式被纳入集群管理。

## 快照极速可用

对于 ESSD 云盘（PL0-PL3 和 AutoPL），动态创建的快照默认开启"快照极速可用能力"。这意味着恢复时不需要等待快照完全拷贝，可以显著缩短从备份到新 PVC 可用的时间。对于数据库等有 RTO 要求的业务，这个特性值得关注。

## 计费

快照会收取存储费用。文档特别提醒"开通快照不收费，创建快照后才开始收费"，这意味着你可以放心地在集群里启用快照功能，只需要为实际保留的快照数据量付费。

来源：[阿里云官方文档](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-volume-snapshots-created-from-disks)

相关页面：[[topics/kubernetes-persistent-storage]] · [[entities/kubernetes]] · [[sources/ack-static-disk-volume]] · [[sources/ack-dynamic-disk-volumes]]
