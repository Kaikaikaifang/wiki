---
title: LLM Wiki 模式
type: topic
tags: [知识管理, LLM, 方法论, PKM]
source_count: 2
updated: 2026-04-16
---

> 用 LLM 增量构建并维护持久 wiki，替代每次从零推导的 RAG 检索。

## 本质区别

| RAG | LLM Wiki |
|-----|----------|
| 每次查询重新检索 | 知识编译一次，持续更新 |
| 无积累 | 复利增长 |
| 碎片化答案 | 结构化、互联的知识体 |
| 基础设施复杂（向量库） | 纯 markdown 文件 |

## 核心机制

**wiki 是持续积累的产物**。每摄入一个来源，交叉引用就被建立，矛盾被标注，综述被更新。下次查询时，这些工作已经完成。

**好的答案可以归档回 wiki**。查询产生的分析、比较、发现，不应消失在聊天记录里——归档后成为下一次查询的基础。

## 分工

- 人类：策源、提问、判断意义、演化模式文件
- LLM：摘要、交叉引用、归档、一致性维护

## 适用场景

个人成长、研究深潜、读书追踪、团队内部知识库、竞品分析、课程笔记……任何需要随时间积累知识的场景。

## 规模与工具

- 小规模（< 100 来源）：`index.md` 足够，无需向量检索
- 中大规模：引入 [[entities/qmd]] 这类本地搜索引擎，补充检索与取回能力

## 与搜索层的边界

[[topics/llm-wiki-pattern]] 的重点是**知识编译**：把来源沉淀为摘要、主题页、实体页和综述。[[entities/qmd]] 代表的搜索层重点是**检索与取回**：在大量 markdown 中快速找到、排序并返回相关内容。

二者并不冲突：wiki 负责长期积累后的结构化知识，搜索引擎负责在原始资料和大量页面中高效导航。

---

来源：[[sources/llm-wiki]] · [[sources/qmd]]

相关页面：[[overview]] · [[topics/knowledge-management]] · [[topics/local-first-search]] · [[topics/hybrid-retrieval]] · [[entities/andrej-karpathy]] · [[entities/qmd]]
