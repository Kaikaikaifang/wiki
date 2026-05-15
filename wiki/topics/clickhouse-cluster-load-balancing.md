---
title: ClickHouse 集群负载均衡
type: topic
tags: [数据库, ClickHouse, 负载均衡, Traefik, 高可用]
source_count: 4
updated: 2026-05-15
---

> 自管 ClickHouse 集群最常被忽略的问题不是“怎么建集群”，而是“客户端连谁”。如果答案永远是“直接指向一个已存在的节点”，那单点故障只是时间问题。

## 核心判断

ClickHouse 自管集群的负载均衡问题要拆成两层理解：

1. **连接层**：客户端应该连接一个稳定的入口，还是直接配多个节点地址？
2. **查询层**：查询到达某个节点后，如何利用集群内其他节点的算力？

这两层不能混为一谈。连接层解决的是“请求发到哪台机器”，查询层解决的是“这台机器怎么把活分出去”。ClickHouse Cloud 把两层都托管了，自管集群需要自己做选择。

## 为什么“直接指向一个节点”不够

当前很多部署的默认做法是让客户端直接连接 ClickHouse Operator 生成的 Kubernetes Service：

```
clickhouse.<namespace>.svc.cluster.local:8123
```

这个 Service 是 ClusterIP 类型，会把流量轮询到所有 Endpoint。但问题在于：

- **没有健康检查**：如果某个 ClickHouse Pod 挂了，Endpoint 更新有延迟，期间流量仍会打到故障节点；
- **无会话感知**：同一条长连接可能被切到不同节点，而 ClickHouse Native 协议是有状态的；
- **故障恢复依赖客户端**：连接超时后，客户端需要自己重试或切换地址。

换句话说，Kubernetes Service 做了一层“能连上谁就连谁”的分发，但没有解决“连上的那个是不是健康的”这个问题。

## ClickHouse Cloud 的体验基准

Cloud 版客户端只需要一个 endpoint：

```go
Addr: []string{"xxx.asia-northeast1.gcp.clickhouse.cloud:9440"}
```

背后由 Cloud 托管的负载均衡器负责：

- 连接分发到可用计算节点；
- 节点故障时自动剔除；
- 扩容/缩容对客户端完全透明。

自管集群无法复制 Cloud 的 SharedMergeTree 引擎和秒级扩容，但可以在**连接层**用外部负载均衡器近似这种体验。

## 自管集群的连接层选项

### 选项 A：客户端多地址 + 轮询/随机

`clickhouse-go` 支持在 `Addr` 中填入所有 replica 地址，通过 `ConnOpenRoundRobin` 或 `ConnOpenRandom` 做连接级负载均衡。

**优点**：
- 不依赖外部基础设施；
- 实现简单，配置即生效。

**缺点**：
- 客户端需要知道所有节点地址，扩容时需更新配置；
- 故障节点不会被自动剔除，连接可能失败；
- `ConnOpenInOrder`（默认）在故障节点排前面时，每次查询都先超时；
- `ConnMaxLifetime` 默认 1 小时，节点离开后连接分布可能长期不均。

**适用**：开发环境、节点数稳定的小集群、能接受应用层重试的场景。

### 选项 B：外部负载均衡器（Traefik / Envoy / 云厂商 LB）

在 ClickHouse 集群前部署一个支持 TCP/HTTP 健康检查的负载均衡器，把所有节点暴露为单一入口。

**Traefik 的具体做法**：

- 在 Traefik 中增加 TCP entrypoints（`:9000` for Native, `:8123` for HTTP）；
- 配置 TCP router + TCP service，指向所有 ClickHouse 节点；
- 启用 `healthCheck`，定期探测节点健康状态；
- 客户端只连接 Traefik 入口地址。

**优点**：
- 客户端只需配一个地址，扩容时只需更新 LB 后端列表；
- 健康检查自动剔除故障节点，故障转移对客户端透明；
- 与现有 `deploy/charts` 的 Traefik gateway 共用基础设施。

**缺点**：
- 引入额外配置层，Traefik TCP healthCheck 只能验证端口监听，不能验证 ClickHouse 内部状态（如 Keeper 失联导致只读）；
- 有状态节点本质限制：LB 解决的是“连不连得上”，不是“数据有没有复制完”；
- 写入路径需谨慎：如果写入直打本地表，LB 轮询可能导致数据路由错误；写入应优先走 `Distributed` 表。

**适用**：生产环境、节点数会动态变化、需要故障自动转移的场景。

### 选项 C：云厂商托管负载均衡器

如果部署在腾讯云、阿里云等环境，可以直接使用云厂商的 CLB/SLB 作为 TCP 负载均衡器。

**优点**：
- 健康检查、故障转移、带宽扩容都由云厂商托管；
- 与 Kubernetes Service 集成成熟（如 LoadBalancer 类型 Service）。

**缺点**：
- 增加云资源成本；
- 跨可用区时可能有额外网络时延；
- 配置粒度不如 Traefik/Envoy 灵活（如不能做基于响应时间的自适应路由）。

**适用**：公有云生产环境、已有云厂商负载均衡基础设施的场景。

## 查询层的并行化：Parallel Replicas

连接层负载均衡只解决了“请求发到哪台机器”。查询到达后，如果希望利用集群内所有 replica 的算力，需要开启 **Parallel Replicas**。

这是自管集群最接近 ClickHouse Cloud 查询体验的配置：

```sql
SET enable_parallel_replicas = 1;
SET cluster_for_parallel_replicas = 'default';
SET max_parallel_replicas = 4;
```

工作机制：

1. 查询到达的节点成为 coordinator；
2. coordinator 收集各 replica 的 announcement（当前拥有哪些 parts）；
3. 把 granules 拆成任务集，通过 dynamic coordination 让 replica 主动领取；
4. 重复查询通过 `hash(part + granules) % replica_count` 命中同一 replica 的本地 cache；
5. 慢节点任务可被其他 replica steal，降低尾延迟。

**关键限制**：
- 复杂查询（CTE、JOIN、子查询）效果可能不佳；
- 小查询的协调开销可能抵消并行收益；
- 使用 `FINAL` 或 projections 时不可用；
- 必须开启新 analyzer。

也就是说，Parallel Replicas 不是“开启就能加速所有查询”的开关，而是**在 granule 级别有充足并行空间时的加速器**。

## 与 Cloud 体验的差距评估

| 维度 | ClickHouse Cloud | 自管 + Traefik LB + Parallel Replicas | 差距 |
|---|---|---|---|
| 客户端连接数 | 1 个 endpoint | 1 个 LB 地址 | ✅ 等价 |
| 连接层负载均衡 | Cloud 内部托管 | Traefik TCP LB | ✅ 近似 |
| 健康检查与故障剔除 | 自动 | Traefik healthCheck | ✅ 可配置实现 |
| 查询层并行化 | Parallel Replicas | Parallel Replicas（手动开启） | ⚠️ 需配置 |
| 扩容透明性 | 完全透明 | 需更新 LB servers 列表 | ❌ 有差距 |
| 节点状态 | 无状态（共享存储） | 有状态（本地盘 + 复制） | ❌ 本质差异 |
| 秒级扩容 | 支持 | 不支持（需数据复制） | ❌ 引擎差异 |

**核心结论**：自管集群可以在**连接层和查询层**近似 Cloud 体验，但**状态层和弹性层**受限于 ReplicatedMergeTree 引擎，无法复制 Cloud 的秒级扩容和完全透明扩缩容。

## 生产建议

### 1. 优先使用外部 LB，而不是客户端多地址

客户端多地址在节点故障时的表现不可预测（尤其是 `ConnOpenInOrder` 的默认行为）。外部 LB 的健康检查能把故障转移从客户端搬到基础设施层，是更稳的选择。

### 2. 如果已经在用 Traefik，优先复用而不是新增组件

`deploy/charts` 已经在每个环境部署了 Traefik gateway。为 ClickHouse 增加 TCP entrypoints 和 router 只是配置变更，不需要引入新的负载均衡器。这减少了运维面和资源开销。

### 3. 写入路径与查询路径分开考虑

- **查询**：可以安全地走 LB -> 任一 replica -> Parallel Replicas 并行化；
- **写入**：如果表是 `Distributed` 表，LB 入口应指向 Distributed 表所在节点，由 Distributed 表负责分片路由；如果直写本地表，LB 轮询会破坏分片键路由，必须避免。

### 4. 健康检查需要分层

- **基础层**：TCP 端口探测，验证进程是否存活；
- **应用层**：HTTP `/ping` 或 `SELECT 1`，验证 ClickHouse 是否真正可服务；
- **复制层**：监控 `system.replicas` 的 `absolute_delay`、`queue_size`，发现复制延迟或 replica 失联。

Traefik 的 TCP healthCheck 只能做基础层。应用层和复制层需要通过监控告警或 sidecar 探针补充。

### 5. 不要期望 LB 解决数据面问题

LB 解决的是连接可用性，不是数据一致性。如果某个 replica 挂了，LB 会把它剔除，但该 replica 恢复后仍需通过复制队列追平数据。复制健康度是独立于 LB 的另一个监控维度。

## 验证结果（k3d-test-cluster）

`deploy/charts/TODO.md` 设计的验证方案已在 `k3d-test-cluster` 上完整执行。以下是实测结果。

### 测试环境

- **集群**：k3d-test-cluster（单节点 K3s v1.33.4）
- **命名空间**：swanlab
- **ClickHouse**：`2 shards × 1 replica`（k3d overlay 配置），Operator 管理
- **Traefik**：v3.6，已有 gateway Deployment + Service + ConfigMap
- **测试工具**：`clickhouse-client`（Native 协议，端口 9000）

### Phase 1：基线（无 LB，直连 headless Service）

**连接目标**：`clickhouse-clickhouse-headless.swanlab.svc.cluster.local:9000`

| 指标 | 结果 |
|---|---|
| 直接查询 `SELECT 1` | ✅ 成功 |
| `SELECT hostname()` 延迟（10 次） | avg 33.7ms / min 27ms / max 62ms |
| `SELECT count() FROM system.parts` 延迟（10 次） | avg 35.7ms / min 30ms / max 49ms |
| 删除一个 ClickHouse Pod 后查询失败数 | **0** |
| 删除到 Pod Ready 恢复时间 | 29s |

**关键发现**：Kubernetes headless Service 在 Pod 删除后**没有产生查询失败**，因为 Endpoint 控制器会立即将删除的 Pod 从 Endpoints 列表中移除，流量自动路由到存活的 Pod。但 headless Service **没有主动健康检查**，它依赖的是 Kubernetes 的 Pod 生命周期事件，而不是端口探测。

### Phase 2：Traefik TCP LB 部署

在现有 Traefik gateway 上增加 ClickHouse TCP 负载均衡：

1. **静态配置**（`traefik.yaml`）：增加 `clickhouse-native` (`:9000`) 和 `clickhouse-http` (`:8123`) entryPoints；
2. **动态配置**（`dynamic.yaml`）：增加 TCP routers 和 TCP services，指向两个 ClickHouse Pod IP；
3. **健康检查**：`interval: 10s`, `timeout: 5s`（TCP 端口探测）；
4. **Deployment**：增加 `containerPort` 9000 和 8123；
5. **Service**：已有端口 9000/8123 定义，无需修改。

**部署难点**：
- Traefik TCP healthCheck 只支持 `interval` 和 `timeout`，不支持 `path`/`scheme`（这些是 HTTP healthCheck 的参数）；
- ClickHouse Pod IP 在删除重建后会变化，ConfigMap 需要同步更新（本次验证中手动更新了 IP）。

### Phase 3：LB 行为验证

**连接分发测试**（20 次 `SELECT hostname()` 通过 `gateway.swanlab.svc.cluster.local:9000`）：

| 后端 | 命中次数 |
|---|---|
| clickhouse-clickhouse-0-0-0 | 10 |
| clickhouse-clickhouse-0-1-0 | 10 |

✅ **完美轮询**，连接均匀分发到两个 shard。

**故障转移测试**：

| 指标 | 结果 |
|---|---|
| 删除 Pod 后查询失败数 | **2** |
| 错误信息 | `Code: 210. DB::NetException: Connection reset by peer (NETWORK_ERROR)` |
| 删除到 Pod Ready 恢复时间 | 16s |
| 恢复后查询是否恢复正常 | ✅ 是 |

**关键发现**：
- Traefik LB 在 Pod 删除时产生了 **2 次瞬态失败**，而 Kubernetes headless Service 在 Phase 1 中是 **0 次失败**；
- 原因是 Traefik 的 health check 间隔为 10s，在 Pod 被删除到 health check 标记为 DOWN 之间存在一个窗口期，期间新建连接可能命中正在终止的 Pod；
- 一旦 health check 将故障 Pod 标记为 DOWN，后续查询立即恢复正常；
- Pod 重建并 Ready 后，Traefik 不会自动重新添加新 IP（因为 ConfigMap 中是静态 IP），需要手动更新 ConfigMap 或改用 Kubernetes CRD provider 实现动态服务发现。

### Phase 4：与 ClickHouse Cloud 体验对比

| 维度 | ClickHouse Cloud | 自管 + Traefik LB（实测） | 差距 |
|---|---|---|---|
| 客户端连接数 | 1 个 endpoint | 1 个 LB 地址 | ✅ 等价 |
| 连接层负载均衡 | Cloud 内部托管 | Traefik TCP LB（轮询） | ✅ 近似 |
| 健康检查与故障剔除 | 自动 | TCP 端口探测（10s 间隔） | ⚠️ 有延迟（实测 2 次失败） |
| 查询层并行化 | Parallel Replicas | Parallel Replicas（手动开启） | ⚠️ 需配置 |
| 扩容透明性 | 完全透明 | ❌ 需手动更新 ConfigMap IP | ❌ 有差距 |
| 节点状态 | 无状态（共享存储） | 有状态（本地盘 + 复制） | ❌ 本质差异 |
| 秒级扩容 | 支持 | 不支持（需数据复制） | ❌ 引擎差异 |

**核心结论**：

1. **连接层可以近似 Cloud**：Traefik LB 让客户端只需配一个地址，连接均匀分发，故障后自动剔除（虽有 10s 级延迟）；
2. **健康检查延迟是真实存在的**：TCP 端口探测的 10s 间隔在节点故障时会产生瞬态失败，生产环境应缩短间隔或增加应用层探针；
3. **静态 IP 是运维负担**：ConfigMap 中的硬编码 Pod IP 在 Pod 重建后失效，生产环境应改用 Kubernetes CRD provider 或 DNS 名称实现动态发现；
4. **状态层无法复制**：ReplicatedMergeTree 的扩容需要数据复制，不是 LB 能解决的。

### 生产建议（基于验证结果）

1. **缩短 health check 间隔**：从 10s 缩短到 3-5s，减少故障窗口；
2. **使用 DNS 名称而非静态 IP**：在 Traefik TCP service 中使用 ClickHouse headless Service 的 DNS 名称（如 `clickhouse-clickhouse-headless.swanlab.svc.cluster.local`），让 Kubernetes DNS 自动解析到存活 Pod；
3. **增加应用层健康检查**：Traefik TCP healthCheck 只能验证端口，建议配合 `clickhouse-client --query "SELECT 1"` 的 sidecar 探针或监控告警；
4. **写入路径仍需走 Distributed 表**：LB 轮询写入本地表会破坏分片键路由，写入必须指向 Distributed 表入口；
5. **考虑 Envoy 替代**：如果需要更细粒度的健康检查（如 HTTP `/ping`）、主动异常检测或熔断，Envoy 比 Traefik 更适合有状态后端。

---

来源：[[sources/clickhouse-cloud-architecture]] · [[sources/clickhouse-go-configuration]] · [[sources/clickhouse-parallel-replicas]] · [[sources/advanced-load-balancing-traefik]]

相关页面：[[topics/clickhouse-deployment-topologies]] · [[topics/load-balancing-strategies]] · [[entities/traefik]] · [[entities/clickhouse]] · [[topics/clickhouse-production-migration]]
