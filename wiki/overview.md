---
title: 整体综述
type: overview
tags: [方法论, 知识管理]
source_count: 5
updated: 2026-04-13
---

# 整体综述

## 核心主题

目前 wiki 围绕一个核心方法论展开：**[[topics/llm-wiki-pattern]]**——用 LLM 增量构建并维护持久知识库，替代每次从零推导的 RAG 检索。

这既是本 wiki 的构建方式，也是第一个被记录的知识对象。随着资料规模增长，wiki 也开始引入第二条基础设施主线：**[[topics/local-first-search]]**，用于在保持 markdown 原生与本地优先前提下扩展检索能力。

最近加入的三篇 Anthropic 文章，则把视角从“知识库如何积累”扩展到“agent 如何可靠执行与扩展”：[[sources/building-effective-ai-agents]] 解释 workflow 与 agent 的边界，[[sources/how-we-built-our-multi-agent-research-system]] 讨论多智能体研究系统何时值得采用，[[sources/scaling-managed-agents-decoupling-the-brain-from-the-hands]] 则进一步落到长程 agent 的运行时架构、恢复与安全边界。

## 当前关注

- 理解并内化 LLM Wiki 模式本身
- 建立个人知识 / 自我提升领域的摄入习惯
- 理解 QMD 这类本地搜索工具如何作为 wiki 的扩展层
- 建立一套对 AI agent 更克制的设计判断：何时保持简单，何时升级为 workflow 或自治 agent
- 理解多智能体的真实适用边界，而不是把“更多 agent”当作默认优化方向
- 理解长程 agent 的状态层、上下文层与执行层应如何分离

## 演化轨迹

- 2026-04-13：wiki 初始化，摄入第一个来源（Karpathy LLM Wiki 方法论文章）
- 2026-04-13：摄入 QMD README，补充 wiki 在规模化后的本地检索基础设施视角
- 2026-04-13：摄入 Anthropic 的 agent 工程文章，引入 agentic systems 与 ACI 两条新主题
- 2026-04-13：摄入 Anthropic 的多智能体 Research 复盘，新增多智能体协作与评估视角
- 2026-04-13：摄入 Anthropic 的 Managed Agents 架构文章，新增长程 agent 运行时与安全边界视角

---

相关页面：[[index]] · [[topics/llm-wiki-pattern]] · [[topics/local-first-search]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/multi-agent-systems]] · [[topics/long-horizon-agents]] · [[entities/qmd]] · [[entities/anthropic]] · [[entities/managed-agents]]
