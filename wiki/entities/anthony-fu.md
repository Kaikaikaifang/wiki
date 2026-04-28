---
title: Anthony Fu
type: entity
tags: [开源, JavaScript, Vue, 工具链]
source_count: 2
updated: 2026-04-28
---

> 我对 Anthony Fu 的印象，是一个很会把工具链实践、开发者体验和开源维护问题放在一起思考的工程师。[[sources/epoch-semantic-versioning]] 表面上讲版本号，实际在讲维护者如何沟通升级风险；[[sources/move-on-to-esm-only]] 表面上讲 ESM-only，实际在讲什么时候应该停止为历史兼容继续支付复杂度。

## 在这个 wiki 中的重要性

目前 Anthony Fu 在这份 wiki 里主要作为开源工具链维护者出现。文章里提到的 UnoCSS、Slidev、unplugin-vue-components、Vite 生态工具等项目，都有一个共同特征：它们面向大量前端用户和生态插件，很多设计决策不只是仓库内部偏好，而会直接影响用户升级、依赖解析和构建体验。

这让我更容易理解为什么他会同时关心 zero-major versioning、Epoch SemVer 和 ESM-only。对这种项目来说，版本号和模块格式都是维护者与生态之间的协议：前者告诉用户升级风险，后者决定依赖链如何被运行时和工具链装载。

Epoch SemVer 是在传统 major 和长期 `v0` 之间找表达尺度；ESM-only 则是在 dual format 过渡期和现代工具链默认值之间找切换时机。两者背后的思路很一致：承认现有生态约束，但不把历史包袱无限期合理化。

## 对我的提醒

Anthony Fu 这些文章最值得我借鉴的，不是具体是否采用 `EPOCH * 1000 + MAJOR`，也不是所有包都立刻切 ESM-only，而是他处理开源维护问题的方式：先承认现有生态工具链的约束，再在约束里寻找更好的沟通协议。

这种思路比“发明一个全新规范”更接近真实工程。很多时候，好的设计不是推翻现有系统，而是在不破坏现有系统的前提下增加一层人能理解的语义；好的迁移也不是永远兼容所有旧路径，而是在时机成熟时把复杂度从默认路径里拿掉。

---

来源：[[sources/epoch-semantic-versioning]] · [[sources/move-on-to-esm-only]]

相关页面：[[topics/software-versioning]] · [[topics/javascript-module-systems]] · [[sources/epoch-semantic-versioning]] · [[sources/move-on-to-esm-only]]
