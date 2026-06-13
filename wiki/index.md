---
title: 内容目录
type: index
tags: [索引, 导航]
source_count: 0
updated: 2026-06-13
---

> 每次摄入后由 LLM 更新。查询时先读此文件定位相关页面。

## 综述

- [[overview]] — 整体综述与核心主题

## 主题

- [[topics/agent-bridge]] — 通讯软件与 CLI Agent 的轻量桥接层，Channel-Agent 解耦、配置驱动、安全默认
- [[topics/agent-computer-interface]] — 面向模型而非人类的工具接口设计原则
- [[topics/ai-agent-harness]] — AI Agent Harness：从单模型会话到多 agent 编排运行时的设计模式与生产实践
- [[topics/agentic-systems]] — 从增强型 LLM 到 workflow 与自治 agent 的复杂度阶梯
- [[topics/b-tree-indexes]] — 用叶子链表、树遍历与回表理解索引为什么会快或慢
- [[topics/clickhouse-cluster-load-balancing]] — 自管 ClickHouse 集群的负载均衡：从客户端多地址到 Traefik TCP LB 的选项对比与 Cloud 体验差距评估
- [[topics/clickhouse-cluster-sizing]] — 把 ClickHouse 集群的 CPU、内存、磁盘、网络四条约束线拧成一组可验证的选型假设
- [[topics/clickhouse-common-pitfalls]] — 用 part、主键、Keeper 与内存模型理解 ClickHouse 常见入门误区
- [[topics/clickhouse-data-export]] — 用导出通道、文件格式和下游消费者理解 ClickHouse 数据导出方案
- [[topics/clickhouse-deployment-topologies]] — 把分片、副本、Keeper、存算分离与冷热分层放进同一部署判断框架
- [[topics/clickhouse-operator-installation-on-shared-clusters]] — 在共享 Kubernetes 集群里安装官方 ClickHouse Operator 时，如何判断 Helm、watch 范围与 CRD 管理策略
- [[topics/clickhouse-keeper-vs-zookeeper]] — 用“专用协调层”与“通用协调服务”的边界判断 Keeper 与 ZooKeeper
- [[topics/clickhouse-replicated-engines-and-conversion]] — 把 `Replicated` 数据库引擎、`ReplicatedMergeTree` 与旧表迁移路径放进同一生产判断框架
- [[topics/clickhouse-sharding-decision]] — 在冷热分层前提下，何时分片、何时全副本的决策框架与真实案例分析
- [[topics/clickhouse-single-node-to-cluster-migration]] — 从单节点 ClickHouse 迁到多副本多分片集群时，如何判断无缝切换、引擎切换与迁移步骤
- [[topics/ddl-vs-dml]] — 用“改结构”和“改数据”的区别理解 `ON CLUSTER` 为什么只管 DDL
- [[topics/doing-great-work]] — 如何找到值得做的事并持续做下去：好奇心、前沿、裂缝与探索的四步方法论
- [[topics/ducklake]] — 把元数据全部交给 SQL 数据库管理的 lakehouse 格式，与 Iceberg、Delta Lake 的数据层通用但元数据层独立
- [[topics/duckdb-vs-clickhouse]] — DuckDB 与 ClickHouse 的互补定位：嵌入式引擎 vs 生产级 OLAP 服务
- [[topics/agent-first-engineering]] — Agent 优先的产品设计五原则：从 PostHog 6000+ 日活 MCP 用户的两次架构迭代
- [[topics/fake-work]] — 识别既不快乐也不产出的“伪工作”：为什么假工作比娱乐更危险
- [[topics/hybrid-retrieval]] — 组合 BM25、向量检索、查询扩展与重排的检索范式
- [[topics/hdfs-and-oss-hdfs]] — 从 NameNode / DataNode 到 OSS-HDFS，理解 HDFS 语义如何被对象存储承接
- [[topics/interaction-models]] — 把实时多模态交互能力原生内建到模型中，以 micro-turns 实现真正的人机协作
- [[topics/index-maintenance-tradeoffs]] — 索引提升读取性能时带来的写入维护成本与过度索引问题
- [[topics/index-supported-sorting-and-pagination]] — 利用索引支撑排序、Top-N 与 seek 分页
- [[topics/javascript-module-systems]] — 把 ESM、CommonJS、Node.js 互操作和包发布策略放进同一个生态迁移判断框架
- [[topics/local-first-search]] — 在本机完成索引与检索，保留 markdown 文件为事实来源
- [[topics/load-balancing-strategies]] — 负载均衡策略的通用选择框架
- [[topics/long-horizon-agents]] — 长程 agent 的状态恢复、上下文管理与运行时分层
- [[topics/local-llm-inference]] — 本地 LLM 推理的约束博弈：量化、KV cache、上下文长度与 agent 兼容性
- [[topics/llm-wiki-pattern]] — LLM 增量构建持久 wiki 的模式，替代 RAG 检索
- [[topics/multi-agent-systems]] — 适合并行开放式任务的多智能体分工与协作模式
- [[topics/opencode-workflow]] — OpenCode 使用技巧与工作流：上下文管理、AGENTS.md 记忆方案、配置层级与信息传递失真
- [[topics/knowledge-management]] — 知识管理的核心问题与主要范式对比
- [[topics/kubernetes-api-groups-and-schema-validation]] — 把 `apiVersion`、core API 与编辑器 schema 假阳性放进同一个判断框架
- [[topics/kubernetes-autoscaling]] — 把 HPA、VPA、KEDA 与节点伸缩放进同一个分层弹性判断框架
- [[topics/kubernetes-crd-recording-strategy]] — 什么时候该记录 CRD 安装配置，什么时候不该直接 vendoring 整份上游 CRD
- [[topics/kubernetes-persistent-storage]] — 把静态卷、动态卷与快照的使用场景放进同一判断框架
- [[topics/cloudnativepg-recovery]] — CloudNativePG 事故恢复、Retain 存储策略与 PostgreSQL 主从同步验证
- [[topics/postgresql-index-ddl-locking]] — 理解 PostgreSQL 中索引创建与删除 DDL 的锁强度和线上体感
- [[topics/progressive-delivery]] — 渐进式交付与蓝绿部署、金丝雀发布、流量镜像
- [[topics/query-result-caching]] — 用 TTL、准入条件与安全边界复用昂贵 `SELECT` 结果
- [[topics/query-shape-and-index-usage]] — `where` 子句形状如何决定索引是否真正缩小扫描范围
- [[topics/service-db-network-latency-diagnosis]] — 用冷连接、热连接与双侧耗时拆分判断接口慢点是否在数据库链路
- [[topics/service-mesh]] — 服务网格的设计模式与 trade-offs
- [[topics/software-versioning]] — 把 SemVer、zero-major 和 Epoch SemVer 放进升级风险沟通框架
- [[topics/clickhouse-production-migration]] — 面向单实例与 7 TiB 数据量场景的 ClickHouse 迁集群方案
- [[topics/clickhouse-scalar-multilane-backfill]] — 用主键友好 cursor、排序键边界和受控 lane 数量完成 ClickHouse scalar 大表回灌
- [[topics/clickhouse-query-optimization]] — 把 ClickHouse 查询优化从技巧提升为物理架构判断：ORDER BY 设计、数据类型、预计算、聚合策略和诊断体系
- [[topics/sql-execution-plans]] — 把执行计划当作 SQL 性能调优的第一现场
- [[topics/sql-indexing]] — 把索引视为开发者必须掌握的查询设计能力
- [[topics/sql-join-performance]] — 按 join 算法选择不同索引策略，而不是机械补索引

## 实体

- [[entities/anthropic]] — 以 Claude 与 agent 工程实践著称的 AI 公司
- [[entities/antirez]] — Redis 作者，ds4.c 本地推理引擎创建者
- [[entities/andrej-karpathy]] — AI 研究者，LLM Wiki 模式提出者
- [[entities/anthony-fu]] — 前端开源工具链作者，Epoch SemVer 提案提出者
- [[entities/clickhouse]] — 面向 OLAP 的列式数据库，强调分析查询性能与可观测性
- [[entities/cloudnativepg]] — Kubernetes 中管理 PostgreSQL 集群生命周期的 Operator
- [[entities/deepseek]] — 开放权重 MoE 大模型提供商，以 DeepSeek V4 Flash 的本地推理友好性著称
- [[entities/duckdb]] — 面向分析型负载的进程内数据库，DuckLake 的创建者与参考实现
- [[entities/ducklake]] — 数据格式实体，把元数据全部交给 SQL 数据库管理的 lakehouse 格式
- [[entities/posthog]] — 全栈开发者平台，提供产品分析、Feature Flags、A/B 测试、数据仓库，同时用 Postgres + ClickHouse + DuckDB 三数据库栈
- [[entities/clickhouse-keeper]] — ClickHouse 的原生协调服务，面向复制与分布式 DDL
- [[entities/hdfs]] — Hadoop 生态里的分布式文件系统，用 block、副本和 NameNode / DataNode 组织大数据存储
- [[entities/ilink]] — 微信 iLink API，面向 Bot 开发者的长轮询消息接口
- [[entities/kubernetes]] — 以声明式 API、调度器和控制器构成的容器编排系统
- [[entities/managed-agents]] — Anthropic 的托管式长程 agent 运行时产品
- [[entities/markus-winand]] — 以 SQL 索引与执行计划教学著称的数据库作者
- [[entities/nodejs]] — JavaScript 服务端运行时，也是 ESM / CommonJS 迁移路径的关键中间层
- [[entities/paul-graham]] — Y Combinator 创始人，关于如何做出伟大工作、识别假工作与时间陷阱的思考者
- [[entities/envoy]] — 开源 L7 代理与通信总线，服务网格的数据面标准实现
- [[entities/oh-my-openagent]] — OpenCode 插件，将单一会话扩展为多模型 specialist 并行编排的运行时
- [[entities/opencode]] — 面向开发者的 AI 编程 Agent 工具，支持 TUI、Web 与桌面端，强调人主导、Agent 协作
- [[entities/thinking-machines-lab]] — Ilya Sutskever 创立的研究实验室，致力于安全 AGI 与 interaction models
- [[entities/traefik]] — 云原生反向代理与负载均衡器，Kubernetes ingress 的主流选择
- [[entities/openclaw]] — 面向 AI agent 的网关与插件框架，支持多通道多 Agent 协同
- [[entities/oss-hdfs]] — 阿里云 OSS 上兼容 HDFS 接口的数据湖存储服务
- [[entities/qmd]] — 面向 markdown 与 agent 工作流的本地搜索引擎
- [[entities/vannevar-bush]] — 1945 年 Memex 构想提出者，LLM Wiki 的精神先驱
- [[entities/zookeeper]] — 经典分布式协调服务，在 ClickHouse 里主要作为 Keeper 的对照基线

## 来源

- [[sources/agent-bridge-design]] — Agent Bridge 的设计与实现：从 OpenClaw 微信插件到通用 Channel-Agent 桥接层（2026-04-29，项目文档）
- [[sources/building-effective-ai-agents]] — Anthropic 的 agent 工程文章（2026-04-13，网络文章）
- [[sources/ack-node-scaling]] — 阿里云 ACK 关于节点自动伸缩与节点即时弹性的概览（2026-04-28，网络文章）
- [[sources/ack-static-disk-volume]] — ACK 静态云盘存储卷：手动 PV/PVC 绑定、节点亲和性与 RWO 约束（2026-05-26，网络文章）
- [[sources/ack-dynamic-disk-volumes]] — ACK 动态云盘存储卷：StorageClass、volumeClaimTemplates 与生产检查单（2026-05-26，网络文章）
- [[sources/ack-disk-volume-snapshots]] — ACK 云盘快照与恢复：VolumeSnapshot API、动态/静态快照与极速可用（2026-05-26，网络文章）
- [[sources/cnpg-recovery-incident]] — CNPG 事故恢复与存储策略复盘：从 Retain PV、快照恢复到主从同步验证（2026-05-26，会话复盘）
- [[sources/aliyun-oss-hdfs-notice]] — 阿里云 OSS-HDFS 使用前须知，强调 `.dlsdata/` 内部目录和 OSS 功能冲突风险（2026-04-28，网络文章）
- [[sources/aliyun-oss-hdfs-overview]] — 阿里云 OSS-HDFS / JindoFS 服务概览，说明 HDFS 接口如何接入对象存储数据湖（2026-04-28，网络文章）
- [[sources/altinity-converting-mergetree-to-replicated]] — Altinity 关于把 `MergeTree` 转为 `ReplicatedMergeTree` 的实务路线图（2026-04-16，网络文章）
- [[sources/clickhouse-13-mistakes]] — ClickHouse 官方总结的 13 个入门常见误区（2026-04-26，网络文章）
- [[sources/clickhouse-attach-as-replicated]] — ClickHouse `ATTACH ... AS REPLICATED` 文档，强调本地数据与复制元数据分离（2026-04-16，网络文章）
- [[sources/clickhouse-cloud-architecture]] — ClickHouse Cloud 官方架构文档：对象存储打底、自动扩缩容、compute-compute separation 与服务隔离（2026-05-13，网络文章）
- [[sources/clickhouse-shared-merge-tree]] — ClickHouse SharedMergeTree 引擎文档：Cloud 架构下 ReplicatedMergeTree 的云原生替代，共享存储 + Keeper 元数据 + 异步 leaderless 复制（2026-05-13，网络文章）
- [[sources/clickhouse-cold-hot-storage]] — ClickHouse 在 Kubernetes 中用阿里云 OSS、cache disk 与 TTL move 实现冷热分层的实践笔记（2026-04-27，网络文章）
- [[sources/clickhouse-external-disks-for-storing-data]] — ClickHouse 外部存储与文件缓存文档（2026-04-16，网络文章）
- [[sources/clickhouse-go-configuration]] — clickhouse-go 客户端配置：连接池、多节点策略、压缩与 TCP/HTTP 协议选择（2026-05-13，网络文章）
- [[sources/clickhouse-issue-20867]] — ClickHouse issue 讨论 `ReplicatedReplacingMergeTree` 中 replacement、version 列与 insert deduplication 的边界（2021-02-18，GitHub issue）
- [[sources/advanced-load-balancing-traefik]] — Traefik Proxy 高级负载均衡实战：WRR、流量镜像、粘性会话与嵌套健康检查（2022-10-06，网络文章）
- [[sources/clickhouse-keeper]] — ClickHouse Keeper 文档，聚焦配置、兼容边界与迁移要点（2026-04-16，网络文章）
- [[sources/choosing-load-balancing-strategy]] — 负载均衡策略选择决策树：WRR、P2C、HRW、Least-Time 的适用场景与组合策略（2026-02-06，网络文章）
- [[sources/clickhouse-manage-and-deploy]] — ClickHouse 部署与运维文档总览（2026-04-16，网络文章）
- [[sources/clickhouse-multi-region-replication]] — ClickHouse 多地域复制 FAQ（2026-04-16，网络文章）
- [[sources/clickhouse-operator-introduction]] — ClickHouse Operator 入门文档，强调生产使用 `Replicated` 数据库引擎（2026-04-16，网络文章）
- [[sources/clickhouse-parallel-replicas]] — ClickHouse Parallel Replicas 指南：无分片架构下用 granule 级任务调度实现查询并行化（2026-05-13，网络文章）
- [[sources/clickhouse-production-v4-tencent-cloud-validation]] — ClickHouse production-v4 在腾讯云 TKE / CBS / COS 形态下的生产迁移验证与资源口径（2026-05-06，项目文档）
- [[sources/clickhouse-query-cache]] — ClickHouse 查询缓存文档（2026-04-15，网络文章）
- [[sources/clickhouse-replicated-table-engines]] — ClickHouse 复制引擎文档，说明从 `MergeTree` 迁移到 `ReplicatedMergeTree` 的官方路径（2026-04-16，网络文章）
- [[sources/clickhouse-replication-and-scaling]] — ClickHouse 分片与多副本集群示例（2026-04-16，网络文章）
- [[sources/clickhouse-separation-storage-compute]] — ClickHouse 存算分离与 S3 架构指南（2026-04-16，网络文章）
- [[sources/ducklake-manifesto]] — DuckLake 宣言：为什么 lakehouse 元数据应该放在数据库里而不是 JSON 文件里（2026-06-11，网络文章）
- [[sources/ducklake-v1-0-announcement]] — DuckLake v1.0 发布说明，包含 Data Inlining、Sorted Tables、Bucket Partitioning、Variant 类型等生产级功能（2026-04-13，网络文章）
- [[sources/duckdb-vs-clickhouse-posthog]] — PostHog 同时使用 DuckDB 和 ClickHouse 的原因对比（2026-05-01，网络文章）
- [[sources/duckdb-vs-postgres]] — DuckDB 与 Postgres 的 OLAP vs OLTP 详细对比（2026-06-13，网络文章）
- [[sources/duckdb-vs-sqlite]] — DuckDB 与 SQLite 的嵌入式数据库对比：OLAP vs OLTP（2026-06-13，网络文章）
- [[sources/agent-first-product-engineering]] — PostHog 的 agent-first 产品设计五原则（2026-06-13，网络文章）
- [[sources/ds4-readme]] — antirez 的 DeepSeek V4 Flash 专用推理引擎，聚焦非对称量化、磁盘 KV cache 与官方向量验证（2026-05-09，项目文档）
- [[sources/harness-vs-platform-engineering]] — Harness Engineering 与 Platform Engineering 的分层架构：agentic 系统的三层参考架构与治理引力陷阱（2026-05-08，网络文章）
- [[sources/databricks-what-is-hdfs]] — Databricks 对 HDFS 的基础介绍，聚焦 block、副本、NameNode 与 DataNode（2021-12-08，网络文章）
- [[sources/epoch-semantic-versioning]] — Anthony Fu 提出的 Epoch SemVer，用现有 SemVer 三段式表达 epoch 与技术破坏性变化（2026-04-28，网络文章）
- [[sources/how-we-built-our-multi-agent-research-system]] — Anthropic 关于 Research 多智能体系统的复盘（2026-04-13，网络文章）
- [[sources/interaction-models]] — Thinking Machines Lab 的 interaction model 研究预览：原生实时多模态交互与双模型架构（2026-05-11，网络文章）
- [[sources/introducing-the-clickhouse-query-cache]] — ClickHouse Query Cache 的设计与早期使用解读（2023-02-09，网络文章）
- [[sources/kubernetes-autoscaling-workloads]] — Kubernetes 官方关于 HPA、VPA、KEDA 与工作负载伸缩的概念页（2025-11-23，网络文章）
- [[sources/llm-wiki]] — LLM Wiki 模式论文（Karpathy，2026-04-13，网络文章）
- [[sources/oh-my-openagent]] — oh-my-openagent 架构分析：5 步初始化、category 路由、模型 fallback、后台任务与 3 层 MCP（2026-05-09，代码分析）
- [[sources/move-on-to-esm-only]] — Anthony Fu 关于 ESM-only 时机、dual format 成本与 Node.js `require(ESM)` 的生态判断（2026-04-28，网络文章）
- [[sources/oneuptime-replicated-replacingmergetree]] — OneUptime 关于 `ReplicatedReplacingMergeTree` 标准建模、`FINAL` 与副本健康检查的教程（2026-03-31，网络文章）
- [[sources/oneuptime-clickhouse-export-file-formats]] — OneUptime 关于 ClickHouse 导出格式、客户端落点、HTTP 导出和 S3 表函数的指南（2026-03-31，网络文章）
- [[sources/qmd]] — QMD README（tobi/qmd，2026-04-13，项目文档）
- [[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]] — Anthropic 关于 Managed Agents 运行时架构的文章（2026-04-13，网络文章）
- [[sources/use-the-index-luke-anatomy-of-an-index]] — Use The Index, Luke 的索引结构章节（2026-04-14，书籍章节）
- [[sources/what-is-envoy]] — Envoy 官方文档：进程外架构、过滤器链、xDS 动态配置与服务网格设计哲学（envoy 1.39.0-dev，官方文档）
- [[sources/use-the-index-luke-clustering-data]] — Use The Index, Luke 的聚簇与覆盖索引章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-execution-plans]] — Use The Index, Luke 的执行计划附录（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-modifying-data]] — Use The Index, Luke 的写入与索引维护章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-myth-directory]] — Use The Index, Luke 的性能误区附录（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-partial-results]] — Use The Index, Luke 的分页与 Top-N 章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-preface]] — Use The Index, Luke 的前言（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-sorting-and-grouping]] — Use The Index, Luke 的排序与分组章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-testing-and-scalability]] — Use The Index, Luke 的可扩展性章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-the-join-operation]] — Use The Index, Luke 的连接章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke-the-where-clause]] — Use The Index, Luke 的 `where` 子句章节（2026-04-14，书籍章节）
- [[sources/use-the-index-luke]] — Markus Winand 的 SQL 索引与性能教程总览（2026-04-14，书籍总览）
- [[sources/opencode-usage-tips]] — OpenCode 使用技巧与最佳实践：上下文管理、AGENTS.md、配置层级与子 Agent 信息传递（2026-05-19，网络文章）
- [[sources/paul-graham-great-work]] — Paul Graham 关于如何做出伟大工作的四步方法论：好奇心、前沿、裂缝与探索（2026-06-13，网络文章）
- [[sources/paul-graham-lose-time-and-money]] — Paul Graham 关于假工作与时间陷阱的类比：为什么假工作比娱乐更危险（2026-06-13，网络文章）
- [[sources/clickhouse-optimize-aggregation-in-order]] — `optimize_aggregation_in_order` 设置专项讲解：利用 MergeTree 排序顺序做流式聚合的内存优化（2026-03-31，网络文章）
- [[sources/clickhouse-query-optimization-guide]] — ClickHouse 官方查询优化权威指南：ORDER BY 设计、数据类型、projection、物化视图、skip index（2026-05-20，网络文章）
