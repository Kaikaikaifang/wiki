---
title: LLM Wiki 模式论文
type: source
tags: [知识管理, LLM, 方法论, PKM]
source_count: 1
source_file: raw/articles/llm-wiki.md
author: Andrej Karpathy
published: 2026-04-13
updated: 2026-04-16
---

来源：[[entities/andrej-karpathy]] · [原文](https://gist.githubusercontent.com/karpathy/442a6bf555914893e9891c11519de94f/raw/ac46de1ad27f92b28ac95459c782c07f6b8c964a/llm-wiki.md)

## 核心论点

传统 RAG 每次查询都从零推导，知识不积累。LLM Wiki 的不同之处：**LLM 增量构建并维护一个持久 wiki**，知识被编译一次后持续更新，而非每次重新检索。wiki 是复利资产——交叉引用已就位，矛盾已标注，综述已反映所有读过的内容。

## 三层架构

| 层级 | 内容 | 所有权 |
|------|------|--------|
| 原始资料（raw/） | 文章、论文、图片、数据，不可修改 | 人类 |
| Wiki（wiki/） | 摘要、实体页、概念页、综述 | LLM |
| 模式文件（CLAUDE.md） | 结构约定、工作流指令 | 人类 + LLM 共同演化 |

## 三种操作

- **摄入**：读取来源 → 讨论要点 → 写摘要页 → 更新索引 → 更新实体/主题页 → 记录日志。一个来源可能触及 10–15 个页面。
- **查询**：读索引定位 → 读相关页 → 综合答案 → 有价值的答案归档回 wiki。
- **检查（Lint）**：扫描矛盾、孤立页、缺失交叉引用、过时内容，建议下一步探索方向。

## 导航机制

- `index.md`：内容目录，按类型分节，每次摄入后更新。中等规模（~100 来源）无需向量检索。
- `log.md`：只追加的时间线，`## [YYYY-MM-DD] 操作 | 标题` 格式，可 grep。

## 为什么有效

知识库的维护负担（更新交叉引用、保持一致性、标注矛盾）是人类放弃 wiki 的根本原因。LLM 不会厌倦，不会漏掉交叉引用，一次可以修改 15 个文件。**维护成本趋近于零，wiki 才能持续生长。**

人类负责：策源、提问、判断意义。LLM 负责：其余一切。

## 历史渊源

与 [[entities/vannevar-bush]] 1945 年提出的 Memex 理念一脉相承——私人的、主动策划的知识库，文档间的关联与文档本身同等重要。Bush 未能解决的问题是谁来做维护，LLM 解决了这个问题。

## 工具提示

- **Obsidian Web Clipper**：浏览器扩展，将网页转为 markdown
- **qmd**：本地 markdown 搜索引擎（BM25 + 向量混合），规模大时引入
- **Marp**：markdown 幻灯片格式，Obsidian 有插件
- **Dataview**：Obsidian 插件，基于 frontmatter 生成动态表格

---

相关页面：[[topics/llm-wiki-pattern]] · [[topics/knowledge-management]] · [[entities/andrej-karpathy]] · [[entities/vannevar-bush]]
