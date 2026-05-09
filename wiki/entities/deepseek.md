---
title: DeepSeek
type: entity
tags: [AI公司, 大语言模型, MoE]
source_count: 1
updated: 2026-05-09
---

> DeepSeek 可能是第一个让「开源模型 + 本地推理」这个组合真正接近 frontier 级别的玩家。

DeepSeek 是一家中国 AI 公司，以发布高性能开源/开放权重大语言模型著称。和闭源 frontier 模型（GPT-4、Claude 3.5 Sonnet 等）不同，DeepSeek 的策略是**让模型权重可下载、可本地部署、可被社区二次开发**。

## 模型谱系

DeepSeek 的模型演进有几个关键节点：

- **DeepSeek-V2/V3**：采用 Mixture-of-Experts（MoE）架构，总参数量极大（V3 达到 671B），但每次推理只激活一小部分专家，实际计算量远低于总参数量暗示的水平。
- **DeepSeek-R1**：专注于推理能力的版本，在数学、代码和逻辑任务上表现出色。
- **DeepSeek V4 Flash**：V4 系列的轻量/高效版本，285B 总参数，但活跃参数更少。支持 1M tokens 上下文窗口，KV cache 极度压缩，能在 128GB RAM 的 MacBook 上通过 2-bit 量化运行。

## MoE 架构的本地推理优势

MoE（混合专家模型）对本地推理有两个关键影响：

1. **活跃参数量远小于总参数量**。DeepSeek V4 Flash 的 284B 参数听起来吓人，但每次前向传播只路由到部分专家。这意味着内存中不需要同时加载全部参数，量化后的模型可以压进消费级硬件。
2. **非对称量化的空间**。ds4.c 采用的量化策略——只量化 routed MoE experts，保持 shared experts 和 routing 层原精度——之所以可行，正是因为 MoE 的架构天然把「高频核心计算」和「低频专家分支」分开了。

## 与本地推理生态的关系

DeepSeek 的开放权重策略，直接催生了 ds4.c 这类「窄赌注」引擎。如果模型权重不可下载，antirez 就不可能做「官方向量验证」；如果架构细节不透明，就不可能做「DeepSeek V4 Flash 专用的 Metal 图执行器」。

换句话说，DeepSeek 的开放性不只是「慷慨」，它也**创造了一种新的工程可能性**：为单个模型做端到端优化的专用推理引擎。

## 为什么现在重要

在 2026 年的语境下，DeepSeek V4 Flash 的吸引力不只是「开源且强」，而是它把几个 previously impossible 的组合变成了 possible：

- **1M 上下文 + 本地运行**：以前只有云端 API 能处理的超长文档，现在可以在本机处理。
- **Thinking mode + 可用长度**：其他模型的 thinking 段太长，导致实际使用中必须关掉。V4 Flash 的思考长度与问题复杂度成正比，让「开着 thinking 用」成为默认选项。
- **Agent 后端可信度**：通过 OpenAI/Anthropic 兼容 API，本地模型可以无缝接入 Claude Code、OpenCode、Pi 等 agent 工作流。

---

来源：[[sources/ds4-readme]]

相关页面：[[topics/local-llm-inference]] · [[entities/antirez]] · [[topics/agentic-systems]] · [[topics/ai-agent-harness]]
