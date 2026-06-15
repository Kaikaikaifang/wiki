---
title: MotherDuck 上的 DuckLake 1.0 发布说明
author: MotherDuck
published: "2026-04-17"
link: "https://motherduck.com/blog/announcing-ducklake-1-0-on-motherduck/"
file: raw/articles/announcing-ducklake-1-0-on-motherduck.md
type: source
tags: [数据湖仓, DuckLake, MotherDuck, DuckDB]
source_count: 1
updated: 2026-06-15
---

这篇文章对我最有价值的地方，不是再讲一遍 DuckLake v1.0 有哪些功能，而是把 DuckLake 从“一个有趣的新格式”推进到了“一个可以被托管交付、并且允许多种拥有权模型的产品形态”。

文章先把 DuckLake 的核心直觉重复得很直接：catalog 和 metadata 本来就该落在 SQL 数据库里，Parquet 留给对象存储承载容量层。然后它把这个判断进一步 productize 成了三种托管选项：Fully Managed、Bring-Your-Own-Bucket、Bring-Your-Own-Compute。对我来说，这比功能表更关键，因为它真正回答了“如果我要把 DuckLake 用在团队里，控制权应该停在哪一层”。

相比已有的 [[sources/ducklake-v1-0-announcement]]，这篇文章新增了几个我之前没写进 wiki 的落点：其一，DuckLake 1.0 的稳定规范开始让多引擎接入变得现实，不再只是 DuckDB 自己的实验场；其二，Data Inlining、Sorted Tables、Bucket Partitioning、Variant 这些设计，不只是格式能力，也是在为低延迟托管 lakehouse 服务准备更平滑的读写体验；其三，MotherDuck 把 serverless compute、权限控制和 BYO Bucket / BYO Compute 组合在一起，说明 DuckLake 的“元数据归数据库”路线天然更容易长出服务化外壳。

来源：[[sources/announcing-ducklake-1-0-on-motherduck]]

相关页面：[[topics/ducklake]] · [[entities/ducklake]] · [[entities/motherduck]] · [[sources/ducklake-v1-0-announcement]]
