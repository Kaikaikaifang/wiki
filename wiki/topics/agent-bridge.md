---
title: Agent Bridge：通讯软件与 CLI Agent 的轻量桥接
type: topic
tags: [Agent, CLI, 桥接器, 架构设计, 微信]
source_count: 1
updated: 2026-04-29
---

我一直在想，为什么让微信消息驱动本机 Claude Code 或 Codex 会这么复杂。现有的路径通常是：装一个完整网关框架 → 写插件 → 配账户 → 再想办法把消息转给 Agent。这个过程的每一步都在增加认知负担，而很多个人开发者真正想要的，只是一个能在本机跑起来的轻量桥接器。

Agent Bridge 就是围绕这个痛点设计的。它不是一个网关，也不是一个框架，而是一个**把通讯软件通道和命令行 Agent 解耦的桥接层**。

## 核心问题：为什么需要解耦

在 Bridge 之前，我的微信 Bot 实现深度绑定 OpenClaw。这意味着：

- 微信通道的逻辑（长轮询、登录、消息收发）与 OpenClaw 的插件生命周期强耦合
- Agent 的选择和调用由 OpenClaw 内部决定，微信通道没有话语权
- 如果你想换一个 Agent（比如从 Codex 切到 Claude Code），要改的不是配置，而是插件代码或网关路由

Bridge 的解耦思路很简单：**让通道只负责"接到消息"，让 Agent 只负责"执行任务"，中间用一个轻量运行时做路由和会话管理。** 这样一来，微信通道不需要知道 Codex 的存在，Codex 也不需要知道微信的存在。

## 设计结构：Channel → Runtime → Agent

Bridge 的核心是三组抽象：

### ChannelAdapter：通讯软件的统一接口

```typescript
interface ChannelAdapter {
  name: ChannelName;
  start(runtime: ChannelRuntime): Promise<void>;
  stop?(): Promise<void>;
  send(message: OutgoingMessage): Promise<void>;
  sendTyping?(conversationId: string): Promise<void>;
}
```

`WeixinChannel` 实现这套接口时，内部封装了 iLink API 的全部细节：二维码登录、长轮询 `getupdates`、消息去重、`context_token` 回传、session 过期自动重连。`CliChannel` 则用 Node.js `readline` 实现终端交互。未来如果要做飞书，只需要再实现一个 `FeishuChannel`，不需要碰 Agent 代码。

### AgentProvider：命令行 Agent 的统一接口

```typescript
interface AgentProvider {
  name: AgentName;
  ask(request: AgentRequest): Promise<AgentResponse>;
}
```

每个 Provider 负责把自己特有的 CLI 参数翻译成子进程调用。Codex 需要 `--sandbox` 和 `--output-last-message`，Claude Code 需要 `--print --output-format json`，Codebuddy 有自己的 `--permission-mode` 语义。这些差异被收敛在各自的 Provider 里，对 Runtime 来说所有 Agent 都是统一的 `ask()` 调用。

`generic` Provider 是一个特别有趣的设计：它通过配置里的 `promptArg`、`cwdArg`、`stdinPrompt`、`outputPattern` 等字段，让任意命令行工具都能被桥接。这意味着你不一定要等 Bridge 官方支持某个新 Agent，只要它能通过命令行接收 prompt 并输出结果，就可以一行配置接入。

### BridgeRuntime：路由、会话与安全

`BridgeRuntime` 是实际的调度中心。收到消息后，它按以下顺序处理：

1. **长度检查**：超过 10,000 字符直接拒绝，避免超长输入导致 Agent 异常
2. **白名单校验**：`allowUsers` 之外的 sender 会收到拒绝回复，并看到自己的用户 ID
3. **内置命令路由**：`/agent`、`/cwd`、`/status`、`/reset`、`/help` 等命令由 `handleBuiltinCommand` 直接处理，不经过 Agent
4. **会话状态读取**：从 `StateStore` 读取当前 conversation 的 agent 和 cwd，回退到全局默认值
5. **Agent 调用**：启动 typing 指示器，调用 `agent.ask()`，保存返回的 `sessionId`
6. **结果回传**：通过 Channel 把 Agent 的文本回复发回用户

整个流程被 `KeyedQueue` 串行化，确保同一个 conversation 不会同时触发多个 Agent 任务。

## 安全模型：默认不信任

Bridge 的安全设计不是事后补丁，而是从一开始就被当作核心约束：

**用户层**：只有 `allowUsers` 白名单中的 sender 才能触发 Agent。首次接入时，管理员可以先留空白名单，用微信发一条测试消息，Bridge 会回显 sender ID，管理员再把 ID 加入配置。

**目录层**：Agent 的工作目录被 `allowedWorkspaceRoots` 限制。`/cwd` 命令只能切到允许范围内的目录，防止 Agent 被诱导访问敏感路径。

**执行层**：不同 Agent 有不同的沙箱语义。Codex 的 `--sandbox read-only` 是原生支持的，Claude Code 的 `--permission-mode` 系列也是透传给 CLI 本身。Bridge 不试图自己实现沙箱，而是把安全委托给更专业的底层工具。

**并发层**：单会话串行避免了"同时收到两条矛盾指令"的风险。虽然这限制了吞吐量，但对个人本机场景来说，正确性远比并发重要。

## 配置驱动的进化

Bridge 最值得注意的设计决策之一，是把 Agent 注册从硬编码改成了配置驱动。早期原型里，`codex` 和 `claude` 是直接 `new` 出来的；现在的 `createAgentRegistry` 会遍历配置文件里的 `agents` 对象，根据键名或 `type` 字段自动选择 Provider。

这个改动看似只是工程整洁性，实际上它改变了 Bridge 的扩展模型：从"改代码重新编译"变成"写配置立即生效"。对于一个定位为本机工具的桥接器来说，这种低门槛扩展比类型安全更贴合用户场景。

## 与原始插件的对比

| 维度 | OpenClaw 微信插件 | Agent Bridge |
|------|------------------|--------------|
| 框架依赖 | 强依赖 OpenClaw SDK | 零外部运行时依赖 |
| Agent 绑定 | 由网关内部决定 | 配置驱动，动态注册 |
| 部署方式 | 插件安装 + 网关重启 | `npm install` 后直接运行 |
| 多 Agent 切换 | 不支持或需改网关配置 | `/agent <name>` 实时切换 |
| 会话管理 | 由网关 session 系统管理 | 本地 JSON 状态存储 |
| 安全模型 | 依赖网关权限体系 | 内置白名单 + 目录限制 + 单会话串行 |
| 适用场景 | 团队级网关部署 | 个人本机桥接 |

## 我还想问自己的问题

Bridge 目前最大的限制是它仍然**只能处理文本**。当用户发了一张截图或一段语音时，Bridge 会回复 `[图片]` 或 `[语音]`，然后 Agent 什么也看不到。要解决这个问题，不是简单地在 Channel 里加媒体解析，而是需要设计一套"如何把媒体转述给文本 Agent"的抽象：是 OCR 提取文字？是语音转文本？还是把媒体文件路径作为上下文塞进 prompt？

另一个还没想清楚的是**跨 Agent 上下文**。当前切 Agent 时，新 Agent 完全不知道之前的对话说了什么。如果要在切换时保留一份"对话摘要"，这份摘要应该由谁生成？是旧 Agent 在退出前总结？还是 Bridge 自己维护一份精简历史？这涉及到 Agent 之间是否应该有标准化的上下文交换协议。

来源：[[sources/agent-bridge-design]]

相关页面：[[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/multi-agent-systems]] · [[entities/openclaw]] · [[entities/ilink]]
