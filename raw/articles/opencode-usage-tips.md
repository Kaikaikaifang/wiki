# OpenCode 使用技巧与最佳实践

---

## 1. 核心理念：知道自己要干什么

用 OpenCode 之前，最重要的一件事是想清楚自己在做什么。Agent 本质上是一种更快的代码输入方式，它帮你提效，但人必须理解问题本身。盲目信任 Agent 的输出、不管它写了什么就直接用，这不叫高效，这叫瞎搞。

很多人喜欢装一堆插件和 MCP，觉得功能越多越好。但装了一堆东西之后，你甚至不知道它们在后台干了什么，出了问题也排查不了。回归简单实用的形态才是正途——关键不在于你拥有多少工具，而在于你是否清楚地知道每一步在做什么。

OpenCode 团队在一次采访分享（[YouTube](https://youtu.be/YpjoPWCncDY?t=1794)）中有一句话让我印象很深：你应该主动去看 Agent 阅读了什么，和 Agent 一起工作，而不是让 Agent 去 leading you。这句话精准地概括了使用 AI 编程工具的正确姿态——你是主导者，Agent 是协作者。你要主动去审阅 Agent 读取了哪些文件、理解了哪些上下文、基于什么信息做出了决策，而不是把需求丢给它就等着收结果。只有这样，你才能真正掌控开发过程，也才能在 Agent 出错的时候第一时间发现问题。

比起市面上各种华丽的智能体框架——多 Agent 工作流、三省六部制、自动拆任务自动编排——我更倾向于原汁原味地使用模型本身。需要它做什么，就直接告诉它做什么。要设计前端，不需要安装一个"前端设计专用 Agent"，只需要跟它说"帮我设计前端"；要讨论方案，就跟它讨论，审阅完再执行；不想让它直接改代码，就说"先不要改代码，先写一份设计文档"。这些事情靠语言指令就够了，不需要搞什么多智能体框架，不需要装一堆插件，不需要 plan-build 模式自动流转。模型本身的能力已经足够强，你需要的只是一个能听懂你说话、老老实实干活的工具，而不是一个替你做决策的"智能管家"。

---

## 2. 模型配置

OpenCode 已经把各家模型的配置预置在了 [models.dev/api.json](https://models.dev/api.json) 里，大多数情况下你只需要在 TUI 中执行 `/connect`，搜到对应的模型，填上 API 密钥就能直接用了，完全不需要碰配置文件。

真正需要手动写配置的场景不多，主要是中转站之类的特殊接入方式。这时候建议先去 [models.dev/api.json](https://models.dev/api.json) 找到你要用的那个模型，把它的配置抄过来作为起点，再根据实际情况微调。手动配置容易漏字段，有几个地方值得特别留意：交错思考（interleaved thinking）关系到模型能不能正确回传思考过程，配错了要么思考内容丢了要么直接报错；`limit.output` 决定单次输出的上限，不写的话默认只有 32000；`limit.context` 决定上下文窗口的大小，设得合理的话，上下文快满的时候会自动触发压缩，不至于直接撑爆。

---

## 3. 上下文管理

上下文管理是使用 OpenCode 最核心的技能。一个基本事实是：同样的任务，上下文越短，输出质量越高。当前的模型都是上下文越长质量越差，200k 之后基本是断崖式下跌。根据 deepseek v4 的论文数据，500k 上下文的召回率只有不到 60%。

所以我倾向于主动管理上下文。具体的做法是：完成一件事之后新开一个会话，保持上下文干净；如果使用 plan-build 模式，plan 阶段消耗了大量上下文后，在切换到 build 之前先手动执行 `/compact` 压缩一下。如果确实需要延续之前的上下文，可以把关键信息告诉 Agent，或者告诉它去哪里找，而不是把整个历史对话都带着。一个会话只做一件事，大型任务先写详细的计划拆分成小任务，逐个开会话逐个验收，每完成一个就提交一次 git commit。

关于 OpenCode 内部的上下文压缩机制，我做了一个交互式的说明页面，可以直观地看到压缩前后上下文的变化：[OpenCode /compact 机制原理](https://hmsy-public.s3.amazonaws.com/compact-demo.html)。

---

## 4. 会话与任务管理

OpenCode 有两个核心概念需要区分：工作区和会话。工作区控制 opencode 在哪个目录下启动 Agent，它会读取该目录下的配置文件，权限检查也默认允许访问工作区目录内的文件。会话则用来隔离上下文，就像 ChatGPT 左侧的会话列表一样。

多开 OpenCode 有一个很实用的技巧：先用 `opencode serve` 开启一个服务常驻后台，然后在其他终端窗口用 `opencode attach http://127.0.0.1:4096 --dir /path/to/your/workspace` 的方式连接上去。这样实际上只有一个后端实例在运行，其他窗口都只是轻量的客户端，资源占用比同时启动多个独立的 opencode 进程要少得多，同时又能各自操作不同的工作区和会话。

---

## 5. AGENTS.md：最实用的记忆方案

目前最接近"记忆"功能的方案就是 AGENTS.md。我尝试过各种第三方记忆插件和 MCP，说实话没见到什么普遍认可的方案，最后还是回归到直接写 AGENTS.md。

AGENTS.md 的内容会作为系统提示词的一部分注入到上下文中，你可以在这里写项目的技术栈、编码规范、常用命令、工作流程等。它的加载机制值得了解一下：项目根目录下的 AGENTS.md 在每次 LLM 调用时都会被加载，始终存在于系统提示词中；而子目录下的 AGENTS.md 则是按需加载的，只有当 Agent 通过 read 工具读取该子目录及其下级目录中的文件时，对应目录下的 AGENTS.md 才会被注入到上下文里，并且同一个会话内不会重复注入。

这意味着你可以把通用的项目规范写在根目录的 AGENTS.md 里，而把特定模块的规则写在对应子目录中。举个例子，我发现有些模型在写 Python 后端代码时会习惯性地用 `if TYPE_CHECKING` 做延迟导入，但我的项目根本没有循环依赖，完全不需要这样做。于是我在后端目录下放了一个 AGENTS.md，写上"禁止使用 `if TYPE_CHECKING`"这条规则，并附上推荐和禁止的代码示例。这样只有当 Agent 读写后端代码时，这条规则才会被注入到上下文中，不会污染其他模块的上下文。

---

## 6. 配置层级与覆盖机制

OpenCode 的配置不是一份文件说了算，而是有多层叠加的机制。理解这个层级关系，对合理组织配置很有帮助。

最底层是 OpenCode 内置的默认配置，比如各家模型的连接参数、上下文限制等，这些打包在程序里，你不需要关心。往上一层是全局配置，放在 `~/.config/opencode/` 目录下，对所有项目生效，适合放你个人的通用偏好，比如常用的 provider、默认 Agent 等。再往上是项目级配置，可以是项目根目录下的 `opencode.json`，也可以是 `.opencode/` 目录下的配置文件，它只对当前项目生效。配置加载时从底层往上逐层合并，上层覆盖下层——也就是说，如果你在项目配置里给某个模型设了不同的参数，它会覆盖全局配置里的同名项，而全局配置又会覆盖内置默认值。

值得一提的是，这个合并是深层合并而非简单替换。如果你在全局配置里设了三个模型，在项目配置里又加了一个模型，最终会得到四个模型而不是三个。只有在两个层级对同一个字段设了不同的值时，才会用上层的覆盖下层的。这个机制意味着你可以在全局配置里放一套通用的模型和偏好，然后在不同项目中按需微调，互不干扰。

---

## 7. 远程与移动端

OpenCode 的 web 模式一直都适配移动端。启动方式很简单：`opencode web --hostname 0.0.0.0` 让它监听所有地址，然后用手机浏览器打开电脑的 IP 地址加 4096 端口就行。为了安全，设置 `OPENCODE_SERVER_PASSWORD` 环境变量来加一个访问密码。更好的体验是用 Chrome 打开 `app.opencode.ai`，安装成 PWA 应用，然后在里面输入电脑上 OpenCode 的地址。我自己搭了 Tailscale 来做网络穿透，这样手机和电脑之间就像在同一个局域网内一样。

另一种方案是租一台高共享带宽的轻量服务器，搭 Tailscale 或 WireGuard VPN 或者反向代理，就能远程访问工作电脑上的 OpenCode。成本大约 50 块钱一个月。

---

## 8. 自定义 Vision 子 Agent

有些模型本身不支持图片输入，但你在开发过程中又免不了要让 Agent 看截图、读设计稿、分析报错画面。OpenCode 的自定义 Agent 机制可以解决这个问题——写一个专门处理图片的子 Agent，配置一个支持多模态的模型，放到 `.opencode/agent/` 目录下就行。主 Agent 遇到图片相关的任务时，会自动把任务委派给这个子 Agent 处理。

我做了一个可以直接用的 Vision 子 Agent 配置文件，可以从[这里下载](https://hmsy-public.s3.amazonaws.com/vision.md)。下载后放到项目的 `.opencode/agent/vision.md` 路径下即可生效。需要注意的是，文件里配置的模型是 `zhipuai-coding-plan/glm-5v-turbo`，你需要根据自己的实际情况替换成你有权使用的多模态模型，比如 `opencode-go/kimi-k2.6` 等。

---

## 9. 主 Agent 与子 Agent 的信息传递

主 Agent 在处理复杂任务时，经常会让子 Agent 代劳——比如派一个 explore 类型的子 Agent 去摸清代码结构，或者让 general 子 Agent 去批量执行某些操作。子 Agent 干完活后，会把结果汇报给主 Agent，主 Agent 再基于这些结果做决策。

这里有一个容易忽视的问题：子 Agent 汇报的内容不一定准确。有时候它会"一本正经地胡说"，把不存在的文件路径当成事实汇报；有时候信息在层层传递中逐渐走样，就像传话游戏一样，传到第三个人耳朵里已经面目全非。主 Agent 拿到这些失真的信息后，基于它做出的后续判断自然也会跑偏。

我写了一个插件 [opencode-verify-subagent-plugin](https://github.com/heimoshuiyu/opencode-verify-subagent-plugin) 来应对这个问题。它的思路很简单：每当子 Agent 完成任务返回结果时，插件会自动在结果末尾追加一条 system-reminder，提醒主 Agent 不要照单全收，要主动验证关键结论。这样做有两个好处：一是降低主 Agent 被错误信息带偏的概率，二是这些追加的验证上下文本身也能丰富主 Agent 的信息量，减少它在信息不足时自己编造答案的情况。

---

## 10. 自定义默认 Agent

OpenCode 的默认 Agent 有一套相当详尽的系统提示词（可以在源码的 `packages/opencode/src/session/prompt/default.txt` 中看到），其中包含了代码风格、工具使用策略、安全规范等各种指导。其中有一条很显眼的要求：回复尽量控制在 4 行以内，能一个词回答就别用一句话。这个设计初衷是为了适配终端场景下的快速交互，但如果你习惯看到完整、详细的输出，它就会变成一个减分项。

我的做法是定义一个极简的自定义 Agent，在配置文件中覆盖默认行为：

```JSON
{
  "default_agent": "normal",
  "agent": {
    "normal": {
      "prompt": "You are a helpful assistant."
    }
  }
}
```

这样主 Agent 的系统提示词就只剩下一句话，没有任何额外约束，模型会按照自己的理解给出自然的回复。这个做法不一定适合所有人——默认提示词里的很多指导（比如不要提交代码、检查 lint）确实是有价值的——但如果你更看重输出完整性和自由度，可以试试这条路。

---

## 11. Bash 命令守卫

OpenCode 为 Agent 提供了专用的 `grep`、`glob`、`read`、`edit` 等工具，但模型有时候还是会习惯性地在 bash 里调用系统命令去搜索文件——比如 `grep`、`rg`、`cat`、`find`。这种做法不仅效率低，还容易出问题：输出格式不规范、漏了关键参数、扫描到 `node_modules` 里塞满上下文，种种情况都可能发生。

[opencode-bash-guard-plugin](https://github.com/heimoshuiyu/opencode-bash-guard-plugin) 就是用来解决这个问题的。它会在 bash 命令执行前做一次检查，如果发现命令以 `grep`、`rg`、`cat`、`find`、`sed`、`cd` 等开头，就拦截并提示 Agent 使用对应的专用工具。逻辑很简单，但效果立竿见影。如果确实需要绕过守卫执行原始命令，在命令末尾加上 `# confirm` 即可放行。

---

## 12. 其他实用技巧

**关闭自动更新**：在配置文件中写 `"autoupdate": false` 即可。

**关闭 Snapshot 节省内存**：如果你不需要 `/undo` 回滚工作区修改的功能，在配置中写 `"snapshot": false`，这对内存占用有明显影响。另外，仓库中大量未提交的 git 文件也会导致 OpenCode 变慢，记得让 Agent 及时提交，也别让 git 追踪 `node_modules` 之类的目录。

**LSP 配置**：LSP 默认关闭，在配置中写 `"lsp": true` 即可开启。之所以默认关闭，是因为模型实现一个功能时通常要反复修改同一文件，而 LSP 会在每次保存后立即报出未完成的语法错误——模型还没改完就被一堆红字打断，反而越改越乱。官方在试过一段时间默认开启后，最终决定关掉它。如果你确信自己需要实时的类型检查和错误提示，可以手动开启；另外设置环境变量 `OPENCODE_EXPERIMENTAL_LSP_TOOL` 后，还能解锁跳转定义、查找引用等进阶能力。

**Bun 与 Electron**：桌面端目前使用的是 Node.js 运行时，许多功能还在测试中，由于 Electron 本身的问题，偶尔也会遇到一些莫名其妙的 bug。相对来说 TUI 端更加稳定，日常使用建议优先选择 TUI。如果你需要桌面端的界面体验，可以用 `opencode web` 开启 web 模式，然后通过浏览器访问，既稳定又能获得和桌面端类似的界面。

---

## 附录：常用参考链接

| 资源            | 链接                                                                                                |
| ------------- | ------------------------------------------------------------------------------------------------- |
| 模型配置参考        | https://models.dev/api.json                                                                       |
| 权限配置文档        | https://opencode.ai/docs/permissions/                                                             |
| 插件文档          | https://opencode.ai/docs/plugins/                                                                 |
| Agent 文档      | https://opencode.ai/docs/agents#additional                                                        |
| 自定义工具         | https://opencode.ai/docs/zh-cn/custom-tools/                                                      |
| LSP 文档        | https://opencode.ai/docs/lsp                                                                      |
| Web 模式文档      | https://opencode.ai/docs/zh-cn/web/                                                               |
| 生态示例          | https://opencode.ai/docs/zh-cn/ecosystem/                                                         |
| 系统提示词源码       | [GitHub](https://github.com/anomalyco/opencode/blob/main/packages/opencode/src/session/system.ts) |
| DeepSeek 编码指南 | https://api-docs.deepseek.com/zh-cn/guides/coding_agents                                          |
| Electron 桌面版  | [GitHub Releases](https://github.com/anomalyco/opencode/releases)                                 |