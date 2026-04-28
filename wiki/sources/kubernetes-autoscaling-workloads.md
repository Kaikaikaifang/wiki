---
title: Kubernetes 工作负载弹性伸缩
type: source
tags: [Kubernetes, 弹性伸缩, HPA, VPA, KEDA]
source_count: 1
source_file: raw/articles/kubernetes-autoscaling-workloads.md
author: Kubernetes
published: 2025-11-23
updated: 2026-04-28
---

来源：[[entities/kubernetes]] · [原文](https://kubernetes.io/docs/concepts/workloads/autoscaling/)

## 核心结论

这篇 Kubernetes 官方文档最有价值的地方，是把 autoscaling 先限定在“工作负载对象如何变化”这个层面，而不是一上来就谈云厂商怎么扩机器。

我会把它理解成一张概念地图：当需求变化时，Kubernetes 可以横向增加副本，也可以纵向调整 Pod 资源；可以人工做，也可以由控制器自动做；还可以根据集群规模、事件队列或时间计划触发。只有当这些还不够时，才进入节点层面的基础设施伸缩。

## 两种基本方向

工作负载伸缩的第一条分叉，是横向和纵向。

**横向伸缩**改变的是副本数量。典型机制是 `HorizontalPodAutoscaler`，它作为 Kubernetes API resource 和 controller，周期性观察 CPU、内存等指标，然后调整 Deployment 等 workload 的 replica 数。

**纵向伸缩**改变的是单个副本可用资源。典型机制是 `VerticalPodAutoscaler`。它不属于 Kubernetes 默认内置能力，需要集群管理员额外安装，并依赖 Metrics Server 等指标基础设施。

这个区分很重要。横向伸缩解决的是“多跑几个副本能不能分摊压力”，纵向伸缩解决的是“当前副本是不是 request / limit 设错了”。如果应用本身不能水平分摊，把 HPA 打开也只是制造更多相似的瓶颈。

## 不只有 HPA

文档还提醒我，Kubernetes 里的 autoscaling 不等于 HPA。

- `Cluster Proportional Autoscaler` 可以按可调度节点数和 core 数调整系统组件副本，例如 DNS；
- `Cluster Proportional Vertical Autoscaler` 可以按集群规模调整 workload 的 resource requests；
- `KEDA` 可以按事件源伸缩，例如消息队列长度；
- KEDA 的 `Cron` scaler 可以按时间计划伸缩，在低峰期减少资源。

我觉得这里真正有用的不是记住每个项目名，而是看到触发信号的差异：资源利用率、集群规模、事件积压、时间计划，其实分别对应不同的系统问题。一个好的伸缩方案应该先问“需求信号是什么”，再选控制器。

## 节点伸缩是下一层

文档最后把 cluster infrastructure scaling 单独放出来：如果工作负载伸缩仍然不能满足需求，就需要增加或移除节点。

这句话看似简单，但它帮我划清了边界：工作负载伸缩改变 Pod 或 replica，节点伸缩改变集群容量。前者是调度对象的变化，后者是可调度资源池的变化。两者经常配合，但不是同一件事。

## 对我的启发

我以后看 Kubernetes 弹性伸缩，会先分三层：

1. 业务是否能靠更多副本分摊压力；
2. 单个 Pod 的资源 request / limit 是否合理；
3. 集群是否有足够节点容量承载这些 Pod。

如果这三层没分清，很容易把问题错配。比如 Pod 因为 request 太大而调度失败，节点 autoscaler 也许会扩机器，但根因可能是资源声明失真；反过来，如果确实有大量 Pending Pod，光调 HPA 参数也不可能凭空变出节点容量。

---

相关页面：[[topics/kubernetes-autoscaling]] · [[sources/ack-node-scaling]] · [[entities/kubernetes]]
