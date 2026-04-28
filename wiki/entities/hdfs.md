---
title: HDFS
type: entity
tags: [HDFS, Hadoop, 分布式存储, 大数据]
source_count: 3
updated: 2026-04-28
---

> 我会把 HDFS 当作理解大数据存储系统的一块基本参照物。它不只是 Hadoop 里的一个组件，而是把“大文件、廉价机器、节点失败、批处理吞吐、数据本地性”这些问题放进了同一个架构模型。

## 在这个 wiki 中的重要性

HDFS 目前连接的是大数据存储和云上数据湖这条新线索。[[sources/databricks-what-is-hdfs]] 给了传统 HDFS 的基础模型：NameNode 管元数据，DataNode 存 block，文件被切块和复制，用横向机器换容量、吞吐和容错。

[[sources/aliyun-oss-hdfs-overview]] 和 [[sources/aliyun-oss-hdfs-notice]] 则说明，HDFS 的影响没有随着对象存储普及而消失。相反，它的接口语义被 OSS-HDFS 这类云服务继续承接，用来降低 Hadoop、Spark、Hive、HBase 等生态迁移到云对象存储的成本。

## 我会保留的系统特征

- **面向大文件和高吞吐**：HDFS 适合大规模顺序读写和批处理，不是万能低延迟文件系统。
- **元数据和数据分离**：NameNode / DataNode 分工让系统扩展性清晰，也让元数据成为关键边界。
- **副本换容错**：block 副本让单个节点失败不至于导致文件不可读。
- **数据本地性曾经很重要**：计算靠近数据，是早期 Hadoop 性能模型的核心。
- **接口语义仍有迁移价值**：云对象存储时代，HDFS API 仍然是很多大数据作业的兼容入口。

## 对我的提醒

学习 HDFS，不是为了回到自建 Hadoop 集群，而是为了理解许多数据平台设计的底层惯性。为什么有 block，为什么怕小文件，为什么元数据服务会成为瓶颈，为什么对象存储迁移需要兼容层，这些问题都能在 HDFS 里找到原型。

---

来源：[[sources/databricks-what-is-hdfs]] · [[sources/aliyun-oss-hdfs-overview]] · [[sources/aliyun-oss-hdfs-notice]]

相关页面：[[topics/hdfs-and-oss-hdfs]] · [[entities/oss-hdfs]] · [[sources/databricks-what-is-hdfs]] · [[sources/aliyun-oss-hdfs-overview]]
