---
title: Traefik Labs
type: entity
tags: [Traefik, 负载均衡, 代理, Kubernetes]
source_count: 3
updated: 2026-05-14
---

## 基本定位

Traefik Labs 是 Traefik Proxy 背后的公司，同时也推广 **Triple Gate Pattern**（三层网关模式），统一 API Gateway、AI Gateway 和 MCP Gateway 的架构理念。

## 核心产品

### Traefik Proxy

开源的反向代理和负载均衡器，原生为容器和 Kubernetes 设计。关键特性：

- **声明式配置**：通过 Kubernetes CRD、Docker labels 或文件自动发现服务
- **L4/L7 负载均衡**：支持 TCP/UDP 和 HTTP，四种核心策略（WRR、P2C、HRW、Least-Time）
- **动态路由**：基于 path、header、host、cookie 的路由规则
- **自动 HTTPS**：通过 Let's Encrypt 自动管理 TLS 证书
- **中间件生态**：压缩、重试、速率限制、基本认证、转发认证等

### Traefik Hub（商业版）

在开源版基础上增加：
- API 管理（发布、版本控制、文档）
- 安全策略（OAuth、JWT、API 密钥）
- 可观测性（实时指标、告警）

## 设计理念

Traefik 的设计哲学与 Envoy 形成有趣对比：

- **配置即代码**：路由、服务、中间件都通过声明式配置定义，而不是通过管理 API 或控制面
- **云原生原生**：从第一天就为动态容器环境设计，而不是从静态配置文件演进而来
- **渐进复杂度**：基础负载均衡开箱即用，高级特性（嵌套健康检查、流量镜像）按需启用

## 适用场景

- **Kubernetes ingress**：Traefik 是最流行的 Kubernetes ingress controller 之一
- **边缘代理**：自动 HTTPS、动态路由、中间件链
- **渐进式交付**：通过 WRR 权重实现金丝雀和蓝绿部署

## 局限

- 高级特性（如嵌套健康检查）仅支持 File provider，在纯 Kubernetes CRD 环境中需要额外维护 ConfigMap
- 服务网格能力弱于 Envoy/Istio，更适合边缘和 ingress 场景，而非东西向服务间通信
- 企业级安全策略（细粒度 RBAC、全局审计）需要商业版

---

相关页面：[[topics/load-balancing-strategies]] · [[topics/progressive-delivery]] · [[sources/advanced-load-balancing-traefik]] · [[sources/choosing-load-balancing-strategy]] · [[sources/harness-vs-platform-engineering]]
