---
title: DuckLake 宣言
author: DuckDB Team
published: ""
link: "https://ducklake.select/manifesto/"
file: raw/articles/ducklake-manifesto.md
type: source
tags: [数据湖仓, DuckDB, 数据格式, SQL]
source_count: 1
updated: 2026-06-11
---

DuckLake 的核心主张是：既然 lakehouse 的目录层最终还是要引入一个数据库，那为什么不干脆把全部元数据也交给数据库来管理？Mark Raasveldt 和 Hannes Mühleisen 在这篇宣言里把 Iceberg 和 Delta Lake 的元数据文件迷宫拆开来看，指出它们为了不依赖数据库而做的种种妥协——JSON/Avro 快照文件、两层 manifest、为原子性而引入的 catalog 服务——本质上都在证明一件事：把元数据放在数据库里是更合理的设计。

DuckLake 的做法是把所有元数据结构迁移到 SQL 数据库中，数据文件仍用开放的 Parquet 格式存放在对象存储上。它强调三个原则：简单性（一套 SQL 搞定所有 catalog 和 metadata 事务）、可扩展性（存储、计算、元数据管理三层解耦）、速度（单次查询即可获得文件列表，避免多次 S3 往返）。

最让我印象深刻的是它把 Iceberg 已有的 catalog 架构做了一个"归一化"：既然 Iceberg 最终也需要一个数据库来管理当前版本指针，那干脆把所有快照、schema、分区统计都放进数据库的表里，用 ACID 事务和主键约束来保证一致性。这不仅减少了小文件数量，也让事务冲突的处理从"S3 原子写"降级为"数据库事务并发控制"——后者是经过数十年验证的成熟机制。

来源：[[sources/ducklake-manifesto]]

相关页面：[[topics/ducklake]] · [[entities/duckdb]] · [[entities/ducklake]] · [[sources/ducklake-v1-0-announcement]]
