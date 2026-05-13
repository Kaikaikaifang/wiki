---
title: clickhouse-go 客户端配置
type: source
tags: [数据库, ClickHouse, Go, 客户端, 连接池, 配置]
source_count: 1
updated: 2026-05-13
---

> 来源：[ClickHouse Configuration | clickhouse-go](https://clickhouse.com/docs/integrations/language-clients/go/configuration)

这篇文档把 clickhouse-go 客户端的配置参数摊得很清楚。它让我意识到，客户端侧的连接策略和服务器侧的拓扑决策是紧密耦合的——如果服务器侧选择了全副本架构，客户端的连接策略也需要相应调整。

## 核心配置参数

| 参数 | 类型 | 默认值 | 关键作用 |
|---|---|---|---|
| `Protocol` | `Protocol` | `Native` | 传输协议：`Native` (TCP) 或 `HTTP`。HTTP 支持更多压缩格式，TCP 内置 session |
| `Addr` | `[]string` | — | 多节点地址列表。全副本架构下应填入所有 replica |
| `ConnOpenStrategy` | `ConnOpenStrategy` | `ConnOpenInOrder` | 多节点连接策略：顺序故障转移、轮询、随机 |
| `MaxOpenConns` | `int` | `MaxIdleConns + 5` | 连接池最大打开连接数 |
| `MaxIdleConns` | `int` | `5` | 空闲连接池大小 |
| `ConnMaxLifetime` | `time.Duration` | `1h` | 连接最大生命周期。注意：节点离开集群后，连接可能分布不均 |
| `Compression` | `*Compression` | `nil` | 块级压缩：Native 支持 `LZ4`、`ZSTD`；HTTP 额外支持 `gzip`、`deflate`、`br` |
| `Settings` | `Settings` | — | 应用到每个查询的 ClickHouse 设置 |

## 多节点连接策略

对于全副本架构（1 shard × N replicas），`Addr` 应填入所有 replica 地址，客户端通过 `ConnOpenStrategy` 决定如何分发连接：

- **`ConnOpenInOrder`**（默认）：顺序消费地址列表。只有前面的地址连接失败时，才尝试后面的地址。本质是**故障转移**策略。
- **`ConnOpenRoundRobin`**：轮询策略，负载均衡到所有地址。
- **`ConnOpenRandom`**：随机选择节点。

**对于查询负载均衡**，`ConnOpenRoundRobin` 或 `ConnOpenRandom` 更合适。但需要注意：`ConnMaxLifetime` 默认 1 小时，如果某个节点离开集群，连接可能重新分布到其他节点，导致负载不均。

## 连接池

- 每个查询从连接池获取连接，查询完成后归还
- 一个连接的生命周期对应一个 batch 的生命周期，`Send()` 后释放
- `MaxOpenConns=1` 可保证同一连接用于后续查询，但仅在使用临时表等特殊场景下需要

## TCP vs HTTP

| 特性 | TCP (Native) | HTTP |
|---|---|---|
| 默认端口 | 9000 (plain), 9440 (TLS) | 8123 (plain), 8443 (TLS) |
| Session | 内置（始终活跃） | 显式传递 `session_id` |
| 压缩 | `lz4`, `zstd` | `lz4`, `zstd`, `gzip`, `deflate`, `br` |
| JWT 认证 | — | ✅ ClickHouse Cloud HTTPS |
| OpenTelemetry | ✅ 客户端发送 | 服务端支持，客户端暂不支持发送 `traceparent` |

## 对我的启发

这篇文档让我意识到，ClickHouse 客户端配置不是"填几个参数就完事"，而是需要和服务端拓扑一起设计：

- 全副本架构下，客户端的 `Addr` 应包含所有 replica，`ConnOpenStrategy` 应选择轮询或随机，实现查询负载均衡；
- `ConnMaxLifetime` 的默认值（1 小时）在节点动态扩缩容时可能导致连接分布不均，需要监控；
- 协议选择（TCP vs HTTP）不仅影响压缩选项，还影响 session 语义和认证方式。

这也让我把"客户端配置"纳入了部署拓扑判断框架：服务端选择全副本架构后，客户端的连接策略、连接池大小和协议选择都需要相应调整。

---

来源：[ClickHouse Configuration | clickhouse-go](https://clickhouse.com/docs/integrations/language-clients/go/configuration)

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-sharding-decision]]
