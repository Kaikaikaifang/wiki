---
title: oh-my-openagent
type: entity
tags: [Agent编排, 开源项目, OpenCode]
source_count: 1
updated: 2026-05-09
---

oh-my-openagent（曾用名 oh-my-opencode）是一个为 OpenCode 设计的插件，核心目标是把"单模型对话"扩展为"多 agent 并行编排运行时"。它由 Kim Yeongyu（@code-yeongyu）维护，宣称 Anthropic 曾因该项目封锁 OpenCode 的 Claude 模型访问。

## 核心定位

不是替代 OpenCode，而是在其之上构建编排层：

- OpenCode 负责会话、模型、原生工具执行（host substrate）。
- oh-my-openagent 负责策略注入、agent 路由、category 解析、模型 fallback、后台任务生命周期（orchestration layer）。

## 关键数字

- **10** 个 OpenCode hook handler
- **53** 个 lifecycle hook（分 5 个 tier）
- **26** 个注册工具
- **11** 个内置 agent
- **3** 层 MCP 架构（built-in / `.mcp.json` / skill-embedded）
- **8** 个内置 category（visual-engineering、ultrabrain、deep、artistry、quick、unspecified-low、unspecified-high、writing）

## Sisyphus

主调度 agent，prompt 被显式训练为：

- 每轮消息先做 Intent Gate 分类（research / implementation / investigation / evaluation / fix / open-ended）。
- 默认 bias 是 **DELEGATE**，只在自己处理明显更快时才亲自执行。
- 并行发射 2–5 个 background agent（explore / librarian），等待 `<system-reminder>` 通知后再收集结果。
- 用 `task_id` 维持子 agent 的 session continuity。

## Category 路由

Sisyphus 选择 `category`，harness 解析为具体模型。每个 category 有硬编码的 `fallbackChain`，按可用 provider 依次尝试：

- `ultrabrain`：gpt-5.5 xhigh → gemini-3.1-pro high → claude-opus-4-7 max
- `visual-engineering`：gemini-3.1-pro high → glm-5 → claude-opus-4-7 max
- `quick`：gpt-5.4-mini → claude-haiku-4-5 → gemini-3-flash

解析顺序：用户覆盖 → category 默认 → provider fallback chain → 系统默认。

## 模型回退

三重防御：

1. **解析 pipeline**：`resolveModelPipeline` 的 4-step fallback。
2. **model-fallback hook**：`chat.params` 级别，provider 错误时切换。
3. **runtime-fallback hook**：`event` 级别，监听 `session.error` 自动重试。

## 后台任务系统

`task(run_in_background=true)` 创建独立 OpenCode 子会话：

- 并发限制 5 个/模型，FIFO 队列。
- 3 秒轮询 + 空闲事件 + 10 秒稳定性验证。
- 完成后向父会话注入 `<system-reminder>`。
- 内置熔断器检测工具循环。

## 与同类项目的区别

- **vs Claude Code**：兼容其 hooks、skills、agents、MCPs、plugins，但增加了自动委派和模型路由。
- **vs Cursor / Windsurf**：不是 IDE，而是 harness 插件，模型选择由 category 驱动而非用户手动切换。
- **vs Anthropic Managed Agents**：omo 是本地插件，Managed Agents 是托管服务；两者都认同 orchestrator-worker 分层，但实现路径不同。

## 实用判断

oh-my-openagent 最值得关注的是它把"模型选择"从用户手动操作变成了"category 语义驱动"的自动行为。这意味着：

- 用户只需说"帮我画个前端界面"，系统自动路由到 `visual-engineering` → gemini-3.1-pro。
- 用户只需说"帮我分析这个复杂架构"，系统自动路由到 `ultrabrain` → gpt-5.5 xhigh。

这种抽象的价值在于**模型选择不再是一个配置问题，而变成一个意图表达问题**。

---

来源：[[sources/oh-my-openagent]]

相关页面：[[topics/ai-agent-harness]] · [[topics/multi-agent-systems]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/agent-bridge]] · [[topics/long-horizon-agents]] · [[topics/opencode-workflow]] · [[entities/opencode]] · [[entities/anthropic]] · [[entities/managed-agents]]
