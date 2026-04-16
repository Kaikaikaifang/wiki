---
title: 整体综述
type: overview
tags: [方法论, 知识管理]
source_count: 18
updated: 2026-04-16
---

# 整体综述

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

## 当前关注

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

## 演化轨迹

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

---

相关页面：[[index]] · [[topics/llm-wiki-pattern]] · [[topics/local-first-search]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/multi-agent-systems]] · [[topics/long-horizon-agents]] · [[topics/sql-indexing]] · [[topics/sql-execution-plans]] · [[topics/query-shape-and-index-usage]] · [[topics/query-result-caching]] · [[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-keeper-vs-zookeeper]] · [[topics/clickhouse-replicated-engines-and-conversion]] · [[topics/clickhouse-single-node-to-cluster-migration]] · [[entities/qmd]] · [[entities/anthropic]] · [[entities/managed-agents]] · [[entities/markus-winand]] · [[entities/clickhouse]] · [[entities/clickhouse-keeper]] · [[sources/clickhouse-replication-and-scaling]] · [[sources/clickhouse-keeper]] · [[sources/clickhouse-operator-introduction]]
