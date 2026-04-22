---
title: 共享集群里的 ClickHouse Operator 安装
type: topic
tags: [Kubernetes, ClickHouse, Operator, Helm, 集群运维]
source_count: 0
updated: 2026-04-22
---

> 我现在越来越警惕一种“先把东西装上再说”的冲动。尤其是在共享 Kubernetes 集群里，Operator 这类集群级组件一旦安装，影响的就不再是某个 namespace，而是整个 API 面和控制面行为。也正因为如此，安装方式本身就应该被当成设计决策，而不是执行细节。

这次我面对的场景很典型：源 ClickHouse 还在 `development` 命名空间里，而目标集群准备放到 `tenant-kaikai`，目的是避免把新旧两套资源混在同一个 namespace 里。问题随之而来：当前集群里其实并没有 `clickhouse.com` 这套 CRD，也就是说，`ClickHouseCluster` 和 `KeeperCluster` 根本还不存在。

这一步真正要决定的，不是“怎么写目标集群 YAML”，而是**怎么把 Operator 安装成一条对共享集群足够克制的路径**。

## 先说结论

如果是在共享集群里安装官方 ClickHouse Operator，我更推荐：

- 用 `Helm`
- 安装到独立 namespace，例如 `clickhouse-operator-system`
- 显式 pin chart 版本
- 如果集群里已经有 `cert-manager`，就关闭 chart 里的 `certManager.install`
- 用 `watchNamespaces` 把 operator 的观察范围收窄到目标 namespace，比如 `tenant-kaikai`

我不会优先推荐直接 `kubectl apply` 官方 bundle。不是因为它不能用，而是因为它更像一条“快速铺开”的路径，而不是一条“适合后续维护、升级、回滚和审计”的路径。

## 为什么 Helm 更适合共享集群

我对 Helm 的偏好，不是出于工具信仰，而是出于运维边界。

在共享集群里，Operator 这类组件有几个特点：

- 它们通常带 CRD；
- 它们可能还带 webhook、证书、RBAC；
- 它们不是一次性资源，而是长期存在的控制器；
- 它们以后很可能要升级。

这时候 Helm 的优势就很现实：

- 有 release 概念，能清楚知道“谁装了什么”；
- 升级有 `helm upgrade`；
- 卸载有 `helm uninstall`；
- 更容易通过 values 把安装范围收窄，而不是直接吃一整份通用 YAML。

相反，`kubectl apply -f` 更适合一次性演示或非常轻量的试验。真到了共享集群，我更在意的是“后面怎么管”，而不只是“现在怎么装上去”。

## 我会怎么控制影响范围

这次最重要的策略，其实不是 Helm 本身，而是**别让 Operator 观测整个集群**。

既然这轮迁移的目标 namespace 已经明确是 `tenant-kaikai`，那我会把 operator 的 watch 范围直接收窄到这个 namespace。这样做的好处很直接：

- 避免它去处理其他 tenant 的对象；
- 避免让集群里所有 namespace 都暴露在这套新控制器的观察范围里；
- 让这次安装更像一次“围绕迁移任务的最小增量”，而不是一次全局性平台改造。

我很喜欢这种做法，因为它符合我对共享集群的基本态度：**默认收窄，而不是默认放开。**

## `cert-manager` 为什么要单独判断

官方 chart 支持和 `cert-manager` 集成，这本身没问题。但问题在于，共享集群里往往已经有一套统一的 `cert-manager` 在运行了。这个时候如果 chart 再顺手装一份，就会让控制面变得很混乱。

所以我的默认策略是：

- 如果集群里已经有 `cert-manager`，就设置 `certManager.install=false`
- 保留 `certManager.enable=true`，让 operator 继续使用现有集群能力

这类判断很像我在数据库迁移里常说的那句话：**不要把“组件接入”和“基础设施重建”绑成同一个动作。**

## `crd.keep=true` 为什么值得打开

我对 `crd.keep=true` 的态度也比较明确。在共享集群里，这个设置通常更稳。

原因不是“CRD 永远不该删”，而是：

- Helm release 可以被卸载；
- 但 CRD 是集群级对象；
- 一旦 CRD 被自动删除，影响的可能不只是你当前这个 namespace，而是所有依赖这套 CRD 的对象定义。

所以如果你还在探索阶段，或者后面可能会反复调整 release，我更愿意先把 CRD 保留住，把“删 CRD”变成一个显式、审慎、单独执行的动作。

## 这类安装配置应该怎么沉淀

这次我后来又往前多想了一步：像 ClickHouse Operator 这种带 CRD 的控制器，真正值得长期保留到仓库里的，通常不是整份上游 CRD YAML，而是下面三类信息：

- Helm chart 来源与版本；
- values 文件；
- CRD 生命周期策略，比如 `crd.enable=true`、`crd.keep=true`、`watchNamespaces=tenant-kaikai`。

我现在更倾向把这三类东西看成“安装配置”，而把上游 CRD 原文看成“发行物内容”。两者不是一回事。前者是我以后要反复判断、升级、审计和复用的；后者如果没有离线安装或强审计要求，直接 vendoring 进仓库的收益并不高，反而容易在 chart 升级后制造漂移。

这也是为什么我觉得它和 `cert-manager` 很像，但又不能简单照抄。`cert-manager` 目录真正被长期维护的，往往是 `values.yaml`、issuer、webhook 和 DNS provider 配置，而不是 CRD 原文本身。ClickHouse Operator 更适合沿用同样的思路：**记录入口、记录边界、记录生命周期，不默认复制上游生成物。**

## 一个更稳的安装姿势

如果让我把这次场景浓缩成一条更稳的安装思路，它应该长这样：

1. 切到目标集群 context；
2. 确认 `cert-manager` 已存在；
3. 确认 `clickhouse.com` 这套 CRD 还没装；
4. 在独立 namespace 里用 Helm 安装 operator；
5. 限制 operator 只 watch `tenant-kaikai`；
6. 验证 `ClickHouseCluster` 与 `KeeperCluster` 的 API 资源已经出现；
7. 再开始创建目标 ClickHouse 集群。

我觉得这套顺序很重要，因为它把“安装 operator”从一个模糊的准备动作，提升成了一个**有前提、有边界、有验证出口**的集群变更。

## 从安装走到真正可用，还差什么

这次真正把目标集群在 `tenant-kaikai` 里拉起来后，我更明显地感受到：Operator 安装完成，其实只意味着“控制面准备好了”，离“迁移目标端真的能用”还差一段不短的路。

我最终补齐的几件事是：

- 把目标镜像从 `docker.io` 改到公开 ACR，避开集群里的 Docker Hub 拉取超时；
- 把 Keeper 明确 pin 到 `26.3`，不继续用 `latest`；
- 在目标 `podTemplate` 上加 `dedicated=high-performance:NoSchedule` 的 toleration；
- 把 `requests` 压到共享集群可调度的下限，但保持 `4 shards × 2 replicas + 3 Keeper` 目标拓扑不变。

对我来说，这一步很有提醒意义：**Operator 安装解决的是“有没有这套 API”，而不是“目标集群一定拉得起来”。** 真正的落地，还要把镜像分发、调度面、存储类和资源请求一起纳入同一条执行路径里。

## 对我的提醒

这次让我更确定一件事：在共享集群里，安装 Operator 从来都不只是“把一个 controller 跑起来”。它同时意味着：

- 引入新的 CRD；
- 引入新的控制循环；
- 改变集群对某类对象的理解方式。

也正因为如此，我更愿意把这类操作当成“平台层变更”，而不是“业务侧准备步骤”。一旦把层次分清楚，很多决策自然就会收敛到同一个方向上：**用 Helm、收窄 watch 范围、复用已有基础组件、把删除动作显式化。**

---

相关页面：[[topics/clickhouse-production-migration]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-deployment-topologies]] · [[topics/kubernetes-crd-recording-strategy]]
