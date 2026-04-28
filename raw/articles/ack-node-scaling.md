---
title: "节点伸缩"
source: "https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/overview-of-node-scaling/?spm=5176.28197681.console-base_help.dexternal.75325ff6TpHpzG"
author:
published:
created: 2026-04-28
description: "当集群的容量规划无法满足应用Pod调度时，可使用节点伸缩功能，自动扩缩节点资源以进行调度容量的补充。ACK提供节点自动伸缩与节点即时弹性两种弹性方案，后者相较于前者有着更快的弹性速度、更高的交付效率和更低的使用门槛。"
tags:
  - "clippings"
---
当集群的容量规划无法满足应用Pod调度时，可使用节点伸缩功能，自动扩缩节点资源以进行调度容量的补充。ACK提供节点自动伸缩与节点即时弹性两种弹性方案，后者相较于前者有着更快的弹性速度、更高的交付效率和更低的使用门槛。

## 阅读前提示

为了让您更好地了解ACK提供的节点伸缩方案，并结合您的业务诉求进行方案选型，建议您在启用节点伸缩能力前阅读本篇概述。

阅读本文前，推荐您参见 [Kubernetes官方文档](https://kubernetes.io/docs/concepts/workloads/autoscaling/) 了解手动伸缩、自动伸缩、水平伸缩、垂直伸缩等伸缩概念。

## 工作原理

在Kubernetes中，节点伸缩的工作原理与传统意义上基于使用率阈值的模型有所差别。这也是从传统IDC或其他编排系统迁移到Kubernetes集群后往往需要解决的问题。

传统的弹性伸缩模型基于使用率实现。例如，一个集群中有3个节点，当集群中的节点CPU、内存使用率超过特定的阈值时，系统将扩容新的节点。但这种模式存在以下问题。

**阈值是如何选择与判断的？**

在一个集群中，部分热点节点的利用率可能较高，而其他节点的利用率可能较低。

- 如果根据整个集群的平均资源利用率来决定是否弹性伸缩，使得热点节点的差异被平均，那么会造成对热点节点的扩缩不够及时。
- 如果依据最高的节点利用率来决定是否弹性伸缩，那么会造成弹出资源的浪费，影响集群的整体服务。

**弹出实例后如何缓解压力？**

在Kubernetes集群中，应用以Pod为最小单元部署在集群的不同节点上。当一个Pod资源利用率较高时，即使该Pod所在的节点或者集群触发了弹性扩容，但该应用的Pod数量以及Pod对应的Limit并没有发生变化，节点负载的压力也无法转移到新扩容的节点上。

**如何判断以及执行实例的缩容？**

如果基于资源利用率的方式判断节点是否缩容，那么很有可能出现Request（资源请求）较大、但Usage（实际资源使用）很小的Pod被驱逐。当集群中这种类型的Pod较多时，会占用集群大量的调度资源，导致部分Pod无法调度。

基于以上问题，ACK通过节点伸缩（资源层）和工作负载伸缩（调度层）两层弹性模型来解决。节点伸缩功能基于资源的使用率来触发应用副本的变化，也就是调度单元的变化。以下介绍技术细节。

**如何判断节点的弹出？**

节点伸缩会监听Pod是否处于调度失败的状态，以判断是否需要触发扩容。当Pod由于调度资源不足而调度失败时，节点伸缩会开始模拟调度，计算在开启弹性的节点池中哪个节点池可为这些Pod提供所需的节点资源，并在满足需求时弹出相应的节点。

**说明**

模拟调度时将一个开启弹性的节点池作为一个的抽象节点，开启弹性的节点池中配置的机型规格会成为抽象节点的CPU、内存或GPU的容量，且其配置的Label、Taint也会成为抽象节点的Label与Taint。模拟调度器会在调度模拟时，将该抽象节点纳入调度参考范围。符合调度条件时，调度模拟器会计算所需的节点数目，驱动节点池弹出节点。

**如何判断节点的缩容？**

节点伸缩仅缩容开启了弹性的节点池中的节点，无法管理静态节点（不在开启了弹性的节点池中的其他节点）。每个节点会单独判断是否进行缩容。当任意一个节点的调度利用率低于所设置的调度阈值时，就会触发缩容判断。此时，节点伸缩会尝试模拟驱逐节点上的负载，判断当前节点是否可以排水。部分特殊的Pod（例如kube-system命名空间的非DaemonSet Pod、PDB控制的Pod等）则会跳过该节点而选择其他的候选节点。当节点发生驱逐时，会先进行排水，将节点上的Pod驱逐到其他的节点，然后再下线该节点。

**多个开启弹性的节点池之间如何选择？**

不同开启弹性的节点池之间，实际上相当于不同的抽象节点之间的选择。和调度策略一样，开启弹性的节点池之间也存在打分机制。弹性组件首先筛选符合调度策略的节点，然后进一步根据 `affinity` 等亲和性策略进行选择。

如果基于上述策略无法选择合适的节点，默认情况下节点自动伸缩会通过least-waste的策略进行选择。least-waste策略的核心是模拟弹出节点后，找到剩余资源最少的节点。

**说明**

当有一个开启弹性的GPU节点池和开启弹性的CPU节点池同时可以弹出生效时，默认CPU会优先于GPU弹出。

而默认情况下，节点即时弹性会综合评估库存可用性与成本，在多个可行的扩容方案中优先选择库存充足且成本较低的实例规格。

**如何提高弹性伸缩的成功率？**

弹性伸缩的成功率主要取决于以下两个因素：

- 调度策略是否满足
	配置开启弹性的节点池后，您需要先确认该节点池可以承载的Pod的调度策略范围。如果无法直接判断，您可以通过 `nodeSelector` 直接选择节点池的Label，来进行预弹模拟。
- 资源配置是否充分
	当模拟调度通过后，系统会选择开启弹性的节点池，以弹出实例。但开启弹性的节点池中配置的ECS规格库存会直接影响是否可以成功弹出实例。因此，推荐您配置多个可用区、多个不同机型组合，以提高弹出成功率。

**如何提高弹性伸缩的速度？**

- 方法一：使用极速模式加速弹出速度。当开启弹性的节点池预热后（已完成一次扩容和一次缩容），节点池即可进入极速伸缩模式。更多信息，请参见 [启用节点自动伸缩](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/auto-scaling-of-nodes) 。
- 方法二：使用自定义镜像的方式，以Alibaba Cloud Linux 3作为基础镜像，大大提升IaaS层的资源交付速度（50%）。更多信息，请参见 [弹性优化之自定义镜像](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/create-custom-images) 。

## 弹性方案：节点自动伸缩与节点即时弹性

节点伸缩属于资源层弹性能力，用于在集群容量无法满足应用Pod调度时，自动扩缩节点资源，以进行调度容量的补充。ACK在节点伸缩层面提供两种弹性方案。

### 方案介绍

**重要**

- 一个集群中只支持运行一个弹性组件，两种弹性方案不支持混用。请参见 [启用节点自动伸缩](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/auto-scaling-of-nodes) 或 [启用节点即时弹性](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/instant-elasticity) 按照标准流程启用节点伸缩功能。
- 本文中提供的弹性测量数据为理论值，均基于弹性优化的自定义镜像实现，实际数据以您的实际业务环境为准。关于自定义镜像的更多信息，请参见 [弹性优化之自定义镜像](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/create-custom-images) 。

<table><tbody><tr><td rowspan="1" colspan="1"><p><b>方案</b></p></td><td rowspan="1" colspan="1"><p><b>弹性组件</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td></tr><tr><td rowspan="1" colspan="1"><p>方案一：节点自动伸缩</p></td><td rowspan="1" colspan="1"><p>cluster-autoscaler组件</p></td><td rowspan="1" colspan="1"><p>以轮询的方式，周期性地维护和检查集群状态，以发现满足扩缩容条件的情况，从而自动扩缩容集群节点。</p></td></tr><tr><td rowspan="1" colspan="1"><p>方案二：节点即时弹性</p></td><td rowspan="1" colspan="1"><p>节点即时弹性组件</p></td><td rowspan="1" colspan="1"><p>一个基于事件驱动的节点伸缩控制器。在大规模集群（例如弹性节点池中节点数大于100，或弹性节点池数大于20）和连续多次弹性扩容等场景下，能够保证更好的弹性资源交付。伸缩速度（即从Pod首次调度失败到Pod调度成功的耗时）稳定在45s、成功率可达99%、资源碎片度降低约30%。同时，在扩缩容自定义策略上有更好的扩展性。</p></td></tr></tbody></table>

### 方案对比

如果您的集群节点池已开启自动弹性伸缩且节点池的 **伸缩模式** 为 **非极速模式** ，节点即时弹性可兼容原弹性节点池的语义与行为，并支持所有类型的应用无感开启与使用。所以，本小节重点阐述节点即时弹性相较于节点自动伸缩的优化特性。

<table><tbody><tr><td rowspan="1" colspan="1"><p><b>优化特性</b></p></td><td rowspan="1" colspan="1"><p>节点自动伸缩</p></td><td rowspan="1" colspan="1"><p>节点即时弹性</p></td></tr><tr><td rowspan="3" colspan="1"><p>伸缩速度与效率</p></td><td rowspan="1" colspan="1"><p>单次伸缩时，标准模式的伸缩速度约为60s，极速模式为50s。</p></td><td rowspan="1" colspan="1"><p>通过事件驱动的机制来触发扩缩行为，结合阿里云的ContainerOS能力进行弹性加速，伸缩速度大约为45±10s。</p></td></tr><tr><td rowspan="1" colspan="1"><p>当达到1分钟的伸缩量级时，伸缩速度会遇到瓶颈，并且在不同规模（多节点池）、不同场景（连续伸缩）下，弹性速度也会有比较明显的抖动。例如，当节点池数量超过100时，伸缩速度将衰减为100～150s。</p></td><td rowspan="1" colspan="1"><p>不会随着节点池的规模与Pod的规模的增大而产生明显的衰减，更适用于对弹性交付速度要求高的场景。</p></td></tr><tr><td rowspan="1" colspan="1"><p>使用轮询式模型，且受制于对集群状态维护的依赖，弹性灵敏度最低为5s。</p></td><td rowspan="1" colspan="1"><p>基于事件驱动，使用响应式模型，弹性灵敏度为1～3s。</p></td></tr><tr><td rowspan="3" colspan="1"><p>资源交付确定性</p></td><td rowspan="1" colspan="1"><p>云上资源的库存变化较为频繁。由于实例规格组合问题、库存不足等原因，节点自动伸缩的弹性成功率在97%左右。</p></td><td rowspan="1" colspan="1"><p>支持库存自动选择策略，可根据您配置的筛选条件与顺序，从阿里云上千个实例规格组合中过滤无库存的实例规格，并选择最合适的规格进行扩容，或在库存不足时补偿符合条件的规格。这大大降低了运维人员选择规格的压力，同时提升了交付的成功率，可达99%。</p></td></tr><tr><td rowspan="1" colspan="1"><p>支持按照节点池配置的规格扩容相同类型的规格。在类型不同时，会选择最小的规格进行扩容。</p></td><td rowspan="1" colspan="1"><p>支持扩容不同类型的规格。</p></td></tr><tr><td rowspan="1" colspan="1"><p>资源交付失败时，会进行周期性重试，手段较为滞后。</p></td><td rowspan="1" colspan="1"><p>资源交付失败时，支持库存预警能力，提前通知规格组合的潜在风险。</p></td></tr><tr><td rowspan="1" colspan="1"><p>使用及运维门槛</p></td><td rowspan="1" colspan="2"><p>相较于节点自动伸缩，节点即时弹性的使用门槛更低。主要体现在以下方面。</p><ul><li><p>节点池配置维护：节点即时弹性能够根据实例属性在多规格和多可用区中自动选择实例，容纳等待调度的Pod。但在节点自动伸缩模式下，您需要自行维护节点池各项配置，以保证Pod的正常调度。因此，当Pods配置发生变更时，往往意味着对应节点池配置也需要更新。</p></li><li><p>节点运维：对于开发者来说，在扩缩容过程中，相关异常都可以通过Pod事件同步，他们只需管理Pod的生命周期。</p></li><li><p>功能拓展：支持扩展机制，例如结合 <a href="https://github.com/kubernetes-sigs/descheduler">Descheduler</a> 准备弹性资源。节点即时弹性支持无侵入式地将资源供给策略、节点生命周期管理与您的自定义行为进行联动，提供更多二次开发的可能性。</p></li></ul></td></tr><tr><td rowspan="2" colspan="1"><p>调度策略</p></td><td rowspan="1" colspan="2"><p>除支持节点自动伸缩所有的调度特性之外，节点即时弹性还支持以下特性：</p><ul><li><p><a href="https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/">Topology</a> ：常用于满足跨可用区维度的高可用需求。</p></li><li><p><a href="https://kubernetes.io/docs/concepts/workloads/pods/disruptions/#/pod-disruption-budgets">Pod Disruption Budgets</a> ：可限制在同一时间可被主动驱逐的多副本应用中Pod的数量，以保障变更期间的稳定性。</p></li></ul></td></tr><tr><td rowspan="1" colspan="2"><p>节点即时弹性支持根据Pod选择最优 <a href="https://kubernetes.io/docs/concepts/scheduling-eviction/resource-bin-packing/">装箱策略（Bin Packing）</a> 和 <a href="https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/#pre-bind">预绑定（PreBind）</a> 策略（自定义特性），将调度碎片率优化30%。</p></td></tr></tbody></table>

### 节点即时弹性的使用限制

在评估节点即时弹性方案时，您需要同时了解节点即时弹性的使用限制。

- 不支持极速模式
- 一个节点池单批扩容节点的个数不可超过180个
- 目前不支持在集群维度配置禁止缩容。
	**说明**
	如需在节点维度实现禁止缩容，请参见 [如何指定节点不被节点即时弹性缩容？](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#title-i8u-c40-ffz) 。
- 节点即时弹性暂不支持对抢占式实例库存的检查。对于 **付费类型** 为抢占式实例且开启了 **使用按量实例补充抢占式容量** 的节点池，可能会出现抢占式库存充足时仍然扩容按量实例的情况。

## 方案选型建议

参见前文的与，如业务对弹性速度、资源交付确定性和使用及运维成本要求相对较低，且无法接受节点即时弹性的使用限制时，节点自动伸缩可能能够满足业务需求。反之，如果有以下业务诉求，更推荐使用节点即时弹性。

- 集群规模较大，例如弹性节点池中节点数大于100，或弹性节点池数大于20时，随着集群规模变大，节点自动伸缩的扩容效率会明显衰减，而节点即时弹性的性能波动较小。
- 对资源交付速度，即弹性速度，有更高要求。单次伸缩场景下，标准模式下的节点自动伸缩的弹性速度为60s左右，而节点即时弹性为45s左右。
- 业务负载批次不可控，对同一个弹性节点池通常有连续扩容的需求。连续伸缩模式下，节点自动伸缩的性能会衰减且抖动较为明显，而节点即时弹性仍然能实现45s左右的伸缩速度。

## 注意事项

#### 配额与限制

- 在专有网络下创建的单个路由表可创建的自定义路由数限额是200条。如需更大的配额，请前往 [配额中心](https://quotas.console.aliyun.com/products/vpc/quotas?query=route) 提交申请。关于其他资源的配额限制及升配详情，请参见 [依赖底层云产品配额限制](https://help.aliyun.com/zh/ack/product-overview/limits#section-9sf-skx-0fx) 。
- 请合理配置开启自动伸缩的节点池的最大实例数，保证此范围内的节点所依赖的资源和配额充足，例如合理规划VPC网段、交换机等网络资源，以避免节点扩容失败。配置开启自动伸缩的节点池的最大实例数，请参见 [配置实例数量](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/auto-scaling-of-nodes#step-5pj-lz8-cgl) 。关于ACK的网络规划，请参见 [ACK托管集群网络规划](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/kubernetes-cluster-network-planning) 。
- 节点伸缩功能不支持包年包月付费类型的节点。如需新建开启自动伸缩的节点池，请勿选择付费类型为包年包月。如需为已有节点池开启自动伸缩，请确保节点池内没有包年包月付费类型的节点。
- 节点伸缩功能暂不支持 [SideCar Containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/) 。请将使用了SideCar Containers的工作负载部署至未开启自动伸缩的节点池上。

#### 依赖资源的维护

选择绑定EIP时，请勿通过ECS控制台直接删除节点伸缩扩容出的ECS节点，否则会导致EIP无法自动释放。

## 后续阅读

- 根据前文的方案介绍和差异对比，您可以选择 [启用节点自动伸缩](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/auto-scaling-of-nodes) 、 [启用节点即时弹性](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/instant-elasticity) 。
- 如在使用节点伸缩过程中遇到问题，您可参见 [节点自动伸缩FAQ](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling) 进行自排查。
	**展开查看** 节点自动伸缩 **的FAQ索引**
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>分类</b></p></td><td rowspan="1" colspan="1"><p><b>二级分类</b></p></td><td rowspan="1" colspan="1"><p><b>跳转链接</b></p></td></tr><tr><td rowspan="4" colspan="1"><p>节点自动伸缩的扩缩容行为</p></td><td rowspan="1" colspan="2"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#0578d5906a4ve">已知限制</a></p></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#3d73c9bce2x1y">扩容行为相关</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#5e458ca0fdeyz">cluster-autoscaler组件使用哪些调度策略来判断不可调度Pod能否调度到开启了弹性的节点池？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#9081e1305c7f2">cluster-autoscaler组件可模拟判断的资源有哪些？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#4bd69dc0fda87">为什么节点自动伸缩组件无法弹出节点？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#29a70230fdx9t">如果一个伸缩组内配置了多资源类型的实例规格，弹性伸缩时如何计算这个伸缩组的资源呢？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#5679b320fde95">弹性伸缩时，如何在多个开启弹性的节点池之间进行选择？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#fff85a7068y34">开启弹性的节点池如何配置自定义资源？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#b348c46bdcxb1">为什么为节点池设置自动扩缩容失败？</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#d965c40777nu9">缩容行为相关</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#51d75430fdnp3">为什么cluster-autoscaler组件无法缩容节点？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#section-kg5-cli-y3i">如何启用或禁用特定DaemonSet的驱逐？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#4000d01068gao">什么类型的Pod可以阻止cluster-autoscaler组件移除节点？</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#4d35a60fc8vqv">拓展支持相关</a></p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#b5fff6905c7fv">cluster-autoscaler组件是否支持CRD？</a></p></td></tr><tr><td rowspan="2" colspan="1"><p>自定义的扩缩容行为</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#c3186b2465my5">通过Pod控制扩缩容行为</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#c7d74de068d5w">如何延迟cluster-autoscaler组件对不可调度Pod的扩容反应时间？</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#9008f67409m0b">通过节点控制扩缩容行为</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#9197847068xlh">如何指定节点不被cluster-autoscaler组件缩容？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#section-mwn-b6z-apt">如何通过Pod Annotation影响cluster-autoscaler组件的节点缩容？</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="2"><p>cluster-autoscaler组件相关</p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#bb7882f068f94">如何升级cluster-autoscaler组件至最新版本？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#60a012b0effpp">哪些操作会触发cluster-autoscaler组件自动更新？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-auto-scaling#cfae8542e6jyf">ACK托管集群已经完成了角色授权，但节点伸缩活动仍然无法正常运行？</a></p></li></ul></td></tr></tbody></table>
	**展开查看** 节点即时弹性 **的FAQ索引**
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>分类</b></p></td><td rowspan="1" colspan="1"><p><b>二级分类</b></p></td><td rowspan="1" colspan="1"><p><b>跳转链接</b></p></td></tr><tr><td rowspan="3" colspan="1"><p>节点即时弹性的扩缩容行为</p></td><td rowspan="1" colspan="2"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#dbbc106bc8vq9">已知限制</a></p></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#8cdf6cea0camp">扩容行为相关</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#9c9ecbb2acns7">节点即时弹性可模拟判断的资源类型有哪些？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#4137b11f51wpg">节点即时弹性是否支持根据Pod Request资源在节点池中扩容合适资源的实例规格？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#b075558334gwl">节点池配了多个实例规格，节点即时弹性默认如何选择？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#4331ccfc84sau">使用节点即时弹性时，如何实时感知节点池中的实例规格库存变化？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#137ca271cat5s">如何优化节点池配置，尽量避免库存不足而导致扩容失败？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#b273b386cdm60">为什么节点即时弹性无法弹出节点？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#VvAtw">开启节点即时弹性的节点池如何配置自定义资源？</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#3b166483bd2uz">缩容行为相关</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#b30d4d1e9d3o6">为什么节点即时弹性无法缩容节点？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#ed53341b2943s">什么类型的Pod可以阻止节点即时弹性移除节点？</a></p></li></ul></td></tr><tr><td rowspan="2" colspan="1"><p>自定义的扩缩容行为</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#cbf256126a6as">通过Pod控制扩缩容行为</a></p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#e47756a141fsu">如何通过Pod控制节点即时弹性的节点缩容？</a></p></td></tr><tr><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#c963086718o0w">通过节点控制扩缩容行为</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#7f37a07acft6o">节点即时弹性在缩容过程中如何指定需要删除的节点？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#ed6ea25edd6ik">如何指定节点不被节点即时弹性缩容？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#c34be0edbad6p">节点即时弹性能否仅缩容空节点？</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="2"><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#af50f8b5d0lih">节点即时弹性组件相关</a></p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#ea3469c40bxi6">是否有操作会触发节点即时弹性组件的自动更新？</a></p></li><li><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-node-instant-scaling#6da5a6c089zxs">ACK托管集群已经完成了角色授权，但节点伸缩活动仍然无法正常运行？</a></p></li></ul></td></tr></tbody></table>