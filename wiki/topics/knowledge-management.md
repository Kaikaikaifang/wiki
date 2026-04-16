---
title: 知识管理
type: topic
tags: [知识管理, PKM, 方法论]
source_count: 2
updated: 2026-04-16
---

> 我越来越觉得，知识管理真正难的从来不是“收集”，而是“维护一张不会越用越乱的理解网络”。

## 核心问题

知识库的最大敌人不是缺乏内容，而是**维护负担**。更新交叉引用、保持一致性、标注矛盾，这些工作一旦主要靠人手完成，增长速度通常会比知识价值积累得更快，最后系统就会退化成一个越来越难回头看的素材堆。

## 主要范式

| 范式 | 代表工具 | 特点 |
|------|----------|------|
| RAG 检索 | NotebookLM, ChatGPT 文件上传 | 每次从原始文档重新推导 |
| 双向链接笔记 | Obsidian, Roam | 人工维护，依赖个人纪律 |
| LLM Wiki | 本 wiki | LLM 负责维护，人类负责策源 |

## LLM Wiki 的突破

我现在最认同的突破点，不是“让回答更聪明”，而是**让维护成本趋近于零**。参见 [[topics/llm-wiki-pattern]]。只有当交叉引用、页面更新与一致性整理这些脏活不再主要消耗人的意志力，知识库才会真的进入复利区间。

## 访问层与编译层

知识管理里有两类常被混淆的能力，而我觉得这恰好是很多工具讨论里最容易糊掉的边界：

- **编译层**：把原始资料沉淀成结构化知识页面
- **访问层**：在大量资料中快速检索、定位并取回内容

[[topics/llm-wiki-pattern]] 主要解决前者，[[topics/local-first-search]] 与 [[topics/hybrid-retrieval]] 主要增强后者。只有把这两层拆开看，知识库才不会在规模变大后变成“搜得到原文，但拿不到判断”的半成品系统。

## 历史参照

[[entities/vannevar-bush]] 1945 年的 Memex 构想，依然是我理解这个主题时最好的历史参照：私人的、主动策划的知识库，文档间的关联与文档本身同等重要。这个愿景其实比后来的万维网更接近 LLM Wiki 的精神，因为它关心的不是公开发布，而是个人思考如何被长期组织、连接与调用。

---

来源：[[sources/llm-wiki]] · [[sources/qmd]]

相关页面：[[topics/llm-wiki-pattern]] · [[topics/local-first-search]] · [[topics/hybrid-retrieval]] · [[entities/vannevar-bush]] · [[entities/qmd]]
