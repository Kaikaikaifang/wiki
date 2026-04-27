---
title: ClickHouse 生产迁移
type: topic
tags: [数据库, ClickHouse, 迁移, 集群, 生产环境]
source_count: 2
updated: 2026-04-27
---

> 我现在更愿意把这次 ClickHouse 迁移理解成一场系统工程，而不是一次数据库搬家。真正的难点不在于能不能建出新集群，而在于如何在 `7 TiB` 级历史数据和持续写入面前，把新增、历史、切换和回滚边界拆清楚。

这套生产环境的起点很具体：当前仍是单实例 StatefulSet，核心表 `scalar`、`media`、`log` 还是单机 `MergeTree`；应用和写入管道都直接使用 `app.scalar`、`app.media`、`app.log` 这些逻辑表名；历史数据已经达到 `7118 GiB`，其中 `scalar` 和 `log` 又是上千亿行量级。

在这个约束下，我不再相信“旧库原地改 replicated，再逐步扩节点”是更稳的路线。它看起来渐进，实质上会把一次大迁移拆成两次高风险变更。我现在更认可的主线是：

1. 直接并行搭建目标集群。
2. 目标侧预建最终表形态。
3. 先用 `Vector` 双写守住新增写入。
4. 再用静态源批处理回灌 `T0` 之前的历史。
5. 最后只补小尾巴、对账、切读、观察，再下线旧写入。

## 当前结论

如果生产机器数不被锁死在现有 4 台节点上，我现在会把首发目标定为：

- 目标拓扑：`6 shards x 2 replicas + 3 Keeper`
- 数据节点：`12` 台，单节点约 `32 vCPU / 128 GiB / 3~4 TiB` 高性能 SSD
- Keeper：`3` 台独立节点，单节点约 `4 vCPU / 16 GiB`
- 数据节点和 Keeper 都不使用 spot / 抢占式节点
- 写入迁移使用 `Vector` 双写，双写验证通过的时刻记为 `T0`
- 目标 schema 由迁移 DDL 预建，应用自动建表必须关闭

早期我曾把 `4 shards x 2 replicas` 视为合理起点，但那是在“机器数可能受限”的前提下。现在既然生产资源可以按迁移目标重新规划，`6 x 2` 更符合未来一两年的稳定运行：它把单 shard 单副本的数据量压到约 `1186 GiB`，给 merge、回灌临时放大、热点项目倾斜和后续增长留出余量，也降低了上线不久再次 reshard 的概率。

`dev-admin` 的验证环境可以缩资源，但不应该缩掉语义。理想状态是也跑 `6 x 2 + 3 Keeper`；如果共享集群配额不足，最低我会退到 `3 x 2 + 3 Keeper`。我不愿意退成单 shard 或单 replica，因为这次要验证的不是 ClickHouse 能不能启动，而是 `Distributed` 写入、shard key 路由、复制恢复、双写、回灌和对账能不能一起成立。

## 目标表形态

目标侧应该一次建成最终访问模型，而不是继续让应用直写本地表：

- 数据库使用 `Replicated` 数据库引擎；
- 本地表命名为 `scalar_local`、`media_local`、`log_local`；
- 本地表使用 `ReplicatedMergeTree`；
- 对外继续保留 `app.scalar`、`app.media`、`app.log`；
- 这三个逻辑表在目标侧改成 `Distributed` 表；
- 分片键优先使用 `cityHash64(projectId)`；
- 分区键优先按 `createdAt` 做月分区。

这里我最看重的是“逻辑表名不变”。应用和写入链路已经绑定这些表名，如果迁移时顺手改访问模型，风险会从数据库层外溢到应用层、配置层和观测层。更稳的做法是让业务继续使用熟悉的逻辑表名，只把背后的物理实现换成 `Distributed -> ReplicatedMergeTree`。

分片键优先围绕 `projectId`，不是因为它在概念上好看，而是因为当前查询大多先按 `projectId + experimentId` 收敛，再做聚合、取最新值、拉日志或拼媒体。`projectId` 是读路径的第一层边界。以后如果少数超大项目把某个 shard 压成热点，再考虑升级成 `cityHash64(projectId, experimentId)`，但迁移阶段我不想为了“分布更漂亮”提前牺牲查询局部性。

## 自动建表必须关掉

当前应用连接 ClickHouse 时会自动建表，而且建出来的是裸 `MergeTree`。在旧单机时代，这只是开发便利；迁到新集群后，它会变成污染目标 schema 的开关。

我会把这件事改成显式配置：

- 新增 `database.auto_create_tables`；
- 默认值可以保留 `true`，兼容本地开发和旧单机；
- 新集群环境必须显式设成 `false`；
- 目标库、`*_local` 表和 `Distributed` 表必须由迁移 DDL 预建。

这是小改动，但优先级很高。否则“预建最终 schema”“统一逻辑表名”“避免错误本地表落库”都会变得很脆弱。

## T0 双写是硬前置

我现在会把双写前置到迁移水位 `T0`，而不是等历史复制结束后再开启。原因很简单：如果先回灌、后双写，回灌窗口里的新增数据会重新长成一个大 gap，最后又要补一场可能很大的增量迁移。

正式顺序应该是：

1. 目标 ClickHouse 集群 Ready。
2. `Vector` 同时写源端和目标端。
3. 发送唯一实时事件，确认 `scalar`、`media`、`log` 三张表都同时落到新旧两边。
4. 把这次端到端验证通过的时刻记为 `T0`。
5. 后续历史回灌只处理 `T0` 之前的数据。

这里的关键不是配置已经 apply，而是唯一事件已经在两边查到。之前在 `dev-admin` 里就踩过一个很像生产问题的坑：`scalar` 和 `log` 双写正常，但 `media` 只进了源端。最后修复方式是给目标端 sink 拆出独立 transform，也就是 `clean_scalar_for_target`、`clean_media_for_target`、`clean_log_for_target`，不再复用源端 transform 输出。

这个经验让我更确信：`T0` 只能建立在真实双写链路验证之后，不能建立在配置发布时间上。

## 历史回灌主路径

`remote()` 可以证明目标端能读源端，也适合小表验证、抽样对账和局部补洞，但我不会再把它当生产主回灌方案。它把源端读取、目标端写入、失败恢复和资源压力绑进一条长查询里；在 `dev-admin` 验证中，它已经暴露过目标内存、磁盘扩容和中断后半截批次清理的问题。

正式主路径应该是批处理数据管道：

1. `T0` 之后的新写入由 `Vector` 双写兜住。
2. `T0` 之前的历史从静态源导出到对象存储。
3. 目标端从对象存储按批次并行导入。
4. 每个批次都有状态、重试和对账记录。
5. 全部批次完成后做全局总账和热点项目抽样校验。

如果源 ClickHouse 的数据本来就在云盘上，并且已经有云盘快照，我会优先用快照恢复出的离线 ClickHouse 做导出源，而不是长时间扫线上源库。但这条边界也必须说清楚：快照是导出源，不是最终迁移结果。目标是新的分片布局和 `Distributed -> ReplicatedMergeTree` 形态，旧单机快照不能替代按新 shard key 重写数据。

对象存储中转的价值也不只是“多了一层文件”。它把源端读和目标端写解耦：导出可以按源端节奏推进，导入可以按目标端负载推进；导入失败时不必重扫源库；导出的 `Native + zstd` 文件还能复用于校验和补跑。

## 回灌控制面

这条路径已经在 `dev-admin` 里证明能跑通，但“能跑通”和“能无人值守地跑完整个生产历史”不是一回事。真正需要补厚的是最小控制面。

我会把控制面固定在几件事上：

- `manifest` 自动生成：从源端拉 `projectId`、`experimentId`、时间窗和粗略行数，生成标准批次；
- 状态表驱动执行：用 `migration_meta.backfill_batches` 作为唯一事实来源；
- Job 自动领取批次：导出、导入和对账任务写回状态、错误和重试次数；
- 空批次自动跳过：例如 `13 B` 的空压缩对象不进入导入阶段；
- 导出和导入目录隔离：避免对象存储工具因同名覆盖进入交互流程；
- 每批自动对账：至少校验 `count()` 和一个轻量聚合，通过后才标记 `verified`；
- 并发按表和 shard 控制：观察 `system.replicas`、`system.merges`、磁盘水位和双写 sink 指标，而不是只看 Job 数。

状态表不需要一开始就做成复杂平台，但字段必须稳定，例如 `batch_id`、`table_name`、`project_id`、`experiment_id`、`time_start`、`time_end`、`export_path`、`status`、`retry_count`、`last_error`、`created_at`、`updated_at`、`verified_at`。只要这个状态面稳定，后续不管用 shell、CronJob 还是调度器，都不会重新发明一套迁移状态。

## 生产量级下要分表治理

最近的真实规模判断让我不再接受三张表共用一套回灌策略：

- `app.scalar`：约 `2973.95 亿` 行；
- `app.log`：约 `1287.73 亿` 行；
- `app.media`：约 `1.86 亿` 行。

`media` 可以继续沿用“快照恢复源 -> OSS -> 批次导入”，重点是把状态、重试和对账自动化。`log` 和 `scalar` 则应该升级成 shard-aware 回灌：主批次从小时清单升级为 `date x target_shard`，导出阶段预先计算目标 shard，导入阶段直接写对应 shard 的 `*_local`，第二副本交给复制追平。

如果业务允许，我最推荐的生产切换策略是“热数据优先切流，深历史后台慢迁”。它直接取消了“所有历史必须先完全回灌，新集群才有资格接流量”这个最重约束。

如果业务硬性要求全历史先入新集群，那就不要继续加长当前小时级脚本，而是直接升级成回灌平台：

- 多快照克隆并行导出；
- `date x target_shard` 主批次；
- 超阈值批次自动 split；
- 导入阶段直写 `*_local`；
- 调度器按表和 shard 做配额、退避和重试。

我现在会把这三项作为最优先升级：按 shard 直写 `*_local`、多快照克隆并行导出、`date x shard + 自动 split`。它们共同把当前已经验证可行的数据管道，升级成能承受生产窗口的执行系统。

## 被降级的路线

### `remote()`

`remote()` 已经完成了它该完成的职责：证明目标端能读取旧源，证明小表和部分时间窗能写入目标端，也提前暴露了内存、磁盘和中断恢复问题。它应该保留为验证、抽样对账和补洞工具，不再承担生产主回灌。

### `clickhouse-copier`

`clickhouse-copier` 纸面上很诱人，因为它能从静态源读取、能重分片、能用 Keeper 协调 worker。但在 `dev-admin` 的验证里，它已经连续暴露出不适合作为正式主路径的边界：

- 自建 `*_piece_*` 中间表会和目标侧 `Replicated` 数据库的 DDL 传播语义冲突；
- 即便降级到普通 staging 库，也会在空分区键等场景里出现兼容问题；
- `24.3` 工具到 `26.3` 目标链路上出现过协议级异常，例如 `Unexpected packet from server (expected EndOfStream or Exception, got Progress)`。

它仍然可以作为离线实验工具，但不能再作为正式生产历史回灌主引擎。关于它的“一致复制需要 source tables and partitions 不变化”这句话，我会保留一个澄清：约束的是 copier 正在读取的那份 source，而不是整个生产系统必须停写。所以理论上可以让 copier 读取 `T0` 附近快照恢复出的静态源，同时线上继续由 `Vector` 双写承接新增。但即便这样，它也只是受控实验选项，不是当前正式路线。

### `ATTACH` 旧历史

直接把旧单机历史 `attach` 成某个 replicated shard，也不能等价成完成了按 `projectId` 分片。分片键决定的是未来写入路由，不会回头观察某个项目的历史眼下在哪个 shard。

如果旧历史整体躺在 shard1，而 `cityHash64(projectId)` 判断某个项目的新数据应该进 shard2，这个项目就会变成“历史在 shard1、新增在 shard2”。这破坏了按 `projectId` 分片原本应该承诺的局部性，也没有真正消灭 reshard，只是把它推迟到未来。

所以 `attach + replicated` 最多是“先把单机表变多副本”的过渡手段，不能被误认成最终的按键分片迁移。

## 已验证到什么程度

本地验证已经证明了这条迁移路径的结构正确性：用 mock 单节点 ClickHouse 做源端，用 operator 起 `4 shards x 2 replicas + 3 Keeper` 的目标集群，目标侧预建 `Replicated` 数据库、`ReplicatedMergeTree` 本地表和 `Distributed` 逻辑表，再用 `Vector` 双写模拟新增，最后只回灌 `T0` 之前的历史。

在 ClickHouse `26.3` 重跑后，DDL 纪律也更清楚了：

- `Replicated` 数据库不再依赖实验开关；
- `CREATE DATABASE ... ENGINE = Replicated` 可以用 `ON CLUSTER`；
- 数据库建好后，表级 DDL 不再继续用 `ON CLUSTER`，而是让 `Replicated` 数据库传播元数据；
- 目标实例上的 `scalar/media/log` 和对应 `*_local` 表都能稳定存在；
- 副本检查保持 `total_replicas=2`、`active_replicas=2`、`queue_size=0`、`absolute_delay=0`。

共享集群 `dev-admin` 又补了一层更接近真实环境的验证。目标集群最终能在 `tenant-kaikai` Ready，但入口问题主要卡在镜像分发和调度面：需要把 ClickHouse server 和 Keeper 镜像同步到公开 ACR，版本显式 pin 到 `26.3`，并给高性能节点补上 toleration。这个经验提醒我，迁移路径从本地走向共享集群时，架构正确性只是第一层，镜像、taint、PVC 和资源请求同样会决定它能不能真正落地。

历史回灌数据面也已经过了比 demo 更强的验证：从快照恢复源导出 `Native + zstd` 到 OSS，再由目标端导入 `Distributed` 表；`2026-04-22` 的 `18` 个非空小时、`2026-04-19` 的 `10` 个有效小时，以及 `2026-04-18` 连续重负载日前 `12` 个小时，都验证过小时级批次、对象存储中转和逐批对账的可行性。

这些结果支撑的是“路径方向成立”，不是“已经可以直接无人值守跑完整个生产历史”。后者还需要前面说的控制面和 shard-aware 升级。

## 执行顺序

我会把正式迁移排成六段：

1. 准备目标集群：搭建目标拓扑，预建 `Replicated` 数据库、`*_local` 表和 `Distributed` 逻辑表。
2. 改应用和写入管道：发布 `database.auto_create_tables`，目标环境关闭自动建表，为 `Vector` 增加目标 sink。
3. 冻结 `T0`：正式开启双写，发送唯一事件，确认三张表在新旧两边都可见。
4. 回灌历史：使用静态源和对象存储中转回灌 `T0` 之前的数据，批次状态、重试和对账全部落表。
5. 切读不切写：读请求先切到新集群，双写继续保留，观察查询结果、复制状态和后台负载。
6. 下线旧写入：停掉旧 sink，保留旧集群只读观察期，通过后再退役。

真正的切换信号不是某条脚本退出为零，而是这些条件同时成立：

- 三张表新旧两边总行数和关键聚合一致；
- 热门项目的业务查询结果一致；
- 新集群 `system.replicas` 没有复制堆积；
- 后台 merge 没有把资源顶满；
- `Vector` 新 sink 的失败率、延迟和 buffer 占用稳定；
- 读流量切到新集群后没有明显长尾和查询异常。

## 对我的提醒

这次最值得我记住的，不是某个 ClickHouse 参数，而是规模改变了问题性质。到了 `7 TiB` 和千亿行级别，迁移就不再是 DDL 设计题，而是跨越表结构、写入入口、静态历史源、批次控制面、资源余量和切换纪律的联合工程。

我会继续坚持一个原则：不要把版本升级、分片重构、去重语义调整和迁集群塞进同一个窗口。迁移本身已经足够难，真正应该追求的是主路径短、状态可恢复、每一步都能独立对账。

---

来源：[[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-replicated-engines-and-conversion]]

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-operator-installation-on-shared-clusters]] · [[topics/clickhouse-common-pitfalls]]
