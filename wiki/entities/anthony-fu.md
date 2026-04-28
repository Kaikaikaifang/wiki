---
title: Anthony Fu
type: entity
tags: [开源, JavaScript, Vue, 工具链]
source_count: 1
updated: 2026-04-28
---

> 我对 Anthony Fu 的印象，是一个很会把工具链实践、开发者体验和开源维护问题放在一起思考的工程师。[[sources/epoch-semantic-versioning]] 这篇文章就是一个典型例子：表面上讲版本号，实际在讲维护者如何更诚实地和用户沟通升级风险。

## 在这个 wiki 中的重要性

目前 Anthony Fu 在这份 wiki 里主要作为 Epoch SemVer 提案的作者出现。文章里提到的 UnoCSS、Slidev、unplugin-vue-components 等项目，都有一个共同特征：它们是面向大量前端用户和生态插件的开源工具，版本号不只是发布标记，也会直接影响用户升级判断。

这让我更容易理解为什么他会关心 zero-major versioning 和 Epoch SemVer。对这种项目来说，过早把所有 breaking change 都包装成传统 major，会制造不必要的心理负担；长期停在 `v0`，又会损害稳定性沟通。Epoch SemVer 是在这两个极端之间找一个现实折中。

## 对我的提醒

Anthony Fu 这篇文章最值得我借鉴的，不是具体是否采用 `EPOCH * 1000 + MAJOR`，而是他处理开源维护问题的方式：先承认现有生态工具链的约束，再在约束里寻找更好的沟通协议。

这种思路比“发明一个全新规范”更接近真实工程。很多时候，好的设计不是推翻现有系统，而是在不破坏现有系统的前提下增加一层人能理解的语义。

---

来源：[[sources/epoch-semantic-versioning]]

相关页面：[[topics/software-versioning]] · [[sources/epoch-semantic-versioning]]
