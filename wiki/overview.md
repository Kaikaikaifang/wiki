---
title: 整体综述
type: overview
tags: [方法论, 知识管理]
source_count: 26
updated: 2026-04-28
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

这次继续补入的 [[sources/clickhouse-operator-introduction]]、[[sources/altinity-converting-mergetree-to-replicated]]、[[sources/clickhouse-replicated-table-engines]] 与 [[sources/clickhouse-attach-as-replicated]]，则把 ClickHouse 主线从“集群怎么搭”推进到“生产上应该在什么时候选 replicated，以及选错后如何迁移”。它们新增了 [[topics/clickhouse-replicated-engines-and-conversion]]，把 `Replicated` 数据库引擎、`ReplicatedMergeTree`、`ATTACH ... AS REPLICATED`、`convert_to_replicated` 与旁路迁移方案放进同一个生产判断框架。

随后归档的 [[topics/clickhouse-single-node-to-cluster-migration]]，则把这些知识进一步落到一个更贴近实战的问题上：当现网还是单节点 ClickHouse 时，迁到多副本多分片集群到底能不能“无缝切换”，以及表引擎切换应不应该和集群迁移绑定在同一次工程里。这个页面把“可以用 `MergeTree`”与“适不适合多副本目标”明确拆开，也把业务侧平滑切换与数据库内部透明升级区分开了。

这次摄入的 [[sources/clickhouse-13-mistakes]] 则把 ClickHouse 主线从“功能与拓扑怎么选”拉回到更基础但更容易出事故的地方：写入 part、partition key、稀疏主键、`LIMIT`、物化视图、Keeper 和内存限制。它新增了 [[topics/clickhouse-common-pitfalls]]，提醒我 ClickHouse 的很多问题不是单点配置错误，而是没有顺着 OLAP 物理模型设计系统。

新归档的 [[sources/clickhouse-cold-hot-storage]] 则把 ClickHouse 冷热分层从文档原语推进到实践检查单：在 Kubernetes 中接入阿里云 OSS，不只是写一个 S3 endpoint，还要把 virtual hosted style、Secret 注入、cache disk、storage policy、TTL move、`system.parts.disk_name` 和冷 / 热查询体感一起验证。这让“全量历史进入新集群后再靠冷热分层降成本”变成一个更可执行的判断。

这次摄入的 [[sources/kubernetes-autoscaling-workloads]] 和 [[sources/ack-node-scaling]]，则把 Kubernetes 从“部署 ClickHouse 的容器平台”推进成一条独立的调度与控制器主线。它们新增了 [[topics/kubernetes-autoscaling]] 与 [[entities/kubernetes]]：工作负载伸缩负责改变 replica 或 Pod 资源，节点伸缩负责为不可调度 Pod 补容量，两者必须通过调度器、resource requests、节点池、PDB 和云厂商库存接起来。

这次摄入的 [[sources/databricks-what-is-hdfs]]、[[sources/aliyun-oss-hdfs-overview]] 和 [[sources/aliyun-oss-hdfs-notice]]，则新增了 [[topics/hdfs-and-oss-hdfs]] 这条大数据存储线索：传统 HDFS 用 NameNode、DataNode、block 和副本解决本地集群时代的大文件存储，OSS-HDFS 则把 HDFS 接口语义接到 OSS 对象存储之上，同时引入 `.dlsdata/` 内部目录、生命周期规则、版本控制和后台角色这些新的云上运维边界。

新摄入的 [[sources/epoch-semantic-versioning]] 则把主题扩展到开源维护与软件版本语义。它新增了 [[topics/software-versioning]] 和 [[entities/anthony-fu]]，提醒我版本号不是完美描述变更的事实系统，而是维护者、用户和包管理器之间的风险沟通信号；Epoch SemVer 的价值在于不改现有 SemVer 工具链，却把技术 breaking change 和时代级变化拆开表达。

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
- 理解 ClickHouse 中 Keeper 与 ZooKeeper 的适用边界，以及协调层选型如何影响生产复杂度
- 理解 ClickHouse 中 `Replicated` 数据库引擎与 `ReplicatedMergeTree` 的分工，以及旧表转 replicated 的风险边界
- 理解单节点 ClickHouse 迁到集群时，哪些变化属于拓扑升级，哪些变化属于表级迁移工程
- 理解 ClickHouse 常见误区背后的物理约束：part 合并、稀疏主键、Keeper 协调与内存治理
- 理解 ClickHouse 冷热分层的生产落点验证：对象存储、cache disk、TTL move 与查询体感要一起评估
- 理解 Kubernetes 弹性伸缩的分层模型：workload 层改副本和资源，node 层补调度容量
- 理解 HDFS 到 OSS-HDFS 的演化：接口语义可以保留，但底层对象存储会带来新的运维边界
- 理解软件版本号作为升级契约的沟通作用，而不是把 SemVer 当作机械规则

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
- 2026-04-28：摄入 Kubernetes 与 ACK 弹性伸缩文档，新增 workload / node 分层伸缩主题
- 2026-04-28：摄入 HDFS 与 OSS-HDFS 文档，新增大数据文件系统和对象存储兼容层主题
- 2026-04-28：摄入 Epoch Semantic Versioning，新增软件版本语义与开源升级沟通主题

---

相关页面：[[index]] · [[topics/llm-wiki-pattern]] · [[topics/local-first-search]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/multi-agent-systems]] · [[topics/long-horizon-agents]] · [[topics/sql-indexing]] · [[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]] · [[topics/query-result-caching]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[topics/clickhouse-common-pitfalls]] · [[topics/kubernetes-autoscaling]] · [[topics/hdfs-and-oss-hdfs]] · [[topics/software-versioning]] · [[entities/qmd]] · [[entities/anthropic]] · [[entities/anthony-fu]] · [[entities/managed-agents]] · [[entities/markus-winand]] · [[entities/clickhouse]] · [[entities/clickhouse-keeper]] · [[entities/kubernetes]] · [[entities/hdfs]] · [[entities/oss-hdfs]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]] · [[sources/clickhouse-13-mistakes]] · [[sources/clickhouse-cold-hot-storage]] · [[sources/kubernetes-autoscaling-workloads]] · [[sources/ack-node-scaling]] · [[sources/databricks-what-is-hdfs]] · [[sources/aliyun-oss-hdfs-overview]] · [[sources/aliyun-oss-hdfs-notice]] · [[sources/epoch-semantic-versioning]]
