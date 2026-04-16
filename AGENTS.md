# LLM Wiki — 个人知识库模式文件

## 目的与领域

这是一个个人知识 / 自我提升 wiki。由 Claude Code 或 OpenAI Codex 负责维护，Obsidian 作为浏览工具。

核心原则：**wiki 是持续积累的产物，不是每次查询时重新推导的结果。** 每摄入一个来源，知识就被编译进 wiki；每次提问，答案可以归档回 wiki，继续沉淀。

---

## 目录结构

```
raw/          ← 原始资料（只读，永不修改）
  articles/   ← 网络文章（Obsidian Web Clipper 导出的 markdown）
  journal/    ← 日记条目
  podcasts/   ← 播客笔记 / 文字稿
  books/      ← 书籍章节 / 读书笔记

wiki/         ← LLM 生成并维护的所有页面
  index.md    ← 内容目录（每次摄入后更新）
  log.md      ← 只追加的操作日志
  overview.md ← 整体综述与核心主题
  topics/     ← 主题 / 概念综合页
  entities/   ← 人物、框架、心智模型、工具
  sources/    ← 每个来源的摘要页
```

---

## 页面规范

### Frontmatter（除 `wiki/log.md` 外，每个 wiki 页面必须包含）

```yaml
---
title: 中文标题
type: topic | entity | source | overview
tags: [标签1, 标签2]
source_count: 0        # 支撑该页面的来源数量
updated: YYYY-MM-DD
---
```

- `wiki/index.md` 属于导航页，`type` 可使用 `index`
- `wiki/log.md` 属于操作日志页，保持**无 frontmatter**，并遵循“只追加，不修改”原则
- `title` 字段使用中文，要求简短且言简意赅
- frontmatter 已包含标题信息；正文首行不再额外重复同名 `# title` 一级标题，正文直接从摘要或 `##` 小节开始
- 所有 `updated`、`created`、日志标题中的日期，统一使用**东八区北京时间**（`Asia/Shanghai`），不要使用系统默认时区或 UTC
- 若需要生成当天日期，优先显式使用 `TZ=Asia/Shanghai date +%F` 取值后再写入

### 标签规范

- `tags` 中的单个标签**不能包含空格**
- 优先使用中文短语或无空格的英文单词 / 词组
- 不合法示例：`AI Agent`、`Prompt Engenieer`
- 合法示例：`Agent`、`提示词工程`
- 摄入、查询归档、lint 修复时，若发现带空格标签，应统一改为无空格表述

### 文件命名

- 文件名使用英文，全部小写，单词间用连字符，尽可能简短且言简意赅
- 示例：`topics/habit-formation.md`、`entities/james-clear.md`、`sources/atomic-habits-ch1.md`

### 交叉引用

- 所有内部链接使用 Obsidian wikilink 语法：`[[页面名]]`
- 链接到具体章节：`[[页面名#章节标题]]`
- 每个页面底部维护"相关页面"列表

### Markdown 格式

- 所有 `wiki/` 页面，以及 `AGENTS.md`、`CLAUDE.md`，都应遵循 [GitHub Flavored Markdown](https://github.github.com/gfm/)
- 不同段落之间必须保留空行，尤其是标题、正文、列表、引用、代码块、分隔线之间
- `来源：`、`相关页面：` 等页尾段落之间必须保留空行，避免在渲染时粘连
- 中文与英文 / 数字 / 专有名词混排时，应在语义边界补空格，例如 `SQL 查询`、`GFM 格式`、`Top-N 查询`
- 代码块优先使用 fenced code block，并与前后正文保留空行
- lint 或手工修订时，若发现不符合 GFM 的段落间距、列表间距或中英混排，应一并修复

### 内容语言

- 所有 wiki 页面内容使用**中文**撰写
- 文件名、frontmatter 字段名保持英文
- frontmatter 的 `title` 字段值使用中文

### 写作风格

- 所有 markdown 文档都应按“个人技术博客”来写，而不是写成中性词条、资料卡或教科书摘要
- 默认采用一名技术博主的第一人称观察视角来组织内容，风格可参考 Andrej Karpathy：强调问题意识、直觉、取舍判断与个人理解
- 行文应保留作者感，允许出现“我会怎么理解”“我更倾向怎样判断”“这件事真正重要的是什么”这类主观但可辩护的表达
- 文档不只罗列结论，还应解释为什么这个主题值得关心、它与其他概念如何连接、实践中容易踩到什么坑
- 优先写出有节奏的叙述性正文，再辅以小节、列表、引用与代码片段；避免把全文堆成提纲式要点清单
- 即便是 `topics/`、`entities/`、`sources/` 这类知识页，也应尽量写成可连续阅读的博客文章，而不是仅供检索的碎片化摘录
- 允许保留鲜明观点，但论断必须能被来源、经验或清晰推理支撑；不要为了“博客感”牺牲准确性
- 若来源材料本身枯燥，应由作者视角重新组织叙事，提炼出主线、张力与启发，而不是机械转述原文结构
- 标题、摘要、章节名都应服务于阅读体验，优先做到具体、凝练、有判断，而不是泛泛命名
- 唯一例外是 `wiki/log.md`：它仍保持操作日志体，不按博客体改写

---

## 工作流

### 摄入（Ingest）

当用户说"摄入 [来源]"或"处理 [文件]"时：

1. 若文件当前位于默认导入目录 `Clippings/`，先按来源类型将其归类移动到 `raw/` 下对应子目录（如 `raw/articles/`、`raw/journal/`、`raw/podcasts/`、`raw/books/`）
2. 读取 `raw/` 中的来源文件
3. 与用户简短讨论核心要点（可选，用户主导）
4. 在 `wiki/sources/` 创建摘要页
5. 更新 `wiki/index.md`（添加新条目）
6. 更新相关的 `topics/` 和 `entities/` 页面（新建或修改）
7. 更新 `wiki/overview.md`（如有重大新洞见）
8. 在 `wiki/log.md` 追加日志条目
9. 提交一次 git commit，记录本次 wiki 变更用于版本管理
10. 执行一次 git push，将本次版本同步到远端仓库

一个来源通常会触及 5–15 个 wiki 页面。

补充约定：若文件已位于 `raw/` 对应子目录，则跳过归类移动步骤，直接继续后续摄入。

**日记特殊处理**：日记原文保持私密，wiki 页面只记录*规律、主题、情绪趋势*，不引用原文内容。

**书籍处理**：可按章节逐步摄入，每章一个 source 页面，同时维护书籍总览页。

### 查询（Query）

当用户提问时：

1. 读取 `wiki/index.md` 定位相关页面
2. 读取相关页面，综合答案
3. 回答时附上来源引用（`[[页面名]]`）
4. 如果答案有独立价值，询问用户是否归档为新 wiki 页面
5. 如果本次查询产出了新的 wiki 变更，提交一次 git commit 记录版本
6. 将该 commit push 到远端仓库，保持 wiki 的持久同步

### 检查（Lint）

当用户说"检查 wiki"或"lint"时，扫描并报告：

- 页面间的矛盾或过时内容
- 不符合规范的标签（尤其是包含空格的 `tags`）
- 孤立页面（无入链）
- 被多次提及但缺少独立页面的概念
- 缺失的交叉引用
- 可以用网络搜索填补的数据空白
- 建议下一步可以深入的问题或来源

### 版本记录（Git）

- 任何实际写入 `wiki/`、`AGENTS.md` 或 `CLAUDE.md` 的工作流，最后都应执行 `git commit`，随后执行 `git push`。
- commit message 应简洁说明本次操作类型与对象，例如：`ingest: atomic habits ch1`、`query: summarize habit loops`、`lint: fix broken wikilinks`。
- 如果当前环境无法 push，应明确告知用户原因，并在恢复网络后尽快同步远端。
- 推荐格式统一为：`<type>: <object>`。
- `type` 建议仅使用：`ingest`、`query`、`lint`、`wiki`、`workflow`。
- `object` 应描述本次变更的主要对象，使用小写英文短语，必要时保留书名 / 章节 / 主题名。
- 推荐示例：`ingest: atomic habits ch1`、`query: compare deep work and deliberate practice`、`lint: fix orphan pages`、`wiki: update overview links`、`workflow: refine git sync rules`。
- 一次工作流只做一个主题时，优先提交为一个 commit；不要为微小中间状态频繁提交。
- push 约定：默认在当前工作流完成后立即 `git push origin <current-branch>`；若连续进行了多个本地 commit，也应在结束时统一 push。
- `wiki/log.md` 与 git 历史应尽量一一对应：一次有记录价值的工作流，通常对应一条日志和一个 commit。
- 日志中的操作类型应与 commit 的 `type` 保持一致，例如日志写 `ingest`，commit 也应使用 `ingest: ...`。
- 日志标题可用中文面向阅读，commit message 保持英文面向版本历史；两者应描述同一对象，不必逐字一致。
- 推荐对应示例：`## [2026-04-13] ingest | Atomic Habits 第一章` ↔ `ingest: atomic habits ch1`。

---

## 索引格式（wiki/index.md）

```markdown
## 主题
- [[topics/xxx]] — 一行摘要

## 实体
- [[entities/xxx]] — 一行摘要

## 来源
- [[sources/xxx]] — 一行摘要（来源类型，日期）
```

---

## 日志格式（wiki/log.md）

每条日志以固定前缀开头，便于 grep：

```
## [YYYY-MM-DD] ingest | 来源标题
## [YYYY-MM-DD] query | 问题摘要
## [YYYY-MM-DD] lint | 检查摘要
```

以上 `YYYY-MM-DD` 统一按**东八区北京时间**（`Asia/Shanghai`）生成。

示例：

```bash
grep "^## \[" wiki/log.md | tail -5   # 查看最近 5 条操作
```

补充约定：

- 若本次工作流写入了日志并创建了 commit，二者应在语义上对应同一批变更。
- 日志更适合写成人类可读的中文摘要；commit 更适合写成简洁英文标签。
- 若一次工作流包含多个独立主题，优先拆成多条日志与多个 commit，而不是混在同一条记录里。

---

## 扩展说明

- **搜索工具**：wiki 规模较小时，index.md 已足够。当来源超过 ~100 个、页面超过几百个时，考虑引入 [qmd](https://github.com/tobi/qmd) 作为本地搜索引擎。
- **Dataview**：Obsidian Dataview 插件可利用 frontmatter 生成动态表格，例如按标签列出所有主题页。
- **版本历史**：wiki 是 git 仓库，所有变更自动有版本记录。

---

## 多 Agent 协作说明

本 wiki 同时支持 Claude Code（读取 CLAUDE.md）和 OpenAI Codex（读取 AGENTS.md）维护。两者共享同一套 wiki 文件，通过 git 保持同步。

**每次新会话的启动流程（无论哪个 agent）：**

1. 读取 `wiki/log.md` 末尾几条，了解上次做了什么
2. 读取 `wiki/index.md`，掌握当前 wiki 全貌
3. 然后执行用户指令

这两步替代了"resume 上一次会话"——wiki 本身就是持久状态，log 是时间线，index 是地图。不需要依赖对话历史。
