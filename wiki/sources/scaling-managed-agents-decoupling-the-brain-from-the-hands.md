---
title: "Scaling Managed Agents: Decoupling the brain from the hands"
type: source
tags: [AI Agent, 长程任务, 运行时架构, 安全]
source_count: 1
source_file: raw/articles/scaling-managed-agents-decoupling-the-brain-from-the-hands.md
author: Lance Martin, Gabe Cemaj, Michael Cohen
published: 2026-04-13
updated: 2026-04-13
---

# Scaling Managed Agents: Decoupling the brain from the hands

来源：[[entities/anthropic]] · [[entities/managed-agents]] · [原文](https://www.anthropic.com/engineering/managed-agents)

## 核心论点

这篇文章关注的不是 prompt，而是**长程 agent 的底层运行时应该如何设计，才能在模型持续变强时仍保持稳定、可恢复、可扩展与安全**。Anthropic 的答案是：把 agent 系统虚拟化成少数稳定接口，把“脑”“手”“会话”彻底解耦。

## 三个基础抽象

Managed Agents 将 agent 运行时抽象为三部分：

- **Session**：只追加的事件日志，保存发生过的一切；
- **Harness**：调用 Claude、路由工具调用、管理上下文的控制循环；
- **Sandbox**：执行代码、编辑文件、访问外部资源的环境。

文章借操作系统做类比：就像 `process` 与 `file` 这些抽象比底层硬件活得更久，agent 基础设施也需要一组**不随当前实现细节而失效的稳定接口**。

## 为什么要解耦 brain 和 hands

早期把 harness、session、sandbox 都放进同一个容器，看起来简单，却会形成“pet server”问题：

- 容器挂了，会话状态一起丢；
- debug 时很难区分是 harness、事件流还是容器本身出错；
- harness 默认所有资源都与它同处一地，难以连接用户自有基础设施；
- 不可信代码与凭证放在同一环境中，安全边界过弱。

解耦之后，harness 不再住在容器里，而是把容器 / 沙箱当作普通工具调用。这样单个 sandbox 失败时，系统可以把它视作可重建、可替换的 cattle，而不是必须手工抢救的 pet。

## 长程任务的恢复与上下文管理

文章最重要的一点是：**session 不是 Claude 的 context window。**

对于长程任务，context window 只是当前可见工作集；真正可恢复、可回放、可重读的历史，应该存在 session log 中。于是：

- harness 崩溃后，可用 `wake(sessionId)` + `getSession(id)` 恢复；
- Claude 需要回看上下文时，不必依赖一次性压缩摘要，而可以从事件流里重新切片读取；
- 上下文工程（compaction、trimming、prompt cache 优化）留在 harness 层演化；
- recoverable storage 与 context shaping 被拆成两个独立关注点。

这个设计很适合长时程任务，因为它降低了“压缩错了就永久丢信息”的风险。

## 安全边界设计

文章对 prompt injection 风险的处理很有代表性：**不要默认靠更严格 prompt 或更窄权限来兜底，而应从架构上让凭证根本不可达。**

Anthropic 采用两种方式：

- Git 凭证随资源初始化进入 sandbox，但 agent 本身不直接接触 token；
- MCP / OAuth 凭证保存在 sandbox 外部 vault 中，由代理按 session 取用。

因此，哪怕 Claude 生成的代码在 sandbox 中运行，也无法直接读取核心凭证。这是一种比“希望模型别犯错”更稳的结构性防护。

## Many brains, many hands

解耦之后，系统既能扩展到 **many brains**，也能扩展到 **many hands**：

- **many brains**：多个无状态 harness 可以快速启动，不必每次都等容器预热；文章称其显著降低 TTFT；
- **many hands**：每个 sandbox 或外部执行环境都被抽象为统一工具接口 `execute(name, input) → string`；
- **brain 与 hand 可自由组合**：不同 brain 可以按需连接不同 hands，而不被固定容器束缚。

这意味着未来不管“手”是容器、手机、MCP 服务还是别的执行环境，系统都不必整体重构。

## 对 harness 设计的更深提醒

这篇文章延续了 Anthropic 一贯的观点：**harness 编码了“模型做不到什么”的假设，而这些假设会随着模型进步迅速过时。**

因此，好的 harness / meta-harness 不是把当下经验写死，而是：

- 尽量把接口稳定下来；
- 尽量把具体策略留给未来可替换的实现；
- 允许不同任务使用不同 harness，但共享底层会话与执行抽象。

## 最值得记住的判断

这篇文章最有价值的洞见是：**做长程 agent 时，不能把“模型当前的上下文窗口”误当成“系统真正的记忆与状态层”。** 只有把状态、执行与协调拆开，agent 才能在失败、扩展与模型迭代中保持韧性。

---

相关页面：[[entities/managed-agents]] · [[topics/long-horizon-agents]] · [[topics/agent-computer-interface]] · [[topics/agentic-systems]] · [[entities/anthropic]]
