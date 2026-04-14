---
title: Query Shape and Index Usage
type: topic
tags:
  - SQL
  - 索引
  - 查询设计
  - 性能
source_count: 4
updated: 2026-04-13
---

# Query Shape and Index Usage

> 决定索引效果的，往往不是“建没建索引”，而是查询把列写成了什么形状。

## `where` 子句是主战场

[[sources/use-the-index-luke]] 把 `where` 子句视为索引调优的核心，因为索引最擅长的就是“快速定位”。如果 `where` 写得模糊、绕弯或把列包进表达式里，数据库即使有索引，也可能只能做大范围扫描。

## 多列索引的基本顺序

最实用的经验法则是：**先等值，后范围。**

- 等值条件越靠前，越能把多列索引收缩到更小子区间；
- 一旦遇到范围条件，后续列通常就更难继续参与真正的访问路径；
- 所以“把选择性最高的列放最左边”不是普适原则，关键是它在查询里扮演等值还是范围角色。

## `LIKE` 只利用第一个通配符之前的前缀

`LIKE 'WIN%D'` 这类模式中，真正能帮助树遍历的是 `WIN` 之前的确定前缀；后面的模式匹配更像过滤。

因此：

- **前缀匹配** 往往仍可索引；
- **前导通配符**（如 `'%term'`）通常破坏索引访问；
- 如果本质是在做全文检索，应该考虑专门的全文索引，而不是强迫 B-tree 承担不擅长的任务。

## 绑定参数与执行计划

绑定参数默认仍然是正确选择，因为它同时解决：

- **安全性**：防止 SQL 注入；
- **复用性**：让数据库能够复用缓存执行计划。

但这份来源也提醒：当具体值会显著改变数据分布与最佳访问路径时，绑定参数会让优化器看不到那些差异。换句话说，**绑定参数通常应该默认使用，但要知道它也会让优化器更“泛化”。**

## 常见反模式

这些写法都容易让索引失效或弱化：

- 对列做函数变换再比较；
- 拼接列后再搜索；
- 把日期、数字写成需要隐式转换的形式；
- 用数学表达式要求数据库“反解方程”；
- 用复杂条件分支把真实意图藏起来。

如果不得不用函数，function-based index 是可选项，但它适合的是少数确实稳定、确定性的表达式，而不是把所有糟糕查询都硬塞给索引。

## 部分索引

对固定常量条件反复出现的查询，可以考虑 partial / filtered index。例如只索引 `processed = 'N'` 的消息，而不是把整个消息表都塞进索引。这会同时缩小索引的行数和宽度。

## 一个实用判断句

写 SQL 时可以不断问自己：**这个条件是在帮助数据库缩小扫描范围，还是只是在它扫完之后再帮忙筛掉一部分结果？**

---

来源：[[sources/use-the-index-luke-preface]] · [[sources/use-the-index-luke-the-where-clause]] · [[sources/use-the-index-luke-execution-plans]] · [[sources/use-the-index-luke-partial-results]]

相关页面：[[topics/sql-indexing]] · [[topics/b-tree-indexes]] · [[topics/sql-execution-plans]] · [[topics/index-supported-sorting-and-pagination]]
