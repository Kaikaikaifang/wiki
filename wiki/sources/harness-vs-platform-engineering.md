---
title: Harness Engineering 与 Platform Engineering 的分层架构
type: source
tags: [Agent, Harness, Platform, 网关, AI架构]
source_count: 1
updated: 2026-05-14
---

## 核心论点

这篇文章提出了一个我认为会被反复引用的判断框架：**agentic 系统的架构不是两层（model + harness），而是三层（harness + platform + targets）**。Harness 不是产品的全部，Platform 也不是可有可无的基础设施——两者之间的 seam（接缝）是企业级 agent 部署中最关键的设计决策。

### Harness：进程内的任务优化层

Harness 是包裹在单个 agent 进程内部的一切：编排循环（ReAct/Thought-Action-Observation）、提示组装、工具定义与调用、子 agent 委派、上下文窗口压缩、会话持久化、结构化输出解析、自我验证逻辑。

这些决策的共同特征是**任务特定、模型特定**。Harness 的优化目标是：让一个 agent 在特定任务上的性能、token 预算和延迟 profile 达到最优。Harness 工程本质上是一门**应用层学科**，它的改进通过观察、追踪、评估和 benchmark 迭代来积累。

### Platform：跨 agent fleet 的治理层

当企业运行几十个甚至几百个 agent 时，跨 fleet 的 concerns 就属于 platform 层：

- 调用 agent 的身份认证与授权（TBAC）
- 每次模型/工具调用的审计记录
- 跨租户的限流与并发控制
- 成本归因与 FinOps 配额
- 密钥管理（secrets 不能进入 harness 进程内存）
- 提示和响应的内容过滤与 DLP
- 数据驻留的区域路由
- 模型提供商降级时的故障转移
- 全流量图的可观测性

这些 concerns 的三条共性：**必须跨不同团队、不同 harness 框架一致执行**；**必须可从单一控制点审计**；**必须比任何单个 harness 或模型选择活得更久**。

### 三层参考架构

```
Layer 1: Harness（进程内）
  → 编排、提示组装、工具选择、子 agent fan-out、上下文压缩、内存、自我验证
  → 归属：应用团队，按 agent 优化

Layer 2: Platform（进程外）
  → 身份、授权、审计、限流、成本、密钥、过滤、路由、故障转移、可观测性
  → 归属：平台/基础设施团队，跨 agent 统一强制执行

Layer 3: Targets（依赖项）
  → 模型（ frontier API / 自托管 / 主权部署）
  → 工具与 MCP 服务器（内部、合作伙伴、第三方）
  → 现有应用 API
  → 归属：各团队或供应商，作为被治理的依赖
```

最重要的设计决策是 Layer 1 与 Layer 2 之间的 seam。如果这个 seam 定义清晰，harness 可以独立于 platform 演进；application team 可以换掉整个 harness 框架而无需重新协商治理策略；platform team 可以引入新策略而无需协调每个应用团队。如果 seam 模糊，两层会互相渗透——授权决策出现在 harness middleware 里，安全团队无法审计；成本控制出现在 platform 代码里，应用团队无法调优。

### 治理引力陷阱

Harness 框架有一种结构性倾向：吸收本属于 platform 层的 concerns。作者归纳了三股驱动力：

1. **商业驱动**：Harness 厂商通过"包揽更多"来提高切换成本
2. **技术驱动**：进程内检查比进程外快几个数量级（微秒 vs 毫秒），延迟敏感场景下诱惑巨大
3. **组织驱动**：应用团队比平台团队移动更快，当需要新工具时，在 harness 里自建治理捷径比等平台团队排期更实际——但"临时方案"很少被真正迁移

结果是：五个 harness、五种 auth 模型、五种审计格式、五种限流配置。CISO 无法回答"哪些 agent 能访问哪些数据"，FinOps 无法做成本归因，合规团队发现审计记录散落在各 vendor 的 trace store 里。

### 反模式清单

| 反模式 | 症状 | 修复方案 |
|---|---|---|
| Auth in the Harness | 安全团队需要读多个应用仓库的源码才能回答授权问题 | 把授权移到 gateway，用统一策略语言，按 agent 身份和任务上下文决策 |
| Per-Product Harness with No Platform | 多种模型合同、多种审计格式、无统一成本视图 | 先标准化 platform 层（网关、身份、审计），再考虑 harness 标准化 |
| Harness Vendor as Governance Vendor | 治理范围受限于 harness vendor 的实现；引入第二个 harness 需重建所有控制 | 把治理保留在 platform 层，与 harness 无关 |
| Model List in Harness Config | 每个 harness 硬编码模型列表；引入新模型需协调所有 harness | Harness 请求"模型类"（planning/coding/summarization），由 AI Gateway 按策略、区域、成本解析为具体模型 |
| MCP Servers as Direct Dependencies | 每个 MCP 服务器各自实现 auth、限流、审计 | MCP 流量通过 MCP Gateway，统一处理身份、TBAC、密钥和审计 |

### 前瞻判断

两个趋势决定了这个架构的未来：

1. **Harness 变薄**：自我验证、规划、工具使用正在迁移到模型内部（如 Opus 4.7 的 self-verification）。LangChain 已明确承认这一轨迹，把 harness 组件定义为"对模型尚不能做之事的押注"。
2. **Platform 变厚**：每一条监管要求（EU AI Act、金融/医疗行业框架、主权数据规则）都落在 platform 层，因为那里是可强制执行的。每一个 CFO 的成本控制反射都落在 platform 层，因为那里可以强制执行归因而非依赖自报。每一次 breach analysis 都落在 platform 层，因为那里才有审计记录。

结论是：赌 harness 会继续变化，赌 platform 会继续积累需求。有意识地构建它们之间的 seam，并**抵抗把两层 collapse 为一层的引力**。

## 实践启示

- 如果你正在构建第一个 agent，最低限度的 platform 层只需要三件事：agent 身份、每次模型/工具调用的审计记录、模型流量的单一出口点。跳过出口点是最容易做也最难回头的决定。
- 如果你已经有三个不同的 harness 框架在生产环境，**从 platform 开始标准化**，而不是从 harness。标准化 harness 是多团队、多季度的谈判；标准化出口层是一次性基础设施决策。
- 进程外治理的延迟惩罚确实存在，但通常被高估。一个部署良好的 gateway 给一次本来就需要几百毫秒的模型往返调用增加个位数毫秒。真正需要优化延迟的是 harness 内的编排循环，而不是 platform 层的治理检查。

## 来源信息

- 作者：Sudeep Goswami（Traefik Labs CEO）
- 发布日期：2026-05-08
- 原文：https://traefik.io/blog/harness-engineering-vs-platform-engineering-a-mental-model-for-how-both-win
- 本地归档：`raw/articles/Harness Engineering vs Platform Engineering How Both Can Win.md`

## 相关页面

- [[topics/agentic-systems]] — 从增强型 LLM 到 workflow 与自治 agent 的复杂度阶梯
- [[topics/agent-computer-interface]] — 面向模型而非人类的工具接口设计原则
- [[topics/multi-agent-systems]] — 适合并行开放式任务的多智能体分工与协作模式
- [[entities/traefik]] — Traefik Labs 与 Triple Gate Pattern
- [[sources/advanced-load-balancing-traefik]] — Traefik Proxy 的高级负载均衡特性
