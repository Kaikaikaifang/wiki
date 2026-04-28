---
title: OSS-HDFS
type: entity
tags: [OSS-HDFS, HDFS, 对象存储, 数据湖]
source_count: 2
updated: 2026-04-28
---

> 我对 OSS-HDFS 的理解是：它不是简单“在 OSS 上放 Hadoop 数据”，而是把 HDFS 接口、目录语义、权限映射、审计和冷热分层这些大数据文件系统习惯，重新接到云对象存储之上。

## 在这个 wiki 中的重要性

OSS-HDFS 代表的是 HDFS 语义的云化路径。[[sources/aliyun-oss-hdfs-overview]] 说明它通过 JindoFS / JindoSDK 兼容 HDFS 文件系统接口，让 Hadoop、Spark、Hive、HBase、Flink、Trino 等生态尽量少改造地访问 OSS 上的数据。

[[sources/aliyun-oss-hdfs-notice]] 则补上了更关键的生产边界：开通 OSS-HDFS 后，Bucket 中的 `.dlsdata/` 是服务内部数据目录，不能再被普通 OSS 操作随意写、删、改、重命名，也不能被生命周期、版本控制、日志转存、清单导出、ZIP 解压等功能误伤。

## 我会保留的系统特征

- **兼容 HDFS 接口**：降低 Hadoop 生态迁移到对象存储的改造成本。
- **托管元数据**：用云服务侧统一元数据管理替代传统 NameNode 机器集群心智。
- **分层命名空间**：在对象存储扁平命名空间之外提供目录层级。
- **生态接入靠 JindoSDK / JindoFuse**：不同计算引擎通过 SDK、配置或 Fuse 方式访问。
- **内部目录不可绕过**：`.dlsdata/` 是文件系统语义和对象存储实现的交界面。
- **冷热分层要走 OSS-HDFS 语义**：不要用普通 OSS 生命周期规则粗暴处理内部数据目录。

## 对我的提醒

OSS-HDFS 的核心风险不是“云服务不可靠”，而是人同时用两套抽象操作同一份数据：上层把它当 HDFS，底层又把 `.dlsdata/` 当普通对象目录。生产上必须明确谁拥有这个目录、哪些功能必须排除它、哪些权限和后台角色不能动。

---

来源：[[sources/aliyun-oss-hdfs-overview]] · [[sources/aliyun-oss-hdfs-notice]]

相关页面：[[topics/hdfs-and-oss-hdfs]] · [[entities/hdfs]] · [[sources/aliyun-oss-hdfs-overview]] · [[sources/aliyun-oss-hdfs-notice]]
