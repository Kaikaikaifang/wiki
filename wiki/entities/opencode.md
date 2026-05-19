---
title: OpenCode
type: entity
tags: [OpenCode, AI编程工具, CLI工具, Agent运行时]
source_count: 1
updated: 2026-05-19
---

OpenCode 是一个面向开发者的 AI 编程 Agent 工具，支持 TUI、Web 和桌面端（Electron）三种交互形态。它把模型对话能力封装成可编写配置文件、可扩展插件、可自定义 Agent 的运行时，核心定位不是"替你做决策的智能管家"，而是"能听懂你说话、老老实实干活的协作者"。

## 核心形态

- **TUI**：终端交互界面，最稳定、资源占用最低的日常形态
- **Web**：浏览器访问，`opencode web --hostname 0.0.0.0` 开启，移动端可用，可安装为 PWA
- **桌面端**：Electron 封装，目前仍在测试中，部分功能不稳定

## 关键概念

- **工作区（workspace）**：控制 OpenCode 在哪个目录下启动，决定配置文件读取和文件权限检查范围
- **会话（session）**：隔离上下文，类似 ChatGPT 左侧的会话列表
- **AGENTS.md**：作为系统提示词一部分注入的记忆方案，根目录版本每次调用都加载，子目录版本按需加载
- **配置层级**：内置默认 → 全局配置（`~/.config/opencode/`）→ 项目配置（`opencode.json` / `.opencode/`），深层合并，上层覆盖下层
- **子 Agent**：自定义的 specialist Agent，放在 `.opencode/agent/` 下，主 Agent 按任务类型自动委派

## 核心能力

- **模型接入**：预置 `models.dev/api.json` 中的主流模型配置，`/connect` 即可快速接入；也支持手动写 JSON 配置接入中转站等特殊场景
- **上下文压缩**：内置 `/compact` 机制，上下文快满时自动触发压缩；也有交互式演示页面可直观看到压缩前后的变化
- **工具集**：`grep`、`glob`、`read`、`edit`、`write`、`bash` 等专用工具，模型调用比直接用 bash 命令更可靠
- **LSP 支持**：默认关闭，可手动开启；开启后支持实时类型检查，实验性功能还包括跳转定义、查找引用
- **插件系统**：通过 hook handler 注入策略，已有社区插件如 bash-guard、verify-subagent 等

## 与 oh-my-openagent 的关系

oh-my-openagent 是一个 OpenCode 插件，它在 OpenCode 之上构建编排层，把单一会话扩展为多 agent 并行运行时。OpenCode 负责会话、模型、原生工具执行（host substrate），oh-my-openagent 负责策略注入、agent 路由、category 解析和后台任务生命周期（orchestration layer）。

---

来源：[[sources/opencode-usage-tips]]

相关页面：[[entities/oh-my-openagent]] · [[topics/opencode-workflow]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/ai-agent-harness]] · [[topics/multi-agent-systems]] · [[topics/local-llm-inference]]
