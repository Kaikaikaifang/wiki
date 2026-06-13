---
title: 整体综述
type: overview
tags: [方法论, 知识管理]
source_count: 50
updated: 2026-06-13
---

这份 wiki 越往后写，我越清楚它不是“资料仓库”，而更像一条不断长出来的思考主线。起点当然是 [[topics/llm-wiki-pattern]]：Karpathy 提醒我，真正有复利的不是一次次对着原始资料发问，而是把理解编译进一个会持续演化的知识系统。

但写到今天，这个系统已经明显不只是在谈知识管理。我能看到几条越来越清晰的技术主线在彼此靠拢：一条是 agent 如何设计、分层与运行；一条是搜索如何在本地、可迁移的前提下扩展；另一条则是数据库系统如何把“查询意图”真正翻译成高性能的访问路径。下面这部分不是冷冰冰的目录，而更像我最近这段时间在反复咀嚼的几组问题。

## 核心主题

目前 wiki 围绕一个核心方法论展开：**[[topics/llm-wiki-pattern]]**——用 LLM 增量构建并维护持久知识库，替代每次从零推导的 RAG 检索。

这既是本 wiki 的构建方式，也是第一个被记录的知识对象。随着资料规模增长，wiki 也开始引入第二条基础设施主线：**[[topics/local-first-search]]**，用于在保持 markdown 原生与本地优先前提下扩展检索能力。

最近加入的三篇 Anthropic 文章，则把视角从“知识库如何积累”扩展到“agent 如何可靠执行与扩展”：[[sources/building-effective-ai-agents]] 解释 workflow 与 agent 的边界，[[sources/how-we-built-our-multi-agent-research-system]] 讨论多智能体研究系统何时值得采用，[[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]] 则进一步落到长程 agent 的运行时架构、恢复与安全边界。

这次新增的 [[sources/use-the-index-luke]] 则把 wiki 的技术主题进一步落到经典数据库工程：它不是讨论 AI 系统，而是讨论**应用查询如何通过索引、执行计划与访问路径设计获得稳定性能**。这条线把“系统如何思考与执行”扩展成了“数据层如何被高效访问”，新增了 [[topics/sql-indexing]]、[[topics/query-shape-and-index-usage]]、[[topics/sql-execution-plans]]、[[topics/sql-join-performance]] 等一组更底层的性能主题。

新摄入的 [[sources/clickhouse-query-cache]] 则把数据库性能视角再往前推一步：除了通过索引减少扫描，还可以在分析型场景里**复用已经算过的结果**。它新增了 [[topics/query-result-caching]] 与 [[entities/clickhouse]] 这条偏 OLAP 的性能主线：通过 TTL、缓存准入与权限隔离，在可接受的新鲜度窗口内换取更低延迟与更低资源消耗。

紧接着补入的 [[sources/introducing-the-clickhouse-query-cache]] 则把这条主线从“怎么用”延伸到“为什么这样设计”。它补充了 query cache 早期作为实验功能的定位、用真实慢查询调试命中失败的过程，以及从事务不一致设计、AST 匹配到未来淘汰策略的产品演化背景。

这次继续沿着 ClickHouse 往下挖的 [[sources/clickhouse-manage-and-deploy]]、[[sources/clickhouse-replication-and-scaling]]、[[sources/clickhouse-separation-storage-compute]]、[[sources/clickhouse-external-disks-for-storing-data]] 与 [[sources/clickhouse-multi-region-replication]]，则把主题从“查询如何更省”扩展到“分析数据库如何真正部署成生产系统”。它们新增了 [[topics/clickhouse-deployment-topologies]] 这条主线，把副本、分片、Keeper、对象存储、本地缓存与多地域时延约束串成一个完整的架构判断框架。

最新补入的 [[sources/clickhouse-keeper]] 则把这条主线继续推进到协调层选型：当 ClickHouse 已经需要 Keeper 这类组件时，团队真正要判断的不是“能不能用”，而是**应不应该在 ClickHouse 专用协调层与通用 ZooKeeper 基础设施之间做切换**。它新增了 [[topics/clickhouse-keeper-vs-zookeeper]]，把兼容性、迁移边界、组织复用与生产运维建议放进同一判断框架。

这次摄入的 [[sources/interaction-models]] 则把 wiki 的 agent 主线从「编排层怎么设计」推进到「人机协作的实时性」这一新维度。它新增了 [[topics/interaction-models]]、[[entities/thinking-machines-lab]]：Thinking Machines Lab 提出的 interaction model 不是让 turn-based 模型跑得更快，而是**彻底取消 turn 的概念**——以 200ms micro-turns 持续运行，原生支持打断、重叠语音、视觉主动性和并发工具调用。双模型架构把实时 presence 交给 interaction model，把深度推理交给 background model，让我意识到 agentic system 的分工维度不只可以是任务空间，还可以是时间空间。

这次继续补入的 [[sources/clickhouse-operator-introduction]]、[[sources/altinity-converting-mergetree-to-replicated]]、[[sources/clickhouse-replicated-table-engines]] 与 [[sources/clickhouse-attach-as-replicated]]，则把 ClickHouse 主线从“集群怎么搭”推进到“生产上应该在什么时候选 replicated，以及选错后如何迁移”。它们新增了 [[topics/clickhouse-replicated-engines-and-conversion]]，把 `Replicated` 数据库引擎、`ReplicatedMergeTree`、`ATTACH ... AS REPLICATED`、`convert_to_replicated` 与旁路迁移方案放进同一个生产判断框架。

随后归档的 [[topics/clickhouse-single-node-to-cluster-migration]]，则把这些知识进一步落到一个更贴近实战的问题上：当现网还是单节点 ClickHouse 时，迁到多副本多分片集群到底能不能“无缝切换”，以及表引擎切换应不应该和集群迁移绑定在同一次工程里。这个页面把“可以用 `MergeTree`”与“适不适合多副本目标”明确拆开，也把业务侧平滑切换与数据库内部透明升级区分开了。

这次摄入的 [[sources/clickhouse-13-mistakes]] 则把 ClickHouse 主线从“功能与拓扑怎么选”拉回到更基础但更容易出事故的地方：写入 part、partition key、稀疏主键、`LIMIT`、物化视图、Keeper 和内存限制。它新增了 [[topics/clickhouse-common-pitfalls]]，提醒我 ClickHouse 的很多问题不是单点配置错误，而是没有顺着 OLAP 物理模型设计系统。

新归档的 [[sources/clickhouse-cold-hot-storage]] 则把 ClickHouse 冷热分层从文档原语推进到实践检查单：在 Kubernetes 中接入阿里云 OSS，不只是写一个 S3 endpoint，还要把 virtual hosted style、Secret 注入、cache disk、storage policy、TTL move、`system.parts.disk_name` 和冷 / 热查询体感一起验证。这让“全量历史进入新集群后再靠冷热分层降成本”变成一个更可执行的判断。

这次补入的 [[sources/oneuptime-clickhouse-export-file-formats]] 则把 ClickHouse 迁移里的“导出”单独拎出来：`FORMAT` 只是结果序列化，`INTO OUTFILE`、HTTP、`clickhouse-client` 和 `s3()` 表函数决定文件落点。它新增了 [[topics/clickhouse-data-export]]，也把生产回灌里坚持 `Native + zstd`、数据湖交换再优先 `Parquet + zstd` 的判断写得更清楚。

这次摄入的 [[sources/tencent-cloud-clickhouse-cluster-sizing]] 则把 ClickHouse 主线从“怎么部署”推进到“用什么机器部署”。它新增了 [[topics/clickhouse-cluster-sizing]]：腾讯云 TCHouse-C 把计算节点打包成标准型、存储优化型与高性能型三类规格，本质上是把 CPU/内存配比与磁盘介质这两个维度做了预设。选型真正的难点不是“哪款最大”，而是先回答查询模式、数据温度与成本约束，再在 CPU、内存、磁盘和网络四条线上做取舍。Keeper 节点虽然常被忽略，但它的网络抖动会直接影响整个集群的副本健康度。

这次继续深挖的 [[sources/clickhouse-cloud-architecture]] 和 [[sources/clickhouse-parallel-replicas]]，则把 ClickHouse 主线从“自管集群怎么搭”推进到“Cloud 托管架构下查询怎么并行化”。前者让我看到 ClickHouse Cloud 并不是自管版的包装，而是以对象存储为默认底座、计算层自动扩缩容与 idle、compute-compute separation 让读写资源彻底解耦的另一种架构。后者则补上了无分片场景下的查询并行化机制：用 granule 取代 shard 作为工作单元，通过 announcement、dynamic coordination、cache locality 和 task stealing 解决异步复制、尾延迟与缓存命中问题。它们共同更新了 [[topics/clickhouse-deployment-topologies]]，把 Cloud 架构判断与并行查询策略也纳入同一框架。

这次补入的 [[sources/clickhouse-go-configuration]] 则把 ClickHouse 主线从"服务端怎么部署"推进到"客户端怎么连接"。它更新了 [[topics/clickhouse-deployment-topologies]]：全副本架构下，客户端的 `Addr` 应填入所有 replica 地址，通过 `ConnOpenStrategy`（轮询或随机）实现查询负载均衡；`ConnMaxLifetime` 默认值 1 小时在节点动态扩缩容时可能导致连接分布不均，需要监控；协议选择（TCP vs HTTP）不仅影响压缩选项，还影响 session 语义和认证方式。

这次摄入的 [[sources/clickhouse-shared-merge-tree]] 则把 ClickHouse Cloud 的底层引擎摊开来看：SharedMergeTree 是 ReplicatedMergeTree 在云原生环境下的重新实现，用"共享存储 + Keeper 元数据 + 异步 leaderless 复制"取代了传统的"replica 间复制"，实现了秒级扩容和数百 replica 支持。这让我理解了为什么 ClickHouse Cloud 能做到 compute-compute separation 和动态扩缩容——底层引擎已经为"共享存储 + 无状态计算节点"做好了设计。自管集群即使配置了对象存储，仍然使用 ReplicatedMergeTree，replica 间仍然需要复制，扩容速度天然受限。

这次摄入的 [[sources/kubernetes-autoscaling-workloads]] 和 [[sources/ack-node-scaling]]，则把 Kubernetes 从“部署 ClickHouse 的容器平台”推进成一条独立的调度与控制器主线。它们新增了 [[topics/kubernetes-autoscaling]] 与 [[entities/kubernetes]]：工作负载伸缩负责改变 replica 或 Pod 资源，节点伸缩负责为不可调度 Pod 补容量，两者必须通过调度器、resource requests、节点池、PDB 和云厂商库存接起来。

这次补入的 [[sources/cnpg-recovery-incident]] 则把 Kubernetes 持久化存储从文档判断推进到事故恢复现场。它新增了 [[topics/cloudnativepg-recovery]] 与 [[entities/cloudnativepg]]：CloudNativePG 能调和 PostgreSQL 集群，但不能替我判断哪块 PV 是权威数据；Pod 删除、PVC 删除、PV 回收策略、VolumeSnapshot 和 WAL 复制状态必须分层处理。

这次摄入的 [[sources/databricks-what-is-hdfs]]、[[sources/aliyun-oss-hdfs-overview]] 和 [[sources/aliyun-oss-hdfs-notice]]，则新增了 [[topics/hdfs-and-oss-hdfs]] 这条大数据存储线索：传统 HDFS 用 NameNode、DataNode、block 和副本解决本地集群时代的大文件存储，OSS-HDFS 则把 HDFS 接口语义接到 OSS 对象存储之上，同时引入 `.dlsdata/` 内部目录、生命周期规则、版本控制和后台角色这些新的云上运维边界。

这次摄入的 [[sources/ducklake-manifesto]] 和 [[sources/ducklake-v1-0-announcement]] 则新增了 [[topics/ducklake]] 这条数据湖格式线索：DuckLake 的核心判断是——既然 lakehouse 的 catalog 层最终还是要引入数据库来保证事务一致性，那不如干脆把全部元数据也交给数据库来管理。数据文件仍用开放的 Parquet 格式存放在对象存储上，但元数据、快照、schema 变更和统计信息全部放在 SQL 数据库的表里。这让我意识到，lakehouse 格式的真正竞争不在数据层（Parquet 已经是事实标准），而在元数据层。DuckLake 的 Data Inlining、Sorted Tables、Bucket Partitioning 和 Variant 类型，则把写入优化、查询优化与类型系统演进放到了同一设计框架里。

这次摄入的 [[sources/duckdb-vs-clickhouse-posthog]]、[[sources/duckdb-vs-postgres]] 和 [[sources/duckdb-vs-sqlite]] 则补充了 DuckDB 的多维定位：它与 ClickHouse 不是竞争关系而是互补——ClickHouse 是生产级 OLAP 服务（长驻进程、水平扩展、高并发写入），DuckDB 是嵌入式分析引擎（进程内、零配置、用完即销毁）。PostHog 同时用 ClickHouse 处理热分析、用 DuckDB 处理数据仓库的即席查询，这个"三数据库栈"（Postgres + ClickHouse + DuckDB）让我看到不同数据库可以按工作负载分层共存。而与 Postgres 的对比则进一步揭示了 OLAP 与 OLTP 的根本差异：列式 vs 行式、向量化执行 vs Volcano 模型、嵌入式 vs 客户端-服务器。与 SQLite 的对比则澄清了"SQLite of OLAP"这个称号的精确含义——DuckDB 的核心不是"本地性"，而是"便携性 + 分析马力"。

这次摄入的 [[sources/agent-first-product-engineering]] 则把 wiki 的 agent 主线从"架构设计"推进到"产品设计"层面。它新增了 [[topics/agent-first-engineering]] 和 [[entities/posthog]]：agent 不是产品的附加功能，而是一种新的交互层。PostHog 从 6000+ 日活 MCP 用户的两次架构迭代中提炼出五条原则——让 agent 能做用户能做的一切、在 agent 的抽象层级上设计（用 SQL 替代 UI 原语）、预加载通用上下文、把 skill 写成"给优秀员工的入职指南"而非 step-by-step 手册、以及把 agent 当作真实用户来做 headless dogfooding 和 trace review。这补充了 agent 主线中缺失的"产品层"视角。

新摄入的 [[sources/epoch-semantic-versioning]] 则把主题扩展到开源维护与软件版本语义。它新增了 [[topics/software-versioning]] 和 [[entities/anthony-fu]]，提醒我版本号不是完美描述变更的事实系统，而是维护者、用户和包管理器之间的风险沟通信号；Epoch SemVer 的价值在于不改现有 SemVer 工具链，却把技术 breaking change 和时代级变化拆开表达。

这次摄入的 [[sources/agent-bridge-design]] 则把视角从"阅读别人的 agent 设计"推进到"自己动手做一套桥接器"。它新增了 [[topics/agent-bridge]]、[[entities/openclaw]] 与 [[entities/ilink]]：原始代码是一套深度绑定 OpenClaw 网关的微信插件，新设计的 Agent Bridge 则把通讯软件通道与 CLI Agent 解耦，用配置驱动的多对多路由、本地状态存储和安全默认值，让个人开发者能在不依赖完整网关框架的前提下，直接用微信消息驱动本机的 Codex、Claude Code、Codebuddy 或任意命令行工具。

继续摄入的 [[sources/move-on-to-esm-only]] 把 Anthony Fu 这条开源维护线从“版本号如何沟通风险”推进到“模块格式什么时候可以停止兼容旧世界”。它新增了 [[topics/javascript-module-systems]] 和 [[entities/nodejs]]：ESM-only 不是单纯语法偏好，而是工具链成熟、Node.js `require(ESM)` 互操作和 dual CJS / ESM 维护成本共同推动出来的生态迁移判断。

这次摄入的 [[sources/ds4-readme]] 则把 wiki 的 agent 主线从「编排层怎么设计」推进到「本地模型能不能成为 agent 的可信后端」。它新增了 [[topics/local-llm-inference]]、[[entities/antirez]] 与 [[entities/deepseek]]：antirez 不为通用性做框架，而是为一个特定模型（DeepSeek V4 Flash）做端到端优化的专用引擎；2-bit 非对称量化只压 routed MoE experts，磁盘 KV cache 把上下文持久化从 RAM 解放到 SSD，官方向量验证则把「感觉差不多」变成比特级一致。这些设计让我意识到，本地推理不是云端的降级版，而是一组独立约束下的重新优化。

这次同时摄入的 [[sources/harness-vs-platform-engineering]] 则把 agent 架构从"单个 harness 怎么设计"推进到"企业级 fleet 如何治理"。它新增了 Harness vs Platform 的分层视角：harness 负责进程内的任务优化（编排、提示组装、工具选择），platform 负责跨 agent 的治理（身份、授权、审计、限流、成本）。三层架构（Harness → Platform → Targets）之间的 seam 定义，是 agentic 系统在企业规模下最关键的设计决策。这篇文章也更新了 [[topics/ai-agent-harness]]，补充了治理引力陷阱、反模式清单和前瞻趋势。

这次摄入的 [[sources/opencode-usage-tips]] 则把视角从"agent 架构怎么设计"拉回到"一个具体工具怎么用才能不踩坑"。它新增了 [[entities/opencode]] 与 [[topics/opencode-workflow]]：上下文管理不是"尽量给模型更多信息"，而是"主动保持上下文干净才能维持输出质量"；AGENTS.md 不是第三方记忆插件的替代品，而是当前最实用的项目记忆方案；子 Agent 汇报失真的问题也不只是理论风险，而是已有插件（verify-subagent-plugin）在尝试解决的实际痛点。这篇文章让我意识到，在讨论 orchestration layer 和 category-based delegation 之前，先把"一个会话只做一件事"、"配置层级深层合并"和"Bash 命令守卫"这类基础工作流做好，可能更重要。

这次摄入的三篇基础设施文章则新增了负载均衡与服务网格主题。[[sources/choosing-load-balancing-strategy]] 和 [[sources/advanced-load-balancing-traefik]] 共同构建了 [[topics/load-balancing-strategies]]：从 WRR、P2C、HRW、Least-Time 四种核心策略的选择框架，到服务级策略（金丝雀、镜像、故障转移）的组合使用。[[sources/what-is-envoy]] 则新增了 [[topics/service-mesh]] 和 [[entities/envoy]]：Envoy 作为进程外代理的设计哲学——语言无关、独立升级、统一治理——以及 sidecar 模式向 ambient mesh 的演进。同时新增的 [[entities/traefik]] 和 [[topics/progressive-delivery]] 则把负载均衡器从"流量分发工具"重新定位为"发布策略的承载面"。

这次摄入的 [[sources/clickhouse-query-optimization-guide]] 和 [[sources/clickhouse-optimize-aggregation-in-order]] 则把 ClickHouse 主线从"怎么部署"推进到"怎么系统地让查询更快"。前者是 ClickHouse 官方工程博客的综合优化指南，用 ORDER BY 设计、数据类型、projection、物化视图、skip index、字典和多趟分组构建了一个完整的优化分层框架；后者则聚焦于 `optimize_aggregation_in_order` 这一个设置，解释为什么当 GROUP BY 对齐 ORDER BY 时，聚合不需要 hash table 就可以流式完成。它们共同新增了 [[topics/clickhouse-query-optimization]]，也更新了 [[topics/clickhouse-common-pitfalls]] 里的 Nullable、分区和 skip index 误区。这次摄入让我真正意识到，ClickHouse 的优化重心不在查询层面，而在建表时的 `ORDER BY` 设计——这本质上是在提前定义数据的物理归宿。

## 当前关注

如果要用一句更个人的话来概括，这一阶段我最关心的不是“又学了哪些零散知识点”，而是能不能把这些主题收敛成几套稳定的判断框架。下面这些点，都是我觉得接下来值得继续深挖的方向。

- 理解并内化 LLM Wiki 模式本身
- 建立个人知识 / 自我提升领域的摄入习惯
- 理解 QMD 这类本地搜索工具如何作为 wiki 的扩展层
- 建立一套对 AI agent 更克制的设计判断：何时保持简单，何时升级为 workflow 或自治 agent
- 理解多智能体的真实适用边界，而不是把“更多 agent”当作默认优化方向
- 理解长程 agent 的状态层、上下文层与执行层应如何分离
- 建立一套关于 SQL 索引、执行计划与分页策略的基础性能判断
- 理解分析型数据库中的查询结果缓存如何在新鲜度、安全性与成本之间折中
- 理解 ClickHouse 中分片、副本、存算分离与冷热分层之间的组合关系
- 理解 ClickHouse 分片决策的触发条件：在冷热分层前提下，何时分片、何时全副本
- 理解 ClickHouse 从独立节点到全副本集群的迁移路径与关键验证点
- 理解 ClickHouse 中 Keeper 与 ZooKeeper 的适用边界，以及协调层选型如何影响生产复杂度
- 理解 ClickHouse 中 `Replicated` 数据库引擎与 `ReplicatedMergeTree` 的分工，以及旧表转 replicated 的风险边界
- 理解单节点 ClickHouse 迁到集群时，哪些变化属于拓扑升级，哪些变化属于表级迁移工程
- 理解 ClickHouse 常见误区背后的物理约束：part 合并、稀疏主键、Keeper 协调与内存治理
- 理解 ClickHouse 冷热分层的生产落点验证：对象存储、cache disk、TTL move 与查询体感要一起评估
- 理解 ClickHouse 数据导出的格式与通道边界：文件落点、对象存储写入和回灌格式要从下游倒推
- 理解 ClickHouse 集群负载均衡的选项对比：客户端多地址、外部 LB（Traefik/Envoy/云厂商）与 Cloud 托管体验之间的差距与取舍
- 理解 Kubernetes 弹性伸缩的分层模型：workload 层改副本和资源，node 层补调度容量
- 理解 Kubernetes 持久化存储的选型框架：静态卷 vs 动态卷的生命周期所有权、StorageClass 的治理含义、RWO 约束对应用架构的影响
- 理解 CloudNativePG 事故恢复的操作边界：先确认权威数据和 PV/PVC 生命周期，再让 Operator 调和；副本健康要看 WAL，而不只看 Ready
- 理解 VolumeSnapshot 不只是备份工具，而是迁移验证、快速恢复和开发环境同步的基础设施
- 理解 HDFS 到 OSS-HDFS 的演化：接口语义可以保留，但底层对象存储会带来新的运维边界
- 理解 DuckLake 的数据库优先元数据架构：为什么把元数据从 JSON 文件迁移到 SQL 数据库是更本质的设计选择，以及这对小文件问题、事务并发和查询规划的影响
- 理解 lakehouse 格式的竞争边界：数据层（Parquet）已经是事实标准，真正的差异在元数据层和生态系统
- 理解 DuckLake 的 Data Inlining 如何改变"小写入进入数据湖"的成本模型
- 理解软件版本号作为升级契约的沟通作用，而不是把 SemVer 当作机械规则
- 理解 JavaScript 模块系统迁移：ESM-only 何时从激进选择变成更低成本的默认值
- 理解通讯软件与 CLI Agent 的桥接设计：何时需要完整网关框架，何时只需要轻量桥接层
- 理解本地 LLM 推理的约束博弈：量化策略、KV cache 持久化、上下文长度与 agent 兼容性的组合关系
- 理解专用推理引擎与通用运行器的取舍：「只做一个模型但做到极致」和「支持所有模型但都不完美」各自适合什么场景
- 理解 DeepSeek V4 Flash 的 MoE 架构如何改变本地推理的硬件边界：2-bit 非对称量化、1M 上下文、磁盘 KV cache
- 理解 AI Agent Harness 的三层模型：host substrate、orchestration layer、specialist agent 如何独立演进
- 理解 category-based delegation 的设计取舍：模型选择从配置问题变成意图表达问题的价值与风险
- 理解多智能体系统的后台并行机制：会话隔离、生命周期管理、结果回注和熔断器如何组成完整基础设施
- 理解 OpenCode 的日常工作流：一个会话只做一件事、主动压缩上下文、AGENTS.md 的分层记忆策略与子 Agent 信息失真的防范
- 理解 agent 复杂度阶梯的可实现性：prompt chaining → routing → orchestrator-workers → evaluator-optimizer 每一层对应什么代码模块
- 理解 interaction model 带来的范式变化：从 turn-based 到流式协作，ACI 是否需要同时回答"模型如何调用工具"和"模型如何与人类共享时间"
- 理解双模型架构中按时间尺度的分工逻辑：实时 presence 与深度推理的边界如何定义，结果如何自然回注到对话流中
- 理解 ClickHouse 查询优化的物理基础：为什么 ORDER BY 设计是第一优化杠杆，以及如何把"优化"从查询技巧重新定位为"让数据物理组织对齐查询模式"
- 理解 DuckDB 与 ClickHouse 的互补边界：嵌入式引擎 vs 生产服务，何时选择单节点分析 vs 分布式 OLAP
- 理解 DuckDB 的两种模式：查询引擎模式（用完即销毁）与数据库模式（持久化 .duckdb 文件）各自的适用场景
- 理解 PostHog 的三数据库栈：为什么一个产品需要同时用 Postgres + ClickHouse + DuckDB，以及它们如何按工作负载分层
- 理解 Agent-first 产品设计的五原则：特别是"在 agent 的抽象层级上设计"——用 SQL 替代 UI 原语，释放 agent 的创造力
- 理解 MCP tool 的暴露策略：默认关闭 vs 默认开放，以及 product team opt-in 的治理模式

## 演化轨迹

这条时间线对我来说也不是纯记录，而是这套知识图谱真正长出来的顺序。回头看它，能很清楚地看到主题是怎样一层层从“知识库”扩展到“agent 工程”，再扩展到“数据库性能与部署”的。

- 2026-04-13：wiki 初始化，摄入第一个来源（Karpathy LLM Wiki 方法论文章）
- 2026-04-13：摄入 QMD README，补充 wiki 在规模化后的本地检索基础设施视角
- 2026-04-13：摄入 Anthropic 的 agent 工程文章，引入 agentic systems 与 ACI 两条新主题
- 2026-04-13：摄入 Anthropic 的多智能体 Research 复盘，新增多智能体协作与评估视角
- 2026-04-13：摄入 Anthropic 的 Managed Agents 架构文章，新增长程 agent 运行时与安全边界视角
- 2026-04-14：摄入 Use The Index, Luke，新增 SQL 索引、执行计划、连接、排序与分页相关主题
- 2026-04-15：摄入 ClickHouse Query Cache 文档，新增 OLAP 查询结果缓存与 ClickHouse 相关主题
- 2026-04-15：补充 ClickHouse Query Cache 设计博客，完善该主题的设计动机、调试方式与演化脉络
- 2026-04-16：摄入 ClickHouse 部署与运维文档，新增分片、副本、存算分离与冷热分层主题
- 2026-04-16：摄入 ClickHouse Keeper 文档，新增 Keeper 与 ZooKeeper 的协调层选型主题
- 2026-04-16：摄入 ClickHouse replicated 引擎与旧表转换文档，新增生产复制与迁移主题
- 2026-04-16：归档单节点 ClickHouse 迁移到集群的问答，补充无缝切换与表引擎切换的实操判断
- 2026-04-26：摄入 ClickHouse 入门 13 个误区，新增常见误区与物理模型检查表
- 2026-04-27：摄入 ClickHouse 冷热分层实践笔记，补充 Kubernetes、OSS、cache disk 与 TTL move 的验证路径
- 2026-04-28：摄入 ClickHouse 导出文件格式指南，新增数据导出格式与通道判断
- 2026-04-28：摄入 Kubernetes 与 ACK 弹性伸缩文档，新增 workload / node 分层伸缩主题
- 2026-04-28：摄入 HDFS 与 OSS-HDFS 文档，新增大数据文件系统和对象存储兼容层主题
- 2026-04-28：摄入 Epoch Semantic Versioning，新增软件版本语义与开源升级沟通主题
- 2026-04-28：摄入 Move on to ESM-only，新增 JavaScript 模块系统与 Node.js 互操作主题
- 2026-04-29：摄入 Agent Bridge 设计与实现，新增通讯软件与 CLI Agent 桥接主题
- 2026-05-09：摄入 oh-my-openagent 架构分析，新增 AI Agent Harness 主题，把 agentic systems 从理论概念推进到具体运行时实现
- 2026-05-09：摄入 ds4.c README，新增本地 LLM 推理主题，把 agent 后端从云端 API 延伸到本地专用引擎
- 2026-05-12：摄入 Thinking Machines Lab 的 interaction models，新增实时多模态交互主题，把 agent 设计从编排层推进到人机协作的时间维度
- 2026-05-14：摄入 Harness Engineering vs Platform Engineering，把 agent 架构从单 harness 设计推进到企业级 fleet 治理，新增 Harness-Platform-Targets 三层架构视角
- 2026-05-14：摄入 Traefik 负载均衡策略文章，新增负载均衡策略选择框架、渐进式交付与 Traefik/Envoy 代理架构主题
- 2026-05-15：设计 ClickHouse 集群负载均衡验证方案，新增自管集群连接层负载均衡主题：对比客户端多地址、Traefik TCP LB 与 ClickHouse Cloud 托管体验
- 2026-05-19：摄入 OpenCode 使用技巧与最佳实践，新增 OpenCode 工具实体与日常工作流主题，把 agent 使用从架构设计拉回具体工具的操作节奏与上下文管理判断
- 2026-05-20：摄入 ClickHouse 查询优化权威指南与 aggregation-in-order 设置专项文章，新增 ClickHouse 查询优化主题：从 ORDER BY 设计、数据类型、预计算、聚合策略到诊断体系的完整优化框架
- 2026-05-26：摄入 ACK 云盘存储卷三篇文档（静态卷、动态卷、快照），新增 Kubernetes 持久化存储主题：把 PV/PVC/StorageClass 的选型从"怎么挂载"推进到"谁管理生命周期"
- 2026-05-26：归档 CNPG/PostgreSQL 事故恢复会话，新增 CloudNativePG 恢复主题：把 Retain PV、快照、临时 clone、逻辑迁回和 WAL 复制验证连成一条可复用的恢复路径
- 2026-06-11：摄入 DuckLake 宣言与 v1.0 发布说明，新增 DuckLake 数据湖格式主题：把元数据从 JSON/Avro 文件迁移到 SQL 数据库，让数据层（Parquet）通用但元数据层独立，同时关注 Data Inlining、Sorted Tables、Bucket Partitioning 与 Variant 类型等写入/查询优化设计
- 2026-06-13：摄入 DuckDB 与 ClickHouse/Postgres/SQLite 三篇对比文章，新增 DuckDB 定位主题：DuckDB 不是 ClickHouse 的替代者，而是嵌入式分析引擎；PostHog 同时使用 Postgres + ClickHouse + DuckDB 的三数据库栈，按工作负载分层；DuckDB 的核心不是"本地性"而是"便携性 + 分析马力"
- 2026-06-13：摄入 Agent-first 产品设计五原则，新增 Agent 产品层主题：agent 不是附加功能而是新交互层；在 agent 的抽象层级上设计（SQL 替代 UI 原语）；默认关闭端点 + product team opt-in 的治理模式；headless dogfooding 和 trace review 作为 agent 测试方法

---

相关页面：[[index]] · [[topics/llm-wiki-pattern]] · [[topics/local-first-search]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/multi-agent-systems]] · [[topics/ai-agent-harness]] · [[topics/long-horizon-agents]] · [[topics/agent-bridge]] · [[topics/local-llm-inference]] · [[topics/interaction-models]] · [[topics/opencode-workflow]] · [[topics/sql-indexing]] · [[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]] · [[topics/query-result-caching]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-common-pitfalls]] · [[topics/clickhouse-data-export]] · [[topics/clickhouse-cluster-load-balancing]] · [[topics/kubernetes-autoscaling]] · [[topics/kubernetes-persistent-storage]] · [[topics/hdfs-and-oss-hdfs]] · [[topics/ducklake]] · [[topics/duckdb-vs-clickhouse]] · [[topics/agent-first-engineering]] · [[topics/software-versioning]] · [[topics/javascript-module-systems]] · [[topics/load-balancing-strategies]] · [[topics/progressive-delivery]] · [[topics/service-mesh]] · [[entities/qmd]] · [[entities/anthropic]] · [[entities/anthony-fu]] · [[entities/openclaw]] · [[entities/ilink]] · [[entities/managed-agents]] · [[entities/markus-winand]] · [[entities/clickhouse]] · [[entities/clickhouse-keeper]] · [[entities/kubernetes]] · [[entities/hdfs]] · [[entities/oss-hdfs]] · [[entities/duckdb]] · [[entities/ducklake]] · [[entities/posthog]] · [[entities/nodejs]] · [[entities/oh-my-openagent]] · [[entities/opencode]] · [[entities/antirez]] · [[entities/deepseek]] · [[entities/thinking-machines-lab]] · [[entities/traefik]] · [[entities/envoy]] · [[sources/agent-bridge-design]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]] · [[sources/clickhouse-13-mistakes]] · [[sources/clickhouse-cold-hot-storage]] · [[sources/oneuptime-clickhouse-export-file-formats]] · [[sources/kubernetes-autoscaling-workloads]] · [[sources/ack-node-scaling]] · [[sources/ack-static-disk-volume]] · [[sources/ack-dynamic-disk-volumes]] · [[sources/ack-disk-volume-snapshots]] · [[sources/databricks-what-is-hdfs]] · [[sources/aliyun-oss-hdfs-overview]] · [[sources/aliyun-oss-hdfs-notice]] · [[sources/ducklake-manifesto]] · [[sources/ducklake-v1-0-announcement]] · [[sources/duckdb-vs-clickhouse-posthog]] · [[sources/duckdb-vs-postgres]] · [[sources/duckdb-vs-sqlite]] · [[sources/agent-first-product-engineering]] · [[sources/epoch-semantic-versioning]] · [[sources/move-on-to-esm-only]] · [[sources/oh-my-openagent]] · [[sources/ds4-readme]] · [[sources/interaction-models]] · [[sources/harness-vs-platform-engineering]] · [[sources/advanced-load-balancing-traefik]] · [[sources/choosing-load-balancing-strategy]] · [[sources/what-is-envoy]] · [[sources/clickhouse-optimize-aggregation-in-order]] · [[sources/clickhouse-query-optimization-guide]] · [[topics/clickhouse-query-optimization]]
