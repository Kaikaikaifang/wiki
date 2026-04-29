---
title: OpenClaw
type: entity
tags: [Agent, 网关, 插件系统]
source_count: 1
updated: 2026-04-29
---

OpenClaw 是一个面向 AI agent 的网关与插件框架。它的核心定位是**让多个通讯软件通道（微信、飞书、Slack 等）和多个 AI Agent 能够在同一个运行时里协同工作**。开发者通过安装插件来扩展通道能力，通过配置来定义消息路由规则。

## 我为什么会接触到它

我的微信 Bot 最初就是基于 OpenClaw 的微信插件（`openclaw-weixin`）构建的。这个插件深度依赖 OpenClaw 的 SDK：它要注册一个 `ChannelPlugin` 接口，要实现 `gateway.startAccount` / `stopAccount` 生命周期，要响应 `auth.login` 的二维码登录流程，还要依赖网关注入的 `channelRuntime` 和 `abortSignal`。这种深度集成在团队级部署场景下是合理的，但对个人开发者来说，它引入了一套必须完整理解才能运行的框架复杂度。

## 核心概念

OpenClaw 的架构围绕几个核心概念展开：

- **Gateway（网关）**：中央运行时，负责加载插件、管理账户、调度消息
- **Plugin（插件）**：扩展网关能力的模块，通常以 npm 包形式分发。微信插件就是一个 `ChannelPlugin`
- **Channel（通道）**：消息的来源和去向，比如微信、飞书、Slack
- **Account（账户）**：通道层面的身份，一个微信 Bot 对应一个账户
- **Session（会话）**：用户与 Agent 之间的对话上下文，由网关统一管理
- **Hook（钩子）**：允许插件在消息发送前后插入自定义逻辑

## 与 Agent Bridge 的关系

Agent Bridge 可以看作是对 OpenClaw 理念的一种**反题**。OpenClaw 说"你需要一个完整网关来管理一切"，Agent Bridge 说"如果我只是想让微信消息驱动本机 Codex，能不能不要网关？"

这并不意味着 OpenClaw 是错的。相反，如果你的场景需要多通道、多账户、多 Agent 的复杂路由，或者需要团队协作和集中配置管理，OpenClaw 的框架化方案仍然是更成熟的选择。Agent Bridge 只是在**个人本机、轻量启动、最小依赖**这个细分场景下，提供了一种更直接的替代路径。

从插件代码里能看到 OpenClaw 的一些设计细节：比如 `blockStreamingCoalesceDefaults` 控制流式消息的分块策略，`textChunkLimit: 4000` 限制单次发送文本长度，`agentPrompt.messageToolHints` 给 Agent 提供通道特有的工具使用提示。这些都是框架在"让 Agent 更好地与通道协作"这件事上做的细致工作，也是独立桥接器短期内难以复制的部分。

来源：[[sources/agent-bridge-design]]

相关页面：[[topics/agent-bridge]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]]
