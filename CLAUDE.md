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

### 精简维护

- 更新 wiki 时，不要只追加内容；应顺手合并重复段落、删减过时判断、替换已经失效的历史描述，避免同一文档越写越长
- 对持续演进的主题页，优先保留当前判断、关键依据和少量必要历史脉络；已经被新结论覆盖的中间推理、临时方案和执行细节应压缩或移除
- 删减时不能破坏可追溯性：重要来源、关键决策和仍有参考价值的反例要保留链接或简短说明，细节交给 `sources/` 页面和 git 历史承载
- 每次更新相关页面时，都应把“新增了什么”和“可以删掉什么”放在同一轮判断里，保持页面精简、言简意赅

### 隐私保护

- **禁止记录本机绝对路径**：wiki 页面、日志和来源引用中，不得出现 `/Users/xxx`、`/home/xxx`、`C:\Users\xxx` 等本机绝对路径。如需引用本地项目，使用相对目录名（如 `test-weixin/bridge`）或公开仓库 URL（如 `https://github.com/...`）
- **禁止记录敏感标识**：不得在 wiki 中写入 Token、API Key、密码、私有 Bucket 名称、内部域名、个人微信号 / 手机号等敏感信息
- **如需引用原始位置**，优先用可公开访问的链接替代本地路径；若来源确实只在本地存在，用描述性相对路径并注明"本地路径，不记录绝对路径"
- lint 时应扫描并清理已泄露的隐私信息

---

## 团队结构

当前阶段（~100 页）不需要多个独立 Agent 物理隔离运行。同一 Agent 在不同任务中切换**思维模式**，既保持灵活性，又提前建立专业化习惯。

### 思维模式（Mental Modes）

| 模式 | 核心职责 | 对应工作流阶段 |
|---|---|---|
| **Ingestor** | 来源读取、分类、frontmatter 标准化、标签合法性检查 | 摄入前端 |
| **Synthesizer** | 提炼主题、维护交叉引用、合并冗余内容 | 摄入中段 + 查询归档 |
| **Curator** | 维护 index/overview 导航结构、识别知识缺口 | 每次摄入后更新索引 |
| **Auditor** | lint、质量兜底、定期扫描 | 独立 lint 工作流 |
| **Editor-in-Chief** | 统一收束阶段（命名、链接、删减、作者声音） | **每个工作流末尾** |

**关键原则**：角色是思维框架，不是 Agent 隔离。Editor-in-Chief 不是独立岗位，而是每个工作流末尾的强制判断阶段。

---

### 摄入（Ingest）

当用户说"摄入 [来源]"或"处理 [文件]"时：

1. **[Ingestor]** 若文件当前位于默认导入目录 `Clippings/`，先按来源类型将其归类移动到 `raw/` 下对应子目录（如 `raw/articles/`、`raw/journal/`、`raw/podcasts/`、`raw/books/`）
2. **[Ingestor]** 读取 `raw/` 中的来源文件
3. **[Ingestor]** 与用户简短讨论核心要点（可选，用户主导）
4. **[Ingestor]** 在 `wiki/sources/` 创建摘要页（frontmatter 标准化、标签无空格检查）
5. **[Synthesizer]** 提炼洞见，更新相关的 `topics/` 和 `entities/` 页面（新建或修改，并适当删减历史无效内容）
6. **[Curator]** 更新 `wiki/index.md`（添加新条目）
7. **[Curator]** 更新 `wiki/overview.md`（如有重大新洞见，并保持综述精简）
8. **[Editor-in-Chief 收束]** 执行统一收束阶段：
   - 命名一致性检查（文件名、wikilink、抽象层级）
   - 链接完整性检查（新页面是否已被正确引用）
   - **删减预算**：列出 1–3 个旧段落的处理决定（保留 / 合并 / 下沉到 `sources/` / 删除）；若无删减候选，明确标注"本轮无删减候选"
   - 作者声音检查（第一人称、问题意识、不写干瘪清单）
9. **[Auditor]** 执行底线门禁（脚本自动检查 frontmatter、标签、死链）
10. 在 `wiki/log.md` 追加日志条目
11. 提交一次 git commit，记录本次 wiki 变更用于版本管理
12. 执行一次 git push，将本次版本同步到远端仓库

一个来源通常会触及 5–15 个 wiki 页面。

补充约定：若文件已位于 `raw/` 对应子目录，则跳过归类移动步骤，直接继续后续摄入。

**日记特殊处理**：日记原文保持私密，wiki 页面只记录*规律、主题、情绪趋势*，不引用原文内容。

**书籍处理**：可按章节逐步摄入，每章一个 source 页面，同时维护书籍总览页。

### 查询（Query）

当用户提问时：

1. **[Synthesizer]** 读取 `wiki/index.md` 定位相关页面
2. **[Synthesizer]** 读取相关页面，综合答案（附来源引用 `[[页面名]]`）
3. **[Curator]** 判断答案是否有独立归档价值；若归档，确定归档位置（`topics/` 或 `entities/`）
4. **[Editor-in-Chief 收束]** 若产生新页面：
   - 命名一致性检查
   - **删减预算**：新增归档页时同步检查可合并/删除的旧内容，列出 1–3 个处理决定
   - 作者声音检查
5. **[Auditor]** 执行底线门禁
6. 提交一次 git commit 记录版本
7. 将该 commit push 到远端仓库，保持 wiki 的持久同步

### 检查（Lint）

当用户说"检查 wiki"或"lint"时：

**步骤 1 [Auditor — 底线自动化]**：运行 lint 脚本自动扫描：
- frontmatter 完整性（除 `wiki/log.md` 外）
- 标签合法性（无空格）
- 死链检测（wikilink 指向不存在的页面）
- 孤立页面检测（无入链）
- 隐私信息扫描（本地绝对路径、API Key 等敏感标识）

脚本用法：`python3 scripts/wiki_lint.py [wiki_dir]`（默认扫描 `wiki/`）

**步骤 2 [Curator — 认知质量抽查]**：
- 页面间的矛盾或过时内容
- 可以删减、合并或移入来源页的冗余内容
- 被多次提及但缺少独立页面的概念
- 缺失的交叉引用
- 可以用网络搜索填补的数据空白
- 建议下一步可以深入的问题或来源

**步骤 3 [Editor-in-Chief 收束]**：
- 对发现的问题制定修复方案
- **删减预算**：针对过时/冗余内容列出处理决定
- 作者声音检查

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

## 删减预算机制

每次新增或大改 `topics/` / `entities/` 页面时，必须同步执行删减判断：

1. **强制结构判断**：列出 1–3 个旧段落的处理决定——保留、合并、下沉到 `sources/`、删除
2. **无删减候选也需声明**：若本轮确实没有可删减内容，明确标注"本轮无删减候选"
3. **删减范围**：主要针对主题页中的重复表述、过时中间判断和低价值总结
4. **可追溯性**：所有删减必须依赖当前读到的页面、git diff 和可追溯来源；必要时先压缩为一句链接，而不是彻底抹除
5. **来源页保护**：不应直接删除来源事实或原始材料

**目的**：防止 wiki 只膨胀不进化，保持页面精简、言简意赅。

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

## 演进路线图

| 阶段 | 条件 | 行动 |
|---|---|---|
| **当前**（~100 页） | 单 Agent 上下文充足，无合并冲突 | 单 Agent + 四思维模式 + 底线自动化 |
| **信号监测** | 持续观察 | 上下文限制、合并冲突、规范耗尽 |
| **下一阶段**（触发信号） | 一次摄入被迫拆分多个会话；或 git 出现真实合并冲突 | 将 Auditor 拆分为独立后台任务；Curator 拆分为定期调度任务 |
| **Team Mode**（远期） | wiki > 500 页；或需要并行摄入多个来源 | 启动 team mode：Ingestor + Synthesizer 并行，Curator 统一收束 |

---

## 成功指标

| 指标 | 目标 | 检查方式 |
|---|---|---|
| 死链率 | < 2% | lint 脚本 |
| 孤立页占比 | < 5% | lint 脚本 |
| 标签合规率 | 100% | lint 脚本 |
| 平均 wikilink 数/页 | > 3 | 脚本统计 |
| 每季度删减预算执行率 | > 80% | `wiki/log.md` 审计 |
| 用户主观满意度 | 持续使用 | 观察使用频率 |

---

## 多 Agent 协作说明

本 wiki 同时支持 Claude Code（读取 CLAUDE.md）和 OpenAI Codex（读取 AGENTS.md）维护。两者共享同一套 wiki 文件，通过 git 保持同步。

**每次新会话的启动流程（无论哪个 agent）：**

1. 读取 `wiki/log.md` 末尾几条，了解上次做了什么
2. 读取 `wiki/index.md`，掌握当前 wiki 全貌
3. 然后执行用户指令

这两步替代了"resume 上一次会话"——wiki 本身就是持久状态，log 是时间线，index 是地图。不需要依赖对话历史。
