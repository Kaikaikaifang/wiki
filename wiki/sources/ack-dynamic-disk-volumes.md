---
title: ACK 动态云盘存储卷使用指南
type: source
tags: [Kubernetes, 持久化存储, 阿里云, CSI, StorageClass]
source_count: 0
updated: 2026-05-26
---

如果说静态卷是"先有车再上牌"，动态卷就是"按需造车"。这篇文章讲的是 ACK 里如何通过 StorageClass 让 CSI 自动创建云盘、自动绑定、自动挂载，整个过程对应用开发者几乎透明。

## StorageClass 才是真正的决策点

很多人把注意力放在 StatefulSet 的 `volumeClaimTemplates` 上，但**真正的选型发生在 StorageClass**。它决定了：创建什么类型的云盘、用哪种绑定策略、删 PVC 时是否同时删盘、支不支持在线扩容。

文档里最推荐的默认 StorageClass 是 `alicloud-disk-topology-alltype`，它的关键参数是 `volumeBindingMode: WaitForFirstConsumer`。这意味着 PVC 不会立刻创建云盘，而是等 Pod 被调度到具体节点后，再根据节点所在可用区的库存情况决定创建哪种云盘。这个延迟绑定策略解决了多可用区场景下"PVC 创建在 A 区、Pod 调度到 B 区"的经典冲突。

但如果你的 Pod 会被调度到虚拟节点（ECI/ACS），就要小心了——虚拟节点的部分调度机制不遵循 `WaitForFirstConsumer` 的流程，CSI 无法获取可用区信息，PVC 会一直 Pending。文档特别给出了这一场景的排查清单（Label、Annotation、nodeName 前缀），这是踩过坑才会写进去的。

## 参数里的隐藏选项

StorageClass 的 `parameters` 里藏了不少值得关注的配置：

- `type`：不只是选 ESSD 还是 SSD，还可以按优先级写一串候选类型，比如 `cloud_auto,cloud_essd,cloud_ssd`，系统会按顺序尝试创建。这比"指定一种类型然后因为库存不足失败"要灵活得多。
- `performanceLevel`：ESSD 云盘的 PL 级别直接影响 IOPS 和吞吐，云盒场景下还需要显式指定 `PL0`。
- `encrypted`：数据敏感型应用可以直接在 StorageClass 里开启云盘加密，不需要应用层改动。
- `allowVolumeExpansion: true`：为未来扩容留门。如果初期没开，后期想在线扩容就得重建 StorageClass 或走手动流程。

## StatefulSet + volumeClaimTemplates 的标准模式

动态卷最常见的用法是在 StatefulSet 里为每个 Pod 分配独立的云盘：

```yaml
volumeClaimTemplates:
- metadata:
    name: pvc-disk
  spec:
    accessModes: [ "ReadWriteOnce" ]
    storageClassName: "alicloud-disk-wait-for-first-consumer"
    resources:
      requests:
        storage: 20Gi
```

这里容易踩的坑是：StorageClass 和 StatefulSet 可能在不同团队手里维护。如果 StorageClass 的 `reclaimPolicy` 设为 `Delete`，删除 StatefulSet 时云盘也会被自动删除。对于数据库这种核心业务，建议用 `Retain` 并在应用层做好备份策略。

## 单 Pod Deployment 的特殊路径

文档还提供了一个不太常见但实用的场景：如何在单副本 Deployment 里挂载动态云盘。这适用于"不需要稳定网络标识、也不需要多副本伸缩"的简单应用。流程是：手动创建 PVC（引用 StorageClass）→ 在 Deployment 的 `volumes` 里引用这个 PVC。

这里的关键约束是副本数必须设为 1。如果后续试图扩容到 2，第二个 Pod 会因为无法挂载已被占用的云盘而永远 Pending。这不是 bug，而是 RWO 访问模式的正确行为。

## 性能优化与成本

- **并行挂载**：默认情况下，单个节点的云盘操作是串行的。如果 Pod 需要挂载多块云盘（比如主数据 + 日志 + 备份），串行挂载会显著拉长启动时间。可以开启并行挂载加速。
- **监控与告警**：文档推荐阅读容器存储监控，及时发现存储卷异常或性能瓶颈。这一点在生产环境里经常被忽略——很多人只监控 Pod CPU/内存，不监控挂载卷的延迟和 IOPS。

## 计费与清理

动态创建的云盘默认按量付费。释放资源时要注意 StorageClass 的 `reclaimPolicy`：`Delete` 会连带删除云盘（数据不可恢复），`Retain` 会保留云盘但需要手动清理 Released 状态的 PV 和实际云盘。

来源：[阿里云官方文档](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-dynamically-provisioned-disk-volumes)

相关页面：[[topics/kubernetes-persistent-storage]] · [[entities/kubernetes]] · [[sources/ack-static-disk-volume]] · [[sources/ack-disk-volume-snapshots]]
