---
title: DuckDB 面向分析型负载的进程内数据库
type: entity
tags: [数据库, OLAP, 分析型, 开源]
source_count: 0
updated: 2026-06-11
---

DuckDB 是一个面向分析型工作负载的进程内数据库，由荷兰 Centrum Wiskunde & Informatica (CWI) 的 Mark Raasveldt 和 Hannes Mühleisen 等人开发。它的定位很清晰：不是 SQLite 的 OLAP 版本，而是让分析查询可以在本地笔记本、CI 流水线、Python 脚本或 Jupyter Notebook 中直接运行，无需启动独立的数据库服务器。

我使用 DuckDB 的核心体验是：它把"加载 CSV 然后做 GROUP BY"这种操作从"先启动数据库服务"变成"import duckdb; con.execute(...)"，而执行速度却能接近或超过一些分布式系统。它直接利用内存进行向量化执行，支持高效的 Parquet 读写，与 pandas 生态集成良好。

DuckDB 团队同时也是 DuckLake 的创建者。DuckLake 可以看作是 DuckDB 设计哲学在数据湖格式领域的延伸：保持简单、进程内可用、用 SQL 作为统一接口，同时把元数据管理从复杂的文件协议中解放出来。

来源：[[sources/ducklake-manifesto]] · [[sources/ducklake-v1-0-announcement]]

相关页面：[[topics/ducklake]] · [[entities/ducklake]]
