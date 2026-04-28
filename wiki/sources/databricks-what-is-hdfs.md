---
title: HDFS 基础概念
type: source
tags: [HDFS, Hadoop, 分布式存储, 大数据]
source_count: 1
source_file: raw/articles/databricks-what-is-hdfs.md
author: Databricks
published: 2021-12-08
updated: 2026-04-28
---

来源：[[entities/hdfs]] · [原文](https://www.databricks.com/blog/what-is-hdfs)

## 核心结论

这篇 Databricks 的 HDFS 介绍适合拿来做概念底座：HDFS 是 Hadoop 生态里的分布式文件系统，核心做法是把大文件切成 block，分散存到多台机器上，再通过副本机制换取吞吐和容错。

我会把它理解成早期大数据系统的一个关键假设：数据量大到单机文件系统不够用，硬件故障又是常态，所以存储系统必须默认分布式、默认可复制、默认能在节点失败后继续服务。

## 架构直觉

HDFS 的两个基本角色是 `NameNode` 和 `DataNode`。

`NameNode` 管元数据：目录树、文件到 block 的映射、block 在哪些 DataNode 上、客户端是否有权限打开或修改文件。它像是整个文件系统的控制平面。

`DataNode` 管真实数据块：保存 block、响应读写请求、按 NameNode 指令创建、删除、复制 block。它像是数据平面。

这套设计的关键取舍是：NameNode 让元数据管理集中化，DataNode 让数据吞吐分布化。它很适合大文件、高吞吐、批处理和顺序读写，但不应该被想象成一个适合大量小文件和低延迟随机写的通用文件系统。

## 为什么它曾经重要

文章把 HDFS 放回 Hadoop 历史里：它源自 Google File System 的设计思想，最早服务于 Nutch 这类需要分布式爬取和处理网页的系统，后来成为 Hadoop 生态的存储层。

这也解释了 HDFS 的系统气质：它不是从“云对象存储”出发的，而是从“本地机架上的廉价机器集群”出发的。数据尽量靠近计算，MapReduce、HBase、Solr 等服务可以围绕数据块位置组织处理路径。

## 对我的启发

理解 HDFS，对今天仍然有价值。即使很多组织已经把湖仓底座迁到对象存储，HDFS 的概念仍然解释了大数据系统的几个基础问题：

- 大文件如何切块；
- 副本如何提升容错；
- 元数据为什么会成为独立问题；
- 数据本地性为什么曾经是性能核心；
- Hadoop 生态为什么把存储、计算和资源管理拆成 HDFS、MapReduce、YARN 这些层。

换句话说，HDFS 不只是一个过时的存储产品名，而是一套理解大数据存储系统如何从本地集群走向云原生数据湖的参照物。

---

相关页面：[[topics/hdfs-and-oss-hdfs]] · [[entities/hdfs]] · [[entities/oss-hdfs]] · [[sources/aliyun-oss-hdfs-overview]]
