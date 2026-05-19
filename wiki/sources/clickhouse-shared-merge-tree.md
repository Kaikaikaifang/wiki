---
title: ClickHouse SharedMergeTree
type: source
tags: [数据库, ClickHouse, 云原生, 存算分离, SharedMergeTree, 复制]
source_count: 1
updated: 2026-05-13
---

> 来源：[SharedMergeTree | ClickHouse Docs](https://clickhouse.com/docs/cloud/reference/shared-merge-tree)

SharedMergeTree 是 ClickHouse Cloud 的默认表引擎，是 ReplicatedMergeTree 家族在云原生共享存储环境下的重新实现。它把"副本间复制"换成了"共享存储 + Keeper 协调"，从根本上改变了存算分离的边界。

## 与 ReplicatedMergeTree 的核心区别

| 维度 | ReplicatedMergeTree | SharedMergeTree |
|---|---|---|
| 数据存储 | 每个 replica 持有完整数据副本 | 数据在共享对象存储，所有 replica 共享 |
| 元数据存储 | 每个 replica 本地持有元数据，需要 replica 间复制 | 元数据在 ClickHouse-Keeper，所有 replica 共享 |
| replica 间通信 | 需要直接通信复制数据和元数据 | 不直接通信，通过共享存储和 Keeper 协调 |
| 复制模型 | 同步/异步 leader-follower | **异步 leaderless** |
| 扩容速度 | 需要复制数据到新 replica | 新 replica 直接从共享存储读取元数据，秒级 |
| 最大 replica 数 | 受复制开销限制 | **可支持数百个 replica** |

## 架构优势

SharedMergeTree 把存算分离推进到了更深层级：

1. **更高的写入吞吐**：不需要 replica 间复制数据，写入直接落共享存储
2. **更快的后台合并**：元数据在 Keeper，merge 协调更高效
3. **更快的 mutation**：不需要广播到所有 replica
4. **更快的扩缩容**：加 replica 时不需要等待数据复制，直接从共享存储拉取元数据
5. **更轻量的强一致性**：通过 Keeper 元数据一致性保证，而不是 replica 间复制确认

## 关键实现细节

- **异步 leaderless 复制**：没有固定的 leader，所有 replica 平等地从 Keeper 获取元数据
- **共享存储承载数据**：Amazon S3、Google Cloud Storage、MinIO、Azure Blob Storage 等
- **Keeper 只存储元数据**：包括 part 列表、checksum、merge 计划等，数据本身不在 Keeper
- **自动引擎转换**：在 ClickHouse Cloud 中，用户写 `ENGINE = MergeTree` 或 `ENGINE = ReplacingMergeTree` 时，系统会自动转换为对应的 `SharedMergeTree` 变体

## Introspection 差异

SharedMergeTree 移除了部分 ReplicatedMergeTree 特有的系统表，因为不需要 replica 间复制：

- **移除**：`system.replication_queue`、`system.replicated_fetches`
- **替代**：
  - `system.virtual_parts` — 替代 `replication_queue`，存储当前 parts 和进行中的 merge/mutation/drop 信息
  - `system.shared_merge_tree_fetches` — 替代 `replicated_fetches`，记录主键和 checksum 加载到内存的进度

## 一致性模型

SharedMergeTree 提供了比 ReplicatedMergeTree 更轻量的一致性保证：

- **写入**：默认就是 quorum 写入（元数据写入 Keeper quorum），不需要设置 `insert_quorum`
- **读取**：大多数情况下不需要 `select_sequential_consistency`，异步复制的延迟极低
- **需要强一致性时的选择**（按推荐顺序）：
  1. 在同一 session 或同一节点读写（该 replica 已有最新元数据）
  2. 写到一个 replica、从另一个 replica 读时，执行 `SYSTEM SYNC REPLICA LIGHTWEIGHT`
  3. 在查询中设置 `select_sequential_consistency`

## 设置变化

以下设置在 SharedMergeTree 中不再需要或行为改变：

- `insert_quorum` — 不需要，所有写入都是 quorum 写入
- `insert_quorum_parallel` — 不需要
- `select_sequential_consistency` — 不需要 quorum 确认，但会额外增加 Keeper 负载

## 对我的启发

SharedMergeTree 让我理解了 ClickHouse Cloud 为什么能做到"无分片 + 数百 replica"：它不是靠复制堆出来的，而是靠"共享存储 + Keeper 元数据"彻底解耦了计算和存储。这意味着：

- 扩容不再是"加 replica 等数据复制"，而是"新 replica 订阅 Keeper 元数据即可"
- 写入性能不再受 replica 间复制带宽限制，只受共享存储吞吐限制
- 一致性不再需要在 N 个 replica 间确认，只需要在 Keeper quorum 间确认

这也解释了为什么 ClickHouse Cloud 可以支持 compute-compute separation 和动态扩缩容：底层引擎已经为"共享存储 + 无状态计算节点"做好了设计。

---

来源：[SharedMergeTree | ClickHouse Docs](https://clickhouse.com/docs/cloud/reference/shared-merge-tree)

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-deployment-topologies]] · [[sources/clickhouse-cloud-architecture]] · [[sources/clickhouse-parallel-replicas]] · [[topics/clickhouse-sharding-decision]] · [[sources/clickhouse-replicated-table-engines]]
