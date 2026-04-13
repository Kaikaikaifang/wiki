---
title: 整体综述
type: overview
tags: [方法论, 知识管理]
source_count: 3
updated: 2026-04-13
---

# 整体综述

## 核心主题

目前 wiki 围绕一个核心方法论展开：**[[topics/llm-wiki-pattern]]**——用 LLM 增量构建并维护持久知识库，替代每次从零推导的 RAG 检索。

这既是本 wiki 的构建方式，也是第一个被记录的知识对象。随着资料规模增长，wiki 也开始引入第二条基础设施主线：**[[topics/local-first-search]]**，用于在保持 markdown 原生与本地优先前提下扩展检索能力。

最新摄入的 [[sources/building-effective-ai-agents]] 则把视角从“知识库如何积累”扩展到“agent 如何可靠执行”——尤其是 workflow 与 agent 的边界、复杂度升级时机，以及工具接口设计的重要性。

## 当前关注

- 理解并内化 LLM Wiki 模式本身
- 建立个人知识 / 自我提升领域的摄入习惯
- 理解 QMD 这类本地搜索工具如何作为 wiki 的扩展层
- 建立一套对 AI agent 更克制的设计判断：何时保持简单，何时升级为 workflow 或自治 agent

## 演化轨迹

- 2026-04-13：wiki 初始化，摄入第一个来源（Karpathy LLM Wiki 方法论文章）
- 2026-04-13：摄入 QMD README，补充 wiki 在规模化后的本地检索基础设施视角
- 2026-04-13：摄入 Anthropic 的 agent 工程文章，引入 agentic systems 与 ACI 两条新主题

---

相关页面：[[index]] · [[topics/llm-wiki-pattern]] · [[topics/local-first-search]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[entities/qmd]] · [[entities/anthropic]]
