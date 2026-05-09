---
title: oh-my-openagent 架构分析
type: source
tags: [Agent编排, 多智能体, OpenCode, 开源项目]
source_count: 0
updated: 2026-05-09
---

> 本页基于对 oh-my-openagent 源码的实际阅读与 Oracle 子 agent 的架构分析整理而成。分析对象是该项目的 `dev` 分支，核心路径覆盖 `src/index.ts`、`src/plugin/`、`src/tools/delegate-task/`、`src/shared/model-resolution-pipeline.ts`、`src/features/background-agent/` 与 `src/agents/sisyphus.ts` 等模块。

## 这是什么

oh-my-openagent（曾用名 oh-my-opencode）是一个面向 OpenCode 的插件，它把单一会话扩展成"Sisyphus 总调度 + 多模型 specialist 并行执行"的编排运行时。它不替换 OpenCode 的内核，而是利用 OpenCode 的 10 个 hook handler 注入策略、路由、委派、模型回退和生命周期自动化。

## 5 步初始化

插件入口 `src/index.ts` 遵循固定的启动顺序：

1. `loadPluginConfig` —— 加载多级 JSONC 配置（项目 `.opencode/` → 用户 `~/.config/` → 默认），Zod 验证，自动迁移 legacy key。
2. `createManagers` —— 创建 `TmuxSessionManager`、`BackgroundManager`、`SkillMcpManager`、`configHandler`、`modelFallbackControllerAccessor`。
3. `createTools` —— 注册 26 个工具（含 `task` 委派、`call_omo_agent`、LSP、AST-grep、会话管理等）。
4. `createHooks` —— 组合 53 个 lifecycle hook，分 5 个 tier：Core(43) + Continuation(7) + Skill(2)。
5. `createPluginInterface` —— 暴露 10 个 OpenCode hook handler（config / tool / chat.message / chat.params / chat.headers / event / tool.execute.before / tool.execute.after / experimental.chat.messages.transform / experimental.session.compacting）。

## 分层架构

- **Host 层**：OpenCode 负责会话、模型、原生工具执行。
- **Plugin 层**：oh-my-openagent 负责策略注入、agent 路由、category 解析、模型 fallback、后台任务生命周期。
- **Agent 层**：Sisyphus（主调度）+ 10 个 specialist（Oracle、Librarian、Explore、Hephaestus、Prometheus、Metis、Momus、Atlas、Multimodal-Looker、Sisyphus-Junior）。

## Category-Based Delegation

Sisyphus 不直接选择模型，而是选择 `category`（如 `visual-engineering`、`ultrabrain`、`quick`），再由 harness 解析为具体模型。每个 category 有硬编码的 `fallbackChain`，按优先级尝试不同 provider/model：

- `ultrabrain` → gpt-5.5 xhigh → gemini-3.1-pro high → claude-opus-4-7 max → glm-5.1
- `visual-engineering` → gemini-3.1-pro high → glm-5 → claude-opus-4-7 max → glm-5.1
- `quick` → gpt-5.4-mini → claude-haiku-4-5 → gemini-3-flash → minimax-m2.7

解析顺序：用户覆盖 → category 默认 → provider fallback chain → 系统默认。

## 后台任务系统

`task(run_in_background=true)` 触发 `BackgroundManager`：

- 创建独立的 OpenCode 子会话（`session.create({ parentID })`）。
- 并发限制默认 5 个/模型，FIFO 队列。
- 3 秒轮询 + 空闲事件检测 + 10 秒稳定性验证（消息数不变才算完成）。
- 完成后通过 `promptAsync` 向父会话注入 `<system-reminder>` 通知。
- 内置熔断器，检测子 agent 陷入工具循环时自动取消。

## 3 层 MCP

- **Tier 1 Built-in**：websearch(Exa)、context7(官方文档)、grep_app(GitHub 搜索)。
- **Tier 2 `.mcp.json`**：兼容 Claude Code，支持 `${VAR}` 环境变量展开。
- **Tier 3 Skill-embedded**：按 `sessionID:skillName:serverName` 隔离，用完即销毁。

合并优先级：`built-in` → `.mcp.json` → 用户 config → plugin MCP servers。

## 模型解析与回退

通用解析在 `src/shared/model-resolution-pipeline.ts`，4-step：

1. Override（UI 选中 / 用户显式配置）
2. Category default（category 配置中的 model）
3. Provider fallback（用户 `fallback_models` → 硬编码 `fallbackChain`）
4. System default（OpenCode 默认模型）

运行时还有两套独立回退：
- **model-fallback hook**：`chat.params` 级别的预防性回退（provider 错误时切换）。
- **runtime-fallback hook**：`event` 级别，监听 `session.error` / `message.updated` 自动重试并注入 continue。

## Sisyphus 的自动委派

Sisyphus 的 system prompt 被显式训练为自动判断意图并委派：

- 调研类 → `task(subagent_type="explore/librarian", run_in_background=true)`
- 实现类 → `task(category="...", load_skills=[...])`
- 复杂架构 → `task(subagent_type="oracle")`
- 简单任务 → 自己直接处理

Prompt 中强调：并行化一切、background agent 永远 `run_in_background=true`、必须等待 `<system-reminder>` 再收集结果、session continuity 用 `task_id` 续接。

## 关键设计取舍

- **Claude Code 兼容性**：`.mcp.json`、skills、agents、hooks、commands、plugins 全部兼容，降低迁移成本。
- **模型无关的 category 路由**：agent 表达意图，harness 决定模型。模型映射可集中更新。
- **防御性模型回退**：三重保险（解析 pipeline + model-fallback + runtime-fallback），应对 provider 故障、模型名漂移、冷 cache。
- **后台并行**：复杂调研在独立会话中并行跑，不阻塞主对话上下文。
- **生命周期密集**：53 个 hook 把每个决策点变成可插拔策略（文件写保护、comment 检查、规则注入、错误恢复、todo 强制延续等）。

## 与 Anthropic Managed Agents 的对比

| 维度 | oh-my-openagent | Anthropic Managed Agents |
|------|-----------------|--------------------------|
| 定位 | OpenCode 插件 / 编排层 | 托管式长程 agent 运行时 |
| 主调度 | Sisyphus（prompt 驱动） | Managed runtime（基础设施驱动） |
| 模型路由 | Category fallback chain | 用户显式指定或运行时动态 |
| 会话隔离 | OpenCode 子会话 | 内部 session 管理 |
| 可观测性 | Hook + polling + circuit breaker | 内置 tracing、eval、sandbox |
| 部署方式 | 本地 OpenCode 插件 | Anthropic 托管服务 |

两者的共性在于：都把"单模型对话"扩展成"orchestrator + specialist"的分层结构，都强调上下文隔离、模型回退和生命周期管理。

---

相关页面：[[entities/oh-my-openagent]] · [[topics/ai-agent-harness]] · [[topics/multi-agent-systems]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/long-horizon-agents]] · [[entities/anthropic]] · [[entities/managed-agents]]
