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

## [2026-04-13] lint | 修复标签与元数据规范问题

修复 `entities/anthropic` 的非法空格标签，补齐 `entities/andrej-karpathy` 的相关页面；为 `index` 补充缺失元数据，并在 AGENTS.md 与 CLAUDE.md 中明确 `index` / `log` 作为 utility 页的规范；同时增强 `overview` 的反向链接。

## [2026-04-13] ingest | Use The Index, Luke 索引专题

摄入 `https://use-the-index-luke.com/sql/table-of-contents` 及其下 89 个索引相关章节，归档 `raw/articles/use-the-index-luke-sql-performance.md`；新增 `sources/use-the-index-luke`、`entities/markus-winand` 与 SQL 索引 / 执行计划 / 连接 / 分页 / 写入权衡等主题页，并同步更新 `index` 与 `overview`。

## [2026-04-13] wiki | 拆分 Use The Index, Luke 章节页

将 `sources/use-the-index-luke` 保留为总览入口，并拆分为前言、索引结构、`where`、可扩展性、连接、聚簇、排序分组、分页、写入代价、执行计划与误区等章节来源页，便于后续查询与交叉引用。
