---
title: Epoch Semantic Versioning
type: source
tags: [版本管理, SemVer, 开源, JavaScript]
source_count: 1
source_file: raw/articles/epoch-semantic-versioning.md
author: Anthony Fu
published: 2026-04-28
updated: 2026-04-28
---

来源：[[entities/anthony-fu]] · [原文](https://antfu.me/posts/epoch-semver)

## 核心结论

Anthony Fu 这篇文章讨论的是一个很细但很真实的开源维护问题：SemVer 技术上能表达“兼容 / 不兼容”，但人对版本号的感知不是线性的。`v2` 到 `v3` 看起来像大事件，`v125` 到 `v126` 又像小事；维护者因此会迟疑要不要 bump major，最后把很多破坏性变更堆进一次大版本里，反而让用户升级更痛。

Epoch Semantic Versioning 的提案，是在不改变现有 SemVer 工具链的前提下，把第一个数字拆成 `EPOCH` 和 `MAJOR` 的组合：`{EPOCH * 1000 + MAJOR}.MINOR.PATCH`。`MAJOR` 仍表达技术上的不兼容 API 变化，`EPOCH` 则表达更面向人的时代级变化。

## 版本号是一份契约

文章里我最认同的一点，是把 versioning 理解成维护者和用户之间的契约，而不是一个绝对可靠的事实系统。

版本号本身无法完整描述变更，它只是给用户一个风险提示：patch 大概率安全，minor 大概率兼容新增，major 需要认真看 changelog。但任何改动都可能有行为影响，甚至 bug fix 也可能破坏依赖旧行为的用户。所以版本号不是保证，而是帮助用户决定“这次升级要多谨慎”的信号。

这个视角比机械背 SemVer 规则更有用。真正成熟的版本管理，应该让版本号、changelog、release note 和迁移指南一起工作。

## 为什么 zero-major 会被滥用

Anthony Fu 解释了自己长期停在 `v0.x.x` 的原因：SemVer 规定 `0.y.z` 里 minor bump 可以代表 breaking change。于是维护者可以用 `v0.65` 到 `v0.66` 这种变化表达较小的破坏性变更，而不用触发 `v2` 到 `v3` 那种心理负担。

这是一种聪明但不理想的绕路。它确实让 breaking change 更渐进，但也浪费了 SemVer 的第一个数字，让版本号对用户的沟通能力变弱。很多稳定项目长期停在 `v0`，用户反而会误以为它们“不生产可用”。

## Epoch SemVer 的设计

Epoch SemVer 的格式是：

```text
{EPOCH * 1000 + MAJOR}.MINOR.PATCH
```

语义大致是：

- `EPOCH`：重大、时代级、面向用户心智的变化；
- `MAJOR`：技术上不兼容的 API 变化，即使影响面较小；
- `MINOR`：向后兼容的新功能；
- `PATCH`：向后兼容的修复。

比如 UnoCSS 可以从 `v0.65.3` 迁到 `v65.3.0`。如果只是 patch，就是 `v65.3.1`；如果是兼容新功能，就是 `v65.4.0`；如果有小范围 breaking change，可以到 `v66.0.0`；如果是核心大改，才跳到 `v1000.0.0`。

它的妙处是对工具链仍然是合法 SemVer。npm、pnpm、yarn 不需要理解 `EPOCH`，依然按 major range 工作；但维护者和用户可以约定：`1000` 这个量级代表一个更大的时代边界。

## 对我的启发

这篇文章让我重新意识到，版本号不是给机器看的唯一输入，也不是给营销看的大标题，而是一个同时服务机器解析和人类判断的沟通界面。

SemVer 的 `MAJOR.MINOR.PATCH` 已经很好，但它把“任何不兼容 API 变化”和“值得所有用户停下来重新理解的时代级变化”都塞进 major 里。Epoch SemVer 的价值，不是发明一个更精确的数学系统，而是给维护者多一个表达尺度，鼓励更渐进地发布 breaking change，同时保留大版本叙事的空间。

我不会把它当成所有项目都该采用的新规范。低层库、内部服务、小工具可能完全不需要。但对用户量大、升级路径复杂、生态插件多、又想避免长期 `v0` 的框架或工具链来说，它是一个值得观察的版本沟通实验。

---

相关页面：[[topics/software-versioning]] · [[entities/anthony-fu]]
