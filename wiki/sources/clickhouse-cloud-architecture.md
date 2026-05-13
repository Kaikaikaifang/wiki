---
title: ClickHouse Cloud 架构
type: source
tags: [数据库, ClickHouse, 云原生, 存算分离, 架构]
source_count: 1
updated: 2026-05-13
---

> 来源：[ClickHouse Cloud architecture | ClickHouse Docs](https://clickhouse.com/docs/cloud/reference/architecture)

## 核心架构特征

ClickHouse Cloud 的架构和自管实例有本质区别：它把存算分离做到了默认层级，同时保留了 ClickHouse 的核心查询能力。

### 对象存储 backed 的存储层

- 存储容量理论上无上限，不需要手动分片；
- 对象存储的单价远低于本地 SSD，尤其适合访问频率低的数据；
- 数据持久性由云厂商对象存储保证，不需要自建副本做数据冗余。

### 计算层的自动扩缩与空闲暂停

- 不需要预先规格化（sizing），也不需要为峰值过度预配；
- 无查询负载时自动 idle，需要时自动 resume；
- 默认高可用，节点故障时自动切换。

### 托管运维

- 安装、监控、备份、计费由平台负责；
- 默认开启成本管控，用户可在 Cloud console 中调节。

## 服务隔离模型

Cloud 环境下多租户隔离分三层：

| 隔离维度 | 实现方式 |
|---|---|
| 网络隔离 | 所有服务在网络层隔离 |
| 计算隔离 | 各服务部署在独立 Kubernetes pod/namespace 中 |
| 存储隔离 | AWS 使用共享 bucket 的不同 subpath，配合独立 IAM role；GCP/Azure 则每个服务独占 bucket/container |

对于 AWS Enterprise 服务，还支持 CMEK（Customer-Managed Encryption Key）实现静态数据的高级隔离。

## 客户端连接方式：为什么只需要一个 Endpoint

ClickHouse Cloud 与自管集群在客户端连接策略上有本质区别。官方文档明确说明：

- 每个 Cloud service 提供一个**服务 endpoint**（如 `xxx.REGION.CSP.clickhouse.cloud:9440`）
- 客户端**不需要**在连接串中列出所有 replica 节点
- Cloud 平台内部负责负载均衡和查询分发

这与自管集群的推荐做法不同：自管集群要么自己配负载均衡器（LB），要么在客户端列出所有 replica 地址做轮询。Cloud 把这些都托管了。

**连接示例（官方推荐）：**

```go
conn, err := clickhouse.Open(&clickhouse.Options{
    Addr: []string{"xxx.asia-northeast1.gcp.clickhouse.cloud:9440"},
    Protocol: clickhouse.Native,
    TLS:      &tls.Config{},
    Auth: clickhouse.Auth{
        Username: "default",
        Password: "xxx",
    },
})
```

注意 `Addr` 只有一个地址，但 Cloud 内部会把连接分发到某个计算节点，再由该节点作为 coordinator 做 Parallel Replicas 并行化。

## Compute-Compute Separation

这是我觉得 Cloud 架构里最有工程价值的设计之一：多个计算节点组（warehouse）可以共享同一份底层对象存储，每个节点组有自己独立的服务 URL。

这意味着：

- 读和写可以用不同的计算资源，避免批量写入冲击交互式查询；
- 不同业务线可以共享同一套数据，但拥有独立的扩缩容边界；
- 计算资源利用率更高，因为每个节点组按自身负载独立伸缩。

## 并发模型

- 没有全局 QPS 上限；
- 每个 replica 有 1000 并发查询的上限；
- 实际 QPS = 平均查询执行时间 × replica 数量，因此水平增加 replica 是提升并发的主要手段。

---

来源：[ClickHouse Cloud architecture | ClickHouse Docs](https://clickhouse.com/docs/cloud/reference/architecture)

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-deployment-topologies]]
