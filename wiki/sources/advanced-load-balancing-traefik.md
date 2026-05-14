---
title: Traefik Proxy 高级负载均衡实战
type: source
tags: [负载均衡, Traefik, Kubernetes, 渐进式交付]
source_count: 1
updated: 2026-05-14
---

## 核心要点

Traefik Proxy 在 Kubernetes 中实现 L7 高级负载均衡的核心机制可分为四类：**加权调度**、**流量镜像**、**会话保持**与**跨环境健康检查**。

### 加权轮询（WRR）与渐进式交付

WRR 的核心价值不在"轮询"本身，而在于通过动态调整权重实现**渐进式交付**。Traefik Service 抽象允许在不停机的前提下，将流量从 v1 逐步切向 v2——这本质上是用负载均衡器做部署策略，而非单纯做流量分发。

关键洞察：部署（deploy）和发布（release）是两个独立事件。你可以随时把新版本部署到集群，但只有开始把真实流量路由过去，才叫发布。WRR 权重从 0 缓慢上调的过程，就是把发布风险摊薄到时间轴上的过程。

### 流量镜像（Mirroring）

镜像会把请求复制到另一组后端，但**不返回响应给客户端**。与渐进式交付相比，镜像的优势是零用户影响——即使新版本返回错误，用户也感知不到。它的适用场景是：用生产流量做 shadow testing，通过日志和指标验证新版本行为，而不是通过用户反馈。

### 粘性会话（Sticky Sessions）

Traefik 用 `Set-Cookie` 实现客户端与后端的亲和性。当后端故障时，会话会被重新绑定到健康实例。这个机制解决的典型问题是：无状态负载均衡器把同一个用户的请求打到不同 Tomcat 实例，导致反复建立新会话。粘性会话是**有状态服务在无状态基础设施上运行**的妥协方案。

### 嵌套健康检查（Nested Health Checks）

这是 Traefik File provider 独有的高级特性，允许在多层后端（如跨数据中心、或 Kubernetes + VM 混合环境）上做层级健康检查。例如：先检查数据中心级 endpoint 是否健康，再检查该数据中心内具体实例。这对**混合云迁移**或**多活架构**特别有用——你可以把传统 VM 上的应用和 Kubernetes 上的新版本放进同一个 server pool，用 WRR 逐步切流。

## 实践启示

- 负载均衡器不只是"把请求分出去"，它是**发布策略、测试策略、故障隔离策略**的承载面
- 在 Kubernetes 中，Traefik 的 CRD 让 L7 规则成为声明式配置的一部分，但高级特性（如嵌套健康检查）仍需 File provider，这意味着你需要用 ConfigMap 管理配置文件——这引入了一个需要维护的额外配置层
- 渐进式交付和镜像可以组合使用：先用镜像做无风险验证，再用 WRR 做真实切流

## 来源信息

- 作者：Jakub Hajek
- 发布日期：2022-10-06
- 原文：https://traefik.io/blog/exploring-advanced-load-balancing-in-kubernetes-with-traefik-proxy
- 本地归档：`raw/articles/Advanced Load Balancing with Traefik Proxy.md`

## 相关页面

- [[topics/load-balancing-strategies]] — 负载均衡策略的通用选择框架
- [[topics/progressive-delivery]] — 渐进式交付与蓝绿部署、金丝雀发布
- [[sources/choosing-load-balancing-strategy]] — 四种核心策略的决策树
