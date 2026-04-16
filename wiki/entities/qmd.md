---
title: QMD 搜索引擎
type: entity
tags: [工具, 搜索, 本地优先, MCP]
source_count: 1
updated: 2026-04-16
---

QMD 是一个面向 markdown 文档的本地搜索工具，支持 CLI、SDK 与 MCP server。它吸引我的地方，不只是“功能很多”，而是它非常明确地站在另一条路线里：保留文件系统、保留本地执行、保留 agent 可直接消费的结构化结果，而不是先把知识迁进一个黑箱平台再谈智能检索。

## 关键特征

- **本地优先**：索引、嵌入、重排都可在本机完成
- **混合检索**：结合关键词搜索与语义搜索
- **Agent 友好**：提供 `--json`、`--files`、`get`、`multi-get` 与 MCP 接口
- **Markdown 原生**：围绕文件系统中的 `.md` 文档组织 collection

## 与本 wiki 的关联

它是 [[topics/llm-wiki-pattern]] 在规模增大后的自然补充：wiki 负责把知识编译成结构化页面，QMD 负责在大量原始资料与页面中快速检索与取回。我越来越把它看成这套系统的“访问层引擎”。

## 设计哲学

QMD 强调**不依赖云端服务**、**不脱离文件系统**、**让 agent 直接消费检索结果**。这使它既适合个人 PKM，也适合需要可审计、可迁移、低外部依赖的本地知识基础设施。对我来说，它重要的不是“又一个搜索工具”，而是它证明了本地优先这条路完全可以做得现代、混合、而且 agent-native。

---

来源：[[sources/qmd]]

相关页面：[[overview]] · [[topics/local-first-search]] · [[topics/hybrid-retrieval]] · [[topics/llm-wiki-pattern]]
