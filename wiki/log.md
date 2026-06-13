# 操作日志

> 只追加，不修改。格式：`## [YYYY-MM-DD] 操作类型 | 标题`
>
> 快速查看最近操作：`grep "^## \[" wiki/log.md | tail -10`

---

## [2026-04-13] init | wiki 初始化

创建目录结构、CLAUDE.md 模式文件、index.md、overview.md。

## [2026-04-13] ingest | LLM Wiki — Andrej Karpathy

触及页面：sources/llm-wiki、topics/llm-wiki-pattern、topics/knowledge-management、entities/andrej-karpathy、entities/vannevar-bush、index、overview。

## [2026-04-13] ingest | QMD 本地搜索引擎

触及页面：sources/qmd、entities/qmd、topics/local-first-search、topics/hybrid-retrieval、topics/llm-wiki-pattern、topics/knowledge-management、index、overview。

## [2026-04-13] workflow | 更新导入前归档规则

同步更新 AGENTS.md 与 CLAUDE.md：当用户从默认 `Clippings/` 目录处理或摄入文件时，先将文件归类移动到 `raw/` 的对应子目录，再执行后续摄入步骤；若文件已在 `raw/` 中则跳过该步骤。

## [2026-04-13] ingest | Building Effective AI Agents

触及页面：sources/building-effective-ai-agents、topics/agentic-systems、topics/agent-computer-interface、entities/anthropic、index、overview。

## [2026-04-13] ingest | How we built our multi-agent research system

触及页面：sources/how-we-built-our-multi-agent-research-system、topics/multi-agent-systems、topics/long-horizon-agents、topics/agentic-systems、topics/agent-computer-interface、entities/anthropic、index、overview。

## [2026-04-13] ingest | Scaling Managed Agents: Decoupling the brain from the hands

触及页面：sources/scaling-managed-agents-decoupling-the-brain-from-the-hands、entities/managed-agents、topics/long-horizon-agents、topics/multi-agent-systems、topics/agentic-systems、topics/agent-computer-interface、entities/anthropic、index、overview。

## [2026-04-13] workflow | 明确 tags 无空格规范

同步更新 AGENTS.md 与 CLAUDE.md：frontmatter 中的 `tags` 不允许包含空格；生成、归档与 lint 时均应统一使用无空格标签，例如 `Agent`、`提示词工程`。

## [2026-04-14] lint | 修复标签与元数据规范问题

修复 `entities/anthropic` 的非法空格标签，补齐 `entities/andrej-karpathy` 的相关页面；为 `index` 补充缺失元数据，并在 AGENTS.md 与 CLAUDE.md 中明确 `index` / `log` 作为 utility 页的规范；同时增强 `overview` 的反向链接。

## [2026-04-14] ingest | Use The Index, Luke 索引专题

摄入 `https://use-the-index-luke.com/sql/table-of-contents` 及其下 89 个索引相关章节，归档 `raw/articles/use-the-index-luke-sql-performance.md`；新增 `sources/use-the-index-luke`、`entities/markus-winand` 与 SQL 索引 / 执行计划 / 连接 / 分页 / 写入权衡等主题页，并同步更新 `index` 与 `overview`。

## [2026-04-14] wiki | 拆分 Use The Index, Luke 章节页

将 `sources/use-the-index-luke` 保留为总览入口，并拆分为前言、索引结构、`where`、可扩展性、连接、聚簇、排序分组、分页、写入代价、执行计划与误区等章节来源页，便于后续查询与交叉引用。

## [2026-04-14] lint | 修正 source_count 与 Markdown 间距

根据拆分后的章节来源页，回填相关 `topics` 的 `source_count` 与来源引用；同时按 GFM 习惯修正页尾 `来源` / `相关页面` 之间的空行，并复查 wiki 中英混排间距与 wikilink 完整性。

## [2026-04-14] lint | 补充 GFM 规范并复查 Markdown

复查 `wiki/` 与规范文件中的 Markdown 间距，仅发现 `AGENTS.md`、`CLAUDE.md` 存在少量 fenced code block 前空行问题；同时在两份规范文件中补充遵循 GFM、段落留空行、页尾段落分隔与中英混排留空格的明确要求。

## [2026-04-15] ingest | ClickHouse Query Cache 文档

摄入 `https://clickhouse.com/docs/operations/query-cache`，归档 `raw/articles/query-cache-clickhouse-docs.md`；新增 `sources/clickhouse-query-cache`、`topics/query-result-caching` 与 `entities/clickhouse`，并更新 `index` 与 `overview`，补充面向 OLAP 的查询结果缓存、一致性取舍与可观测性视角。

## [2026-04-15] ingest | Introducing the ClickHouse Query Cache

摄入 `https://clickhouse.com/blog/introduction-to-the-clickhouse-query-cache-and-design`，归档 `raw/articles/introducing-the-clickhouse-query-cache.md`；新增 `sources/introducing-the-clickhouse-query-cache`，并更新 `topics/query-result-caching`、`entities/clickhouse`、`index` 与 `overview`，补充 Query Cache 的设计动机、排障方法与演化背景。

## [2026-04-15] query | PostgreSQL 索引 DDL 的锁表现

归档关于 PostgreSQL 中 `create index` / `drop index` 是否会锁表的问答；新增 `topics/postgresql-index-ddl-locking`，总结不带 `concurrently` 时建索引通常阻塞写入、删索引更可能同时挡住读写，以及锁等待放大为排队堆积的线上表现，并补充到 `index` 与相关主题页。

## [2026-04-15] query | 服务与云数据库网络时延排查

归档关于服务访问云数据库时如何判断网络时延是否导致接口变慢的问答；新增 `topics/service-db-network-latency-diagnosis`，总结冷连接、热连接、应用侧与数据库侧双侧耗时对比、单请求 SQL 数统计，以及同集群自建库与托管云数据库的优先对比项，并补充到 `index` 与相关性能主题页。

## [2026-04-16] ingest | ClickHouse 部署与运维文档

摄入 `https://clickhouse.com/docs/guides/manage-and-deploy-index` 及相关官方文档，归档 `raw/articles/clickhouse-manage-and-deploy-overview.md`、`raw/articles/clickhouse-replication-and-scaling.md`、`raw/articles/clickhouse-separation-storage-compute.md`、`raw/articles/clickhouse-external-disks-for-storing-data.md` 与 `raw/articles/clickhouse-multi-region-replication.md`；新增 `sources/clickhouse-manage-and-deploy`、`sources/clickhouse-replication-and-scaling`、`sources/clickhouse-separation-storage-compute`、`sources/clickhouse-external-disks-for-storing-data`、`sources/clickhouse-multi-region-replication` 与 `topics/clickhouse-deployment-topologies`，并更新 `entities/clickhouse`、`index` 与 `overview`，补充分片、多副本、存算分离、冷热数据分层与多地域复制边界。

## [2026-04-16] query | DDL 与 DML 的区别

归档关于 `DDL` 与 `DML` 区别的问答；新增 `topics/ddl-vs-dml`，结合 ClickHouse 中 `ON CLUSTER` 的语境，说明 DDL 负责结构变更、DML 负责数据变更，以及为什么 `ON CLUSTER` 只同步 DDL 而不承担 DML 分发。

## [2026-04-16] ingest | ClickHouse Keeper 文档

摄入 `https://clickhouse.com/docs/guides/sre/keeper/clickhouse-keeper`，归档 `raw/articles/clickhouse-keeper.md`；新增 `sources/clickhouse-keeper`、`topics/clickhouse-keeper-vs-zookeeper`、`entities/clickhouse-keeper` 与 `entities/zookeeper`，并更新 `topics/clickhouse-deployment-topologies`、`entities/clickhouse`、`index` 与 `overview`，补充 Keeper 与 ZooKeeper 的兼容边界、迁移约束、优缺点及生产选型建议。

## [2026-04-16] ingest | ClickHouse replicated 引擎与旧表转换

摄入 `https://clickhouse.com/docs/clickhouse-operator/guides/introduction`、`https://kb.altinity.com/altinity-kb-setup-and-maintenance/altinity-kb-converting-mergetree-to-replicated/`、`https://clickhouse.com/docs/engines/table-engines/mergetree-family/replication#converting-from-mergetree-to-replicatedmergetree` 与 `https://clickhouse.com/docs/sql-reference/statements/attach#attach-mergetree-table-as-replicatedmergetree`，归档 `raw/articles/clickhouse-operator-introduction.md`、`raw/articles/altinity-converting-mergetree-to-replicated.md`、`raw/articles/clickhouse-replicated-table-engines.md` 与 `raw/articles/clickhouse-attach-as-replicated.md`；新增 `sources/clickhouse-operator-introduction`、`sources/altinity-converting-mergetree-to-replicated`、`sources/clickhouse-replicated-table-engines`、`sources/clickhouse-attach-as-replicated` 与 `topics/clickhouse-replicated-engines-and-conversion`，并更新 `topics/clickhouse-deployment-topologies`、`entities/clickhouse`、`index` 与 `overview`，补充生产环境使用 replicated 引擎的分层含义，以及旧 `MergeTree` 表迁移到 `ReplicatedMergeTree` 的主要路径与风险边界。

## [2026-04-16] query | 单节点 ClickHouse 迁移到集群

归档关于“多副本多分片集群里是否仍可使用 `MergeTree`、单节点生产环境迁到集群能否无缝切换、能否在迁移时一并完成表引擎切换，以及迁移过程中需要完成哪些工作”的问答；新增 `topics/clickhouse-single-node-to-cluster-migration`，并更新 `index` 与 `overview`，明确区分 `MergeTree` 的可用性与适用性，补充业务侧平滑切换与数据库内部迁移工程之间的边界。

## [2026-04-16] workflow | 统一页面命名与标题元信息规范

更新 `AGENTS.md` 与 `CLAUDE.md` 的页面规范，明确文件名使用简短英文连字符命名、frontmatter 的 `title` 使用简短中文标题，并规定 frontmatter 后不再重复同名一级标题。

## [2026-04-16] wiki | 清理历史页面标题与格式

批量清理 `wiki/` 历史页面：统一将 frontmatter 的 `title` 改为简短中文标题，移除 frontmatter 后重复的同名一级标题，并同步更新 `updated` 日期；文件名未批量重命名，因为现有命名整体已符合英文连字符规则，且避免为压缩长度而打断既有历史引用。

## [2026-04-16] wiki | 简化 Use The Index, Luke 标题

更新 `wiki/sources/use-the-index-luke*.md` 这一批来源页的 frontmatter `title`，去掉 `Use The Index, Luke` 来源名前缀，仅保留简短中文概括，避免标题重复携带来源信息。

## [2026-04-16] workflow | 新增博客式写作规范

更新 `AGENTS.md` 与 `CLAUDE.md`，要求所有 markdown 文档默认按个人技术博客写法撰写：采用技术博主视角组织内容，强调问题意识、直觉、判断、叙事与可读性，避免退化为中性词条式摘要；同时保留 `wiki/log.md` 作为例外，继续使用操作日志体。

## [2026-04-16] wiki | 改写历史基础页面为博客体

按新的个人技术博客写作规范，批量改写一组历史基础页面，包括 `overview`、`topics/knowledge-management`、`topics/local-first-search`、`topics/hybrid-retrieval`、`topics/llm-wiki-pattern`、`entities/andrej-karpathy`、`entities/vannevar-bush`、`entities/qmd`、`sources/llm-wiki` 与 `sources/qmd`；统一补入作者视角、问题意识、叙述性引子与更强的判断表达，减少卡片式摘要感。

## [2026-04-16] wiki | 继续改写 SQL 与 Agent 历史页面

继续按博客体改写一批历史核心页面，包括 `topics/sql-indexing`、`topics/query-shape-and-index-usage`、`topics/sql-execution-plans`、`entities/markus-winand`、`sources/use-the-index-luke`、`entities/clickhouse`、`topics/agentic-systems`、`topics/agent-computer-interface`、`topics/multi-agent-systems`、`topics/long-horizon-agents`、`topics/clickhouse-deployment-topologies` 与 `topics/clickhouse-keeper-vs-zookeeper`；强化作者视角、技术判断与叙事性开场，减少讲义式表达。

## [2026-04-16] wiki | 继续改写短实体与来源页面

继续按博客体改写一批较短的历史页面，包括 `entities/anthropic`、`entities/clickhouse-keeper`、`entities/managed-agents`、`entities/zookeeper`、`sources/clickhouse-replicated-table-engines`、`sources/clickhouse-attach-as-replicated`、`sources/altinity-converting-mergetree-to-replicated`、`sources/clickhouse-keeper`、`sources/use-the-index-luke-clustering-data`、`sources/use-the-index-luke-modifying-data` 与 `sources/use-the-index-luke-myth-directory`；补充更明确的作者判断、背景动机与阅读引导，缩小短页与长页之间的风格落差。

## [2026-04-16] wiki | 收尾短章节来源页的博客体改写

继续按博客体改写一批章节级历史来源页，包括 `sources/use-the-index-luke-preface`、`sources/use-the-index-luke-anatomy-of-an-index`、`sources/use-the-index-luke-sorting-and-grouping`、`sources/use-the-index-luke-testing-and-scalability`、`sources/use-the-index-luke-execution-plans`、`sources/use-the-index-luke-the-join-operation`、`sources/clickhouse-manage-and-deploy`、`sources/clickhouse-operator-introduction`、`sources/clickhouse-separation-storage-compute` 与 `sources/clickhouse-multi-region-replication`；补充阅读动机、技术判断与章节定位，继续降低章节摘要感。

## [2026-04-17] wiki | 记录 ClickHouse 迁集群较短路径

把一次本地 ClickHouse 迁移演练沉淀回 `topics/clickhouse-single-node-to-cluster-migration`：补充“较短路径”小节，记录用本地 mock 单节点源验证 `MergeTree -> Replicated 数据库 + ReplicatedMergeTree + Distributed` 的最小闭环，以及连通性、权限、分片分布与副本健康这几个关键校验点。

## [2026-04-20] wiki | 记录 ClickHouse 生产迁移方案

新增 `topics/clickhouse-production-migration`，把一套面向当前单实例生产形态的 ClickHouse 迁集群方案沉淀进 wiki：明确以 `4 shards × 2 replicas` 为目标拓扑，以 `Vector` 双写兜住新增写入，以自动建表开关化避免污染目标 schema，并强调按 `projectId` 批次回灌 `7118 GiB` 级历史数据；同步更新 `index`，正文避免写入本机绝对路径。

## [2026-04-20] wiki | 补充生产迁移方案的本地验证结果

更新 `topics/clickhouse-production-migration` 与 `topics/clickhouse-single-node-to-cluster-migration`，把一次本地验证过的迁移闭环写回 wiki：用 mock 单节点源验证 `4 shards × 2 replicas + 3 Keeper` 目标集群、`Vector` 双写、`T0` 水位切分、历史回灌与副本健康检查，并补记 ClickHouse `24.3 + operator` 下 `Replicated` 数据库实验开关与 DDL 下发方式的实际注意事项。

## [2026-04-21] wiki | 泛化 ClickHouse 生产迁移页面命名

将原生产迁移页面重命名为 `topics/clickhouse-production-migration`，并同步清理索引、交叉引用与正文中的特定业务名，保留迁移拓扑、双写、水位切分与回灌策略这些可复用经验。

## [2026-04-21] wiki | 同步 ClickHouse 26.3 迁移规则

更新 `topics/clickhouse-production-migration` 与 `topics/clickhouse-single-node-to-cluster-migration`，补记一次面向 ClickHouse `26.3` 的本地重跑结果：`Replicated` 数据库已不再依赖实验开关，但 DDL 规则应调整为“建库时使用 `ON CLUSTER`，建表时在单个目标实例上执行一次，再由 `Replicated` 数据库同步元数据”，并记录该路径下的对账结果、版本信息与副本健康状态。

## [2026-04-21] query | 记录 Kubernetes API 组与 schema 误报

新增 `topics/kubernetes-api-groups-and-schema-validation`，把一次围绕 `apiVersion: v1`、core API、API group 与 `yaml-language-server` schema 假阳性的讨论沉淀进 wiki：解释为什么 `v1` 不能为了压告警而改值，为什么 core API 在 YAML 里直接写 `v1`，以及为什么多资源 Kubernetes 文件在聚合 schema 下更容易触发 `Matches multiple schemas` 这类编辑器误报。

## [2026-04-22] wiki | 记录共享集群中的 Operator 安装策略

新增 `topics/clickhouse-operator-installation-on-shared-clusters`，把一次围绕 `dev-admin` 共享集群安装官方 ClickHouse Operator 的判断沉淀进 wiki：明确推荐用 Helm 安装到独立 namespace，复用已有 `cert-manager`，通过 `watchNamespaces` 收窄到目标 namespace，并把 CRD 生命周期和卸载动作视为独立的集群级决策。

## [2026-04-22] wiki | 同步 tenant-kaikai 目标集群重建与 CRD 记录策略

更新 `topics/clickhouse-production-migration` 与 `topics/clickhouse-operator-installation-on-shared-clusters`，并新增 `topics/kubernetes-crd-recording-strategy`，把一次在 `dev-admin` 共享集群里将目标 ClickHouse 重建到 `tenant-kaikai` 的实际结果沉淀进 wiki：记录公开 ACR 镜像、`26.3` 固定版本、`high-performance` 节点 toleration、共享集群调度约束，以及“默认记录安装入口与生命周期策略，而不是直接 vendoring 上游 CRD 原文”的判断。

## [2026-04-23] wiki | 补记 dev-admin 迁移里的 Vector 双写前置条件

更新 `topics/clickhouse-production-migration`，把一次在 `dev-admin` 共享集群里的真实迁移推进结果写回 wiki：明确目标集群 `Ready` 之后不能直接倒灌，而应先在 `development` 命名空间打通 Vector 双写，再把唯一事件验证通过的时刻记为 `T0`；同时补记这次真实排障里 `media` 流未进入目标 sink 的现象，以及通过为 target sink 拆分独立 transform 恢复三张表双写一致性的做法。

## [2026-04-23] wiki | 停止 remote 回灌并切换到生产级回灌思路

更新 `topics/clickhouse-production-migration`，把一次在 `dev-admin` 共享集群里的真实历史回灌验证写回 wiki：记录 `remote() + INSERT SELECT` 在共享集群中先后暴露出的内存上限、磁盘扩容和中断残留问题，并明确在 `7 TiB` 级生产场景下，应将它降级为验证与补洞工具，而把正式主回灌方案切换为“对象存储中转 + 批次清单 + 并行导入 + 分层对账”的批处理架构。

## [2026-04-23] wiki | 补记云盘快照在生产回灌中的正确角色

更新 `topics/clickhouse-production-migration`，把一次围绕生产回灌执行清单的整理结果写回 wiki：补记 `development` 源 ClickHouse 当前本质上就是“PVC 挂载的阿里云云盘”，并进一步明确在生产环境里，云盘快照最适合作为离线历史导出源，而不是直接充当新集群迁移结果；正式主路径应是“快照克隆盘导出到对象存储，再由目标集群按批次逻辑导入”。

## [2026-04-23] wiki | 补记生产回灌的可执行骨架

更新 `topics/clickhouse-production-migration`，把这次继续落到 `test-migration` 里的生产级回灌骨架同步进 wiki：补记批次 manifest、单批导出 / 导入脚本和 Kubernetes Job 模板这三类最小可运行组件为什么值得先做，以及它们如何把“对象存储中转 + 批次清单 + 并行导入”从方案文字推进到可操作系统。

## [2026-04-23] wiki | 补记 runner 镜像与 manifest 生成器

更新 `topics/clickhouse-production-migration`，把这次继续落到 `test-migration` 里的执行入口同步进 wiki：补记为什么生产回灌除了单批导出 / 导入脚本和 Job 模板，还需要一层 runner 镜像定义以及 manifest 生成器，以及它们如何把“批次定义”和“批次执行”从手工拼装变成统一入口。

## [2026-04-23] wiki | 补记生产回灌最小控制面

更新 `topics/clickhouse-production-migration`，把这次继续落到 `test-migration` 里的控制面约定同步进 wiki：补记回灌 Job 依赖的最小 `ConfigMap/Secret` 命名、批次状态表 `migration_meta.backfill_batches` 的最小 schema，以及 `manifest` 生成器已经支持直接从 ClickHouse 拉项目清单，意味着这条生产回灌路径已经从执行骨架进入最小控制面阶段。

## [2026-04-24] wiki | 补记生产回灌的真实批量验证结果

更新 `topics/clickhouse-production-migration`，并同步把 `test-migration` 里的生产回灌文档补齐：记录这条“快照恢复源 -> OSS 中转 -> 目标 Distributed 表”主路径在 `dev-admin` 里的真实推进结果，包括 `2026-04-22` 的 `18` 个非空小时、`2026-04-19` 的 `10` 个有效小时已经完整对齐，以及 `2026-04-18` 这类连续重负载日截至当日已稳定通过前 `12` 个小时；同时固化空批次 `13 B` 过滤、导出 / 导入目录分离和 `project-list` 空列错位这几条执行纪律。

## [2026-04-26] query | 记录生产回灌自动化控制面判断

更新 `topics/clickhouse-production-migration`，把一次围绕“OSS 中转回灌已验证可行，但在 `dev-admin` 中仍耗时很长且无法完全自动化”的讨论沉淀进 wiki：明确问题不在 OSS 数据面，而在缺少批次状态、自动领取、失败重试、空批次跳过、目录隔离、自动对账和按表 / shard 限流的最小控制面；同时记录 `remote()`、快照恢复和 `ATTACH PART` 仍应作为验证、导出源或补洞工具，而不是替代面向新分片布局的正式批处理回灌。

## [2026-04-26] wiki | 补记生产量级回灌为何还需继续升级

更新 `topics/clickhouse-production-migration`，并同步把 `test-migration` 里的新文档补齐：明确“快照恢复源 -> OSS -> 小时级批次 -> 目标导入”已经被验证可行，但还不足以直接支撑 `scalar 2973.95 亿`、`log 1287.73 亿` 这一档生产历史数据的最终自动化回灌；同时把两条正式生产路径沉淀下来，一条是“热数据优先切流，深历史后台慢迁”，另一条是“若必须全历史先入新集群，则升级成 shard-aware 回灌平台”，并把最优先的三项升级固定为按 shard 直写 `*_local`、多快照克隆并行导出和“日期 x shard + 自动 split”的主批次模型。

## [2026-04-26] ingest | ClickHouse 入门 13 个误区

摄入 ClickHouse 官方文章 `Getting started with ClickHouse? 13 mistakes and how to avoid them`，将剪藏归档到 `raw/articles/clickhouse-13-mistakes.md`，新增 `sources/clickhouse-13-mistakes` 与 `topics/clickhouse-common-pitfalls`，并更新 ClickHouse 实体、部署拓扑、Keeper 选型、SQL 索引、查询形状和 join 性能页面。核心沉淀是：ClickHouse 常见入门事故背后不是单个配置问题，而是没有顺着 part 合并、稀疏主键、Keeper 协调和内存治理这些物理约束设计系统。

## [2026-04-26] query | 澄清按 projectId 分片与物理落点的区别

更新 `topics/clickhouse-production-migration`，把一次围绕“能否先把旧单机 `attach` 成一个 replicated shard，再让新数据继续按 `projectId` 写入集群”的讨论沉淀进 wiki：明确 shard key 决定的是未来写入路由，而不是历史数据当前的物理落点；如果旧历史只是整体挂到 shard1，那么某些按 hash 理应属于 shard2 的项目会出现“历史在 shard1、新增在 shard2”的裂缝，这意味着 `attach + replicated` 最多只能充当过渡态，不能等价成已经完成真正的按键分片。

## [2026-04-26] query | 澄清 copier 的一致性前提与快照源角色

更新 `topics/clickhouse-production-migration`，把一次围绕 `clickhouse-copier` 的讨论沉淀进 wiki：明确 README 里“source tables and partitions should not change”约束的是 copier 正在读取的那份源，而不是整个生产系统都必须停写；因此在更稳的生产时序里，应由 `T0` 之后恢复出来的只读快照源承担 copier 的历史复制，而让线上热库继续写入并通过 `Vector` 双写守住 `T0` 之后的新增数据，最后只对边界尾巴做补数与对账。

## [2026-04-26] query | 更新生产资源规格与首发拓扑判断

更新 `topics/clickhouse-production-migration`，把一次围绕“生产环境资源规格应该如何设计”的讨论沉淀进 wiki：在确认机器数并不受限于当前 4 台节点后，把首发生产拓扑判断从早期偏保守的 `4 shards × 2 replicas` 升级为 `6 shards × 2 replicas + 3 Keeper`，并明确推荐数据节点按 `32 vCPU / 128 GiB / 3~4 TiB SSD` 规划、Keeper 按 `4 vCPU / 16 GiB` 独立部署；同时把 spot 节点不再适合承载正式数据面，以及 `dev-admin` 应尽量保持多分片多副本逻辑拓扑这两条执行纪律一并记下。

## [2026-04-26] query | 补记 copier 的定位与 T0 双写优先级

更新 `topics/clickhouse-production-migration`，把两条这轮会话里已经明确的判断继续沉淀进 wiki：第一，`clickhouse-copier` 即使支持 reshard，也更适合作为 `dev-admin` 或离线快照源上的实验工具，而不应继续作为正式生产主引擎；第二，相比“等历史复制结束到 `T1` 再开启双写”，更稳的正式时序应当把双写尽量前置到 `T0`，让快照 / copier 只负责 `T0` 之前的静态历史，避免 `T0 ~ T1` 的 gap 重新长成第二场大回灌。

## [2026-04-26] wiki | 新建精简版生产迁移目录

更新 `topics/clickhouse-production-migration`，并同步整理迁移资料目录：不再继续把新的正式迁移判断耦合在旧的本地验证、`remote()` 试验和 OSS 批次骨架材料上，而是单独拆出一套精简版正式路径，只保留一条主时序 `T0 双写 + 静态快照源 + 历史回灌 + 小尾巴补数`，以及配套的顺序执行文档、目标集群示例 manifest、双写配置示例和最小脚本入口。

## [2026-04-27] ingest | ClickHouse Issue 20867

摄入 GitHub issue `ReplicatedReplacingMergeTree replaces only when the new value is bigger`，新增 `sources/clickhouse-issue-20867` 并归档到 `raw/articles/clickhouse-issue-20867.md`；同步更新 ClickHouse 常见误区、复制引擎与实体页。核心沉淀是：`ReplacingMergeTree` 的 replacement、version 列与 replicated insert deduplication 是三层不同机制，做每日快照或最后状态表时必须拆开设计业务 key、版本信号和插入唯一性。

## [2026-04-27] ingest | OneUptime ReplicatedReplacingMergeTree 教程

摄入 OneUptime 文章 `How to Use ReplicatedReplacingMergeTree in ClickHouse`，新增 `sources/oneuptime-replicated-replacingmergetree` 并归档到 `raw/articles/oneuptime-replicated-replacingmergetree.md`；同步更新 ClickHouse 复制引擎、常见误区、部署拓扑与实体页。核心沉淀是：`ReplicatedReplacingMergeTree` 的标准用法应把 `ORDER BY` 作为逻辑身份、version 作为新旧顺序、Keeper 宏与 `system.replicas` 作为复制运行面，而 `FINAL` / `OPTIMIZE FINAL` 只是显式支付成本换取去重可见性或维护收敛。

## [2026-04-27] workflow | 修正 OneUptime 剪藏归档

将仍停留在 `Clippings/` 的 `How to Use ReplicatedReplacingMergeTree in ClickHouse.md` 移动并覆盖到 `raw/articles/oneuptime-replicated-replacingmergetree.md`，让本次摄入的原始资料回到真实 Obsidian Web Clipper 剪藏，而不是网页抓取摘要。

## [2026-04-27] query | 补记 clickhouse-copier 验证失败结论

更新 `topics/clickhouse-production-migration`，把这轮 `dev-admin` 上的 `clickhouse-copier` 验证结论正式沉淀下来：`final` 版本工具虽然能连上静态源、Keeper 和目标集群，也能走到 piece 表创建和少量写入阶段，但它会与 `Replicated` 数据库 DDL 语义冲突，并在 `24.3` 工具到 `26.3` 目标端链路上继续暴露协议兼容问题，因此不再作为正式生产历史回灌主路径候选。

## [2026-04-27] wiki | 精简 ClickHouse 生产迁移页

整理 `topics/clickhouse-production-migration`，把连续追加形成的本地验证、`remote()` 试验、OSS 回灌骨架、copier 讨论和生产资源判断收敛成当前有效主线：`6 x 2 + 3 Keeper` 目标拓扑、`T0` 双写前置、静态源到对象存储再导入的历史回灌、shard-aware 生产升级，以及被降级为验证或实验工具的 `remote()`、`clickhouse-copier` 和 `ATTACH` 路线。

## [2026-04-27] query | 统一三张表的回灌方案

更新 `topics/clickhouse-production-migration`，把 `scalar`、`log`、`media` 从“分表治理”调整为统一回灌方案：三张表共享同一个控制面、批次模型、状态机、重试、split、对账和完成判定，只在并发、split 阈值、导入配额等参数上体现数据量差异，避免生产迁移时维护三套执行纪律。

## [2026-04-27] query | 移除生产回灌里的草图口径

更新 `topics/clickhouse-production-migration`，明确所有回灌方案设计都必须面向生产执行，不保留手写取模 shard 路由等草图口径；目标 shard 必须来自目标 `Distributed` 表真实 sharding key、`system.clusters` 的 shard 顺序与 weight，或者直接交给 `Distributed` 表路由，只有通过等价性验证后才允许直写 `*_local`。

## [2026-04-27] query | 明确全量历史闭环与冷热分层

更新 `topics/clickhouse-production-migration`，把生产切流门槛收紧为历史数据完全回灌并对账后新集群才有资格接管流量；同时取消 `archive-only` 分叉，改为全量历史进入新集群，再通过 ClickHouse 冷热分层、对象存储和缓存策略降低长期存储成本，PostgreSQL 已删除项目 / 实验清单只作为冷数据占比评估与迁移后抽样观测输入。

## [2026-04-27] query | 澄清 OSS 中转与冷热分层顺序

更新 `topics/clickhouse-production-migration`，明确回灌阶段的 OSS 是中转层而不是冷层本身：历史数据仍然先从静态源导出到 OSS，再由导入任务按批写入目标 ClickHouse 集群；冷热分层的数据沉积是导入后的后续过程，由目标表 storage policy、分区 / TTL、后台移动和访问热度共同决定。

## [2026-04-27] query | 评估 scalar 与 media 去重引擎

更新 `topics/clickhouse-production-migration`，把 `scalar_local` 和 `media_local` 切换为 `ReplicatedReplacingMergeTree` 的生产判断写入目标 schema 设计：它可用于同一实验、同一指标、同一 `step` 的重复打点收敛，但必须先定义业务去重 key 与 version 列，并明确这是后台 merge 收敛语义，不是实时唯一约束；`log` 不跟随切换。

## [2026-04-27] ingest | ClickHouse 冷热分层实战

摄入 `clickhouse-cold-hot-storage` 剪藏，新增 `sources/clickhouse-cold-hot-storage` 并归档到 `raw/articles/clickhouse-cold-hot-storage.md`；同步更新 ClickHouse 部署拓扑、生产迁移、实体页与整体综述。核心沉淀是：冷热分层不是单纯配置 S3，而是要把 OSS virtual hosted endpoint、Secret 注入、cache disk、storage policy、TTL move、`system.parts.disk_name` 与冷 / 热查询体感一起验证；在生产迁移里，它应作为全量历史导入后的长期成本治理机制，而不是替代回灌与对账的捷径。

## [2026-04-27] query | 更新 ClickHouse production-v3 迁移资源口径

更新 `topics/clickhouse-production-migration`，把 `test-migration/production-v3` 的当前资源设计沉淀为正式执行口径：`6 x 2 + 3 Keeper` 目标集群、`Vector` T0 双写、`VolumeSnapshot` 恢复只读静态源、OSS 中转回灌、统一 runner / verifier、冷热分层配置与状态表。根据生产项目生命周期统计，把首版冷热 TTL 从 `180d` 收紧为 `createdAt + 30 DAY TO VOLUME 'cold'`，不设置删除 TTL，后续再由查询日志决定是否对 `media` 或 `log` 单独收紧。

## [2026-04-28] ingest | Kubernetes 弹性伸缩

摄入 `Autoscaling Workloads` 与 ACK `节点伸缩` 两篇剪藏，新增 `sources/kubernetes-autoscaling-workloads`、`sources/ack-node-scaling`、`topics/kubernetes-autoscaling` 与 `entities/kubernetes`，并归档原文到 `raw/articles/`。核心沉淀是：Kubernetes 弹性伸缩必须分成 workload 层和 node 层理解；HPA、VPA、KEDA 改变副本或 Pod 资源，节点伸缩则围绕不可调度 Pod、节点池、调度约束、PDB 和云厂商库存补容量。

## [2026-04-28] ingest | HDFS 与 OSS-HDFS

摄入 clippings 中 HDFS 相关 3 篇来源，新增 `sources/databricks-what-is-hdfs`、`sources/aliyun-oss-hdfs-overview`、`sources/aliyun-oss-hdfs-notice`、`topics/hdfs-and-oss-hdfs`、`entities/hdfs` 与 `entities/oss-hdfs`，并归档到 `raw/articles/`。核心沉淀是：传统 HDFS 用 NameNode / DataNode、block 和副本解决本地集群时代的大文件存储；OSS-HDFS 保留 HDFS 接口语义并接入 OSS 对象存储，但 `.dlsdata/` 内部目录、生命周期、版本控制、Bucket Policy 和 RAM 角色都成为新的生产边界。

## [2026-04-28] ingest | Epoch Semantic Versioning

摄入 Anthony Fu 的 `Epoch Semantic Versioning`，新增 `sources/epoch-semantic-versioning`、`topics/software-versioning` 与 `entities/anthony-fu`，并归档到 `raw/articles/epoch-semantic-versioning.md`。核心沉淀是：版本号是维护者、用户和包管理器之间的升级风险沟通信号；Epoch SemVer 在不改变现有 SemVer 工具链的前提下，用 `{EPOCH * 1000 + MAJOR}.MINOR.PATCH` 拆开技术破坏性变化与时代级变化，作为长期 `v0` 和过度膨胀 major 之间的折中。

## [2026-04-28] query | 验证 ClickHouse production-v3 迁移资源

验证 `test-migration/production-v3` 的 `dev-admin` 缩配资源：`3 x 2 + 3 Keeper` 目标集群 Ready，静态源由快照 `s-bp1b3lo6gyodshti9o0a` 恢复，独立冷层 bucket `swanlab-clickhouse-cold-layer.oss-cn-hangzhou-internal.aliyuncs.com` 可写，`cold_oss` / `s3_cache` / `hot_cold_policy` 生效。目标 schema 与回灌控制表可创建，三张目标表复制状态正常，并完成从静态源各抽样 `3` 行写入目标 `Distributed` 表的端到端验证；真实 runner 镜像、批次调度、OSS 中转导出 / 导入和自动对账仍未解除占位。

## [2026-04-28] ingest | Move on to ESM-only

摄入 Anthony Fu 的 `Move on to ESM-only`，新增 `sources/move-on-to-esm-only`、`topics/javascript-module-systems` 与 `entities/nodejs`，并归档到 `raw/articles/move-on-to-esm-only.md`；同步更新 Anthony Fu 实体页、索引与整体综述。核心沉淀是：ESM-only 的成熟不是单一语法偏好，而是 Vite 等现代工具链、Node.js `require(ESM)` 互操作能力、以及 dual CJS / ESM 维护成本共同推动出的生态迁移判断。

## [2026-04-28] ingest | ClickHouse 导出文件格式

摄入 OneUptime 的 `How to Export ClickHouse Data to Different File Formats`，新增 `sources/oneuptime-clickhouse-export-file-formats` 与 `topics/clickhouse-data-export`，并归档到 `raw/articles/oneuptime-clickhouse-export-file-formats.md`；同步更新 ClickHouse 实体页、生产迁移页、索引与整体综述。核心沉淀是：ClickHouse 导出要拆开格式和通道，`FORMAT` 决定序列化，`INTO OUTFILE`、HTTP、`clickhouse-client` 和 `s3()` 决定结果落点；生产回灌优先 `Native + zstd`，数据湖交换再优先 `Parquet + zstd`。

## [2026-04-29] query | ClickHouse 回灌 cursor 与多 lane 提速

更新 `topics/clickhouse-production-migration`、`topics/query-shape-and-index-usage` 与 `topics/clickhouse-data-export`，把 `scalar` 回灌第 `99` 批的性能定位沉淀为当前判断：慢点不在目标导入或 OSS 备份，而在静态源导出 cursor 没有命中主键裁剪；`tuple(...) > tuple(...)` 在 ClickHouse `24.3` 上退化为大范围扫描，展开成字典序 `OR` 后才能把读取量从十亿行级别降回二千万行级别。多 lane 提速必须基于互斥 key range 和独立 cursor，当前只读验证证明相邻 lane 覆盖 40M 行且 overlap 为 `0`，但端到端导入验证前仍不进入 `validation` 口径。

## [2026-04-29] ingest | Agent Bridge 设计与实现

摄入 `test-weixin/bridge` 项目，新增 `sources/agent-bridge-design`、`topics/agent-bridge`、`entities/openclaw` 与 `entities/ilink`，并更新 `index` 与 `overview`。核心沉淀是：从深度绑定 OpenClaw 网关的微信插件，演进为独立的 Channel-Agent 轻量桥接器，用配置驱动的多对多路由、本地状态存储和安全默认值，让个人开发者能在不依赖完整网关框架的前提下，直接用微信消息或终端交互驱动本机 CLI Agent。

## [2026-04-30] query | ClickHouse scalar 多 lane 回灌方案

归档 `scalar` 多 lane 自动回灌经验，新增 `topics/clickhouse-scalar-multilane-backfill` 并更新索引。核心沉淀是：大表回灌的速度先取决于 cursor 是否命中主键裁剪，再取决于 lane 边界是否互斥和目标集群是否能消化导入；当前 `2 lanes x 20M` 是稳定无人值守策略，`4 lanes x 20M` 只适合有人监控时追求更快完成。

## [2026-05-01] query | 记录 ClickHouse 最终水位迁移方案

更新 `topics/clickhouse-production-migration`，把最终验证流程收敛为显式 `S0` / `T0` 双水位：先给原始源打快照并记录 `S0`，再开启 `Vector` 双写并用唯一事件确认 `T0`；静态源只负责 `S0` 之前历史，原始源单独补 `(S0, T0)` 缺口，双写负责 `T0` 之后新增。同步记录三张表分别计算缺口，并在历史回灌、缺口补数和对账中统一排除垃圾项目 `projectId = 'l3baiq5daqucvtypcd2y0'`。

## [2026-05-06] ingest | ClickHouse production-v4 腾讯云验证

摄入 production-v4 的腾讯云 TKE 验证文档，新增 `sources/clickhouse-production-v4-tencent-cloud-validation` 并更新 `topics/clickhouse-production-migration`。核心沉淀是：在 CBS 热盘 + COS 冷层前置的前提下，首发目标从早期偏保守的多 shard 规划收敛为 `2 shards x 2 replicas + 3 Keeper`，单 ClickHouse Pod 以 `16C / 64GiB / 2TiB` 起步；后续优先纵向升配到 `32C / 128GiB`，不先增加 shard。同步记录腾讯云落地时要先验证 Operator 镜像拉取、节点形态、CBS 持久化、COS endpoint 与 Secret 交付这些基础设施边界。

## [2026-05-09] ingest | ds4.c 推理引擎

摄入 `https://github.com/antirez/ds4/blob/main/README.md`，归档 `raw/articles/ds4-readme.md`；新增 `sources/ds4-readme`、`entities/antirez`、`entities/deepseek` 与 `topics/local-llm-inference`，并更新 `topics/ai-agent-harness`、`index` 与 `overview`。核心沉淀是：本地推理不是云端降级版，而是一组独立约束下的重新优化；antirez 的「窄赌注」——一次只做一个模型、做官方向量验证、追求端到端可信——和非对称量化、磁盘 KV cache、OpenAI/Anthropic 兼容 API 共同构成了一条新的 agent 后端路径。

## [2026-05-09] ingest | oh-my-openagent 架构分析

触及页面：`sources/oh-my-openagent`、`entities/oh-my-openagent`、`topics/ai-agent-harness`、`topics/multi-agent-systems`、`topics/agentic-systems`、`index`、`overview`。核心沉淀是：oh-my-openagent 是一个把"单模型对话"扩展为"多 agent 并行编排运行时"的 OpenCode 插件，其最值得关注的架构决策是把模型选择从"用户手动配置"变成"category 语义驱动"的自动行为——用户表达意图，harness 自动路由到合适的模型和 specialist。它实现了 5 步初始化、10 个 hook handler、53 个 lifecycle hook、26 个工具和 11 个 agent，把 orchestrator-worker 模式落地为可安装的基础设施。

## [2026-05-11] ingest | 腾讯云 ClickHouse 集群实例选型指南

触及页面：`sources/tencent-cloud-clickhouse-cluster-sizing`、`topics/clickhouse-cluster-sizing`、`index`、`overview`。核心沉淀是：腾讯云 TCHouse-C 把计算节点打包成标准型、存储优化型与高性能型三类规格，选型核心不在"哪款最大"，而在先回答查询模式、数据温度与成本约束；Keeper 节点虽常被忽略，但其网络抖动会直接影响整个集群的副本健康度。新增主题页把 CPU、内存、磁盘、网络四条约束线拧成一组可验证的选型假设，并与既有 `clickhouse-deployment-topologies`、`clickhouse-production-migration` 形成互补。

## [2026-05-12] ingest | 腾讯云 CVM 完整实例规格补充

触及页面：`sources/tencent-cloud-clickhouse-cluster-sizing`、`topics/clickhouse-cluster-sizing`。核心沉淀是：补充了腾讯云全量 CVM 实例族信息（标准型 SA9/S9/SA9e/S9e/S9pro/S8/SA5/SA4/S6/SA3/SR1/S5 等、内存型 MA9/M9/MA9e/M9e/M9pro/M8/MA5/MA4/MA3/M6/M5/M4/M3/M2、高 IO 型 ITA5/IT5/IT3/IA5se/IA3se、大数据型 D3/D2、计算型 C6/C5/C4 等），在主题页中增加了精细的实例族-场景映射表和五个具体场景的推荐配置（通用 OLAP、内存密集型、热数据低延迟、海量冷数据归档、大规模生产集群），并补充了网络性能关键指标（PPS、带宽、队列数、DPDK）和垂直变配限制的详细说明。

## [2026-05-12] ingest | Interaction Models：可扩展的人机协作方式

触及页面：`sources/interaction-models`、`topics/interaction-models`、`entities/thinking-machines-lab`、`topics/agent-computer-interface`、`topics/agentic-systems`、`topics/multi-agent-systems`、`index`、`overview`。核心沉淀是：Thinking Machines Lab 提出的 interaction model 不是让 turn-based 模型跑得更快，而是彻底取消 turn 的概念——以 200ms micro-turns 持续运行，原生支持打断、重叠语音、视觉主动性和并发工具调用；双模型架构把实时 presence 交给 interaction model，把深度推理交给 background model，让 agentic system 的分工维度从任务空间扩展到时间空间。

## [2026-05-13] ingest | ClickHouse Cloud 架构与 Parallel Replicas

触及页面：`sources/clickhouse-cloud-architecture`、`sources/clickhouse-parallel-replicas`、`topics/clickhouse-deployment-topologies`、`entities/clickhouse`、`index`、`overview`。核心沉淀是：ClickHouse Cloud 并非自管版的 UI 包装，而是以对象存储为默认底座、计算层自动扩缩容与 idle、compute-compute separation 让读写资源彻底解耦的另一种架构；Parallel Replicas 则补上了无分片场景下的查询并行化机制，用 granule 取代 shard 作为工作单元，通过 announcement、dynamic coordination、cache locality 和 task stealing 解决异步复制、尾延迟与缓存命中问题。两者共同更新了部署拓扑判断框架，把 Cloud 架构选择并行查询策略也纳入同一体系。

## [2026-05-13] ingest | clickhouse-go 客户端配置

触及页面：`sources/clickhouse-go-configuration`、`topics/clickhouse-deployment-topologies`、`entities/clickhouse`、`index`、`overview`。核心沉淀是：全副本架构下，客户端的 `Addr` 应填入所有 replica 地址，通过 `ConnOpenStrategy`（轮询或随机）实现查询负载均衡；`ConnMaxLifetime` 默认值 1 小时在节点动态扩缩容时可能导致连接分布不均，需要监控；协议选择（TCP vs HTTP）不仅影响压缩选项，还影响 session 语义和认证方式。

## [2026-05-13] query | ClickHouse 分片决策：从 4 个独立节点到全副本集群

触及页面：`topics/clickhouse-sharding-decision`（新建）、`topics/clickhouse-deployment-topologies`、`entities/clickhouse`、`index`、`overview`。核心沉淀是：在冷热分层前提下（目标周期 1 个月，热数据约 0.53TB/月，压缩后 < 200GB），4 个独立单节点（64C/256GiB，CPU 峰值 28%，内存峰值 12%）不应分片，而应改为 1 shard × 4 replicas 的全副本集群。分片不是配置参数的变化，而是需要分片键设计、数据重分布、查询路径调整的架构重构；副本才是配置参数的变化。关键判断：分片的唯一合理触发条件是单机处理能力成为明确瓶颈，而当前所有指标都远未触达。迁移路径：选定一个权威源节点执行 `ATTACH ... AS REPLICATED`，其他节点清空重建为 replica，配合冷热分层和 Parallel Replicas。

## [2026-05-13] ingest | ClickHouse SharedMergeTree

触及页面：`sources/clickhouse-shared-merge-tree`、`topics/clickhouse-deployment-topologies`、`entities/clickhouse`、`index`、`overview`。核心沉淀是：SharedMergeTree 是 ClickHouse Cloud 的默认引擎，用"共享存储 + Keeper 元数据 + 异步 leaderless 复制"取代了 ReplicatedMergeTree 的"replica 间复制"，实现了秒级扩容和数百 replica 支持。用户写 `ENGINE = MergeTree` 时 Cloud 会自动转换为 SharedMergeTree，完全透明。这也解释了为什么 ClickHouse Cloud 能做到 compute-compute separation 和动态扩缩容——底层引擎已经为"共享存储 + 无状态计算节点"做好了设计。自管集群即使配置了对象存储，仍然使用 ReplicatedMergeTree，replica 间仍然需要复制，扩容速度天然受限。

## [2026-05-13] query | ClickHouse Cloud 客户端连接策略

触及页面：`sources/clickhouse-cloud-architecture`、`topics/clickhouse-deployment-topologies`。核心沉淀是：ClickHouse Cloud 的客户端只需要连接一个 service endpoint（如 `xxx.clickhouse.cloud:9440`），Cloud 内部负责负载均衡和查询分发。这与自管集群"配多地址做轮询"的策略不同——自管集群需要外部 LB 或客户端多地址来实现连接分发，Cloud 则把这些都内置了。根本原因是引擎差异：Cloud 使用无状态的 SharedMergeTree（数据在共享存储），自管集群使用有状态的 ReplicatedMergeTree（数据在本地盘）。自管集群可以通过"外部 LB + Parallel Replicas"近似 Cloud 体验，但无法实现秒级透明扩缩容。

## [2026-05-13] query | 多分片架构下的 Parallel Replicas

触及页面：`sources/clickhouse-parallel-replicas`、`topics/clickhouse-deployment-topologies`。核心沉淀是：多分片架构（M shards × N replicas）下**可以**开启 Parallel Replicas，而且这是官方文档介绍的场景。工作机制是分层并行：`Distributed` 表负责第一层跨 shard 分发，每个 shard 内部再由 Parallel Replicas 做第二层 granule 级并行化。`max_parallel_replicas` 控制的是**每个 shard 内部**的并行度，而不是整个集群的总 replica 数。配置时 `cluster_for_parallel_replicas` 应指向与 `Distributed` 表相同的集群名。常见误区是以为 Parallel Replicas 只能用于无分片架构——实际上官方文档最初就是在分片架构的语境下介绍它的。

## [2026-05-14] ingest | Traefik 负载均衡与 Envoy 服务网格

触及页面：`sources/advanced-load-balancing-traefik`、`sources/choosing-load-balancing-strategy`、`sources/what-is-envoy`、`topics/load-balancing-strategies`（新建）、`topics/progressive-delivery`（新建）、`topics/service-mesh`（新建）、`entities/traefik`（新建）、`entities/envoy`（新建）、`index`、`overview`。核心沉淀是：负载均衡策略的选择取决于后端是否同构与请求是否可预测，四种核心策略（WRR、P2C、HRW、Least-Time）覆盖从最简单到最复杂的全部场景；渐进式交付的本质是用负载均衡器的权重和路由规则把发布风险摊薄到时间轴上；Envoy 的进程外架构让服务到服务通信从应用代码中抽离，形成统一治理的基础设施层。

## [2026-05-14] ingest | Harness Engineering vs Platform Engineering

触及页面：`sources/harness-vs-platform-engineering`、`topics/ai-agent-harness`、`index`、`overview`。核心沉淀是：agentic 系统的架构不是两层（model + harness），而是三层（harness + platform + targets）。Harness 负责进程内的任务优化，Platform 负责跨 agent fleet 的治理。Harness 与 Platform 之间的 seam 是企业级 agent 部署中最关键的设计决策。治理引力陷阱（商业、技术、组织三股驱动力）会导致 harness 吸收本属于 platform 的 concerns，最终形成"五个 harness、五种 auth 模型"的不可治理状态。前瞻趋势：harness 变薄（能力迁移到模型），platform 变厚（监管/成本/审计需求增加）。

## [2026-05-15] query | ClickHouse 集群负载均衡验证方案

触及页面：`topics/clickhouse-cluster-load-balancing`（新建）、`deploy/charts/TODO.md`、`index`、`overview`。核心沉淀是：自管 ClickHouse 集群可以在连接层用 Traefik TCP LB 近似 ClickHouse Cloud 的托管体验——客户端只需连接一个入口，健康检查自动剔除故障节点；但状态层和弹性层受限于 ReplicatedMergeTree 引擎，无法复制 Cloud 的秒级扩容。验证方案分四阶段：基线确认、Traefik TCP LB 部署、负载均衡行为验证、与 Cloud 体验对比。生产建议优先复用现有 Traefik 基础设施，写入路径仍应走 Distributed 表，查询层配合 Parallel Replicas 实现服务端并行化。

## [2026-05-19] ingest | OpenCode 使用技巧与最佳实践

触及页面：`sources/opencode-usage-tips`（新建）、`entities/opencode`（新建）、`topics/opencode-workflow`（新建）、`entities/oh-my-openagent`、`index`、`overview`，并顺手修复 `sources/clickhouse-parallel-replicas` 与 `sources/clickhouse-shared-merge-tree` 中的死链。核心沉淀是：用好 OpenCode 的关键不在于装多少插件，而在于建立"人主导、Agent 协作"的工作节奏。上下文管理是核心技能——200k 之后质量断崖下跌，主动压缩、拆分会话、每完成一件事就提交一次 commit。AGENTS.md 是当前最实用的记忆方案，根目录版本全局注入，子目录版本按需加载。配置层级是深层合并而非简单替换。子 Agent 信息传递失真不是理论问题，已有 verify-subagent-plugin 在尝试解决。本轮无删减候选。

## [2026-05-20] ingest | ClickHouse 查询优化权威指南 + in-order 聚合优化

触及页面：`sources/clickhouse-query-optimization-guide`（新建）、`sources/clickhouse-optimize-aggregation-in-order`（新建）、`topics/clickhouse-query-optimization`（新建）、`topics/clickhouse-common-pitfalls`、`entities/clickhouse`、`index`、`overview`。核心沉淀是：ClickHouse 的优化重心不在查询层面，而在建表时的 `ORDER BY` 设计——这本质上是在提前定义数据的物理归宿。官方指南用六层优化框架（ORDER BY 设计 → 数据类型 → 预计算 → 查询模式 → 额外索引 → 分区）把零散的优化技巧串成了有优先级的分层判断体系。`optimize_aggregation_in_order` 则让 GROUP BY 在数据已经排好序时走流式聚合而不构建 hash table，本质上是用建表时的排序成本交换查询时的聚合内存成本。互补更新了常见误区页：新增 Nullable 列的实际开销判断、分区数上限警告和 skip index 必须与 ORDER BY 有相关性的前提。删减预算：本轮无删减候选，本次新增的内容填补了 ClickHouse 主题线中"查询优化"的独立判断层，与已有部署、迁移、误区主题互补而非重叠。

## [2026-05-26] ingest | ACK 云盘存储卷（静态、动态、快照）

摄入阿里云 ACK 官方三篇云盘存储文档：
- `raw/articles/ack-static-disk-volume.md` — 静态卷的手动 PV/PVC 绑定流程
- `raw/articles/ack-dynamic-disk-volumes.md` — 动态卷的 StorageClass 与 volumeClaimTemplates
- `raw/articles/ack-disk-volume-snapshots.md` — VolumeSnapshot / VolumeSnapshotClass 快照与恢复

触及页面：
- 新增 `sources/ack-static-disk-volume`、`sources/ack-dynamic-disk-volumes`、`sources/ack-disk-volume-snapshots`
- 新增 `topics/kubernetes-persistent-storage` — 把静态卷、动态卷与快照的使用场景放进同一判断框架
- 更新 `entities/kubernetes` — 补充持久化存储第四条主线
- 更新 `index`、`overview`

删减预算：本轮无删减候选。

## [2026-05-26] ingest | CNPG 事故恢复与存储策略复盘

触及页面：`sources/cnpg-recovery-incident`（新建）、`topics/cloudnativepg-recovery`（新建）、`entities/cloudnativepg`（新建）、`topics/kubernetes-persistent-storage`、`entities/kubernetes`、`index`、`overview`。核心沉淀是：CloudNativePG 事故恢复要先判断权威数据和 PV/PVC 生命周期，再让 Operator 调和；`Retain` 能防误删 PVC 连带删云盘，但不能替代快照和数据库备份；主从同步要看 `pg_stat_replication` / `pg_stat_wal_receiver` 和 WAL LSN，而不能只看 Cluster Ready。

删减预算：保留 `topics/kubernetes-persistent-storage` 原有 ACK 文档框架；将 CNPG 事故经验合并为一个新实战小节，避免重复另写一套 PV/PVC 基础概念；`entities/kubernetes` 只追加一条有状态 Operator 边界判断，不扩写成运维清单。

## [2026-06-11] ingest | DuckLake 宣言与 v1.0 发布

触及页面：`sources/ducklake-manifesto`（新建）、`sources/ducklake-v1-0-announcement`（新建）、`topics/ducklake`（新建）、`entities/duckdb`（新建）、`entities/ducklake`（新建）、`index`、`overview`。核心沉淀是：DuckLake 的核心判断是把 lakehouse 全部元数据交给 SQL 数据库管理，而不是像 Iceberg/Delta Lake 那样用 JSON/Avro 文件；数据层仍用通用 Parquet 格式，竞争边界在元数据层。v1.0 的 Data Inlining、Sorted Tables、Bucket Partitioning、Variant 类型和 Deletion Vectors 把写入优化、查询优化与类型系统演进放到了同一框架。

删减预算：本轮无删减候选。DuckLake 是全新主题，与现有 ClickHouse 冷热分层、HDFS/OSS-HDFS 数据存储主题互补而非重叠。

## [2026-06-13] ingest | DuckDB 与 ClickHouse/Postgres/SQLite 对比

触及页面：`sources/duckdb-vs-clickhouse-posthog`（新建）、`sources/duckdb-vs-postgres`（新建）、`sources/duckdb-vs-sqlite`（新建）、`topics/duckdb-vs-clickhouse`（新建）、`entities/duckdb`（更新）、`entities/posthog`（新建）、`index`、`overview`。核心沉淀是：DuckDB 与 ClickHouse 不是竞争而是互补——ClickHouse 是生产级 OLAP 服务（长驻进程、水平扩展、高并发写入），DuckDB 是嵌入式分析引擎（进程内、零配置、用完即销毁）；PostHog 同时使用 Postgres + ClickHouse + DuckDB 的三数据库栈，按工作负载分层；DuckDB 与 Postgres 的对比揭示了 OLAP 与 OLTP 的根本差异（列式 vs 行式、向量化 vs Volcano、嵌入式 vs 客户端-服务器）；与 SQLite 的对比则澄清了"SQLite of OLAP"的精确含义——核心不是"本地性"而是"便携性 + 分析马力"。

删减预算：本轮无删减候选。新增内容与现有 ClickHouse 部署、查询优化、DuckLake 主题互补，不重叠。

## [2026-06-13] ingest | Agent-first 产品设计的五原则

触及页面：`sources/agent-first-product-engineering`（新建）、`topics/agent-first-engineering`（新建）、`entities/posthog`（更新）、`index`、`overview`。核心沉淀是：agent 不是产品的附加功能，而是一种新的交互层——它坐在用户和产品之间；PostHog 从 6000+ 日活 MCP 用户的两次架构迭代中提炼出五条原则——让 agent 能做用户能做的一切（默认关闭端点 + product team opt-in）、在 agent 的抽象层级上设计（用 SQL 替代 UI 原语）、预加载通用上下文（固定 + 动态平衡）、把 skill 写成"给优秀员工的入职指南"（领域知识 + 边界情况 + 品味）、把 agent 当作真实用户（headless dogfooding + trace review + eval loop）。

删减预算：本轮无删减候选。新增内容补充了 agent 主线中缺失的"产品层"视角，与现有 agentic-systems、agent-computer-interface、ai-agent-harness 主题互补。
