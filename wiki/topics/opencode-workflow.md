---
title: OpenCode 使用技巧与工作流
type: topic
tags: [OpenCode, 上下文管理, Agent使用, 工作流, 配置管理]
source_count: 1
updated: 2026-05-19
---

这篇文章让我意识到，用好 OpenCode 的关键不在于装多少插件、配多少模型，而在于建立一套清晰的"人主导、Agent 协作"的工作节奏。下面这几点，是我从实际使用经验中提炼出的判断框架。

## 你是主导者，Agent 是协作者

OpenCode 团队在一次采访中有一句话让我印象很深：你应该主动去看 Agent 阅读了什么，和 Agent 一起工作，而不是让 Agent 去 leading you。

这句话精准地概括了使用 AI 编程工具的正确姿态。很多人装了一堆插件和 MCP，却不知道它们在后台干了什么，出了问题也排查不了。比起花哨的多 Agent 框架——三省六部制、自动拆任务自动编排——我更倾向直接用模型本身。需要它做什么，就直接告诉它做什么；不想让它改代码，就说"先不要改，先写设计文档"。模型本身的能力已经足够强，你需要的只是一个能听懂你说话、老老实实干活的工具，而不是一个替你做决策的"智能管家"。

## 上下文管理是最核心的技能

一个基本事实是：同样的任务，上下文越短，输出质量越高。当前模型都是上下文越长质量越差，200k 之后基本是断崖式下跌。DeepSeek V4 的论文数据显示，500k 上下文的召回率不到 60%。

所以我倾向于主动管理上下文：

- **完成一件事之后新开一个会话**，保持上下文干净
- **plan-build 模式中，plan 阶段消耗大量上下文后，切换 build 前先 `/compact` 压缩**
- **大型任务先写详细计划拆分成小任务**，逐个开会话逐个验收，每完成一个就提交一次 git commit
- **确实需要延续上下文时**，把关键信息告诉 Agent 或告诉它去哪里找，而不是带着整个历史对话

## AGENTS.md 是最实用的记忆方案

我尝试过各种第三方记忆插件和 MCP，说实话没见到什么普遍认可的方案，最后还是回归到直接写 AGENTS.md。

它的加载机制值得了解：

- **根目录 AGENTS.md**：每次 LLM 调用都加载，始终存在于系统提示词中——适合放项目技术栈、编码规范、常用命令
- **子目录 AGENTS.md**：只有当 Agent 读取该子目录及其下级文件时才注入，同一会话内不会重复——适合放模块特定规则

举个例子，有些模型写 Python 后端时会习惯性地用 `if TYPE_CHECKING` 做延迟导入，但我的项目根本没有循环依赖。于是我在后端目录下放了一个 AGENTS.md，写上"禁止使用 `if TYPE_CHECKING`"，并附上代码示例。这样只有当 Agent 读写后端代码时，这条规则才会被注入，不会污染其他模块。

## 配置层级的深层合并逻辑

OpenCode 的配置不是一份文件说了算，而是多层叠加：

1. **内置默认**：各家模型的连接参数、上下文限制，打包在程序里
2. **全局配置**（`~/.config/opencode/`）：个人通用偏好，如常用 provider、默认 Agent
3. **项目配置**（`opencode.json` 或 `.opencode/`）：只对当前项目生效

加载时从底层往上逐层合并，**是深层合并而非简单替换**。全局配了三个模型，项目又加一个，最终会得到四个模型。只有在两个层级对同一字段设了不同值时，才会用上层的覆盖下层的。

这个机制意味着你可以在全局配置里放一套通用的模型和偏好，在不同项目中按需微调，互不干扰。

## 子 Agent 的信息传递失真

主 Agent 在处理复杂任务时，经常会让子 Agent 代劳——比如派 explore 子 Agent 去摸清代码结构，或者让 general 子 Agent 去批量执行操作。子 Agent 干完活后会把结果汇报给主 Agent，主 Agent 再基于这些结果做决策。

但这里有个容易被忽视的问题：**子 Agent 汇报的内容不一定准确**。有时候它会"一本正经地胡说"，把不存在的文件路径当成事实；有时候信息在层层传递中逐渐走样，传到第三个人耳朵里已经面目全非。主 Agent 拿到失真信息后，后续判断自然也会跑偏。

heimoshuiyu 写的 opencode-verify-subagent-plugin 就是用来应对这个问题的：每当子 Agent 完成任务返回结果时，插件会自动在结果末尾追加一条 system-reminder，提醒主 Agent 不要照单全收，要主动验证关键结论。

## 自定义默认 Agent 调整输出风格

OpenCode 默认系统提示词要求回复尽量控制在 4 行以内，能一个词回答就别用一句话。这个设计初衷是适配终端场景下的快速交互，但如果你习惯看到完整、详细的输出，它就会变成减分项。

一个可行的做法是定义极简自定义 Agent：

```json
{
  "default_agent": "normal",
  "agent": {
    "normal": {
      "prompt": "You are a helpful assistant."
    }
  }
}
```

这样主 Agent 的系统提示词就只剩一句话，没有任何额外约束。代价是失去默认提示词里的安全指导（不要提交代码、检查 lint 等），需要自行权衡是否值得。

## Bash 命令守卫

模型有时习惯性地在 bash 里调用 `grep`、`rg`、`cat`、`find` 等系统命令去搜索文件，而不是使用 OpenCode 提供的专用工具。这种做法不仅效率低，还容易出问题：输出格式不规范、漏了关键参数、扫描到 `node_modules` 里塞满上下文。

opencode-bash-guard-plugin 在 bash 命令执行前做检查，发现上述命令时拦截并提示使用对应工具。如果确实需要绕过，在命令末尾加 `# confirm` 即可放行。

## 实用技巧速查

- **多开工作区**：`opencode serve` 常驻后台，其他终端用 `opencode attach http://127.0.0.1:4096 --dir /path/to/workspace` 连接
- **远程访问**：`opencode web --hostname 0.0.0.0` + `OPENCODE_SERVER_PASSWORD` + Tailscale 网络穿透
- **关闭自动更新**：配置中写 `"autoupdate": false`
- **节省内存**：配置中写 `"snapshot": false` 关闭 `/undo` 回滚
- **加速运行**：及时 git commit，避免大量未提交文件拖慢 OpenCode；不要让 git 追踪 `node_modules`
- **LSP**：默认关闭， `"lsp": true` 手动开启；环境变量 `OPENCODE_EXPERIMENTAL_LSP_TOOL` 解锁跳转定义、查找引用

---

来源：[[sources/opencode-usage-tips]]

相关页面：[[entities/opencode]] · [[entities/oh-my-openagent]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/ai-agent-harness]] · [[topics/multi-agent-systems]] · [[topics/local-llm-inference]]
