---
title: Use The Index, Luke：Where 子句
type: source
tags:
  - SQL
  - 索引
  - 查询设计
  - 数据库
source_count: 1
source_file: raw/books/use-the-index-luke-sql-performance.md
author: Markus Winand
updated: 2026-04-16
---

来源：[[entities/markus-winand]] · [原文](https://use-the-index-luke.com/sql/where-clause)

## 为什么这是全书主体

作者把 `where` 子句视为索引最核心的应用场景，因为索引的根本功能就是快速筛选。查询慢，很多时候不是没建索引，而是 `where` 写法让索引只能大范围扫描。

## 这一章的主线

- **等值查询**：多列索引里通常先放等值条件；
- **范围查询**：一旦进入范围，后续列对访问路径的帮助会明显减弱；
- **`LIKE` 查询**：只有第一个通配符之前的前缀能真正参与索引访问；
- **函数与表达式**：会遮蔽原始列，让索引失效或退化成过滤；
- **绑定参数**：默认应该使用，但要知道它会让优化器看不见具体值分布；
- **部分索引**：对固定常量条件反复出现的查询，可以只索引满足条件的那部分行。

## 最实用的几条原则

- **等值优先、范围其次**；
- **不要把列藏进函数、拼接、数学表达式或隐式类型转换里**；
- **结果集小不等于扫描范围小**；
- **前导通配符不是 B-tree 擅长的问题**。

## 常见反模式

作者集中批评了一类“聪明但慢”的写法：

- 拼接列后再搜索；
- 用字符串存数字；
- 把日期条件写成函数包裹列的形式；
- 用复杂逻辑分支让优化器看不清真正意图。

这些写法共同的问题是：**数据库很难从表达式中直接推出索引访问边界。**

---

相关页面：[[sources/use-the-index-luke]] · [[topics/query-shape-and-index-usage]] · [[topics/sql-indexing]] · [[topics/sql-execution-plans]]
