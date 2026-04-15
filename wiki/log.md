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
