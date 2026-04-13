---
title: "QMD — 本地优先的 Markdown 搜索引擎"
type: source
tags: [搜索, 本地优先, MCP, Agent, 知识管理]
source_count: 1
source_file: raw/articles/qmd.md
author: tobi / qmd
published: 2026-04-13
updated: 2026-04-13
---

# QMD — 本地优先的 Markdown 搜索引擎

来源：[[entities/qmd]] · [原文](https://github.com/tobi/qmd/blob/main/README.md)

## 核心定位

QMD 是一个面向 markdown 文档、笔记、会议记录与知识库的**本地搜索引擎**。它的目标不是把知识上传到云端，而是在本机上完成索引、语义检索与结果重排，适合个人知识库和 agent 工作流。

## 搜索架构

QMD 采用混合检索流水线：

- **BM25 / FTS5**：负责关键词与精确匹配
- **向量检索**：负责语义相似性
- **查询扩展**：用本地 LLM 生成变体查询
- **RRF 融合**：整合多路候选结果
- **LLM 重排**：对 Top-K 候选做相关性判断
- **位置感知混合**：高位保留检索信号，低位更信任 reranker

这说明 QMD 不只是"向量搜索"，而是把**精确匹配、语义匹配与模型判断**组合成一条可解释的检索链。

## 为什么对个人 wiki 重要

[[topics/llm-wiki-pattern]] 在来源规模较小时可直接依赖 `wiki/index.md` 导航；当来源和页面增多后，QMD 提供了一个**仍然本地、仍然 markdown 原生**的扩展路径。它保留了文件系统作为事实来源，不把知识库封装进一个难以迁移的专有系统。

## 对 Agent 工作流的价值

QMD 明确为 agent 设计了几类接口：

- `--json` / `--files` 输出，便于程序消费
- `get` / `multi-get`，便于精确回收文档正文
- MCP server，便于 Claude / 其他客户端直接接入

它的关键思想是：**搜索结果不只是文件名列表，还应带有上下文、片段与结构化元数据**，这样 agent 才能更高效地继续推理。

## 关键实现取舍

- **本地模型**：通过 `node-llama-cpp` 运行 GGUF 模型，强调隐私与离线可用
- **上下文树**：可为 collection 或路径添加 context，帮助模型理解文档所属语境
- **智能切块**：对 markdown 做边界感知分块，对代码可选 AST-aware chunking
- **可嵌入 SDK**：不仅是 CLI，也能作为 Node/Bun 库使用

## 限制与边界

QMD 解决的是**检索与取回**问题，不取代 [[topics/llm-wiki-pattern]] 里的知识编译工作。它擅长在大量 markdown 中找到相关材料，但不会自动把材料沉淀为综述、主题页与实体页。

---

相关页面：[[entities/qmd]] · [[topics/local-first-search]] · [[topics/hybrid-retrieval]] · [[topics/llm-wiki-pattern]]
