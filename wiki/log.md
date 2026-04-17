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
