---
title: ClickHouse 复制引擎与旧表转换
type: topic
tags: [数据库, ClickHouse, ReplicatedMergeTree, 复制, 迁移]
source_count: 6
updated: 2026-04-27
---

> 在生产环境里，最好一开始就把 replicated 路径选对；从 `MergeTree` 再转 `ReplicatedMergeTree` 是可行的，但本质上属于迁移工程。

## 先说结论

如果这是**新建的生产 ClickHouse 集群**，我的默认建议是：

1. 数据库层优先使用 `ENGINE = Replicated`；
2. 需要副本容灾的数据表优先使用 `ReplicatedMergeTree` 家族；
3. 不要把“后面再转”当成默认计划。

这里第 1 点是 Operator 文档的直接建议；第 2 点是**结合 Operator 文档与复制文档做出的归纳**，因为 Operator 明确说它不负责 table data replication，而表数据复制仍由 ClickHouse 自身机制承担。

## 为什么要区分数据库引擎和表引擎

这个问题很容易被一句“生产用 replicated”说糊。

- **数据库引擎 `Replicated`**：解决 schema 和数据库定义在副本间的同步；
- **表引擎 `ReplicatedMergeTree` 家族**：解决表数据副本的一致性与恢复；
- **Operator**：帮你管理声明式集群与 schema 复制，不替代表引擎级的数据复制语义。

这意味着，哪怕你已经在 Kubernetes 里用了 Operator，真正的高可用数据表依然要认真决定是否落在 `ReplicatedMergeTree` 家族上。

## `ReplicatedReplacingMergeTree` 里有两种去重

[[sources/oneuptime-replicated-replacingmergetree]] 和 [[sources/clickhouse-issue-20867]] 放在一起，正好把 `ReplicatedReplacingMergeTree` 的标准用法和误用边界都补齐了。到了这个引擎，我不能只说“Replacing 会去重”，还必须区分几层不同机制。

第一层是 `ReplacingMergeTree` 自身的 replacement：它按 `ORDER BY` 定义的排序键识别可折叠的行，如果传了 version 列，就在同一个 key 下选择 version 最大的行。这里的关键是，version 必须真能表达新旧顺序；如果把同一个 `timestamp` 同时放进 `ORDER BY` 和 version 参数，又用 `toStartOfDay(now())` 这种日粒度值反复插入，ClickHouse 其实没有拿到一个可靠的“哪条更新”的信号。

第二层是 replicated 表的 insert deduplication：它服务的是重复 insert block 的幂等，不是业务行级去重。如果一个 cron 从多个节点反复插入同一批每日账号快照，payload 完全相同，复制层可能先把后来的 block 当成重复提交跳过，后面的 `ReplacingMergeTree` merge 逻辑根本没有机会参与。

标准建模方式是：用 `ORDER BY` 表达逻辑身份，用 version 列表达新旧顺序，用 Keeper / ZooKeeper 承担复制协调。`FINAL` 可以让查询在后台 merge 之前看到去重后的状态，`OPTIMIZE ... FINAL` 可以对分区做维护式强制合并，但它们都不能替 schema 补出缺失的版本语义。

这对建模的影响很直接：如果业务要存“每天每个账号最后状态”，我会把 `date` 这类业务粒度放进去重 key，把高精度 `created_at`、递增版本或源端 `insert_id` 作为新旧顺序或插入唯一性，而不是让 `account_name` 这种业务字段的大小关系意外决定结果。

## 已有 `MergeTree` 时有哪些迁移路径

### 1. 小表直接复制

适合数据量不大、可以接受额外写放大和迁移时长的场景：

1. 创建新的 `ReplicatedMergeTree` 表；
2. `INSERT INTO new_table SELECT * FROM old_table`；
3. 校验后切流或 rename。

优点是简单；缺点是对大表太重。

### 2. 旁路新建表，再 `ATTACH PARTITION`

这是我更偏向的大表生产路径：

1. 旁路创建 replicated 新表；
2. 用 `ALTER TABLE new_table ATTACH PARTITION ... FROM old_table` 挂入原表分区；
3. 校验计数与关键查询；
4. `RENAME TABLE` 完成切换；
5. 暂时保留旧表作为便宜回滚点。

Altinity KB 强调，这种方式大量利用硬链接，因此对大表更现实。

### 3. `DETACH` + `ATTACH ... AS REPLICATED`

这是官方给出的原地转换路径之一：

1. `DETACH TABLE test`;
2. `ATTACH TABLE test AS REPLICATED`;
3. `SYSTEM RESTORE REPLICA test`;

但有两个关键前提：

- `ATTACH` 不会自动修改 Keeper / ZooKeeper 元数据；
- 如果你是在给已有 replicated 表补 replica，本地数据会先被 detach。

所以它更像**原地切换工具**，不是自动迁移器。

### 4. `convert_to_replicated` + 重启

如果能接受重启窗口，官方也支持在数据目录下放置 `convert_to_replicated` 标记文件，让服务重启时按 replicated 方式加载。

这种方式的关键约束是：

- 依赖 `default_replica_path` 与 `default_replica_name`；
- 需要准确知道表数据目录；
- 对已有多副本场景，仍要先确认数据一致性。

### 5. 更手工的 rename / detached / attach 路线

官方复制文档保留了更底层的手工做法：rename 旧表、新建 replicated 表、把数据移到新表目录下的 `detached`，再 `ATTACH PARTITION`。这条路麻烦，但在默认路径不适配时提供了更强控制力。

## 迁移前必须先想清楚的事

1. **当前多份数据是否完全一致**：如果不一致，先同步，或者只保留一个权威源。
2. **你要的是重启窗口，还是在线旁路切换**：这决定你更像走原地转换还是旁路建表。
3. **Keeper / ZooKeeper 路径是否已准备好**：尤其是 `ATTACH` 和重启转换都依赖复制元数据语义。
4. **回滚策略是什么**：rename 保留旧表通常比直接覆盖更稳。
5. **是否已经在生产上使用 `Replicated` 数据库引擎**：否则 schema 复制和表复制会变成两套不同步的运维问题。
6. **是否误把 replicated insert deduplication 当成表内去重**：它跳过的是重复 insert block，不会替 `ReplacingMergeTree` 设计业务版本。

## 一个实用的生产建议

- **新建生产集群**：直接上 `Replicated` 数据库引擎 + `ReplicatedMergeTree` 家族。
- **已有小表**：优先考虑旁路新表 + `INSERT SELECT`。
- **已有大表**：优先考虑旁路新表 + `ATTACH PARTITION` + rename。
- **已有单机或明确维护窗口**：可评估 `ATTACH ... AS REPLICATED` 或 `convert_to_replicated`。
- **已有复杂多副本且数据可能漂移**：先做一致性治理，不要急着套转换命令。
- **需要低频 upsert 式当前状态表**：可以评估 `ReplicatedReplacingMergeTree`，但前提是 identity、version 和 `FINAL` 成本都已经被明确设计。

## 对我的启发

这几篇文档放在一起之后，一个判断变得非常稳定：**ReplicatedMergeTree 的最佳使用时机是建表时，而不是出事后。** 转换能力很重要，但它更像补救路径、演进路径和迁移路径，而不是默认开发流程的一部分。

---

来源：[[sources/clickhouse-operator-introduction]] · [[sources/altinity-converting-mergetree-to-replicated]] · [[sources/clickhouse-replicated-table-engines]] · [[sources/clickhouse-attach-as-replicated]] · [[sources/clickhouse-issue-20867]] · [[sources/oneuptime-replicated-replacingmergetree]]

相关页面：[[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-common-pitfalls]] · [[entities/clickhouse]] · [[sources/clickhouse-operator-introduction]] · [[sources/altinity-converting-mergetree-to-replicated]] · [[sources/clickhouse-replicated-table-engines]] · [[sources/clickhouse-attach-as-replicated]] · [[sources/clickhouse-issue-20867]] · [[sources/oneuptime-replicated-replacingmergetree]]
