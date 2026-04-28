---
title: 软件版本语义
type: topic
tags: [版本管理, SemVer, 开源, 软件工程]
source_count: 1
updated: 2026-04-28
---

> 我以前容易把版本号看成一种机械规则：breaking change 就 major，feature 就 minor，bug fix 就 patch。读完 [[sources/epoch-semantic-versioning]] 后，我更愿意把版本号看成一层沟通协议：它既要让包管理器能工作，也要让用户大致判断升级风险。

## 版本号不是事实，而是风险信号

版本号无法完整描述软件变化。真实代码改动太复杂，行为影响也不总是可预期。一个 patch release 可能因为修复了旧 bug 而破坏依赖旧行为的用户；一个 major release 也可能只是某个边缘 API 的删除。

所以版本号更像维护者和用户之间的契约。它告诉用户：这次升级大概率应该用什么心态看待。patch 可以更放心，minor 要看新增能力，major 则应该检查 changelog 和迁移说明。

这也是 SemVer 真正有价值的地方：不是因为它完美，而是因为维护者、用户和包管理器都围绕同一套信号做决策。

## SemVer 的人类感知问题

SemVer 的技术规则很清楚：`MAJOR.MINOR.PATCH`。但人对数字的感知不清楚。

`v2` 到 `v3` 会让人觉得是一次很大的产品事件；`v125` 到 `v126` 又让人觉得只是例行更新。可是按 SemVer，它们都只表达“有不兼容 API 变化”。这种心理差异会影响维护者行为：有人不敢频繁 bump major，于是把很多 breaking change 攒到一次大版本；也有人在高 major 之后失去表达重大变化的能力。

这提醒我，版本管理不是纯技术问题。它还有产品叙事、用户心理和生态升级成本。

## zero-major 是一种绕路

长期停在 `v0.x.x` 的项目，经常不是不稳定，而是在利用 SemVer 的特殊规则：`0.y.z` 中 minor bump 可以代表 breaking change。这样维护者可以用更小的数字变化发布渐进破坏，而不触发 `v2`、`v3` 这种心理警报。

但这个做法有明显代价。它让稳定项目看起来“不正式”，也浪费了 major 位置的沟通价值。用户看到 `v0.65`，不一定能理解它其实已经非常成熟。

## Epoch SemVer 的折中

Epoch SemVer 的想法，是在现有 SemVer 三段式里塞进第四层语义：

```text
{EPOCH * 1000 + MAJOR}.MINOR.PATCH
```

`MAJOR` 继续承担技术破坏性变化，`EPOCH` 承担时代级、面向用户心智的变化。比如 `v66.0.0` 可以只是一个较小 breaking change，而 `v1000.0.0` 才代表一个新阶段。

这个方案的工程现实感很强：它不要求 npm、pnpm、yarn 或现有 SemVer parser 改规则。工具仍然看到三段 SemVer；人则通过数字量级理解 `EPOCH`。

我喜欢它的地方，是它没有幻想“全生态一起改规范”。它承认工具链惯性，然后在现有规则里寻找表达空间。

## 我会怎么判断是否采用

Epoch SemVer 不适合所有项目。它更适合这些场景：

- 用户很多，升级影响面大；
- 项目稳定，但仍需要持续引入小的 breaking change；
- 维护者想摆脱长期 `v0`；
- 生态插件多，需要更细的破坏性变化信号；
- 偶尔确实需要一个“新时代”级别的大版本叙事。

它不太适合内部服务、低层小库、生命周期短的工具，或者用户不依赖包管理器版本区间的项目。对这些项目来说，清晰 changelog 和常规 SemVer 可能已经足够。

## 对我的提醒

版本号设计的核心不是“规则更复杂”，而是“升级沟通更诚实”。如果维护者因为害怕 major 而把 breaking change 藏起来，用户最终会在一次大升级里付出更多成本。更好的做法，是让破坏性变化更小、更频繁、更可解释，同时保留真正重大变化的表达空间。

Epoch SemVer 只是其中一种实验。它背后的原则更重要：版本号应该服务于渐进升级，而不是服务于维护者对数字的心理洁癖。

---

来源：[[sources/epoch-semantic-versioning]]

相关页面：[[entities/anthony-fu]] · [[sources/epoch-semantic-versioning]]
