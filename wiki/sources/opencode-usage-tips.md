---
title: OpenCode 使用技巧与最佳实践
type: source
tags: [OpenCode, AI编程工具, Agent使用, 上下文管理, 工作流]
source_count: 0
updated: 2026-05-19
---

> 本页基于网络文章整理，原作者为 heimoshuiyu（heimoshuiyu/opencode-usage-tips），记录了从实际使用 OpenCode 过程中提炼出的 12 组技巧与判断框架。原始文件归档于 `raw/articles/opencode-usage-tips.md`。

## 来源信息

- 原始标题：OpenCode 使用技巧与最佳实践
- 归档日期：2026-05-19
- 原始位置：`raw/articles/opencode-usage-tips.md`

## 核心要点

### 1. 你是主导者，Agent 是协作者

OpenCode 团队在一次采访中提到：你应该主动去看 Agent 阅读了什么，和 Agent 一起工作，而不是让 Agent 去 leading you。盲目信任 Agent 的输出、不审阅直接采用，不是高效而是风险。比起花哨的多 Agent 框架，作者更倾向直接用模型本身——需要设计前端就直接说"帮我设计前端"，需要讨论方案就直接讨论，需要写文档就说"先不要改代码，先写一份设计文档"。

### 2. 上下文管理是最核心的技能

同样的任务，上下文越短，输出质量越高。当前模型在 200k 上下文后基本是断崖式下跌，500k 召回率不到 60%。主动管理上下文的具体做法：完成一件事就新开会话；plan-build 模式中 plan 阶段消耗大量上下文后，切换 build 前先 `/compact` 压缩；大型任务拆分成小任务逐个验收，每完成一个就提交一次 git commit。

### 3. AGENTS.md 是最实用的记忆方案

项目根目录下的 AGENTS.md 在每次 LLM 调用时都会被加载，始终存在于系统提示词中；子目录下的 AGENTS.md 则是按需加载，只有当 Agent 读取该子目录及其下级文件时才会注入，且同一会话内不会重复注入。这意味着可以把通用规范写在根目录，模块特定规则写在对应子目录中（例如后端目录下写"禁止使用 `if TYPE_CHECKING`"）。

### 4. 配置层级：深层合并而非简单替换

OpenCode 的配置从底到顶分为：内置默认 → 全局配置（`~/.config/opencode/`）→ 项目配置（`opencode.json` 或 `.opencode/`）。加载时逐层合并，上层覆盖下层，但合并是深层合并——全局配置里设了三个模型，项目配置又加一个，最终会得到四个而不是三个。这允许在全局放一套通用偏好，在不同项目中按需微调。

### 5. 工作区与会话的区分

工作区控制 OpenCode 在哪个目录下启动 Agent，决定配置文件读取和权限检查范围。会话则隔离上下文，类似 ChatGPT 左侧的会话列表。多开的实用技巧：`opencode serve` 常驻后台，其他终端用 `opencode attach http://127.0.0.1:4096 --dir /path/to/workspace` 连接，只有一个后端实例在运行。

### 6. 子 Agent 汇报的信息可能失真

主 Agent 派子 Agent 去摸代码结构或批量操作时，子 Agent 返回的内容不一定准确——可能"一本正经地胡说"，把不存在的文件路径当成事实汇报；信息在层层传递中逐渐走样。heimoshuiyu 写了 opencode-verify-subagent-plugin，在子 Agent 返回结果时自动追加 system-reminder，提醒主 Agent 主动验证关键结论。

### 7. 自定义默认 Agent 以调整输出风格

OpenCode 默认系统提示词要求回复控制在 4 行以内，这适合终端快速交互，但如果你习惯完整详细的输出，就会感到受限。作者的做法是定义一个极简自定义 Agent，把 prompt 设为 "You are a helpful assistant"，覆盖所有额外约束。代价是失去默认提示词里的安全指导（如不要提交代码、检查 lint），需要自行权衡。

### 8. Bash 命令守卫

模型有时会习惯性地在 bash 里调用 `grep`、`rg`、`cat`、`find` 等命令去搜索文件，而不是使用 OpenCode 提供的专用工具。opencode-bash-guard-plugin 会在 bash 执行前检查，发现上述命令时拦截并提示使用对应工具。需要绕过时在命令末尾加 `# confirm`。

### 9. 自定义 Vision 子 Agent

有些模型不支持图片输入，但开发中免不了要看截图、读设计稿。可以在 `.opencode/agent/` 下配置一个使用多模态模型的 Vision 子 Agent，主 Agent 遇到图片任务时自动委派给它。

### 10. 远程访问与移动端

`opencode web --hostname 0.0.0.0` 开启 web 模式后，手机浏览器可直接访问。设置 `OPENCODE_SERVER_PASSWORD` 加密码。更好的体验是用 Chrome 打开 `app.opencode.ai` 安装为 PWA，再输入电脑上的 OpenCode 地址。作者推荐用 Tailscale 做网络穿透，手机和电脑如同在同一局域网。

### 11. 关闭不必要的功能以节省资源

- `autoupdate: false` 关闭自动更新
- `snapshot: false` 关闭 `/undo` 回滚功能，明显降低内存占用
- 及时 git commit，避免大量未提交文件拖慢 OpenCode
- LSP 默认关闭（`lsp: true` 手动开启），因为模型反复修改同一文件时，LSP 的实时报错反而干扰

### 12. 常用参考链接

| 资源 | 链接 |
|------|------|
| 模型配置参考 | https://models.dev/api.json |
| 权限配置文档 | https://opencode.ai/docs/permissions/ |
| 插件文档 | https://opencode.ai/docs/plugins/ |
| Agent 文档 | https://opencode.ai/docs/agents#additional |
| 自定义工具 | https://opencode.ai/docs/zh-cn/custom-tools/ |
| LSP 文档 | https://opencode.ai/docs/lsp |
| Web 模式文档 | https://opencode.ai/docs/zh-cn/web/ |
| 生态示例 | https://opencode.ai/docs/zh-cn/ecosystem/ |
| 系统提示词源码 | https://github.com/anomalyco/opencode/blob/main/packages/opencode/src/session/system.ts |
| DeepSeek 编码指南 | https://api-docs.deepseek.com/zh-cn/guides/coding_agents |
| Electron 桌面版 | https://github.com/anomalyco/opencode/releases |

---

相关页面：[[entities/opencode]] · [[topics/opencode-workflow]] · [[topics/agentic-systems]] · [[topics/agent-computer-interface]] · [[topics/ai-agent-harness]] · [[topics/multi-agent-systems]] · [[entities/oh-my-openagent]]
