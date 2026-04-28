---
title: ClickHouse 生产迁移
type: topic
tags: [数据库, ClickHouse, 迁移, 集群, 生产环境]
source_count: 6
updated: 2026-04-28
---

> 我现在更愿意把这次 ClickHouse 迁移理解成一场生产系统工程，而不是一次数据库搬家。真正的难点不在于能不能建出新集群，而在于如何在 `7 TiB` 级历史数据和持续写入面前，把新增、历史、切换和回滚边界拆清楚，并且不把未经生产验证的草图带进执行路径。

这套生产环境的起点很具体：当前仍是单实例 StatefulSet，核心表 `scalar`、`media`、`log` 还是单机 `MergeTree`；应用和写入管道都直接使用 `app.scalar`、`app.media`、`app.log` 这些逻辑表名；历史数据已经达到 `7118 GiB`，其中 `scalar` 和 `log` 又是上千亿行量级。

在这个约束下，我不再相信“旧库原地改 replicated，再逐步扩节点”是更稳的路线。它看起来渐进，实质上会把一次大迁移拆成两次高风险变更。我现在更认可的主线是：

1. 直接并行搭建目标集群。
2. 目标侧预建最终表形态。
3. 先用 `Vector` 双写守住新增写入。
4. 再用静态源批处理回灌 `T0` 之前的历史。
5. 最后只补小尾巴、对账、切读、观察，再下线旧写入。

这里有一条总原则必须放在最前面：**所有方案设计都面向生产执行，不保留“先用草图试试看”的隐含前提。** 文档里可以记录历史验证和被否定路线，但进入主路径的设计必须满足三件事：规则来自目标生产集群的真实配置，失败后能恢复，结果能独立对账。

## 当前结论

如果生产机器数不被锁死在现有 4 台节点上，我现在会把首发目标定为：

- 目标拓扑：`6 shards x 2 replicas + 3 Keeper`
- 数据节点：`12` 台，单节点约 `32 vCPU / 128 GiB / 3~4 TiB` 高性能 SSD
- Keeper：`3` 台独立节点，单节点约 `4 vCPU / 16 GiB`
- 数据节点和 Keeper 都不使用 spot / 抢占式节点
- 写入迁移使用 `Vector` 双写，双写验证通过的时刻记为 `T0`
- 目标 schema 由迁移 DDL 预建，应用自动建表必须关闭
- 当前生产资源配置入口收敛到 `/Users/kaikai/projects/test/test-migration/production-v3`

早期我曾把 `4 shards x 2 replicas` 视为合理起点，但那是在“机器数可能受限”的前提下。现在既然生产资源可以按迁移目标重新规划，`6 x 2` 更符合未来一两年的稳定运行：它把单 shard 单副本的数据量压到约 `1186 GiB`，给 merge、回灌临时放大、热点项目倾斜和后续增长留出余量，也降低了上线不久再次 reshard 的概率。

`dev-admin` 的验证环境可以缩资源，但不应该缩掉语义。理想状态是也跑 `6 x 2 + 3 Keeper`；如果共享集群配额不足，最低我会退到 `3 x 2 + 3 Keeper`。我不愿意退成单 shard 或单 replica，因为这次要验证的不是 ClickHouse 能不能启动，而是 `Distributed` 写入、shard key 路由、复制恢复、双写、回灌和对账能不能一起成立。

## 目标表形态

目标侧应该一次建成最终访问模型，而不是继续让应用直写本地表：

- 数据库使用 `Replicated` 数据库引擎；
- 本地表命名为 `scalar_local`、`media_local`、`log_local`；
- `log_local` 使用 `ReplicatedMergeTree`；
- `scalar_local` 和 `media_local` 使用 `ReplicatedReplacingMergeTree`，用于收敛重复打点；
- 对外继续保留 `app.scalar`、`app.media`、`app.log`；
- 这三个逻辑表在目标侧改成 `Distributed` 表；
- 分片键优先使用 `cityHash64(projectId)`；
- 分区键优先按 `createdAt` 做月分区。

这里我最看重的是“逻辑表名不变”。应用和写入链路已经绑定这些表名，如果迁移时顺手改访问模型，风险会从数据库层外溢到应用层、配置层和观测层。更稳的做法是让业务继续使用熟悉的逻辑表名，只把背后的物理实现换成 `Distributed -> ReplicatedMergeTree / ReplicatedReplacingMergeTree`。

分片键优先围绕 `projectId`，不是因为它在概念上好看，而是因为当前查询大多先按 `projectId + experimentId` 收敛，再做聚合、取最新值、拉日志或拼媒体。`projectId` 是读路径的第一层边界。以后如果少数超大项目把某个 shard 压成热点，再考虑升级成 `cityHash64(projectId, experimentId)`，但迁移阶段我不想为了“分布更漂亮”提前牺牲查询局部性。

## `scalar` 和 `media` 的去重引擎

`scalar` 和 `media` 可以考虑在目标侧直接使用 `ReplicatedReplacingMergeTree`，动机是解决重复打点：同一个实验、同一个指标、同一个 `step` 被重复写入时，目标表最终只保留一条有效记录。这个判断只适用于 `scalar` / `media` 这类有明确业务身份的事实表，不应该顺手扩展到 `log`。日志的重复通常更像真实事件流问题，贸然折叠会改变排障和审计语义。

这里最关键的是把“去重身份”和“版本信号”提前设计清楚。`ORDER BY` 不能只照着查询过滤列堆字段，它在 `ReplacingMergeTree` 里同时承担“哪些行代表同一个逻辑对象”的身份定义。对重复打点场景，我会把去重 key 理解成类似：

- `projectId`
- `experimentId`
- `metric` / `metricName`
- `step`
- 必要时再加能区分数据类型、series、variant 或 media 维度的业务字段

version 列则必须表达确定的新旧顺序，例如高精度 `createdAt`、采集端单调版本，或服务端生成的 ingestion version。不能把低精度时间同时放进 `ORDER BY` 和 version，也不能让一个没有单调含义的业务字段决定谁留下。

这件事要带着两个 ClickHouse 边界来做。

第一，`ReplicatedReplacingMergeTree` 的表内 replacement 是后台 merge 收敛语义，不是写入时唯一约束。重复行在一段时间内可能同时存在；需要强一致去重视图的查询，要显式使用 `FINAL`，或者由上层读模型 / 物化结果承担去重成本。把 `FINAL` 当默认大范围查询开关，通常会把写入侧省下来的复杂度转嫁到查询侧。

第二，replicated insert deduplication 和业务行级去重不是一回事。前者跳过的是重复 insert block，服务的是重试幂等；后者按 `ORDER BY` 身份折叠表内多行。重复打点如果来自不同 block、不同时间或不同 producer，不能指望复制层自动理解业务重复。

所以这个引擎切换可以进入目标 schema 设计，但必须作为生产 schema 决策一次性固定下来，而不是回灌到一半再改。回灌对账也要同步改口径：对 `scalar` / `media`，除了原始导入行数，还要验证去重 key 级别的最终记录数和关键聚合；否则会出现“源端重复行完整导入了，但目标最终语义到底对不对”说不清的状态。

但有一个生产边界不能模糊：**回灌系统不能自己发明 shard 路由规则。** `cityHash64(projectId) % shard_count` 这类手写推导不进入方案设计、脚本、manifest 或执行手册。真实的目标 shard 必须来自目标 `Distributed` 表的实际 sharding key、`system.clusters` 里的 shard 顺序与 weight，或者更简单地交给目标 `Distributed` 表自己路由。

如果为了吞吐选择直写 `*_local`，那就必须先把 ClickHouse 的路由规则固化成可测试的生产函数：读取目标集群配置，生成 `projectId -> shard` 的映射，并用唯一测试行通过 `Distributed` 表实际插入后反查本地表落点，证明 planner 与 ClickHouse 路由一致。没有这一步，直写 `*_local` 就不能进入正式回灌。

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

[[sources/oneuptime-clickhouse-export-file-formats]] 正好补上了这条路径里的格式和通道边界：`FORMAT` 决定序列化，`clickhouse-client`、HTTP、`INTO OUTFILE` 和 `s3()` 表函数决定结果落点。对这次 ClickHouse 到 ClickHouse 的历史回灌，我会继续把 `Native + zstd` 作为优先格式；`Parquet + zstd` 更适合数据湖或跨系统消费，不应该因为“更通用”就替代迁移主路径里的高效回灌格式。

这里还要特别记住 `INTO OUTFILE` 的客户端侧语义。文件写在运行客户端的机器上，而不是 ClickHouse server 上；HTTP 接口也不支持 `INTO OUTFILE`。生产回灌如果目标是 OSS 中转层，更稳的做法是让 runner 明确管理本地临时文件和上传，或者用 `s3()` 表函数直接写对象存储，但无论哪条路都必须把对象路径、压缩方式、重试和对账状态落进同一张批次表。

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

我会刻意让控制面保持简单：一张状态表、一份 manifest、一类 runner、三类动作，分别是导出、导入和对账。复杂度不应该藏在临时脚本里，也不应该靠人工记忆状态。批次可以被 split，Job 可以重试，但状态机本身必须短，能被值班的人一眼看懂。

## 三张表使用统一回灌方案

最近的真实规模判断仍然值得保留，因为它解释了为什么回灌平台必须足够强：

- `app.scalar`：约 `2973.95 亿` 行；
- `app.log`：约 `1287.73 亿` 行；
- `app.media`：约 `1.86 亿` 行。

但我现在不再把这个差异理解成“三张表要走三套方案”。更稳的做法是反过来：**三张表使用同一个回灌控制面、同一个批次模型、同一套状态机和同一套对账语义，只在参数上体现表规模差异。**

也就是说，`scalar`、`log`、`media` 都走同一条主路径：

1. 从静态源按标准 manifest 导出到 OSS；
2. 批次维度统一使用生产确认过的切分维度，优先围绕日期、水位和目标 shard；
3. 目标 shard 的计算必须来自目标集群真实路由规则，不能使用手写取模草图；
4. 默认导入目标是 `Distributed` 表，让 ClickHouse 负责路由；
5. 只有当 planner 已经通过生产等价性验证时，才允许直写对应 shard 的 `*_local`，第二副本交给复制追平；
6. 每批进入同一张状态表，经过同一套重试、split、对账和完成判定。

这样做的价值，是避免迁移系统自己变成三套小系统。三张表的数据量不同，但失败恢复、并发控制、对象路径、批次状态、对账口径和最终切换信号应该一致。否则到了真实生产窗口，最容易出问题的不是某条 SQL，而是不同表各自有一套执行纪律，排障和恢复时无法共用判断。

表规模差异仍然要体现在参数层：

- `scalar` 可以给更低并发、更小 split 阈值和更保守的导入配额；
- `log` 可以按实际写入密度调高并发，但仍然服从 shard 级限流；
- `media` 可以更快跑完，但不因此绕过统一状态表和统一对账。

我会把这里的边界说清楚：**统一方案不是三张表完全同速同批大小，而是三张表共享同一个控制面和执行协议。** 差异只应该是配置，不应该是架构。

现在的生产约束要更硬：**必须历史数据完全回灌后，新集群才有资格接管流量。** 这个前提下，我不再建议把已删除项目 / 实验从回灌主路径里分叉成 `archive-only`。那样会让切换验收变成两套口径：一套证明新集群可服务，一套证明 OSS 归档完整。生产上更简单的方案是全量历史都进入新集群，接管流量前只做一类完成判定：源端该迁的数据已经导入目标并对账通过。

存储成本应该交给目标集群的冷热分层去解决。[[sources/clickhouse-external-disks-for-storing-data]] 和 [[sources/clickhouse-separation-storage-compute]] 给出的底层原语已经足够明确：ClickHouse 可以通过 storage policy、对象存储和本地缓存 / 热盘组合，把容量层和性能层拆开。对这次迁移来说，更合适的生产判断是：**数据完整性由统一回灌保证，长期成本由冷热分层承担。**

这里的顺序必须说清楚：**回灌阶段的 OSS 是中转层，不是冷层本身。** 历史数据仍然先从静态源导出到 OSS，再由导入任务按批写入目标 ClickHouse 集群。冷热分层的数据沉积是导入后的后续过程，由目标表的 storage policy、分区 / TTL 规则、后台移动和访问热度共同决定，而不是 manifest 在回灌阶段决定某批数据“直接进冷层还是热层”。

已删除项目和实验仍然值得从 PostgreSQL 导出 `project cuid` 与 `experiment cuid` 清单，但这份清单不再决定“导不导入”。它的角色应该降级为三件事：

- 估算冷数据占比，帮助规划热盘和对象存储容量；
- 验证这些资源在迁移后确实不会成为热查询主路径；
- 为后续冷层观测提供标签，例如按已删除资源抽样检查访问频率和存储落点。

这里还要避免一个误解：ClickHouse 不会天然因为某个项目在 PostgreSQL 里被删除，就自动知道这批历史数据应该进冷层。冷热分层必须通过生产可验证的存储策略来表达。最简单的起点，是按时间和分区让旧数据逐步落到冷层；删除资源因为长期不再被访问，即使仍在新集群可查询，也会自然停留在对象存储 / 冷层，不再持续占用宝贵热盘或缓存。

[[sources/clickhouse-cold-hot-storage]] 给了这件事一个更接近执行手册的版本：目标表可以先挂上包含本地热盘、OSS 冷盘和 cache disk 的 storage policy，再用业务时间字段上的 TTL move 把旧 part 推到 cold volume。`production-v3` 里我已经把这层固化成 `00-hot-cold-storage.example.yaml`：`default` disk 做热层，OSS 做 `cold_oss`，外面包一层 `s3_cache`，再暴露为 `hot_cold_policy`。

TTL 窗口也应该跟着生产项目生命周期数据更新，而不是继续沿用保守的 `180d`。这批统计里，总项目数 `139,067`；单实验项目占 `25.86%`，多实验但生命周期 `<1d` 占 `34.54%`，两者合计 `60.40%`；生命周期 `<=7d` 的项目占 `77.92%`；生命周期 `>30d` 只剩 `10.10%`，`>90d` 是 `3.58%`，`>180d` 是 `1.03%`，`>=365d` 只有 `43` 个项目。基于这组分布，我现在把首版生产 TTL 定为 `createdAt + 30 DAY TO VOLUME 'cold'`，并且不设置删除 TTL。

我没有直接压到 `7d`，因为项目生命周期不是查询访问热度。`30d` 已经覆盖接近 `90%` 项目的完整生命周期，同时能把绝大部分长尾历史从热盘移走；它比 `180d` 更符合成本目标，又比 `7d` 更稳。后续如果查询日志证明 `media` 或 `log` 的冷访问更低，可以单独把这些表收紧到 `7d` 或 `14d`，但首版迁移不应该把三张表拆成三套 TTL 纪律。

这里的重点不是照抄某个 `app.log` 示例，而是把几条生产检查固定下来：

- OSS endpoint 必须按云厂商要求使用可工作的 S3 兼容形式；
- `system.disks` 和 `system.storage_policies` 要能看到冷盘、缓存盘和策略；
- 表要显式 `MODIFY SETTING storage_policy`，不能只把配置文件挂进容器；
- TTL move 的落点要通过 `system.parts.disk_name` 验证；
- 冷数据首次查询、缓存后查询、热数据查询都要分别压测。

这也补强了我对迁移顺序的判断：冷热分层是导入后数据沉积和长期成本治理机制，不是回灌控制面的替代品。它可以让全量历史进入新集群后逐步沉到 OSS，但不能用来绕开“所有历史批次都导入、对账、验证”的切流门槛。

因此正式生产路径不再有“热数据先切、深历史后台慢迁”，也不引入 `archive-only` 分叉，而是直接升级成统一的生产级回灌平台：

- 多快照克隆并行导出；
- 以真实路由规则确认过的目标 shard 作为主批次维度之一；
- 超阈值批次自动 split；
- 所有批次默认导入 `Distributed` 表，只有在路由等价性验证通过后才直写 `*_local`；
- 目标表配置生产冷热分层策略，让旧数据和长期未访问数据在导入后逐步沉到低成本冷层；
- 调度器按表和 shard 做配额、退避和重试。

我现在会把这三项作为最优先升级：生产路由规则固化与验证、多快照克隆并行导出、基于真实 shard 维度的自动 split。它们共同把当前已经验证可行的数据管道，升级成能承受生产窗口的统一执行系统。

`production-v3` 资源包把这条主线压成了当前最小可执行形态：目标集群 manifest、冷热分层配置、目标 schema、`Vector` 双写占位、从 `VolumeSnapshot` 克隆出的静态源 ClickHouse、统一回灌 runtime、runner / verifier 入口，以及最小状态表。这里最重要的边界是：静态源来自 `T0` 附近快照恢复出的临时 ClickHouse，供导出任务读取；它不是最终迁移结果，也不承担线上写入。回灌默认写 `Distributed` 表，只有 `route_equivalence_checks` 证明 planner 与 ClickHouse 实际路由一致后，才允许开启直写 `*_local`。

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

`production-v3/validation/dev-admin.yaml` 已经完成一轮更贴近生产路径的缩配验证：目标侧跑 `3 shards x 2 replicas + 3 Keeper`，ClickHouse 和 Keeper 都显式声明 `dataVolumeClaimSpec`，验证盘使用 `disk-essd-auto-delete`；静态源通过阿里云快照 `s-bp1b3lo6gyodshti9o0a` 恢复成 `static-source-clickhouse-0`，并用 StatefulSet 的 PVC retention 约束跟随实例释放。冷热分层也不再复用回灌中转 bucket，而是使用独立的 `swanlab-clickhouse-cold-layer.oss-cn-hangzhou-internal.aliyuncs.com`。这轮验证里真正有价值的坑是：OSS Secret 不能写进资源包，只能从运行环境同步；验证盘只有 `20Gi` 时，`s3_cache.max_size` 必须低于文件系统可用容量，否则 ClickHouse 会因为 cache 容量等于磁盘容量而启动失败。

验证结果是正向的：目标集群 `6` 个 ClickHouse Pod、`3` 个 Keeper Pod 全部 Ready；`system.disks` 能看到 `cold_oss` 与 `s3_cache`，`hot_cold_policy` 的热层 / 冷层符合预期；一条测试 part 可以 `MOVE PARTITION ... TO VOLUME 'cold'` 并落到 `s3_cache`；目标 schema 能创建 `app` 的三张 `Distributed` 表和三张 replicated 本地表，复制队列为 `0`，活跃副本为 `2/2`；目标 Pod 也能通过 `readonly` 用户连接快照恢复出的静态源。到这里，资源包已经不只是规划草案，而是具备了可以继续推进回灌 runner 与对账任务的验证基线。

历史回灌数据面也已经过了比 demo 更强的验证：从快照恢复源导出 `Native + zstd` 到 OSS，再由目标端导入 `Distributed` 表；`2026-04-22` 的 `18` 个非空小时、`2026-04-19` 的 `10` 个有效小时，以及 `2026-04-18` 连续重负载日前 `12` 个小时，都验证过小时级批次、对象存储中转和逐批对账的可行性。

这些结果只能说明早期验证材料解释了为什么选择这条路，不能替代生产方案本身。正式执行仍然必须以生产控制面、真实路由规则、可恢复状态和独立对账为准；任何只在验证环境里成立、但没有被固化成生产规则的做法，都应该留在历史记录里，而不是进入主路径。

## 执行顺序

我会把正式迁移排成八段：

1. 准备目标集群：搭建目标拓扑，预建 `Replicated` 数据库、`*_local` 表和 `Distributed` 逻辑表。
2. 配置冷热分层：为目标表确认 storage policy、热盘 / 冷层容量和对象存储路径；首版 TTL 使用 `createdAt + 30 DAY TO VOLUME 'cold'`，这一步只准备导入后的数据沉积规则，不改变“先导出至 OSS 中转，再按批导入集群”的回灌顺序。
3. 改应用和写入管道：发布 `database.auto_create_tables`，目标环境关闭自动建表，为 `Vector` 增加目标 sink。
4. 冻结 `T0`：正式开启双写，发送唯一事件，确认三张表在新旧两边都可见。
5. 回灌全量历史：使用静态源和 OSS 中转处理 `T0` 之前的数据，所有批次按行导入新集群，批次状态、重试和对账全部落表。
6. 历史闭环验收：确认所有批次都进入 `verified`，并抽样检查已删除项目 / 实验是否按冷热策略落入低成本存储路径。
7. 切读不切写：读请求先切到新集群，双写继续保留，观察查询结果、复制状态和后台负载。
8. 下线旧写入：停掉旧 sink，保留旧集群只读观察期，通过后再退役。

真正的切换信号不是某条脚本退出为零，而是这些条件同时成立：

- 三张表新旧两边总行数和关键聚合一致；
- 已删除项目 / 实验的历史数据仍可在新集群查询，但应按冷热策略落入低成本存储路径；
- 热门项目的业务查询结果一致；
- 新集群 `system.replicas` 没有复制堆积；
- 后台 merge 没有把资源顶满；
- `Vector` 新 sink 的失败率、延迟和 buffer 占用稳定；
- 读流量切到新集群后没有明显长尾和查询异常。

## 对我的提醒

这次最值得我记住的，不是某个 ClickHouse 参数，而是规模改变了问题性质。到了 `7 TiB` 和千亿行级别，迁移就不再是 DDL 设计题，而是跨越表结构、写入入口、静态历史源、批次控制面、资源余量和切换纪律的联合工程。

我会继续坚持一个原则：不要在迁移执行过程中临时追加新的语义变更。`scalar` / `media` 如果要切到 `ReplicatedReplacingMergeTree`，它必须在目标 schema 预建阶段就完成 key、version、查询口径和对账口径设计；一旦进入正式回灌，就不要再边迁边改引擎语义。迁移本身已经足够难，真正应该追求的是主路径短、状态可恢复、每一步都能独立对账。

---

来源：[[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[sources/oneuptime-replicated-replacingmergetree]] · [[sources/clickhouse-issue-20867]] · [[sources/clickhouse-cold-hot-storage]] · [[sources/oneuptime-clickhouse-export-file-formats]]

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-operator-installation-on-shared-clusters]] · [[topics/clickhouse-common-pitfalls]] · [[topics/clickhouse-data-export]] · [[sources/clickhouse-cold-hot-storage]] · [[sources/oneuptime-clickhouse-export-file-formats]]
