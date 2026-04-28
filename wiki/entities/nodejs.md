---
title: Node.js
type: entity
tags: [JavaScript, 运行时, ESM, CommonJS]
source_count: 1
updated: 2026-04-28
---

> 在这份 wiki 里，我现在主要从模块系统演进的角度理解 Node.js：它不是单纯“支持 JavaScript 的服务端运行时”，而是 npm 生态、模块格式、包发布协议和工具链迁移路径共同交汇的地方。

## 为什么它重要

[[sources/move-on-to-esm-only]] 让我重新注意到 Node.js 在 ESM 迁移里的位置。很多时候我们会把 ESM-only 讨论成包作者自己的选择，但包作者真正能不能这么做，很大程度取决于 Node.js 运行时是否给了足够平滑的消费路径。

过去最大的痛点之一，是 CJS 代码消费 ESM 模块时经常要用动态 `import()`。这会把同步加载路径变成异步路径，对配置加载、插件系统和 CLI 启动链路很不友好。Node.js 支持 `require(ESM)` 后，这个边界没有消失，但迁移从“一次性改完整条依赖链”变成了更接近渐进改造。

## 我会关注的边界

Node.js 的 ESM 支持不是一个单点功能，而是一组边界条件：

- ESM 能否被 CJS 以可接受方式消费；
- ESM 包是否能提供 CJS 兼容导出；
- 包的最低 Node.js 版本要求是否可以上调；
- `exports`、`type: module`、`.mjs`、`.cjs` 与类型声明如何共同工作；
- 工具链是否已经把这些规则包起来，不再让最终用户反复踩坑。

这些边界决定了 ESM-only 是成熟默认值，还是仍然会变成用户升级时的断点。

## 对我的提醒

Node.js 的价值经常体现在“生态中间层”的稳定性上。它既不能只追求新规范，也不能永远被历史兼容拖住。好的运行时演进，应该给包作者更简单的发布目标，同时给旧项目可迁移的中间路径。

`require(ESM)` 正是这种中间路径的例子。它没有要求所有 CJS 项目立刻消失，却让 ESM-only 包更容易成为现实选择。

---

来源：[[sources/move-on-to-esm-only]]

相关页面：[[topics/javascript-module-systems]] · [[sources/move-on-to-esm-only]]
