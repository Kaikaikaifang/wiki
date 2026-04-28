---
title: 走向 ESM-only
type: source
tags: [JavaScript, ESM, CommonJS, Node.js, 开源]
source_count: 1
source_file: raw/articles/move-on-to-esm-only.md
author: Anthony Fu
published: 2026-04-28
updated: 2026-04-28
---

来源：[[entities/anthony-fu]] · [原文](https://antfu.me/posts/move-on-to-esm-only)

## 核心结论

Anthony Fu 这篇文章的判断很直接：到 2025 年，JavaScript 生态已经不太需要继续把 dual CJS / ESM 当成默认姿势；对新包、面向浏览器的包、独立 CLI，以及只支持现代 Node.js 的包来说，ESM-only 已经是更值得优先考虑的发布策略。

我觉得这篇文章重要，不只是因为它讨论了 `type: module` 或 `exports` 这些包配置细节，而是因为它把一个生态迁移问题拆成了三层：工具链是否准备好，运行时互操作是否足够顺滑，维护双格式的成本是否仍然值得支付。

## 生态从过渡期走向默认值

文章开头回顾了 Anthony Fu 自己的立场变化。他三年前还更倾向 dual CJS / ESM，因为那时 aggressive ESM-only 更像低层库作者的 bottom-up 推动：底层依赖先切 ESM，会把许多仍在 CJS 里的上游项目逼到尴尬位置。

现在情况变了。Vite、Nuxt、SvelteKit、Astro、Remix、Storybook、Vitest、tsx、jiti、ESLint flat config 等工具都把 ESM 当成一等公民。也就是说，迁移不再只靠底层包“倒逼”，而是有了更强的 top-down 支撑：应用框架、测试工具、CLI 执行器和配置系统都已经默认理解 ESM。

这个变化很关键。生态迁移最难的地方不是单个项目能不能改，而是依赖链里有没有足够多的中间层愿意承接变化。当高层工具已经 ESM-ready，包作者发布 ESM-only 的阻力就小很多。

## Node.js 的 `require(ESM)` 改变了中间地带

这篇文章里最让我注意的是 Node.js 对 `require()` ESM 模块的支持。过去 CJS 消费 ESM 往往要动态 `import()`，这会把同步调用链染成异步调用链，很多库和配置加载场景很难自然迁移。

`require(ESM)` 的意义，是让 ESM-only 包仍然能被一部分 CJS 代码以接近同步的方式消费。它不等于 CJS 和 ESM 完全没有边界了，但它把迁移路径从“底层或顶层二选一”扩展成了 middle-out：依赖链可以出现 `ESM -> CJS -> ESM -> CJS` 这样的混合路径，而不必马上把所有节点一次性改完。

Node.js 还引入了 `export { Foo as 'module.exports' }` 这种面向 CJS 兼容的导出方式。对包作者来说，这意味着“发布 ESM-only”和“照顾 CJS 消费者”不再总是互斥，只是会把最低 Node.js 版本要求变成新的边界条件。

## dual format 的成本是真成本

dual CJS / ESM 曾经是很有价值的过渡方案，但它不是免费的。

首先是互操作复杂度。CJS 的 `module.exports` 和 ESM 的 default / named exports 在语义上不同，转译后还要处理 `.d.mts`、`.d.cts` 这些类型声明分叉。许多问题最后并不是用户真的需要理解，而是因为包作者为了兼容两套模块系统被迫把复杂度暴露出来。

其次是依赖解析。一个包同时提供 CJS 和 ESM，遇到 transitive dependency、singleton 包和条件导出时，很容易出现“看似同一个包，实际被装载成多个实例”的问题。

最后是包体积。双格式意味着发布物、类型文件和构建产物都可能翻倍。单个包看起来只是几 KB，放进上百个依赖后，就会变成 `node_modules` 的长期膨胀。

## 我会怎么采用这条判断

我不会把 “ESM-only” 理解成一种道德正确，而会把它理解成一个迁移时机判断。

如果是新包、浏览器优先包、独立 CLI、现代 Node.js 工具，默认 ESM-only 已经很合理。反过来，如果包的消费者仍大量停留在旧 Node.js、旧构建链或同步 CJS 插件生态里，dual format 仍可能是更现实的过渡成本。

真正值得借鉴的是 Anthony Fu 的判断方式：不要永远停留在“兼容所有人”的惯性里，也不要为了推动生态而忽视消费者的真实位置。模块格式是生态协议，不是单个仓库里的局部偏好。只有当工具链、运行时和消费者迁移路径都足够成熟时，ESM-only 才会从激进选择变成朴素默认。

---

相关页面：[[topics/javascript-module-systems]] · [[entities/anthony-fu]] · [[entities/nodejs]]
