---
title: Envoy Proxy
type: entity
tags: [Envoy, 服务网格, L7代理, 可观测性]
source_count: 1
updated: 2026-05-14
---

## 基本定位

Envoy 是一个开源的 L7 代理和通信总线，面向大型现代面向服务的架构。它由 Lyft 创建，现在是 CNCF 毕业项目，被 Istio、AWS App Mesh、Consul Connect 等服务网格方案采用为数据面。

## 核心设计

### 进程外架构

Envoy 作为独立进程运行在每个应用服务器旁边，所有进出流量经过它。所有 Envoy 共同构成一个透明通信网格：应用只与 localhost 通信，对网络拓扑一无所知。

这个设计的关键收益是**语言无关**和**独立升级**：一个 Envoy 部署可以同时桥接 Java、Go、Python 等服务，通信策略的更新不需要协调各服务的发布节奏。

### 过滤器架构

Envoy 的核心是可插拔过滤器链：
- **L3/L4 网络过滤器**：TCP/UDP 代理、TLS 认证、Redis/MongoDB/Postgres 协议代理
- **HTTP L7 过滤器**：缓冲、速率限制、路由、DynamoDB 嗅探等

同一套过滤器机制被复用到完全不同的协议层，降低了扩展的心智负担。

### 协议支持

- **HTTP/2 一流支持**：双向透明桥接 HTTP/1.1 与 HTTP/2，服务间通信推荐 HTTP/2 以利用多路复用
- **gRPC 原生兼容**：基于 HTTP/2，Envoy 提供完整的路由和负载均衡能力
- **HTTP/3（alpha）**：从 1.19.0 开始支持上游和下游 QUIC

## 关键能力

### 动态配置（xDS）

Envoy 通过分层 xDS API 实现完全动态管理：
- CDS（Cluster Discovery Service）：后端集群定义
- EDS（Endpoint Discovery Service）：集群内实例列表
- RDS（Route Discovery Service）：HTTP 路由规则
- LDS（Listener Discovery Service）：监听端口配置
- SDS（Secret Discovery Service）：TLS 证书
- ADS（Aggregated Discovery Service）：聚合所有配置的单一端点

### 高级负载均衡与弹性

- 自动重试、熔断、全局速率限制
- 请求镜像（shadow traffic）
- 异常检测（outlier detection，被动健康检查）
- 主动健康检查 + 最终一致的服务发现

### 可观测性

Envoy 的设计假设是：**网络问题可能是应用问题，应用问题可能表现为网络症状**。所有子系统暴露统计指标（statsd 兼容），支持分布式追踪，并通过 admin 端口提供运行时诊断。

## 适用场景

- **服务网格数据面**：Istio、Consul Connect 等控制面的默认代理
- **边缘代理**：TLS 终止、L7 路由、限流
- **多语言微服务桥接**：统一不同语言服务的通信策略

## 与 Traefik 的对比

| 维度 | Envoy | Traefik |
|---|---|---|
| 部署模式 | Sidecar / 独立代理 | Ingress / 边缘代理 |
| 配置方式 | xDS API / 静态文件 | 声明式（CRD / labels / 文件） |
| 服务网格 | 原生设计 | 非核心场景 |
| 协议扩展 | 过滤器链 | 中间件链 |
| 可观测性 | 深度集成（stats、tracing） | 基础指标 + 商业版增强 |
| 学习曲线 | 陡峭（xDS、过滤器概念） | 平缓（云原生原生设计） |

## 演进方向

Envoy 社区正在配合 Istio 推进 **ambient mesh**（无 sidecar）模式，把 L4 功能下沉到节点级 ztunnel，L7 功能按需部署为 waypoint proxy。这反映了社区对 sidecar 资源成本的反思，但 Envoy 作为数据面的核心地位没有变化。

---

相关页面：[[topics/service-mesh]] · [[topics/load-balancing-strategies]] · [[sources/what-is-envoy]]
