---
title: Kubernetes
type: entity
tags: [Kubernetes, 容器编排, 云原生]
source_count: 2
updated: 2026-04-28
---

> 我越来越把 Kubernetes 看成一套“调度语义系统”，而不是一个单纯跑容器的平台。它真正难的地方，经常不是 YAML 能不能 apply，而是资源、调度、控制器和云基础设施之间的因果关系有没有被想清楚。

## 在这个 wiki 中的重要性

Kubernetes 目前在这份 wiki 里主要连接三条线。

第一条是 API 与资源定义。[[topics/kubernetes-api-groups-and-schema-validation]] 让我把 `apiVersion`、core API、GVK 和编辑器 schema 假阳性拆开看，提醒我不要为了让工具安静而篡改 Kubernetes API 身份。

第二条是平台组件安装。[[topics/clickhouse-operator-installation-on-shared-clusters]] 和 [[topics/kubernetes-crd-recording-strategy]] 讨论的是共享集群里的 Operator、CRD、Helm、watch 范围和生命周期边界。这里的关键不是“怎么装”，而是集群级控制器会改变整个平台对某类资源的理解方式。

第三条是弹性伸缩。[[sources/kubernetes-autoscaling-workloads]] 和 [[sources/ack-node-scaling]] 把 Kubernetes 的伸缩拆成 workload 层与 node 层：HPA、VPA、KEDA 改变 Pod 或副本，节点伸缩则为不可调度 Pod 补充容量。

## 我会保留的系统特征

- **资源身份由 GVK 决定**：`apiVersion` 和 `kind` 是协议身份，不是编辑器提示。
- **控制器是持续调和循环**：Operator、HPA、VPA、node autoscaler 都不是一次性脚本，而是长期改变系统状态的控制面。
- **调度是第一现场**：Label、Taint、affinity、PDB、resource requests 会决定 Pod 能不能落到节点上。
- **弹性是分层的**：工作负载伸缩和节点伸缩必须配合，单独打开某个控制器不能保证系统真的变得有弹性。
- **共享集群需要收窄边界**：CRD、Operator、watch namespace、证书和 RBAC 都应该被当成平台变更管理。

## 对我的提醒

Kubernetes 的抽象很强，但它不会替我消灭物理约束。Pod 需要资源，节点来自云厂商库存，镜像需要拉取，PDB 会阻止驱逐，CRD 会改变 API 面。越是依赖自动化控制器，越要把这些边界提前写清楚。

对我来说，Kubernetes 最值得学习的不是某个命令，而是这种工程直觉：声明式 API 只是入口，真正的系统行为发生在多个控制循环、调度约束和基础设施能力交汇的地方。

---

来源：[[sources/kubernetes-autoscaling-workloads]] · [[sources/ack-node-scaling]]

相关页面：[[topics/kubernetes-autoscaling]] · [[topics/kubernetes-api-groups-and-schema-validation]] · [[topics/kubernetes-crd-recording-strategy]] · [[topics/clickhouse-operator-installation-on-shared-clusters]] · [[sources/kubernetes-autoscaling-workloads]] · [[sources/ack-node-scaling]]
