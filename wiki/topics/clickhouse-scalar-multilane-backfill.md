---
title: ClickHouse scalar 多 lane 回灌
type: topic
tags: [数据库, ClickHouse, 数据迁移, 回灌, Kubernetes]
source_count: 0
updated: 2026-04-30
---

> 我现在会把 `scalar` 历史回灌理解成一个“按主键排序空间推进的批处理系统”，而不是简单的并发导出脚本。真正决定速度和安全性的，不是 lane 数量本身，而是 cursor 是否能命中主键裁剪、lane 是否互斥、目标集群是否还能稳定消化导入。

## 问题不是 ClickHouse 导入，而是源端扫描形状

这次 `scalar` 回灌一开始卡在第 `99` 批附近。单批耗时里，目标 ClickHouse 导入和 OSS 备份都很快，真正慢的是源端导出。

旧查询使用：

```sql
WHERE tuple(projectId, experimentId, key, step) > tuple(...)
```

这个写法语义正确，但在源端 ClickHouse `24.3` 上没有被优化成主键裁剪，`EXPLAIN indexes = 1` 里会退化成 `PrimaryKey Condition: true`。结果是后段每批 `LIMIT 20M` 虽然只返回 2000 万行，但源端会扫描十亿级行数。

修复方式是把 tuple cursor 展开成字典序 `OR`：

```sql
WHERE projectId > :projectId
   OR (projectId = :projectId AND experimentId > :experimentId)
   OR (projectId = :projectId AND experimentId = :experimentId AND key > :key)
   OR (projectId = :projectId AND experimentId = :experimentId AND key = :key AND step > :step)
```

优化后，真实 `20M` 批次源端 `read_rows` 回到约 `20.3M`，不再是 `~1.98B`。

## 单 lane 先修到正确模式

多 lane 之前必须先把单 lane 修正确，否则只是把错误查询并发放大。

已验证的单 lane 模式是：

- 源端每批只执行一次 `SELECT ... FORMAT Native`；
- `file_rows` 从本地 Native 文件用 `clickhouse-local` 统计；
- `next_cursor` 从本地 Native 文件取最后一个排序键；
- run log 记录 `export_seconds`、`import_seconds`、`backup_seconds`；
- 目标写入 `Distributed` 表，同时把同一个 Native 文件 zstd 后备份到 OSS。

这个改法让 `20M` 单批总耗时从约 `180s` 级别回落到 `31-38s`。

## lane 的隔离来自边界，不是调度约定

`scalar` 的排序键是：

```sql
(projectId, experimentId, key, step)
```

多 lane 必须先把这个排序键空间切成连续、不重叠的区间。比如边界是 `B0 < B1 < B2 < B3 < B4`，则 4 lane 应该是：

```text
lane-a: B0 < key <= B1
lane-b: B1 < key <= B2
lane-c: B2 < key <= B3
lane-d: B3 < key <= B4
```

每条 lane 必须同时带上固定 lane range 和 lane-local cursor：

```sql
WHERE <key > lane_start>
  AND <key <= lane_end>
  AND <key > lane_cursor>
ORDER BY projectId, experimentId, key, step
LIMIT 20000000
```

如果每个 lane 只设置起点、不设置终点，那么后面的 lane 会覆盖前面的后续空间；如果多个 lane 共享同一个 cursor，则会争抢同一段数据。这两种都不是安全的多 lane。

## 边界推导要低内存

一开始用过这种方式推导下一个 `20M` 边界：

```sql
SELECT ...
FROM (
  SELECT ... ORDER BY projectId, experimentId, key, step LIMIT 20000000
)
ORDER BY projectId DESC, experimentId DESC, key DESC, step DESC
LIMIT 1
```

它能得到正确结果，但外层倒序排序给源端带来额外内存压力，验证中出现过 `EOF`。

现在推荐用：

```sql
SELECT projectId, experimentId, key, toString(step)
FROM app.scalar
WHERE <key > previous_boundary>
ORDER BY projectId, experimentId, key, step
LIMIT 1 OFFSET 19999999
FORMAT TSV
```

这个形式更贴近“取排序后第 2000 万行”，验证中没有触发源 Pod 重启。

## lane 数量不是越多越好

实测吞吐大致是：

| 模式 | 行数 | wall-clock | 吞吐 | 典型导出 | 典型导入 | 结论 |
|---|---:|---:|---:|---:|---:|---|
| 单 lane | 100M | 165s | 0.61M rows/s | 4-5s | 8-9s | 最稳，资源竞争最小 |
| 2 lane | 40M | 59s | 0.68M rows/s | 8s | 17s | 稳定性与速度较均衡 |
| 4 lane | 80M | 105-112s | 0.71-0.76M rows/s | 18-21s | 34s | 略快，但竞争明显 |

这说明多 lane 有提升，但不是线性提升。瓶颈已经从“源端单查询扫描放大”转移成“源端并发读取 + 目标并发导入竞争”。

因此当前策略是：

- 无人值守优先 `2 lanes × 20M`；
- 有人监控、追求最快时可以用 `4 lanes × 20M`；
- 不建议直接上 `5+ lanes`，除非重新验证目标导入和复制队列。

## 自动化 runner 的职责

自动化脚本在迁移仓库中是：

```text
production-v3/validation/scripts/run-scalar-multilane-backfill.sh
```

它做几件事：

- 从当前 safe cursor 推导下一波边界；
- 为每条 lane 创建独立 runtime ConfigMap；
- 并发启动 lane Job；
- 从 lane Job 日志解析 `rows`、`next_cursor` 和三段耗时；
- 只有在 lane 结果可解析后才推进 safe cursor；
- 将每条 lane 的结果写入 TSV run log。

当前采用的稳定命令形态是：

```bash
MIGRATION_NAMESPACE=tenant-kaikai \
LANES=2 \
BATCH_LIMIT=20000000 \
MAX_WAVES=0 \
RUN_ID=scalar-auto-2lane-full-20260430160000 \
RUN_LOG=production-v3/validation/runs/scalar-auto-2lane-full-20260430160000.tsv \
START_CURSOR=$'<projectId>\t<experimentId>\t<key>\t<step>' \
production-v3/validation/scripts/run-scalar-multilane-backfill.sh
```

## 运行中的安全阈值

继续跑时看这些信号：

- 目标 `system.replicas.queue_size = 0`；
- 目标 `absolute_delay = 0`；
- 源端 Pod 没有新增 `OOMKilled`；
- 每 lane `import_seconds` 不持续超过 `45-60s`；
- 每 lane `export_seconds` 不持续超过 `30s`；
- OSS `backup_seconds` 不持续超过 `15s`。

如果目标 count 低于源端 count，不要立即判定丢数据。`scalar` 源端存在重复排序键，目标 `ReplacingMergeTree` 会按排序键收敛。正确做法是按 lane 缩小范围，再只对可疑 lane 做 `uniqExact(projectId, experimentId, key, step)`，不要直接在 `80M+` 或 `100M+` 大区间上跑 `uniqExact`，验证中这样做触发过源 Pod OOM。

## 当前进度快照

截至 `2026-04-30 17:32 +0800` 左右，自动化 2-lane run 已完成到 wave `74`：

```text
run_id: scalar-auto-2lane-full-20260430160000
run_log: production-v3/validation/runs/scalar-auto-2lane-full-20260430160000.tsv
本 run 已完成: 2.96B rows
最新 cursor: l3baiq5daqucvtypcd2y0 / i252r5pp2naqf8sj5gua4 / train_4/metric_68 / 685
```

累计已确认完成大约 `5.68B` 行，源端总行数约 `11.85B`。按 `2 lanes × 20M` 的近期速度估算，剩余约 `6.17B` 行，约 `154` 波，预计还需要 `2.5-3.5` 小时。这个估算会随后段重复键比例、目标 merge 压力和单波导入耗时变化。

## 我会怎么记住这次经验

这次回灌的关键经验不是“并发越高越快”，而是：

1. 先用 `EXPLAIN indexes = 1` 和 `system.query_log.read_rows` 证明 cursor 命中主键裁剪；
2. 再把回灌拆成有边界的、可恢复的排序键区间；
3. 并发数只在目标复制队列、导入耗时和源端稳定性允许的范围内增加；
4. 大区间校验优先 `count()`，可疑区间再做精确唯一键校验。

这套判断也适用于其他 ClickHouse 大表迁移：先修查询形状，再谈并发。

---

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-data-export]] · [[topics/clickhouse-production-migration]] · [[topics/clickhouse-single-node-to-cluster-migration]]
