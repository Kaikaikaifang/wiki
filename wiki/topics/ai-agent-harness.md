---
title: AI Agent Harness
type: topic
tags: [Agent编排, 运行时, 多智能体, 工具链]
source_count: 3
updated: 2026-05-14
---

> 当我把"agent 系统"拆成"host substrate + orchestration layer + specialist agents"三层后，很多之前觉得混乱的设计突然变得清晰了。

## 什么是 Harness

在 AI agent 的语境里，**harness** 指的是把模型调用、工具注册、会话管理、生命周期钩子和安全策略组装成一个可运行系统的中间层。它不是模型本身，也不是某个具体工具，而是**让模型与工具、会话与策略、编排与执行能够协同工作的运行时框架**。

如果用最短的定义：harness 是 agent 的"操作系统"。

## 三层模型

从 oh-my-openagent 的源码分析中，我看到一个非常清晰的分层：

| 层级 | 职责 | 实例 |
|------|------|------|
| **Host Substrate** | 会话、模型、原生工具执行 | OpenCode、Claude Code、Cursor |
| **Orchestration Layer** | 策略注入、路由、委派、生命周期、回退 | oh-my-openagent、LangGraph、AutoGen |
| **Specialist Agents** | 具体任务的执行体 | Sisyphus、Oracle、Explore、Librarian 等 |

这种分层的价值在于：**每一层都可以独立演进**。OpenCode 更新模型支持，不影响 orchestration 逻辑；omo 新增一个 category，不需要改 OpenCode 内核； specialist agent 的 prompt 调优，也不影响 harness 层。

## 核心能力

一个完整的 agent harness 通常需要具备以下能力：

### 1. Agent 注册与发现

不是硬编码 agent 列表，而是让 harness 能动态发现可用 agent。oh-my-openagent 在 `src/agents/builtin-agents.ts` 中维护内置 agent map，同时支持用户通过配置覆盖和自定义 agent。

### 2. Category / Intent 路由

用户表达意图 → orchestrator 分类 → 路由到对应 specialist。omo 的 Sisyphus 在 prompt 层面做 Intent Gate，然后选择 `category`（如 `visual-engineering`）；harness 再把 category 解析为具体模型。

这比"用户手动选模型"或"固定 agent 做所有事"都更灵活。

### 3. 模型解析与回退

模型选择不能只靠静态配置。omo 实现了 4-step 解析管道：

1. 用户显式覆盖
2. Category 默认模型
3. Provider fallback chain（按可用性依次尝试）
4. 系统默认模型

此外还有运行时回退（provider 错误时自动切换）。这种防御性设计是生产级 harness 的标配。

### 4. 后台并行执行

复杂任务需要多个 specialist 同时工作。omo 的 `BackgroundManager` 创建独立 OpenCode 子会话，每个子会话有自己的模型和上下文，并发限制为 5 个/模型。

关键设计点：
- 子会话通过 `parentID` 与主会话关联
- 完成后通过 `<system-reminder>` 注入结果，不污染主上下文
- 熔断器防止子 agent 陷入无限循环

### 5. 生命周期钩子

omo 注册了 53 个 hook，覆盖会话创建、消息发送、工具执行前后、会话压缩、错误恢复等节点。每个 hook 都是独立可禁用的策略单元。

常见 hook 类型：
- **Session hooks**：模型回退、上下文窗口监控、自动恢复
- **Tool guard hooks**：文件写保护、comment 检查、规则注入
- **Transform hooks**：关键词检测、上下文注入、thinking block 验证
- **Continuation hooks**：todo 强制延续、compaction 保护

### 6. MCP 集成

harness 需要统一接入外部工具。omo 采用 3 层 MCP：
- 内置 MCP（websearch、context7、grep_app）
- Claude Code 兼容层（`.mcp.json`）
- Skill 内嵌 MCP（按 session 隔离）

## 设计取舍

### 兼容性 vs 原生优化

omo 选择兼容 Claude Code 的全部生态（hooks、skills、agents、MCPs、plugins、commands），代价是更大的兼容表面和更复杂的配置合并逻辑。好处是用户迁移零成本。

### 集中路由 vs 去中心化

omo 采用 Sisyphus 作为单一 orchestrator，所有委派决策由它做出。这比完全去中心化的多智能体更容易调试，但也意味着 Sisyphus 的 prompt 质量直接决定系统上限。

### Prompt 驱动 vs 代码驱动

omo 的路由和委派逻辑大量依赖 Sisyphus 的 system prompt（Intent Gate、category 选择、并行规则）。这与 LangGraph 等代码驱动的 workflow 形成对比。前者的灵活性更高，后者的可预测性更强。

## Harness 的企业级边界：与 Platform 的分层

以上讨论聚焦单个 harness 的技术实现，但当企业运行几十个甚至几百个 agent 时，一个新的架构维度浮现出来：**harness 负责进程内的任务优化，platform 负责跨 agent fleet 的治理**。这是 [[sources/harness-vs-platform-engineering]] 提出的核心框架。

### 三层参考架构

```
Layer 1: Harness（进程内）
  → 编排、提示组装、工具选择、子 agent fan-out、上下文压缩、内存、自我验证
  → 归属：应用团队，按 agent 优化

Layer 2: Platform（进程外）
  → 身份、授权、审计、限流、成本、密钥、过滤、路由、故障转移、可观测性
  → 归属：平台/基础设施团队，跨 agent 统一强制执行

Layer 3: Targets（依赖项）
  → 模型、工具与 MCP 服务器、现有应用 API
  → 归属：各团队或供应商，作为被治理的依赖
```

Harness 与 Platform 的分界是 agentic 系统中最关键的设计决策。Harness 的优化目标是**单个 agent 的任务性能、token 预算和延迟 profile**；Platform 的优化目标是**跨所有 agent 的一致性治理、可审计性和长期稳定性**。

### 治理引力陷阱

Harness 框架有一种结构性倾向：吸收本属于 platform 层的 concerns。三股驱动力：

1. **商业驱动**：Harness 厂商通过"包揽更多"提高切换成本
2. **技术驱动**：进程内检查比进程外快几个数量级（微秒 vs 毫秒）
3. **组织驱动**：应用团队比平台团队移动更快，自建治理"临时方案"很少被真正迁移

结果是：五个 harness、五种 auth 模型、五种审计格式。CISO 无法回答"哪些 agent 能访问哪些数据"，FinOps 无法做成本归因，合规团队发现审计记录散落在各 vendor 的 trace store 里。

### 关键反模式

| 反模式                                  | 症状                        | 修复                                        |
| ------------------------------------ | ------------------------- | ----------------------------------------- |
| Auth in the Harness                  | 安全团队需要读多个仓库源码才能回答授权问题     | 把授权移到 gateway，按 agent 身份和任务上下文统一决策        |
| Per-Product Harness with No Platform | 多种模型合同、多种审计格式、无统一成本视图     | 先标准化 platform 层（网关、身份、审计），再考虑 harness 标准化 |
| Harness Vendor as Governance Vendor  | 引入第二个 harness 需重建所有控制     | 把治理保留在 platform 层，与 harness 无关            |
| Model List in Harness Config         | 引入新模型需协调所有 harness 更新     | Harness 请求"模型类"，由 AI Gateway 按策略解析为具体模型   |
| MCP Servers as Direct Dependencies   | 每个 MCP 服务器各自实现 auth、限流、审计 | MCP 流量通过 MCP Gateway 统一治理                 |

### 前瞻趋势

- **Harness 变薄**：自我验证、规划、工具使用正在迁移到模型内部（如 Opus 4.7 的 self-verification）。LangChain 已明确承认这一轨迹。
- **Platform 变厚**：每一条 AI 监管要求（EU AI Act、行业框架、主权数据规则）都落在 platform 层，因为那里是可强制执行的。每一次 breach analysis 都落在 platform 层，因为那里才有审计记录。

结论：赌 harness 会继续变化，赌 platform 会继续积累需求。有意识地构建它们之间的 seam，并**抵抗把两层 collapse 为一层的引力**。

## 与 Anthropic Managed Agents 的对比

| 维度 | oh-my-openagent（本地插件） | Anthropic Managed Agents（托管服务） |
|------|------------------------------|--------------------------------------|
| orchestrator | Sisyphus（prompt 驱动） | Managed runtime（基础设施驱动） |
| 模型路由 | Category fallback chain | 用户显式或运行时动态 |
| 会话隔离 | OpenCode 子会话 | 内部 session 管理 |
| 可观测性 | Hook + polling + circuit breaker | 内置 tracing、eval、sandbox |
| 部署 | 本地 OpenCode | Anthropic 托管 |
| 安全边界 | 依赖 host（OpenCode） | 内置 sandbox 与权限控制 |

两者的共性在于：都认同"orchestrator + specialist"的分层，都强调上下文隔离、模型回退和生命周期管理。

## 什么时候需要 harness

不是所有项目都需要一个完整的 harness。根据 [[sources/building-effective-ai-agents]] 的复杂度阶梯：

- **增强型 LLM / Prompt chaining**：不需要 harness，直接调用模型即可。
- **Routing / Parallelization**：简单的路由可以用 `if/else` 或 switch，不需要完整 harness。
- **Orchestrator-workers**：当需要动态分配子任务、管理多个 specialist 的生命周期时，harness 的价值开始显现。
- **Evaluator-optimizer / Autonomous agent**：当需要多轮自治、错误恢复、状态持久化时，harness 几乎是必需的。

也就是说，harness 的引入门槛是"**你是否需要管理多个 agent 的生命周期、上下文隔离和模型路由**"。

## 实用判断

如果你正在评估是否要引入一个 harness 框架，我会建议按以下顺序检查：

1. 你是否已经在手动切换多个模型来完成不同任务？
2. 你是否需要让多个 agent 并行工作，然后把结果汇总？
3. 你是否需要为不同任务类型配置不同的工具集和权限？
4. 你是否需要模型故障时的自动回退机制？

如果以上有 2 个以上答案是 yes，那么一个 harness（无论是 omo、LangGraph 还是自研）通常是值得的。

## 本地模型作为 Harness 后端

以上讨论默认模型来自云端 API，但 [[topics/local-llm-inference]] 让我意识到 harness 的后端选择还有另一条线：本地专用推理引擎。

ds4.c 的启示是，本地模型不只是「云端的降级版」，而是一组不同约束下的重新优化：

- **延迟**。本地模型没有网络往返，对于 orchestrator 需要频繁调用 specialist 的场景，延迟差异会累积成体验差异。
- **隐私**。代码、文档、个人笔记不需要离开本机。
- **长上下文成本**。1M tokens 的云端调用是一笔可观开销，本地运行是一次性硬件投入。
- **可控性**。本地环境完全控制版本、配置和状态，不受提供商更新策略影响。

但本地模型对 harness 也提出了新要求：

1. **兼容性**。本地引擎需要提供 OpenAI/Anthropic 兼容 API，否则 harness 的 tool calling、streaming、thinking controls 都需要重新适配。
2. **验证标准**。本地模型的「可用性」不能靠感觉，而需要官方向量验证（如 ds4.c 的 logits 对比）来保证 agent 场景下的可靠性。
3. **上下文管理**。本地推理的 KV cache 持久化（磁盘缓存）改变了 harness 对会话恢复和上下文重用的假设。

换句话说，引入 harness 时，「用哪个模型」不只是能力选择，也是部署模式选择：云端 API、本地通用运行器（llama.cpp/Ollama）、还是本地专用引擎（ds4.c）——这三者的延迟、成本、隐私和可靠性特征完全不同，harness 的路由和回退策略需要把它们纳入同一决策框架。

---

来源：[[sources/oh-my-openagent]] · [[sources/ds4-readme]] · [[sources/harness-vs-platform-engineering]]

相关页面：[[topics/multi-agent-systems]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/long-horizon-agents]] · [[topics/local-llm-inference]] · [[entities/oh-my-openagent]] · [[entities/anthropic]] · [[entities/managed-agents]] · [[entities/deepseek]] · [[entities/antirez]] · [[entities/traefik]]
