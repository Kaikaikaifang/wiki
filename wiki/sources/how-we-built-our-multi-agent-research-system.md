---
title: How we built our multi-agent research system
type: source
tags:
  - Agent
  - 多智能体
  - 研究工作流
  - 提示词工程
source_count: 1
source_file: raw/articles/how-we-built-our-multi-agent-research-system.md
author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, Daniel Ford
published: 2026-04-13
updated: 2026-04-14
---

# How we built our multi-agent research system

来源：[[entities/anthropic]] · [原文](https://www.anthropic.com/engineering/multi-agent-research-system)

## 核心论点

这篇文章回答的不是“multi-agent 听起来酷不酷”，而是**什么任务值得付出多智能体的复杂度与 token 成本，以及怎样把它真正做成可上线的系统**。Anthropic 的结论很明确：多智能体最适合开放式、可并行、信息量超过单一上下文窗口的高价值研究任务。

## 为什么多智能体在研究任务上有效

- **研究过程天然路径依赖**：用户问题常常无法预先写死执行路径，必须边搜边改策略。
- **子 agent 提供并行压缩**：不同 subagent 用各自上下文窗口探索不同方向，再把高价值发现压缩给 lead agent。
- **收益主要来自可扩展 token 预算**：文章指出 BrowseComp 表现差异里，token 使用量本身解释了大部分方差；多智能体本质上是在并行扩展推理容量。
- **适合 breadth-first 查询**：当问题需要同时追多条独立线索时，lead + subagents 明显优于单 agent 串行搜索。

文章也强调代价：multi-agent 大约比普通 chat 显著更耗 token，因此只适合“性能提升值得额外成本”的任务。

## 架构模式

其核心是一个 **orchestrator-worker** 结构：

1. lead agent 先理解问题并形成研究计划；
2. 把问题拆给多个 subagents 并行搜索；
3. subagents 使用工具执行搜索、筛选、比较；
4. lead agent 汇总结果，必要时继续追加新一轮 subagents；
5. 最后再交给 citation agent 补齐可追溯引用。

这里有两个很重要的工程点：

- **计划要持久化**：因为上下文窗口会截断，lead agent 要把研究计划写入 memory；
- **引用生成独立成环节**：把“答案生成”和“证据定位”拆开，降低最终输出的不可核查性。

## Prompt 工程经验

Anthropic 总结了 8 条最有价值的提示工程原则：

1. **先建立 agent 的心智模型**：通过模拟运行观察失败模式，而不是仅凭直觉改 prompt。
2. **教 orchestrator 正确委派**：subagent 指令必须写清目标、输出格式、工具边界和职责分工。
3. **让 effort 随问题复杂度缩放**：简单问题别乱开几十个 subagents，复杂问题也不要配额不足。
4. **工具设计与工具选择同等关键**：先看可用工具，再按任务意图选最合适的工具。
5. **让 agent 帮你改 prompt / 改工具描述**：Claude 4 可作为 prompt engineer 和 tool tester。
6. **先宽搜，再收窄**：先用短而广的搜索，再逐渐聚焦。
7. **显式引导 thinking**：lead 用 extended thinking 规划，subagent 用 interleaved thinking 根据工具结果修正路径。
8. **两层并行化**：lead 并行启动多个 subagents，subagents 内部也并行调多个工具。

其中最关键的直觉是：**多智能体系统的上限不只是模型能力，也取决于是否把“分工、预算、工具选择”这些协作规则写进 prompt。**

## 评估方法

文章强调，多智能体不能按传统软件那样只检查“有没有走预定路径”，因为不同 agent 可能以不同但合理的方式抵达正确答案。因此评估要更偏向：

- **结果导向**：看是否得到正确、完整、有引用支撑的答案；
- **过程合理性**：是否用了合适工具、合理次数、较高质量来源；
- **LLM-as-judge**：用 rubric 同时评分事实准确性、引用准确性、完整性、来源质量和工具效率；
- **保留人工测试**：人工最容易发现自动评测漏掉的边角失败，如来源偏见和奇怪 query 下的幻觉。

## 生产工程难点

从 prototype 到 production，文章点出几类典型难题：

- **agent 有状态，错误会累积**：不能简单从头重跑，需要 checkpoint、恢复与 retry 机制；
- **debug 需要可观测性**：要看 agent 的决策模式与交互结构，而不只是最终输出；
- **部署要兼容长跑中的会话**：因此使用 rainbow deployment 逐步切流；
- **同步执行会形成瓶颈**：当前 lead 等 subagent 全部完成再继续，未来异步化会更强，但也更复杂。

## 最值得记住的判断

这篇文章给出的实践判断可以压缩成一句话：**只有当任务足够开放、足够高价值、足够可并行时，多智能体才值得上。** 否则它带来的 token 成本、协调复杂度与可靠性负担，可能会超过收益。

---

相关页面：[[topics/multi-agent-systems]] · [[topics/long-horizon-agents]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[entities/anthropic]]
