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
