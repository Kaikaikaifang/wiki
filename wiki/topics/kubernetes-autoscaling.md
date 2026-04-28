---
title: Kubernetes 弹性伸缩
type: topic
tags: [Kubernetes, 弹性伸缩, 调度, 节点池]
source_count: 2
updated: 2026-04-28
---

> 我现在更愿意把 Kubernetes 弹性伸缩理解成一套分层控制系统，而不是一个“负载高了自动加资源”的按钮。真正重要的问题不是能不能自动伸缩，而是伸缩发生在哪一层、由什么信号触发、结果能不能被调度器真正落地。

## 先分清两层伸缩

读完 [[sources/kubernetes-autoscaling-workloads]] 和 [[sources/ack-node-scaling]] 后，我最想保留的判断是：**工作负载伸缩和节点伸缩不是同一件事。**

工作负载伸缩改变的是 Pod 或 replica：

- HPA 增减副本；
- VPA 调整 Pod 资源请求；
- KEDA 按事件、队列或时间计划触发扩缩；
- Cluster Proportional Autoscaler 按集群节点或 core 数调整系统组件副本。

节点伸缩改变的是集群容量：

- 当 Pod 因资源不足而不可调度时，节点伸缩组件模拟调度；
- 它判断哪些弹性节点池能满足 Pod 的资源、Label、Taint、affinity 等约束；
- 然后再驱动云厂商节点池扩容；
- 缩容时则要模拟驱逐和排水，检查 PDB、系统 Pod、DaemonSet 等边界。

这两层必须配合。HPA 能把副本数扩出来，但如果集群没有可用节点，结果就是更多 Pending Pod；节点 autoscaler 能补节点，但如果 workload 副本数没有变化，它也不会神奇地把单个高负载 Pod 的压力转移走。

## 传统利用率模型为什么不够

我过去很容易把弹性伸缩想成“CPU 到某个阈值就扩容”。ACK 文档很明确地拆掉了这个直觉。

在 Kubernetes 里，节点平均利用率不一定代表真实调度压力。热点节点可能被平均值掩盖；最高节点利用率又可能被某个局部热点放大。更关键的是，Pod 才是调度单元。一个 Pod 忙，不代表新节点能帮它分担，除非上层 workload 能扩出更多副本，或者资源 request / limit 被重新设计。

所以节点伸缩更合理的触发信号是 Pending / Unschedulable Pod，而不是单纯的节点 CPU 曲线。这个视角让我更容易理解为什么 cluster-autoscaler 的核心动作是模拟调度，而不是看监控图扩机器。

## 伸缩信号决定控制器

Kubernetes 官方文档把多种 autoscaling 方式放在一起，给我一个很实用的选择框架：先识别需求信号，再选工具。

- 如果压力能被更多副本分摊，用 HPA；
- 如果问题是 request / limit 不合理，用 VPA 或人工资源调整；
- 如果压力来自队列、消息、任务积压，用 KEDA；
- 如果系统组件规模应跟节点数或 core 数同步，用 Cluster Proportional Autoscaler；
- 如果 Pod 已经不可调度，用节点伸缩补容量；
- 如果低峰时段可以主动降容量，用计划式伸缩。

这比“我们要不要开 autoscaling”更具体。弹性能力本身没有答案，只有和业务信号匹配之后才有意义。

## 节点池设计就是弹性设计

[[sources/ack-node-scaling]] 让我更强烈地意识到，节点伸缩的成功率不是后端控制器单方面决定的。它取决于节点池设计给了系统多少选择空间。

如果 Pod 的 `nodeSelector`、affinity、toleration、topology spread 约束很窄，而弹性节点池又只配了少量实例规格和单可用区，那么模拟调度就很容易通过不了，或者通过了也会被云上库存卡住。相反，多可用区、多规格、合理 Label / Taint 边界，才是提高交付成功率的基础。

这里我会避免一个常见误会：弹性不是为了掩盖调度约束，而是要和调度约束一起设计。越是高优先级、强隔离、强拓扑要求的 workload，越需要提前证明对应节点池能被弹出来。

## 节点自动伸缩与即时弹性的取舍

ACK 把节点自动伸缩和节点即时弹性拆成两条路径，这对云上 Kubernetes 很有参考价值。

`cluster-autoscaler` 路径更经典：轮询集群状态，按调度失败和缩容条件维护节点数。它适合弹性诉求相对稳定、规模不太极端、团队想沿用标准语义的场景。

节点即时弹性更像是面向大规模和高频弹性的优化控制器：事件驱动，强调更快响应、更高资源交付确定性、库存和成本综合选择，以及更低碎片率。它适合节点池很多、连续扩容频繁、扩容速度和库存成功率很关键的场景。

但我不会把它抽象成“新方案替代旧方案”。即时弹性有自己的限制，例如不支持极速模式、单批扩容数量限制，以及部分抢占式库存检查限制。真正的选型应该看集群规模、弹性频率、业务对 Pending 时长的容忍度、节点池配置复杂度和运维团队是否需要更强的云厂商托管策略。

## 我会怎么检查一个生产弹性方案

如果要判断一套 Kubernetes 弹性伸缩设计是否靠谱，我现在会按这个顺序看：

1. workload 是否真的能通过副本数变化扩展吞吐；
2. resource requests 是否接近真实调度需求，而不是长期虚高或虚低；
3. HPA / VPA / KEDA 的触发信号是否对应真实业务压力；
4. Pending Pod 是否能被弹性节点池模拟调度成功；
5. 节点池是否覆盖足够多可用区和实例规格；
6. PDB、DaemonSet、系统 Pod 是否会阻止缩容；
7. 扩容后的节点是否能通过镜像拉取、初始化、CNI 和存储挂载这几段真实启动路径；
8. 缩容是否有足够的观察期和禁止缩容边界，避免把稳定性问题伪装成成本优化。

这份检查表的核心思想是：不要只证明“控制器会改数字”，要证明“改完数字以后，Pod 真的能调度、启动、服务流量，并且节点真的能安全退出”。

## 对我的提醒

Kubernetes 弹性伸缩最容易让人误判的地方，是它把多个控制循环叠在了一起：HPA 看指标调 replica，VPA 看资源建议调 request，KEDA 看事件源调副本，node autoscaler 看 Pending Pod 调节点，调度器再把 Pod 放到某个节点上。

每一层都看起来自动，但自动系统之间并不会天然互相理解。一个成熟的弹性方案，本质上是在这些控制循环之间建立清晰的因果关系：业务压力变成可观测信号，信号触发 workload 变化，workload 变化触发调度需求，调度需求触发节点容量变化，最后再通过服务指标验证真的缓解了压力。

---

来源：[[sources/kubernetes-autoscaling-workloads]] · [[sources/ack-node-scaling]]

相关页面：[[entities/kubernetes]] · [[topics/kubernetes-api-groups-and-schema-validation]] · [[topics/clickhouse-operator-installation-on-shared-clusters]] · [[sources/kubernetes-autoscaling-workloads]] · [[sources/ack-node-scaling]]
