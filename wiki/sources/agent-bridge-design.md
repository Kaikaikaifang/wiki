---
title: Agent Bridge 设计与实现
type: source
tags: [Agent, CLI, 桥接器, 微信]
source_count: 1
updated: 2026-04-29
---

这个项目是一次从"专用插件"到"通用桥接层"的架构重构。原始代码是一套绑定 OpenClaw 框架的微信通道插件，深度依赖 OpenClaw 的插件生命周期、配置系统和网关运行时；新设计的 Agent Bridge 则试图回答一个更通用的问题：**如果我不想要一个完整网关框架，能不能让微信消息直接驱动本机的 Codex、Claude Code、Codebuddy 或任意 CLI 工具？**

## 原始形态：OpenClaw 微信插件

`src/` 与 `cc-weixin/` 共同构成一套面向 OpenClaw 的微信通道实现。它的核心职责包括：

- 通过 iLink API 与微信 Bot 平台建立长轮询连接
- 二维码扫码登录、Token 续期与多账号管理
- 消息收发、媒体文件 CDN 上传与 AES-128-ECB 加密
- 深度嵌入 OpenClaw 的插件 SDK：注册 `ChannelPlugin`、实现 `gateway.startAccount` / `stopAccount`、响应 `auth.login` 生命周期

这个形态的问题是**耦合过深**。如果你想让微信消息驱动 Claude Code，必须先安装 OpenClaw 网关、理解它的插件注册机制、配置它的账户体系。对于"只想在本机跑一个微信机器人"的场景来说，这太重了。

## 新形态：Agent Bridge

`bridge/` 是一个独立运行的 Node.js CLI 工具，不依赖 OpenClaw，也不预设任何 Agent。它的设计可以用三个关键词概括：**多对多**、**配置驱动**、**安全默认**。

### 多对多：Channel ↔ Agent 解耦

Bridge 的核心抽象是两组接口：

- `ChannelAdapter`：负责接入通讯软件。当前实现了 `WeixinChannel`（iLink 长轮询）、`CliChannel`（终端 REPL），`FeishuChannel` 预留。
- `AgentProvider`：负责驱动命令行 Agent。当前实现了 `codex`、`claude`、`codebuddy`、`opencode` 四个专用适配器，以及一个 `generic` 通用适配器。

`BridgeRuntime` 作为中间调度层，把 Channel 收到的 `ChatMessage` 路由到当前会话选中的 Agent。一个 Channel 可以切换不同 Agent，一个 Agent 也可以被多个 Channel 复用。这种解耦意味着新增 Agent 不需要改 Channel 代码，新增 Channel 也不需要改 Agent 代码。

### 配置驱动：从硬编码到插件系统

早期的原型直接把 `codex` 和 `claude` 写死在启动代码里。Bridge 把它们改成了配置驱动的注册表：

```json
{
  "agents": {
    "codex": { "sandbox": "read-only", "approval": "never" },
    "my-tool": { "type": "generic", "command": "my-ai-tool", "stdinPrompt": true }
  }
}
```

配置键名自动推断 Provider 类型（`codex` → codex provider），未知键名则回退到 `generic`。这种设计让"新增 Agent"变成纯配置行为，不需要重新编译 Bridge。

### 安全默认：本机执行的三道防线

因为 Agent 最终会在本机执行 shell 命令，Bridge 把安全当作默认行为而不是可选项：

1. **用户白名单**：`allowUsers` 为空时，Bridge 会拒绝所有消息，并回显发送者 ID 供管理员配置。
2. **工作目录限制**：`allowedWorkspaceRoots` 限定 Agent 可访问的目录范围，`/cwd` 内置命令会校验路径是否落在允许范围内。
3. **单会话串行**：`KeyedQueue` 确保同一个 conversation 同时只能驱动一个 Agent，避免并发指令冲突。
4. **Agent 级沙箱**：Codex 的 `--sandbox read-only`、Claude Code 的 `--permission-mode dontAsk` 等参数直接透传给底层 CLI，而不是由 Bridge 自行判断。

### 微信通道的重新实现

`WeixinChannel` 并非直接复用原始插件代码，而是基于同一套 iLink API 重新实现了一个更轻量的版本：

- 会话状态用本地 JSON 文件存储（`~/.agent-bridge/weixin-session.json`），而不是 OpenClaw 的账户系统
- 长轮询、登录、消息去重、session 过期重连全部自包含在 `WeixinChannel` 内部
- `notifyStart` / `notifyStop` 生命周期通过 API 显式通知微信服务端
- 消息去重用 `Map<string, number>` 维护最近 60 秒已见消息 ID，避免微信重复投递触发多次 Agent

### CLI 交互模式

除了微信，Bridge 还提供了一个 `CliChannel`，让终端本身成为一个 Channel。这意味着你可以直接运行 `agent-bridge chat --agent claude`，在终端里与 Claude Code 交互，而不需要打开另一个窗口。这种统一入口的设计，让 Bridge 不只是"微信转接器"，而是所有 CLI Agent 的通用启动器。

## 关键取舍

**为什么不直接复用原始插件代码？**

原始代码与 OpenClaw 的耦合太深：它依赖 `openclaw/plugin-sdk` 的类型定义、依赖 OpenClaw 的配置树、依赖网关注入的 `channelRuntime` 和 `abortSignal`。要把这些全部剥离，工作量不亚于重写。Bridge 选择重写微信通道的核心 API 层，换取零外部依赖的独立可运行性。

**为什么不做成 HTTP 服务或 WebSocket 网关？**

Bridge 的定位是"本机桥接器"，不是"云端网关"。它的目标是让个人开发者能在自己的机器上，用微信消息驱动本地 CLI 工具。做成 HTTP 服务会引入端口监听、身份认证、网络暴露等额外复杂度，与"轻量"目标冲突。

**为什么 Agent 适配器直接调用 CLI 而不是用 SDK？**

因为 Codex、Claude Code、Codebuddy 这些工具的本机体验就是 CLI。它们的最稳定接口是命令行参数和 stdin/stdout，而不是某个可能会变的 API。Bridge 通过 `runCommand` 统一封装子进程调用、超时控制和 stdout 提取，让不同 Agent 的差异收敛在各自的 Provider 里。

## 仍待完善的方向

从 `TODO.md` 可以看到，Bridge 已经解决了配置校验、session 过期、优雅关停、typing 指示器、消息去重、测试覆盖等基础问题，但仍有几个明确的方向：

- 媒体消息支持：当前只能收发文本，图片/语音/文件全部丢弃
- Markdown 过滤：Agent 返回的 markdown 在微信中无法渲染，需要一套简化转换
- 智能路由：按任务类型/成本/能力自动选择最优 Agent，而不是靠用户手动 `/agent`
- 跨 Agent 上下文桥接：切换 Agent 时保留对话摘要，而不是完全重置会话

来源：`/Users/kaikai/projects/test/test-weixin/bridge`

相关页面：[[topics/agent-bridge]] · [[entities/openclaw]] · [[entities/ilink]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]]
